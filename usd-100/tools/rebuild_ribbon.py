"""
The 3-D Security Ribbon, rebuilt: the scan's ribbon is blotchy up close, so it is repainted as a clean
woven ribbon in the artwork (usd-100-front.png), in exactly the scan's place:
  - band edges and the windows where it shows through the paper are measured from the scan's blue;
  - the fill is the scan's median blue with fine lengthwise lens lines and slightly darker edges;
  - it fades out where it weaves under the paper, and black print over it is kept.
Reads the untouched artwork from source/usd-100-front-pre-ribbon.png (made on the first run), so it
can be re-run.   Run: python tools/rebuild_ribbon.py
"""
import os, shutil
import numpy as np, cv2
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, 'usd-100-front.png')
PRE = os.path.join(ROOT, 'source', 'usd-100-front-pre-ribbon.png')
SEARCH = (362, 412)                 # note units: x range to look for the band in
BLUE = np.array([62, 89, 178], np.float32)


def runs(on, min_len):
    out, s = [], None
    for i, v in enumerate(list(on) + [False]):
        if v and s is None:
            s = i
        elif not v and s is not None:
            if i - s >= min_len:
                out.append((s, i))
            s = None
    return out


def main():
    if not os.path.exists(PRE):
        shutil.copyfile(ART, PRE)
    im = Image.open(PRE).convert('RGB'); W, H = im.size; sx, sy = W / 720, H / 320
    full = np.asarray(im).astype(np.float32)
    x0, x1 = int(SEARCH[0] * sx), int(SEARCH[1] * sx)
    rgb = full[:, x0:x1]
    lab = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
    L, A, B = lab[..., 0], lab[..., 1] - 128, lab[..., 2] - 128
    blue = B < -15
    xs = np.nonzero(blue.mean(0) > 0.25)[0]
    bl, br = xs.min(), xs.max() + 1                        # band edges (px, in the search strip)
    row = blue[:, bl:br].mean(1) > 0.35
    row = cv2.morphologyEx(row.astype(np.uint8)[:, None], cv2.MORPH_CLOSE, np.ones((int(5 * sy), 1), np.uint8))[:, 0] > 0
    wins = runs(row, int(6 * sy))
    print('band units', round((x0 + bl) / sx, 1), round((x0 + br) / sx, 1), 'windows', [(round(a / sy, 1), round(b / sy, 1)) for a, b in wins])
    h, w = rgb.shape[:2]
    # coverage: band columns x window rows, anti-aliased sides, soft ends where it goes under the paper
    yy = np.zeros(h, np.float32)
    fade = 1.6 * sy
    for a, b in wins:
        t = np.arange(h, dtype=np.float32)
        yy = np.maximum(yy, np.clip(np.minimum(t - a, b - t) / fade + 0.5, 0, 1) if a > 0 else np.clip((b - t) / fade + 0.5, 0, 1) * (t >= 0))
        if b >= h:
            yy[a:] = np.maximum(yy[a:], np.clip((np.arange(a, h) - a) / fade + 0.5, 0, 1))
    xx = np.zeros(w, np.float32); t = np.arange(w, dtype=np.float32)
    xx = np.clip(np.minimum(t - bl, br - 1 - t) + 0.5, 0, 1)
    cov = yy[:, None] * xx[None, :]
    # the paint: lens lines along the ribbon, darker edges, a faint shimmer down its length
    u = (t - bl) / max(br - bl - 1, 1)                       # 0..1 across
    lens = 1 + 0.06 * np.sin(2 * np.pi * (t - bl) / 3.2)    # ~0.75 unit pitch
    edge = 1 - 0.22 * np.clip(1 - np.minimum(u, 1 - u) / 0.08, 0, 1)
    rng = np.random.default_rng(7)
    shimmer = cv2.GaussianBlur(rng.normal(0, 1, (h, 1)).astype(np.float32), (0, 0), 25 * sy)[:, 0]
    shimmer = 1 + 0.05 * shimmer / (np.abs(shimmer).max() + 1e-6)
    grain = 1 + 0.015 * rng.normal(0, 1, (h, w)).astype(np.float32)
    paint = BLUE[None, None] * (lens * edge)[None, :, None] * shimmer[:, None, None] * grain[..., None]
    # black print over the ribbon stays
    chroma = np.sqrt(A ** 2 + B ** 2)
    keep = np.clip((95 - L) / 30, 0, 1) * np.clip((30 - chroma) / 12, 0, 1)
    keep = cv2.GaussianBlur(keep, (0, 0), 0.6)
    a = (cov * (1 - keep))[..., None]
    rgb_new = rgb * (1 - a) + np.clip(paint, 0, 255) * a
    full[:, x0:x1] = rgb_new
    Image.fromarray(full.clip(0, 255).astype(np.uint8)).save(ART, optimize=True)
    print('ribbon rebuilt ->', ART)
    # the ribbon's page layer and effect mask: the ribbon's own shape (band x windows); print over it is
    # left to the artwork, so the moving images aren't punched full of holes
    import re, json
    boxes = open(os.path.join(ROOT, 'assets', 'boxes.js'), encoding='utf8').read()
    bx, by, bw, bh = json.loads(re.search(r'"front-ribbon": (\[[^\]]*\])', boxes).group(1))
    alpha = np.zeros(full.shape[:2], np.float32); alpha[:, x0:x1] = cov
    rgba = np.dstack([full, alpha * 255]).clip(0, 255).astype(np.uint8)
    fx0, fy0, fx1, fy1 = round(bx * sx), round(by * sy), round((bx + bw) * sx), round((by + bh) * sy)
    frame = np.zeros((fy1 - fy0, fx1 - fx0, 4), np.uint8)
    sy0, sx0 = max(0, fy0), max(0, fx0)
    frame[sy0 - fy0:min(H, fy1) - fy0, sx0 - fx0:min(W, fx1) - fx0] = rgba[sy0:min(H, fy1), sx0:min(W, fx1)]
    page = Image.fromarray(frame, 'RGBA')
    page = page.resize((round(bw * 3), round(bh * 612 / 320 * 1.5)), Image.LANCZOS)
    for n in ('front-ribbon-cut.png', 'front-ribbon.png'):
        page.save(os.path.join(ROOT, 'assets', 'layers', n), optimize=True)
    print('ribbon layer + mask source written, box', [bx, by, bw, bh])


if __name__ == '__main__':
    main()
