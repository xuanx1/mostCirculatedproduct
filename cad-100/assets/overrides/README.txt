Hand-edited feature images go here. tools/cad_isolate.py never overwrites this folder, and uses any
file found here instead of its own result.

Name a file after the layer it replaces (same names as in assets/layers/), and give it the full
artwork size (2000 x 916, the same frame as cad-100-front.png / cad-100-back.png), e.g.

  front-mbuilding.png   back-dna.png   front-boc-en.png

Rules:
  - PNG with transparency (alpha). Transparent = not part of the feature.
  - Keep the feature where it sits on the full artwork; the script trims and frames it.
  - Run:  python tools/cad_isolate.py
