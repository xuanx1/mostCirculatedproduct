"""
Full rebuild of every generated layer, in order:
  python tools/extract_features.py      (feature-crops/, then everything below)
Steps after the box crops (also runnable alone: python tools/build.py):
  isolate_features  - edge-detected cut-outs, boxes.js, offset layers
  circle_cut        - the Governor's seal, an exact circle
  sam_isolate       - Segment Anything: portrait, lower-right 10000 plate (GPU)
  engrave_cut       - cartouche and Tokyo Station, cut along their engraving
  watermark         - portrait watermark + diamond pattern, bar pattern
  latent            - latent 10000 / NIPPON masks
  hologram          - the BOJ's views of the turning portrait
  pearl, uv_map     - pearl-ink bands, UV glow map
  masks.css         - effect masks as data URIs; then clean_assets.js drops unused layers
Hand-cleaned files in assets/overrides/ always win.
"""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def after_extract(sam=True):
    import isolate_features as IF, circle_cut, engrave_cut, watermark, latent, hologram, pearl, uv_map
    IF.main()
    for fid, (geom, kind) in circle_cut.SEALS.items():
        circle_cut.cut(fid, geom, kind)
    if sam:
        import sam_isolate, time
        # the GPU is shared with other jobs: hold the project-wide lock while SAM runs
        lock = os.path.join(os.path.dirname(os.path.dirname(HERE)), '.gpu-lock')
        while True:
            try:
                os.mkdir(lock); break
            except FileExistsError:
                time.sleep(15)
        try:
            sam_isolate.main()
        finally:
            os.rmdir(lock)
    engrave_cut.main()
    watermark.ghost(); watermark.bars()
    latent.front(); latent.back()
    hologram.main(); pearl.main(); uv_map.main()
    IF.write_mask_css()
    subprocess.run(['node', os.path.join(HERE, 'clean_assets.js')], check=False)


if __name__ == '__main__':
    after_extract(sam='--no-sam' not in sys.argv)
