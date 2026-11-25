# Singapore S$10,000: Portrait Series security features

Interactive explorer of the S$10,000 note (Portrait Series, first issued 9 September 1999).

**Live:** [xuanx1.github.io/mostCirculatedproduct/sgd-10000](https://xuanx1.github.io/mostCirculatedproduct/sgd-10000/) · **Locally:** open `index.html` directly (works from `file://`).

## Features covered

Watermark (Yusof bin Ishak, visible from both sides) · security thread (windowed on the reverse) · Kinegram foil · colour-shift 10000 · intaglio printing · quadrilingual title · latent 10K · see-through register (Merlion) · serial numbers · Chairman's signature · Chinese seal · state crest · tactile mark · Onyx cowrie · guilloche portrait · ultraviolet view.

## Controls

| Action | How |
|---|---|
| Tilt | move the pointer over the note (gyroscope on phones) |
| Rotate | left-drag |
| Pan | right-drag |
| Zoom | mouse wheel, or the slider |
| Bend | drag an edge, or the Bend slider |
| Fold / Explode / Flip | **G** / **E** / **F** |
| Reset | **R** |
| Leave a feature or the exploded view | **Esc** |

## Files

| Path | What |
|---|---|
| `index.html`, `styles.css`, `script.js`, `data.js` | the page; feature text and positions are in `data.js` |
| `sgd-10k-front.png`, `sgd-10k-rear.png` | artwork used by the page |
| `assets/layers/` | cut-outs the page uses (highlights, exploded view) |
| `assets/overrides/` | hand-cleaned images; every build uses these and never overwrites them |
| `assets/masks.css`, `assets/boxes.js` | generated effect masks and layer positions |
| `feature-crops/` | full-resolution transparent cut-outs, for presentations |
| `tools/` | extraction scripts: `python tools/extract_features.py` rebuilds everything (Pillow, numpy, OpenCV, scipy) |

## Sources

- Issue date, signatory and reverse theme: [Wikipedia, Singapore Portrait Series](https://en.wikipedia.org/wiki/Singapore_Portrait_Series_currency_notes).
- Discontinuation from 1 October 2014: [MAS](https://www.mas.gov.sg/currency/singapores-circulation-currency-notes) and press coverage.
- Brunei interchangeability: [BullionStar](https://www.bullionstar.com/blogs/bullionstar/singapore-brunei-and-the-10000-banknote/).
- UV and colour-shift behaviour on this page are illustrative, not a record of the real note.
