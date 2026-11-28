"""
Remove the SPECIMEN overprint from both sides of the £50 with LaMa inpainting.

Per side: a letter-shaped mask (tools/unblend_specimen.letters: dark, grey pixels inside a band along the
word), grown toward the overprint's soft upper-left shadow; real print the word crosses is protected
(KEEP_OUT boxes, and black text inside TEXT_ROWS); LaMa fills it from the print around it
(tools/remove_specimen.lama). A second pass cleans any small TIPS left over, and a final step lifts
any flat grey left there by its ratio to the clean print beside it.

Reads source/<side>-levelled-specimen.png (made on first run from the untouched levelled image),
writes source/<side>-levelled.png.   Run: python tools/remove_specimen_run.py [front|back] [--preview]
then python tools/cutouts.py
"""
import os, sys, shutil
import numpy as np, cv2
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import remove_specimen as RS, unblend_specimen as UB

def letters_dark(rgb, side):
    """Overprint letters as pixels that are grey AND darker than their own neighbourhood (a 151 px median):
    works where the print under the word is itself dark grey (the machine photo on the back), which a
    plain dark-and-grey test would fill solid. A looser second pass, only right beside the letters found,
    picks up strokes over dark hair where the overprint darkens less."""
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    L, C = lab[..., 0], np.hypot(lab[..., 1] - 128, lab[..., 2] - 128)
    zone = np.zeros(L.shape, np.uint8); cv2.fillPoly(zone, [np.array(RS.BANDS[side], np.int32)], 255)
    bgL = cv2.medianBlur(L.astype(np.uint8), 151).astype(np.float32)
    m = ((C < 36) & (L < bgL - 18) & (L < 170) & (zone > 0)).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    n, lab_, st, _ = cv2.connectedComponentsWithStats(m, 8)
    m = np.isin(lab_, 1 + np.nonzero(st[1:, cv2.CC_STAT_AREA] > 2500)[0]).astype(np.uint8) * 255
    near = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))) > 0
    m2 = ((C < 40) & (L < bgL - 5) & (L < 175) & near & (zone > 0)).astype(np.uint8) * 255
    m = cv2.morphologyEx(m | m2, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21)))
    ff = m.copy(); cv2.floodFill(ff, np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8), (0, 0), 255)
    n, lab_, st, _ = cv2.connectedComponentsWithStats((~ff) & 255, 8)
    m[np.isin(lab_, 1 + np.nonzero(st[1:, cv2.CC_STAT_AREA] < 6000)[0])] = 255     # gaps inside strokes
    return m


LETTERS = {'back': letters_dark}       # front: UB.letters (plain dark-and-grey test)
TIPS = {'front': [[(1895, 345), (1945, 395), (1905, 430), (1850, 380)]],   # the N's tip over '…NDS'
        'back':  [[(1600, 560), (1795, 560), (1795, 745), (1600, 745)]]}   # stroke LaMa redrew on the cheek
PROTECT_TEXT = {'front'}                 # sides whose tip passes sit on black text that must stay


def run(side, preview=False):
    lev = os.path.join(RS.ROOT, 'source', f'{side}-levelled.png')
    keep = os.path.join(RS.ROOT, 'source', f'{side}-levelled-specimen.png')
    if not os.path.exists(keep):
        shutil.copyfile(lev, keep)
    rgb = np.asarray(Image.open(keep).convert('RGB'))
    m = LETTERS.get(side, UB.letters)(rgb, side)
    sh = cv2.warpAffine(m, np.float32([[1, 0, -10], [0, 1, -10]]), (m.shape[1], m.shape[0]))
    m = cv2.dilate(m | sh, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))
    for x0, y0, x1, y1 in RS.KEEP_OUT.get(side, []):
        m[y0:y1, x0:x1] = 0
    L = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)[..., 0]
    for x0, y0, x1, y1 in RS.TEXT_ROWS.get(side, []):
        ink = cv2.dilate((L[y0:y1, x0:x1] < 70).astype(np.uint8) * 255, np.ones((3, 3), np.uint8))
        m[y0:y1, x0:x1][ink > 0] = 0
    if preview:
        ov = rgb.copy(); ov[m > 0] = (0.4 * ov[m > 0] + [0, 150, 0]).astype(np.uint8)
        Image.fromarray(ov).save(os.path.join(RS.ROOT, 'source', f'{side}-specimen-mask-preview.png'))
        print(side, 'mask px', int((m > 0).sum())); return
    out = RS.lama(rgb, m)
    for poly in TIPS.get(side, []):
        tip = np.zeros_like(m); cv2.fillPoly(tip, [np.array(poly, np.int32)], 255)
        if side in PROTECT_TEXT:
            tip = cv2.dilate(tip, np.ones((7, 7), np.uint8))
            tip[cv2.dilate((L < 70).astype(np.uint8) * 255, np.ones((3, 3), np.uint8)) > 0] = 0
        else:   # only the dark grey residue inside the box
            lab_t = cv2.cvtColor(out, cv2.COLOR_RGB2LAB).astype(np.float32)
            resid = (lab_t[..., 0] < 125) & (np.hypot(lab_t[..., 1] - 128, lab_t[..., 2] - 128) < 30)
            tip = cv2.dilate(((tip > 0) & resid).astype(np.uint8) * 255, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17)))
        out = RS.lama(out, tip)
        # any flat grey still left there: lift it by its ratio to the clean print beside it
        f = out.astype(np.float32); lab_o = cv2.cvtColor(out, cv2.COLOR_RGB2LAB).astype(np.float32)
        Lo = lab_o[..., 0]
        ring = (cv2.dilate(tip, np.ones((25, 25), np.uint8)) > 0) & ~(tip > 0) & (Lo >= 70)
        grey = (tip > 0) & (Lo >= 70) & (Lo < 170) & (np.hypot(lab_o[..., 1] - 128, lab_o[..., 2] - 128) < 18)
        if grey.sum() > 50 and ring.sum() > 50:
            g = np.median(f[grey], 0) / np.median(f[ring], 0)
            soft = cv2.GaussianBlur(grey.astype(np.float32), (0, 0), 2.0)[..., None]
            out = (f * (1 - soft) + np.clip(f / np.maximum(g, 0.2), 0, 255) * soft).astype(np.uint8)
    Image.fromarray(out).save(lev, optimize=True)
    print(side, ': SPECIMEN removed')


if __name__ == '__main__':
    sides = [a for a in sys.argv[1:] if a in ('front', 'back')] or ['front', 'back']
    for sd in sides:
        run(sd, '--preview' in sys.argv)
