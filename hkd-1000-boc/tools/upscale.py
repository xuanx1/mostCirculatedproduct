"""
AI upscale (Real-ESRGAN x2, two passes = x4) and level the HK$1,000 (Bank of China (Hong Kong), 2018 Series)
artwork, from the originals in source/.

  python tools/upscale.py path/to/RealESRGAN_x2plus.pth

The only official images of this note are small (the HKMA 2018 Series leaflet: 518 x 259 front,
260 x 514 back), so each side is upscaled twice with the x2 model.

Steps per side:
  1. The reverse is printed in vertical orientation: it is turned a quarter turn anticlockwise so it
     lies on the landscape note the way it really backs the obverse (the see-through pieces at the
     reverse's top left land behind the obverse's bottom right).
  2. Real-ESRGAN x2 (RRDBNet), run in tiles on the GPU, twice: sharper line-work than plain resizing.
     Note: an AI upscaler reconstructs plausible detail; it cannot recover microprint or fine
     engraving that the source image never captured.
  3. Level: paper set to near-white (levels from the paper's own brightness), a very gentle gamma lift
     (the source is clean digital artwork, not a photo, so it needs far less than a scan).
  4. Resize to the working size (2880 x 1440, the note's 163 x 81.5 mm = 2 : 1) -> hkd-1000-boc-front.png / -back.png
  5. The HKMA's close-up of this note's watermark (108 x 102) is upscaled the same way for the watermark
     layer (source/watermark-esrgan-x4.png; tools/hkd_features.py builds the layer from it).
"""
import os, sys, math
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES = {'front': 'source/front-hkma-leaflet-518.jpg', 'back': 'source/back-hkma-leaflet-260.jpg'}
WM_SRC = 'source/reference/hkma_boc_1000_no5.jpg'
OUT_W, OUT_H = 2880, 1440


class RDB(nn.Module):
    def __init__(self, nf=64, gc=32):
        super().__init__()
        self.conv1 = nn.Conv2d(nf, gc, 3, 1, 1)
        self.conv2 = nn.Conv2d(nf + gc, gc, 3, 1, 1)
        self.conv3 = nn.Conv2d(nf + 2 * gc, gc, 3, 1, 1)
        self.conv4 = nn.Conv2d(nf + 3 * gc, gc, 3, 1, 1)
        self.conv5 = nn.Conv2d(nf + 4 * gc, nf, 3, 1, 1)
        self.lrelu = nn.LeakyReLU(0.2, True)

    def forward(self, x):
        x1 = self.lrelu(self.conv1(x))
        x2 = self.lrelu(self.conv2(torch.cat((x, x1), 1)))
        x3 = self.lrelu(self.conv3(torch.cat((x, x1, x2), 1)))
        x4 = self.lrelu(self.conv4(torch.cat((x, x1, x2, x3), 1)))
        x5 = self.conv5(torch.cat((x, x1, x2, x3, x4), 1))
        return x5 * 0.2 + x


class RRDB(nn.Module):
    def __init__(self, nf=64, gc=32):
        super().__init__()
        self.rdb1, self.rdb2, self.rdb3 = RDB(nf, gc), RDB(nf, gc), RDB(nf, gc)

    def forward(self, x):
        return self.rdb3(self.rdb2(self.rdb1(x))) * 0.2 + x


class RRDBNet(nn.Module):
    """basicsr RRDBNet, scale 2 (input pixel-unshuffled by 2)."""
    def __init__(self, nb=23, nf=64, gc=32):
        super().__init__()
        self.conv_first = nn.Conv2d(3 * 4, nf, 3, 1, 1)
        self.body = nn.Sequential(*[RRDB(nf, gc) for _ in range(nb)])
        self.conv_body = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_up1 = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_up2 = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_hr = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_last = nn.Conv2d(nf, 3, 3, 1, 1)
        self.lrelu = nn.LeakyReLU(0.2, True)

    def forward(self, x):
        feat = self.conv_first(F.pixel_unshuffle(x, 2))
        feat = feat + self.conv_body(self.body(feat))
        feat = self.lrelu(self.conv_up1(F.interpolate(feat, scale_factor=2, mode='nearest')))
        feat = self.lrelu(self.conv_up2(F.interpolate(feat, scale_factor=2, mode='nearest')))
        return self.conv_last(self.lrelu(self.conv_hr(feat)))


def upscale(model, img, dev, tile=256, pad=16):
    x = torch.from_numpy(np.asarray(img, np.float32) / 255).permute(2, 0, 1)[None].to(dev)
    _, _, h, w = x.shape
    ph, pw = (2 - h % 2) % 2, (2 - w % 2) % 2               # even size for pixel_unshuffle
    x = F.pad(x, (0, pw, 0, ph), mode='reflect')
    _, _, H, W = x.shape
    out = torch.zeros((1, 3, H * 2, W * 2), device=dev)
    for ty in range(math.ceil(H / tile)):
        for tx in range(math.ceil(W / tile)):
            y0, x0 = ty * tile, tx * tile
            y1, x1 = min(y0 + tile, H), min(x0 + tile, W)
            py0, px0 = max(y0 - pad, 0), max(x0 - pad, 0)
            py1, px1 = min(y1 + pad, H), min(x1 + pad, W)
            patch = x[:, :, py0:py1, px0:px1]
            if (patch.shape[2] % 2) or (patch.shape[3] % 2):
                patch = F.pad(patch, (0, patch.shape[3] % 2, 0, patch.shape[2] % 2), mode='reflect')
            with torch.no_grad():
                o = model(patch)
            oy, ox = (y0 - py0) * 2, (x0 - px0) * 2
            out[:, :, y0 * 2:y1 * 2, x0 * 2:x1 * 2] = o[:, :, oy:oy + (y1 - y0) * 2, ox:ox + (x1 - x0) * 2]
    out = out[:, :, :h * 2, :w * 2].clamp(0, 1)
    return Image.fromarray((out[0].permute(1, 2, 0).cpu().numpy() * 255).round().astype(np.uint8))


def brighten(img):
    a = np.asarray(img, np.float32)
    lum = a @ np.array([.299, .587, .114], np.float32)
    paper = np.percentile(lum, 90)                           # the note's paper tone
    black = np.percentile(lum, 0.5)
    black = min(black, 20)                                   # keep the darkest print dark
    a = np.clip((a - black) / max(paper - black, 1) * 248, 0, 255)   # paper -> near white
    a = 255 * (a / 255) ** 0.97                              # very gentle lift of the mid-tones
    out = Image.fromarray(a.astype(np.uint8))
    return ImageEnhance.Color(out).enhance(1.04)


def main():
    weights = sys.argv[1]
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = RRDBNet()
    sd = torch.load(weights, map_location='cpu')
    model.load_state_dict(sd.get('params_ema', sd.get('params', sd)), strict=True)
    model.eval().to(dev)
    for side, src in SOURCES.items():
        img = Image.open(os.path.join(ROOT, src)).convert('RGB')
        if side == 'back':
            img = img.transpose(Image.ROTATE_90)             # vertical reverse -> landscape, top to the left
        up = upscale(model, upscale(model, img, dev), dev)
        up.save(os.path.join(ROOT, 'source', f'{side}-esrgan-x4.png'), optimize=True)
        final = brighten(up).resize((OUT_W, OUT_H), Image.LANCZOS)
        final.save(os.path.join(ROOT, f'hkd-1000-boc-{side}.png'), optimize=True)
        print(side, img.size, '->', up.size, '->', final.size)
    wm = Image.open(os.path.join(ROOT, WM_SRC)).convert('RGB')
    up = upscale(model, upscale(model, wm, dev), dev)
    up.save(os.path.join(ROOT, 'source', 'watermark-esrgan-x4.png'), optimize=True)
    print('watermark', wm.size, '->', up.size)


if __name__ == '__main__':
    main()
