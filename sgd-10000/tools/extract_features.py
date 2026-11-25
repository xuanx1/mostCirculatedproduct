"""
Cut each security feature out of the note artwork onto a transparent background.

For every region below it writes, at full source resolution:
  feature-crops/<side>/<id>.png       shape cut-out (alpha outside the outline, feathered edge)
  feature-crops/<side>/<id>-ink.png   ink only: the paper is keyed to transparent
                                       (colour-to-alpha against the local paper tone)
and a manifest.json + contact-sheet.png for quick review.

It also writes the alpha masks the page uses to confine the tilt effects to real ink:
  assets/masks/*.png

Coordinates are in the page's 720 x 320 note space (same as data.js), so the
crops line up 1:1 with the markers.

Run from the project root:  python tools/extract_features.py
Requires Pillow and numpy.
"""
import json, math, os
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = {'front': 'sgd-10k-front.png', 'back': 'sgd-10k-rear.png'}
OUT = os.path.join(ROOT, 'feature-crops')
MASKS = os.path.join(ROOT, 'assets', 'masks')
VB_W, VB_H = 720, 320
PAD = 4          # page masks / exploded-view layers: tight box (data.js + script.js depend on it)
PRESENT_PAD = 18 # presentation crops: generous margin so glyphs crossing the box stay whole
FEATHER = 10     # ghost-portrait vignette width, in note units
CUT_FEATHER = 2  # paper cut-outs: a short anti-aliased edge (~2 px), not a blur

# Presentation "-ink" files keep each feature's own connected ink, so the edge is the
# printing's real edge (crisp) and unrelated background engraving / neighbouring print
# is dropped. These features are areas rather than ink shapes, so they keep their outline:
SHAPE_ONLY = {('front', 'kinegram'), ('front', 'latent-patch'),
              ('front', 'watermark'), ('back', 'watermark'), ('back', 'coat-of-arms'),
              ('back', 'eurion'), ('back', 'thread'), ('back', 'lion-head')}

# id, side, label, shape, geometry (note-space units)
REGIONS = [
    ('coat-of-arms',      'front', 'Coat of arms (see-through register)', 'rect',    (46, 8, 126, 94)),
    ('watermark',         'front', 'Watermark portrait',                  'ellipse', (97, 190, 70, 80)),
    ('kinegram',          'front', 'Kinegram foil',                       'poly',    ((251, 34), (285, 34), (315, 55), (315, 94),
                                                                                    (285, 118), (251, 118), (221, 94), (221, 55))),
    ('intaglio-10000',    'front', 'Intaglio "10000"',                    'rect',    (205, 124, 205, 62)),
    ('wordmark',          'front', 'TEN THOUSAND DOLLARS wordmark',       'rect',    (214, 182, 184, 48)),
    ('latent-patch',      'front', 'Latent image patch',                  'rect',    (327, 208, 87, 73)),
    ('seal',              'front', 'Chinese seal',                            'rect',    (326, 231, 24, 22)),
    ('signature',         'front', 'Signature + microprint baseline',     'rect',    (236, 234, 90, 46)),
    ('portrait',          'front', 'Engraved portrait',                   'poly',    ((420, 8), (662, 8), (662, 306), (409, 306), (409, 262), (420, 236))),
    ('ovi-10000',         'front', 'Colour-shift "10000"',                'poly',    ((574.6, 261.5), (585, 261.5), (588, 263.5), (590, 261), (716, 259), (716, 306), (569.5, 304), (568.2, 300), (572.6, 296.5), (572.6, 272), (568, 269.5), (569.5, 267), (573, 264))),
    ('serial-horizontal', 'front', 'Horizontal serial',                   'rect',    (37, 272, 117, 23)),
    ('serial-vertical',   'front', 'Vertical serial',                     'rect',    (668, 64, 20, 150)),
    ('tactile-dots',      'front', 'Tactile dots',                        'rect',    (680, 6, 30, 28)),
    ('lion-head-outline', 'front', 'Merlion outline (see-through register)', 'poly', ((183.8, 223.1), (192.7, 223.9), (201.6, 225.8), (207.8, 230.2), (212.2, 235.7), (214.9, 243.6), (214.4, 249.9), (211.3, 256.2), (205.1, 261), (198.9, 263.3), (191.8, 264.5), (189.1, 266.5), (184.7, 267.3), (180.2, 272), (178.4, 278.4), (175.8, 275.2), (170.4, 268.9), (166, 262.6), (165.6, 256.2), (168.7, 249.9), (173.1, 246), (166, 245.2), (164.7, 243.6), (164.2, 239.6), (164.2, 234.9), (164.7, 231), (174.9, 230.6), (172.2, 229), (173.1, 227.4), (180.2, 225))),
    ('thread',            'back',  'Windowed security thread',            'rect',    (405, 40, 18, 280)),
    ('molecular',         'back',  'Molecular fine-line',                 'rect',    (70, 92, 332, 76)),
    ('chip',              'back',  'Micro-chip guilloche',                'rect',    (36, 120, 172, 168)),
    ('intaglio-10000',    'back',  'Intaglio "10000"',                    'rect',    (28, 14, 214, 70)),
    ('small-10000',       'back',  'Small "10000"',                       'rect',    (378, 230, 124, 37)),
    ('lion-head',         'back',  'Gold Merlion (see-through register)', 'poly',    ((551.2, 222.1), (556.6, 226.2), (563.7, 229), (570.8, 231.7), (572.7, 235.7), (572.6, 240.4), (571.7, 246.8), (569, 250.7), (567.2, 249.1), (560.1, 247.7), (567.2, 254.7), (570.8, 261), (570.3, 268.9), (566.3, 275.2), (552.1, 284.3), (551.2, 283.1), (553, 276.8), (549.4, 272), (543.2, 268.9), (531.7, 262.6), (522.8, 256.2), (518.3, 249.9), (517, 242), (519.2, 234.9), (524.6, 227.8), (531.7, 223.8), (542.3, 221.9))),
    ('watermark',         'back',  'Watermark portrait (reverse)',        'ellipse', (640, 200, 62, 74)),
    ('coat-of-arms',      'back',  'Coat of arms (reverse, see-through)', 'rect',    (562, 12, 116, 84)),
    ('serial',            'back',  'Serial',                              'rect',    (580, 277, 122, 20)),
    ('microprint',        'front', 'SINGAPURA · 新加坡 · சிங்கப்பூர் · SINGAPORE', 'rect', (212, 15, 260, 12)),
    ('cowrie',            'front', 'Onyx cowrie contour shell',           'poly',    ((641, 92), (670, 90), (688, 98), (690, 140), (689, 190), (685, 225), (678, 250), (668, 258), (642, 258), (637, 232), (636, 218), (651, 208), (655, 185), (655, 160), (653, 146), (642, 140), (640, 120))),
]

# Masks the page uses (feature id on the page -> crop above)
PAGE_MASKS = {
    'ovi-front':      ('front', 'ovi-10000', 'ink'),
    'kinegram-front': ('front', 'kinegram',  'shape'),
    'thread-back':    ('back',  'thread',    'ink-dark'),
    'latent-front':   ('front', 'latent-patch', 'ink'),
    'kinegram-lion':  ('front', 'lion-head-outline', 'ink-boost'),
}

# Every crop is also written at screen size for the page's exploded view
LAYER_DIR = os.path.join(ROOT, 'assets', 'layers')


def bbox(shape, g, pad=PAD):
    if shape == 'poly':
        xs, ys = [p[0] for p in g], [p[1] for p in g]
        x, y, w, h = min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
    elif shape == 'ellipse':
        cx, cy, rx, ry = g
        x, y, w, h = cx - rx, cy - ry, 2 * rx, 2 * ry
    else:
        x, y, w, h = g
    x0, y0 = max(0, x - pad), max(0, y - pad)
    x1, y1 = min(VB_W, x + w + pad), min(VB_H, y + h + pad)
    return (x0, y0, x1, y1), (x, y, w, h)


EXCLUDE = {('front', 'portrait'): [(560, 250, 160, 70)]}   # the colour-shift 10000 overlaps the portrait


def shape_mask(size, shape, inner, origin, sx, sy, feather=0, exclude=(), poly=None):
    """Anti-aliased mask (L) of the outline, drawn at 4x then reduced.
    With `feather` (note units) the outline is grown by half the feather and
    blurred, so the feature stays fully opaque and the surround fades out softly
    instead of being cut with a hard edge."""
    k = 4
    W, H = size
    m = Image.new('L', (W * k, H * k), 0)
    d = ImageDraw.Draw(m)
    x, y, w, h = inner
    if feather:
        gr = feather * 0.25
        x, y, w, h = x - gr, y - gr, w + 2 * gr, h + 2 * gr
    ox, oy = origin
    X0, Y0 = (x - ox) * sx * k, (y - oy) * sy * k
    X1, Y1 = (x + w - ox) * sx * k, (y + h - oy) * sy * k
    if shape == 'ellipse':
        d.ellipse([X0, Y0, X1, Y1], fill=255)
    elif shape == 'poly':
        # traced outline; convex corners rounded slightly (the foil is die-cut with soft corners)
        ox_, oy_ = origin
        pts = [((px - ox_) * sx * k, (py - oy_) * sy * k) for px, py in poly]
        d.polygon(pts, fill=255)
        rr = int(1.6 * sx * k) | 1
        m = m.filter(ImageFilter.MinFilter(rr)).filter(ImageFilter.MaxFilter(rr))
        d = ImageDraw.Draw(m)
    elif shape == 'octagon':
        cx, cy = (X0 + X1) / 2, (Y0 + Y1) / 2
        rx, ry = (X1 - X0) / 2, (Y1 - Y0) / 2
        pts = [(cx + rx * math.cos(math.radians(22.5 + 45 * i)),
                cy + ry * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]
        d.polygon(pts, fill=255)
    else:
        d.rectangle([X0, Y0, X1, Y1], fill=255)
    for ex, ey, ew, eh in exclude:
        d.rectangle([(ex - ox) * sx * k, (ey - oy) * sy * k, (ex + ew - ox) * sx * k, (ey + eh - oy) * sy * k], fill=0)
    m = m.resize((W, H), Image.LANCZOS)
    if feather:
        return m.filter(ImageFilter.GaussianBlur(feather * 0.3 * (sx + sy) / 2))
    return m.filter(ImageFilter.GaussianBlur(0.6))


def paper_tone(rgb):
    """Local paper colour: median of the brightest 8% of pixels."""
    flat = rgb.reshape(-1, 3).astype(np.float32)
    lum = flat @ np.array([.299, .587, .114], np.float32)
    cut = np.percentile(lum, 92)
    return np.median(flat[lum >= cut], axis=0)


FAINT = {('front', 'watermark'), ('back', 'watermark'), ('back', 'coat-of-arms')}


def faint_to_alpha(rgb, paper, soften=0, region=None):
    """Watermarks are only a few levels darker than the paper: stretch that
    difference to full opacity and render it as a neutral sepia tone."""
    lum = rgb.astype(np.float32) @ np.array([.299, .587, .114], np.float32)
    if soften:  # true watermarks are continuous-tone; suppress paper grain
        lum = np.asarray(Image.fromarray(np.clip(lum, 0, 255).astype(np.uint8))
                         .filter(ImageFilter.GaussianBlur(soften)), np.float32)
    pl = float(paper @ np.array([.299, .587, .114], np.float32))
    diff = np.clip(pl - lum, 0, None)
    sample = diff[region] if region is not None and region.any() else diff
    hi = max(np.percentile(sample, 99.5), 1.0)   # scale to the watermark, not to nearby dark print
    a = np.clip((diff - hi * .08) / (hi * .92), 0, 1) ** .8
    col = np.empty(rgb.shape, np.float32)
    col[...] = (92, 70, 48)
    out = np.dstack([col, a * 255]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def colour_to_alpha(rgb, paper, dark_only=False):
    """GIMP-style colour-to-alpha: remove `paper`, keep what was printed on it."""
    p = rgb.astype(np.float32)
    bg = np.maximum(paper.astype(np.float32), 1.0)
    a_dark = (bg - p) / bg                     # how far each channel is below paper
    a_lite = (p - bg) / np.maximum(255 - bg, 1)  # above paper (foils, highlights)
    a = np.maximum(a_dark, 0 if dark_only else a_lite).max(axis=2)
    if dark_only:
        a = np.clip((a - .35) / .4, 0, 1)      # threads: keep only the dark metal
    else:
        a = np.clip((a - .04) / .96, 0, 1)     # drop faint paper texture
    a = np.clip(a * 1.25, 0, 1)
    safe = np.maximum(a, 1e-3)[..., None]
    col = np.clip((p - bg) / safe + bg, 0, 255)  # un-mix the paper from the ink
    out = np.dstack([col, a * 255]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


GHOST_BOX = (97, 190, 66, 84)      # front watermark ellipse (cx, cy, rx, ry) in note units
PORTRAIT = (538, 158, 118, 142)     # main engraved portrait ellipse


def make_ghost(front, out_w, out_h, feather_px):
    """The printed ghost portrait in the artwork is badly processed, so rebuild the
    watermark from the main engraved portrait: same face, rendered the way a
    mould-made watermark looks — soft, continuous-tone shading with no line-work,
    fading out at the edges."""
    W, H = front.size
    sx, sy = W / VB_W, H / VB_H
    cx, cy, rx, ry = PORTRAIT
    src = front.crop((int((cx - rx) * sx), int((cy - ry) * sy), int((cx + rx) * sx), int((cy + ry) * sy)))
    g = src.convert('L').resize((out_w, out_h), Image.LANCZOS)
    # engraving lines -> continuous tone
    g = g.filter(ImageFilter.GaussianBlur(max(2.0, out_w / 160)))
    a = np.asarray(g, np.float32)
    paper = np.percentile(a, 97)
    t = np.clip((paper - a) / max(paper - np.percentile(a, 2), 1), 0, 1) ** 0.85
    # elliptical vignette so it melts into the paper
    yy, xx = np.mgrid[0:out_h, 0:out_w]
    d = np.sqrt(((xx - out_w / 2) / (out_w / 2)) ** 2 + ((yy - out_h / 2) / (out_h / 2)) ** 2)
    fade = np.clip((1.0 - d) / (feather_px / (min(out_w, out_h) / 2)), 0, 1)
    fade = fade * fade * (3 - 2 * fade)
    alpha = t * fade
    col = np.empty((out_h, out_w, 3), np.float32)
    col[...] = (96, 78, 58)
    return Image.fromarray(np.dstack([col, alpha * 255]).astype(np.uint8), 'RGBA')


def main():
    os.makedirs(MASKS, exist_ok=True)
    imgs = {s: Image.open(os.path.join(ROOT, f)).convert('RGB') for s, f in SRC.items()}
    manifest, made = [], {}
    def extract(im, fid, side, shape, g, pad, feather):
        W, H = im.size
        sx, sy = W / VB_W, H / VB_H
        (x0, y0, x1, y1), inner = bbox(shape, g, pad)
        box = tuple(int(round(v)) for v in (x0 * sx, y0 * sy, x1 * sx, y1 * sy))
        crop = im.crop(box)
        rgb = np.asarray(crop)
        mask = shape_mask(crop.size, shape, inner, (x0, y0), sx, sy, feather, EXCLUDE.get((side, fid), ()), g if shape == 'poly' else None)
        cut = crop.copy()
        cut.putalpha(mask)
        paper = paper_tone(rgb)
        if (side, fid) in FAINT:
            ink = faint_to_alpha(rgb, paper, soften=4 if (side, fid) == ('front', 'watermark') else 0)
        else:
            ink = colour_to_alpha(rgb, paper, dark_only=(fid == 'thread'))
        arr = np.asarray(ink).copy()
        arr[..., 3] = (arr[..., 3].astype(np.float32) * np.asarray(mask, np.float32) / 255).astype(np.uint8)
        return dict(cut=cut, ink=Image.fromarray(arr, 'RGBA'), mask=mask, box=box,
                    nb=(x0, y0, x1, y1), paper=paper, size=crop.size)

    def present(im, fid, side, shape, g):
        W, H = im.size
        sx, sy = W / VB_W, H / VB_H
        (x0, y0, x1, y1), inner = bbox(shape, g, PRESENT_PAD)
        box = tuple(int(round(v)) for v in (x0 * sx, y0 * sy, x1 * sx, y1 * sy))
        crop = im.crop(box)
        rgb = np.asarray(crop)
        hard = np.asarray(shape_mask(crop.size, shape, inner, (x0, y0), sx, sy, 0, EXCLUDE.get((side, fid), ()), g if shape == 'poly' else None), np.float32) / 255
        edge = shape_mask(crop.size, shape, inner, (x0, y0), sx, sy, CUT_FEATHER, EXCLUDE.get((side, fid), ()), g if shape == 'poly' else None)
        paper = paper_tone(rgb)
        inside = hard > 0.5
        if (side, fid) in FAINT:
            ink = faint_to_alpha(rgb, paper, soften=0, region=inside)
        else:
            ink = colour_to_alpha(rgb, paper, dark_only=(fid == 'thread'))
        arr = np.asarray(ink).copy()
        a = arr[..., 3].astype(np.float32)
        if (side, fid) in SHAPE_ONLY:
            keep = np.asarray(edge, np.float32) / 255
        else:
            # solid ink within a small margin of the outline, split into connected pieces;
            # pieces that are mostly outside the outline (neighbouring print poking in) are dropped
            p99 = np.percentile(a[inside], 99) if inside.any() else 255
            strong = a > max(0.42 * p99, 40)
            margin = int(round(3 * (sx + sy) / 2))
            cand = strong & ndimage.binary_dilation(inside, iterations=margin)
            lab, n = ndimage.label(cand, structure=np.ones((3, 3)))
            km = np.zeros_like(inside)
            if n:
                idx = np.arange(1, n + 1)
                tot = ndimage.sum(np.ones_like(a), lab, idx)
                ins = ndimage.sum(inside, lab, idx)
                ok = idx[((ins / np.maximum(tot, 1)) >= 0.6) & (tot >= 6)]
                km = np.isin(lab, ok)
            near = ndimage.binary_dilation(km, iterations=3)
            # finer shading inside the outline that sits right next to kept ink
            near |= ndimage.binary_dilation(km, iterations=9) & inside
            keep = np.asarray(Image.fromarray((near * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7)),
                              np.float32) / 255
        arr[..., 3] = (a * keep).astype(np.uint8)
        ink = Image.fromarray(arr, 'RGBA')
        cut = crop.copy()
        cut.putalpha(edge)
        # trim both to their content (+ a small margin) so the files aren't mostly empty
        def trim(img, margin=10):
            bb = img.getchannel('A').point(lambda v: 255 if v > 6 else 0).getbbox()
            if not bb:
                return img
            l, t, r, b = bb
            return img.crop((max(0, l - margin), max(0, t - margin),
                             min(img.width, r + margin), min(img.height, b + margin)))
        return dict(cut=trim(cut), ink=trim(ink), nb=(x0, y0, x1, y1), box=box, paper=paper)

    for fid, side, label, shape, g in REGIONS:
        im = imgs[side]
        # tight, hard-edged version: page masks (must match the boxes in script.js)
        tight = extract(im, fid, side, shape, g, PAD, 0)
        # tight but softly faded at its edge: exploded-view layers (boxes in data.js)
        soft = extract(im, fid, side, shape, g, PAD, 3)
        # presentation version: isolated ink with its own crisp edge; paper cut-out with a short AA edge
        pres = present(im, fid, side, shape, g)

        d = os.path.join(OUT, side)
        os.makedirs(d, exist_ok=True)
        pres['cut'].save(os.path.join(d, f'{fid}.png'), optimize=True)
        pres['ink'].save(os.path.join(d, f'{fid}-ink.png'), optimize=True)
        made[(side, fid)] = (soft['cut'], tight['ink'], tight['mask'], soft['ink'])
        x0, y0, x1, y1 = pres['nb']
        box, crop, paper = pres['box'], pres, pres['paper']
        manifest.append({
            'id': fid, 'side': side, 'label': label, 'shape': shape,
            'note_box': [round(x0, 2), round(y0, 2), round(x1 - x0, 2), round(y1 - y0, 2)],
            'source_px': list(box),
            'size_px': {'cutout': list(pres['cut'].size), 'ink': list(pres['ink'].size)},
            'paper_rgb': [int(v) for v in paper],
            'files': {'cutout': f'{side}/{fid}.png', 'ink': f'{side}/{fid}-ink.png'},
        })
        print(f'{side:5} {fid:18} ink {pres["ink"].size}')

    # ---- ghost portrait rebuilt from the main portrait -------------------
    front = imgs['front']
    W, H = front.size
    sx, sy = W / VB_W, H / VB_H
    cx, cy, rx, ry = GHOST_BOX
    gw, gh = int(2 * rx * sx), int(2 * ry * sy)
    ghost = make_ghost(front, gw, gh, feather_px=FEATHER * sx)
    ink_g = ghost.copy()
    ink_g.putalpha(ink_g.getchannel('A').point(lambda v: min(255, int(v * 0.55))))  # watermark strength
    ink_g.save(os.path.join(OUT, 'front', 'watermark-ink.png'), optimize=True)
    on_paper = Image.new('RGBA', ghost.size, (251, 250, 248, 255))
    on_paper.alpha_composite(ink_g)
    vign = ghost.getchannel('A').point(lambda v: 255)  # full rect, then soft ellipse edge
    yy, xx = np.mgrid[0:gh, 0:gw]
    dd = np.sqrt(((xx - gw / 2) / (gw / 2)) ** 2 + ((yy - gh / 2) / (gh / 2)) ** 2)
    edge = np.clip((1.0 - dd) / 0.18, 0, 1)
    on_paper.putalpha(Image.fromarray((edge * edge * (3 - 2 * edge) * 255).astype(np.uint8), 'L'))
    on_paper.save(os.path.join(OUT, 'front', 'watermark.png'), optimize=True)
    # the reverse shows the same watermark, mirrored (it is formed in the paper, not printed)
    ink_g.transpose(Image.FLIP_LEFT_RIGHT).save(os.path.join(OUT, 'back', 'watermark-ink.png'), optimize=True)
    on_paper.transpose(Image.FLIP_LEFT_RIGHT).save(os.path.join(OUT, 'back', 'watermark.png'), optimize=True)
    for e in manifest:
        if e['side'] == 'back' and e['id'] == 'watermark':
            e['label'] = 'Watermark portrait (reverse: the same watermark, mirrored)'
            e['note_box'] = [720 - cx - rx, cy - ry, 2 * rx, 2 * ry]
            e['size_px'] = [gw, gh]
        if e['side'] == 'front' and e['id'] == 'watermark':
            e['label'] = 'Watermark portrait (rebuilt from the engraved portrait)'
            e['note_box'] = [cx - rx, cy - ry, 2 * rx, 2 * ry]
            e['size_px'] = [gw, gh]
    # screen-size copy for the page: drawn over the artwork's own ghost
    os.makedirs(os.path.join(ROOT, 'assets'), exist_ok=True)
    # (same box as the exploded-view watermark layer: 23,106,148,168 note units)
    g_page = make_ghost(front, int(148 * 2 * 1.5), int(168 * 2.25 * 1.5), feather_px=FEATHER * 3 * 2)
    os.makedirs(LAYER_DIR, exist_ok=True)
    g_page.save(os.path.join(LAYER_DIR, 'watermark-ghost.png'), optimize=True)
    globals()['_GHOST_PAGE'] = g_page

    with open(os.path.join(OUT, 'manifest.json'), 'w', encoding='utf8') as f:
        json.dump({'note_space': [VB_W, VB_H], 'sources': SRC, 'crops': manifest}, f, indent=2)

    # (page layers, masks and boxes are written by isolate_features.py)

    # Contact sheet on a checkerboard so the transparency is visible
    tiles = []
    for e in manifest:
        for key in ('cutout', 'ink'):
            t = Image.open(os.path.join(OUT, e['files'][key]))
            t.thumbnail((260, 200))
            tiles.append((t, f"{e['side']}/{e['id']} {key}"))
    cols, cw, ch = 6, 280, 230
    rows = math.ceil(len(tiles) / cols)
    sheet = Image.new('RGB', (cols * cw, rows * ch), 'white')
    chk = Image.new('RGB', (cw, ch))
    dc = ImageDraw.Draw(chk)
    for yy in range(0, ch, 10):
        for xx in range(0, cw, 10):
            dc.rectangle([xx, yy, xx + 9, yy + 9], fill=(205, 205, 205) if (xx + yy) // 10 % 2 else (245, 245, 245))
    ds = ImageDraw.Draw(sheet)
    for i, (t, name) in enumerate(tiles):
        cx, cy = (i % cols) * cw, (i // cols) * ch
        sheet.paste(chk, (cx, cy))
        sheet.paste(t, (cx + (cw - t.width) // 2, cy + 8), t)
        ds.text((cx + 6, cy + ch - 18), name, fill=(0, 0, 0))
    sheet.save(os.path.join(OUT, 'contact-sheet.png'))
    print(f'\n{len(manifest)} regions -> {OUT}')


if __name__ == '__main__':
    main()
    # clean, edge-detected cut-outs replace the box crops (see isolate_features.py)
    import isolate_features
    isolate_features.main()
