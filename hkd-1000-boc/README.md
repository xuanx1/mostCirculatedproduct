# HK$1,000 (Bank of China (Hong Kong), 2018 Series): security features

Interactive explorer of the HK$1,000 note of Hong Kong's 2018 Series as issued by Bank of China (Hong Kong) Limited (BOCHK, 中國銀行(香港)有限公司). The 2018 Series HK$1,000 notes went into circulation on 12 December 2018.

**Locally:** open `index.html` directly (works from `file://`).

## Features covered

Dynamic shimmering pattern · windowed metallic thread · embossed feel · concealed denomination · enhanced watermark · fluorescent see-through denomination (the HKMA's six, which BOCHK lists too) · braille · tactile lines (BOCHK's accessibility features) · serial numbers · the Bank of China Tower · the bauhinia flower · signature and date · A Smart Metropolis (the reverse) · ultraviolet view.

The wording follows the Hong Kong Monetary Authority's 2018 Series pages (English and Chinese) and BOCHK's own 2018 New Series page. See Sources.

Unlike the HSBC page, this page has no iridescent pattern and no microtext. Neither the HKMA nor BOCHK lists either feature for this note, so neither is shown.

## Controls

These are the same as on the HSBC HK$1,000 page:

- Move the pointer to tilt the note.
- Left-drag to rotate, right-drag to pan, and use the wheel to zoom.
- Drag an edge to bend the note.
- **G** folds, **E** explodes, **F** flips, **R** resets and **Esc** goes back.
- The see-through denomination and the watermark each have a **Hold up to the light** button.

## The reverse is vertical

The whole 2018 Series has its reverse printed in vertical orientation. The page shows the note as it really backs the obverse: flipped, the reverse lies a quarter turn round. `tools/upscale.py` turns the vertical reverse image a quarter turn anticlockwise. The see-through pieces at the reverse's top left then land behind the front pieces at the obverse's bottom right. Overlaying the two cut-outs at their mirrored positions showed them interlocking into one complete 1000. The front half is the upper left of each digit plus the top of the 1; the back half is the rest. They meet to within a few pixels.

## Illustrative, not exact

- **Artwork resolution.** No high-resolution unmarked image of this note exists from an open or official source (see Sources). The images are 518 × 259 (front) and 260 × 514 (back). Each was upscaled ×4 by running Real-ESRGAN ×2 twice, then levelled. Small print, such as the bank's English name and the promise text, could not be recovered and looks garbled at high zoom.
- **Concealed denomination.** The scans cannot show it, so it is drawn. It uses the note's own large 1000, from the numeral cut-out, filled with a fine diamond lattice in a deeper red of the tower, the way the HKMA's close-up (`boc_1000_no4.jpg`) shows it. It is placed in the middle section of the Bank of China Tower, at the HKMA's marker 4. Its exact size and position are approximate.
- **Dynamic shimmering pattern and thread rings.** These are animated renderings of the official descriptions, clipped to the real print:
  - a ring of light moves over the bauhinia;
  - large and small rings move along the thread windows.
- **Watermark.** It is built from the HKMA's own photograph of this note's watermark (`boc_1000_no5.jpg`, 108 × 102), upscaled ×4. It is registered onto the artwork by the vertical serial number visible in the photograph: 1.16 leaflet px per photo px. Because the photograph is small, the watermark is soft. Faint printed lines that showed through at its top right were faded out.
- **UV.** The HKMA says the see-through patterns appear in two fluorescent colours under UV. Its close-up of this note (`boc_1000_no6.jpg`) shows the front's upper pieces magenta and its lower pieces white, which is what the front shows here. The back's split, upper magenta and lower white, is inferred from the front and is not shown by the HKMA. Nothing else is made to glow, because the official sources describe no other UV feature.
- **Serial.** The artwork carries the sample number AB123456. The HKMA's marked images show AA000000.
- **Cut-outs.**
  - Bauhinia flower: below the flower, Segment Anything also took in the pale faceted "diamond" shape of the background. That part was cut away along a hand-placed line with a soft fade, so the flower's lower left edge there is a fade, not a printed edge.
  - The last 0 of the large 1000 overlaps the red top of the tower, which is as dark as the digits. Its right half is the mirror of its clean left half, since the digit is upright and symmetric.
  - A Smart Metropolis: the cut-out's right edge stops where the neck meets the red vertical band.

## Files

| Path | What |
|---|---|
| `index.html`, `styles.css`, `script.js`, `data.js` | the page; feature text, labels and positions are in `data.js` |
| `hkd-1000-boc-front.png`, `hkd-1000-boc-back.png` | working artwork, 2880 × 1440 (163 × 81.5 mm = 2 : 1); the back is turned to landscape |
| `assets/layers/` | the cut-outs (glow highlights, exploded layers, optics, UV), framed on the boxes in `assets/boxes.js` |
| `assets/masks.css` | masks for the optical effects, as data URIs (works from `file://`) |
| `assets/offset-*.jpg` | the print with the separately layered features removed (exploded view) |
| `assets/overrides/` | hand-cleaned cut-outs (empty); a file here always wins over a generated one |
| `feature-crops/` | full-resolution trimmed cut-outs for inspection |
| `source/` | not used by the page: the original HKMA images, raw ESRGAN outputs (`*-esrgan-x4.png`, including the watermark photo), SAM's raw candidate masks (`sam/`), the HKMA's close-ups of this note (`reference/`) and the line-work masks |
| `tools/upscale.py` | Real-ESRGAN ×2 twice + levels; turns the reverse; upscales the watermark photo |
| `tools/sam_isolate.py` | Segment Anything (ViT-L) for the tower and the flower (front) and the heads (back); caches the raw masks in `source/sam/` |
| `tools/hkd_features.py` | the other cut-outs by colour and lightness rules, the watermark, the concealed 1000, masks, boxes and offset layers |
| `tools/subset_fonts.py` | builds the two subset fonts |
| `tools/common.py` | shared helpers |

To rebuild, run these in order. `tools/upscale.py` needs the [RealESRGAN_x2plus](https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth) weights. `tools/sam_isolate.py` needs facebook/sam-vit-large.

```
python tools/upscale.py <RealESRGAN_x2plus.pth>
python tools/sam_isolate.py --rerun
python tools/hkd_features.py
python tools/subset_fonts.py <Montserrat[wght].ttf> <NotoSerifTC[wght].ttf>
```

## Sources and credits

- **Base images.**
  - Wikimedia Commons has no image of any 2018 Series Hong Kong note. Searches of Commons by API found only historical notes: English and Chinese terms, the "Banknotes of Hong Kong" category, and the Bank of China (Hong Kong) categories.
  - The images are therefore the HKMA's own published images: the clean (unmarked) BOCHK note images embedded on page 2 of the HKMA leaflet [*2018 Series Hong Kong Banknotes*](https://www.hkma.gov.hk/media/eng/doc/key-functions/money/notes-and-coins/design-and-security/2018/Leaflet_Eng.pdf):
    - front: image xref 16, 518 × 259 px JPEG, kept byte-for-byte as `source/front-hkma-leaflet-518.jpg`;
    - back: image xref 18, 260 × 514 px JPEG, kept as `source/back-hkma-leaflet-260.jpg`.

    The Chinese leaflet holds the same images at the same size. They are © HKMA / BOCHK, not under an open licence, and are shown here under the HKMA reproduction rules below.
  - Larger official images exist only with markings, so they were not used:
    - the HKMA's [front](https://www.hkma.gov.hk/media/eng/img/key-functions/money/notes-and-coins/notes/design-security-features-of-currency-notes/2018/BOCHK/1000/banknotes_boc_1000_front_mark.jpg) (635 × 318) and [back](https://www.hkma.gov.hk/media/eng/img/key-functions/money/notes-and-coins/notes/design-security-features-of-currency-notes/2018/BOCHK/1000/banknotes_boc_1000_back_mark.jpg) (317 × 635), which carry "SPECIMEN 樣本" and numbered markers;
    - BOCHK's own images (403 × 201, "樣本 Specimen").
  - No specimen marking appears on any image the page uses, so no marking had to be removed.
- **Close-ups of this note** (`source/reference/`): the HKMA's six feature close-ups on the 2018 Series page, `…/2018/BOCHK/1000/boc_1000_no1.jpg` to `no6.jpg`:
  - shimmering bauhinia;
  - thread windows;
  - large 1000 (embossed feel);
  - concealed 1000 in the tower lattice;
  - watermark held to the light;
  - see-through and UV.

  The watermark layer is built from `no5`. The marked images above were used only to read the positions of the HKMA's feature markers and the printed text, such as 總裁 CHIEF EXECUTIVE and the date.
- **Feature facts:**
  - HKMA, [2018 Series Banknotes: design and security features](https://www.hkma.gov.hk/eng/key-functions/money/hong-kong-currency/notes/design-and-security-features-of-currency-notes/) ([Chinese](https://www.hkma.gov.hk/chi/key-functions/money/hong-kong-currency/notes/design-and-security-features-of-currency-notes/)): the six features with BOCHK's front and back markers; and the leaflet above (size 163 × 81.5 mm);
  - HKMA press release [2018 New Series Hong Kong Banknotes, 24 July 2018](https://www.hkma.gov.hk/eng/news-and-media/press-releases/2018/07/20180724-5/): the six features, the vertical reverse, and the HK$1,000 theme of Hong Kong as an international financial centre;
  - HKMA press release [11 December 2018](https://www.hkma.gov.hk/eng/news-and-media/press-releases/2018/12/20181211-3/): the HK$1,000 in circulation from 12 December 2018;
  - BOCHK, [2018 New Series Design / Security Features](https://www.bochk.com/dam/bochk/desktop/top/aboutus/banknote/2018/index_en.html) ([Chinese](https://www.bochk.com/dam/bochk/desktop/top/aboutus/banknote/2018/index_tc.html)), the source for the design elements:
    - the bauhinia, Hong Kong's floral emblem, and the Bank of China Tower on the front of every note;
    - the diamond patterns and the head silhouette on the right of the HK$1,000;
    - the golden colour scheme;
    - the theme "A Smart Metropolis": two people in profile, a brain structure of the digits 0 and 1, a globe;
    - braille and tactile lines;
    - intaglio printing (凹版印刷) for the embossed feel.
- **Fonts** (SIL Open Font License, bundled in `fonts/` with their licence texts):
  - Montserrat for the title amount: the note's numerals are a rounded geometric sans.
  - Noto Serif TC for the bank's Chinese name, subset to the 72 Chinese characters the page uses: a Ming face like the Chinese text on the note.
  - Source Serif 4, Source Sans 3 and IBM Plex Mono for the text, Latin only.
- **Palette.** The note's own gold, orange and olive (the colours of its large 1000) run through the title, with BOC red as the accent on a warm paper-white page.
- **Tools.** The upscale uses [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) (RealESRGAN_x2plus). The masks use Segment Anything (facebook/sam-vit-large).

## Reproduction rules (Hong Kong)

Under the Laws of Hong Kong (Crimes Ordinance, Cap. 200, s. 103), a person who reproduces any Hong Kong currency note or any part of one on any substance, whether or not to the correct scale, without the Monetary Authority's written consent commits an offence. BOCHK's page repeats this notice. The HKMA states that its approval is not required for filming currency notes for viewing on mobile phones and electronic screens, unless the electronic images are to be reproduced into a physical form. Anyone reproducing notes should also liaise with the note-issuing bank, here BOCHK, over its rights in the design. Source: HKMA, [Reproduction of Hong Kong Currency Notes](https://www.hkma.gov.hk/eng/key-functions/money/hong-kong-currency/reproduction-of-hong-kong-currency/reproduction-of-hong-kong-notes/), and the notice on the HKMA's [2018 Series page](https://www.hkma.gov.hk/eng/key-functions/money/hong-kong-currency/notes/design-and-security-features-of-currency-notes/).

This page is for viewing on screen. Printing it or saving it as a PDF gives only a flat front image covered by the EURion constellation, and it should not be printed.
