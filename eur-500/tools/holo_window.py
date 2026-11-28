"""
The hologram patch's second image: the window / doorway.

The specimen scan shows the patch at one angle only (the value, 500). The other image comes from a
photograph of a genuine EUR 500 in a museum case, taken at the angle where the hologram shows the
window (Wikimedia Commons, "500 euro banknote type 2002 hologram building.jpg", by Copyleft,
CC BY-SA 4.0; source/holo-building-commons.jpg):
  1. the photo is rectified onto the note's own geometry from its four corners (perspective warp),
  2. the patch is cut where both the scan's hologram silhouette (assets/layers/front-hologram-cut.png)
     and the photo's own foil outline agree, so no paper from either image shows.
Writes assets/layers/holo-window.png (same frame as front-hologram). Run after tools/cutouts.py.
"""
import json, os, re
import numpy as np
import cv2
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTO = os.path.join(ROOT, 'source', 'holo-building-commons.jpg')
CORNERS = [(272, 536), (4409, 428), (4426, 2587), (302, 2615)]     # TL, TR, BR, BL in the photo (px)


def main():
    scan = np.asarray(Image.open(os.path.join(ROOT, 'eur-500-front.png')).convert('RGB'))
    H, W = scan.shape[:2]
    photo = np.asarray(Image.open(PHOTO).convert('RGB'))
    M = cv2.getPerspectiveTransform(np.float32(CORNERS), np.float32([(0, 0), (W, 0), (W, H), (0, H)]))
    warped = cv2.warpPerspective(photo, M, (W, H), flags=cv2.INTER_CUBIC)
    # the rectified photo lies within a few px of the scan (ECC on the whole note was tried: the museum
    # glass and lighting pull it off by ~15 px, so the plain corner rectification is used)
    boxes = json.loads(re.search(r'const BOXES = (\{.*\});', open(os.path.join(ROOT, 'assets', 'boxes.js'), encoding='utf8').read(), re.S).group(1))
    x, y, w, h = boxes['front-hologram']
    sx, sy = W / 720, H / 320
    X0, Y0, X1, Y1 = int(round(x * sx)), int(round(y * sy)), int(round((x + w) * sx)), int(round((y + h) * sy))
    crop = warped[Y0:Y1, X0:X1]
    # the photo's own patch outline: not paper (dark foil or strong colour), one convex die-cut piece
    lab = cv2.cvtColor(crop, cv2.COLOR_RGB2LAB).astype(np.float32)
    paperL = np.percentile(lab[..., 0], 90)            # the photo is darker than the scan: relative to its paper
    m = ((lab[..., 0] < paperL - 40) | (np.hypot(lab[..., 1] - 128, lab[..., 2] - 128) > 26)).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    n, lab_, st, _ = cv2.connectedComponentsWithStats(m, 8)
    m = ((lab_ == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))) * 255).astype(np.uint8)
    hull = np.zeros_like(m)
    cv2.fillPoly(hull, [cv2.convexHull(cv2.findNonZero(m))], 255)
    hull = cv2.erode(hull, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (27, 27)))   # inside the tiny EURO 500 text round the rim
    cut = Image.open(os.path.join(ROOT, 'assets', 'layers', 'front-hologram-cut.png')).convert('RGBA')
    pa = Image.fromarray(cv2.GaussianBlur(hull, (0, 0), 1.2)).resize(cut.size, Image.LANCZOS)
    alpha = np.minimum(np.asarray(cut.getchannel('A')), np.asarray(pa))
    img = Image.fromarray(crop).resize(cut.size, Image.LANCZOS).convert('RGBA')
    img.putalpha(Image.fromarray(alpha))
    img.save(os.path.join(ROOT, 'assets', 'layers', 'holo-window.png'), optimize=True)
    print('holo-window', img.size)


if __name__ == '__main__':
    main()
