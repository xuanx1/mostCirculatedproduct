"""
AI isolation of the large printed subjects with Segment Anything (SAM, ViT-L) on the working artwork:
the Bank of China Tower and the bauhinia flower on the front, and the two heads of "A Smart
Metropolis" on the back.

SAM is prompted with each subject's box and a few positive (and negative) points, returns three
candidate masks, and the best-scoring one that stays inside the box is kept (or a fixed candidate,
see TARGETS). The mask is cleaned (small parts dropped, holes filled, ~1 px anti-aliased edge) and
applied to the original pixels, so nothing is redrawn.

Writes assets/layers/front-tower.png, front-flower.png, back-smart.png (+ feature-crops/),
source/linework-front.png / linework-back.png (the subjects' own darker line-work, for the page's
colour flow) and updates assets/boxes.js. SAM's raw masks are cached in source/sam/ (re-cleaning
needs no GPU). Hand-cleaned files in assets/overrides/ win.

Run: python tools/sam_isolate.py [--rerun]   (needs the facebook/sam-vit-large weights; GPU if available)
"""
import os, sys
import numpy as np
import cv2
import torch
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

# id -> (side, box x0,y0,x1,y1 in note units, positive points, negative points) in note units
TARGETS = {
    'tower':  ('front', (158, 40, 328, 320), [(215, 250), (255, 170), (200, 300), (300, 300), (230, 120)],
               [(130, 150), (400, 200)]),
    'flower': ('front', (255, 55, 425, 250), [(330, 110), (370, 160), (320, 190), (345, 225), (395, 160)],
               [(290, 240), (420, 90)]),
    'smart':  ('back',  (225, 18, 595, 292), [(330, 130), (300, 220), (420, 250), (520, 190), (380, 70)],
               [(150, 160), (640, 160)]),
}
RAW = os.path.join(C.ROOT, 'source', 'sam')


def load_model():
    from transformers import SamModel, SamProcessor
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = SamModel.from_pretrained('facebook/sam-vit-large').to(dev).eval()
    proc = SamProcessor.from_pretrained('facebook/sam-vit-large')
    return model, proc, dev


def segment(model, proc, dev, img, box, points, labels):
    inputs = proc(img, input_boxes=[[list(box)]], input_points=[[points]], input_labels=[[labels]],
                  return_tensors='pt').to(dev)
    with torch.no_grad():
        out = model(**inputs, multimask_output=True)
    masks = proc.image_processor.post_process_masks(
        out.pred_masks.cpu(), inputs['original_sizes'].cpu(), inputs['reshaped_input_sizes'].cpu())[0][0]
    return masks.numpy(), out.iou_scores.cpu()[0, 0].numpy()


def linework(rgb, alpha):
    """the subject's own darker strokes (black top-hat on lightness), inside its mask"""
    L = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
    th = cv2.morphologyEx(L, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))) - L
    return np.clip((th - 6) / 18, 0, 1) * alpha


def run_sam():
    model, proc, dev = load_model()
    os.makedirs(RAW, exist_ok=True)
    for fid, (side, bu, pos, neg) in TARGETS.items():
        full = C.load(side)
        sx, sy = C.scale(full)
        box = [bu[0], bu[1], bu[2] - bu[0], bu[3] - bu[1]]
        x0, y0, x1, y1 = C.px(full, box)
        R = full[y0:y1, x0:x1]
        to_px = lambda X, Y: [(X - bu[0]) * sx, (Y - bu[1]) * sy]
        masks, scores = segment(model, proc, dev, Image.fromarray(R.astype(np.uint8)),
                                to_px(bu[0] + 1, bu[1] + 1) + to_px(bu[2] - 1, bu[3] - 1),
                                [to_px(*p) for p in pos + neg], [1] * len(pos) + [0] * len(neg))
        print(fid, 'scores', np.round(scores, 3))
        for k, m in enumerate(masks):
            Image.fromarray(m.astype(np.uint8) * 255).save(os.path.join(RAW, f'{fid}-{k}.png'))


# which SAM candidate is kept for each subject (chosen by looking at all three: source/sam/<id>-<k>.png)
PICK = {'tower': 1, 'flower': 1, 'smart': 0}
# below the flower SAM also takes in the pale faceted 'diamond' shape of the background (straight ruled
# edges, not petals): it is cut away along this polygon (note units) with a soft fade, not a hard cut
# above the neck at the far right SAM also takes a strip of the green blocks: cut away
SMART_CUT = [(571, 14), (600, 14), (600, 99), (571, 99)]
FLOWER_CUT = [(268, 162), (312, 166), (327, 175), (335, 195), (340, 230), (346, 252), (268, 252)]


def _poly(shape, pts):
    im = Image.new('L', (shape[1], shape[0]), 0)
    ImageDraw.Draw(im).polygon(pts, fill=255)
    return im


def main():
    C.load_boxes()
    if '--rerun' in sys.argv or not os.path.exists(os.path.join(RAW, 'tower-0.png')):
        run_sam()
    lw = {}
    for fid, (side, bu, pos, neg) in TARGETS.items():
        full = C.load(side)
        box = [bu[0], bu[1], bu[2] - bu[0], bu[3] - bu[1]]
        x0, y0, x1, y1 = C.px(full, box)
        R = full[y0:y1, x0:x1]
        m = np.asarray(Image.open(os.path.join(RAW, f'{fid}-{PICK[fid]}.png'))) > 127
        # no slivers or crumbs along the edge: open, keep the main body, smooth the outline
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))) > 0
        m = C.keep_components(m, min_area=4000, keep=lambda st, c: st[cv2.CC_STAT_AREA] > 0.05 * m.sum())
        m = C.fill_holes(m)
        m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 2) > 0.5
        sx, sy = C.scale(full)
        poly = lambda pts: np.asarray(_poly(m.shape, [((x - bu[0]) * sx, (y - bu[1]) * sy) for x, y in pts]), np.float32) / 255
        if fid == 'smart':
            m &= poly(SMART_CUT) < 0.5
        a = C.soft_edge(m, 1.0)
        if fid == 'flower':
            cut = cv2.GaussianBlur(poly(FLOWER_CUT), (0, 0), 1.6 * sx)
            a = a * np.clip(1 - cut * 2, 0, 1)
        C.save_piece(side, fid, full, box, C.defringe(R, a), a)
        if side not in lw:
            lw[side] = np.zeros(full.shape[:2], np.float32)
        lw[side][y0:y1, x0:x1] = np.maximum(lw[side][y0:y1, x0:x1], linework(R, a))
    for side, L in lw.items():
        Image.fromarray((L * 255).astype(np.uint8)).resize((1440, 640), Image.LANCZOS) \
            .save(os.path.join(C.ROOT, 'source', f'linework-{side}.png'), optimize=True)
    C.write_boxes()


if __name__ == '__main__':
    if '--raw' in sys.argv:
        run_sam()
    else:
        main()
