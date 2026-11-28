# Australian $100 banknote (next generation, 2020): security features

Interactive explorer of the Reserve Bank of Australia's next generation $100, first issued on 29 October 2020: Dame Nellie Melba on the signature side, Sir John Monash on the serial number side. The note shown is serial DK204519478.

**Locally:** open `index.html` directly (works from `file://`).

## Features covered

Top-to-bottom window · 3D fan · flying owl · colourful owl · reversing 100 in the Shrine of Remembrance · rolling colour effect (both sides) · fan in a small window · intaglio print · microprint · background print · fluorescent ink (ultraviolet view) · tactile feature · serial number.

The feature names, descriptions and "how to check" wording follow the RBA's own pages (see Sources). The page calls the sides **Melba side** and **Monash side**, as the RBA does ("signature side" and "serial number side"). This series has no Coat of Arms shadow image and no see-through registration device. Those belong to the first polymer series, which the RBA's feature list separates from the next generation features.

## Controls

These match the S$10,000 and US $100 pages:

- Move the pointer to tilt the note.
- Left-drag to rotate, right-drag to pan and use the wheel to zoom.
- Drag an edge to bend the note.
- Keys: **G** fold, **E** explode, **F** flip, **R** reset, **Esc** back.

Click a label or a feature to zoom in to it and see its callouts. After 10 s idle the note returns to rest. **Ultraviolet** shows the note under a UV lamp. Printing or saving as PDF covers the note with the EURion pattern.

## Illustrative, not exact

- **Optical effects:** the scans are flat, so every tilt effect is a simulation driven by the viewing angle and clipped to the feature's own cut-out:
  - the fan's raised copy and its diffraction lines
  - the flying owl's colour change and wing beat. The real owl moves its wings through a lenticular image. Here a copy of its line-work flexes.
  - the colourful owl's colour change
  - the forwards and backwards 100 in the Shrine, built from the window's own printed 100
  - the rolling colour band
  - the light and shade on the embossed fan in the small window

  None of these is a capture of the real optical effect.
- **Clear windows:** the scanner lid shows black through the windows. `tools/prepare_art.py` mattes that black out, so the page shows what is behind the note. The print in the windows keeps its own pixels and the embossing keeps partial alpha. The faint cool tint of the clear polymer is added.
- **Ultraviolet:** the RBA says "an owl and wattle branch" fluoresce on the Melba side and "a serial number and year of print" on the Monash side. It does not say which owl, or where the year of print is. The glow is put on the flying owl and the wattle branch, whose shapes match the UV image on the RBA's $100 security features flyer. The serial glows on the Monash side. The year of print cannot be located on the scan, so it is not drawn. The glow colours are illustrative.
- **Exploded view:** the order of the print layers is a teaching aid, not the printer's real sequence. The polymer substrate layer is the polymer with its clear windows (`assets/polymer.png`, drawn from the window shape). The window's print sits on its own layer next to it.
- **Tactile feature:** the RBA describes five raised bumps on each long edge. The scan shows only a faint row of reliefs along the top edge, and `front-tactile.png` is five round cuts of the artwork at the positions read from the scan, so those positions are approximate. The bumps on the bottom edge cannot be seen in the scan.
- **Microprint:** the scan resolves the *Melodies and Memories* block below the La Bohème score and the text curving through the Monash-side window. The cut-outs show those two places only. The quoted text was read from the scan.

## Weak cut-outs

- `front-microprint.png`: the letters are only a few pixels high, so the cut-out is legible but broken in places.
- `front-wattle.png`: on the left edge and among the small flowers a few specks of the background tint remain.
- `front-colourowl.png`: the foil reflects dark where the scanner lid shows through, so its darkest shading is a little patchy.

## Files

| Path | What |
|---|---|
| `index.html`, `styles.css`, `script.js`, `data.js` | the page; feature text and positions are in `data.js` |
| `aud-100-front.png`, `aud-100-back.png` | working artwork, 3072 × 1264 RGBA (clear windows transparent) |
| `assets/layers/` | clean alpha cut-outs of each feature; `assets/boxes.js` says where each sits |
| `assets/offset-*.webp`, `assets/polymer.png` | exploded-view layers: background print, and the polymer with its windows |
| `assets/masks.css` | effect masks as data URIs (so the page works from `file://`) |
| `assets/overrides/` | hand-cleaned cut-outs go here and always win (none yet) |
| `feature-crops/` | full-resolution copies of the cut-outs and `contact-sheet.png` (on a dark background) |
| `source/` | the Commons originals, the levelled scan (`flat-*`), the window masks and the SAM masks |
| `tools/prepare_art.py` | crop to the note edge, level, matte the clear windows |
| `tools/sam_masks.py` | Segment Anything (ViT-L) masks for the portraits, Rosina, the Shrine and the rolling-colour patches (GPU) |
| `tools/cut_features.py` | all cut-outs, boxes, offset and polymer layers, masks and the contact sheet |

To rebuild, run `python tools/prepare_art.py`, then `python tools/sam_masks.py`, then `python tools/cut_features.py`.

## Sources and credits

- **Images:** Wikimedia Commons, by BAVhah, licensed **CC BY-SA 4.0** (as stated on Commons). The licence is the uploader's claim. RBA banknote designs are RBA copyright, so confirm the rights before publishing.
  - Front: [File:100dollarnoteaus.jpg](https://commons.wikimedia.org/wiki/File:100dollarnoteaus.jpg), 8319 × 3421 px
  - Back: [File:100dollarnotrevers444.jpg](https://commons.wikimedia.org/wiki/File:100dollarnotrevers444.jpg), 8218 × 3413 px
- **Feature facts:** all from the Reserve Bank of Australia:
  - [Banknote Features: Explore, new $100](https://banknotes.rba.gov.au/banknote-features/explore/): feature names and wording, first issue date, size 65 × 158 mm, concept designer emerystudio, and the sources of the portraits and vignettes
  - [List of security features](https://banknotes.rba.gov.au/counterfeit-detection/list-of-security-features/): polymer, rolling colour effect, image in a small window, top-to-bottom window, 3D image, flying bird, colourful bird, reversing number, intaglio, background print, microprint, fluorescent ink (UV light centred around 365 nm)
  - [$100 security features flyer (PDF)](https://banknotes.rba.gov.au/assets/pdf/ngb100-security-features-flyer.pdf)
  - [$100 banknote page](https://banknotes.rba.gov.au/australias-banknotes/banknotes-in-circulation/hundred-dollar/): Melba and Monash, the Golden Wattle (*Acacia pycnantha*) and the Australian Masked Owl (*Tyto novaehollandiae*), the microprint sources, and the issue dates (29 October 2020; the first polymer $100 on 15 May 1996)
  - [Media release 20-04, $100 design reveal](https://www.rba.gov.au/media-releases/2020/mr-20-04.html): the wattle framing the window, and five raised bumps on each long edge
  - [Counterfeit detection](https://banknotes.rba.gov.au/counterfeit-detection/): only the newer series has the top-to-bottom window
- **Fonts:** all under the SIL Open Font License and bundled in `fonts/`.
  - Title: **Barlow** (Jeremy Tribby), a DIN-like grotesque. The RBA's next generation banknote material is set in DIN (DINOT), and the note's own numerals are in a similar grotesque.
  - Text: Source Sans 3, Source Serif 4 and IBM Plex Mono.
- **Palette:** the note's own greens, with golden wattle gold from the window's print.

## Reproduction rules for Australian banknotes

The RBA's [Guidelines for reproducing banknotes](https://banknotes.rba.gov.au/legal/reproducing-banknotes/) give its consent under the *Crimes (Currency) Act 1981* and the *Copyright Act 1968* to reproductions and images that meet these conditions:

- **Physical reproductions** must be less than three-quarters, or more than one and a half times, the length and width of the genuine banknote. They must also be one-sided only.
- **Electronic images**, viewed at 100 per cent, must be less than three-quarters the length and width of the genuine banknote and have a resolution not exceeding 72 dpi.
- **Footage** must not be usable to create reproductions that could mislead people.
- **Files** used to make a reproduction must be destroyed or deleted after use.
- **The RBA's name** must not be associated with the reproduction.
- **No derogatory use:** a reproduction must not distort a banknote in an inappropriate or derogatory way.

Partial images must meet the same requirements as complete ones.

The working artwork here (3072 px wide, both sides) is much larger and sharper than condition 2 allows, so it is for **local study only**. Before publishing the page, reduce the artwork to meet the guidelines, and take the RBA's name out of the page's own text and branding. The printed copy is covered with a EURion pattern, but that does not by itself meet the guidelines.
