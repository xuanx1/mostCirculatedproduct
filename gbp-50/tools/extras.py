"""
Everything the page builds on top of the cut-outs (called by tools/cutouts.py at the end of a run):

  assets/layers/front-hologram-pounds.png  the hologram as it reads when tilted: "Pounds" instead of
                                           "Fifty". The word "Fifty" is removed from the foil (inpainted
                                           from the foil around it) and "Pounds" is set in its place,
                                           using the note's own "Pounds" lettering from the reverse
                                           (filled solid and coloured like the hologram's "Fifty").
  assets/layers/front-windowfoil-swap.png  the window foil with its two gold squares swapped (50 <-> £)
  assets/layers/uv-50.png                  the ultraviolet 50 (red and green), see UV_BOX
  assets/print-front.webp, print-back.webp exploded view: the print without the separately layered parts
  assets/substrate.webp                    exploded view: the polymer film, white, with its clear windows
  assets/masks.css                         optical-effect masks as data URIs
"""
import base64, io, os
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYERS = os.path.join(ROOT, 'assets', 'layers')
VB_W, VB_H = 720, 320

# The two gold squares in the main window's foil (note units): body boxes, 40 units apart
SQ_TOP = (153.6, 144.6, 18.4, 16.2)
SQ_BOT = (153.6, 184.6, 18.4, 16.2)
# "Pounds" on the reverse's "Fifty Pounds" (note units, seed box)
POUNDS_SEED = (192, 255, 300, 288)
# Ultraviolet 50: behind "of England" on the front (approximate: placed from the Bank of England's
# UV photograph of the note; the Bank does not publish its exact position)
UV_BOX = [322, 6, 86, 66]


def disk(r):
    r = max(1, int(round(r)))
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def fill_holes(m):
    h, w = m.shape
    ff = m.copy()
    cv2.floodFill(ff, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 255)
    return m | cv2.bitwise_not(ff)


def to_page(art, rgba_full, box):
    x, y, w, h = box
    (a, b), (c, d) = art.px(x, y), art.px(x + w, y + h)
    k = 1440 / VB_W * 1.5
    return Image.fromarray(np.ascontiguousarray(rgba_full[b:d, a:c]), 'RGBA').resize(
        (max(1, round(w * k)), max(1, round(h * k * art.sy / art.sx))), Image.LANCZOS)


def ofl_font(file, size, wght=None):
    """a bundled OFL woff2 (fonts/), decompressed for PIL; variable weight set when given"""
    from fontTools.ttLib import TTFont
    tt = TTFont(os.path.join(ROOT, 'fonts', file))
    tt.flavor = None
    buf = io.BytesIO()
    tt.save(buf)
    buf.seek(0)
    font = ImageFont.truetype(buf, size)
    if wght is not None:
        try:
            axes = font.get_variation_axes()
            font.set_variation_by_axes([wght if a['name'] in (b'Weight', 'Weight') else a['default'] for a in axes])
        except Exception as e:
            print('  (no variable weight:', e, ')')
    return font


SERIF = 'vEFI2_tTDB4M7-auWDN0ahZJW1gb8tc.woff2'       # Source Serif 4 (OFL), latin
BODONI = 'bodoni-moda-latin.woff2'                    # Bodoni Moda (OFL), latin


def hologram_pounds(arts, boxes):
    """The hologram as it reads tilted: "Pounds". The scan only shows "Fifty", so the word is removed
    from the foil (inpainted from the foil around it) and "Pounds" is set in a bold serif (Source Serif 4)
    with the same cap height and colour, centred where "Fifty" is. Its lettering is illustrative."""
    front = arts['front']
    box = boxes['front-hologram']
    x, y, w, h = box
    (a, b), (c, d) = front.px(x, y), front.px(x + w, y + h)
    rgb = front.rgb[b:d, a:c].copy()
    page_size = Image.open(os.path.join(LAYERS, 'front-hologram.png')).size
    alpha = np.asarray(Image.open(os.path.join(LAYERS, 'front-hologram.png')).getchannel('A').resize((c - a, d - b), Image.LANCZOS))
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    L, A, B = lab[..., 0], lab[..., 1] - 128, lab[..., 2] - 128
    purple = ((B < -28) & (A > 12) & (L < 150)).astype(np.uint8) * 255
    hh = purple.shape[0]
    purple[: int(hh * 0.2)] = 0
    purple[int(hh * 0.72):] = 0                                                # the comb below is not the word
    n, lab_, st, _ = cv2.connectedComponentsWithStats(purple, 8)
    word_m = np.zeros_like(purple)
    for k in range(1, n):
        if st[k, 4] > (0.5 * front.s) ** 2:
            word_m[lab_ == k] = 255
    ys, xs = np.nonzero(word_m)
    word = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    col = np.median(rgb[word_m > 0], axis=0)
    hole = cv2.dilate(word_m, disk(0.8 * front.s))
    clean = cv2.inpaint(rgb, hole, 11, cv2.INPAINT_TELEA)
    # cap height of "Fifty": the F's own column
    fcol = word_m[:, word[0]:word[0] + int(1.5 * front.s)]
    fy = np.nonzero(fcol.any(1))[0]
    target_cap = fy.max() - fy.min() + 1
    img = Image.new('L', (c - a, d - b), 0)
    dr = ImageDraw.Draw(img)
    font = ofl_font(SERIF, 100, 700)
    capP = dr.textbbox((0, 0), 'P', font=font)
    font = ofl_font(SERIF, max(8, int(100 * target_cap / (capP[3] - capP[1]))), 700)
    bb = dr.textbbox((0, 0), 'Pounds', font=font)
    capP = dr.textbbox((0, 0), 'P', font=font)
    cx = (word[0] + word[2]) / 2
    dr.text((cx - (bb[2] - bb[0]) / 2 - bb[0], fy.min() - capP[1]), 'Pounds', font=font, fill=255)
    gm = np.asarray(img).astype(np.float32) / 255
    shade = np.linspace(1.08, 0.92, gm.shape[0])[:, None, None]
    glyph = np.clip(col[None, None, :] * shade, 0, 255)
    out = clean.astype(np.float32) * (1 - gm[..., None]) + glyph * gm[..., None]
    rgba = np.dstack([out.clip(0, 255).astype(np.uint8), alpha])
    Image.fromarray(rgba, 'RGBA').resize(page_size, Image.LANCZOS).save(os.path.join(LAYERS, 'front-hologram-pounds.png'), optimize=True)
    print('hologram: Fifty at', word, 'cap', target_cap, '-> Pounds', bb)


def foil_swap(arts, boxes):
    """the window foil with the two square bodies exchanged, feathered, on the windowfoil frame"""
    f = arts['front']
    box = boxes['front-windowfoil']
    x, y, w, h = box
    (a, b), (c, d) = f.px(x, y), f.px(x + w, y + h)
    rgb = f.rgb[b:d, a:c]
    out = np.zeros((d - b, c - a, 4), np.float32)
    for src, dst in ((SQ_BOT, SQ_TOP), (SQ_TOP, SQ_BOT)):
        (sx0, sy0), (sx1, sy1) = f.px(src[0], src[1]), f.px(src[0] + src[2], src[1] + src[3])
        (dx0, dy0) = f.px(dst[0], dst[1])
        patch = f.rgb[sy0:sy1, sx0:sx1].astype(np.float32)
        hh, ww = patch.shape[:2]
        m = np.zeros((hh, ww), np.float32)
        e = int(0.6 * f.s)
        m[e:-e, e:-e] = 1
        m = cv2.GaussianBlur(m, (0, 0), 0.5 * f.s)
        X, Y = dx0 - a, dy0 - b
        out[Y:Y + hh, X:X + ww, :3] = patch
        out[Y:Y + hh, X:X + ww, 3] = m * 255
    page = Image.fromarray(out.clip(0, 255).astype(np.uint8), 'RGBA').resize(
        Image.open(os.path.join(LAYERS, 'front-windowfoil.png')).size, Image.LANCZOS)
    page.save(os.path.join(LAYERS, 'front-windowfoil-swap.png'), optimize=True)


def uv50():
    """A bold Didone 50 in the red-and-green UV colours (diamond pattern as in the Bank's UV photo).
    Drawn with Bodoni Moda (OFL), not cut from the note: the ink is invisible in daylight scans."""
    W = int(UV_BOX[2] * 6)
    H = int(UV_BOX[3] * 6 * (760 / 320) / 2)
    img = Image.new('L', (W * 2, H * 2), 0)
    dr = ImageDraw.Draw(img)
    font = ofl_font(BODONI, 200, 900)
    bb = dr.textbbox((0, 0), '50', font=font)
    k = min(W * 2 * 0.96 / (bb[2] - bb[0]), H * 2 * 0.96 / (bb[3] - bb[1]))
    font = ofl_font(BODONI, int(200 * k), 900)
    bb = dr.textbbox((0, 0), '50', font=font)
    dr.text(((W * 2 - (bb[2] - bb[0])) / 2 - bb[0], (H * 2 - (bb[3] - bb[1])) / 2 - bb[1]), '50', font=font, fill=255)
    m = np.asarray(img.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
    yy, xx = np.mgrid[0:H, 0:W]
    p = 46.0                                                   # diamond (harlequin) pattern
    u, v = (xx + yy) / p, (xx - yy) / p
    red = ((np.floor(u) + np.floor(v)) % 2 == 0)
    col = np.where(red[..., None], np.array([255, 52, 110], np.float32), np.array([150, 255, 90], np.float32))
    lines = (np.minimum(np.abs(u - np.round(u)), np.abs(v - np.round(v))) < 0.05)
    col[lines] = col[lines] * 0.35
    rgba = np.dstack([col, m * 255]).astype(np.uint8)
    Image.fromarray(rgba, 'RGBA').save(os.path.join(LAYERS, 'uv-50.png'), optimize=True)
    return UV_BOX


def print_layers(arts, masks):
    """exploded view: the print of each side without the parts that have their own layer"""
    for side, art in arts.items():
        rgba = art.rgba.astype(np.float32)
        H, W = rgba.shape[:2]
        rgb = rgba[..., :3]
        L = cv2.cvtColor(art.rgb, cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
        out = rgba.copy()
        if side == 'front':
            # raised (intaglio) lettering: spread the tint under it over the dark strokes
            k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
            closed = cv2.merge([cv2.morphologyEx(art.rgb[..., c], cv2.MORPH_CLOSE, k) for c in range(3)]).astype(np.float32)
            rm = cv2.dilate(masks[('front', 'raised')], disk(0.6 * art.s)).astype(np.float32)[..., None] / 255
            out[..., :3] = out[..., :3] * (1 - rm) + closed * rm
            foils = masks[('front', 'crown')] | masks[('front', 'hologram')]
            clear = masks[('front', 'windowfoil')]
        else:
            foils = masks[('back', 'redfoil')] | masks[('back', 'serial-v')] | masks[('back', 'serial-h')]
            clear = np.roll(cv2.flip(masks[('front', 'windowfoil')], 1), int(round(MIRROR_DX * art.sx)), 1)   # the same foil, from behind
        f = cv2.dilate(foils, disk(0.4 * art.s)).astype(np.float32)[..., None] / 255
        out[..., :3] = out[..., :3] * (1 - f) + np.float32([245, 244, 245]) * f   # opaque white polymer under them
        cm = cv2.GaussianBlur(cv2.dilate(clear, disk(0.4 * art.s)).astype(np.float32) / 255, (0, 0), 0.6 * art.s)
        out[..., :3] = out[..., :3] * (1 - cm[..., None]) + 255 * cm[..., None]
        out[..., 3] = out[..., 3] * (1 - cm) + 0.14 * 255 * cm
        Image.fromarray(out.clip(0, 255).astype(np.uint8), 'RGBA').resize((1440, 760), Image.LANCZOS) \
            .save(os.path.join(ROOT, 'assets', f'print-{side}.webp'), quality=88, method=6)


def substrate(arts, masks):
    """the polymer film: white (its opacity coating) everywhere except the two clear windows"""
    f = arts['front']
    win = masks[('front', 'window')] | masks[('front', 'portrait')] | masks[('front', 'smallwindow')]
    win = cv2.morphologyEx(win, cv2.MORPH_CLOSE, disk(1.2 * f.s))
    a = 0.92 - cv2.GaussianBlur(win.astype(np.float32) / 255, (0, 0), 0.8 * f.s) * (0.92 - 0.1)
    rgb = np.empty(win.shape + (3,), np.float32)
    rgb[...] = (236, 238, 243)                                     # a cool film white, so it reads on the page
    rgba = np.dstack([rgb, a * 255]).astype(np.uint8)
    Image.fromarray(rgba, 'RGBA').resize((1440, 760), Image.LANCZOS).save(
        os.path.join(ROOT, 'assets', 'substrate.webp'), quality=90, method=6)


def data_uri(img):
    buf = io.BytesIO()
    img.save(buf, 'PNG', optimize=True)
    return 'url("data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode() + '")'


def mask_rule(sel, layer_png, max_side=520, flip=False):
    a = Image.open(os.path.join(LAYERS, layer_png)).getchannel('A')
    if flip:
        a = a.transpose(Image.FLIP_LEFT_RIGHT)
    k = min(1.0, max_side / max(a.size))
    if k < 1:
        a = a.resize((round(a.width * k), round(a.height * k)), Image.LANCZOS)
    m = Image.new('LA', a.size, 255)
    m.putalpha(a)
    u = data_uri(m)
    return f'{sel}{{-webkit-mask-image:{u};mask-image:{u}}}'


def write_masks_css():
    rules = ['/* generated by tools/extras.py: optical-effect masks as data URIs (plain rules, parsed once) */',
             mask_rule('.crown-holo', 'front-crown.png'),
             mask_rule('.holo-fx', 'front-hologram.png'),
             mask_rule('.foil-sheen.wf', 'front-windowfoil.png'),
             mask_rule('.foil-sheen.bf', 'front-windowfoil.png', flip=True),
             mask_rule('.foil-sheen.rf', 'back-redfoil.png')]
    open(os.path.join(ROOT, 'assets', 'masks.css'), 'w', encoding='utf8').write('\n'.join(rules) + '\n')


MIRROR_DX = 0.0


def build(arts, masks, boxes, framed):
    global MIRROR_DX
    # registration of the two sides: the main window, front mirrored onto the back (note units)
    cx = lambda m: np.nonzero(m.any(0))[0].mean()
    fw, bw = masks[('front', 'window')], masks[('back', 'window')]
    MIRROR_DX = (cx(bw) - cx(cv2.flip(fw, 1))) / arts['back'].sx
    print('mirror registration dx', round(MIRROR_DX, 2), 'units')
    hologram_pounds(arts, boxes)
    foil_swap(arts, boxes)
    boxes['uv-50'] = uv50()
    wf = boxes['front-windowfoil']
    boxes['back-windowfoil'] = [round(VB_W - wf[0] - wf[2] + MIRROR_DX, 2), wf[1], wf[2], wf[3]]   # the foil from behind
    print_layers(arts, masks)
    substrate(arts, masks)
    write_masks_css()
    print('extras: hologram words, foil swap, uv 50, print layers, substrate, masks.css')
