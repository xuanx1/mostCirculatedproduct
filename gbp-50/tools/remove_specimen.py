"""
Remove the SPECIMEN overprint from the levelled artwork with LaMa inpainting (big-lama, TorchScript).

The overprint is translucent dark grey lettering on a diagonal: inside a hand-placed band around it,
its pixels are both darker and greyer (lower chroma) than the print around them. That mask is closed
into solid letters, grown by a few pixels, and LaMa fills it from the surrounding print.

The untouched levelled image is kept as source/<side>-levelled-specimen.png (first run), so this can be
re-run. Then run tools/cutouts.py to rebuild the page artwork and every cut-out.
Model: big-lama.pt (Suvorov et al., LaMa; TorchScript release of simple-lama-inpainting), path in LAMA.

Run: python tools/remove_specimen.py [--preview]
"""
import os, sys, shutil
import numpy as np, cv2
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAMA = os.environ.get('LAMA_MODEL', r'C:/Users/65963/AppData/Local/Temp/claude/c0d258789f1d297c/94e98cd5-0543-44a8-952a-896d58182aaf/scratchpad/lama/big-lama.pt')
# band around the overprint, in px of the 3072 x 1620 levelled image
BANDS = {'front': [(1040, 1150), (1225, 1345), (2119, 458), (1967, 300)],
         'back':  [(986, 1188), (1165, 1372), (2112, 451), (1933, 266)]}   # along the text's centre line
DARK, GREY = 160, 38          # L below, chroma below
KEEP_OUT = {'front': [(1080, 1232, 1430, 1350)]}     # the printed 'Fifty' under the S: never masked
TEXT_ROWS = {'front': [(1690, 368, 1990, 408)]}      # the promise line under the N: mask only grey, not the black text


def mask_for(rgb, band, side='front'):
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    L, C = lab[..., 0], np.hypot(lab[..., 1] - 128, lab[..., 2] - 128)
    zone = np.zeros(L.shape, np.uint8); cv2.fillPoly(zone, [np.array(band, np.int32)], 255)
    m = ((L < DARK) & (C < GREY) & (zone > 0)).astype(np.uint8) * 255
    for x0, y0, x1, y1 in KEEP_OUT.get(side, []):
        m[y0:y1, x0:x1] = 0
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17)))
    n, lab_, st, _ = cv2.connectedComponentsWithStats(m, 8)       # letters are big blobs; specks are print
    keep = np.isin(lab_, 1 + np.nonzero(st[1:, cv2.CC_STAT_AREA] > 600)[0]).astype(np.uint8) * 255
    keep = cv2.dilate(keep, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    for x0, y0, x1, y1 in KEEP_OUT.get(side, []):
        keep[y0:y1, x0:x1] = 0
    return keep


def lama(rgb, m):
    import torch
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = torch.jit.load(LAMA, map_location=dev).eval()
    ys, xs = np.nonzero(m)
    pad = 96
    y0, y1 = max(0, ys.min() - pad), min(rgb.shape[0], ys.max() + pad)
    x0, x1 = max(0, xs.min() - pad), min(rgb.shape[1], xs.max() + pad)
    crop, mc = rgb[y0:y1, x0:x1], m[y0:y1, x0:x1]
    h, w = crop.shape[:2]; H, W = (h + 7) // 8 * 8, (w + 7) // 8 * 8
    im = np.pad(crop, ((0, H - h), (0, W - w), (0, 0)), mode='reflect')
    mk = np.pad(mc, ((0, H - h), (0, W - w)))
    t = torch.from_numpy(im).permute(2, 0, 1)[None].float().div(255).to(dev)
    tm = torch.from_numpy((mk > 127).astype(np.float32))[None, None].to(dev)
    with torch.no_grad():
        out = model(t, tm)[0].permute(1, 2, 0).clamp(0, 1).mul(255).byte().cpu().numpy()[:h, :w]
    res = rgb.copy()
    a = (cv2.GaussianBlur(mc.astype(np.float32) / 255, (0, 0), 1.2))[..., None]
    res[y0:y1, x0:x1] = (crop * (1 - a) + out * a).astype(np.uint8)
    return res


def main():
    preview = '--preview' in sys.argv
    for side, band in BANDS.items():
        lev = os.path.join(ROOT, 'source', f'{side}-levelled.png')
        keep = os.path.join(ROOT, 'source', f'{side}-levelled-specimen.png')
        if not os.path.exists(keep):
            shutil.copyfile(lev, keep)
        rgb = np.asarray(Image.open(keep).convert('RGB'))
        m = mask_for(rgb, band, side)
        if preview:
            ov = rgb.copy(); ov[m > 0] = (0.5 * ov[m > 0] + [0, 127, 255]).astype(np.uint8)
            Image.fromarray(ov).save(os.path.join(ROOT, 'source', f'{side}-specimen-mask-preview.png'))
            print(side, 'mask px', int((m > 0).sum())); continue
        Image.fromarray(lama(rgb, m)).save(lev, optimize=True)
        print(side, 'SPECIMEN removed ->', lev)


if __name__ == '__main__':
    main()
