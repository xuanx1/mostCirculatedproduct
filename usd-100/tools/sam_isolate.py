"""
AI isolation of the $100's features with Segment Anything (SAM, ViT-L) on the upscaled artwork.

For each feature below, SAM is prompted with the feature's box (plus optional positive points),
returns three candidate masks, and the best-scoring one that stays inside the box is kept. The
mask is cleaned (largest parts, holes filled, ~1 px anti-aliased edge) and applied to the
original pixels of the enhanced artwork, so nothing is redrawn.

Writes, per feature (hand-cleaned files in assets/overrides/ always win):
  feature-crops/<side>/<id>.png     the isolated feature, full resolution, transparent background
  assets/layers/<side>-<id>-cut.png the same, framed for the page (glow / exploded view)
  assets/layers/<side>-<id>.png     (same file, so the ink layer matches)

Run: python tools/sam_isolate.py            (first run downloads facebook/sam-vit-large, ~1.2 GB)
"""
import os, sys
import numpy as np
import cv2
import torch
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import extract_features as EF  # noqa: E402

ROOT = EF.ROOT
OVR = os.path.join(ROOT, 'assets', 'overrides')
LAYERS = os.path.join(ROOT, 'assets', 'layers')

# id -> (side, box x0,y0,x1,y1 in note units, extra positive points in note units)
TARGETS = {
    'portrait':      ('front', (104, 8, 374, 296), [(270, 120), (230, 270)]),
    'bell':          ('front', (411, 196, 489, 286), [(450, 240)]),
    'ovi-100':       ('front', (543, 241, 677, 291), [(568, 266), (610, 266), (650, 266)]),
    'treasury-seal': ('front', (505, 96, 597, 188), [(551, 142)]),
    'gold-100':      ('back',  (571, 35, 687, 267), [(628, 90), (628, 150), (628, 225)]),
    'hall':          ('back',  (93, 46, 575, 262), [(330, 150), (330, 70)]),
}


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
    scores = out.iou_scores.cpu()[0, 0]
    return masks.numpy(), scores.numpy()


def clean(mask, min_frac=0.02):
    m = (mask > 0).astype(np.uint8) * 255
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    if n > 1:
        big = st[1:, cv2.CC_STAT_AREA].max()
        keep = np.zeros_like(m)
        for k in range(1, n):
            if st[k, cv2.CC_STAT_AREA] >= big * min_frac:
                keep[lab == k] = 255
        m = keep
    ff = m.copy(); pad = np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8)
    cv2.floodFill(ff, pad, (0, 0), 255)
    m |= cv2.bitwise_not(ff)                                   # fill enclosed holes
    a = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 0.8)
    return np.clip((a - 0.5) * 2.2 + 0.5, 0, 1)


def main():
    model, proc, dev = load_model()
    imgs = {s: Image.open(os.path.join(ROOT, f)).convert('RGB') for s, f in EF.SRC.items()}
    report = []
    for fid, (side, box_u, pts_u) in TARGETS.items():
        im = imgs[side]
        W, H = im.size
        sx, sy = W / EF.VB_W, H / EF.VB_H
        m = 10                                                    # context margin (note units)
        cx0, cy0 = max(0, box_u[0] - m), max(0, box_u[1] - m)
        cx1, cy1 = min(EF.VB_W, box_u[2] + m), min(EF.VB_H, box_u[3] + m)
        crop_box = (int(cx0 * sx), int(cy0 * sy), int(cx1 * sx), int(cy1 * sy))
        crop = im.crop(crop_box)
        to_px = lambda X, Y: [(X - cx0) * sx, (Y - cy0) * sy]
        box = to_px(box_u[0], box_u[1]) + to_px(box_u[2], box_u[3])
        pts = [to_px(x, y) for x, y in pts_u]
        masks, scores = segment(model, proc, dev, crop, box, pts)
        # prefer high score and a mask that fills a sensible part of the box
        bx0, by0, bx1, by1 = [int(v) for v in box]
        best, best_val = 0, -1
        for k in range(masks.shape[0]):
            mk = masks[k]
            inside = mk[by0:by1, bx0:bx1].sum() / max(1, mk.sum())
            val = scores[k] * inside
            if val > best_val:
                best, best_val = k, val
        alpha = clean(masks[best])
        rgba = np.dstack([np.asarray(crop), (alpha * 255).astype(np.uint8)])
        out = Image.fromarray(rgba, 'RGBA')
        bb = out.getchannel('A').point(lambda v: 255 if v > 6 else 0).getbbox()
        pres = out.crop((max(0, bb[0] - 12), max(0, bb[1] - 12), min(out.width, bb[2] + 12), min(out.height, bb[3] + 12)))
        os.makedirs(os.path.join(EF.OUT, side), exist_ok=True)
        if not os.path.exists(os.path.join(OVR, f'{side}-{fid}-cut.png')):
            pres.save(os.path.join(EF.OUT, side, f'{fid}.png'), optimize=True)
            for stale in (f'{fid}-ink.png',):
                p = os.path.join(EF.OUT, side, stale)
                if os.path.exists(p):
                    os.remove(p)
        # page layer: re-frame onto the PAD box the page uses for this feature (assets/boxes.js)
        shape, g = next((r[3], r[4]) for r in EF.REGIONS if (r[1], r[0]) == (side, fid))
        (px0, py0, px1, py1), _ = EF.bbox(shape, g, EF.PAD)
        frame = Image.new('RGBA', (int(round((px1 - px0) * sx)), int(round((py1 - py0) * sy))), (0, 0, 0, 0))
        frame.alpha_composite(out, (int(round((cx0 - px0) * sx)), int(round((cy0 - py0) * sy))))
        scale = 1440 / W * 1.5
        frame = frame.resize((max(1, round(frame.width * scale)), max(1, round(frame.height * scale))), Image.LANCZOS)
        for name in (f'{side}-{fid}-cut.png', f'{side}-{fid}.png'):
            if not os.path.exists(os.path.join(OVR, name)):
                frame.save(os.path.join(LAYERS, name), optimize=True)
        report.append(f'{side:5} {fid:14} mask {best} score {scores[best]:.3f}')
    print('\n'.join(report))


if __name__ == '__main__':
    main()
