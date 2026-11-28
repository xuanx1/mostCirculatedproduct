"""
Remove PBC's specimen overprint (样币, and the small 样币禁止流通 "specimen, not for circulation")
from the ¥100 working artwork with LaMa inpainting (big-lama, TorchScript).

Where the marks are (3100 x 1540 working image):
  front  large outlined 样 (watermark area) and 币 (over 壹佰圆), and the vertical 样币禁止流通 at the right edge
  back   large outlined 样币 (right panel) and the horizontal 样币禁止流通 along the bottom left
The serial numbers (AA00000000, front, and its show-through on the back) are part of the note design
and are left alone.

The overprint is a dark teal ink, unlike anything else on the note: inside a hand-placed box around each
mark its pixels are those that are not red (G and B at least as high as R), darker than the paper, and not
the blue of the vertical serial (B not far above G). The large characters are hollow outlines whose inside
shows the print, so only the outline is masked (closed, small holes filled, grown a few px for the
anti-aliased edge). LaMa then fills each mark from the print around it. A second small pass cleans any teal
residue LaMa left.

The untouched working images (tools/upscale.py output) are kept as source/<side>-upscaled-specimen.png;
this tool reads those and writes cny-100-<side>.png. Afterwards re-run the cut-out pipeline (README).
Model: big-lama.pt (Suvorov et al., LaMa; TorchScript release), path in LAMA / env LAMA_MODEL.

Run: python tools/remove_specimen.py [front|back] [--preview]
"""
import os, sys, shutil
import numpy as np, cv2
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAMA = os.environ.get('LAMA_MODEL', r'C:/Users/65963/AppData/Local/Temp/claude/c0d258789f1d297c/94e98cd5-0543-44a8-952a-896d58182aaf/scratchpad/lama/big-lama.pt')

# boxes around each mark (x0, y0, x1, y1, px of the 3100 x 1540 working image)
MARKS = {
    'front': [(340, 730, 700, 1080),      # 样 (large, outline)
              (1310, 730, 1660, 1090),    # 币 (large, outline, over 壹佰圆)
              (2995, 420, 3100, 1250)],   # 样币禁止流通, vertical, right edge
    'back':  [(2410, 530, 3000, 780),     # 样币 (large, outline)
              (100, 1405, 1000, 1530)],   # 样币禁止流通, horizontal, bottom left
}
KEEP_OUT = {'front': [(2880, 420, 2985, 1250)]}    # the blue vertical serial: never masked

_model = None


def teal(rgb):
    f = rgb.astype(np.int32)
    R, G, B = f[..., 0], f[..., 1], f[..., 2]
    lum = (R * 299 + G * 587 + B * 114) // 1000
    tealish = (G - R > -4) & (B - R > -8) & (lum < 175)
    dark = (R < 95) & (lum < 120)                # teal laid over red print multiplies to near black
    return (tealish | dark) & (B - G < 40)


def mask_for(rgb, side):
    t = teal(rgb)
    m = np.zeros(t.shape, np.uint8)
    for x0, y0, x1, y1 in MARKS[side]:
        m[y0:y1, x0:x1] = t[y0:y1, x0:x1] * 255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)        # strokes are big blobs; specks are print
    big = np.isin(lab, 1 + np.nonzero(st[1:, cv2.CC_STAT_AREA] > 60)[0]).astype(np.uint8) * 255
    # small pieces (dots of 流, 禁, 通 in the small text) count only right beside a stroke found
    near = cv2.dilate(big, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (61, 61))) > 0
    small = np.isin(lab, 1 + np.nonzero(st[1:, cv2.CC_STAT_AREA] > 6)[0]) & near
    m = (big > 0) | small
    m = cv2.dilate(m.astype(np.uint8) * 255, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    ff = m.copy(); cv2.floodFill(ff, np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8), (0, 0), 255)
    n, lab, st, _ = cv2.connectedComponentsWithStats((~ff) & 255, 8)
    m[np.isin(lab, 1 + np.nonzero(st[1:, cv2.CC_STAT_AREA] < 120)[0])] = 255   # pinholes in strokes
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    for x0, y0, x1, y1 in KEEP_OUT.get(side, []):
        m[y0:y1, x0:x1] = 0
    return m


def lama(rgb, m, pad=128):
    """Inpaint mask m (uint8, 255 = fill) in rgb, one crop around the mask's bounding box."""
    import torch
    global _model
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    if _model is None:
        _model = torch.jit.load(LAMA, map_location=dev).eval()
    ys, xs = np.nonzero(m)
    if not len(ys):
        return rgb
    y0, y1 = max(0, ys.min() - pad), min(rgb.shape[0], ys.max() + pad)
    x0, x1 = max(0, xs.min() - pad), min(rgb.shape[1], xs.max() + pad)
    crop, mc = rgb[y0:y1, x0:x1], m[y0:y1, x0:x1]
    h, w = crop.shape[:2]; H, W = (h + 7) // 8 * 8, (w + 7) // 8 * 8
    im = np.pad(crop, ((0, H - h), (0, W - w), (0, 0)), mode='reflect')
    mk = np.pad(mc, ((0, H - h), (0, W - w)))
    t = torch.from_numpy(np.ascontiguousarray(im)).permute(2, 0, 1)[None].float().div(255).to(dev)
    tm = torch.from_numpy((mk > 127).astype(np.float32))[None, None].to(dev)
    with torch.no_grad():
        out = _model(t, tm)[0].permute(1, 2, 0).clamp(0, 1).mul(255).byte().cpu().numpy()[:h, :w]
    res = rgb.copy()
    a = np.clip(cv2.GaussianBlur(mc.astype(np.float32) / 255, (0, 0), 1.0) * 1.5, 0, 1)[..., None]
    res[y0:y1, x0:x1] = (crop * (1 - a) + out * a).astype(np.uint8)
    return res


def lama2x(rgb, m, pad=128):
    """LaMa on a 2x (Lanczos) enlargement of the crop around the mask, brought back down: on the fine
    engraving under 币 the fill keeps the hatching's contrast better than at 1x."""
    ys, xs = np.nonzero(m)
    if not len(ys):
        return rgb
    y0, y1 = max(0, ys.min() - pad), min(rgb.shape[0], ys.max() + pad)
    x0, x1 = max(0, xs.min() - pad), min(rgb.shape[1], xs.max() + pad)
    crop, mc = rgb[y0:y1, x0:x1], m[y0:y1, x0:x1]
    h, w = crop.shape[:2]
    big = cv2.resize(crop, (w * 2, h * 2), interpolation=cv2.INTER_LANCZOS4)
    bm = cv2.resize(mc, (w * 2, h * 2), interpolation=cv2.INTER_NEAREST)
    out = lama(big, bm, pad=2 * pad)
    small = cv2.resize(out, (w, h), interpolation=cv2.INTER_AREA)
    res = rgb.copy()
    a = np.clip(cv2.GaussianBlur(mc.astype(np.float32) / 255, (0, 0), 1.0) * 1.5, 0, 1)[..., None]
    res[y0:y1, x0:x1] = (crop * (1 - a) + small * a).astype(np.uint8)
    return res


def per_box(rgb, m, side):
    """LaMa once per mark box, so each crop stays small and local."""
    out = rgb
    for i, (x0, y0, x1, y1) in enumerate(MARKS[side]):
        mb = np.zeros_like(m); mb[y0:y1, x0:x1] = m[y0:y1, x0:x1]
        out = (lama2x if i in UPSCALE.get(side, []) else lama)(out, mb)
    return out


TIPS = {'back': [(2505, 640, 36)]}   # (cx, cy, r): a faint grey ring LaMa invented beside 样 (back), re-filled
TINT = {'back': [0]}          # boxes (index in MARKS) where LaMa drew the pink line pattern a little grey
PAPER_EDGE = {'front': [2]}   # boxes where the mark sits on blank paper right beside a pattern edge
MESH = {'front': [1], 'back': [0, 1]}   # boxes where LaMa's fill has whiter gaps than the print around it
UPSCALE = {'front': [1]}      # boxes inpainted at 2x: on fine engraving LaMa's fill is sharper there


def finish(out, m, side):
    """Two clean-ups LaMa needs here.
    1. Blank paper (the watermark area, the right margin): LaMa leaves a faint speckle in the shape of the
       letters; where the print around a masked pixel is all paper, the pixel is set to that paper tone.
    2. TINT boxes (one-colour line pattern): masked pixels are re-coloured to the pattern's own pink at
       their own darkness, so redrawn lines do not read greyer than the lines beside them."""
    f = out.astype(np.float32)
    mk = (m > 0).astype(np.float32)
    lum = f @ np.array([.299, .587, .114], np.float32)
    outside = 1 - mk
    sig = 10
    den = cv2.GaussianBlur(outside, (0, 0), sig) + 1e-4
    local = cv2.GaussianBlur(f * outside[..., None], (0, 0), sig) / den[..., None]
    paperish = cv2.GaussianBlur(outside * (lum >= 232), (0, 0), sig) / den
    # the letters' JPEG blocks reach ~16 px past the ink: on blank paper the whole neighbourhood is reset
    zone = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (33, 33))) > 0
    flat = zone & (paperish > 0.95) & (local @ np.array([.299, .587, .114], np.float32) >= 236) & (den > 0.05)
    flat &= (mk > 0) | (lum >= 226)                # never a real (darker) print pixel outside the mask
    # paper tone: the modal paper colour beside the letters (per box), or where the paper itself is tinted
    # (the greenish band at the top of the right margin) the local mean of the clean paper outside the zone
    R, G = f[..., 0], f[..., 1]
    clean = (~zone & (lum >= 226) & (R - G < 12)).astype(np.float32)
    dz = cv2.GaussianBlur(clean, (0, 0), 25) + 1e-4
    tone = cv2.GaussianBlur(f * clean[..., None], (0, 0), 25) / dz[..., None]
    far = cv2.GaussianBlur(f * clean[..., None], (0, 0), 60) / (cv2.GaussianBlur(clean, (0, 0), 60) + 1e-4)[..., None]
    tone[dz < 0.05] = far[dz < 0.05]                 # no clean paper within ~25 px: a wider look
    for i, (x0, y0, x1, y1) in enumerate(MARKS[side]):
        ring = zone[y0:y1, x0:x1] & (m[y0:y1, x0:x1] == 0)
        px = out[y0:y1, x0:x1][ring & (lum[y0:y1, x0:x1] >= 232)]
        if len(px):
            vals, cnt = np.unique(px.reshape(-1, 3), axis=0, return_counts=True)
            mode = vals[cnt.argmax()].astype(np.float32)
            t = tone[y0:y1, x0:x1]
            close = np.abs(t - mode).max(-1) <= 2
            t[close] = mode
        if i in PAPER_EDGE.get(side, []):     # blank paper right beside a pink pattern: every pixel in the
            zb = zone[y0:y1, x0:x1]           # zone that is not pink ink is paper
            fb = f[y0:y1, x0:x1]
            flat[y0:y1, x0:x1] |= zb & (fb[..., 0] - fb[..., 1] < 12) & (fb[..., 0] >= 200)
    soft = flat.astype(np.float32)
    f = f * (1 - soft[..., None]) + tone * soft[..., None]
    for i in PAPER_EDGE.get(side, []):   # grey specks LaMa left on the pattern edge: re-coloured to its pink
        x0, y0, x1, y1 = MARKS[side][i]
        bf = f[y0:y1, x0:x1]; bl = bf @ np.array([.299, .587, .114], np.float32)
        zb = zone[y0:y1, x0:x1]
        rope = ~zb & (bl < 220) & (bf[..., 0] - bf[..., 1] > 50)
        D = np.median((248 - bf[rope]) / (248 - bl[rope])[:, None], 0)
        grey = zb & (bl < 232) & (bf[..., 0] - bf[..., 1] < 45)
        bf[grey] = np.clip(248 - D * (248 - bl)[..., None], 0, 255)[grey]
        print(side, 'edge box', i, 'grey px re-coloured', int(grey.sum()))
    for i in TINT.get(side, []):
        x0, y0, x1, y1 = MARKS[side][i]
        bf, bl = f[y0:y1, x0:x1], lum[y0:y1, x0:x1]
        bm, paper = mk[y0:y1, x0:x1] > 0, np.float32([248, 248, 248])
        pink = lambda a: a[..., 2] > a[..., 1] - 5                     # not the orange dots
        line = (~bm) & (bl < 230) & pink(bf)
        D = np.median((paper - bf[line]) / (248 - bl[line])[:, None], 0)
        # each masked pixel keeps its own darkness, in the pattern's pink; where LaMa left a grey smudge
        # (a grey film adds the same to every channel, so R - G still measures the pink under it) the
        # pixel is much darker than its pink accounts for, and only the pink part is kept
        sel = bm & (bl < 246) & pink(bf)
        d_lum = 248 - bl
        d_pink = np.clip((bf[..., 0] - bf[..., 1]) / (D[1] - D[0]), 0, 248)
        smudge = cv2.GaussianBlur(((d_lum - d_pink) > 5).astype(np.float32) * bm, (0, 0), 4) > 0.3
        d = np.where(smudge & bm, np.minimum(d_lum, d_pink + 1), d_lum)[..., None]
        bf[sel] = np.clip(paper - D * d, 0, 255)[sel]
        print(side, 'tint box', i, 'smudge px', int((smudge & bm).sum()))
        print(side, 'tint box', i, 'line colour per unit darkness', np.round(D, 2))
    for i in MESH.get(side, []):
        # LaMa draws the fine purple-pink mesh right of 圆 with whiter gaps than the real mesh, which shows
        # as a pale outline of 币, most of all in the offset layer (built from that light envelope). Where
        # the print round a masked pixel is that mesh, the pixel is scaled per channel so its envelope
        # matches the mesh's around it.
        x0, y0, x1, y1 = MARKS[side][i]
        pad = 60
        X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), min(f.shape[1], x1 + pad), min(f.shape[0], y1 + pad)
        bf = f[Y0:Y1, X0:X1]; band = (mk[Y0:Y1, X0:X1] > 0)
        sm = cv2.GaussianBlur(bf, (0, 0), 3)
        ring = (~(cv2.dilate(band.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0)).astype(np.float32)
        lo = lambda v, w, sg: cv2.GaussianBlur(v * w[..., None], (0, 0), sg) / (cv2.GaussianBlur(w, (0, 0), sg)[..., None] + 1e-4)
        # the light envelope of the print (closing: the tint between the lines), inside vs around
        u8 = np.clip(bf, 0, 255).astype(np.uint8)
        k1, k2 = (cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (d, d)) for d in (15, 23))
        env = cv2.merge([cv2.morphologyEx(cv2.morphologyEx(u8[..., c], cv2.MORPH_CLOSE, k1), cv2.MORPH_CLOSE, k2)
                         for c in range(3)]).astype(np.float32)
        classes = {'line pattern': np.ones(band.shape, bool)} if side == 'back' else {'purple mesh': (sm[..., 2] - sm[..., 1] > 4) & (sm[..., 0] - sm[..., 1] < 75),
                   'orange hatch': (sm[..., 2] < sm[..., 1]) & (sm[..., 0] - sm[..., 1] < 140)}
        for name, cls in classes.items():
            frac = cv2.GaussianBlur(ring * cls, (0, 0), 10) / (cv2.GaussianBlur(ring, (0, 0), 10) + 1e-4)
            tgt = band & (frac > 0.85)
            ratio = np.clip(lo(env, ring * cls, 12) / (lo(env, tgt.astype(np.float32), 4) + 1e-3), 0.85, 1.03)
            w = np.clip(cv2.GaussianBlur(tgt.astype(np.float32), (0, 0), 2.0) * 1.5, 0, 1) * band
            bf[:] = bf * (1 - w[..., None]) + bf * ratio * w[..., None]
            print(side, 'envelope box', i, name, 'px', int(tgt.sum()), 'median ratio', np.round(np.median(ratio[tgt], 0), 3) if tgt.any() else '-')
    return np.clip(f + 0.5, 0, 255).astype(np.uint8)


def run(side, preview=False):
    work = os.path.join(ROOT, f'cny-100-{side}.png')
    keep = os.path.join(ROOT, 'source', f'{side}-upscaled-specimen.png')
    if not os.path.exists(keep):
        shutil.copyfile(work, keep)
    rgb = np.asarray(Image.open(keep).convert('RGB'))
    m = mask_for(rgb, side)
    if preview:
        ov = rgb.copy(); ov[m > 0] = (0.4 * ov[m > 0] + [0, 150, 0]).astype(np.uint8)
        Image.fromarray(ov).save(os.path.join(ROOT, 'source', f'{side}-specimen-mask-preview.png'))
        print(side, 'mask px', int((m > 0).sum())); return
    out = per_box(rgb, m, side)
    # second pass: any teal left inside the boxes (residue or a redrawn stroke)
    r = mask_for(out, side)
    print(side, 'residue px after pass 1:', int((r > 0).sum()))
    if (r > 0).sum():
        out = per_box(out, r, side)
    for cx, cy, rad in TIPS.get(side, []):
        tip = np.zeros_like(m); cv2.circle(tip, (cx, cy), rad, 255, -1)
        out = lama(out, tip, pad=160)
        m = m | tip
    out = finish(out, m | r, side)
    Image.fromarray(out).save(work, optimize=True)
    print(side, ': specimen overprint removed ->', work)


if __name__ == '__main__':
    sides = [a for a in sys.argv[1:] if a in ('front', 'back')] or ['front', 'back']
    for sd in sides:
        run(sd, '--preview' in sys.argv)
