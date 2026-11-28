"""
Clean-ups for two €500 cut-outs that the automatic cut gets wrong. Run after tools/cutouts.py.

  architecture  the SAM mask picks up bits of the star and the big "500" above the glass gateway. It is cut
                along the gateway's top edge (GATE_LINE, artwork px in the layer's frame), reduced to the largest
                piece, holes filled, and its outline straightened (the building is rectilinear), never growing
                past the original mask by more than a few px.
  bar           the navy bar: an orange star's tip printed over its left edge bit a notch out of the cut.
                The bar is a solid shape, so its silhouette is the convex hull of the cut.

Both are rebuilt from the artwork's own pixels at the layer's frame (assets/boxes.js), and written as the
page layers (ink and -cut) and the full-resolution feature crops.
Run: python tools/fix_cuts.py
"""
import json, os, re
import numpy as np, cv2
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYERS = os.path.join(ROOT, 'assets', 'layers')
CROPS = os.path.join(ROOT, 'feature-crops', 'front')
SCALE = 0.75                                   # as tools/cutouts.py


def frame(key):
    boxes = json.loads(re.search(r'=\s*(\{[\s\S]*\})', open(os.path.join(ROOT, 'assets', 'boxes.js')).read()).group(1))
    art = Image.open(os.path.join(ROOT, 'eur-500-front.png')).convert('RGB')
    W, H = art.size; sx, sy = W / 720, H / 320
    x, y, w, h = boxes[key]
    x0, y0 = round(x * sx), round(y * sy)
    x1, y1 = x0 + round(w * sx), y0 + round(h * sy)
    rgb = np.asarray(art.crop((x0, y0, x1, y1)))
    cut = Image.open(os.path.join(LAYERS, f'{key}-cut.png')).getchannel('A').resize((x1 - x0, y1 - y0), Image.LANCZOS)
    return rgb, (np.asarray(cut) > 127).astype(np.uint8) * 255


def aa(m):
    f = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 0.9)
    return np.clip((f - 0.5) * 2.2 + 0.5, 0, 1)


def largest(m):
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    return ((lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))) * 255).astype(np.uint8) if n > 1 else m


def fill_holes(m):
    ff = m.copy(); cv2.floodFill(ff, np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8), (0, 0), 255)
    return m | (~ff & 255)


def write(key, rgb, m):
    a = (aa(m) * 255).astype(np.uint8)
    arr = np.dstack([rgb, a])
    img = Image.fromarray(arr, 'RGBA')
    size = (round(img.width * SCALE), round(img.height * SCALE))
    for name in (f'{key}.png', f'{key}-cut.png'):
        img.resize(size, Image.LANCZOS).save(os.path.join(LAYERS, name), optimize=True)
    ys, xs = np.nonzero(a > 6)
    crop = arr[max(0, ys.min() - 10):ys.max() + 11, max(0, xs.min() - 10):xs.max() + 11]
    Image.fromarray(crop, 'RGBA').save(os.path.join(CROPS, key.replace('front-', '') + '.png'), optimize=True)
    print(key, 'written', size)


# the building's top edge, measured on the artwork (px in the layer's frame): left column top, the glass
# gateway's top corner and edge, then along the big "5" that is printed over the building, to the right block
TOP_EDGE = [(0, 107), (150, 107), (154, 57), (330, 167), (400, 200), (1200, 200)]


def architecture():
    rgb, m = frame('front-architecture')
    h, w = m.shape
    allowed = np.zeros_like(m)
    cv2.fillPoly(allowed, [np.array(TOP_EDGE + [(w, 200), (w, h), (0, h)], np.int32)], 255)
    # notches the navy bar and a star tip bit into the cut are closed; nothing above the measured edge
    closed = fill_holes(cv2.morphologyEx(largest(m), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))))
    # the right-hand block's upper rows lie under the big "5", so the automatic mask misses them: the block is
    # filled from its measured top (row 200) down to where the mask has it, out to its right edge there
    rows = np.nonzero(closed[480:620].any(1))[0]
    right = int(np.percentile([np.nonzero(closed[480 + r])[0].max() for r in rows], 50))
    block = np.zeros_like(m); block[200:500, 600:right + 1] = 255
    clean = largest((closed | block) & allowed)
    cnt = max(cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0], key=cv2.contourArea)
    poly = cv2.approxPolyDP(cnt, 3.0, True)                  # straight edges: the building is rectilinear
    clean = np.zeros_like(m); cv2.fillPoly(clean, [poly], 255)
    clean &= allowed
    write('front-architecture', rgb, clean)


def bar():
    rgb, m = frame('front-bar')
    m = largest(m)
    hull = cv2.convexHull(cv2.findNonZero(m))
    clean = np.zeros_like(m); cv2.fillPoly(clean, [hull], 255)
    write('front-bar', rgb, clean)


if __name__ == '__main__':
    architecture()
    bar()
