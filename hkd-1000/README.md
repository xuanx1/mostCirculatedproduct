# HK$1,000 (HSBC, 2018 Series): security features

Interactive explorer of the HK$1,000 note of Hong Kong's 2018 Series as issued by The Hongkong and Shanghai Banking Corporation Limited (HSBC). The HK$1,000 was the first note of the series to circulate, from the last quarter of 2018.

**Locally:** open `index.html` directly (works from `file://`).

## Features covered

Dynamic shimmering pattern · windowed metallic thread · embossed feel · concealed denomination · enhanced watermark · fluorescent see-through denomination (the HKMA's six) · iridescent pattern on the lion's mane · microtext in the large 1000 (HSBC's additions) · braille · tactile lines · serial numbers · Stitt, the HSBC lion · signature and date · Financial Metropolis (the reverse) · ultraviolet view.

Feature wording follows the Hong Kong Monetary Authority's 2018 Series pages (English and Chinese) and HSBC's own 2018 banknotes page; see Sources.

## Controls

These are the same as on the S$10,000 and US $100 pages:

- Move the pointer to tilt the note.
- Left-drag to rotate, right-drag to pan, and use the wheel to zoom.
- Drag an edge to bend the note.
- **G** folds, **E** explodes, **F** flips, **R** resets and **Esc** goes back.
- The see-through denomination and the watermark each have a **Hold up to the light** button.

## The reverse is vertical

The whole 2018 Series has its reverse printed in vertical orientation. The page shows the note as it really backs the obverse: flipped, the reverse lies a quarter turn round. The back half of the see-through 1000 at the reverse's top left then lands exactly behind the front half at the obverse's bottom right. `tools/upscale.py` turns the vertical reverse image a quarter turn anticlockwise to do this. The two halves register to the pixel at their mirrored positions, which was checked by overlaying them.

## Illustrative, not exact

- **Artwork resolution.** No high-resolution image of this note exists from an open or official source (see Sources). The images are 516 × 260 (front) and 259 × 518 (back). Each was upscaled ×4 by running Real-ESRGAN ×2 twice, then levelled. Small text such as the bank's English name, the promise text and the microtext could not be recovered and looks garbled at high zoom.
- **Concealed denomination.** The scans cannot show it, so it is drawn. The drawing uses the note's own 1000 numerals: the two see-through halves joined, filled with fine lines in the area's red, the way HSBC's close-up shows it. Its exact position in the red area below the lion is approximate. It is placed from HSBC ("at the bottom of the note") and the HKMA's marker.
- **Dynamic shimmering pattern, thread rings and iridescent mane.** These are animated renderings of the official descriptions, clipped to the real print:
  - a ring of light moves over the bauhinia;
  - large and small rings move along the thread windows;
  - a pearly sheen crosses the mane.
- **Extent of the iridescent area.** HSBC says only "on the mane". The mane cut-out is the lion minus its face, with a soft boundary.
- **Watermark.** It is built from HSBC's own photograph of it, registered onto the artwork by the serial-number column (template match). The photograph cuts the top of the flower slightly.
- **UV.** The HKMA says the see-through patterns appear in two fluorescent colours. The leaflet's UV picture shows the front's upper pieces magenta and lower pieces white, which is what the front shows here. The back's split, upper magenta and lower white, is inferred from the front and is not shown by the HKMA. Nothing else is made to glow, because the official sources describe no other UV feature.
- **Serial.** The artwork carries the sample number AB123456. HSBC's series started at AA.
- **Lion.** Its lower edge fades into the pedestal. The painting has no printed edge there.

## Files

| Path | What |
|---|---|
| `index.html`, `styles.css`, `script.js`, `data.js` | the page; feature text, labels and positions are in `data.js` |
| `hkd-1000-front.png`, `hkd-1000-back.png` | working artwork, 2880 × 1440 (163 × 81.5 mm = 2 : 1); the back is turned to landscape |
| `assets/layers/` | the cut-outs (glow highlights, exploded layers, optics, UV), framed on the boxes in `assets/boxes.js` |
| `assets/masks.css` | masks for the optical effects, as data URIs (works from `file://`) |
| `assets/offset-*.jpg` | the print with the separately layered features removed (exploded view) |
| `assets/overrides/` | hand-cleaned cut-outs (empty); a file here always wins over a generated one |
| `feature-crops/` | full-resolution trimmed cut-outs for inspection |
| `source/` | the original official images, raw ESRGAN outputs, SAM's raw masks, reference photos; not used by the page |
| `tools/upscale.py` | Real-ESRGAN ×2 twice + levels; turns the reverse |
| `tools/sam_isolate.py` | Segment Anything (ViT-L) for the lion (and its mane) and the city view; caches the raw masks in `source/sam/` |
| `tools/hkd_features.py` | the other cut-outs by colour and outline rules, the watermark, the latent image, masks, boxes and offset layers |
| `tools/subset_fonts.py` | builds the two subset fonts |
| `tools/common.py` | shared helpers |

To rebuild, run these in order (`tools/upscale.py` needs the RealESRGAN_x2plus weights; `tools/sam_isolate.py` needs facebook/sam-vit-large):

```
python tools/upscale.py <RealESRGAN_x2plus.pth>
python tools/sam_isolate.py --rerun
python tools/hkd_features.py
python tools/subset_fonts.py <Montserrat[wght].ttf> <NotoSerifTC[wght].ttf>
```

## Sources and credits

- **Base images.** Wikimedia Commons has no image of any 2018 Series Hong Kong note. Searches of Commons by API (English and Chinese terms, the Hong Kong banknote and HSBC banknote categories) found only historical notes; modern Hong Kong notes are copyright works of their issuers. The images are therefore the HKMA's own published images, the clean (unmarked) note images embedded on page 2 of the HKMA leaflet [*2018 Series Hong Kong Banknotes*](https://www.hkma.gov.hk/media/eng/doc/key-functions/money/notes-and-coins/design-and-security/2018/Leaflet_Eng.pdf):
  - front: image xref 24, 516 × 260 px;
  - back: image xref 26, 259 × 518 px.

  They are © HKMA / HSBC, not under an open licence, and are shown here under the HKMA reproduction rules below. Larger official images (635 × 318) exist only with a SPECIMEN overprint across the note, so they were not used.
- **Watermark and reference close-ups.** HSBC, [2018 HSBC New Series Hong Kong Banknotes](https://www.hsbc.com.hk/banknotes-2018/): the watermark, see-through, iridescent, microtext, latent and thread close-ups, kept in `source/reference/`. The watermark is built from HSBC's watermark photograph. Also used: the HKMA's annotated front and back images on the page below.
- **Feature facts:**
  - HKMA, [2018 Series Banknotes: design and security features](https://www.hkma.gov.hk/eng/key-functions/money/hong-kong-currency/notes/design-and-security-features-of-currency-notes/) ([Chinese](https://www.hkma.gov.hk/chi/key-functions/money/hong-kong-currency/notes/design-and-security-features-of-currency-notes/)), and its leaflet (size 163 × 81.5 mm; UV picture);
  - HKMA press release [2018 New Series Hong Kong Banknotes, 24 July 2018](https://www.hkma.gov.hk/eng/news-and-media/press-releases/2018/07/20180724-5/) (six features, vertical reverse, circulation timing);
  - HSBC, [banknotes-2018](https://www.hsbc.com.hk/banknotes-2018/) ([Chinese](https://www.hsbc.com.hk/zh-hk/banknotes-2018/)) for the seven features, Stitt, the Main Building, watercolour, Financial Metropolis, serials starting AA, braille, tactile lines and the high-tactility numeral.
- **Fonts** (SIL Open Font License, bundled in `fonts/` with their licence texts):
  - Montserrat for the title amount: the note's numerals are a geometric sans.
  - Noto Serif TC, subset to the 70 Chinese characters the page uses: a Ming face like the bank's Chinese name on the note.
  - Source Serif 4, Source Sans 3 and IBM Plex Mono for the text, Latin only.
- **Palette.** The note's own gold and orange (title flow, highlights), with HSBC red as the accent on a warm paper-white page.

## Reproduction rules (Hong Kong)

Under the Laws of Hong Kong (Crimes Ordinance, Cap. 200, s. 103), a person who reproduces any Hong Kong currency note or any part of one on any substance, whether or not to the correct scale, without the Monetary Authority's written consent commits an offence. The HKMA states that unless the electronic images are to be reproduced into a physical form, its approval is not required for filming currency notes for viewing on mobile phones and electronic screens. Anyone reproducing notes should also liaise with the note-issuing bank, here HSBC, over its rights in the design. Source: HKMA, [Reproduction of Hong Kong Currency Notes](https://www.hkma.gov.hk/eng/key-functions/money/hong-kong-currency/reproduction-of-hong-kong-currency/reproduction-of-hong-kong-notes/), and the notice on the HKMA's [2018 Series page](https://www.hkma.gov.hk/eng/key-functions/money/hong-kong-currency/notes/design-and-security-features-of-currency-notes/).

This page is for viewing on screen. Printing it or saving it as a PDF gives only a flat front image covered by the EURion constellation, and it should not be printed.
