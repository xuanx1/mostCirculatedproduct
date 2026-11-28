# Bank of England £50 polymer note (Alan Turing): security features

Interactive explorer of the Bank of England's polymer £50, issued on 23 June 2021, Alan Turing's birthday. The note shown is the **Queen Elizabeth II** version. Notes carrying the portrait of King Charles III have been issued since 5 June 2024, but no usable image of the King Charles III front *and* back exists on Wikimedia Commons, or as a matching pair from the Bank (see Sources).

**Locally:** open `index.html` directly (works from `file://`).

## Features covered

Hologram ("Fifty" changes to "Pounds") · see-through windows (gold and green foil on the front, silver on the back; the two gold squares swap "50" and "£") · the monarch's portrait in the window · silver foil patch with a 3D coronation crown · red foil patch with "AT" · the second, smaller window · raised print · raised dots (tactile feature) · ultraviolet number · print quality and microlettering · unique numbering · Alan Turing's portrait · Turing's work (table and formulae, ticker tape) · the quote · Turing's signature · the Chief Cashier's signature.

Feature wording follows the Bank of England's £50 page ([bankofengland.co.uk/banknotes/polymer-50-pound-note](https://www.bankofengland.co.uk/banknotes/polymer-50-pound-note)). The Bank calls the monarch's side the front and the Turing side the back, and so does this page.

## Controls

Same as the other explorers: move to tilt, left-drag to rotate, right-drag to pan, wheel to zoom, drag an edge to bend, and **G** fold · **E** explode · **F** flip · **R** reset · **Esc** back. After 10 s without input the note eases back to its resting pose.

## How the optics work

- **Windows.** The page artwork is transparent where the polymer is clear (main window and portrait oval, small window), with a slight haze; print and foil on the windows stay solid. You see the page through them, on both sides.
- **Hologram.** Rainbow diffraction bands slide with the tilt, as on the other explorers' foils. Tilted side to side by about 4 degrees, "Fifty" changes to "Pounds".
- **Window foil.** A metallic glint runs across the gold foil (silver on the back). Past about 4 degrees of tilt the two gold squares change places, so "50" and "£" swap.
- **Silver crown patch** and **red foil patch.** These have diffraction bands and a metallic glint.
- **Ultraviolet.** The polymer and print go dull violet, and only the front's "50" lights up, in red and green. That is the only fluorescent feature the Bank describes.
- **Exploded view.** It shows the reverse (serial numbers, red foil, print), the polymer film (white, with its two clear windows) and the obverse (print, foils and hologram, raised print, UV ink).

## Illustrative, not exact

- **"Pounds" in the hologram.** The specimen image only shows the word "Fifty". The tilted state has "Fifty" removed from the foil (inpainted from the foil around it) and "Pounds" set in Source Serif 4 Bold, at the same cap height and colour (`tools/extras.py`). The real hologram's lettering differs.
- **Ultraviolet 50.** UV ink is invisible in daylight images, so the 50 is drawn in Bodoni Moda with a red and green diamond pattern, after the Bank's UV photograph. The Bank does not publish its exact position. It is placed behind "of England", where the Bank's UV photograph shows it, so treat the position as approximate.
- **Swapped squares.** The tilted state of the gold squares is the note's own two squares exchanged. The real foil's transition is an optical effect, not a cross-fade.
- **Tactile dots.** These are four clusters of four, measured from the embossing shadows in the image and cut as exact circles.
- **The polymer layer** in the exploded view is drawn as a film, not taken from an image. The Bank's pages say only that the note is printed on polymer. The separate print layers are the artwork with the foils removed.
- **Artwork.** It was upscaled with Real-ESRGAN x2 and levelled (`tools/upscale.py`). The upscaler sharpens line-work but cannot recover microlettering the source image never had.

## Files

| Path | What |
|---|---|
| `index.html`, `styles.css`, `script.js`, `data.js` | the page; feature text, layers, highlights and callouts are in `data.js` |
| `gbp-50-front.png`, `gbp-50-back.png` | page artwork (3072 × 1620, the note's 146 × 77 mm), windows transparent |
| `assets/layers/` | each feature as an alpha cut-out at page resolution, plus the hologram "Pounds" state, the swapped foil squares and the UV 50 |
| `assets/boxes.js`, `assets/masks.css` | where each layer sits (note units), and the effect masks as data URIs (so `file://` works) |
| `assets/print-*.webp`, `assets/substrate.webp` | exploded-view layers |
| `feature-crops/` | every cut-out at full resolution, and `contact-sheet.png` |
| `source/` | the Bank's original images, the ESRGAN output, the levelled artwork, Segment Anything masks (not needed by the page) |
| `tools/upscale.py` | Real-ESRGAN x2 and levels |
| `tools/sam_masks.py` | Segment Anything (ViT-L) masks for the distinct objects (GPU) |
| `tools/cutouts.py` | all cut-outs (SAM, fitted ellipses, colour separation, exact circles), window alpha, boxes, contact sheet |
| `tools/extras.py` | hologram "Pounds", foil swap, UV 50, exploded-view layers, `masks.css` |
| `assets/overrides/` | hand-cleaned cut-outs go here and always win (none yet) |

Rebuild: `python tools/upscale.py <RealESRGAN_x2plus.pth>`, then `python tools/sam_masks.py`, then `python tools/cutouts.py`.

## Sources and credits

- **Base images.** These are the Bank of England's own specimen images, from its banknote image library on Flickr: [£50 front, polymer](https://www.flickr.com/photos/bankofengland/51069593723) and [£50 back, polymer](https://www.flickr.com/photos/bankofengland/51001108075), each 1417 × 758 px. They are © Bank of England, marked CC BY-NC-ND 2.0, and "approved by the Bank of England for public use" under its reproduction conditions. They carry the Bank's SPECIMEN overprint, which has been removed (see *SPECIMEN removal* below). (On Flickr their titles are swapped: the image titled "£50 back" is the Turing side.)
- **Wikimedia Commons** was searched first. It has no usable image of the polymer £50. The only photographs are [File:Alan Turing £50 Banknote.jpg](https://commons.wikimedia.org/wiki/File:Alan_Turing_%C2%A350_Banknote.jpg) and a display panel next to it, both CC BY 4.0, by Vintage Fan 5678. They show only the Turing side, in a museum case, at an angle, through glass, so they were not used. The Bank's King Charles III £50 images are a front only (1920 px, [Flickr](https://www.flickr.com/photos/bankofengland/52573411731)) or 570 px web images. A King Charles III front would not match the available back, whose window shows the Queen, so the consistent Queen Elizabeth II pair is used.
- **Feature facts.** These come from the Bank of England's [£50 note page](https://www.bankofengland.co.uk/banknotes/polymer-50-pound-note): every security feature, the design features, the size (approximately 146 mm x 77 mm), the key dates and the artwork descriptions. The unveiling (25 March 2021), the two windows, the two-colour foil and Sarah John's signature come from [The new £50 note unveiled](https://www.bankofengland.co.uk/news/2021/march/the-new-50-note-unveiled). The UV position follows the Bank's UV feature photograph on the same page.
- **Fonts.** These are bundled in `fonts/`, all under the SIL Open Font License:
  - Bodoni Moda, for "£50", a Didone like the note's numerals.
  - UnifrakturMaguntia, a blackletter like the note's engraved "Bank of England".
  - Source Sans 3, Source Serif 4 and IBM Plex Mono.
- **Segment Anything** (facebook/sam-vit-large) and **Real-ESRGAN** (RealESRGAN_x2plus) were used for the masks and the upscale.

## SPECIMEN removal

The SPECIMEN overprint was removed from both sides with **LaMa** inpainting (Suvorov et al., *Resolution-robust Large Mask Inpainting with Fourier Convolutions*, 2022; the `big-lama` TorchScript model), run locally on the GPU:

- `tools/remove_specimen.py`: the LaMa model call, the band along each side's diagonal word, and boxes of real print to protect.
- `tools/unblend_specimen.py`: finds the letters of the overprint on the front (dark, grey pixels inside the band).
- `tools/remove_specimen_run.py`: the run for both sides. The back's letters are found as grey pixels darker than their own neighbourhood, because the print under the word there is itself dark. Each letter is masked separately (masking the whole band smeared the engraving). The printed "Fifty" and the promise line's lettering are protected. A second small pass cleans spots LaMa left grey or redrew.

The untouched images are kept as `source/<side>-levelled-specimen.png`. Then `tools/cutouts.py` rebuilds the artwork and every cut-out from the cleaned images.

What is left: inside the former letters, LaMa's reconstruction is slightly softer than the engraving around it, and on the front a faint trace remains beside "…NDS" of the promise line.

## Reproduction rules (Bank of England)

The Bank of England sets [reproduction conditions](https://www.bankofengland.co.uk/banknotes/using-images-of-banknotes) for all images of its notes. It is an offence to reproduce a Bank of England note, or part of one, without the Bank's consent (Forgery and Counterfeiting Act 1981, s.18). The Bank consents when its conditions are met, and no permission request is needed.

Digital reproductions on screen must meet conditions 3 and 4, and at least one of 5b and 5c:

- **Condition 3:** no offensive or inappropriate context.
- **Condition 4:** no distortion of the monarch's image, apart from enlargement, reduction or slant.
- **Condition 5b:** an image showing more than 50% of one side must be overprinted "SPECIMEN" in bold grey at 45° through the centre, at least 1/3 the note's length and 1/10 its height, unless the note is slanted more than 20°.
- **Condition 5c:** less than 50% of one side needs no overprint.

Physical reproductions must also be one-sided, at least 25% smaller or larger than actual size, and on a clearly different material.

How this page relates to them:

- **SPECIMEN overprint removed.** The Bank's specimen images carry a SPECIMEN overprint, which condition 5b requires on images like these. It has been removed at the project owner's request, so the page does not meet condition 5b as it stands: check with the Bank before publishing.
- **Cut-outs.** Each feature cut-out shows well under 50% of a side.
- **Bend and fold.** These views curve the note, which arguably distorts the monarch's image (condition 4).
- **Licence.** The CC BY-NC-ND licence on the Flickr images excludes derivatives. The upscale, cut-outs and the rebuilt hologram and UV states are derivatives.

Check both points with the Bank before publishing. Printing or saving the page as PDF prints a flat front covered by the EURion constellation.
