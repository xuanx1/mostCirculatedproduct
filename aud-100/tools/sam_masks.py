"""
Segment Anything (SAM, ViT-L) masks for the features that are distinct objects on a busy background:
the two engraved portraits, the Shrine of Remembrance engraving and the two rolling-colour patches.

  python tools/sam_masks.py          (GPU: take the shared lock first, see the project brief)

Each feature is prompted with its box and a few positive points (note units, 720 x 320 over the
note); the best-scoring candidate that stays inside the box is kept, cleaned (small parts dropped,
holes filled) and written as a full-size mask, source/sam/<side>-<name>.png. tools/cut_features.py
applies it to the artwork's own pixels; nothing is redrawn.
"""
import os
import numpy as np
import cv2
import torch
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'source', 'sam')
VB_W, VB_H = 720, 320

# name -> (side, box x0, y0, x1, y1, positive points, negative points)   note units
TARGETS = {
    'portrait':  ('front', (350, 10, 532, 292), [(440, 150), (430, 60), (445, 255), (400, 110)], []),
    'rolling':   ('front', (26, 28, 124, 100), [(92, 72), (60, 48)], []),
    'rosina':    ('front', (522, 100, 604, 270), [(565, 150), (560, 220)], []),
}
TARGETS_BACK = {
    'portrait':  ('back', (138, 28, 352, 300), [(245, 150), (245, 60), (245, 260), (180, 260)], []),
    'shrine':    ('back', (36, 34, 172, 154), [(100, 100), (100, 60), (60, 130)], []),
    'rolling':   ('back', (580, 28, 694, 152), [(634, 96), (670, 50)], []),
}


def load_model():
    from transformers import SamModel, SamProcessor
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = SamModel.from_pretrained('facebook/sam-vit-large').to(dev).eval()
    proc = SamProcessor.from_pretrained('facebook/sam-vit-large')
    return model, proc, dev


def segment(model, proc, dev, img, box, pos, neg):
    pts = pos + neg
    labels = [1] * len(pos) + [0] * len(neg)
    inputs = proc(img, input_boxes=[[list(box)]], input_points=[[pts]], input_labels=[[labels]],
                  return_tensors='pt').to(dev)
    with torch.no_grad():
        out = model(**inputs, multimask_output=True)
    masks = proc.image_processor.post_process_masks(
        out.pred_masks.cpu(), inputs['original_sizes'].cpu(), inputs['reshaped_input_sizes'].cpu())[0][0]
    return masks.numpy(), out.iou_scores.cpu()[0, 0].numpy()


def clean(mask, min_frac=0.03):
    m = (mask > 0).astype(np.uint8) * 255
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    if n > 1:
        big = st[1:, cv2.CC_STAT_AREA].max()
        keep = np.zeros_like(m)
        for k in range(1, n):
            if st[k, cv2.CC_STAT_AREA] >= big * min_frac:
                keep[lab == k] = 255
        m = keep
    ff = m.copy()
    cv2.floodFill(ff, np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8), (0, 0), 255)
    return m | cv2.bitwise_not(ff)


def main():
    os.makedirs(OUT, exist_ok=True)
    model, proc, dev = load_model()
    for side, targets in (('front', TARGETS), ('back', TARGETS_BACK)):
        im = Image.open(os.path.join(ROOT, f'aud-100-{side}.png')).convert('RGBA')
        flat = Image.new('RGB', im.size, (245, 245, 240))
        flat.paste(im, mask=im.getchannel('A'))
        W, H = flat.size
        sx, sy = W / VB_W, H / VB_H
        for name, (_, b, pos, neg) in targets.items():
            m = 12
            cx0, cy0 = max(0, b[0] - m), max(0, b[1] - m)
            cx1, cy1 = min(VB_W, b[2] + m), min(VB_H, b[3] + m)
            crop = flat.crop((int(cx0 * sx), int(cy0 * sy), int(cx1 * sx), int(cy1 * sy)))
            px = lambda X, Y: [(X - cx0) * sx, (Y - cy0) * sy]
            box = px(b[0], b[1]) + px(b[2], b[3])
            masks, scores = segment(model, proc, dev, crop, box, [px(*p) for p in pos], [px(*p) for p in neg])
            bx0, by0, bx1, by1 = [int(v) for v in box]
            best, val = 0, -1
            for k in range(masks.shape[0]):
                inside = masks[k][by0:by1, bx0:bx1].sum() / max(1, masks[k].sum())
                v = scores[k] * inside
                if v > val:
                    best, val = k, v
            full = np.zeros((H, W), np.uint8)
            x0, y0 = int(cx0 * sx), int(cy0 * sy)
            mk = clean(masks[best])
            full[y0:y0 + mk.shape[0], x0:x0 + mk.shape[1]] = mk
            Image.fromarray(full).save(os.path.join(OUT, f'{side}-{name}.png'), optimize=True)
            print(f'{side:5} {name:10} mask {best} score {scores[best]:.3f}')


if __name__ == '__main__':
    main()
