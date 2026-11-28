"""
Isolate the two large painted subjects by colour separation on the working artwork: the Standard
Chartered Bank Building and the Forum on the front, and the Central skyline on the back.

  python tools/subjects.py        (no GPU or model needed)

Both subjects are printed in the note's coral red, much redder than the peach paper, the pale
geometric cuts, the yellow logo and the green-grey haze behind them, so red minus green separates
them. (Segment Anything, tried first as for the HSBC note, returned the whole prompt box: these
subjects sit on a busy, continuous background with no clear figure-ground edge.)
  1. ink:    R - G above a threshold, inside the subject's box;
  2. shape:  closed (windows, the skyline's dot-matrix digits and the gaps between towers bridged),
             holes filled, opened, only the large body kept, outline smoothed;
  3. edge:   ~1 px anti-aliased; edge pixels take the colour of the nearest solid pixel.
Where a subject meets a printed area of the same red that is not part of it (the coral ground the
Forum stands on; the copyright line along the skyline's base) the mask is cut there with a soft
fade rather than a hard line. Original pixels only; nothing is redrawn.

Writes assets/layers/front-building.png, back-skyline.png (+ feature-crops/),
source/linework-front.png / linework-back.png (the subjects' own darker line-work, for the page's
colour flow) and updates assets/boxes.js. Hand-cleaned files in assets/overrides/ win.
"""
import os, sys
import numpy as np
import cv2
from PIL import Image
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

# id -> (side, box [x, y, w, h] in note units, R - G threshold, closing kernel px)
TARGETS = {
    'building': ('front', [186, 50, 236, 270], 75, 21),
    'skyline':  ('back',  [160, 0, 375, 320], 80, 21),
}


def linework(rgb, alpha):
    """the subject's own darker strokes (black top-hat on lightness), inside its mask"""
    L = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
    th = cv2.morphologyEx(L, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))) - L
    return np.clip((th - 6) / 18, 0, 1) * alpha


def main():
    C.load_boxes()
    for fid, (side, box, T, K) in TARGETS.items():
        full = C.load(side)
        sx, sy = C.scale(full)
        x0, y0, x1, y1 = C.px(full, box)
        R = full[y0:y1, x0:x1]
        uy = box[1] + np.arange(R.shape[0]) / sy            # note units of each row / column
        ux = box[0] + np.arange(R.shape[1]) / sx
        ink = (R[..., 0] - R[..., 1]) > T
        if fid == 'skyline':                                # the copyright line where no tower is behind it
            ink &= ~((uy[:, None] > 290) & (uy[:, None] < 302) & (ux[None, :] < 398))
        m = cv2.morphologyEx(ink.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (K, K)))
        m = ndimage.binary_fill_holes(m)
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (K, K)))
        m = C.keep_components(m, min_area=20000)
        m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 3) > 0.5
        a = C.soft_edge(m, 1.0)
        if fid == 'building':                               # the Forum stands on a coral ground: fade at its foot
            a = a * (1 - C.smoothstep(295.5, 299, uy))[:, None]
        C.save_piece(side, fid, full, box, C.defringe(R, a), a)
        full_lw = np.zeros(full.shape[:2], np.float32)
        full_lw[y0:y1, x0:x1] = linework(R, a)
        Image.fromarray((full_lw * 255).astype(np.uint8)).resize((1440, 640), Image.LANCZOS) \
            .save(os.path.join(C.ROOT, 'source', f'linework-{side}.png'), optimize=True)
    C.write_boxes()


if __name__ == '__main__':
    main()
