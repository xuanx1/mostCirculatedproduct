"""
Clean alpha cut-outs of the $100 Frontier note's features, from the working artwork
(cad-100-front.png / cad-100-back.png, 2000 x 916 RGBA; note space 720 x 320 units).

The Bank of Canada's images keep the polymer's clear areas transparent, so everything to do with
the windows comes straight from that alpha, exactly:
  window      the large window: its clear area and everything enclosed by it
  clear       every clear area of the note (window + the frosted leaf's outline)
  mportrait   the metallic portrait   (largest opaque island in the upper window)
  mbuilding   the metallic building   (largest opaque island in the lower window)
  canada      the transparent word CANADA (opaque white islands on the CANADA band)
  smallnum    the small numbers in the window (the other white islands)
  leafwindow  the frosted maple leaf window (its clear outline + the frosted leaf inside)
  frost       the frosted leaf inside it (where the hidden numbers appear)
Printed features are separated by colour inside a hand-drawn seed polygon (note units):
  100         the large numeral (dark brown; counters stay open)
  boc-fr/en   BANQUE DU CANADA 100 / BANK OF CANADA 100 with their small 100 rows (dark glyphs)
  leafborder  the maple leaves around the window (red-brown leaves, text removed)
  ecg         the electrocardiogram traces (thin lines, separated by hue)
Distinct objects come from Segment Anything (tools/sam_isolate.py writes them; this script frames them).

Writes per feature: feature-crops/<side>/<id>.png (full resolution, trimmed), assets/layers/<side>-<id>.png
(framed on its page box), assets/boxes.js, assets/masks.css, assets/offset-*.webp, assets/layers/film-front.png,
feature-crops/contact-sheet.png. Hand-cleaned files in assets/overrides/ always win.

  python tools/cad_isolate.py
"""
import base64, io, json, os, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYERS = os.path.join(ROOT, 'assets', 'layers')
CROPS = os.path.join(ROOT, 'feature-crops')
OVR = os.path.join(ROOT, 'assets', 'overrides')
SAMDIR = os.path.join(ROOT, 'source', 'sam')
VB_W, VB_H = 720, 320
PAD = 2                                   # note units of margin around each framed layer

IM = {s: np.asarray(Image.open(os.path.join(ROOT, f'cad-100-{s}.png')).convert('RGBA')) for s in ('front', 'back')}
H, W = IM['front'].shape[:2]
SX, SY = W / VB_W, H / VB_H
S = (SX + SY) / 2


def disk(r):
    r = max(1, int(round(r)))
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def fill_holes(m, max_area=None):
    """Fill enclosed holes; with max_area only holes smaller than that (keeps counters open)."""
    h, w = m.shape
    ff = np.pad(m, 1, constant_values=0).copy()
    cv2.floodFill(ff, np.zeros((h + 4, w + 4), np.uint8), (0, 0), 255)
    holes = cv2.bitwise_not(ff)[1:-1, 1:-1]
    if max_area is None:
        return m | holes
    n, lab, st, _ = cv2.connectedComponentsWithStats(holes, 4)
    out = m.copy()
    for k in range(1, n):
        if st[k, cv2.CC_STAT_AREA] <= max_area:
            out[lab == k] = 255
    return out


def poly_mask(pts, dil=0):
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.array([(x * SX, y * SY) for x, y in pts], np.int32)], 255)
    return cv2.dilate(m, disk(dil * S)) if dil else m


def rect(x0, y0, x1, y1):
    return poly_mask([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def components(m, conn=8):
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, conn)
    return [(lab == k, st[k], cen[k]) for k in range(1, n)]


def aa(binary, sigma=0.8):
    """binary mask -> alpha with a ~1 px anti-aliased edge, no partial transparency inside"""
    f = cv2.GaussianBlur((binary > 0).astype(np.float32), (0, 0), sigma)
    return np.clip((f - 0.5) * 2.2 + 0.5, 0, 1)


def lab_of(side):
    lab = cv2.cvtColor(IM[side][..., :3], cv2.COLOR_RGB2LAB).astype(np.float32)
    return lab[..., 0] * 100 / 255, lab[..., 1] - 128, lab[..., 2] - 128


GLASS = np.array([214, 236, 246], np.float32)      # the tint a clear area gets when it is highlighted


def rgba_from(side, alpha, glass=None):
    """original pixels under alpha; where the polymer is clear (no pixels) a pale glass tint instead"""
    rgb = IM[side][..., :3].astype(np.float32)
    src_a = IM[side][..., 3].astype(np.float32) / 255
    if glass is not None:
        g = (glass > 0).astype(np.float32) if glass.dtype != np.float32 else glass
        rgb = rgb * src_a[..., None] + GLASS * (1 - src_a[..., None])
        a = np.maximum(alpha * src_a, alpha * (1 - src_a) * 0.55 * g)
    else:
        a = alpha * src_a
    return np.dstack([rgb, a * 255]).clip(0, 255).astype(np.uint8)


# ---------------------------------------------------------------- the polymer's clear areas
def clear_mask(side):
    return ((IM[side][..., 3] < 128) * 255).astype(np.uint8)


def window_parts(side):
    """large window: its clear area (from the alpha) plus the metallic images it holds. The metal runs off
    the top and bottom edges (the window crosses the whole note), so the window outline is taken row by
    row as the span of clear + metal, smoothed along its length."""
    T = clear_mask(side)
    x0, x1 = (455, 625) if side == 'front' else (95, 265)
    mx0, mx1 = (498, 592) if side == 'front' else (128, 222)       # where the metal strips can be
    zone = rect(x0, 0, x1, 320)
    Tz = T & zone
    # the window's own clear area is one large piece; the small clear pieces around it are the
    # outlined numbers printed in clear on the window's border (small numbers)
    Tw = np.zeros_like(Tz); Tsmall = np.zeros_like(Tz)
    for c, st, cen in components(Tz):
        (Tw if st[cv2.CC_STAT_AREA] > (20 * S) ** 2 else Tsmall)[c] = 255
    L, A, B = lab_of(side)
    opaque = IM[side][..., 3] >= 128
    light = (opaque & (L > 48) & ~((A > 8) & (B > 22) & (L < 72))).astype(np.uint8) * 255 & rect(mx0, 0, mx1, 320)
    light = cv2.morphologyEx(light, cv2.MORPH_CLOSE, disk(0.6 * S))
    near = cv2.dilate(Tw, disk(1.5 * S))
    metal = np.zeros_like(light)
    for c, st, cen in components(light):
        if st[cv2.CC_STAT_AREA] > (12 * S) ** 2 and (c & (near > 0)).any():
            metal[c] = 255
    metal = fill_holes(metal)
    both = (Tw | metal) > 0
    rows = np.where(both.any(1))[0]
    lo = np.full(H, np.nan); hi = np.full(H, np.nan)
    for r in rows:
        xs = np.where(both[r])[0]; lo[r], hi[r] = xs.min(), xs.max()
    win = np.zeros((H, W), np.uint8)
    k = int(2 * S)
    for r in rows:
        a, b = max(0, r - k), min(H, r + k + 1)
        l, h = np.nanmedian(lo[a:b]), np.nanmedian(hi[a:b])
        win[r, int(l):int(h) + 1] = 255
    win = cv2.morphologyEx(win, cv2.MORPH_CLOSE, disk(1.0 * S)) | Tw
    win &= cv2.bitwise_not(Tsmall)
    islands = win & cv2.bitwise_not(Tw)
    return win, Tw, islands, metal, Tsmall


def leaf_parts(side):
    T = clear_mask(side)
    zone = rect(55, 50, 165, 155) if side == 'front' else rect(555, 50, 665, 155)
    ring = T & zone
    leaf = fill_holes(cv2.morphologyEx(ring, cv2.MORPH_CLOSE, disk(0.6 * S)))
    frost = cv2.erode(leaf & cv2.bitwise_not(ring), disk(0.3 * S))
    return leaf, ring, frost


def island_sets(side):
    win, Tw, isl, metal, Tsmall = window_parts(side)
    L, A, B = lab_of(side)
    chroma = np.sqrt(A ** 2 + B ** 2)
    mc = sorted(components(metal), key=lambda c: -c[1][cv2.CC_STAT_AREA])
    # the two metallic images: portrait above, building below
    top = [c for c in mc if c[2][1] / SY < 160][0]
    top = ((top[0] > 0) & (Tw == 0),)
    bot = [c for c in mc if c[2][1] / SY >= 160][0]
    # the tower's spire sparkles up into the CANADA band: the building is what lies below the band
    bot = ((bot[0] > 0) & (rect(0, 176, 720, 320) > 0),)
    # small outlined numbers cross the spire: thin strokes, opened off (only up there)
    b8 = (bot[0] * 255).astype(np.uint8) & cv2.bitwise_not(Tw)
    up = rect(0, 0, 720, 206)
    core = cv2.dilate(cv2.morphologyEx(b8 & up, cv2.MORPH_OPEN, disk(1.1 * S)), disk(1.2 * S))
    b8 = (b8 & cv2.bitwise_not(up)) | (b8 & up & core)
    n_, lab_, st_, _ = cv2.connectedComponentsWithStats(b8, 8)
    bot = ((lab_ == 1 + int(np.argmax(st_[1:, cv2.CC_STAT_AREA]))),)
    rest = metal & cv2.bitwise_not((bot[0] * 255).astype(np.uint8)) & cv2.bitwise_not((top[0] * 255).astype(np.uint8))
    comps = components((isl & cv2.bitwise_not(metal)) | rest)
    small_white, leaves = np.zeros((H, W), np.uint8), np.zeros((H, W), np.uint8)
    for m, st, cen in comps:
        c = np.median(chroma[m]); l = np.median(L[m])
        if c > 22 and l < 60:                 # brown maple leaves crossing into the window
            leaves[m] = 255
        else:
            small_white[m] = 255
    return dict(win=win, isl=isl & cv2.bitwise_not(((top[0] | bot[0]) * 255).astype(np.uint8)), clear=Tw, clearnum=Tsmall, mportrait=(top[0] * 255).astype(np.uint8),
                mbuilding=(bot[0] * 255).astype(np.uint8), small=small_white, leaves_in=leaves)


# CANADA runs diagonally across the window (C at 507,127 ... last A at 586,182 on the front, read from
# the artwork); this band holds its six letters and nothing else. The back sees the window from behind:
# mirrored.
_BAND = [(503, 121), (512, 119), (594, 171), (592, 188), (580, 187), (500, 136)]
CANADA_BAND = {'front': _BAND, 'back': [(720 - x, y) for x, y in _BAND]}


def canada_split(side, small, isl):
    """CANADA = the white pixels of the window's islands inside the band (pixel-level, so a letter that
    touches a maple leaf is still found); everything else white is a small number"""
    band = poly_mask(CANADA_BAND[side])
    L, A, B = lab_of(side)
    white = ((L > 78) & (np.sqrt(A ** 2 + B ** 2) < 16)).astype(np.uint8) * 255
    c = cv2.morphologyEx(isl & band & white, cv2.MORPH_CLOSE, disk(0.3 * S))
    keep = np.zeros_like(c)
    for m, st, cen in components(c):
        if st[cv2.CC_STAT_AREA] > (2.5 * S) ** 2:
            keep[m] = 255
    return keep, small & cv2.bitwise_not(cv2.dilate(keep, disk(0.5 * S)))


# ---------------------------------------------------------------- printed features
def large_numeral():
    L, A, B = lab_of('front')
    seed = rect(52, 155, 246, 268)
    dark = ((L < 40) * 255).astype(np.uint8) & seed
    m = cv2.morphologyEx(dark, cv2.MORPH_CLOSE, disk(1.0 * S))          # outer outline + fill, over the cream line
    m = fill_holes(m, max_area=int((6 * S) ** 2))                        # small gaps only: the 0s keep their counters
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(0.6 * S))
    keep = np.zeros_like(m)
    for c, st, cen in components(m):
        if st[cv2.CC_STAT_AREA] > (8 * S) ** 2:
            keep[c] = 255
    return keep


def text_glyphs(side, poly, thr=30, exclude=None):
    """dark glyphs inside a seed polygon: strokes kept as they are, counters open"""
    L, A, B = lab_of(side)
    seed = poly_mask(poly)
    m = ((L < thr) * 255).astype(np.uint8) & seed
    if exclude is not None:
        m &= cv2.bitwise_not(exclude)
    keep = np.zeros_like(m)
    for c, st, cen in components(m):
        a = st[cv2.CC_STAT_AREA]
        w, h = st[cv2.CC_STAT_WIDTH], st[cv2.CC_STAT_HEIGHT]
        right = (st[cv2.CC_STAT_LEFT] + w) / SX
        if a > 6 and max(w, h) < 14 * S and not (side == 'front' and 470 < right < 485):   # glyph-sized; no leaf tips
            keep[c] = 255
    return cv2.dilate(keep, disk(0.25 * S))


# the arcs of lettering left and right of the window (with their rows of small 100s), read from the artwork
BANQUE_POLY = [(414, 0), (482, 0), (482, 192), (414, 192)]
BANK_POLY = [(600, 140), (645, 140), (684, 230), (692, 312), (645, 314), (640, 262), (598, 185)]


def leaf_border(side, win, exclude):
    L, A, B = lab_of(side)
    ring = cv2.dilate(win, disk(40 * S)) & cv2.bitwise_not(cv2.erode(win, disk(1)))
    redbrown = (A > 14) & (L < 58) & (A > B * 0.35)
    m = ((redbrown) * 255).astype(np.uint8) & ring & cv2.bitwise_not(exclude)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(0.5 * S))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, disk(0.5 * S))
    keep = np.zeros_like(m)
    for c, st, cen in components(m):
        if st[cv2.CC_STAT_AREA] > (3 * S) ** 2:
            keep[c] = 255
    return keep


DNA_POLY = [(452, 36), (508, 36), (545, 86), (580, 124), (576, 142), (562, 152), (548, 150), (515, 128), (466, 82), (452, 62)]


def dna_strand(exclude):
    """the faint helix: darker and less yellow than the paper around it (local contrast in L and b)"""
    L, A, B = lab_of('back')
    r = 12 * S
    dL = cv2.GaussianBlur(L, (0, 0), r) - L
    dB = cv2.GaussianBlur(B, (0, 0), r) - B
    m = (((dL > 1.3) & (dB < -0.3)) * 255).astype(np.uint8) & poly_mask(DNA_POLY) & cv2.bitwise_not(exclude)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(0.4 * S))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, disk(0.4 * S))
    keep = np.zeros_like(m)
    for c, st, cen in components(m):
        if st[cv2.CC_STAT_AREA] > (2.5 * S) ** 2:
            keep[c] = 255
    return keep


def ecg_lines():
    L, A, B = lab_of('back')
    out = np.zeros((H, W), np.uint8)
    # left trace: thin red-brown line on the pale border panel
    s1 = rect(12, 195, 104, 240)
    l1 = ((A > 12) & (L < 70)).astype(np.uint8) * 255 & s1
    # middle trace: thin olive-green line on the orange paper (and under SPECIMEN)
    s2 = rect(250, 195, 430, 248)
    l2 = ((A < 4) & (B > 18) & (L < 80)).astype(np.uint8) * 255 & s2
    for m in (l1, l2):
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, disk(0.5 * S))
        for c, st, cen in components(m):
            if max(st[cv2.CC_STAT_WIDTH], st[cv2.CC_STAT_HEIGHT]) > 6 * S:
                out[c] = 255
    return cv2.dilate(out, disk(0.3 * S))


# ---------------------------------------------------------------- output
BOXES, MADE = {}, {}


def save(side, fid, rgba, also_ink=None):
    """trim, keep full resolution, frame on its page box (note units), record the box"""
    name = f'{side}-{fid}'
    ov = os.path.join(OVR, name + '.png')
    if os.path.exists(ov):
        print('  using override', name)
        rgba = np.asarray(Image.open(ov).convert('RGBA').resize((W, H)))
    a = rgba[..., 3]
    ys, xs = np.where(a > 4)
    if not len(xs):
        print('  EMPTY', name); return
    m = int(PAD * S)
    x0, x1 = max(0, xs.min() - m), min(W, xs.max() + m + 1)
    y0, y1 = max(0, ys.min() - m), min(H, ys.max() + m + 1)
    crop = Image.fromarray(rgba[y0:y1, x0:x1], 'RGBA')
    os.makedirs(os.path.join(CROPS, side), exist_ok=True)
    crop.save(os.path.join(CROPS, side, f'{fid}.png'), optimize=True)
    crop.save(os.path.join(LAYERS, name + '.png'), optimize=True)
    BOXES[name] = [round(x0 / SX, 2), round(y0 / SY, 2), round((x1 - x0) / SX, 2), round((y1 - y0) / SY, 2)]
    MADE[name] = crop
    print(f'  {name:22} box {BOXES[name]}  {crop.size}')


def sam_layer(side, fid, exclude=None, keep_rect=None):
    p = os.path.join(SAMDIR, f'{side}-{fid}.png')
    if not os.path.exists(p):
        print('  (no SAM mask yet for', side, fid, '- run tools/sam_isolate.py)'); return None
    m = (np.asarray(Image.open(p).convert('L')) > 127).astype(np.uint8) * 255
    if exclude is not None:
        m &= cv2.bitwise_not(exclude)
    if keep_rect is not None:
        m &= rect(*keep_rect)
    return m


def write_masks_css(masks):
    out = ['/* generated by tools/cad_isolate.py: effect masks as data URIs (work from file://), plain rules parsed once */']
    for sel, img in masks.items():
        k = min(1.0, 700 / max(img.size))
        if k < 1:
            img = img.resize((round(img.width * k), round(img.height * k)), Image.LANCZOS)
        m = Image.new('LA', img.size, 255)
        m.putalpha(img.getchannel('A'))
        buf = io.BytesIO(); m.save(buf, 'PNG', optimize=True)
        u = f'url("data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}")'
        out.append(f'{sel}{{-webkit-mask-image:{u};mask-image:{u}}}')
    out += linework_rules()
    open(os.path.join(ROOT, 'assets', 'masks.css'), 'w', encoding='utf8').write('\n'.join(out) + '\n')


FLOW_CLIP = {}


def linework_rules():
    """engraved line-work of the portrait (front) and the researcher (back), for the gold flow"""
    rules = []
    for side, cls in (('front', '.flow-front'), ('back', '.flow-back')):
        clip = FLOW_CLIP.get(side)
        if clip is None:
            continue
        im = Image.fromarray(IM[side][..., :3]).resize((1080, 495), Image.LANCZOS)
        L = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
        bg = cv2.GaussianBlur(cv2.morphologyEx(L, cv2.MORPH_CLOSE, disk(4)), (0, 0), 3)
        lines = ((bg - L - 7) > 0) & (cv2.resize(clip, (1080, 495)) > 127)
        a = Image.fromarray((lines * 255).astype(np.uint8)).convert('1')
        buf = io.BytesIO(); a.save(buf, 'PNG', optimize=True)
        u = f'url("data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}")'
        rules.append(f'{cls}{{-webkit-mask-mode:luminance;mask-mode:luminance;-webkit-mask-image:{u};mask-image:{u}}}')
    return rules


def offset_layer(side, remove):
    """the print layer for the exploded view: the artwork with its windows clear and the metallic images
    (which belong to the foil in the polymer) taken out"""
    rgba = IM[side].copy()
    rgba[..., 3] = np.where(remove > 0, 0, rgba[..., 3])
    Image.fromarray(rgba, 'RGBA').resize((1440, 660), Image.LANCZOS).save(
        os.path.join(ROOT, 'assets', f'offset-{side}.webp'), quality=88, method=6)


def film_layer(side, clear):
    """the polymer film: one clear sheet. Where it is printed it carries the (illustrative) white base;
    the windows stay clear"""
    a = aa(cv2.bitwise_not(clear))
    rgb = np.empty((H, W, 3), np.float32); rgb[:] = (250, 246, 238)
    edge = cv2.morphologyEx(clear, cv2.MORPH_GRADIENT, disk(0.5 * S)) > 0
    alpha = a * 0.92 + (1 - a) * 0.10
    alpha[edge] = 0.95
    rgb[edge] = (150, 170, 182)
    Image.fromarray(np.dstack([rgb, alpha * 255]).clip(0, 255).astype(np.uint8), 'RGBA').resize(
        (1440, 660), Image.LANCZOS).save(os.path.join(LAYERS, f'film-{side}.png'), optimize=True)


def contact_sheet():
    items = sorted(MADE.items())
    cols, cw, ch = 5, 300, 240
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * cw, rows * ch), (28, 24, 22))
    d = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(items):
        t = im.copy(); t.thumbnail((cw - 20, ch - 34))
        cx, cy = (i % cols) * cw, (i // cols) * ch
        sheet.paste(t, (cx + (cw - t.width) // 2, cy + 8), t)
        d.text((cx + 8, cy + ch - 20), name, fill=(240, 230, 210))
    sheet.save(os.path.join(CROPS, 'contact-sheet.png'))


def main():
    os.makedirs(LAYERS, exist_ok=True)
    flow_masks = {}
    masks = {}
    for side in ('front', 'back'):
        I = island_sets(side)
        canada, nums = canada_split(side, I['small'], I['isl'])
        leaf, ring, frost = leaf_parts(side)
        clear = clear_mask(side)
        save(side, 'window', rgba_from(side, aa(I['win']), glass=I['win']))
        save(side, 'clear', rgba_from(side, aa(clear), glass=clear))
        save(side, 'mportrait', rgba_from(side, aa(I['mportrait'])))
        save(side, 'mbuilding', rgba_from(side, aa(I['mbuilding'])))
        save(side, 'canada', rgba_from(side, aa(canada)))
        save(side, 'smallnum', rgba_from(side, aa(nums | I['clearnum']), glass=I['clearnum']))
        save(side, 'leafwindow', rgba_from(side, aa(leaf), glass=leaf))
        if side == 'front':                      # the hidden numbers work only from the front
            save(side, 'frost', rgba_from(side, aa(frost)))
        # the print's own window content is not part of the window "border"
        text_ex = np.zeros((H, W), np.uint8)
        if side == 'front':
            fr = text_glyphs('front', BANQUE_POLY)
            en = text_glyphs('front', BANK_POLY, exclude=rect(612, 244, 639, 288))   # leaf tips beside the arc
            save('front', 'boc-fr', rgba_from('front', aa(fr)))
            save('front', 'boc-en', rgba_from('front', aa(en)))
            text_ex = cv2.dilate(fr | en, disk(0.8 * S))
            save('front', '100', rgba_from('front', aa(large_numeral())))
            pm = sam_layer('front', 'portrait', exclude=cv2.dilate(I['win'], disk(1)))
            if pm is not None:
                save('front', 'portrait', rgba_from('front', aa(pm)))
                sh = pm & rect(0, 232, 720, 320)                 # the shoulders (raised ink)
                save('front', 'shoulders', rgba_from('front', aa(sh)))
                FLOW_CLIP['front'] = pm
        else:
            for fid in ('researcher', 'insulin'):
                m = sam_layer('back', fid)
                if m is not None and fid == 'researcher':
                    # the SPECIMEN overprint's grey M runs into the SAM mask below the microscope
                    Lb, Ab, Bb = lab_of('back')
                    grey = (np.sqrt(Ab ** 2 + Bb ** 2) < 16).astype(np.uint8) * 255 & rect(360, 182, 440, 236)
                    m &= cv2.bitwise_not(cv2.dilate(grey, disk(0.8 * S)))
                    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(0.8 * S))
                    n_, lab_, st_, _ = cv2.connectedComponentsWithStats(m, 8)
                    m = ((lab_ == 1 + int(np.argmax(st_[1:, cv2.CC_STAT_AREA]))) * 255).astype(np.uint8)
                if m is not None:
                    save('back', fid, rgba_from('back', aa(m)))
                    if fid == 'researcher':
                        FLOW_CLIP['back'] = m
            ex = cv2.dilate(leaf | (sam_layer('back', 'researcher') if os.path.exists(os.path.join(SAMDIR, 'back-researcher.png')) else 0), disk(1.0 * S))
            save('back', 'dna', rgba_from('back', aa(dna_strand(ex))))
            save('back', 'ecg', rgba_from('back', aa(ecg_lines())))
        lb = leaf_border(side, I['win'], text_ex) | I['leaves_in']
        save(side, 'leafborder', rgba_from(side, aa(lb)))
        offset_layer(side, I['mportrait'] | I['mbuilding'])
        if side == 'front':                      # one film: the exploded view shows it from the front
            film_layer(side, clear)
        for fid, sel in (('mportrait', f'.holo-mp.{side}'), ('mbuilding', f'.holo-mb.{side}'),
                         ('canada', f'.glint-canada.{side}'), ('window', f'.win-glass.{side}')):
            if f'{side}-{fid}' in MADE:
                masks[sel] = MADE[f'{side}-{fid}']
        # the window glass glint only over the clear area of the window
        wa = Image.fromarray(I['clear'][..., None].repeat(4, 2))
        x0, y0, w, h = BOXES[f'{side}-window']
        masks[f'.win-glass.{side}'] = wa.crop((round(x0 * SX), round(y0 * SY), round((x0 + w) * SX), round((y0 + h) * SY)))
    write_masks_css(masks)
    with open(os.path.join(ROOT, 'assets', 'boxes.js'), 'w', encoding='utf8') as f:
        f.write('// generated by tools/cad_isolate.py: where each extracted layer sits (720x320 note units)\n')
        f.write('const BOXES = ' + json.dumps(BOXES, indent=1) + ';\n')
    contact_sheet()


if __name__ == '__main__':
    main()
