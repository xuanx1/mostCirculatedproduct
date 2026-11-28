"""
Remove the SPECIMEN overprint from both sides of the $100 working artwork with LaMa inpainting
(big-lama, TorchScript release of simple-lama-inpainting; Suvorov et al., LaMa).

The Bank of Canada's images carry a translucent dark grey SPECIMEN diagonally across each side. Per side:
  1. Letter mask: inside a hand-placed band along the word, the pixels that are darker than their own
     neighbourhood (a 101 px median) AND greyer than it (or grey outright, over the white numeral),
     opened, closed into solid letters, small holes filled, grown a few px.
     On the front most of the word lies over the sepia portrait, where that test is weak, so the letter
     shapes are taken from the back (same lettering, cleanly found on the orange paper), fitted onto the
     front's well-found letters (M E N on the cream) by a similarity transform, and joined with what the
     front's own test finds next to them.
  2. Real print the word crosses is protected: dark, coloured pixels (lettering, the numeral's outline)
     are taken out of the mask (KEEP_OUT boxes and the dark-ink test).
  3. LaMa fills the mask in the colour channels where the polymer is printed (alpha opaque).
  4. Alpha: kept exactly as it is everywhere, EXCEPT where the overprint itself lies on a clear window:
     there the Bank's image draws the letters as half-opaque grey on the clear polymer, so those letter
     pixels (only those) are made clear again, with the window's 1 px anti-aliased edge kept.
  5. A small second LaMa pass over any spot that still shows residue (TIPS).

The untouched working artwork is kept as source/<side>-working-specimen.png (made on first run), so this
can be re-run. Writes cad-100-<side>.png. Then run python tools/cad_isolate.py to rebuild every cut-out.
Note: tools/upscale.py rebuilds cad-100-*.png from the Bank's originals and so brings SPECIMEN back; run
this script again after it.

  python tools/remove_specimen.py [front|back] [--preview]
"""
import os, sys, shutil
import numpy as np, cv2
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAMA = os.environ.get('LAMA_MODEL', r'C:/Users/65963/AppData/Local/Temp/claude/c0d258789f1d297c/94e98cd5-0543-44a8-952a-896d58182aaf/scratchpad/lama/big-lama.pt')
PREVIEW_DIR = os.environ.get('SPECIMEN_PREVIEW', os.path.join(ROOT, 'source'))

# The overprint sits at the same pixels on both sides (checked: best match of the front's and the back's
# letters is a (0, 0) shift). px of the 2000 x 916 artwork.
BAND = [(585, 630), (1460, 418), (1460, 625), (605, 830)]       # along the word
FRONT_FROM_X = 1060           # the front's own test is used only right of the portrait (M E N on the cream)
JUNK = [[(1395, 600), (1460, 600), (1460, 660), (1395, 660)],    # the numeral 1's outline below the N (back)
        [(1430, 440), (1470, 440), (1470, 600), (1430, 600)],    # ... and its stem's edge
        [(1250, 445), (1300, 445), (1300, 482), (1250, 482)],    # a knob of the microscope (back)
        ]
FRONT_ONLY = [(1190, 480), (1305, 480), (1305, 670), (1190, 670)]   # the E over the insulin bottle on the
                                                                     # back: its shape from the front only
# hand-drawn strokes (centre line, width px) where neither side shows the letter well: the S over the
# window's dark border and the portrait's suit, the N over the dark border
STROKES = [([(692, 656), (670, 654), (650, 657), (637, 667), (633, 682), (640, 697), (657, 706), (683, 713),
             (702, 723), (709, 738), (706, 752), (693, 762), (672, 766), (648, 764)], 12),   # S
           ([(1317, 505), (1336, 620)], 14),                    # N left stem
           ([(1320, 509), (1412, 604)], 14),                    # N diagonal
           ([(1396, 490), (1417, 605)], 14)]                    # N right stem
HAND_ONLY = [[(600, 630), (719, 630), (719, 840), (600, 840)]]   # the S: hand stroke + window letters only
KEEP_OUT = {'back': [], 'front': []}           # boxes (x0, y0, x1, y1) never masked
# rows of real lettering the word crosses: inside these boxes the dark ink is never masked
TEXT_ROWS = {'back': [(835, 724, 1095, 762)]}  # INNOVATION MEDICALE under the E
# thin lines the word crosses (the ECG trace): kept, and lifted by the ratio LaMa applied around them
LINES = {'back': [(694, 558, 1194, 710)]}
LINE_RADIUS = 1.4                # half-width of the trace, px (measured outside the letters)
LINE_BRIDGE = 9                  # px: breaks in its centre line bridged up to this
SNAP = 2                         # px a guide point may move to the trace's ridge
# guide for the ECG trace's centre line across the letters (read from the un-blended image), back side
TRACE = {'back': [[(690, 680), (697, 674), (707, 667), (716, 673), (723, 678), (750, 678), (757, 578),
                   (764, 692), (771, 680), (800, 679), (812, 670), (822, 662), (830, 661), (840, 669),
                   (850, 677), (870, 679), (890, 676), (899, 670), (906, 667), (913, 672), (920, 678),
                   (955, 678), (962, 577), (970, 692), (976, 680), (1000, 678), (1010, 675), (1020, 667),
                   (1030, 661), (1040, 663), (1050, 672), (1058, 678), (1080, 679), (1095, 676),
                   (1105, 668), (1113, 672), (1120, 678), (1158, 678), (1166, 577), (1172, 698),
                   (1177, 680), (1194, 678)]]}
LINE_GB = 88                     # the trace's G - B (paper ~80, the grey film ~0)
LINE_RIDGE = 12                  # green-minus-red ridge height of the trace (as outside the letters)
# boxes where the other side's clear window holds the overprint's exact soft shape (its alpha); there the
# film is divided out instead of inpainted. The back's numeral 1, whose white flag the N crosses.
UNBLEND = {'back': [((1350, 440, 1465, 640), 'front')]}
FILM_ALPHA = 121.0                              # the overprint's alpha on a clear window (median)
NUMERAL_WHITE = (255, 255, 249)
FILM_GAIN = np.array([0.655, 0.64, 0.65], np.float32)   # it darkens the print by this (on the numeral's white)
SMOOTH = {'front': [(1060, 430, 1330, 700)]}   # flat paper: smooth fill (see run)
TIPS = {'back': [], 'front': []}
TEXT_FILM = {'back': [(828, 690, 905, 745)]}   # the E's foot over 'INN': film divided out (see run)                                # polygons for a second small pass


def disk(r):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def poly(pts, shape):
    m = np.zeros(shape, np.uint8); cv2.fillPoly(m, [np.array(pts, np.int32)], 255)
    return m


def fill_small_holes(m, max_area):
    ff = m.copy(); cv2.floodFill(ff, np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8), (0, 0), 255)
    n, lab, st, _ = cv2.connectedComponentsWithStats((~ff) & 255, 8)
    out = m.copy()
    out[np.isin(lab, 1 + np.nonzero(st[1:, cv2.CC_STAT_AREA] < max_area)[0])] = 255
    return out


def big_only(m, min_area):
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    return np.isin(lab, 1 + np.nonzero(st[1:, cv2.CC_STAT_AREA] >= min_area)[0]).astype(np.uint8) * 255


def unblend_model(rgba, core):
    """the overprint as a grey film: observed = g * print + b per channel, fitted on letter cores
    against the print around them (a 101 px median)"""
    rgb = rgba[..., :3].astype(np.float32)
    local = np.dstack([cv2.medianBlur(rgba[..., c], 101) for c in range(3)]).astype(np.float32)
    G, B = [], []
    for c in range(3):
        x, y = local[..., c][core], rgb[..., c][core]
        (g, b), *_ = np.linalg.lstsq(np.vstack([x, np.ones_like(x)]).T, y, rcond=None)
        G.append(g); B.append(b)
    return local, np.array(G), np.array(B)


def overprinted(rgba, local, G, B, thr=12):
    """pixels closer to 'print under the film' than to the print itself"""
    rgb = rgba[..., :3].astype(np.float32)
    d0 = np.linalg.norm(rgb - local, axis=2)
    d1 = np.linalg.norm(rgb - (local * G + B), axis=2)
    zone = poly(BAND, rgb.shape[:2]) > 0
    return ((d1 < d0) & (d0 > thr) & zone & (rgba[..., 3] >= 250)).astype(np.uint8) * 255


def simple_core(rgba):
    """first guess at letter pixels on the back's orange paper: darker and greyer than the neighbourhood"""
    lab = cv2.cvtColor(rgba[..., :3], cv2.COLOR_RGB2LAB).astype(np.float32)
    L, C = lab[..., 0], np.hypot(lab[..., 1] - 128, lab[..., 2] - 128)
    bgL = cv2.medianBlur(L.astype(np.uint8), 101).astype(np.float32)
    bgC = cv2.medianBlur(C.astype(np.uint8), 101).astype(np.float32)
    zone = poly(BAND, L.shape)
    m = ((L < bgL - 10) & (C < bgC - 8) & (rgba[..., 3] >= 250) & (zone > 0)).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(2))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, disk(7))
    return cv2.erode(big_only(m, 1500), disk(4)) > 0


def window_letters(rgba):
    """the overprint where it lies on a clear window: half-opaque grey (the window's own edge is a thin
    1-2 px ramp; the letters are ~14 px strokes)"""
    rgb, alpha = rgba[..., :3], rgba[..., 3]
    L = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
    zone = poly(BAND, L.shape)
    m = ((alpha > 25) & (alpha < 235) & (L < 140) & (zone > 0)).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(3))
    m = big_only(m, 150)
    return cv2.dilate(m, disk(2)) & ((alpha < 250) * 255).astype(np.uint8)


FILM = [None, None]           # the overprint's per-channel gain and offset, fitted in template()


def template(arts):
    """the letters, the same on both sides: from the back's orange paper, the front's cream (right of the
    portrait), both sides' window letters, the hand-drawn strokes, minus the junk boxes"""
    b, f = arts['back'], arts['front']
    local_b, G, B = unblend_model(b, simple_core(b))
    local_f = np.dstack([cv2.medianBlur(f[..., c], 101) for c in range(3)]).astype(np.float32)
    t = cv2.morphologyEx(overprinted(b, local_b, G, B), cv2.MORPH_OPEN, disk(4))
    t[poly(FRONT_ONLY, t.shape) > 0] = 0
    cream = (local_f @ np.array([.299, .587, .114], np.float32)) > 160
    tf = cv2.morphologyEx(overprinted(f, local_f, G, B) & (cream * 255).astype(np.uint8), cv2.MORPH_OPEN, disk(4))
    tf[:, :FRONT_FROM_X] = 0
    t |= tf
    for p in JUNK + HAND_ONLY:
        t[poly(p, t.shape) > 0] = 0
    t |= window_letters(b) | window_letters(f)
    for pts, w in STROKES:
        cv2.polylines(t, [np.array(pts, np.int32)], False, 255, w, cv2.LINE_AA)
    t = (t > 127).astype(np.uint8) * 255
    t = cv2.morphologyEx(t, cv2.MORPH_CLOSE, disk(3))
    t = fill_small_holes(t, 400)
    FILM[:] = [G, B]
    return big_only(t, 300)


def protect(m, rgba, side):
    for x0, y0, x1, y1 in KEEP_OUT.get(side, []):
        m[y0:y1, x0:x1] = 0
    L = cv2.cvtColor(rgba[..., :3], cv2.COLOR_RGB2LAB)[..., 0]
    for x0, y0, x1, y1 in TEXT_ROWS.get(side, []):
        ink = cv2.dilate((L[y0:y1, x0:x1] < 92).astype(np.uint8) * 255, disk(1))
        m[y0:y1, x0:x1][ink > 0] = 0
    return m


def lama(rgb, m):
    import torch
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = torch.jit.load(LAMA, map_location=dev).eval()
    ys, xs = np.nonzero(m)
    pad = 128
    y0, y1 = max(0, ys.min() - pad), min(rgb.shape[0], ys.max() + pad)
    x0, x1 = max(0, xs.min() - pad), min(rgb.shape[1], xs.max() + pad)
    crop, mc = rgb[y0:y1, x0:x1], m[y0:y1, x0:x1]
    h, w = crop.shape[:2]; H, W = (h + 7) // 8 * 8, (w + 7) // 8 * 8
    im = np.pad(crop, ((0, H - h), (0, W - w), (0, 0)), mode='reflect')
    mk = np.pad(mc, ((0, H - h), (0, W - w)))
    t = torch.from_numpy(np.ascontiguousarray(im)).permute(2, 0, 1)[None].float().div(255).to(dev)
    tm = torch.from_numpy((mk > 127).astype(np.float32))[None, None].to(dev)
    with torch.no_grad():
        out = model(t, tm)[0].permute(1, 2, 0).clamp(0, 1).mul(255).byte().cpu().numpy()[:h, :w]
    res = rgb.copy()
    a = (cv2.GaussianBlur(mc.astype(np.float32) / 255, (0, 0), 1.2))[..., None]
    res[y0:y1, x0:x1] = (crop * (1 - a) + out * a).astype(np.uint8)
    return res


GROW = 7                      # px the letter mask is grown by (the letters' soft edges)


def load():
    arts = {}
    for side in ('front', 'back'):
        art = os.path.join(ROOT, f'cad-100-{side}.png')
        keep = os.path.join(ROOT, 'source', f'{side}-working-specimen.png')
        if not os.path.exists(keep):
            shutil.copyfile(art, keep)
        arts[side] = np.asarray(Image.open(keep).convert('RGBA'))
    return arts


def thin_lines(rgba, tpl, box):
    """the ECG trace under the letters: a thin ridge in green-minus-red (the grey film dims it but keeps
    its shape), small gaps closed"""
    f = rgba[..., :3].astype(np.float32)
    g = f[..., 1] - f[..., 0]
    th = g - cv2.morphologyEx(g, cv2.MORPH_OPEN, disk(4))
    x0, y0, x1, y1 = box
    line = np.zeros(g.shape, np.uint8)
    line[y0:y1, x0:x1] = ((th[y0:y1, x0:x1] > 6) * 255).astype(np.uint8)
    line &= cv2.dilate(tpl, disk(GROW + 4))
    return big_only(cv2.morphologyEx(line, cv2.MORPH_CLOSE, disk(2)), 15)


def line_outside(rgba, tpl, box):
    """the same trace where no letter covers it: its true colour"""
    f = rgba[..., :3].astype(np.float32)
    g = f[..., 1] - f[..., 0]
    th = g - cv2.morphologyEx(g, cv2.MORPH_OPEN, disk(4))
    x0, y0, x1, y1 = box
    out = np.zeros(g.shape, np.float32)
    out[y0:y1, x0:x1] = th[y0:y1, x0:x1] > 12
    out[cv2.dilate(tpl, disk(GROW + 3)) > 0] = 0
    return out


def film_from_alpha(arts, src_side, tpl):
    """where the other side is a clear window, its alpha IS the overprint (half-opaque grey, the same
    pixels on both sides): the film's exact soft shape there (only near the letters)"""
    a = arts[src_side][..., 3].astype(np.float32)
    s = np.clip(a / FILM_ALPHA, 0, 1) * (cv2.dilate(tpl, disk(GROW)) > 0)
    s[a >= 250] = np.nan                          # opaque there: unknown
    return s


def masks_for(rgba, side, tpl, arts):
    alpha = rgba[..., 3]
    printed = cv2.erode(((alpha >= 250) * 255).astype(np.uint8), disk(3))   # not right at a window's edge
    m = big_only(cv2.dilate(tpl, disk(GROW)) & printed, 200)                  # printed: inpaint the colour
    m = protect(m, rgba, side)
    lines = np.zeros_like(m)
    for box in LINES.get(side, []):
        lines |= thin_lines(rgba, tpl, box)
    lines &= m
    unb = np.zeros(m.shape, bool)                 # put back by dividing the film out (exact shape known)
    for (x0, y0, x1, y1), src in UNBLEND.get(side, []):
        s = film_from_alpha(arts, src, tpl)
        u = np.zeros(m.shape, bool); u[y0:y1, x0:x1] = True
        u &= ~np.isnan(s) & (alpha >= 250)
        clean = rgba[..., :3].astype(np.float32) / (1 - np.nan_to_num(s)[..., None] * (1 - FILM_GAIN))
        R_, G_, B_ = clean[..., 0], clean[..., 1], clean[..., 2]
        paper = (R_ - B_ > 80) & (G_ > 45) & (G_ < 140)          # the orange paper: inpainted instead
        keep = ((u & ~paper) * 255).astype(np.uint8)
        unb |= big_only(keep, 40) > 0                              # specks on the paper: inpainted
    m[unb] = 0
    inbox = np.zeros(m.shape, bool)
    for (x0, y0, x1, y1), src in UNBLEND.get(side, []):
        inbox[y0:y1, x0:x1] = True
    m[inbox & ~unb & (cv2.dilate(tpl, disk(GROW)) > 0) & (printed > 0)] = 255   # ... including those specks
    win = window_letters(rgba)                                                # on a clear window
    return m, win, lines, unb


def run(side, arts, tpl, preview=False):
    art = os.path.join(ROOT, f'cad-100-{side}.png')
    rgba = arts[side]
    m, win, lines, unb = masks_for(rgba, side, tpl, arts)
    if preview:
        bg = np.empty_like(rgba[..., :3]); bg[:] = (0, 120, 220)
        a = rgba[..., 3:4].astype(np.float32) / 255
        ov = (rgba[..., :3] * a + bg * (1 - a)).astype(np.uint8)
        ov[m > 0] = (0.45 * ov[m > 0] + [0, 140, 0]).astype(np.uint8)
        ov[win > 0] = (0.45 * ov[win > 0] + [140, 0, 140]).astype(np.uint8)
        ov[lines > 0] = (255, 0, 255)
        ov[unb & (cv2.dilate(tpl, disk(GROW)) > 0)] = (0.45 * ov[unb & (cv2.dilate(tpl, disk(GROW)) > 0)] + [140, 140, 0]).astype(np.uint8)
        Image.fromarray(ov).save(os.path.join(PREVIEW_DIR, f'{side}-specimen-mask-preview.png'))
        print(side, 'mask px', int((m > 0).sum()), 'window px', int((win > 0).sum())); return
    f = rgba[..., :3].astype(np.float32)
    src = rgba[..., :3].copy()
    unb_clean = None
    for (x0, y0, x1, y1), other in UNBLEND.get(side, []):
        sf = np.nan_to_num(film_from_alpha(arts, other, tpl))[..., None]
        unb_clean = np.clip(f / (1 - sf * (1 - FILM_GAIN)), 0, 255).astype(np.uint8)
        cf = unb_clean.astype(np.float32)
        white = ((cf.min(2) > 172) & (np.ptp(cf, axis=2) < 28) & unb).astype(np.uint8) * 255
        white = (cv2.morphologyEx(white, cv2.MORPH_CLOSE, disk(2)) > 0) & unb & (sf[..., 0] > 0)
        # the film's soft edge runs a pixel or two past the other side's (cleaned) window alpha: grey-white
        # pixels right beside the numeral's white are evened out too
        edge = (cv2.dilate(white.astype(np.uint8) * 255, disk(2)) > 0) & ~white & (cv2.dilate(tpl, disk(GROW)) > 0)
        edge &= (f.min(2) > 172) & (np.ptp(f, axis=2) < 28) & (rgba[..., 3] >= 250)
        white |= edge
        unb_clean[white] = NUMERAL_WHITE          # the numeral's flat white (no faint edge of the film left)
        unb |= white
        src[unb] = unb_clean[unb]                 # LaMa sees the restored numeral as context
    out = lama(src, m | win)
    # the thin line the word crosses (the ECG trace): LaMa can't rebuild it, so it is drawn again as a
    # clean stroke along its own path. The path: a hand-placed guide (TRACE), each point snapped to the
    # trace's darkest ridge in the un-blended image (the grey film divided out, FILM) within a few px;
    # width and core colour measured on the trace outside the letters
    if TRACE.get(side):
        G, B = FILM
        s_ = np.clip(cv2.GaussianBlur(tpl.astype(np.float32) / 255, (0, 0), 1.6) * 1.15, 0, 1)[..., None]
        U = np.clip((f - B * s_) / (1 - (1 - G) * s_), 0, 255)
        LU = U @ np.array([.299, .587, .114], np.float32)
        ridge = cv2.GaussianBlur(cv2.morphologyEx(LU, cv2.MORPH_CLOSE, disk(4)) - LU, (0, 0), 0.8)
        cl = np.zeros(m.shape, bool)
        for box in LINES[side]:
            cl |= line_outside(rgba, tpl, box) > 0
        g0 = f[..., 1] - f[..., 0]
        th0 = g0 - cv2.morphologyEx(g0, cv2.MORPH_OPEN, disk(4))
        col = np.median(f[cl & (th0 >= np.percentile(th0[cl], 60))], 0)
        stroke = np.zeros(m.shape, np.uint8)
        for guide in TRACE[side]:
            pts = []
            for (x0, y0), (x1, y1) in zip(guide[:-1], guide[1:]):
                n = max(2, int(np.hypot(x1 - x0, y1 - y0)))
                for t in np.linspace(0, 1, n, endpoint=False):
                    pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, -(y1 - y0), x1 - x0))
            pts.append((guide[-1][0], guide[-1][1], 0, 0))
            offs = []
            for x, y, nx, ny in pts:
                l = np.hypot(nx, ny)
                if l == 0:
                    offs.append(0); continue
                nx, ny = nx / l, ny / l
                cand = [(ridge[int(round(y + k * ny)), int(round(x + k * nx))], k) for k in np.arange(-SNAP, SNAP + 0.5, 0.5)]
                offs.append(max(cand)[1])
            offs = np.array(offs, np.float32)
            offs = np.array([np.median(offs[max(0, i - 6):i + 7]) for i in range(len(offs))])
            poly_pts = []
            for (x, y, nx, ny), o in zip(pts, offs):
                l = np.hypot(nx, ny) or 1
                poly_pts.append((x + o * nx / l, y + o * ny / l))
            P = (np.array(poly_pts) * 8).round().astype(np.int32)
            cv2.polylines(stroke, [P], False, 1, 1, cv2.LINE_8, shift=3)
        dist = cv2.distanceTransform((1 - stroke).astype(np.uint8), cv2.DIST_L2, 5)
        alpha_l = cv2.GaussianBlur(np.clip(LINE_RADIUS + 0.5 - dist, 0, 1).astype(np.float32), (0, 0), 0.6)[..., None]
        zone = (cv2.dilate(stroke, disk(6)) > 0) & (m > 0)
        nz = (~zone & (m > 0)).astype(np.float32)
        paper = out.astype(np.float32).copy(); done = np.zeros(m.shape, bool)
        for sig in (3, 6, 12):                    # the paper LaMa made just outside the zone
            den = cv2.GaussianBlur(nz, (0, 0), sig)
            est = cv2.GaussianBlur(out.astype(np.float32) * nz[..., None], (0, 0), sig) / np.maximum(den, 1e-6)[..., None]
            ok = (den > 0.05) & ~done
            paper[ok] = est[ok]; done |= ok
        core = (cl & (th0 >= np.percentile(th0[cl], 60))).astype(np.float32)
        w = cv2.GaussianBlur(core, (0, 0), 25)[..., None]              # the trace's colour nearby (it
        loc = cv2.GaussianBlur(f * core[..., None], (0, 0), 25) / np.maximum(w, 1e-6)   # pales to the right)
        col = np.where(w > 0.002, loc, col)
        comp = paper * (1 - alpha_l) + col * alpha_l
        out[zone] = np.clip(comp, 0, 255)[zone].astype(np.uint8)
    changed = (m > 0) | (win > 0) | unb
    # lettering the word crosses (kept out of the mask): divide the grey film back out of its pixels
    G, B = FILM
    s_ = np.clip(cv2.GaussianBlur(tpl.astype(np.float32) / 255, (0, 0), 1.6) * 1.15, 0, 1)[..., None]
    ink = np.zeros(m.shape, bool)
    for x0, y0, x1, y1 in TEXT_ROWS.get(side, []):
        ink[y0:y1, x0:x1] = True
    ink &= (m == 0) & (s_[..., 0] > 0.02) & (rgba[..., 3] >= 250) & (lines == 0)
    clean = np.clip((f - B * s_) / (1 - (1 - G) * s_), 0, 255)
    out[ink] = clean[ink].astype(np.uint8)
    changed |= ink
    # flat paper (the front's cream right of the portrait): LaMa leaves a faint outline of the letters
    # there, so the letters and a ring around them are filled from the paper outside by a smooth
    # normalised blur instead (the paper there is a smooth gradient with no print)
    for (x0, y0, x1, y1) in SMOOTH.get(side, []):
        box = np.zeros(m.shape, bool); box[y0:y1, x0:x1] = True
        L0 = cv2.cvtColor(rgba[..., :3], cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
        paper = cv2.medianBlur(L0.astype(np.uint8), 101).astype(np.float32) > 200
        dark = cv2.dilate(((L0 < 150) & (cv2.dilate(tpl, disk(GROW)) == 0)).astype(np.uint8), disk(6)) > 0
        hole = (cv2.dilate(m, disk(3)) > 0) & box & paper & ~dark & (rgba[..., 3] >= 250)
        known = (~(cv2.dilate(hole.astype(np.uint8), disk(1)) > 0) & ~(cv2.dilate(tpl, disk(GROW + 4)) > 0)
                 & ~dark & (rgba[..., 3] >= 250)).astype(np.float32)
        fill = np.zeros_like(f)
        for sig in (6, 12, 24):                  # finest scale that has support
            num = cv2.GaussianBlur(f * known[..., None], (0, 0), sig)
            den = cv2.GaussianBlur(known, (0, 0), sig)[..., None]
            est = num / np.maximum(den, 1e-6)
            fill = np.where((den > 0.08) & (fill.sum(2, keepdims=True) == 0), est, fill)
        fill = np.where(fill.sum(2, keepdims=True) == 0, out, fill)
        soft = cv2.GaussianBlur(hole.astype(np.float32), (0, 0), 1.5)[..., None]
        sel = soft[..., 0] > 0.01
        mix = out * (1 - soft) + fill * soft
        out[sel] = np.clip(mix, 0, 255)[sel].astype(np.uint8)
        changed |= sel
    # where the word crosses printed lettering on smooth paper (the E over 'INN'): the film's opacity is
    # measured pixel by pixel on the paper (against the paper outside the film, filled in smoothly), filled
    # in under the ink strokes from around them, and divided out of every pixel: the strokes come back
    # exactly as printed, the paper flat
    G, B = FILM
    Lw = np.array([.299, .587, .114], np.float32)
    for (x0, y0, x1, y1) in TEXT_FILM.get(side, []):
        sl = np.s_[y0:y1, x0:x1]
        F = f[sl]; T = cv2.dilate(tpl, disk(GROW + 2))[sl] > 0
        LF = F @ Lw
        def smooth_fill(known):
            P = np.zeros_like(F); done = np.zeros(LF.shape, bool)
            for sig in (4, 8, 16, 32):
                den = cv2.GaussianBlur(known, (0, 0), sig)
                est = cv2.GaussianBlur(F * known[..., None], (0, 0), sig) / np.maximum(den, 1e-6)[..., None]
                ok = (den > 0.05) & ~done; P[ok] = est[ok]; done |= ok
            return P
        P = smooth_fill((~T & (LF > 130)).astype(np.float32))        # the paper, from outside the film
        Lf = (P * G + B) @ Lw                                         # ... and with the film on it
        inkc = LF < np.minimum(Lf, P @ Lw) - 18                       # the printed strokes: darker than both
        inkc = cv2.dilate(inkc.astype(np.uint8), disk(1)) > 0
        inkc = cv2.morphologyEx(inkc.astype(np.uint8), cv2.MORPH_OPEN, disk(1)) > 0
        r = F / np.maximum(P, 1)                                      # the film here: a plain multiply,
        core = T & ~inkc & (r.mean(2) < 0.8)                          # its gain fitted on its own core
        g = np.median(r[core], 0)
        sm = np.clip(((1 - r) / np.maximum(1 - g, 0.05)).mean(2), 0, 1)   # film opacity on the paper
        sm[~T] = 0
        sm8 = (sm * 255).astype(np.uint8)
        sm = cv2.inpaint(sm8, (inkc * 255).astype(np.uint8), 3, cv2.INPAINT_TELEA).astype(np.float32) / 255
        sm = sm[..., None]
        Uc = np.clip(F / (1 - (1 - g) * sm), 0, 255)
        sel = np.zeros(m.shape, bool); sel[sl] = T & (rgba[sl][..., 3] >= 250)
        o = out[sl].astype(np.float32)
        Uc[~inkc] = P[~inkc]                         # the paper itself: the smooth paper from outside
        o[T] = Uc[T]
        out[sl] = o.astype(np.uint8)
        changed |= sel
    for p in TIPS.get(side, []):
        tip = protect(poly(p, m.shape) & ((rgba[..., 3] >= 250) * 255).astype(np.uint8), rgba, side)
        out = lama(out, tip)
        changed |= tip > 0
    alpha = rgba[..., 3].copy()
    # letters on a clear window: clear again, keeping the window edge's 1 px ramp from the print beside it
    opaque = ((alpha >= 250) & (win == 0)).astype(np.float32)
    ramp = np.clip((cv2.GaussianBlur(opaque, (0, 0), 0.8) - 0.5) * 2.2 + 0.5, 0, 1) * 255
    alpha[win > 0] = np.minimum(alpha[win > 0], ramp[win > 0]).astype(np.uint8)
    changed &= rgba[..., 3] >= 10                  # never touch the colour under the clear polymer
    res = rgba.copy()
    res[..., :3][changed] = out[changed]           # colour only where masked
    res[..., 3] = alpha                            # alpha unchanged except the window letters
    Image.fromarray(res, 'RGBA').save(art, optimize=True)
    print(side, ': SPECIMEN removed ->', art)


if __name__ == '__main__':
    sides = [a for a in sys.argv[1:] if a in ('front', 'back')] or ['front', 'back']
    arts = load()
    tpl = template(arts)
    if '--preview' in sys.argv:
        Image.fromarray(tpl).save(os.path.join(PREVIEW_DIR, 'specimen-letters.png'))
    for sd in sides:
        run(sd, arts, tpl, '--preview' in sys.argv)
