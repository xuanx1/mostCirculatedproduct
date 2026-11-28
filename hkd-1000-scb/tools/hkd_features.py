"""
Cut every HK$1,000 (Standard Chartered, 2018 Series) feature out of the working artwork as a clean alpha
layer, build the watermark from the HKMA's close-up photograph of this note's watermark, and write the
page's masks and boxes.

  python tools/hkd_features.py          (run tools/sam_isolate.py first for the bank buildings and the skyline)

Each feature is isolated by its own rule (no hand painting), always from the original pixels:
  ink        the large 1000: every pixel clearly away from the paper colour (counters stay open)
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
assets/layers/watermark-ghost.png and assets/layers/front-latent.png
(source/numeral-1000-mask.png: the joined see-through 1000 the latent image is drawn from).
Hand-cleaned files in assets/overrides/ always win.
"""
import base64, io, os
import numpy as np
import cv2
from PIL import Image, ImageFilter
from scipy import ndimage

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

LUM = np.array([.299, .587, .114], np.float32)

# boxes in note units [x, y, w, h] (checked against tools/grid.py overlays of the artwork)
BOX = {
    ('front', 'numeral'):    [10, 10, 204, 78],      # large 1000, top left (embossed feel)
    ('front', 'shimmer'):    [544, 16, 116, 100],    # bauhinia: dynamic shimmering pattern
    ('front', 'thread'):     [449, 54, 34, 254],     # the three windows of the metallic thread
    ('front', 'seethrough'): [526, 256, 146, 58],    # front half of the see-through 1000
    ('back', 'seethrough'):  [46, 256, 140, 58],     # back half
    ('front', 'serial-h'):   [40, 260, 108, 24],
    ('front', 'serial-v'):   [664, 122, 24, 126],
    ('front', 'braille'):    [40, 282, 112, 26],
    ('front', 'tactile-l'):  [0, 130, 24, 180],
    ('front', 'tactile-r'):  [696, 136, 24, 174],
    ('front', 'signature'):  [36, 176, 166, 34],     # the two signatures (Chief Financial Officer, Chief Executive)
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


# ---------------------------------------------------------------- features
def numeral(f):
    """the large 1000: red and olive ink on the peach paper. The digits are every pixel clearly away from
    the paper's colour; the counters of the 0s are paper, so they stay open by construction."""
    box = BOX[('front', 'numeral')]
    R = region(f, box)
    paper = C.paper_tone(R, 70)
    d = np.linalg.norm(R - paper, axis=2)
    m = cv2.morphologyEx((d > 45).astype(np.uint8), cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    m = C.keep_components(m, min_area=5000)
    m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.5) > 0.5          # smooth outline, no stair-steps
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
    b = R[..., 2]
    r, g = R[..., 0], R[..., 1]
    m = (b < 125) & (r > 170) & (r - b > 110)                       # flat orange print
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
    m = C.keep_components(m, min_area=600)
    m = ndimage.binary_fill_holes(m)
    a = finish(side, 'seethrough', img, box, R, m, 0.8)
    # UV: the upper pieces fluoresce one colour, the lower pieces another (HKMA leaflet image)
    n, lab, st, cen = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8), 8)
    sy = C.scale(img)[1]
    upper = np.zeros_like(a)
    for k in range(1, n):
        top = st[k, cv2.CC_STAT_TOP] / sy + box[1]
        if top < 270:                                               # pieces that start on the top row
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


def red_print(f, name, min_area):
    box = BOX[('front', name)]
    R = region(f, box)
    r, g = R[..., 0], R[..., 1]
    sel = (r - g > 95) & (r > 150)
    sel = C.keep_components(sel, min_area=min_area)
    a = C.soft_edge(cv2.morphologyEx(sel.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)) > 0, 0.8)
    C.save_piece('front', name, f, box, C.defringe(R, a), a)
    return a


def signature(f):
    box = BOX[('front', 'signature')]
    R = region(f, box)
    paper = C.paper_tone(R, 70)
    d = np.linalg.norm(R - paper, axis=2)
    sel = C.keep_components(d > 60, min_area=30)
    return ink('front', 'signature', f, box, R, sel, paper)


# ---------------------------------------------------------------- watermark
# The HKMA's close-up of this note's watermark (scb_1000_no5.jpg, 108 x 102), upscaled x4 by
# tools/upscale.py. It is registered onto the artwork by the vertical serial number column it shows
# (glyph pitch 41.1 photo px = 67.9 artwork px, so 1.651 artwork px per photo px; the first glyph's
# top-centre, photo px (353.5, 65), lands on the artwork's, px (2703, 567)): note units below.
WM_PHOTO = os.path.join(C.ROOT, 'source', 'watermark-esrgan-x4.png')
WM_SCALE = 1.651
WM_ORIGIN = ((2703 - 353.5 * WM_SCALE) / 4, (567 - 65 * WM_SCALE) / 4.5)
WM_X1 = 334                                # right of this: the serial and the tactile lines


def watermark():
    ph = np.asarray(Image.open(WM_PHOTO).convert('RGB')).astype(np.float32)
    lum = ph @ LUM
    h, w = lum.shape
    yy, xx = np.mgrid[0:h, 0:w] / np.array([h, w])[:, None, None]
    X = np.stack([np.ones_like(xx), xx, yy, xx * xx, yy * yy, xx * yy, xx ** 3, yy ** 3], -1).reshape(-1, 8)
    Lf = lum.reshape(-1)
    keep = (xx.reshape(-1) < WM_X1 / w) & (yy.reshape(-1) > 40 / h)
    for _ in range(6):                     # paper (backlight gradient) by a robust smooth fit
        c, *_ = np.linalg.lstsq(X[keep], Lf[keep], rcond=None)
        r = Lf - X @ c
        sd = np.std(r[keep])
        keep = keep & (np.abs(r) < 1.5 * sd)
    d = lum - (X @ c).reshape(h, w)        # < 0: the watermark's shadows, > 0: its bright parts
    d = cv2.GaussianBlur(d, (0, 0), 2.2)   # a watermark is soft: the upscaler's crisp edges are eased
    win = np.ones((h, w), np.float32)
    win *= C.smoothstep(2, 16, np.arange(w))[None, :]
    win *= 1 - C.smoothstep(WM_X1 - 18, WM_X1, np.arange(w))[None, :]
    win *= C.smoothstep(34, 52, np.arange(h))[:, None]        # the bauhinia's print at the photo's top edge
    win *= 1 - C.smoothstep(h - 14, h, np.arange(h))[:, None]
    hp = d - cv2.GaussianBlur(d, (0, 0), 18)                  # broad shading removed: the motif's own relief stays
    dark = np.clip((-hp - 3) / 26, 0, 1) * win
    lite = np.clip((hp - 2) / 16, 0, 1) * win
    x0, x1 = 0, WM_X1
    dark, lite = dark[:, x0:x1], lite[:, x0:x1]
    # one RGBA: warm grey shading, white highlights (a watermark is paper, thicker or thinner)
    a = np.clip(dark + lite, 0, 1)
    wgt = lite / np.maximum(dark + lite, 1e-4)
    col = np.dstack([(1 - wgt) * 96 + wgt * 255, (1 - wgt) * 84 + wgt * 253, (1 - wgt) * 66 + wgt * 246])
    rgba = np.dstack([col, a * 255]).astype(np.uint8)
    im = Image.fromarray(rgba, 'RGBA')
    im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
    im.save(os.path.join(C.LAYERS, 'watermark-ghost.png'), optimize=True)
    os.makedirs(os.path.join(C.CROPS, 'front'), exist_ok=True)
    im.save(os.path.join(C.CROPS, 'front', 'watermark.png'), optimize=True)
    # box in note units: photo px -> artwork px (x WM_SCALE) -> note units (/4, /4.5)
    bx = WM_ORIGIN[0] + x0 * WM_SCALE / 4
    bw = (x1 - x0) * WM_SCALE / 4
    by, bh = WM_ORIGIN[1], h * WM_SCALE / 4.5
    C._boxes['watermark-ghost'] = [round(bx, 2), round(by, 2), round(bw, 2), round(bh, 2)]


# ---------------------------------------------------------------- concealed denomination
# The note hides a 1000 in its background. The HKMA marks it on the red lower part of the Standard
# Chartered Bank Building, and its close-up (scb_1000_no4.jpg) shows a red 1000 in fine lines there.
# The scans cannot show it, so it is drawn: the note's own 1000 numerals (the front and back
# see-through halves joined, exactly as they register) filled with fine horizontal lines in the
# area's own red, darker. Its exact position and size are approximate. Illustrative.
LATENT_BOX = [334, 218, 62, 26]


def latent(f, b):
    fa = np.asarray(Image.open(os.path.join(C.LAYERS, 'front-seethrough.png')))[..., 3].astype(np.float32) / 255
    ba = np.asarray(Image.open(os.path.join(C.LAYERS, 'back-seethrough.png')))[..., 3].astype(np.float32) / 255
    # place both halves in front coordinates (the back half seen through the paper: mirrored)
    sx, sy = C.scale(f)
    fb, bb = C._boxes['front-seethrough'], C._boxes['back-seethrough']
    W, H = int(720 * sx), int(320 * sy)
    canvas = np.zeros((H, W), np.float32)
    x0, y0 = int(round(fb[0] * sx)), int(round(fb[1] * sy))
    canvas[y0:y0 + fa.shape[0], x0:x0 + fa.shape[1]] = np.maximum(canvas[y0:y0 + fa.shape[0], x0:x0 + fa.shape[1]], fa)
    bm = ba[:, ::-1]
    bx0 = int(round((720 - bb[0] - bb[2]) * sx)); by0 = int(round(bb[1] * sy))
    canvas[by0:by0 + bm.shape[0], bx0:bx0 + bm.shape[1]] = np.maximum(canvas[by0:by0 + bm.shape[0], bx0:bx0 + bm.shape[1]], bm)
    ys, xs = np.where(canvas > 0.5)
    glyph = canvas[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    # join the seams between the two halves (they meet edge to edge)
    glyph = cv2.morphologyEx(glyph, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
    Image.fromarray((glyph * 255).astype(np.uint8)).save(os.path.join(C.ROOT, 'source', 'numeral-1000-mask.png'))
    # fit into the latent box, keeping the glyph's proportions
    lx0, ly0, lx1, ly1 = C.px(f, LATENT_BOX)
    bw, bh = lx1 - lx0, ly1 - ly0
    k = min(bw / glyph.shape[1], bh / glyph.shape[0])
    g = cv2.resize(glyph, (int(glyph.shape[1] * k), int(glyph.shape[0] * k)), interpolation=cv2.INTER_AREA)
    m = np.zeros((bh, bw), np.float32)
    oy, ox = (bh - g.shape[0]) // 2, (bw - g.shape[1]) // 2
    m[oy:oy + g.shape[0], ox:ox + g.shape[1]] = g
    lines = (np.sin(np.arange(bh) / bh * np.pi * 2 * 34)[:, None] > -0.2).astype(np.float32)
    a = np.clip(m, 0, 1) * (0.55 + 0.45 * lines)
    R = f[ly0:ly1, lx0:lx1]
    reds = R[(R[..., 0] - R[..., 1] > 90)]
    tone = np.median(reds, axis=0) * np.array([.82, .55, .55], np.float32) if len(reds) else np.array([190, 50, 40], np.float32)
    deep = np.broadcast_to(tone, R.shape).copy()                       # the area's own red, darker
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
    print('red');        red_print(f, 'braille', 40); red_print(f, 'tactile-l', 60); red_print(f, 'tactile-r', 60)
    print('watermark');  watermark()
    print('latent');     lat = latent(f, b)
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
