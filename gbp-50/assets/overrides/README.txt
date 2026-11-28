Hand-edited feature images go here. The extractor (tools/cutouts.py) never overwrites
this folder, and uses any file found here instead of its own result.

Name a file after the layer it replaces (same names as in assets/layers/):

  <side>-<feature>.png       the cut-out (highlight glow and exploded view)


  e.g.  front-crown.png  back-redfoil.png  back-table.png

Rules:
  - PNG with transparency (alpha). Transparent = not part of the feature.
  - Keep the same framing as the matching file in assets/layers/ (open that file, edit it,
    save it here under the same name). Size can differ; it is resized to fit the frame.
  - Run:  python tools/cutouts.py   (or just copy your file over the one in
    assets/layers/ to see it immediately; the copy here keeps it safe from the next run).
