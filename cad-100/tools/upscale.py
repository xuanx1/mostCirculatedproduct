"""
AI upscale (Real-ESRGAN x2) and level the $100 Frontier artwork, from the Bank of Canada originals.

  python tools/upscale.py path/to/RealESRGAN_x2plus.pth

The Bank of Canada's published images (source/front-boc-1000.png, source/back-boc-1000.png, 1000 x 458)
are RGBA: the polymer's clear areas (the large window, the outline of the frosted maple leaf) are
transparent. Steps per side:
  1. Real-ESRGAN x2 (RRDBNet) on the colour, run in tiles on the GPU: sharper line-work than plain
     resizing. The alpha (the windows) is upscaled with the same network (as grey), so the window
     edges stay crisp, then cleaned to fully clear / fully opaque with a 1 px anti-aliased edge.
     Note: an AI upscaler reconstructs plausible detail; it cannot recover microprint the
     1000 px source never had.
  2. Level: these are clean digital renders, not photos, and the note's tan/brown is its real
     colour, so the paper is NOT pushed to white (unlike the US $100 photo). Only a gentle
     black-point clip (0.3 %) and a slight saturation lift.
  3. Saved at the x2 size (2000 x 916, the note's 152.4 x 69.85 mm = 2.18 : 1) -> cad-100-front.png / -back.png
"""
import os, sys, math
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES = {'front': 'source/front-boc-1000.png', 'back': 'source/back-boc-1000.png'}


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


def upscale(model, arr, dev, tile=256, pad=16):
    x = torch.from_numpy(arr.astype(np.float32) / 255).permute(2, 0, 1)[None].to(dev)
    _, _, h, w = x.shape
    ph, pw = (2 - h % 2) % 2, (2 - w % 2) % 2
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
    return (out[0].permute(1, 2, 0).cpu().numpy() * 255).round().astype(np.uint8)


def level(rgb):
    a = rgb.astype(np.float32)
    lum = a @ np.array([.299, .587, .114], np.float32)
    black = np.percentile(lum, 0.3)
    a = np.clip((a - black) / (255 - black) * 255, 0, 255)
    return np.asarray(ImageEnhance.Color(Image.fromarray(a.astype(np.uint8))).enhance(1.06))


def main():
    weights = sys.argv[1]
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = RRDBNet()
    sd = torch.load(weights, map_location='cpu')
    model.load_state_dict(sd.get('params_ema', sd.get('params', sd)), strict=True)
    model.eval().to(dev)
    for side, src in SOURCES.items():
        im = np.asarray(Image.open(os.path.join(ROOT, src)).convert('RGBA'))
        rgb, alpha = im[..., :3], im[..., 3]
        up = upscale(model, rgb, dev)
        ua = upscale(model, np.dstack([alpha] * 3), dev).mean(2)
        # clean alpha: clear or opaque, ~1 px ramp at the edge (no haze in the windows)
        ua = np.clip((ua - 128) * 2.2 + 128, 0, 255).astype(np.uint8)
        Image.fromarray(np.dstack([up, ua])).save(os.path.join(ROOT, 'source', f'{side}-esrgan-x2.png'), optimize=True)
        final = np.dstack([level(up), ua])
        Image.fromarray(final, 'RGBA').save(os.path.join(ROOT, f'cad-100-{side}.png'), optimize=True)
        print(side, rgb.shape[1::-1], '->', up.shape[1::-1])


if __name__ == '__main__':
    main()
