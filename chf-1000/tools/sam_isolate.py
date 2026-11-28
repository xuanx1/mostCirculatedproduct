"""
Segment Anything (SAM, ViT-L) for the one feature that is a distinct object on a busy ground:
the handshake on the front. SAM is prompted with the hand's box and points on both hands (and
negative points on the background), returns three candidate masks, and the best-scoring one that
stays inside the box is kept. The full-size mask goes to source/masks/front-hand.png;
tools/extract_chf.py cleans it and cuts the layer from the original pixels.

Run: python tools/sam_isolate.py          (uses the cached facebook/sam-vit-large)
"""
import os
import numpy as np
import torch
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PX = 5
# id -> (side, box x0,y0,x1,y1 in note units, positive points, negative points)
TARGETS = {
    'hand': ('front', (0, 84, 320, 322),
             [(25, 130), (60, 150), (150, 140), (230, 125), (250, 220), (170, 240), (110, 290), (205, 300), (285, 170)],
             [(30, 260), (150, 70), (290, 90), (60, 330), (300, 300), (314, 147), (316, 245), (20, 75), (230, 96)]),
}


def main():
    from transformers import SamModel, SamProcessor
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = SamModel.from_pretrained('facebook/sam-vit-large').to(dev).eval()
    proc = SamProcessor.from_pretrained('facebook/sam-vit-large')
    os.makedirs(os.path.join(ROOT, 'source', 'masks'), exist_ok=True)
    for fid, (side, box, pos, neg) in TARGETS.items():
        im = Image.open(os.path.join(ROOT, f'chf-1000-{side}.png')).convert('RGB')
        m = 12
        cx0, cy0 = max(0, box[0] - m), max(0, box[1] - m)
        cx1, cy1 = min(320, box[2] + m), min(722, box[3] + m)
        crop = im.crop((cx0 * PX, cy0 * PX, cx1 * PX, cy1 * PX))
        to = lambda x, y: [(x - cx0) * PX, (y - cy0) * PX]
        b = to(box[0], box[1]) + to(box[2], box[3])
        pts = [to(*p) for p in pos] + [to(*p) for p in neg]
        lbl = [1] * len(pos) + [0] * len(neg)
        inputs = proc(crop, input_boxes=[[b]], input_points=[[pts]], input_labels=[[lbl]], return_tensors='pt').to(dev)
        with torch.no_grad():
            out = model(**inputs, multimask_output=True)
        masks = proc.image_processor.post_process_masks(out.pred_masks.cpu(), inputs['original_sizes'].cpu(),
                                                        inputs['reshaped_input_sizes'].cpu())[0][0].numpy()
        scores = out.iou_scores.cpu()[0, 0].numpy()
        best = int(np.argmax(scores))
        full = np.zeros((im.height, im.width), np.uint8)
        full[cy0 * PX:cy1 * PX, cx0 * PX:cx1 * PX] = masks[best] * 255
        Image.fromarray(full).save(os.path.join(ROOT, 'source', 'masks', f'{side}-{fid}.png'))
        for k in range(masks.shape[0]):
            Image.fromarray((masks[k] * 255).astype(np.uint8)).save(os.path.join(ROOT, 'source', 'masks', f'{side}-{fid}-cand{k}.png'))
        print(fid, 'scores', scores, 'best', best)


if __name__ == '__main__':
    main()
