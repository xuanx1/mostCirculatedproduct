"""
Clean alpha cut-outs of the EUR 500's features, from the working artwork (eur-500-front/back.png).

Every feature below is isolated from the original pixels, never redrawn:
  ink   - colour separation in Lab space: the feature's own ink is selected by its colour
          (navy intaglio, magenta/purple print, yellow circles, orange stars, black serials...),
          small specks dropped, only pieces inside the seed box kept;
  solid - the same, then closed into one silhouette (striped numerals, line drawings);
  rect  - an exact rectangle found from the ink (the EU flag);
  sam   - Segment Anything (facebook/sam-vit-large) prompted with a box and points
          (the main image, the hologram patch, the map), for distinct objects.
Alpha is binary with a ~1 px anti-aliased edge (no haze), and enclosed counters stay open
(holes are filled only below a size limit, so the insides of 0, 6, 8, 9, A... stay transparent).

The working artwork has had the scan's overprinted marking removed beforehand (tools/remove_specimen.py,
LaMa inpainting), so every cut-out here is made from the cleaned image.

Writes
  assets/layers/<side>-<id>.png       the feature (ink), framed to its box
  assets/layers/<side>-<id>-cut.png   its silhouette (glow highlight), same frame
  assets/boxes.js                     where each layer sits (720 x 320 note units)
  assets/offset-front.jpg / -back.jpg the offset print: intaglio, foil, silk-screen and letterpress removed
  assets/masks.css                    optical-effect masks + line-work masks as data URIs
  feature-crops/<side>/<id>.png, contact-sheet.png   full-resolution cut-outs for review
Hand-cleaned files in assets/overrides/ always win.

Run:  python tools/cutouts.py           (SAM needs the GPU lock; see README)
      python tools/cutouts.py --no-sam  (reuse the SAM masks cached in source/sam/)
      add --clean to delete layer images the page no longer references
"""
import base64, io, json, math, os, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = {'front': 'eur-500-front.png', 'back': 'eur-500-back.png'}
LAYERS = os.path.join(ROOT, 'assets', 'layers')
OVR = os.path.join(ROOT, 'assets', 'overrides')
CROPS = os.path.join(ROOT, 'feature-crops')
SAMDIR = os.path.join(ROOT, 'source', 'sam')
VB_W, VB_H = 720, 320
SCALE = 0.75            # page layers: 0.75 x artwork resolution (~3.2 px per note unit, 1.6x the face)


def lab_of(rgb):
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    return lab[..., 0], lab[..., 1] - 128, lab[..., 2] - 128


# ---- colour predicates (Lab, a/b centred on 0) --------------------------------------------
def p_navy(L, A, B):        # dark blue-violet intaglio: initials, signature, bar
    return (B < -24) & (L < 140)
def p_dark(L, A, B):        # any dark ink on pale ground (the tactile marks shade from navy to wine)
    return L < 135
def p_magenta(L, A, B):     # magenta / pink-violet print on white
    return (A > 14) & (L < 215)
def p_purple(L, A, B):      # dark purple numerals
    return (L < 175) & (A > 10) & (B < 12)
def p_wine(L, A, B):        # the large intaglio 500 (dark wine / plum), not the orange stars
    return (L < 150) & (A > 18) & (B < 18)
def p_yellow(L, A, B):      # small yellow circles (with their orange rims)
    return (B > 38) & (L > 120) & (A < 40)
def p_orange(L, A, B):      # the large orange stars
    return (A > 38) & (B > 38)
def p_black(L, A, B):       # black serial numbers
    return (L < 120) & (np.abs(A) < 25) & (np.abs(B) < 25)
def p_foil(L, A, B):        # the hologram foil: strongly coloured (rainbow) or dark
    return (np.hypot(A, B) > 24) | (L < 110)
def p_initials(L, A, B):    # the copyright line: navy, its lighter year 2002 included
    return (B < -16) & (L < 178)
def p_blue(L, A, B):        # the flag's blue field
    return (B < -40) & (L < 120)


def disk(r):
    r = max(1, int(round(r)))
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def fill_small_holes(m, max_area):
    inv = cv2.bitwise_not(m)
    n, lab, st, _ = cv2.connectedComponentsWithStats(inv, 4)
    out = m.copy()
    H, W = m.shape
    for k in range(1, n):
        x, y, w, h, a = st[k]
        if a <= max_area and x > 0 and y > 0 and x + w < W and y + h < H:
            out[lab == k] = 255
    return out


def keep_big(m, min_area, seed=None, min_inside=0.6):
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    out = np.zeros_like(m)
    for k in range(1, n):
        if st[k, cv2.CC_STAT_AREA] < min_area:
            continue
        comp = lab == k
        if seed is not None and (comp & seed).sum() / comp.sum() < min_inside:
            continue
        out[comp] = 255
    return out


def aa(binary, s=0.8):
    f = cv2.GaussianBlur(binary.astype(np.float32) / 255, (0, 0), s)
    return np.clip((f - 0.5) * 2.2 + 0.5, 0, 1)


# ---- the features ---------------------------------------------------------------------------
# id: side, box (x, y, w, h note units), method, options
#   pred   colour predicate          close  closing radius (note units) for solid silhouettes
#   holes  fill holes up to this area (note units^2)   min  smallest piece kept (note units^2)
#   excl   boxes (note units) left out                 poly polygon seed (note units)
F = {
    # ---------- front ----------
    'register':     ('front', (12, 8, 82, 58),    'ink',   dict(pred=p_magenta, min=6, cut=0.5)),
    'flag':         ('front', (90, 9, 86, 56),    'rect',  dict(pred=p_blue)),
    'initials':     ('front', (180, 8, 212, 24),  'ink',   dict(pred=p_initials, min=0.8, cut=0.5)),
    'flag-stars':   ('front', (90, 9, 86, 56),    'ink',   dict(pred=p_yellow, min=0.6, cut=0.4)),
    'signature':    ('front', (224, 33, 118, 62), 'ink',   dict(pred=p_navy, min=0.6, cut=0.6)),
    'bar':          ('front', (378, 22, 30, 78),  'solid', dict(pred=p_navy, min=40, close=0.8, holes=60, hull=True)),
    'numeral':      ('front', (424, 8, 216, 100), 'solid', dict(pred=p_wine, min=30, close=1.1, holes=40, open=3.0)),
    'tactile-top':  ('front', (664, 8, 50, 166),  'ink',   dict(pred=p_dark, min=4, cut=0.5)),
    'tactile-bottom': ('front', (664, 248, 50, 70), 'ink', dict(pred=p_dark, min=4, cut=0.5)),
    'eurion':       ('front', (158, 50, 512, 252), 'ink',  dict(pred=p_yellow, min=1.2, cut=0.6, circles=True,
                                                               excl=[(330, 60, 270, 260), (600, 185, 110, 120)])),
    'architecture': ('front', (334, 60, 272, 246), 'sam',  dict(pts=[(355, 200), (420, 200), (540, 200), (540, 120),
                                                                    (400, 290), (560, 285)],
                                                               neg=[(450, 40), (395, 50), (630, 230)])),
    'hologram':     ('front', (606, 190, 102, 104), 'solid', dict(pred=p_foil, min=20, close=1.6, holes=10 ** 6,
                                                                largest=True, open=1.2, excl=[(664, 248, 50, 50)])),
    # the large stars that glow under UV: located on the ECB's own UV photograph of the note
    # (source/uv-front-ecb-commons.jpg), registered by scale; the glow takes that shape
    'uv-stars':     ('front', (150, 20, 520, 300), 'uvphoto', dict(min=150)),
    'ir-right':     ('front', (480, 0, 240, 320), 'full',  dict()),     # the IR feature's area (no cut-out: the issuers name only the area)
    # ---------- back ----------
    'register-b':   ('back', (628, 6, 80, 66),    'ink',   dict(pred=p_purple, min=6, cut=0.5)),
    'ovi':          ('back', (570, 246, 140, 72), 'solid', dict(pred=p_purple, min=40, close=0.9, holes=25)),
    'serial-top':   ('back', (470, 26, 150, 30),  'ink',   dict(pred=p_black, min=1, cut=0.5)),
    'serial-left':  ('back', (118, 228, 154, 34), 'ink',   dict(pred=p_black, min=1, cut=0.5)),
    'bridge':       ('back', (4, 8, 544, 162),    'ink',   dict(pred=p_magenta, min=3, cut=0.5, lines=3.0,
                                                               excl=[(4, 8, 34, 80), (4, 100, 34, 70), (20, 10, 80, 30), (430, 92, 120, 80), (4, 142, 544, 30)])),
    'map':          ('back', (336, 100, 222, 220), 'sam',  dict(pts=[(450, 230), (500, 190), (410, 250), (520, 130),
                                                                    (380, 270)],
                                                               neg=[(600, 180), (300, 200), (480, 300)])),
    'value-back':   ('back', (10, 248, 246, 72),  'ink',   dict(pred=lambda L, A, B: (A > 24) & (L < 185), min=6, cut=0.5)),
    'eurion-b':     ('back', (326, 10, 220, 300), 'ink',   dict(pred=p_yellow, min=1.2, cut=0.6, circles=True)),
}


def art(side):
    return Image.open(os.path.join(ROOT, SRC[side])).convert('RGB')


def px_box(box, im):
    W, H = im.size
    sx, sy = W / VB_W, H / VB_H
    x, y, w, h = box
    return (int(round(x * sx)), int(round(y * sy)), int(round((x + w) * sx)), int(round((y + h) * sy))), sx, sy


def run_sam(targets, imgs):
    import torch
    from transformers import SamModel, SamProcessor
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = SamModel.from_pretrained('facebook/sam-vit-large').to(dev).eval()
    proc = SamProcessor.from_pretrained('facebook/sam-vit-large')
    os.makedirs(SAMDIR, exist_ok=True)
    for fid in targets:
        side, box, _, o = F[fid]
        im = imgs[side]
        (x0, y0, x1, y1), sx, sy = px_box(box, im)
        m = 12
        cb = (max(0, x0 - int(m * sx)), max(0, y0 - int(m * sy)), min(im.width, x1 + int(m * sx)), min(im.height, y1 + int(m * sy)))
        crop = im.crop(cb)
        to = lambda X, Y: [X * sx - cb[0], Y * sy - cb[1]]
        pts = [to(*p) for p in o['pts']] + [to(*p) for p in o['neg']]
        labels = [1] * len(o['pts']) + [0] * len(o['neg'])
        inputs = proc(crop, input_boxes=[[[x0 - cb[0], y0 - cb[1], x1 - cb[0], y1 - cb[1]]]],
                      input_points=[[pts]], input_labels=[[labels]], return_tensors='pt').to(dev)
        with torch.no_grad():
            out = model(**inputs, multimask_output=True)
        masks = proc.image_processor.post_process_masks(out.pred_masks.cpu(), inputs['original_sizes'].cpu(),
                                                        inputs['reshaped_input_sizes'].cpu())[0][0].numpy()
        scores = out.iou_scores.cpu()[0, 0].numpy()
        k = int(np.argmax(scores))
        full = np.zeros((im.height, im.width), np.uint8)
        full[cb[1]:cb[3], cb[0]:cb[2]] = masks[k].astype(np.uint8) * 255
        Image.fromarray(full).save(os.path.join(SAMDIR, f'{side}-{fid}.png'), optimize=True)
        print(f'sam {fid}: mask {k} score {scores[k]:.3f}')


def isolate(fid, im):
    side, box, method, o = F[fid]
    (x0, y0, x1, y1), sx, sy = px_box(box, im)
    s = (sx + sy) / 2
    rgb = np.asarray(im.crop((x0, y0, x1, y1)))
    L, A, B = lab_of(rgb)
    hh, ww = rgb.shape[:2]
    seed = np.ones((hh, ww), bool)
    for ex, ey, ew, eh in o.get('excl', ()):
        seed[max(0, int((ey - box[1]) * sy)):max(0, int((ey + eh - box[1]) * sy)),
             max(0, int((ex - box[0]) * sx)):max(0, int((ex + ew - box[0]) * sx))] = False
    if method == 'sam':
        full = np.asarray(Image.open(os.path.join(SAMDIR, f'{side}-{fid}.png')))
        m = full[y0:y1, x0:x1].copy()
        n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
        if n > 1:                                   # one object: its largest piece, holes filled
            m = ((lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))) * 255).astype(np.uint8)
        m = fill_small_holes(m, 10 ** 9)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(0.5 * s))
        cut = ink = m
    elif method == 'uvphoto':
        uv = np.asarray(Image.open(os.path.join(ROOT, 'source', 'uv-front-ecb-commons.jpg')).convert('RGB')).astype(np.float32)
        R, G, Bc = uv[..., 0], uv[..., 1], uv[..., 2]
        red = ((R > 120) & (R - G > 40) & (Bc < 235)).astype(np.uint8) * 255      # red / pink glow on the blue-violet note
        red = fill_small_holes(cv2.morphologyEx(red, cv2.MORPH_CLOSE, disk(2)), 400)
        ux, uy = uv.shape[1] / VB_W, uv.shape[0] / VB_H
        red = keep_big(red, int(o['min'] * ux * uy))
        full = cv2.resize(cv2.GaussianBlur(red.astype(np.float32), (0, 0), 1.0), (im.width, im.height), interpolation=cv2.INTER_CUBIC)
        m = ((full[y0:y1, x0:x1] > 110) * 255).astype(np.uint8)
        cut = ink = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(2))
    elif method == 'full':
        cut = ink = np.full((hh, ww), 255, np.uint8)
    elif method == 'rect':
        m = (o['pred'](L, A, B) * 255).astype(np.uint8)
        m = keep_big(m, int(50 * s * s))
        ys, xs = np.where(m > 0)
        cut = np.zeros_like(m)
        cut[ys.min():ys.max() + 1, xs.min():xs.max() + 1] = 255
        ink = cut
    else:
        m = (o['pred'](L, A, B) & seed).astype(np.uint8) * 255
        if o.get('lines'):                      # only strokes darker than their surroundings (black-hat), not fills
            bh = cv2.morphologyEx(L, cv2.MORPH_BLACKHAT, disk(o['lines'] * s))
            m &= ((bh > 14) * 255).astype(np.uint8)
        if o.get('dark'):                       # only clearly printed strokes, not pale tints
            m &= ((L < np.percentile(L, 60)) * 255).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(0.18 * s))
        m = keep_big(m, int(o.get('min', 2) * s * s))
        if method == 'solid':
            ink = m
            m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, disk(o['close'] * s))
            m = fill_small_holes(m, int(o.get('holes', 0) * s * s))
            if o.get('open'):                   # thin print touching the feature (hatching, lines) drops off
                m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(o['open'] * s))
            m = keep_big(m, int(o.get('min', 2) * s * s))
            if o.get('largest'):
                n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
                if n > 1:
                    m = ((lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))) * 255).astype(np.uint8)
            if o.get('hull'):
                cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                cv2.fillPoly(m, [cv2.convexHull(np.vstack(cnts))], 255)
            cut = m
            ink = cv2.bitwise_and(cut, cv2.dilate(ink, disk(1)))

        else:
            if o.get('circles'):                # the rings: fill each small circle, it is one mark
                m = fill_small_holes(cv2.morphologyEx(m, cv2.MORPH_CLOSE, disk(0.25 * s)), int(12 * s * s))
            ink = m
            cut = cv2.dilate(m, disk(o.get('cut', 0.5) * s))
    a_cut, a_ink = aa(cut), aa(ink)
    # ink colour: un-mix the paper from partly covered edge pixels
    paper = np.array([250, 246, 250], np.float32)
    safe = np.maximum(a_ink, 0.25)[..., None]
    ink_rgb = np.clip((rgb.astype(np.float32) - paper * (1 - safe)) / safe, 0, 255).astype(np.uint8)
    ink_rgb = np.where(a_ink[..., None] > 0.97, rgb, ink_rgb)
    return dict(cut=np.dstack([rgb, (a_cut * 255).astype(np.uint8)]),
                ink=np.dstack([ink_rgb, (a_ink * 255).astype(np.uint8)]),
                box=box, px=(x0, y0, x1, y1), mask=cut)


def save_layer(arr, name):
    ov = os.path.join(OVR, name)
    img = Image.fromarray(arr, 'RGBA')
    size = (max(1, round(img.width * SCALE)), max(1, round(img.height * SCALE)))
    if os.path.exists(ov):
        img = Image.open(ov).convert('RGBA')
        print('  using override', name)
    img.resize(size, Image.LANCZOS).save(os.path.join(LAYERS, name), optimize=True)


def trim(arr, margin=10):
    ys, xs = np.where(arr[..., 3] > 6)
    if not len(xs):
        return arr
    return arr[max(0, ys.min() - margin):ys.max() + margin + 1, max(0, xs.min() - margin):xs.max() + margin + 1]


# ---- the offset print: what is left once intaglio, foil, silk-screen and letterpress are taken off
OFFSET_REMOVE = {'front': ['architecture', 'numeral', 'initials', 'bar', 'tactile-top', 'tactile-bottom', 'hologram'],
                 'back': ['ovi', 'serial-top', 'serial-left']}


def write_offset(imgs, res):
    for side, im in imgs.items():
        rgb = np.asarray(im)
        H, W = rgb.shape[:2]
        hole = np.zeros((H, W), np.uint8)
        for fid in OFFSET_REMOVE[side]:
            x0, y0, x1, y1 = res[fid]['px']
            hole[y0:y1, x0:x1] = np.maximum(hole[y0:y1, x0:x1], res[fid]['mask'])
        hole = cv2.dilate(hole, disk(4))
        q = 4
        small = cv2.resize(rgb, (W // q, H // q), interpolation=cv2.INTER_AREA)
        ms = cv2.resize(hole, (W // q, H // q), interpolation=cv2.INTER_NEAREST)
        f = cv2.inpaint(cv2.cvtColor(small, cv2.COLOR_RGB2BGR), ms, 10, cv2.INPAINT_TELEA)
        f = cv2.cvtColor(cv2.resize(f, (W, H), interpolation=cv2.INTER_CUBIC), cv2.COLOR_BGR2RGB)
        b = cv2.GaussianBlur(hole.astype(np.float32) / 255, (0, 0), 2.0)[..., None]
        out = (rgb * (1 - b) + f * b).astype(np.uint8)
        Image.fromarray(out).resize((2160, 1107), Image.LANCZOS).save(
            os.path.join(ROOT, 'assets', f'offset-{side}.jpg'), quality=88, optimize=True)


def png_uri(img):
    buf = io.BytesIO()
    img.save(buf, 'PNG', optimize=True)
    return f'url("data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}")'


def write_masks_css():
    """Masks as data URIs (file:// cannot fetch mask images): optical effects + line-work."""
    out = ['/* generated by tools/cutouts.py: effect masks as data URIs (plain rules, parsed once) */']
    for sel, name in (('.holo-diff, .holo-glyphs', 'front-hologram-cut'), ('.ovi-tint', 'back-ovi-cut')):
        img = Image.open(os.path.join(LAYERS, name + '.png')).convert('RGBA')
        k = min(1.0, 600 / max(img.size))
        img = img.resize((round(img.width * k), round(img.height * k)), Image.LANCZOS)
        m = Image.new('LA', img.size, 255)
        m.putalpha(img.getchannel('A'))
        out.append(f'{sel}{{-webkit-mask-image:{png_uri(m)};mask-image:{png_uri(m)}}}')
    for side, cls in (('front', '.flow-front'), ('back', '.flow-back')):
        im = art(side).resize((1080, 554), Image.LANCZOS)
        L = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
        bg = cv2.GaussianBlur(cv2.morphologyEx(L, cv2.MORPH_CLOSE, disk(4)), (0, 0), 3)
        lines = (bg - L - 9) > 0
        a = Image.fromarray((lines * 255).astype(np.uint8)).convert('1')
        u = png_uri(a)
        out.append(f'{cls}{{-webkit-mask-mode:luminance;mask-mode:luminance;-webkit-mask-image:{u};mask-image:{u}}}')
    open(os.path.join(ROOT, 'assets', 'masks.css'), 'w', encoding='utf8').write('\n'.join(out) + '\n')


def contact_sheet():
    files = []
    for side in ('front', 'back'):
        d = os.path.join(CROPS, side)
        files += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith('.png')]
    cols, cw, ch = 5, 300, 220
    rows = math.ceil(len(files) / cols)
    sheet = Image.new('RGB', (cols * cw, rows * ch), (24, 18, 40))
    dr = ImageDraw.Draw(sheet)
    for i, p in enumerate(files):
        t = Image.open(p)
        t.thumbnail((cw - 16, ch - 30))
        cx, cy = (i % cols) * cw, (i // cols) * ch
        sheet.paste(t, (cx + (cw - t.width) // 2, cy + 6), t)
        dr.text((cx + 6, cy + ch - 18), os.path.relpath(p, CROPS), fill=(230, 220, 255))
    sheet.save(os.path.join(CROPS, 'contact-sheet.png'))


def clean_layers():
    """Delete layer images the page does not reference (assets/overrides/ is never touched)."""
    import re as _re
    rd = lambda f: open(os.path.join(ROOT, f), encoding='utf8').read()
    data, script, other = rd('data.js'), rd('script.js'), rd('styles.css') + rd('index.html')
    text_glow = set(_re.findall(r"'([\w-]+)'", _re.search(r'TEXT_GLOW = new Set\(\[(.*?)\]', script, _re.S).group(1)))
    used = set()
    for src in _re.findall(r"P\('(?:front|back)','([\w-]+)'", data):
        used.add(src + '.png' if src in text_glow else src + '-cut.png')
    used |= {m + '.png' for m in _re.findall(r"\['([\w-]+)'\]", data)}                  # exploded-view pieces
    used |= {m + '.png' for m in _re.findall(r"uvFluo\('([\w-]+)'", script)}
    used |= set(_re.findall(r'assets/layers/([\w-]+\.png)', script + other))
    gone = [f for f in os.listdir(LAYERS) if f not in used]
    for f in gone:
        os.remove(os.path.join(LAYERS, f))
    missing = sorted(f for f in used if not os.path.exists(os.path.join(LAYERS, f)))
    print('clean_layers: removed', ' '.join(gone) or 'nothing', '| missing:', ' '.join(missing) or 'none')


def main():
    imgs = {s: art(s) for s in SRC}
    sam_ids = [k for k, v in F.items() if v[2] == 'sam']
    if '--no-sam' not in sys.argv:
        run_sam(sam_ids, imgs)
    os.makedirs(LAYERS, exist_ok=True)
    boxes, res = {}, {}
    for fid, (side, box, method, o) in F.items():
        r = isolate(fid, imgs[side])
        res[fid] = r
        x0, y0, x1, y1 = r['px']
        W, H = imgs[side].size
        name = f'{side}-{fid}'
        boxes[name] = [round(x0 * VB_W / W, 3), round(y0 * VB_H / H, 3), round((x1 - x0) * VB_W / W, 3), round((y1 - y0) * VB_H / H, 3)]
        save_layer(r['ink'], name + '.png')
        save_layer(r['cut'], name + '-cut.png')
        d = os.path.join(CROPS, side)
        os.makedirs(d, exist_ok=True)
        Image.fromarray(trim(r['cut']), 'RGBA').save(os.path.join(d, f'{fid}.png'), optimize=True)
        print(f'{side:5} {fid:15} {method:5} box {boxes[name]}')
    with open(os.path.join(ROOT, 'assets', 'boxes.js'), 'w', encoding='utf8') as f:
        f.write('// generated by tools/cutouts.py: where each extracted layer sits (720 x 320 note units)\n')
        f.write('const BOXES = ' + json.dumps(boxes, indent=1) + ';\n')
    write_offset(imgs, res)
    write_masks_css()
    contact_sheet()
    if '--clean' in sys.argv:          # after tools/watermark.py, make_thread.py, holo_window.py have run
        clean_layers()


if __name__ == '__main__':
    main()
