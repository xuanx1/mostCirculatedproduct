"""
Clean alpha cut-outs of the Australian $100's features, from the working artwork (aud-100-*.png,
made by tools/prepare_art.py) and the SAM masks (tools/sam_masks.py).

  python tools/cut_features.py

Modes (boxes in the page's 720 x 320 note units):
  win      print standing in a clear window: the window matte already separates it from the polymer,
           so the cut is the artwork's own alpha inside the box (connected pieces mostly inside)
  region   a whole window: everything inside the clear area and its print
  sam      a SAM mask (source/sam/<side>-<name>.png) applied to the artwork, ~1 px anti-aliased edge
  ink      dark printing (numerals, text, serial): strokes darker than their local background; counters
           (inside 0, 4, 6, 8, 9, A ...) stay open; only pieces mostly inside the box are kept
  wattle   the wattle branch: dark leaves, yellow flowers and the stem, by colour against the tint
  bumps    the tactile bumps: small round cuts of the artwork centred on each bump

Writes, per piece, assets/layers/<side>-<name>.png (original pixels, transparent background, framed
to its own box) and assets/boxes.js (where each piece sits). Also:
  assets/offset-<side>.webp   offset print: the artwork with intaglio lines lifted off, the windows
                              clear and the separately layered patches removed (exploded view)
  assets/polymer.png          the polymer substrate with its clear windows (exploded view)
  assets/masks.css            effect masks as data URIs (so file:// works)
  feature-crops/              full-resolution copies and a contact sheet on a dark background
Hand-cleaned files in assets/overrides/ (same names) always win and are never overwritten.
"""
import base64, io, json, os, shutil
import numpy as np
import cv2
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYERS = os.path.join(ROOT, 'assets', 'layers')
OVR = os.path.join(ROOT, 'assets', 'overrides')
CROPS = os.path.join(ROOT, 'feature-crops')
VB_W, VB_H = 720, 320

# name: (side, mode, box (x0, y0, x1, y1), options)
PIECES = {
    # ---- Melba (signature) side ----
    'front-window':      ('front', 'region', (166, 0, 344, 320), {'win': 'main'}),
    'front-fan3d':       ('front', 'win', (220, 12, 284, 58), {'largest': True, 'sep': 0.6}),
    'front-flyingowl':   ('front', 'win', (218, 44, 290, 108), {'t': 0.3, 'thin': True, 'lines': True, 'near': 1.0, 'drop': [(222, 64, 239, 92)]}),
    'front-colourowl':   ('front', 'win', (220, 132, 270, 228), {'largest': True, 'sep': 2.2, 'regrow': 0.5}),
    'front-shrine':      ('front', 'win', (218, 254, 284, 306), {'largest': True, 'sep': 0.8, 'near': 3}),
    'front-window-100':  ('front', 'win', (224, 114, 262, 136), {'min': 3}),
    'front-fanwin':      ('front', 'region', (580, 192, 694, 314), {'win': 'fan', 'tint': True}),
    'front-rolling':     ('front', 'sam', (20, 22, 130, 106), {}),
    'front-portrait':    ('front', 'sam', (344, 4, 538, 298), {}),
    'front-rosina':      ('front', 'sam', (516, 94, 610, 276), {}),
    'front-100':         ('front', 'ink', (540, 12, 708, 106), {'solid': True, 'min': 60}),
    'front-microprint':  ('front', 'ink', (588, 146, 642, 182), {'otsu': True, 'k': 0.97,
                          'poly': [(602, 151.5), (637, 151.5), (636, 161), (629, 172), (619, 179), (604, 179), (596, 172), (591, 160)]}),
    'front-wattle':      ('front', 'wattle', (8, 92, 166, 192), {'drop': [(52, 84, 122, 118)]}),
    'front-lines':       ('front', 'lines', (328, 4, 354, 236), {}),
    'back-lines':        ('back', 'lines', (346, 4, 386, 262), {}),
    'front-tactile':     ('front', 'bumps', (12, 8, 168, 30), {'at': [(25.3, 18.2), (57.2, 18.2), (90.0, 18.2), (121.9, 18.2), (153.8, 18.2)], 'r': 4.2}),
    # ---- Monash (serial number) side ----
    'back-window':       ('back', 'region', (376, 0, 554, 320), {'win': 'main'}),
    'back-fanwin':       ('back', 'region', (26, 192, 140, 314), {'win': 'fan', 'tint': True}),
    'back-window-text':  ('back', 'win', (438, 136, 500, 262), {'thin': True, 'drop_largest': True, 'sep': 1.2, 'min': 0.3, 'drop': [(440, 220, 468, 242)]}),
    'back-rolling':      ('back', 'sam', (574, 22, 700, 158), {}),
    'back-portrait':     ('back', 'sam', (132, 22, 358, 306), {}),
    'back-shrine':       ('back', 'sam', (30, 28, 178, 160), {}),
    'back-100':          ('back', 'ink', (536, 204, 710, 310), {'solid': True, 'min': 60}),
    'back-serial':       ('back', 'ink', (2, 48, 28, 196), {'solid': True, 't': 120, 'close': 0.15, 'open': 0.3, 'min': 1.5}),
}


def disk(r):
    r = max(1, int(round(r)))
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def fill_holes(m, max_area=None):
    inv = cv2.bitwise_not(m)
    n, lab, st, _ = cv2.connectedComponentsWithStats(inv, 4)
    out = m.copy()
    H, W = m.shape
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if x == 0 or y == 0 or x + w == W or y + h == H:
            continue
        if max_area is None or a <= max_area:
            out[lab == i] = 255
    return out


def keep_inside(m, seed, frac=0.6, min_area=0):
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    out = np.zeros_like(m)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] < min_area:
            continue
        comp = lab == i
        if (comp & seed).sum() / st[i, cv2.CC_STAT_AREA] >= frac:
            out[comp] = 255
    return out


def aa(binary, s=0.8):
    f = cv2.GaussianBlur(binary.astype(np.float32) / 255, (0, 0), s)
    return np.clip((f - 0.5) * 2.2 + 0.5, 0, 1)


class Art:
    def __init__(self, side):
        im = Image.open(os.path.join(ROOT, f'aud-100-{side}.png')).convert('RGBA')
        self.rgba = np.asarray(im).copy()
        self.H, self.W = self.rgba.shape[:2]
        self.sx, self.sy = self.W / VB_W, self.H / VB_H
        self.s = (self.sx + self.sy) / 2
        win = np.asarray(Image.open(os.path.join(ROOT, 'source', f'window-{side}.png'))) > 0
        self.win = win
        # levelled scan before the window matte: foil keeps its real (dark) reflections
        self.flat = np.asarray(Image.open(os.path.join(ROOT, 'source', f'flat-{side}.png')).convert('RGB'))

    def px(self, box):
        x0, y0, x1, y1 = box
        return (max(0, int(round(x0 * self.sx))), max(0, int(round(y0 * self.sy))),
                min(self.W, int(round(x1 * self.sx))), min(self.H, int(round(y1 * self.sy))))


def cut_piece(art, name, side, mode, box, o):
    X0, Y0, X1, Y1 = art.px(box)
    rgba = art.rgba[Y0:Y1, X0:X1].astype(np.float32)
    rgb, A = rgba[..., :3], rgba[..., 3] / 255
    h, w = A.shape
    seed = np.zeros((h, w), bool)
    seed[:, :] = True
    for dx0, dy0, dx1, dy1 in o.get('drop', []):
        a0, b0, a1, b1 = art.px((dx0, dy0, dx1, dy1))
        seed[max(0, b0 - Y0):max(0, b1 - Y0), max(0, a0 - X0):max(0, a1 - X0)] = False
    if o.get('poly'):
        pm = np.zeros((h, w), np.uint8)
        cv2.fillPoly(pm, [np.array([(int(round(x * art.sx - X0)), int(round(y * art.sy - Y0))) for x, y in o['poly']], np.int32)], 255)
        seed &= pm > 0
    s = art.s
    win_crop = art.win[Y0:Y1, X0:X1]
    if mode == 'win':
        # print in the window = the matte's alpha inside the window (outside it the polymer is opaque)
        a = A * win_crop
        m = ((a > o.get('t', 0.35)) * 255).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, disk((0.15 if o.get('thin') else 0.25) * s))
        if o.get('lines'):
            m[~seed] = 0
            n_, lab_, st_, _ = cv2.connectedComponentsWithStats(m, 8)
            m = np.isin(lab_, [i for i in range(1, n_) if st_[i, cv2.CC_STAT_AREA] >= o.get('min', 0.12) * s * s]).astype(np.uint8) * 255
        else:
            m = keep_inside(m, seed & _inner(h, w, 2 * s), 0.85, int(o.get('min', 0.12) * s * s))
        if o.get('lines'):
            # line art (the flying owl): the largest connected line network, and short bits close to it
            n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
            if n > 1:
                k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
                core = ((lab == k) * 255).astype(np.uint8)
                m = cv2.bitwise_or(core, keep_inside(m, cv2.dilate(core, disk(o.get('near', 1.0) * s)) > 0, 0.99))
        if o.get('largest') or o.get('drop_largest'):
            # separate what merely touches the object (micro-text, wattle dots), then grow back
            core = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(o.get('sep', 1.0) * s))
            n, lab, st, _ = cv2.connectedComponentsWithStats(core, 8)
            if n > 1:
                k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
                core = ((lab == k) * 255).astype(np.uint8)
                body = cv2.bitwise_and(cv2.dilate(core, disk(o.get('regrow', o.get('sep', 1.0) + 0.1) * s)), m)
                if o.get('drop_largest'):
                    m = cv2.bitwise_and(m, cv2.bitwise_not(cv2.dilate(body, disk(0.4 * s))))
                else:
                    near = o.get('near', 0)
                    if near:                                 # small parts that belong (the Shrine's cross)
                        zone = cv2.dilate(body, disk(near * s))
                        body = cv2.bitwise_or(body, keep_inside(m, zone > 0, 0.99))
                    m = fill_holes(body)
                    rgb = art.flat[Y0:Y1, X0:X1].astype(np.float32)   # a solid foil: its real colours
                    a = np.maximum(a, (m > 0).astype(np.float32))
        reach = cv2.dilate(m, disk(0.5 * s)) > 0
        alpha = np.where(reach, a, 0)
        alpha = np.maximum(alpha, aa(cv2.erode(m, disk(0.4 * s))) * (alpha > 0.05))
        if o.get('largest'):
            alpha = aa(cv2.dilate(m, disk(0.25 * s))) * (A > 0.02)
    elif mode == 'region':
        reg = (win_crop * 255).astype(np.uint8)
        reg = cv2.dilate(reg, disk(0.8 * s))
        reg = keep_inside(reg, _inner(h, w, 1), 0.8, int((3 * s) ** 2))     # this window's parts, not a neighbour's
        alpha = A * aa(reg, 0.6)
        # the clear polymer itself has no pixels of its own in the scan: a pale tint shows the
        # window's shape (illustrative), the print in it keeps its own pixels
        clear = aa(reg, 0.6) * (1 - A) * bool(o.get('tint'))
        tint = np.array([232, 244, 250], np.float32)
        rgb = rgb * A[..., None] + tint * (1 - A[..., None])
        alpha = alpha + clear * 0.42
    elif mode == 'sam':
        mp = os.path.join(ROOT, 'source', 'sam', f'{side}-{name.split("-", 1)[1]}.png')
        if not os.path.exists(mp):
            raise SystemExit(f'missing {mp}: run tools/sam_masks.py first')
        mk = np.asarray(Image.open(mp))[Y0:Y1, X0:X1]
        mk = cv2.morphologyEx(mk, cv2.MORPH_OPEN, disk(0.5 * s))
        alpha = aa(mk) * A
    elif mode == 'ink':
        lab = cv2.cvtColor(np.ascontiguousarray(rgb.astype(np.uint8)), cv2.COLOR_RGB2LAB).astype(np.float32)
        L = lab[..., 0]
        if o.get('solid'):
            # bold numerals: very dark, thick strokes with hatching; thin lines around are opened away
            t = o.get('t', 95)
            m = ((L < t) * 255).astype(np.uint8)
            m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, disk(o.get('close', 0.5) * s))
            m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(o.get('open', 1.5) * s))
            m = fill_holes(m, int((1.5 * s) ** 2))           # hatching gaps inside strokes, not counters
            m = keep_inside(m, seed, 0.9, int(o.get('min', 1) * s * s))
            alpha = aa(m) * A
        elif o.get('otsu'):
            # a block of micro-text: letters darker than the block's own paper (threshold chosen in the block)
            v = np.clip(L[seed], 0, 255).astype(np.uint8).reshape(-1, 1)
            t, _ = cv2.threshold(v, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            t = t * o.get('k', 1.0)
            m = (((L < t) & seed) * 255).astype(np.uint8)
            n_, lab_, st_, _ = cv2.connectedComponentsWithStats(m, 8)
            big = [i for i in range(1, n_) if st_[i, cv2.CC_STAT_AREA] > (2.5 * s) ** 2]   # not hair / scroll lines
            m[np.isin(lab_, big)] = 0
            ramp = np.clip((t + 12 - L) / 24, 0, 1)
            alpha = ramp * (cv2.dilate(m, disk(0.25 * s)) > 0) * A
        else:
            # text: strokes darker than the local background
            bg = cv2.morphologyEx(L, cv2.MORPH_CLOSE, disk(o.get('bgr', 1.2) * s))
            bg = cv2.GaussianBlur(bg, (0, 0), 0.6 * s)
            dark = bg - L
            t = o.get('dark', 40)
            m = ((dark > t) * 255).astype(np.uint8)
            if o.get('open'):
                m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(o['open'] * s))
            m = keep_inside(m, seed, 0.9, int(o.get('min', 0.1) * s * s))
            ramp = np.clip((dark - t * 0.5) / (t * 0.8), 0, 1)
            alpha = np.maximum(ramp * (cv2.dilate(m, disk(0.3 * s)) > 0), aa(m, 0.6)) * A
    elif mode == 'wattle':
        lab = cv2.cvtColor(np.ascontiguousarray(rgb.astype(np.uint8)), cv2.COLOR_RGB2LAB).astype(np.float32)
        L, Bb = lab[..., 0], lab[..., 2]
        bgL = cv2.GaussianBlur(cv2.medianBlur(L.astype(np.uint8), int(4 * s) | 1).astype(np.float32), (0, 0), 3 * s)
        bgB = cv2.GaussianBlur(cv2.medianBlur(Bb.astype(np.uint8), int(4 * s) | 1).astype(np.float32), (0, 0), 3 * s)
        u8 = lambda b: (b * 255).astype(np.uint8)
        leaves = cv2.morphologyEx(u8((bgL - L) > 32), cv2.MORPH_OPEN, disk(0.35 * s))   # spurs of the tint
        flowers = cv2.morphologyEx(u8((Bb - bgB) > 14), cv2.MORPH_CLOSE, disk(0.35 * s))
        flowers = cv2.morphologyEx(fill_holes(flowers, int((2.2 * s) ** 2)), cv2.MORPH_OPEN, disk(0.5 * s))
        flowers = keep_inside(flowers, np.ones_like(seed), 0, int((2.2 * s) ** 2))   # flower heads, not tint specks
        flowers = cv2.dilate(flowers, disk(0.2 * s)) & cv2.morphologyEx(u8((Bb - bgB) > 10), cv2.MORPH_CLOSE, disk(0.35 * s))
        flowers = fill_holes(flowers, int((2.2 * s) ** 2))
        m = cv2.morphologyEx(leaves | flowers, cv2.MORPH_CLOSE, disk(0.4 * s))
        m = fill_holes(m, int((1.5 * s) ** 2))
        m = keep_inside(m, seed, 0.9, int((1.2 * s) ** 2))
        alpha = aa(m) * A
    elif mode == 'lines':
        # fine-line background print: lines darker than the tint around them, minus dark text
        lab = cv2.cvtColor(np.ascontiguousarray(rgb.astype(np.uint8)), cv2.COLOR_RGB2LAB).astype(np.float32)
        L = lab[..., 0]
        bg = cv2.GaussianBlur(cv2.morphologyEx(L, cv2.MORPH_CLOSE, disk(0.8 * s)), (0, 0), 0.8 * s)
        lines = np.clip((bg - L - 4) / 14, 0, 1)
        text = cv2.dilate(cv2.morphologyEx(((L < 150) * 255).astype(np.uint8), cv2.MORPH_OPEN, disk(0.25 * s)), disk(1.0 * s)) > 0
        lines[text] = 0
        fade = cv2.GaussianBlur(_inner(h, w, 3 * s).astype(np.float32), (0, 0), 2 * s)   # soft edge of the sample
        alpha = lines * fade * A
    elif mode == 'bumps':
        m = np.zeros((h, w), np.uint8)
        for cx, cy in o['at']:
            cv2.circle(m, (int(round(cx * art.sx - X0)), int(round(cy * art.sy - Y0))), int(round(o['r'] * s)), 255, -1)
        alpha = aa(m, 1.2) * A
    else:
        raise ValueError(mode)
    out = np.dstack([rgb, alpha * 255]).clip(0, 255).astype(np.uint8)
    return out, (X0, Y0)


def _inner(h, w, margin):
    m = np.zeros((h, w), bool)
    k = int(margin)
    m[k:h - k or h, k:w - k or w] = True
    return m


def frame(art, out, origin, pad_u=1.0):
    """Trim to the alpha's own extent plus a margin; return the image and its box in note units."""
    a = out[..., 3]
    ys, xs = np.where(a > 4)
    if not len(xs):
        return Image.fromarray(out, 'RGBA'), [0, 0, 1, 1]
    p = int(round(pad_u * art.s))
    y0, y1 = max(0, ys.min() - p), min(out.shape[0], ys.max() + p + 1)
    x0, x1 = max(0, xs.min() - p), min(out.shape[1], xs.max() + p + 1)
    X0, Y0 = origin
    box = [round((X0 + x0) / art.sx, 2), round((Y0 + y0) / art.sy, 2),
           round((x1 - x0) / art.sx, 2), round((y1 - y0) / art.sy, 2)]
    return Image.fromarray(out[y0:y1, x0:x1], 'RGBA'), box


def offset_layer(art, side, remove):
    """What is printed under the intaglio and the patches: dark lines lifted off by a per-channel
    closing (the light tint either side of a line closes over it), only inside the intaglio pieces;
    the patches filled from their surroundings; the windows left clear."""
    rgba = art.rgba.copy()
    rgb = np.ascontiguousarray(rgba[..., :3])
    L = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
    closed = cv2.merge([cv2.morphologyEx(rgb[..., c], cv2.MORPH_CLOSE, disk(7)) for c in range(3)])
    closed = cv2.merge([cv2.morphologyEx(closed[..., c], cv2.MORPH_CLOSE, disk(11)) for c in range(3)])
    bgL = cv2.cvtColor(closed, cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
    zone = np.zeros(L.shape, np.float32)
    blobs = np.zeros(L.shape, np.uint8)
    for kind, m in remove:
        if kind == 'lines':
            zone = np.maximum(zone, m)
        else:
            blobs = np.maximum(blobs, (m > 0.1).astype(np.uint8) * 255)
    a = np.clip((bgL - L - 6) / 14, 0, 1) * cv2.GaussianBlur(zone, (0, 0), 2)
    a = cv2.GaussianBlur(a, (0, 0), 1.0)[..., None]
    out = (rgb * (1 - a) + closed * a).astype(np.uint8)
    blobs = cv2.dilate(blobs, disk(5))
    q = 4
    H, W = L.shape
    small = cv2.resize(out, (W // q, H // q), interpolation=cv2.INTER_AREA)
    ms = cv2.resize(blobs, (W // q, H // q), interpolation=cv2.INTER_NEAREST)
    f = cv2.inpaint(cv2.cvtColor(small, cv2.COLOR_RGB2BGR), ms, 12, cv2.INPAINT_TELEA)
    f = cv2.cvtColor(cv2.resize(f, (W, H), interpolation=cv2.INTER_CUBIC), cv2.COLOR_BGR2RGB)
    b = cv2.GaussianBlur(blobs.astype(np.float32) / 255, (0, 0), 3.0)[..., None]
    out = (out * (1 - b) + f * b).astype(np.uint8)
    # the windows are clear in this layer: their print is its own layer
    clear = cv2.dilate((art.win * 255).astype(np.uint8), disk(1.0 * art.s))
    alpha = (1 - aa(clear, 1.0)) * 255
    img = Image.fromarray(np.dstack([out, alpha.astype(np.uint8)]), 'RGBA').resize((2160, 889), Image.LANCZOS)
    img.save(os.path.join(ROOT, 'assets', f'offset-{side}.webp'), quality=88, method=6)


def polymer_layer(art_front):
    """The substrate: polymer with its opacifying layers, clear where the windows are."""
    W, H = 1440, 592
    win = cv2.resize((art_front.win * 255).astype(np.uint8), (W, H), interpolation=cv2.INTER_AREA)
    win = cv2.GaussianBlur(win.astype(np.float32) / 255, (0, 0), 0.8)
    rgb = np.empty((H, W, 3), np.float32)
    rgb[:] = (250, 250, 246)
    rgb = rgb * (1 - win[..., None]) + np.array([226, 240, 248], np.float32) * win[..., None]
    alpha = 0.94 * (1 - win) + 0.16 * win
    Image.fromarray(np.dstack([rgb, alpha * 255]).astype(np.uint8), 'RGBA').save(
        os.path.join(ROOT, 'assets', 'polymer.png'), optimize=True)


MASK_RULES = {      # page selector -> piece whose alpha clips the effect
    '.fan-fx': 'front-fan3d', '.fly-fx': 'front-flyingowl', '.cowl-fx': 'front-colourowl',
    '.rev-fx': 'front-shrine', '.roll-fx.f': 'front-rolling', '.roll-fx.b': 'back-rolling',
    '.emb-fx.f': 'front-fanwin', '.emb-fx.b': 'back-fanwin',
    '.uvm-front-flyingowl': 'front-flyingowl', '.uvm-front-wattle': 'front-wattle', '.uvm-back-serial': 'back-serial',
}


def data_uri(img, maxdim=600):
    a = img.getchannel('A')
    k = min(1.0, maxdim / max(a.size))
    if k < 1:
        a = a.resize((round(a.width * k), round(a.height * k)), Image.LANCZOS)
    m = Image.new('LA', a.size, 255)
    m.putalpha(a)
    buf = io.BytesIO()
    m.save(buf, 'PNG', optimize=True)
    return f'url("data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}")'


def linework_rules():
    """Fine-line background print of each face (lines darker than their surroundings) as a luminance
    mask, for the colour flow that shows the background print."""
    rules = []
    for side, cls in (('front', '.flow-front'), ('back', '.flow-back')):
        im = Image.open(os.path.join(ROOT, f'aud-100-{side}.png')).convert('RGB').resize((1080, 444), Image.LANCZOS)
        L = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
        bg = cv2.GaussianBlur(cv2.morphologyEx(L, cv2.MORPH_CLOSE, disk(3)), (0, 0), 3)
        lines = (bg - L - 7) > 0
        win = cv2.resize((np.asarray(Image.open(os.path.join(ROOT, 'source', f'window-{side}.png'))) > 0).astype(np.uint8), (1080, 444)) > 0
        lines &= ~cv2.dilate(win.astype(np.uint8), disk(4)).astype(bool)
        a = Image.fromarray((lines * 255).astype(np.uint8)).convert('1')
        buf = io.BytesIO()
        a.save(buf, 'PNG', optimize=True)
        u = f'url("data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}")'
        rules.append(f'{cls}{{-webkit-mask-mode:luminance;mask-mode:luminance;-webkit-mask-image:{u};mask-image:{u}}}')
    return rules


def contact_sheet(files):
    cols, cw, ch = 5, 330, 270
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * cw, rows * ch), (24, 26, 32))
    d = ImageDraw.Draw(sheet)
    for i, (n, img) in enumerate(files):
        t = img.copy()
        t.thumbnail((cw - 20, ch - 34))
        cx, cy = (i % cols) * cw, (i // cols) * ch
        sheet.paste(t, (cx + (cw - t.width) // 2, cy + 8), t)
        d.text((cx + 8, cy + ch - 20), n, fill=(230, 230, 230))
    sheet.save(os.path.join(CROPS, 'contact-sheet.png'))


def main():
    os.makedirs(LAYERS, exist_ok=True)
    os.makedirs(CROPS, exist_ok=True)
    arts = {s: Art(s) for s in ('front', 'back')}
    boxes, imgs, full = {}, {}, {}
    for name, (side, mode, box, o) in PIECES.items():
        art = arts[side]
        out, origin = cut_piece(art, name, side, mode, box, o)
        img, b = frame(art, out, origin)
        ov = os.path.join(OVR, name + '.png')
        if os.path.exists(ov):                               # hand-cleaned file wins
            img = Image.open(ov).convert('RGBA').resize(img.size, Image.LANCZOS)
            print('  using override', name)
        img.save(os.path.join(LAYERS, name + '.png'), optimize=True)
        img.save(os.path.join(CROPS, name + '.png'), optimize=True)
        boxes[name] = b
        imgs[name] = img
        fm = np.zeros((art.H, art.W), np.float32)            # full-size alpha, for the offset layer
        x0, y0 = int(round(b[0] * art.sx)), int(round(b[1] * art.sy))
        a = np.asarray(img.getchannel('A'), np.float32) / 255
        fm[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a[:art.H - y0, :art.W - x0]
        full[name] = fm
        print(f'{name:20} {mode:7} box {b}')
    with open(os.path.join(ROOT, 'assets', 'boxes.js'), 'w', encoding='utf8') as f:
        f.write('// generated by tools/cut_features.py: where each cut-out sits (720 x 320 note units)\n')
        f.write('const BOXES = ' + json.dumps(boxes, indent=1) + ';\n')
    offset_layer(arts['front'], 'front', [('lines', full['front-portrait']), ('lines', full['front-rosina']),
                                          ('lines', full['front-100']), ('blob', full['front-rolling'])])
    offset_layer(arts['back'], 'back', [('lines', full['back-portrait']), ('lines', full['back-shrine']),
                                        ('lines', full['back-100']), ('lines', full['back-serial']),
                                        ('blob', full['back-rolling'])])
    polymer_layer(arts['front'])
    css = ['/* generated by tools/cut_features.py: effect masks as data URIs (plain rules, parsed once) */']
    for sel, name in MASK_RULES.items():
        u = data_uri(imgs[name])
        css.append(f'{sel}{{-webkit-mask-image:{u};mask-image:{u}}}')
    css += linework_rules()
    open(os.path.join(ROOT, 'assets', 'masks.css'), 'w', encoding='utf8').write('\n'.join(css) + '\n')
    contact_sheet(list(imgs.items()))


if __name__ == '__main__':
    main()
