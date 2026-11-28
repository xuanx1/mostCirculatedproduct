"""
Engraved vignettes cut along their own line-work (for shapes Segment Anything confuses with the
tinted background around them):
  - back-station:   Tokyo Station with its trees and the curved border scroll that frames it;
  - front-cartouche: the latent-image cartouche at the bottom centre of the front.
Method: the engraved lines are far darker than the offset tints and guilloche around them, so the
line-work is found by darkness, closed into one solid silhouette, holes
filled, only the piece(s) at the seed points kept, smoothed, and an ~1 px anti-aliased edge applied to
the original pixels. Writes assets/layers/<side>-<id>.png and -cut.png on the boxes.js frame, and
feature-crops/<side>/<id>.png.     Run: python tools/engrave_cut.py
"""
import os, sys
import numpy as np, cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import extract_features as EF  # noqa: E402

ROOT = EF.ROOT
LAYERS = os.path.join(ROOT, 'assets', 'layers')
OVR = os.path.join(ROOT, 'assets', 'overrides')
# id: side, search box (x0, y0, x1, y1), seed points, line darkness (L* below), closing radius, opening radius (note units),
#     exclusions: rectangles (x0, y0, x1, y1) or polygons [(x, y), ...] (note units)
TARGETS = {
    'station':   ('back',  (8, 22, 300, 286), [(150, 150), (60, 200), (250, 240), (115, 70), (40, 40)], 150, 2.6, 1.4,
                  [(110, 24, 240, 60), (0, 266, 140, 320)]),          # the NIPPON wordmark; the 10000 YEN below
    'cartouche': ('front', (284, 250, 434, 310), [(360, 280)], 135, 1.6, 2.2,
                  [[(0, 284), (291, 284), (298, 296), (304, 320), (0, 320)],     # the scrolls beside its lower corners
                   [(720, 284), (428, 284), (421, 296), (415, 320), (720, 320)]]),
}


def unmask(m, excl, x0, y0, sx, sy):
    for e in excl:
        if isinstance(e, list):
            cv2.fillPoly(m, [np.array([((x - x0) * sx, (y - y0) * sy) for x, y in e], np.int32)], 0)
        else:
            ex0, ey0, ex1, ey1 = e
            m[max(0, int((ey0 - y0) * sy)):max(0, int((ey1 - y0) * sy)), max(0, int((ex0 - x0) * sx)):max(0, int((ex1 - x0) * sx))] = 0


def cut(fid):
    side, (x0, y0, x1, y1), seeds, contrast, close_u, open_u, excl = TARGETS[fid]
    im = Image.open(os.path.join(ROOT, EF.SRC[side])).convert('RGB')
    W, H = im.size; sx, sy = W / 720, H / 320; s = (sx + sy) / 2
    box = (int(x0 * sx), int(y0 * sy), int(x1 * sx), int(y1 * sy))
    rgb = np.asarray(im.crop(box))
    L = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
    disk = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(r * s) * 2 + 1,) * 2)
    lines = L < contrast                                                 # engraved lines: far darker than the tints
    m = lines.astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, disk(close_u))
    unmask(m, excl, x0, y0, sx, sy)
    ff = cv2.copyMakeBorder(m, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    cv2.floodFill(ff, np.zeros((ff.shape[0] + 2, ff.shape[1] + 2), np.uint8), (0, 0), 255)
    m |= cv2.bitwise_not(ff[1:-1, 1:-1])                                 # fill holes
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(open_u))               # drop hairline attachments
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros_like(m)
    for (px, py) in seeds:
        k = lab[int((py - y0) * sy), int((px - x0) * sx)]
        if k:
            keep[lab == k] = 255
    # fine parts the opening took off (a spire, a finial) come back if they touch what is kept
    fine = cv2.morphologyEx(lines.astype(np.uint8) * 255, cv2.MORPH_CLOSE, disk(0.5))
    unmask(fine, excl, x0, y0, sx, sy)
    n2, lab2, _, _ = cv2.connectedComponentsWithStats(fine, 8)
    touch = np.unique(lab2[(cv2.dilate(keep, disk(0.3)) > 0) & (fine > 0)])
    grown = np.isin(lab2, touch[touch > 0]) & (cv2.dilate(keep, disk(12)) > 0)
    keep = np.maximum(keep, (grown * 255).astype(np.uint8))
    keep = ((cv2.GaussianBlur(keep.astype(np.float32), (0, 0), 0.4 * s) > 127) * 255).astype(np.uint8)   # smooth outline
    a = cv2.GaussianBlur(keep.astype(np.float32) / 255, (0, 0), 0.8)
    a = np.clip((a - 0.5) * 2.2 + 0.5, 0, 1)
    out = Image.fromarray(np.dstack([rgb, (a * 255).astype(np.uint8)]), 'RGBA')
    bb = out.getchannel('A').point(lambda v: 255 if v > 6 else 0).getbbox()
    out.crop((max(0, bb[0] - 12), max(0, bb[1] - 12), min(out.width, bb[2] + 12), min(out.height, bb[3] + 12))) \
       .save(os.path.join(EF.OUT, side, f'{fid}.png'), optimize=True)
    shape, g = next((r[3], r[4]) for r in EF.REGIONS if (r[1], r[0]) == (side, fid))
    (px0, py0, px1, py1), _ = EF.bbox(shape, g, EF.PAD)
    frame = Image.new('RGBA', (int(round((px1 - px0) * sx)), int(round((py1 - py0) * sy))), (0, 0, 0, 0))
    frame.alpha_composite(out, (int(round((x0 - px0) * sx)), int(round((y0 - py0) * sy))))
    k = 1440 / W * 1.5
    frame = frame.resize((round(frame.width * k), round(frame.height * k)), Image.LANCZOS)
    for name in (f'{side}-{fid}-cut.png', f'{side}-{fid}.png'):
        if not os.path.exists(os.path.join(OVR, name)):
            frame.save(os.path.join(LAYERS, name), optimize=True)
    print(f'{side}-{fid}: pieces kept {len(seeds)}, bbox px {bb}')


def main():
    for fid in TARGETS:
        cut(fid)


if __name__ == '__main__':
    main()
