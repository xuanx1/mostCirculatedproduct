Hand-edited feature images go here. The extractor (tools/extract_features.py) never overwrites
this folder, and uses any file found here instead of its own result.

Name a file after the layer it replaces (same names as in assets/layers/):

  <side>-<feature>.png       the ink / fill layer   (exploded view, see-through, text glows)
  <side>-<feature>-cut.png   the silhouette layer   (hover / select glow)

  e.g.  front-seal.png  front-seal-cut.png  front-latent-patch.png  back-lion-head.png

Rules:
  - PNG with transparency (alpha). Transparent = not part of the feature.
  - Keep the same framing as the matching file in assets/layers/ (open that file, edit it,
    save it here under the same name). Size can differ; it is resized to fit the frame.
  - Run:  python tools/extract_features.py   (or just copy your file over the one in
    assets/layers/ to see it immediately; the copy here keeps it safe from the next run).
