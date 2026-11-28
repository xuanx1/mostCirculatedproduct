# €500 banknote, first series: security features

Interactive explorer of the €500 note of the first series of euro banknotes (2002 design, "modern 20th-century architecture"), issued by the European Central Bank and the national central banks of the euro area (the Eurosystem). There is no Europa-series €500. The ECB stopped producing the €500 in 2016. It has not been issued since 27 April 2019, but it is still legal tender: it keeps its value and can be exchanged at any euro area national central bank for an unlimited period. The note shown is the ECB's specimen, signed by Jean-Claude Trichet, serial S00000004795.

**Locally:** open `index.html` directly (works from `file://`).

## Features covered

Hologram patch (value ↔ window or doorway) · colour-changing number (back) · watermark · security thread · see-through number · raised print (intaglio) · tactile marks · gateway and bridge (the design) · ECB President's signature · small circles (EURion) · serial numbers · map of Europe · infrared (description only) · ultraviolet view.

Feature wording follows the ECB and the Deutsche Bundesbank (a Eurosystem central bank). The sources are listed below.

## Controls

The controls are the same as on the S$10,000 and US $100 pages:

- **Move** the pointer to tilt the note.
- **Left-drag** to rotate, **right-drag** to pan, **wheel** to zoom.
- **Drag an edge** to bend the paper.
- **G** folds, **E** explodes, **F** flips, **R** resets, **Esc** goes back.

The card for the watermark, the thread and the see-through number has a **Hold up to the light** button. It completes the see-through 500, shows the thread as a dark stripe, and brings out the watermark.

## Illustrative, not exact

- **Artwork.** The only flat, straight scans on Wikimedia Commons are 944 × 484 px, and both sides carry the word "specimen" diagonally across them. The word has been removed from both sides by LaMa inpainting (`tools/remove_specimen.py`, big-lama model). A mask is made of each letter and its white rim, and LaMa fills it from the print around it. A few spots needed a further fix. The front "e" got a second pass, in two halves. The pink star it hid has its top arm redrawn from the star's own geometry and colour. On the back, the three serial digits hidden by the "p" are copies of a "0" from the same serial. What lies under the letters is therefore reconstructed, not original print. The untouched upscales are kept as `source/*-artwork-specimen.png`. The page has no specimen layer, and every cut-out is made from the cleaned artwork. **The ECB's reproduction rules require this word on electronic reproductions (see the last section), so the owner must check this before publishing the page.**
- **Upscaling.** The artwork is upscaled ×2 with Real-ESRGAN, then resized and brightened (`tools/upscale.py`). The upscaler sharpens line-work, but it cannot recover microlettering the 944 px scan never captured.
- **Hologram.** The "window or doorway" image is the real hologram, taken from a museum photograph of a genuine note (see the credits). It is rectified and cut to the scan's own patch outline (`tools/holo_window.py`). The rainbow bands and rings that move with the tilt are drawn. The € perforations are described but not drawn.
- **Watermark.** The scan's own faint watermark shows the window grid in slight perspective with "500" below it. `tools/watermark.py` lifts it out of the 944 px scan, but at that size it is mostly noise. `tools/watermark_clean.py` then redraws it: the window's lines are placed where they read in the recovered image and drawn as even soft lines, and the "500" uses the note's own printed "500" (cut by colour from the front's lower left), fitted onto the recovered figures, whose proportions it matches (1.98 : 1). Positions and proportions are the real ones; the line weight and softness are illustrative.
- **Security thread.** A reflected-light scan doesn't show the thread, so it is drawn from the ECB and Bundesbank descriptions (`tools/make_thread.py`). Its position (x ≈ 323 of 720, in the middle third) is read off the ECB Quick Guide diagram and is approximate. So is its width.
- **Colour-changing number.** The page fades the ink from purple, as printed, to olive brown and then olive green with tilt. The exact hues are approximate.
- **Ultraviolet.** The paper stays dull. What glows follows the ECB: the flag green with orange stars, the signature green, the large stars and the small circles, and on the back the bridge, the map and the 500. Which large stars glow, and their shape, comes from the ECB's own UV photograph of the note (`source/uv-front-ecb-commons.jpg`). The coloured fibres are random, as in every real note.
- **Infrared.** The issuers say only that "parts of the motif" in the right third of the front remain visible, and that the back's top-right serial number can be read. The page therefore marks that area and that number. It has no infrared view.
- **Microlettering.** The Bundesbank puts it "at several places of the banknote motif" without naming them. Only the thread's microletters are placed on the page.
- **EURion.** The ECB names the small circles (they glow under UV) but does not document the EURion constellation. The name and purpose come from independent research by Markus Kuhn (University of Cambridge, 2002).

## Weak cut-outs

- **Large 500 numeral.** Its lower edge, where it overlaps the main image, is cut by a straight line. The bottom of the middle 0 and the top right of the last 0 are inpainted (the removed word crossed them there), and their engraving is smoother than elsewhere.
- **Main image** (Segment Anything). It includes the stars printed over the building.
- **Bridge** and **500 EURO ΕΥΡΩ** on the back. A few pale hatching fragments remain, plus part of the lavender band behind ΕΥΡΩ.

## Files

| Path | What |
|---|---|
| `index.html`, `styles.css`, `script.js`, `data.js` | the page; feature text and positions are in `data.js` |
| `eur-500-front.png`, `eur-500-back.png` | working artwork (3072 × 1574, 160 × 82 mm) |
| `assets/layers/` | feature cut-outs, the watermark, the thread and the hologram's window image |
| `assets/boxes.js`, `assets/masks.css` | where each layer sits; optical and line-work masks as data URIs |
| `assets/offset-*.jpg` | offset print for the exploded view (intaglio, foil, silk-screen and letterpress removed) |
| `assets/overrides/` | hand-cleaned layers go here and always win (none yet) |
| `feature-crops/` | full-resolution cut-outs and `contact-sheet.png`, for review |
| `source/` | original images, the raw ESRGAN upscales, the untouched working artwork before the word was removed (`*-artwork-specimen.png`) and the cached SAM masks (`source/sam/`) |
| `tools/upscale.py` | Real-ESRGAN ×2, brightening and resizing |
| `tools/remove_specimen.py` | removes the word "specimen" from the working artwork by LaMa inpainting (`--preview` writes the letter mask over the image) |
| `tools/cutouts.py` | colour-separation, rectangle and Segment Anything cut-outs, `boxes.js`, offset layers, `masks.css`; `--no-sam` reuses the cached masks, `--clean` deletes unreferenced layers |
| `tools/fix_cuts.py` | clean-ups for the architecture and bar cut-outs (run after `cutouts.py`) |
| `tools/watermark.py`, `tools/watermark_clean.py`, `tools/make_thread.py`, `tools/holo_window.py` | the watermark (recovered, then redrawn), the thread and the hologram's window image |

Rebuild order: `upscale.py`, then `remove_specimen.py`, then `cutouts.py`, then `fix_cuts.py` (straightens the architecture's outline under the big "5" and fills the star-tip notch in the bar), then `watermark.py`, `watermark_clean.py`, `make_thread.py` and `holo_window.py`. `upscale.py` writes the artwork with the word on it, so `remove_specimen.py` must follow it: delete `source/*-artwork-specimen.png` first, so the new upscale is kept as the untouched copy. The GPU steps (ESRGAN, LaMa and SAM) take the shared `.gpu-lock`.

## Sources and credits

**Base images (Wikimedia Commons):**
- [EUR 500 obverse (2002 issue).jpg](https://commons.wikimedia.org/wiki/File:EUR_500_obverse_(2002_issue).jpg) and [EUR 500 reverse (2002 issue).jpg](https://commons.wikimedia.org/wiki/File:EUR_500_reverse_(2002_issue).jpg): 944 × 484 px each, design by Robert Kalina / ECB. Commons source: euromena.sk. Licence: "use permitted by the ECB" under Decisions ECB/2003/4 and ECB/2003/5, which were superseded by ECB/2013/10 (see below).

**Other images:**
- **Hologram, window state:** [500 euro banknote type 2002 hologram building.jpg](https://commons.wikimedia.org/wiki/File:500_euro_banknote_type_2002_hologram_building.jpg) by Copyleft, CC BY-SA 4.0 (4640 × 3472 px), in `source/holo-building-commons.jpg`. The hologram layer derived from it (`assets/layers/holo-window.png`) is shared under the same licence. This photo shows a whole genuine front at higher resolution. It is not used as the base because it has pins over its corners and reflections from the museum glass.
- **UV reference:** [500euro-uv-front.jpg](https://commons.wikimedia.org/wiki/File:500euro-uv-front.jpg) and [500euro-uv-rear.jpg](https://commons.wikimedia.org/wiki/File:500euro-uv-rear.jpg), by the European Central Bank, ECB-decision licence (700 × 358 and 700 × 356 px).
- **Not used:** the ECB's own downloadable images. They are 72 dpi and marked "specimen", which is smaller than the Commons scans, and the 300 dpi set is available on request for professional print use only. The textures of the ECB website's 3-D viewer are colour-encoded.

**Feature facts (ECB):**
- [Quick Guide to the security features of euro banknotes](https://www.ecb.europa.eu/euro/pdf/material/Quick_Guide_EN_Specimen.pdf), the €500 pages: size, colour, architecture, hologram patch, colour-changing number, watermark, thread, UV.
- [Trainer's Guide to the euro banknotes and coins](https://www.ecb.europa.eu/euro/pdf/material/Trainer_A4_EN_SPECIMEN.pdf): see-through number, perforations, tactile marks, microprinting, printing processes, signatures, design theme, UV images.
- [Current banknotes](https://www.ecb.europa.eu/euro/banknotes/current/html/index.en.html): first series, legal tender status, not issued since 27 April 2019.
- [Press release of 4 May 2016](https://www.ecb.europa.eu/press/pr/date/2016/html/pr160504.en.html): the end of production and issuance.

**Feature facts (Deutsche Bundesbank):**
- [Security features of the €500 banknote, first series: front](https://www.bundesbank.de/en/tasks/cash-management/counterfeit-money/counterfeit-detection/security-features-of-the-500-banknote-first-series-755312) and [back](https://www.bundesbank.de/en/tasks/cash-management/counterfeit-money/counterfeit-detection/-500-1st-series/counterfeit-detection-500-euro-banknote-reverse-side): thread text, watermark 500, raised copyright line, IR, UV, microlettering.

**Signature:** identified as Jean-Claude Trichet's by comparison with the specimen signatures in the ECB Trainer's Guide (p. 5).

**Fonts:** Fira Sans ExtraBold (title, chosen for its resemblance to the note's open sans-serif EURO lettering and value numerals), Source Sans 3, Source Serif 4 and IBM Plex Mono. All are under the SIL Open Font License and bundled in `fonts/`.

**Palette:** the note's own purples and lavender, with the EU flag's blue (#003399) as a secondary accent. The page background shows the flag's twelve stars, drawn in CSS.

## Reproduction rules (ECB Decision ECB/2013/10, Article 2)

The ECB summarises the rules on its [banknote images page](https://www.ecb.europa.eu/euro/banknotes/images/html/index.en.html). The full text is [Decision ECB/2013/10, consolidated](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A02013D0010-20210104). Its Article 2 was amended by Decision (EU) 2020/2090. Reproductions that follow the rules need no authorisation:

- **Physical, both sides:** at least 200 % or at most 50 % of the note's length and width.
- **Physical, one side:** at least 125 % or at most 75 %.
- **Part of a side:** smaller than 33 % of that side.
- **Physical, any size:** allowed if made of a material clearly different from banknote paper.
- **Electronic:** the word "specimen" must run diagonally across the reproduction, in bold Arial, in a colour that contrasts with the note. It must be at least 75 % of the reproduction's length and at least 15 % of its width in height. The resolution must not exceed **72 dpi at 100 % of the note's size**.
- **Design elements:** single elements may be reproduced, as long as they are not shown on a background that resembles a banknote.

Anything else needs the ECB's authorisation, and the person making the reproduction is responsible for compliance.

**This page does not meet these rules as it stands.** At the owner's request, the "specimen" marking has been removed from both sides (see "Illustrative, not exact"). The artwork is also shown at well above 72 dpi: the working images are about 490 dpi at 100 % size, and even the original Commons scans are about 150 dpi. Before publishing the page, the owner must check this with the ECB and get its authorisation, or restore the marking and reduce the resolution. The print/PDF version adds the EURion pattern over the note.
