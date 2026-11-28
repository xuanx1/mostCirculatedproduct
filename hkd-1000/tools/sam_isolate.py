"""
AI isolation of the large painted subjects with Segment Anything (SAM, ViT-L) on the working artwork:
the HSBC lion "Stitt" on the front and the "Financial Metropolis" fisheye view on the back.

SAM is prompted with each subject's box and a few positive points, returns three candidate masks,
and the best-scoring one that stays inside the box is kept. The mask is cleaned (small parts
dropped, holes filled, ~1 px anti-aliased edge) and applied to the original pixels, so nothing is
redrawn. The lion's mane (the iridescent area, HSBC) is the lion's mask minus its face, muzzle and
chest (a hand-placed polygon, note units).

Writes assets/layers/front-lion.png, front-mane.png, back-metropolis.png (+ feature-crops/),
source/linework-front.png / linework-back.png (the subjects' own darker line-work, for the
page's colour flow) and updates assets/boxes.js. Hand-cleaned files in assets/overrides/ win.

Run: python tools/sam_isolate.py   (needs the facebook/sam-vit-large weights; GPU if available)
"""
import os, sys
import numpy as np
import cv2
import torch
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

# id -> (side, box x0,y0,x1,y1 in note units, positive points in note units)
TARGETS = {
    'lion':       ('front', (160, 46, 430, 272), [(300, 150), (230, 210), (390, 170), (270, 90)]),
    'metropolis': ('back',  (262, 0, 596, 320),  [(440, 160), (340, 220), (520, 260), (400, 60)]),
}
# the face: everything right of the mane (eye, muzzle, jaw, beard) and the chest below it
FACE = [(298, 30), (440, 30), (440, 300), (300, 300), (300, 262), (338, 232), (334, 180),
        (322, 140), (304, 100)]
# the dotted red pedestal the bust stands on (not part of the lion)
PEDESTAL = [(326, 214), (440, 266), (440, 300), (322, 300)]
RAW = os.path.join(C.ROOT, 'source', 'sam')          # SAM's raw masks: re-cleaning needs no GPU


def load_model():
    from transformers import SamModel, SamProcessor
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = SamModel.from_pretrained('facebook/sam-vit-large').to(dev).eval()
    proc = SamProcessor.from_pretrained('facebook/sam-vit-large')
    return model, proc, dev


def segment(model, proc, dev, img, box, points):
    inputs = proc(img, input_boxes=[[list(box)]], input_points=[[points]] if points else None,
                  return_tensors='pt').to(dev)
    with torch.no_grad():
        out = model(**inputs, multimask_output=True)
    masks = proc.image_processor.post_process_masks(
        out.pred_masks.cpu(), inputs['original_sizes'].cpu(), inputs['reshaped_input_sizes'].cpu())[0][0]
    return masks.numpy(), out.iou_scores.cpu()[0, 0].numpy()


def poly_mask(shape, pts, sx, sy, ox, oy):
    m = Image.new('L', (shape[1], shape[0]), 0)
    ImageDraw.Draw(m).polygon([((x - ox) * sx, (y - oy) * sy) for x, y in pts], fill=255)
    return np.asarray(m) > 127


def linework(rgb, alpha):
    """the subject's own darker strokes (black top-hat on lightness), inside its mask"""
    L = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
    th = cv2.morphologyEx(L, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))) - L
    return np.clip((th - 6) / 18, 0, 1) * alpha


def main():
    C.load_boxes()
    os.makedirs(RAW, exist_ok=True)
    rerun = '--rerun' in sys.argv or not all(os.path.exists(os.path.join(RAW, f'{k}.png')) for k in TARGETS)
    model = proc = dev = None
    if rerun:
        model, proc, dev = load_model()
    for fid, (side, bu, pts_u) in TARGETS.items():
        full = C.load(side)
        sx, sy = C.scale(full)
        box = [bu[0], bu[1], bu[2] - bu[0], bu[3] - bu[1]]
        x0, y0, x1, y1 = C.px(full, box)
        R = full[y0:y1, x0:x1]
        to_px = lambda X, Y: [(X - bu[0]) * sx, (Y - bu[1]) * sy]
        raw = os.path.join(RAW, f'{fid}.png')
        if rerun:
            masks, scores = segment(model, proc, dev, Image.fromarray(R.astype(np.uint8)),
                                    to_px(bu[0] + 1, bu[1] + 1) + to_px(bu[2] - 1, bu[3] - 1), [to_px(*p) for p in pts_u])
            best = int(np.argmax(scores * np.array([m.mean() > 0.2 for m in masks])))
            print(fid, 'scores', np.round(scores, 3), 'kept', best)
            Image.fromarray(masks[best].astype(np.uint8) * 255).save(raw)
        m = np.asarray(Image.open(raw)) > 127
        if fid == 'lion':                  # the bust, not its pedestal
            m &= ~poly_mask(m.shape, PEDESTAL, sx, sy, bu[0], bu[1])
        # no slivers or crumbs along the edge: open, keep the main body, smooth the outline
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))) > 0
        m = C.keep_components(m, min_area=4000, keep=lambda st, c: st[cv2.CC_STAT_AREA] > 0.05 * m.sum())
        m = C.fill_holes(m)
        m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 4) > 0.5
        a = C.soft_edge(m, 1.0)
        if fid == 'lion':                  # where the bust meets its pedestal is not a printed edge: fade, not a cut
            ped = cv2.GaussianBlur(poly_mask(m.shape, PEDESTAL, sx, sy, bu[0], bu[1]).astype(np.float32), (0, 0), 3 * sx)
            a = a * np.clip(1 - ped * 1.5, 0, 1)
            # and it fades into its base
            fade = 1 - C.smoothstep(252, 272, bu[1] + np.arange(m.shape[0]) / sy)
            a = a * fade[:, None]
        C.save_piece(side, fid, full, box, C.defringe(R, a), a)
        full_lw = np.zeros(full.shape[:2], np.float32)
        full_lw[y0:y1, x0:x1] = linework(R, a)
        Image.fromarray((full_lw * 255).astype(np.uint8)).resize((1440, 640), Image.LANCZOS) \
            .save(os.path.join(C.ROOT, 'source', f'linework-{side}.png'), optimize=True)
        if fid == 'lion':
            # where the mane meets the face is not a printed edge: a soft transition, not a cut
            face = poly_mask(m.shape, FACE, sx, sy, bu[0], bu[1]).astype(np.float32)
            face = cv2.GaussianBlur(face, (0, 0), 5 * sx)
            am = a * np.clip(1 - face * 1.6, 0, 1)
            C.save_piece('front', 'mane', full, box, C.defringe(R, am), am)
    C.write_boxes()


if __name__ == '__main__':
    main()
