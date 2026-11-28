"""
Ultraviolet: what fluoresces, traced from the Bank of Japan's own photograph of the note under a UV
lamp (boj.or.jp/note_tfjgs/note/n_note/security.htm, image security11.png, saved in source/boj/).

The BOJ photo is a flat, square-on view of the whole front (1014 x 482 px, the note's own 160 : 76),
so it maps straight onto the note. Two things glow in it:
  - the Governor's seal, orange  -> assets/layers/uv-seal.png, the seal's own vermilion ink;
  - parts of the background pattern, yellow-green -> written here as assets/layers/uv-front.png.
    Where it glows comes from the BOJ photo (low resolution); in it the glow lies on the pink
    background tint, so the glow's fine texture is taken from that tint in the daylight artwork
    (the BOJ photo alone would be blocky up close).
The NPB says parts of the back's pattern glow too, but no official image shows which, so the page
does not invent them.
Run: python tools/uv_map.py
"""
import os
import numpy as np, cv2
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'source', 'boj', 'boj-security11-uv.png')
OUT_W, OUT_H = 2160, 1026


def main():
    im = cv2.cvtColor(cv2.imread(SRC), cv2.COLOR_BGR2RGB)
    nw = im.min(2) < 235                              # the note (the page around it is white)
    ys, xs = np.nonzero(nw)
    note = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.float32)
    R, G, B = note[..., 0], note[..., 1], note[..., 2]
    # yellow-green fluorescence: green well above blue (the unlit note is deep blue)
    glow = np.clip((G - B - 10) / 90, 0, 1) * np.clip((G - 90) / 100, 0, 1)
    # the seal glows orange: excluded here (it is lit from its own cut-out)
    seal = (R > G + 25) & (R > 120)
    seal = cv2.dilate(seal.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    glow[seal] = 0
    glow = cv2.resize(glow, (OUT_W, OUT_H), interpolation=cv2.INTER_CUBIC)
    region = cv2.GaussianBlur(glow, (0, 0), 6)
    region = np.clip((region - 0.12) / 0.3, 0, 1); region = region * region * (3 - 2 * region)   # where, not how much
    # texture: the pale pink tint of the daylight artwork (not the dark engraving)
    art = np.asarray(Image.open(os.path.join(ROOT, 'jpy-10000-front.png')).convert('RGB').resize((OUT_W, OUT_H), Image.LANCZOS))
    lab = cv2.cvtColor(art, cv2.COLOR_RGB2LAB).astype(np.float32)
    pink = np.clip((lab[..., 1] - np.median(lab[..., 1])) / 10, 0, 1) * np.clip((lab[..., 0] - 120) / 60, 0, 1)
    glow = np.clip(region * (0.4 + 0.75 * pink), 0, 1) ** 1.1
    rgba = np.zeros((OUT_H, OUT_W, 4), np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = 214, 255, 120          # fluorescent yellow-green
    rgba[..., 3] = (glow * 255).astype(np.uint8)
    Image.fromarray(rgba, 'RGBA').save(os.path.join(ROOT, 'assets', 'layers', 'uv-front.png'), optimize=True)
    # the seal: only its vermilion ink glows (not the paper inside its ring)
    seal = Image.open(os.path.join(ROOT, 'assets', 'layers', 'front-seal.png')).convert('RGBA')
    sl = cv2.cvtColor(np.asarray(seal.convert('RGB')), cv2.COLOR_RGB2LAB).astype(np.float32)
    red = np.clip((sl[..., 1] - 140) / 25, 0, 1) * (np.asarray(seal.getchannel('A')) / 255)
    out = np.zeros(red.shape + (4,), np.uint8); out[..., 0], out[..., 1], out[..., 2] = 255, 170, 80
    out[..., 3] = (np.clip(red, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(out, 'RGBA').save(os.path.join(ROOT, 'assets', 'layers', 'uv-seal.png'), optimize=True)
    print('uv-front.png', note.shape, 'glowing share', float((glow > .3).mean()))


if __name__ == '__main__':
    main()
