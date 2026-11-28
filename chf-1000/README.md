# Swiss 1000-franc note (ninth series): security features

Interactive explorer of the Swiss National Bank's 1000-franc note of the ninth series, issued on 13 March 2019. Its theme is Switzerland's communicative flair, with language as the key motif: a handshake and a globe with phonetic symbols on the front, the federal parliament and an open network on the back. The note shown is the **specimen** the SNB publishes. It has the SPECIMEN overprint, which is kept on purpose (see *Reproduction rules* below).

**Locally:** open `index.html` directly. It works from `file://`.

## Orientation

The ninth-series notes are upright designs. The SNB shows both sides of the 1000-franc note in portrait format, 70 × 158 mm, with all lettering reading horizontally. This page keeps the note upright rather than turning it on its side: the note space is 320 × 722 units, drawn at 640 × 1444 px and shown at half size, and the labels sit in a column on either side of the tall note. Flip (**F**) turns the note about its long axis, which shows the back the right way up, as it is when you turn a real note over. Bending and folding use the existing engine, which bends about the vertical axis, so on this upright note the fold runs along the note's length.

## Features covered

These are the SNB's own numbers and names:

1 Globe test · 2 Security strip test · 3 Cross test · 4 Triangle test · 5 Hand test (raised intaglio print: hand, 1000, bank name) · 6 Microperf® · 7 Tactile elements (six blocks on each long edge) · 8 Watermark (Swiss flag and globe) · 9 Tilt effect · 10 See-through register · 11 Serial number · 12 Microtext · 13 Ultraviolet globe, which also covers 14, the ultraviolet fibres.

Number 15 (infrared properties) appears in the ultraviolet overview text only. The SNB does not say which elements change under infrared, so the page does not draw it.

**Against the light:** for the Cross, Triangle, Microperf, Watermark and See-through register tests, the feature panel has a **Hold up to the light** button. It brightens the note and shows what transmitted light reveals: the window cross becomes the Swiss flag, the thread becomes a continuous line, the perforated cross shines through, both watermarks show, and the register marks join into one cross outline.

**Exploded view (E):** the three-layer Durasafe® substrate is the core: paper (back), polymer core, paper (front). The window cross is a hole through both paper layers, so only the polymer fills it. The watermarks and the thread sit in the substrate. The reverse layers (offset print, serials and register, intaglio) are on one side and the obverse layers (offset print, security strip, globe, intaglio, UV ink) on the other.

## Controls

Move the pointer to tilt the note. Left-drag rotates it, right-drag pans and the wheel zooms. Drag an edge to bend it. Keys: **G** fold · **E** explode · **F** flip · **R** reset · **Space** auto-rotate · **Esc** back. Hovering a label lights up its feature, and clicking one zooms in with detail callouts. After 10 s without input the note returns to rest. Printing or saving as PDF gives a flat front covered by the EURion ring pattern.

## Illustrative, not exact

The tilt optics and the transmitted-light effects are drawn from the SNB's descriptions, not filmed from a note:

- **Globe test:** the golden arc is a light band that moves with left-right tilt. The colour change on tilting backwards is a hue-shifted copy of the globe. The SNB says the colour changes but not to which colour.
- **Security strip:** tilted backwards, the strip's own silver print (the map and the 1000) turns to rainbow colours, using a mask taken from the strip's silver pixels. The red and green numbers on four lines are the digits 1000 repeated, sliding in opposite directions. Their exact artwork is not published, and the shining crosses inside the 1000 are not drawn.
- **Tilt effect:** the Swiss cross at position C is drawn. Its position comes from the SNB brochure photo; its size is estimated.
- **Watermarks:** the globe watermark is rebuilt from the note's own globe as soft continuous tone. The Swiss-flag watermark is a drawn outline of a flag. Their positions and sizes were measured on the SNB brochure's transmitted-light photo (`tools/extract_chf.py`: `GLOBE_WM`, `FLAG_WM`); the flag's size is approximate.
- **Microperf®:** the hole pitch and the size of the perforated cross are not published. The cross of holes is drawn at position D.
- **Triangle and thread:** the triangle's outline was traced by eye on the artwork. The thread seen against the light (a line with the Swiss flag and 1000) is drawn from the SNB's description, and the spacing of the repeats is invented.
- **Cross test against the light:** the red flag square around the window is drawn, and its size is estimated.
- **UV globe:** the glow is the SNB's own UV photograph of the globe (from the brochure, `source/found/snb-brochure-uv-globe.png`), fitted to the note. It is low resolution and soft. The UV fibres are drawn at random positions in five colours.
- **Microtext:** the letters are too small to read in the photograph. The layer keeps the two blocks of fine marks the photo does resolve at position B, measured on the artwork.
- **Artwork:** upscaled ×2 with Real-ESRGAN and levelled (`tools/upscale.py`). The upscaler sharpens line-work but cannot recover detail the 827 px source never captured.

## Files

| Path | What |
|---|---|
| `index.html`, `styles.css`, `script.js`, `data.js` | the page. Feature text and positions are in `data.js` (320 × 722 note units) |
| `chf-1000-front.png`, `chf-1000-back.png` | working artwork, 1600 × 3610 (5 px per note unit) |
| `assets/layers/` | the feature cut-outs and drawn layers. `assets/boxes.js` says where each one sits |
| `assets/masks.css` | the effect masks as data URIs (globe, strip silver print, triangle glitter, line-work) |
| `assets/offset-*.jpg` | the offset print with the intaglio and foil features removed (exploded view) |
| `assets/network-bg.png` | page background: the note's open network, from the SNB brochure |
| `feature-crops/` | every cut-out trimmed to its content, for review |
| `source/` | the SNB originals, the raw ×2 upscales, the SAM hand mask and the SNB brochure (`found/`). The page does not need these |
| `tools/upscale.py` | Real-ESRGAN ×2 and levelling |
| `tools/sam_isolate.py` | Segment Anything mask of the handshake |
| `tools/extract_chf.py` | every cut-out, drawn layer, mask, box and offset layer |
| `tools/network_bg.py` | page background |
| `assets/overrides/` | hand-cleaned layers, which always win (none yet) |

How each cut-out is made (`tools/extract_chf.py`):

| Cut-out | Method |
|---|---|
| Handshake | SAM, then cleaned |
| Globe | an exact circle measured on the rim |
| Front 1000 | purple ink with its counters open |
| Back 1000 | the 0s from their dark hatching; the 1 cut to its traced outline, because it stands on a purple ground of the same darkness |
| Bank names | selected by gold colour |
| Serials, tactile bars | ink darker than its local background |
| Register marks | colour |
| Strip, window cross | exact geometry |

## Sources and credits

- **Artwork: the SNB's own images.** Wikimedia Commons has the ninth-series 1000-franc note only at 345 × 778 px ([front](https://commons.wikimedia.org/wiki/File:CHF_1000_9_front.jpg), [back](https://commons.wikimedia.org/wiki/File:CHF_1000_9_back.jpg)). Both files credit the Swiss National Bank and designer Manuela Pfrunder and are marked public domain, with a currency restriction. They are too small for this page, so it uses the larger specimen images the SNB publishes on its series page, [snb.ch: Banknotes, series 9](https://www.snb.ch/en/the-snb/mandates-goals/cash/series-9):
  - `banknote_widget_series_9_design_denomination_1000_front.n.jpg`, 827 × 1866 (from `snb.ch/dam/jcr:778b68b3-…`)
  - `…_1000_back.n.jpg`, 827 × 1866 (from `snb.ch/dam/jcr:0b7471d0-…`)
  - Both are Hasselblad photographs with a translucent SPECIMEN overprint (originals kept in `source/`). Design: Manuela Pfrunder; © Swiss National Bank.
  - **The overprint has been removed** (it is a translucent grey film that darkens the print under it):
    1. `tools/remove_specimen.py`, `tools/restore_detail.py`: a first LaMa pass and detail restore, used only as a starting point.
    2. `tools/unblend_all.py --preview`, `tools/glyph_fit.py`, `tools/template_fit.py`: the overprint's exact letter shapes. Its darkening is measured pixel by pixel; the typeface is Corbel; the back's clean S, P, E, C, I are used as stencils on both sides, and bold Corbel for M and N.
    3. `tools/unblend_all.py`: inside each letter the original's own fine detail is kept and only its brightness is matched to the print around it, so what is under the letters (the hands' engraving, both bank names, the serial 17C6215816) is the real print; a 4–7 px band along each letter's edge is filled by LaMa, and letter ends the fit missed are added and treated the same way.
    4. `tools/fix_slivers.py`, `tools/fix_rim.py`: two slivers by "Mille Franchi" and the overprint's light rim along its letters' upper-left edges.
  - Measured result: the letters' contrast against the print around them fell from 0.28 to 0.03 (front) and 0.31 to 0.02 (back). What remains up close: faint light lines along some letter edges, most visible on the "M" across the fingers. The handshake cut-out's wrists fade out (`tools/hand_wrists.py`).
- **Feature facts, positions (A to E) and the UV photograph:** the SNB brochure [*The new 1000-franc note*](https://www.snb.ch/dam/jcr:8d5b56a1-54c4-4a95-83f4-5429fea8b7be/nb_1000.en.pdf) (2019), pages 8 to 11; copy in `source/found/`. Also [snb.ch, series 9](https://www.snb.ch/en/the-snb/mandates-goals/cash/series-9) and the [downloads page](https://www.snb.ch/en/the-snb/mandates-goals/cash/downloads).
- **Open-network background:** the illustration on page 6 of the same SNB brochure.
- **Fonts**, all under the SIL Open Font License 1.1 and bundled in `fonts/`:
  - **Fira Sans** for the title and headings: a humanist sans chosen to sit with the note's own lettering. It is not the typeface the note uses.
  - **Source Sans 3** for text.
  - **IBM Plex Mono** for figures.
- **Palette:** the note's purple, the SNB's colour for this denomination, with the gold of the printed bank name as a second accent.

## Reproduction rules

From the SNB's [Instruction sheet on the reproduction of banknotes](https://www.snb.ch/dam/jcr:7ab35b8a-2bd5-4ad7-8255-52711da841ac/instr_rep_notes.en.pdf) (30 August 2017), which covers the ninth series, and the [reproduction page](https://www.snb.ch/en/the-snb/mandates-goals/cash/reproduction):

- **The law:** reproducing banknotes in a way that risks confusion with genuine notes is an offence under art. 243 of the Swiss Criminal Code.
- **SPECIMEN:** the SNB generally sees no risk of confusion when the word SPECIMEN is printed diagonally across the reproduction, at least 75 % of its length and 15 % of its width, in a clearly contrasting colour. The SNB images carry that overprint, but it has been removed here at the project owner's request, so this condition is not met as the page stands: check with the SNB before publishing.
- **One further condition** must also be met, for example:
  - a reduced size whose length is at most 66 % of the original, or an enlarged one of at least 150 %;
  - a partial reproduction of less than 40 % of one side;
  - a clearly different material or colour.

  The overall circumstances also count, including printing both sides.
- **Resolution:** banknote images in an electronic medium that third parties can freely access may not exceed **72 dpi**. This page's artwork is far above that, about 580 dpi at actual size, and it shows both sides at a size the viewer controls, so as built it does not meet the instruction sheet's conditions for a public website. Downsample the artwork or ask SNB Archives (archiv@snb.ch) before publishing.
- **Credit:** publication should carry an illustration credit; the SNB's "Permission for reproduction" form comes from SNB Archives.
