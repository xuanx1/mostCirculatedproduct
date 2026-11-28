# HK$1,000 (Standard Chartered, 2018 Series): security features

Interactive explorer of the HK$1,000 note of Hong Kong's 2018 Series as issued by Standard Chartered Bank (Hong Kong) Limited (渣打銀行(香港)有限公司), Hong Kong's oldest note-issuing bank. Its HK$1,000 was the first note of the bank's 2018 series, its tenth, to circulate, from 12 December 2018.

**Locally:** open `index.html` directly (works from `file://`).

## Features covered

Dynamic shimmering pattern · windowed metallic thread · embossed feel · concealed denomination · enhanced watermark · fluorescent see-through denomination (the HKMA's six) · braille · tactile lines · serial numbers · the Standard Chartered Bank Building and the Forum · signatures and date · Wit and Wisdom: the Central skyline (the reverse) · ultraviolet view.

Feature wording follows the Hong Kong Monetary Authority's 2018 Series pages and leaflet, and Standard Chartered's own 2018 Banknotes Series page and documents; see Sources.

Neither the HKMA nor Standard Chartered names any feature specific to this bank's note. HSBC lists an iridescent pattern and microtext on its own note, but no source gives either for the Standard Chartered note, so this page does not show them. Its optical effects are the shimmering pattern, the thread and the concealed denomination.

## Controls

These are the same as on the HSBC HK$1,000 page:

- Move the pointer to tilt the note.
- Left-drag to rotate, right-drag to pan, and use the wheel to zoom.
- Drag an edge to bend the note.
- **G** folds, **E** explodes, **F** flips, **R** resets and **Esc** goes back.
- The see-through denomination and the watermark each have a **Hold up to the light** button.

## The reverse is vertical

The whole 2018 Series has its reverse printed in vertical orientation. The page shows the note as it really backs the obverse: flipped, the reverse lies a quarter turn round. `tools/upscale.py` turns the vertical reverse image a quarter turn anticlockwise to do this. The back half of the see-through 1000 at the reverse's top left then lands behind the front half at the obverse's bottom right. Overlaid at their mirrored positions, the two halves register to within about 1 to 3 px of the 2880 px artwork.

## Illustrative, not exact

- **Artwork resolution.** No high-resolution image of this note exists from an open or official source (see Sources). The images are 518 × 259 (front) and 260 × 518 (back). Each was upscaled ×4 by running Real-ESRGAN ×2 twice, then levelled. Small text, such as the promise text and the titles under the signatures, could not be recovered and looks garbled at high zoom.
- **Concealed denomination.** The scans cannot show it, so it is drawn. The drawing uses the note's own 1000 numerals: the two see-through halves joined, filled with fine lines in the area's own red, darker. Its place comes from the HKMA's marker and close-up, in the red print at the foot of the bank building. Its exact position and size are approximate.
- **Dynamic shimmering pattern and thread rings.** These are animated renderings of the official descriptions, clipped to the real print:
  - a ring of light moves over the bauhinia;
  - large and small rings move along the thread windows.
- **Watermark.** It is built from the HKMA's close-up photograph of this note's watermark (108 × 102 px, upscaled ×4). It is registered onto the artwork by the vertical serial number the photograph shows, which fixes both its scale and its position. Because the source is so small, the motif's relief is soft and partly reconstructed by the upscaler.
- **UV.** The HKMA says the see-through patterns appear in two fluorescent colours. The HKMA leaflet's UV picture of this note shows the front's upper pieces magenta and its lower pieces white, which is what the front shows here. The back's split, upper magenta and lower white, is inferred from the front and is not shown by the HKMA. Nothing else is made to glow, because the official sources describe no other UV feature.
- **Building names on the callouts.** Standard Chartered says the front shows "the Standard Chartered Bank Building and the Forum in Central", but it does not say which building is which. The tower bearing the bank's logo is labelled the Standard Chartered Bank Building. The faceted glass block is labelled the Forum, whose glass façade the bank says inspired the background.
- **"Towers drawn in tiny digits".** This callout describes what the reverse visibly shows. Standard Chartered says only that the design includes "symbols of technology and the stock market" (象徵金融科技的設計圖案), and it does not say which elements those are.
- **Serial.** The HKMA artwork carries the sample number AB123456.
- **Cut-out edges.** The building and skyline cut-outs follow the coral ink. Their outlines are smoothed, and where the skyline's towers are dot-matrix the outline runs round the dots, not through them. The Forum fades out at its foot, where it meets a coral ground of the same colour. That ground is not part of the building and has no printed edge.

## Files

| Path | What |
|---|---|
| `index.html`, `styles.css`, `script.js`, `data.js` | the page; feature text, labels and positions are in `data.js` |
| `hkd-1000-scb-front.png`, `hkd-1000-scb-back.png` | working artwork, 2880 × 1440 (163 × 81.5 mm = 2 : 1); the back is turned to landscape |
| `assets/layers/` | the cut-outs (glow highlights, exploded layers, optics, UV), framed on the boxes in `assets/boxes.js` |
| `assets/masks.css` | masks for the optical effects, as data URIs (works from `file://`) |
| `assets/offset-*.jpg` | the print with the separately layered features removed (exploded view) |
| `assets/overrides/` | hand-cleaned cut-outs (empty); a file here always wins over a generated one |
| `feature-crops/` | full-resolution trimmed cut-outs for inspection |
| `source/` | the original HKMA images, the raw ESRGAN outputs, the line-work masks and the HKMA close-ups (`reference/`); not used by the page |
| `tools/upscale.py` | Real-ESRGAN ×2 twice + levels; turns the reverse; upscales the watermark close-up |
| `tools/subjects.py` | the bank buildings (front) and the Central skyline (back), by colour separation |
| `tools/hkd_features.py` | the other cut-outs by colour rules, the watermark, the concealed denomination, masks, boxes and offset layers |
| `tools/subset_fonts.py` | builds the two subset fonts |
| `tools/common.py` | shared helpers |

To rebuild, run these in order. `tools/upscale.py` needs the RealESRGAN_x2plus weights; nothing else needs a model.

```
python tools/upscale.py <RealESRGAN_x2plus.pth>
python tools/subjects.py
python tools/hkd_features.py
python tools/subset_fonts.py <Inter[opsz,wght].ttf> <NotoSansTC[wght].ttf>
```

Segment Anything, which the HSBC page used for its lion and city, was tried first for the buildings and the skyline. It returned the whole prompt box both times, because these subjects sit on a continuous printed background. They are separated by their coral ink instead (red minus green), from the original pixels.

## Sources and credits

- **Base images.** Wikimedia Commons has no image of any 2018 Series Hong Kong note. Searches of Commons by API (English and Chinese terms, and the "Banknotes of Hong Kong" category) found only historical notes and an older Standard Chartered HK$10. The images are therefore the HKMA's own published images: the clean, unmarked note images embedded on page 2 ("Security features of Standard Chartered Bank (HK) Limited $1000 banknote") of the HKMA leaflet [*2018 Series Hong Kong Banknotes*](https://www.hkma.gov.hk/media/eng/doc/key-functions/money/notes-and-coins/design-and-security/2018/Leaflet_Eng.pdf):
  - front: image xref 20, 518 × 259 px;
  - back: image xref 22, 260 × 518 px.

  The leaflet's own "Specimen" overprint is a separate layer drawn over these images, so the embedded images carry no marking and nothing had to be removed. They are © HKMA / Standard Chartered Bank (Hong Kong) Limited, not under an open licence, and are shown here under the HKMA reproduction rules below. Larger official images exist only with a SPECIMEN overprint, so they were not used:
  - the HKMA's 635 × 318 [front](https://www.hkma.gov.hk/media/eng/img/key-functions/money/notes-and-coins/notes/design-security-features-of-currency-notes/2018/SCBHK/1000/banknotes_scb_1000_front_mark.jpg) and [back](https://www.hkma.gov.hk/media/eng/img/key-functions/money/notes-and-coins/notes/design-security-features-of-currency-notes/2018/SCBHK/1000/banknotes_scb_1000_back_mark.jpg) (SPECIMEN · 樣本);
  - Standard Chartered's [SCB1000_2.png](https://av.sc.com/hk/content/images/SCB1000_2.png), about 615 px wide per side (SPECIMEN).
- **Watermark and reference close-ups.** The HKMA's six feature close-ups of this note, `scb_1000_no1.jpg` to `scb_1000_no6.jpg` (kept in `source/reference/`), from the HKMA's 2018 Series page below. The watermark is built from `scb_1000_no5.jpg`. The concealed denomination is placed from `scb_1000_no4.jpg` and the HKMA's markers.
- **Feature facts:**
  - HKMA, [2018 Series Banknotes: design and security features](https://www.hkma.gov.hk/eng/key-functions/money/hong-kong-currency/notes/design-and-security-features-of-currency-notes/) ([Chinese](https://www.hkma.gov.hk/chi/key-functions/money/hong-kong-currency/notes/design-and-security-features-of-currency-notes/)): the six security features, the accessibility features (braille, tactile lines, high-tactility numerals), the standardised reverse themes and the vertical reverse;
  - its leaflet (size 163 × 81.5 mm; feature markers; the UV picture of this note);
  - HKMA press release [2018 New Series Hong Kong Banknotes, 24 July 2018](https://www.hkma.gov.hk/eng/news-and-media/press-releases/2018/07/20180724-5/).
- **Design facts** (front buildings, "Wit and Wisdom", the Central skyline, symbols of technology and the stock market, Lion Rock, the "Hong Kong Spirit" theme, tenth series, the issue date):
  - Standard Chartered, [Standard Chartered 2018 Banknotes Series](https://www.sc.com/hk/standard-chartered-2018-banknotes-series/) ([Chinese](https://www.sc.com/hk/zh/standard-chartered-2018-banknotes-series/): 渣打銀行大廈與渣打財富管理中心, 靈活睿智, 中環海濱);
  - its [design features document](https://av.sc.com/hk/content/docs/hk-banknotes-series-design-features-en.pdf);
  - its press release of [11 December 2018](https://av.sc.com/hk/content/docs/hk-sc-2018-banknotes-series-en.pdf) (circulation from 12 December 2018).
- **Signatures, titles and date.** These are read from the note itself (the HKMA images): 財務總裁 Chief Financial Officer, 行政總裁 Chief Executive, 香港 二〇一八年一月一日 Hong Kong 1 January 2018.
- **Fonts** (SIL Open Font License, bundled in `fonts/` with their licence texts):
  - Inter for the title amount: the note's numerals and the bank's name are a clean grotesque sans;
  - Noto Sans TC, subset to the 77 Chinese characters the page uses: a Hei face like the bank's Chinese name on the note;
  - Source Serif 4, Source Sans 3 and IBM Plex Mono for the text, Latin only.
- **Palette.** The note's own coral and peach run through the title, with a glint of Standard Chartered blue. Standard Chartered blue is the accent, with a deep navy ink, on a warm paper-white page.

## Reproduction rules (Hong Kong)

Under the Laws of Hong Kong (Crimes Ordinance, Cap. 200, s. 103), a person who reproduces any Hong Kong currency note or any part of one on any substance, whether or not to the correct scale, without the Monetary Authority's written consent commits an offence. The HKMA states that unless the electronic images are to be reproduced into a physical form, its approval is not required for filming currency notes for viewing on mobile phones and electronic screens. Anyone reproducing notes should also liaise with the note-issuing bank, here Standard Chartered Bank (Hong Kong) Limited, over its rights in the design. Source: HKMA, [Reproduction of Hong Kong Currency Notes](https://www.hkma.gov.hk/eng/key-functions/money/hong-kong-currency/reproduction-of-hong-kong-currency/reproduction-of-hong-kong-notes/), and the notice on the HKMA's [2018 Series page](https://www.hkma.gov.hk/eng/key-functions/money/hong-kong-currency/notes/design-and-security-features-of-currency-notes/).

This page is for viewing on screen. Printing it or saving it as a PDF gives only a flat front image covered by the EURion constellation, and it should not be printed.
