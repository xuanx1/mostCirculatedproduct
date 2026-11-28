"""
Cut every HK$1,000 (Bank of China (Hong Kong), 2018 Series) feature out of the working artwork as a
clean alpha layer, build the watermark from the HKMA's own photograph of this note's watermark, draw
the concealed denomination, and write the page's masks and boxes.

  python tools/hkd_features.py          (run tools/sam_isolate.py first for the tower, flower and heads)

Each feature is isolated by its own rule (no hand painting), always from the original pixels:
  darker     the large 1000: its digits are clearly darker than the pale ground (lightness), the
             counters of the 0s stay open (no hole filling)
  green      the bauhinia of the dynamic shimmering pattern (the 1000 inside it kept), the thread windows
  orange     the see-through pieces (front and back), flat orange print
  dark       the serial numbers (black), ink only
  red        braille dots and tactile lines (red raised print), ink only
  script     the signature, ink only (colour-to-alpha against the local paper)
Edges: a binary shape blurred to a ~1-2 px anti-aliased edge; edge pixels take the colour of the
nearest solid pixel (no paper halo on a dark background).

Writes assets/layers/<side>-<id>.png (framed on the box the page uses), feature-crops/<side>/<id>.png,
assets/boxes.js, assets/masks.css (data URIs: works from file://), assets/offset-front.jpg /
offset-back.jpg (the print with the separately layered features removed, for the exploded view),
assets/layers/watermark-ghost.png and assets/layers/front-latent.png.
Hand-cleaned files in assets/overrides/ always win.
"""
import base64, io, os
import numpy as np
import cv2
from PIL import Image
from scipy import ndimage

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

LUM = np.array([.299, .587, .114], np.float32)

# boxes in note units [x, y, w, h] (checked against grid overlays of the artwork)
BOX = {
    ('front', 'numeral'):    [10, 10, 210, 82],      # large 1000, top left (embossed feel)
    ('front', 'shimmer'):    [544, 12, 118, 100],    # bauhinia: dynamic shimmering pattern
    ('front', 'thread'):     [448, 52, 36, 256],     # the three windows of the metallic thread
    ('front', 'seethrough'): [526, 254, 148, 60],    # front half of the see-through 1000
    ('back', 'seethrough'):  [46, 254, 140, 60],     # back half
    ('front', 'serial-h'):   [38, 258, 112, 24],
    ('front', 'serial-v'):   [664, 122, 24, 128],
    ('front', 'braille'):    [40, 282, 116, 26],
    ('front', 'tactile-l'):  [0, 132, 24, 166],
    ('front', 'tactile-r'):  [694, 136, 26, 178],
    ('front', 'signature'):  [62, 183, 60, 23],
}


def region(img, box):
    x0, y0, x1, y1 = C.px(img, box)
    return img[y0:y1, x0:x1]


def finish(side, name, img, box, R, binary, sigma=0.9):
    a = C.soft_edge(binary, sigma)
    rgb = C.defringe(R, a)
    C.save_piece(side, name, img, box, rgb, a)
    return a


def ink(side, name, img, box, R, select, paper=None):
    """ink only: paper keyed out by colour-to-alpha, then limited to the selected strokes"""
    paper = C.paper_tone(R) if paper is None else paper
    col, a = C.colour_to_alpha(R, paper)
    sel = cv2.dilate(select.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32)
    sel = cv2.GaussianBlur(sel, (0, 0), 0.8)
    a = np.clip(a * 1.15, 0, 1) * np.clip(sel, 0, 1)
    C.save_piece(side, name, img, box, col, a)
    return a


def lightness(R):
    return cv2.cvtColor(R.astype(np.uint8), cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32) * 100 / 255


# ---------------------------------------------------------------- features
def numeral(f):
    box = BOX[('front', 'numeral')]
    R = region(f, box)
    m = lightness(R) < 72                  # the digits (L ~60) on the pale ground (L ~85)
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    m = C.keep_components(m, min_area=8000)   # the four digits only (not the promise text below)
    H = m.shape[0]                            # each digit stands the full height of the numeral
    m = C.keep_components(m, min_area=8000, keep=lambda st, c: st[cv2.CC_STAT_HEIGHT] > 0.6 * H)
    # the last 0 overlaps the red top of the tower, which is as dark as the digits: that 0 is upright and
    # symmetric, so its right half is taken as the mirror of its clean left half (about its own centre,
    # measured on its lower half, which stands on the pale ground)
    lab, n = ndimage.label(m)
    cx_of = ndimage.center_of_mass(m, lab, range(1, n + 1))
    last = 1 + int(np.argmax([c[1] for c in cx_of]))
    z = lab == last
    rows = np.where(z.any(1))[0]
    lo = [r for r in range(int(rows.min() + 0.6 * (rows.max() - rows.min())), int(rows.max() - 0.1 * (rows.max() - rows.min())))]
    mids = []
    for r in lo:
        xs = np.where(z[r])[0]
        mids.append((xs.min() + xs.max()) / 2)
    cx = int(round(np.median(mids)))
    left = z[:, :cx + 1]
    w = min(cx + 1, z.shape[1] - cx)
    zz = z.copy()
    zz[:, cx:cx + w] = left[:, ::-1][:, :w]
    zz[:, cx + w:] = False
    m = (m & ~z) | zz
    # tiny pinholes inside the strokes (but never the counters of the 0s)
    holes = ndimage.binary_fill_holes(m) & ~m
    lab, n = ndimage.label(holes)
    if n:
        sizes = ndimage.sum(holes, lab, range(1, n + 1))
        for k, s in enumerate(sizes, 1):
            if s < 400:
                m |= lab == k
    return finish('front', 'numeral', f, box, R, m, 1.0)


def green(f, name, min_area, fill=True, rects=False):
    box = BOX[('front', name)]
    R = region(f, box)
    r, g, b = R[..., 0], R[..., 1], R[..., 2]
    m = (g - r > 18) & (g - b > 0)
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))) > 0
    m = C.keep_components(m, min_area=min_area)
    if fill:
        m = ndimage.binary_fill_holes(m)
    if rects:                              # windows are rectangles: square them off from their extent
        n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), 8)
        out = np.zeros_like(m)
        for k in range(1, n):
            x, y, w, h, _ = st[k]
            colw = ((lab == k).sum(0) > h * 0.5)
            xs = np.where(colw)[0]
            rows = ((lab == k).sum(1) > w * 0.35)
            ys = np.where(rows)[0]
            out[ys.min():ys.max() + 1, xs.min():xs.max() + 1] = True
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        m = cv2.morphologyEx(out.astype(np.uint8), cv2.MORPH_OPEN, k) > 0     # softly rounded corners
    return finish('front', name, f, box, R, m, 0.9)


def seethrough(img, side):
    box = BOX[(side, 'seethrough')]
    R = region(img, box)
    r, g, b = R[..., 0], R[..., 1], R[..., 2]
    m = (r > 200) & (r - b > 120) & (g < 205)                       # flat orange print on white paper
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
    m = C.keep_components(m, min_area=600)
    m = ndimage.binary_fill_holes(m)
    a = finish(side, 'seethrough', img, box, R, m, 0.8)
    # UV: the upper pieces fluoresce magenta, the lower pieces white (the HKMA's close-up of this note)
    n, lab, st, cen = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8), 8)
    sy = C.scale(img)[1]
    upper = np.zeros_like(a)
    for k in range(1, n):
        cy = cen[k][1] / sy + box[1]
        if cy < 280:                                                # pieces on the top row
            upper[lab == k] = 1
    upper = cv2.dilate(upper, np.ones((5, 5), np.uint8))
    up = a * upper
    lo = a * (1 - upper)
    white = np.full(R.shape, 255, np.float32)
    C.save_piece(side, 'seethrough-uv-a', img, box, white, up, crop=False)
    C.save_piece(side, 'seethrough-uv-b', img, box, white, lo, crop=False)
    return a


def dark_text(f, name):
    box = BOX[('front', name)]
    R = region(f, box)
    lum = R @ LUM
    sel = C.keep_components(lum < 125, min_area=25)
    a = C.soft_edge(sel, 0.7)                  # black glyphs: crisp shape, counters stay open
    rgb = np.minimum(C.defringe(R, a), 70)     # the ink is black; ESRGAN's coloured fringes dropped
    C.save_piece('front', name, f, box, rgb, a)
    return a


def red_print(f, name, min_area, rg=95):
    box = BOX[('front', name)]
    R = region(f, box)
    r, g = R[..., 0], R[..., 1]
    sel = (r - g > rg) & (r > 150)
    sel = C.keep_components(sel, min_area=min_area)
    a = C.soft_edge(cv2.morphologyEx(sel.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)) > 0, 0.8)
    C.save_piece('front', name, f, box, C.defringe(R, a), a)
    return a


def signature(f):
    box = BOX[('front', 'signature')]
    R = region(f, box)
    paper = C.paper_tone(R, 70)
    r, g = R[..., 0], R[..., 1]
    sel = C.keep_components((r - g > 110) & (np.linalg.norm(R - paper, axis=2) > 60), min_area=30)
    return ink('front', 'signature', f, box, R, sel, paper)


# ---------------------------------------------------------------- watermark
# The HKMA's own close-up of this note's watermark (boc_1000_no5.jpg, 108 x 102, note held to the
# light), upscaled x4 by tools/upscale.py. It is registered onto the artwork by the vertical serial
# number it shows: photo px 14..93 (the 8 characters) and column centre 91.5 map onto the artwork's
# serial at leaflet px 104..197, column 486, i.e. 1.16 leaflet px per photo px.
WM_PHOTO = os.path.join(C.ROOT, 'source', 'watermark-esrgan-x4.png')
WM_K = 1.16                               # leaflet px per photo px
WM_O = (486 - 91.5 * WM_K, 104 - 14 * WM_K)   # leaflet px of the photo's (0, 0)
LEAF = (518, 259)                         # leaflet image size (the artwork's source)


def watermark():
    ph = np.asarray(Image.open(WM_PHOTO).convert('RGB')).astype(np.float32)
    lum = ph @ LUM
    h, w = lum.shape                      # 408 x 432: 4 px per photo px
    q = 4.0
    yy, xx = np.mgrid[0:h, 0:w] / np.array([h, w])[:, None, None]
    X = np.stack([np.ones_like(xx), xx, yy, xx * xx, yy * yy, xx * yy, xx ** 3, yy ** 3], -1).reshape(-1, 8)
    Lf = lum.reshape(-1)
    keep = xx.reshape(-1) < 82 * q / w
    for _ in range(6):                     # backlit paper (lighting gradient) by a robust smooth fit
        c, *_ = np.linalg.lstsq(X[keep], Lf[keep], rcond=None)
        r = Lf - X @ c
        sd = np.std(r[keep])
        keep = keep & (np.abs(r) < 1.5 * sd)
    d = lum - (X @ c).reshape(h, w)        # > 0: thinner paper (the motif's bright lines), < 0: thicker
    d = cv2.GaussianBlur(d, (0, 0), 1.2)
    # only the watermark: not the serial (photo x > 84), the tactile lines (right edge)
    win = np.ones((h, w), np.float32)
    win *= 1 - C.smoothstep(80 * q, 85 * q, np.arange(w))[None, :]
    win *= C.smoothstep(0, 3 * q, np.arange(w))[None, :]
    win *= C.smoothstep(0, 3 * q, np.arange(h))[:, None]
    win *= 1 - C.smoothstep(h - 3 * q, h, np.arange(h))[:, None]
    # printed lines of the front showing through at the top right (not the watermark)
    gx, gy = np.meshgrid(np.arange(w) / q, np.arange(h) / q)
    win *= 1 - C.smoothstep(-6, 0, np.minimum(gx - 56, 24 - gy))
    hp = d - cv2.GaussianBlur(d, (0, 0), 14)
    lite = np.clip((d - 4) / 22, 0, 1) * np.clip((hp + 2) / 6, 0, 1) * win
    dark = np.clip((-hp - 3) / 16, 0, 1) * win * 0.8
    x1 = int(84 * q)
    dark, lite = dark[:, :x1], lite[:, :x1]
    a = np.clip(dark + lite, 0, 1)
    wgt = lite / np.maximum(dark + lite, 1e-4)
    col = np.dstack([(1 - wgt) * 96 + wgt * 255, (1 - wgt) * 84 + wgt * 253, (1 - wgt) * 66 + wgt * 246])
    rgba = np.dstack([col, a * 255]).astype(np.uint8)
    im = Image.fromarray(rgba, 'RGBA')
    im.save(os.path.join(C.LAYERS, 'watermark-ghost.png'), optimize=True)
    os.makedirs(os.path.join(C.CROPS, 'front'), exist_ok=True)
    im.save(os.path.join(C.CROPS, 'front', 'watermark.png'), optimize=True)
    # box in note units: photo px -> leaflet px -> note units
    ux, uy = 720 / LEAF[0], 320 / LEAF[1]
    bx, by = WM_O[0] * ux, WM_O[1] * uy
    bw, bh = 84 * WM_K * ux, (h / q) * WM_K * uy
    C._boxes['watermark-ghost'] = [round(bx, 2), round(by, 2), round(bw, 2), round(bh, 2)]


# ---------------------------------------------------------------- concealed denomination
# The note hides a 1000 in the red diamond lattice of the Bank of China Tower (the HKMA's marker 4 and
# its close-up boc_1000_no4.jpg). The scans cannot show it, so it is drawn: the note's own large 1000
# (the numeral cut-out's shape) filled with a fine diamond lattice in a deeper red of the tower, the way
# the HKMA's close-up shows it. Its exact size and position in the tower's middle section are approximate.
LATENT_BOX = [188, 206, 84, 26]


def latent(f):
    na = np.asarray(Image.open(os.path.join(C.LAYERS, 'front-numeral.png')))[..., 3].astype(np.float32) / 255
    ys, xs = np.where(na > 0.5)
    glyph = na[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    lx0, ly0, lx1, ly1 = C.px(f, LATENT_BOX)
    bw, bh = lx1 - lx0, ly1 - ly0
    k = min(bw / glyph.shape[1], bh / glyph.shape[0])
    g = cv2.resize(glyph, (int(glyph.shape[1] * k), int(glyph.shape[0] * k)), interpolation=cv2.INTER_AREA)
    m = np.zeros((bh, bw), np.float32)
    oy, ox = (bh - g.shape[0]) // 2, (bw - g.shape[1]) // 2
    m[oy:oy + g.shape[0], ox:ox + g.shape[1]] = g
    yy, xx = np.mgrid[0:bh, 0:bw].astype(np.float32)
    p = 9.0                                                            # lattice pitch, px
    d1 = np.abs(((xx + yy) / p) % 1 - 0.5); d2 = np.abs(((xx - yy) / p) % 1 - 0.5)
    lattice = np.clip((0.5 - np.minimum(d1, d2)) * 4 - 0.6, 0, 1)      # diamonds with light ruled gaps
    a = np.clip(m, 0, 1) * (0.62 + 0.38 * lattice)
    R = f[ly0:ly1, lx0:lx1]
    reds = R[(R[..., 0] - R[..., 1] > 70)]
    tone = np.median(reds, axis=0) * 0.72 if len(reds) else np.array([170, 45, 35], np.float32)
    deep = np.broadcast_to(tone, R.shape).copy()
    C.save_piece('front', 'latent', f, LATENT_BOX, deep, a)
    return m


# ---------------------------------------------------------------- masks + offset layers
def mask_uri(a, max_w=360):
    # CSS masks read the image's alpha (mask-mode: match-source), so the mask goes in the alpha channel
    al = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    im = Image.fromarray(np.dstack([np.zeros_like(al), al]), 'LA')
    if im.width > max_w:
        im = im.resize((max_w, max(1, round(im.height * max_w / im.width))), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def layer_alpha(name):
    return np.asarray(Image.open(os.path.join(C.LAYERS, name + '.png')).convert('RGBA'))[..., 3].astype(np.float32) / 255


def write_masks(extra):
    rules = []
    for cls, a, w in extra:
        uri = mask_uri(a, w)
        rules.append(f'.{cls}{{-webkit-mask-image:url({uri});mask-image:url({uri})}}')
    with open(os.path.join(C.ROOT, 'assets', 'masks.css'), 'w') as fh:
        fh.write('/* generated by tools/hkd_features.py: masks that clip the optical effects to the real print */\n')
        fh.write('\n'.join(rules) + '\n')


def paste_alpha(full, name, box):
    a = layer_alpha(name)
    x0, y0, x1, y1 = C.px(full, box)
    h, w = min(a.shape[0], full.shape[0] - y0), min(a.shape[1], full.shape[1] - x0)
    m = np.zeros(full.shape[:2], np.float32)
    m[y0:y0 + h, x0:x0 + w] = a[:h, :w]
    return m


def offset_layer(img, side, names):
    """the print with every separately layered feature taken out (inpainted), for the exploded view"""
    m = np.zeros(img.shape[:2], np.float32)
    for n in names:
        m = np.maximum(m, paste_alpha(img, f'{side}-{n}', C._boxes[f'{side}-{n}']))
    hole = (cv2.dilate((m > 0.05).astype(np.uint8), np.ones((9, 9), np.uint8)))
    small = cv2.resize(img.astype(np.uint8), (img.shape[1] // 2, img.shape[0] // 2), interpolation=cv2.INTER_AREA)
    hs = cv2.resize(hole, (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST)
    out = cv2.inpaint(small, hs, 6, cv2.INPAINT_TELEA)
    Image.fromarray(out).save(os.path.join(C.ROOT, 'assets', f'offset-{side}.jpg'), quality=86)


def main():
    C.load_boxes()
    f, b = C.load('front'), C.load('back')
    print('numeral');    numeral(f)
    print('shimmer');    green(f, 'shimmer', 4000, fill=True)
    print('thread');     green(f, 'thread', 3000, fill=True, rects=True)
    print('seethrough'); seethrough(f, 'front'); seethrough(b, 'back')
    print('text');       dark_text(f, 'serial-h'); dark_text(f, 'serial-v'); signature(f)
    print('red');        red_print(f, 'braille', 40, 80); red_print(f, 'tactile-l', 60); red_print(f, 'tactile-r', 60)
    print('watermark');  watermark()
    print('latent');     lat = latent(f)
    C.write_boxes()
    masks = [
        ('shimmer-fx', layer_alpha('front-shimmer'), 240),
        ('thread-fx', layer_alpha('front-thread'), 60),
        ('latent-fx', lat, 240),
    ]
    for side, cls in (('front', 'flow-front'), ('back', 'flow-back')):
        p = os.path.join(C.ROOT, 'source', f'linework-{side}.png')
        if os.path.exists(p):
            masks.append((cls, np.asarray(Image.open(p).convert('L')).astype(np.float32) / 255, 720))
    write_masks(masks)
    print('offset layers')
    offset_layer(f, 'front', ['numeral', 'shimmer', 'thread', 'seethrough', 'serial-h', 'serial-v', 'braille',
                              'tactile-l', 'tactile-r'])
    offset_layer(b, 'back', ['seethrough'])


if __name__ == '__main__':
    main()
