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
SRC = {'front': 'jpy-10000-front.png', 'back': 'jpy-10000-back.png'}
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
SHAPE_ONLY = {('front', 'watermark'), ('back', 'watermark')}

# id, side, label, shape, geometry (note-space units, 720 x 320 over the whole note)
REGIONS = [
    # front (obverse): Shibusawa Eiichi
    ('hologram',          'front', '3D hologram (stripe)',               'poly',
        ((70, 299), (70, 44), (73, 33), (80, 25), (88, 21.5), (96, 21), (104, 22), (110, 26), (114, 33), (115.5, 44), (115.5, 299))),
    ('portrait',          'front', 'Portrait of Shibusawa Eiichi',       'rect',    (412, 36, 244, 244)),       # SAM: tools/sam_isolate.py
    ('numeral',           'front', 'Face value 10000 (deep intaglio)',   'rect',    (128, 110, 184, 70)),
    ('numeral-br',        'front', '10000, lower right',                 'rect',    (594, 254, 110, 56)),       # SAM
    ('tactile-left',      'front', 'Identification mark (left)',         'rect',    (14, 114, 42, 102)),
    ('tactile-right',     'front', 'Identification mark (right)',        'rect',    (660, 114, 46, 102)),
    ('seal',              'front', 'Seal of the Governor of the Bank of Japan', 'ellipse', (251, 246.5, 33, 31)),   # exact circle: tools/circle_cut.py
    ('cartouche',         'front', 'Latent-image cartouche',             'rect',    (286, 252, 146, 56)),       # tools/engrave_cut.py
    ('watermark',         'front', 'Portrait watermark',                 'ellipse', (383, 148, 66, 80)),
    # back (reverse): Tokyo Station, Marunouchi building
    ('station',           'back',  'Tokyo Station Marunouchi building',  'rect',    (8, 22, 292, 264)),         # tools/engrave_cut.py
    ('numeral-big',       'back',  '10000 (large, back)',                'rect',    (460, 20, 244, 96)),
    ('numeral-small',     'back',  '10000 YEN (lower left)',             'rect',    (18, 268, 150, 40)),
    ('wordmark',          'back',  'NIPPON (wordmark)',                  'rect',    (122, 28, 108, 30)),
    ('watermark',         'back',  'Portrait watermark (reverse)',       'ellipse', (337, 148, 66, 80)),
]

# Masks the page uses
PAGE_MASKS = {}

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


EXCLUDE = {}


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
        import numpy as _np, cv2 as _cv2           # fast morphological open (PIL's rank filters are very slow here)
        _k = _cv2.getStructuringElement(_cv2.MORPH_ELLIPSE, (rr, rr))
        m = Image.fromarray(_cv2.morphologyEx(_np.asarray(m), _cv2.MORPH_OPEN, _k))
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


FAINT = {('front', 'watermark'), ('back', 'watermark')}


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


GHOST_BOX = (383, 148, 66, 80)     # front watermark: inside the blank oval left of the portrait (cx, cy, rx, ry)
PORTRAIT_HEAD = (420, 36, 650, 276)   # x0, y0, x1, y1: head and shoulders of the engraved portrait (proportions kept)


def make_ghost(front, out_w, out_h, feather_px):
    """The printed ghost portrait in the artwork is badly processed, so rebuild the
    watermark from the main engraved portrait: same face, rendered the way a
    mould-made watermark looks — soft, continuous-tone shading with no line-work,
    fading out at the edges."""
    W, H = front.size
    sx, sy = W / VB_W, H / VB_H
    x0, y0, x1, y1 = PORTRAIT_HEAD
    src = front.crop((int(x0 * sx), int(y0 * sy), int(x1 * sx), int(y1 * sy))).convert('L')
    # keep the face's proportions: scale to the frame's width, centre it, pad with paper (no stretching)
    k = out_w / src.width
    src = src.resize((out_w, round(src.height * k)), Image.LANCZOS)
    g = Image.new('L', (out_w, out_h), 255)
    g.paste(src.crop((0, 0, out_w, min(src.height, out_h))), (0, max(0, out_h - src.height)))   # shoulders at the frame's foot: the oval fade hides the cut
    # engraving lines -> continuous tone
    g = g.filter(ImageFilter.GaussianBlur(max(2.0, out_w / 160)))
    a = np.asarray(g, np.float32)
    top = max(0, out_h - src.height)                    # where the portrait starts: fade in from there
    paper = np.percentile(a, 97)
    t = np.clip((paper - a) / max(paper - np.percentile(a, 2), 1), 0, 1) ** 0.85
    # elliptical vignette so it melts into the paper
    yy, xx = np.mgrid[0:out_h, 0:out_w]
    d = np.sqrt(((xx - out_w / 2) / (out_w / 2)) ** 2 + ((yy - out_h / 2) / (out_h / 2)) ** 2)
    fade = np.clip((1.0 - d) / (feather_px / (min(out_w, out_h) / 2)), 0, 1)
    fade = fade * fade * (3 - 2 * fade)
    alpha = t * fade * np.clip((yy - top + 0.06 * out_h) / (0.12 * out_h), 0, 1)
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
    # (the page's watermark layer is built by tools/watermark.py)

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
    # clean, edge-detected cut-outs replace the box crops (see isolate_features.py); then the rest
    import build
    build.after_extract()
