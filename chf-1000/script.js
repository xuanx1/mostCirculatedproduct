// FEATURES, TWEAK_DEFAULS, LAYERS and GLOW come from data.js (loaded first, as a plain script)

/* =====================================================================
   Geometry
   The note is portrait (70 × 158 mm), as the SNB shows both sides. The face
   is drawn at 640 × 1444 px and scaled by 0.5. Feature coordinates are in a
   320 × 722 "note space" (same as data.js), 1 unit = 1 px at scale 1.
   ===================================================================== */
const VW = 320, VH = 722;                       // note space
const NW = 640, NH = 1444;                      // face px: 70 x 158 mm, 1 : 2.257
const KY = NH / 2 / VH;                         // note units (y) -> on-screen px at scale 1
const UX = NW / VW, UY = NH / VH;               // note units → face px
const D2R = Math.PI / 180;
// layer boxes from assets/boxes.js; the page still works (with built-in boxes) if it is missing
const BX = (typeof BOXES !== 'undefined') ? BOXES : {};
const lastPtr = { x: -999, y: -999 };   // last pointer position (used by the cursor tag)
const pct = (x, y, w, h) => ({
  left: (x / VW * 100) + '%', top: (y / VH * 100) + '%',
  width: (w / VW * 100) + '%', height: (h / VH * 100) + '%',
});
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const smooth01 = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/* =====================================================================
   State
   ===================================================================== */
const REST = { rx: 0, ry: 0, rz: 0 };          // flat, facing front: the annotated view
const state = {
  view: 'front',
  rx: REST.rx, ry: REST.ry, rz: REST.rz,
  zoom: 1, tx: 0, ty: 0,
  drag: false, lastX: 0, lastY: 0,
  auto: false,
  active: new Set(TWEAK_DEFAULS.defaultActive),
  selected: null, hovered: null, showAll: false,
  zoomedFeature: null,
  seethrough: false,
  exploded: false, pinnedLayer: null,
  homeRy: REST.ry,          // pose the note was last presented in
  bend: 0,                  // user bend, degrees of arc across the note
};
const hover = { x: 0, y: 0, tx: 0, ty: 0, smoothUntil: 0 };
const spin = { target: null, v: 0, free: false };   // flip spring + release momentum
const ret = { on: false };                          // easing back to the neutral pose after inactivity
let baseX = 0, baseY = 0;                           // centres the note in the space the columns leave
const phys = { flex: 0, v: 0, fold: 0, foldT: 0, dragVel: 0, foldSide: 'right', lastFold: '' };
let fit = 1;

/* =====================================================================
   DOM
   ===================================================================== */
const $ = (id) => document.getElementById(id);
const stage = $('stage');
const noteWrap = $('noteWrap');
const note = $('note');
const frontFace = note.querySelector('.face.front');
const backFace = note.querySelector('.face.back');
const detailCard = $('detailCard');
const readout = $('angleReadout');
const cursorTag = $('cursorTag');
const zoomSlider = $('zoomSlider');
const bendSlider = $('bendSlider');
const featIndex = (id) => FEATURES.findIndex(f => f.id === id);
const featById = (id) => FEATURES.find(f => f.id === id);

/* =====================================================================
   Annotations: labels around the flat note, each with a needle to its
   feature. They live in the note's own 3D plane (so needles stay pinned
   during small tilts) and show only while the note lies flat.
   Anchors in note units; the back plane uses the reverse's own coordinates.
   ===================================================================== */
const ANNO = {
  // left column (x < 160): cross, microtext, tilt, hand, microperf, watermark; right: UV globe, globe, strip, register, tactile
  front: [['cross', 71, 63], ['microtext', 64, 196], ['tilt', 80, 344], ['hand', [[150, 200], [110, 616]]], ['microperf', 74, 484],
          ['watermark', [[97, 622], [218, 586]]],
          ['uv', 221, 93], ['tactile', [[314, 180], [314, 422]]], ['globe', 250, 380], ['strip', 276, 497], ['register', 194, 554]],
  back:  [['hand', [[97, 53], [33, 460]]], ['triangle', 64, 276], ['register', 131, 549],
          ['cross', 249, 63], ['serial', [[285, 280], [79, 524]]], ['watermark', [[223, 622], [102, 586]]]],
};
const annoEls = [];
// Labels are drawn in a flat 2D layer (crisp text, never rasterised inside the 3D note).
// Each label has one or more invisible anchor points on the note face; every frame their
// real on-screen positions are read back and a needle is drawn to each.
const SVGNS = 'http://www.w3.org/2000/svg';
function makeLayer(cls) {
  const el = document.createElement('div');
  el.className = cls;
  el.innerHTML = '<svg class="anno-lines"></svg>';
  document.body.appendChild(el);
  return el;
}
function makeAnchor(face, x, y) {
  const a = document.createElement('i');
  a.className = 'anchor';
  a.style.left = (x / VW * 100) + '%';
  a.style.top = (y / VH * 100) + '%';
  face.appendChild(a);
  return a;
}
// needles draw in, then fade out after 2 s (labels stay); hovering a label brings its needle back
let needleTimer = 0;
function restNeedlesLater() {
  document.body.classList.remove('needles-rest');
  clearTimeout(needleTimer);
  needleTimer = setTimeout(() => document.body.classList.add('needles-rest'), 2000);
}
// one label + a needle to every anchor
function makeItem(layer, side, pts, html, cls) {
  const face = side === 'front' ? frontFace : backFace;
  const anchors = pts.map(([x, y]) => makeAnchor(face, x, y));
  const b = document.createElement('button');
  b.className = `${cls} ${side}`;
  b.innerHTML = html;
  layer.appendChild(b);
  const g = document.createElementNS(SVGNS, 'g');
  g.setAttribute('class', `needle ${side}`);
  // each needle: a navy halo under the gold line, so it reads on the light note and the dark page alike
  g.innerHTML = pts.map(() => '<path class="halo" pathLength="1"/><circle class="ring-halo" r="7"/><path pathLength="1"/><circle class="ring" r="7"/><circle class="pin" r="2.6"/>').join('');
  layer.firstChild.appendChild(g);
  b.addEventListener('pointerenter', () => g.classList.add('peek'));
  b.addEventListener('pointerleave', () => g.classList.remove('peek'));
  const parts = pts.map((_, n) => [g.children[n * 5 + 2], g.children[n * 5 + 3], g.children[n * 5 + 4], g.children[n * 5], g.children[n * 5 + 1]]);
  return { side, x: pts.reduce((a, q) => a + q[0], 0) / pts.length, anchors, label: b, needle: g, parts };
}
const annoLayer = makeLayer('anno-layer');
const ANN = { front: [], back: [] };
['front', 'back'].forEach(side => {
  ANNO[side].forEach(([fid, ...rest]) => {
    const pts = Array.isArray(rest[0]) ? rest[0] : [[rest[0], rest[1]]];
    const f = featById(fid);
    const it = makeItem(annoLayer, side, pts,
      `<span class="n">${String(featIndex(fid) + 1).padStart(2, '0')}</span><span class="t">${f.name}</span>`, 'anno');
    it.fid = fid;
    it.label.dataset.f = fid; it.needle.dataset.f = fid;
    it.label.addEventListener('pointerenter', () => setHovered(fid));
    it.label.addEventListener('pointerleave', () => setHovered(null));
    it.label.addEventListener('click', () => selectFeature(fid));
    ANN[side].push(it);
    annoEls.push(it.label, it.needle);
  });
});
// needle route using only horizontal, vertical and 45° segments:
// out of the label horizontally, then a 45° run, then straight into the point
function octiPath(x0, y0, ax, ay) {
  const sx = Math.sign(ax - x0) || 1, sy = Math.sign(ay - y0) || 1;
  const dx = Math.abs(ax - x0), dy = Math.abs(ay - y0);
  const stub = Math.min(18, dx);
  if (dx - stub >= dy) {                          // wide: horizontal, then a 45° approach
    const hx = ax - sx * dy;
    return `M${x0} ${y0} H${hx.toFixed(1)} L${ax.toFixed(1)} ${ay.toFixed(1)}`;
  }
  const d = dx - stub;                            // tall: stub, 45° run, then vertical
  return `M${x0} ${y0} H${(x0 + sx * stub).toFixed(1)} L${ax.toFixed(1)} ${(y0 + sy * d).toFixed(1)} V${ay.toFixed(1)}`;
}
// lay out a set of items: labels in a column left/right of `region`, needles to their anchors
function layoutSet(items, region, opts) {
  const pts = items.map(it => {
    const a = it.anchors.map(el => { const r = el.getBoundingClientRect(); return [r.left, r.top]; });
    const ax = a.reduce((t, q) => t + q[0], 0) / a.length, ay = a.reduce((t, q) => t + q[1], 0) / a.length;
    return { it, a, ax, ay, lr: opts.side(it, ax) };
  });
  ['L', 'R'].forEach(lr => {
    const group = pts.filter(q => q.lr === lr).sort((a, b) => a.ay - b.ay);
    const n = group.length;
    let ys;
    if (opts.spread) {
      const top = region.top - 6, bottom = region.bottom + 6;
      ys = group.map((q, m) => n === 1 ? q.ay : top + m * (bottom - top) / (n - 1));
    } else {
      // keep each label level with its point, at least `gap` apart, inside the window
      const gap = opts.gap || 34;
      ys = group.map(q => q.ay);
      for (let m = 1; m < n; m++) ys[m] = Math.max(ys[m], ys[m - 1] + gap);
      const over = n ? ys[n - 1] - (window.innerHeight - 130) : 0;
      if (over > 0) for (let m = 0; m < n; m++) ys[m] -= over;
      for (let m = 0; m < n; m++) ys[m] = Math.max(ys[m], 130 + m * gap);
    }
    const xl = Math.max(opts.minX ?? -1e9, region.left - (opts.reach || 36));
    const xr = Math.min(opts.maxX ?? 1e9, region.right + (opts.reach || 36));
    group.forEach((q, m) => {
      const ly = Math.round(ys[m]);
      // keep the whole label on screen (left labels extend leftwards from lx, right ones rightwards)
      const lw = q.it.label.offsetWidth || 0;
      const lx = lr === 'L' ? Math.max(xl, lw + 16) : Math.min(xr, (opts.maxRight ?? window.innerWidth) - lw - 16);
      const x0 = lr === 'L' ? lx + 6 : lx - 6, x1 = lr === 'L' ? lx + 26 : lx - 26;
      q.a.forEach(([ax, ay], t) => {
        const [path, ring, pin, halo, ringHalo] = q.it.parts[t];
        const d = octiPath(x0, ly, ax, ay);
        path.setAttribute('d', d); halo.setAttribute('d', d);
        ring.setAttribute('cx', ax); ring.setAttribute('cy', ay);
        ringHalo.setAttribute('cx', ax); ringHalo.setAttribute('cy', ay);
        pin.setAttribute('cx', ax); pin.setAttribute('cy', ay);
      });
      const L = q.it.label;
      L.classList.toggle('L', lr === 'L'); L.classList.toggle('R', lr === 'R');
      L.style.left = Math.round(lx) + 'px';
      L.style.top = ly + 'px';
    });
  });
}
function layoutAnnotations() {
  const side = state.view === 'back' ? 'back' : 'front';
  annoLayer.dataset.side = side;
  const face = (side === 'front' ? frontFace : backFace).getBoundingClientRect();
  layoutSet(ANN[side], face, { spread: true, side: it => it.x < VW / 2 ? 'L' : 'R' });   // both faces read unmirrored on screen
}

/* Detail callouts: zoomed into a feature, its own needles and dots name its parts */
const detLayer = makeLayer('det-layer');
let detItems = [], detFor = null;
function buildDetails(fid) {
  if (detFor === fid) return;
  detItems.forEach(it => it.anchors.forEach(a => a.remove()));
  detLayer.querySelectorAll('.det').forEach(e => e.remove());
  detLayer.firstChild.innerHTML = '';
  detItems = (DETAILS[fid] || []).map(([side, pts, text]) =>
    makeItem(detLayer, side, pts, `<span class="d"></span><span class="t">${text}</span>`, 'det'));
  detFor = fid;
}
function layoutDetails() {
  const side = state.view === 'back' ? 'back' : 'front';
  detLayer.dataset.side = side;
  const vw = window.innerWidth, vh = window.innerHeight;
  const onScreen = el => { const r = el.getBoundingClientRect(); return r.left > 20 && r.left < vw - 20 && r.top > 20 && r.top < vh - 20; };
  detItems.forEach(it => { const v = it.side === side && it.anchors.every(onScreen); it.label.hidden = !v; it.needle.style.display = v ? '' : 'none'; });
  const items = detItems.filter(it => it.side === side && !it.label.hidden);
  if (!items.length) return false;
  const rs = items.flatMap(it => it.anchors.map(a => a.getBoundingClientRect()));
  const cx = rs.reduce((t, r) => t + r.left, 0) / rs.length;
  const region = { left: Math.min(...rs.map(r => r.left)) - 50, right: Math.max(...rs.map(r => r.left)) + 50,
                   top: Math.min(...rs.map(r => r.top)), bottom: Math.max(...rs.map(r => r.top)) };
  const colR = document.querySelector('.col-right').getBoundingClientRect();
  const maxX = (colR.left > window.innerWidth * 0.5 ? colR.left : window.innerWidth) - 250;
  layoutSet(items, region, {
    side: (it, ax) => (items.length === 1 ? ax < window.innerWidth / 2 : ax < cx) ? 'L' : 'R',
    gap: 36, reach: 90, minX: 260, maxX, maxRight: colR.left > window.innerWidth * 0.5 ? colR.left - 8 : window.innerWidth });
  return true;
}

/* =====================================================================
   Faces: veil, glow pieces, optics, glare
   ===================================================================== */
function place(el, box) { Object.assign(el.style, pct(...box)); return el; }

// Spotlight veil + glow layer on each face
const glowPieces = [];
// text and drawn layers glow along their own strokes (their ink image), shapes along their silhouette (-cut)
const TEXT_GLOW = new Set(['watermark-ghost', 'front-tactile', 'front-microtext', 'front-register', 'back-register', 'back-serial-a', 'back-serial-b', 'front-bankname', 'back-bankname', 'front-uvglobe', 'front-microperf', 'front-tilt']);
[frontFace, backFace].forEach(face => {
  const veil = document.createElement('div');
  veil.className = 'veil';
  face.appendChild(veil);
  const layer = document.createElement('div');
  layer.className = 'glow-layer';
  face.appendChild(layer);
  face._glow = layer;
});
// largest first, so small features sit on top and stay hoverable
Object.entries(GLOW)
  .flatMap(([fid, ps]) => ps.map(p => ({ fid, ...p })))
  .sort((a, b) => b.box[2] * b.box[3] - a.box[2] * a.box[3])
  .forEach(p => {
    const img = document.createElement('img');
    img.className = 'glow-piece' + (p.mirror ? ' mirror' : '');
    // shapes glow along their detected silhouette; text glows along its own strokes (no paper margin)
    img.src = p.src.endsWith('.svg') ? `assets/layers/${p.src}`
      : TEXT_GLOW.has(p.src) ? `assets/layers/${p.src}.png` : `assets/layers/${p.src}-cut.png`;
    img.alt = '';
    img.draggable = false;
    img.dataset.f = p.fid;
    if (p.fid === 'uv') img.style.pointerEvents = 'none';   // shares shapes with other features
    place(img, p.box);
    img.addEventListener('pointerenter', () => {
      if (state.drag) return;
      setHovered(p.fid);
      if (!document.body.classList.contains('annotate')) showTag(p.fid);   // the label already names it
    });
    img.addEventListener('pointerleave', () => { setHovered(null); hideTag(); });
    (p.side === 'front' ? frontFace : backFace)._glow.appendChild(img);
    glowPieces.push(img);
  });

// Optical-effect overlays, each clipped to its real print or foil (masks in assets/masks.css, or the
// feature's own shape). A masked element blends as one group, so every effect is its own element.
const OPTICS = {
  // globe test: a golden arc moves across the globe as the note tilts left-right; tilted backwards
  // the globe changes colour (a hue-shifted copy of the globe itself fades in)
  globe: [['optic globe-fx', '<img class="shift" src="assets/layers/front-globe-cut.png" alt="" draggable="false"><i class="arc"></i>']],
  // security strip: red and green numbers on four lines, moving in opposite directions (left-right
  // tilt); the silver map and 1000 turn to rainbow colours when the note is tilted backwards
  strip: [['optic strip-fx', '<i class="rainbow"></i><div class="rows"><b class="r1"></b><b class="r2"></b><b class="r3"></b><b class="r4"></b></div>']],
  // tilt effect: the Swiss cross at C stands out only when the note is tilted backwards
  tilt:  [['optic tilt-fx', '<img src="assets/layers/front-tilt.png" alt="" draggable="false">']],
  // triangle: the thread glitters in its window as the light moves over it
  triangle: [['optic tri-fx', '<i></i>']],
};
const OPTIC_BOX = {               // note units, from assets/boxes.js (same frames as the masks)
  globe: BX['front-globe'] || [150, 329, 143, 143], strip: BX['front-strip'] || [0, 449, 320, 70],
  tilt: BX['front-tilt'] || [32, 323, 93, 43], triangle: [40, 266, 50, 22],
};
const OPTIC_SIDE = { globe: 'front', strip: 'front', tilt: 'front', triangle: 'back' };
function mkOptics(container, id, px) {
  return OPTICS[id].map(([cls, html]) => {
    const el = document.createElement('div');
    el.className = cls;
    el.dataset.opt = id;
    if (html) el.innerHTML = html;
    if (px) Object.assign(el.style, px); else place(el, OPTIC_BOX[id]);
    container.appendChild(el);
    return el;
  });
}
const opticEls = {};
Object.keys(OPTICS).forEach(id => {
  opticEls[id] = mkOptics(OPTIC_SIDE[id] === 'front' ? frontFace : backFace, id);
});
// gold flow: a gold sweep masked to the note's own engraved line-work (masks in assets/masks.css)
[frontFace, backFace].forEach((f, n) => {
  const d = document.createElement('div');
  d.className = 'flow ' + (n ? 'flow-back' : 'flow-front');
  d.innerHTML = '<i></i>';
  f.insertBefore(d, f.querySelector('.glow-layer'));
});
const glares = [frontFace, backFace].map(f => {
  const g = document.createElement('div');
  g.className = 'glare' + (f === backFace ? ' back' : '');
  g.innerHTML = '<i></i>';
  f.appendChild(g);
  return g;
});
// optic variables are written only to the elements that read them (not the whole note),
// so a frame doesn't restyle hundreds of strips, layers and glow pieces
let opticTargets = [...frontFace.querySelectorAll('.optic'), ...backFace.querySelectorAll('.optic')];

/* =====================================================================
   Bendable note: the face is rebuilt as vertical strips, each set at its
   own angle along a curve. Each strip has its own lighting and its own
   copy of the optics, so a bent note shows the colour-shift running
   across the curve. Used whenever the paper is bent or folded; the flat
   note uses the full faces above.
   ===================================================================== */
const N = 64, SW = NW / N, OVER = 2;      // overlap hides seams between strips
const GHOST_BOX = BX['watermark-ghost'] || [62, 526, 216, 132];   // the flag (left) and globe (right) watermarks, position E
const GHOST_BOX_BACK = [VW - GHOST_BOX[0] - GHOST_BOX[2], GHOST_BOX[1], GHOST_BOX[2], GHOST_BOX[3]];   // in the paper: mirrored on the reverse
const WM_PATCH_BACK = [0, 0, 0, 0];                         // (no printed watermark to cover on this artwork)
const stripsEl = document.createElement('div');
stripsEl.className = 'strips';
stripsEl.style.setProperty('--sw', SW + 'px');
stripsEl.style.setProperty('--ov', OVER + 'px');
note.appendChild(stripsEl);
const strips = [];
const toPx = ([x, y, w, h]) => [x * UX, y * UY, w * UX, h * UY];
const overlaps = (X, Wp, s0) => X < s0 + SW + OVER && X + Wp > s0;
for (let i = 0; i < N; i++) {
  const s = i * SW, r0 = NW - s - SW;
  const el = document.createElement('div');
  el.className = 'strip';
  el.style.width = (SW + OVER) + 'px';
  const sf = document.createElement('div');
  sf.className = 'sf';
  sf.style.backgroundPosition = `${-s}px 0`;
  const sb = document.createElement('div');
  sb.className = 'sb';
  sb.style.backgroundPosition = `${-(r0 - OVER)}px 0`;   // local x 0 sits on the overlap, past the strip edge
  if (i === 0) { sf.classList.add('first'); sb.classList.add('first'); }
  if (i === N - 1) { sf.classList.add('last'); sb.classList.add('last'); }
  // rebuilt ghost portrait on the front
  const [gx, gy, gw, gh] = toPx(GHOST_BOX);
  if (overlaps(gx, gw, s)) {
    const g = document.createElement('div');
    g.className = 'ghost-fix';
    Object.assign(g.style, { left: (gx - s) + 'px', top: gy + 'px', width: gw + 'px', height: gh + 'px' });
    g.innerHTML = '<img src="assets/layers/watermark-ghost.png" alt="" draggable="false">';
    sf.appendChild(g);
  }
  const [bx, by, bw, bh] = toPx(GHOST_BOX_BACK);
  if (overlaps(bx, bw, r0)) {
    const p = document.createElement('div');
    p.className = 'wm-patch';
    const [px, py, pw, ph] = toPx(WM_PATCH_BACK);
    Object.assign(p.style, { left: (px - r0) + 'px', top: py + 'px', width: pw + 'px', height: ph + 'px' });
    const g = document.createElement('div');
    g.className = 'ghost-fix mirror';
    Object.assign(g.style, { left: (bx - r0) + 'px', top: by + 'px', width: bw + 'px', height: bh + 'px' });
    g.innerHTML = '<img src="assets/layers/watermark-ghost.png" alt="" draggable="false">';
    sb.append(p, g);
  }
  let hasOptics = false;
  Object.keys(OPTICS).forEach(id => {
    const [X, Y, Wp, Hp] = toPx(OPTIC_BOX[id]);
    const front = OPTIC_SIDE[id] === 'front';
    const origin = front ? s : r0;
    if (!overlaps(X, Wp, origin)) return;
    hasOptics = true;
    mkOptics(front ? sf : sb, id, { left: (X - origin) + 'px', top: Y + 'px', width: Wp + 'px', height: Hp + 'px' });
  });
  sf.insertAdjacentHTML('beforeend', '<i class="shade"></i><i class="hi"></i>');
  sb.insertAdjacentHTML('beforeend', '<i class="shade"></i><i class="hi"></i>');
  el.append(sf, sb);
  stripsEl.appendChild(el);
  strips.push({ el, s, hasOptics });
}
const strip_th = new Float64Array(N + 1);       // angle at each strip boundary
const LIGHT = (() => { const v = [-0.3, -0.5, 0.81]; const m = Math.hypot(...v); return v.map(c => c / m); })();
const HALF = (() => { const v = [LIGHT[0], LIGHT[1], LIGHT[2] + 1]; const m = Math.hypot(...v); return v.map(c => c / m); })();
function normal(rxDeg, ryDeg) {
  const a = rxDeg * D2R, b = ryDeg * D2R;
  return [Math.sin(b), -Math.sin(a) * Math.cos(b), Math.cos(a) * Math.cos(b)];
}
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
function lightAt(n) {                         // [diffuse, specular] for a face normal
  return [dot(n, LIGHT), Math.pow(Math.max(0, dot(n, HALF)), 26)];
}
function isBent() { return note.classList.contains('bent'); }
function updateBentMode() {
  const amt = Math.abs(state.bend + phys.flex) + Math.abs(phys.fold);
  const on = !state.exploded && (isBent() ? amt > 0.4 : amt > 2.5);
  if (on !== isBent()) note.classList.toggle('bent', on);
  return on;
}
function renderStrips(rx, ry) {
  const B = (state.bend + phys.flex) * D2R;
  const F = phys.fold * D2R;
  const k = B / NW, c = NW / 2, hinge = SW * 2.2;
  // fold: either half swings about the centre crease (F > 0 toward the viewer, < 0 away)
  const left = phys.foldSide === 'left';
  const th = (s) => k * (s - c) + (left ? -F * (1 - smooth01(c - hinge, c + hinge, s))
                                       : F * smooth01(c - hinge, c + hinge, s));
  for (let j = 0; j <= N; j++) strip_th[j] = th(j * SW);
  // lay strips end to end along the curve (arc length is preserved)
  const P = new Float64Array((N + 1) * 2);
  const mid = new Float64Array(N);
  for (let i = 0; i < N; i++) {
    const t = th(i * SW + SW / 2);
    mid[i] = t;
    P[(i + 1) * 2] = P[i * 2] + SW * Math.cos(t);
    P[(i + 1) * 2 + 1] = P[i * 2 + 1] + SW * Math.sin(t);
  }
  // anchor: centre for a bend, the left half's middle as the fold closes
  const ff = Math.min(1, Math.abs(phys.fold) / 60);
  const sA = c + (left ? 1 : -1) * (NW / 4) * ff;      // the half that stays put
  const ia = Math.min(N - 1, Math.floor(sA / SW)), da = sA - ia * SW;
  const ax = P[ia * 2] + da * Math.cos(mid[ia]), az = P[ia * 2 + 1] + da * Math.sin(mid[ia]);
  const ox = (sA + (c - sA) * ff) - ax, oz = -az;   // folded half ends up centred
  // lighting relative to the flat note, so a flat strip looks identical to the face
  const n0 = normal(rx, ry);
  const [d0, s0] = lightAt(n0);
  const [bd0, bs0] = lightAt(n0.map(v => -v));
  const shadeF = [], hiF = [], shadeB = [], hiB = [];
  for (let j = 0; j <= N; j++) {
    const n = normal(rx, ry - strip_th[j] / D2R);
    const [d, sp] = lightAt(n);
    const [bd, bsp] = lightAt(n.map(v => -v));
    shadeF[j] = clamp((d0 - d) * 1.25, 0, 0.72).toFixed(3);
    hiF[j] = clamp((sp - s0) * 0.9, 0, 0.6).toFixed(3);
    shadeB[j] = clamp((bd0 - bd) * 1.25, 0, 0.72).toFixed(3);
    hiB[j] = clamp((bsp - bs0) * 0.9, 0, 0.6).toFixed(3);
  }
  for (let i = 0; i < N; i++) {
    const st = strips[i], es = st.el.style;
    es.transform = `translate3d(${(P[i * 2] + ox).toFixed(2)}px,0,${(P[i * 2 + 1] + oz).toFixed(2)}px) rotateY(${(-mid[i]).toFixed(5)}rad)`;
    es.setProperty('--s0', shadeF[i]); es.setProperty('--s1', shadeF[i + 1]);
    es.setProperty('--h0', hiF[i]);    es.setProperty('--h1', hiF[i + 1]);
    es.setProperty('--b0', shadeB[i + 1]); es.setProperty('--b1', shadeB[i]);   // back face runs right→left
    es.setProperty('--bh0', hiB[i + 1]);   es.setProperty('--bh1', hiB[i]);
    if (st.hasOptics) applyOpticVars(es, rx, ry - mid[i] / D2R);
  }
}

/* =====================================================================
   Optical model
   Surface normal from the effective rotation (n = Rx·Ry·ẑ, as CSS
   rotateX() rotateY()). Every effect is a pure function of that angle —
   nothing loops on a timer — so features only change when the note moves.
   ===================================================================== */
function opticValues(rxDeg, ryDeg) {
  const [nx, ny, nz] = normal(rxDeg, ryDeg);
  const theta = Math.acos(Math.min(1, Math.abs(nz))) / D2R;     // viewing angle off the normal
  const ry = ((ryDeg + 540) % 360) - 180;                        // left-right tilt relative to face-on (either side)
  const rr = Math.abs(ry) > 90 ? (ry > 0 ? 180 - ry : -180 - ry) : ry;
  return {
    theta, nx, ny,
    vars: [
      // golden arc: slides across the globe with left-right tilt (ry)
      ['--arc-x', (clamp(rr * 9, -100, 100)).toFixed(1) + '%'],
      ['--arc-a', (0.25 + 0.75 * smooth01(0.5, 6, Math.abs(rr))).toFixed(3)],
      // tilted backwards (top edge away, rx > 0): the globe's colour changes; the strip's silver
      // print turns to rainbow; the tilt-effect cross stands out
      ['--back-t', smooth01(3, 10, rxDeg).toFixed(3)],
      ['--rainbow-x', (50 + rxDeg * 6 + rr * 2).toFixed(1) + '%'],
      // strip numbers: appear with left-right tilt, alternate lines move in opposite directions
      ['--rows-a', smooth01(1, 6, Math.abs(rr)).toFixed(3)],
      ['--rows-x', (rr * 1.6).toFixed(2) + '%'],
      ['--rows-nx', (-rr * 1.6).toFixed(2) + '%'],
      // thread glitter in the triangle: glints slide with the light
      ['--glint-x', (50 + nx * 260 - ny * 120).toFixed(1) + '%'],
      ['--glint-a', (0.35 + 0.65 * smooth01(1, 10, theta)).toFixed(3)],
    ],
  };
}
// write a CSS variable only when its value changed: an unchanged write still invalidates style
const varCache = new WeakMap();
function setVar(el, k, v) {
  let c = varCache.get(el);
  if (!c) { c = {}; varCache.set(el, c); }
  if (c[k] === v) return;
  c[k] = v;
  el.style.setProperty(k, v);
}
function applyOpticVars(style, rx, ry) {
  for (const [k, v] of opticValues(rx, ry).vars) style.setProperty(k, v);
}
let lastReadout = '', lastWm = '', ghostImgs = null;
function updateOptics(rx, ry) {
  const o = opticValues(rx, ry);
  for (const el of opticTargets) for (const [k, val] of o.vars) setVar(el, k, val);
  // glare: light just above-left of the viewer; the highlight slides opposite to the normal.
  // Moved with a transform (compositor only) instead of repainting a gradient every frame.
  const gx = 38 - o.nx * 150, gy = 30 - o.ny * 150;
  const spec = Math.max(0, 1 - Math.hypot(gx - 50, gy - 50) / 110);
  glares[0].firstChild.style.transform = `translate(${(gx - 50).toFixed(1)}%, ${(gy - 50).toFixed(1)}%)`;
  glares[1].firstChild.style.transform = `translate(${(50 - gx).toFixed(1)}%, ${(gy - 50).toFixed(1)}%)`;
  glares[0].style.opacity = glares[1].style.opacity = (0.3 + spec * 0.7).toFixed(2);
  // watermarks (flag and globe, in the paper): barely there in reflected light (2% face-on, 9% tilted);
  // held up to the light they show clearly
  const wm = note.classList.contains('seethrough') ? '0.85' : (0.02 + 0.07 * smooth01(2, 10, o.theta)).toFixed(3);
  if (wm !== lastWm) {
    lastWm = wm;
    if (!ghostImgs) ghostImgs = [...note.querySelectorAll('.ghost-fix img')];
    for (const g of ghostImgs) g.style.opacity = wm;
  }
  const r = `${o.theta.toFixed(0)}°`;
  if (readout && r !== lastReadout) { readout.textContent = r; lastReadout = r; }
  return o.theta;
}

/* =====================================================================
   Transform
   ===================================================================== */
function computeFit() {
  const vw = window.innerWidth, vh = window.innerHeight;
  const R = document.querySelector('.col-right').getBoundingClientRect();
  const edge = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--edge')) || 40;
  // the detail column sits beside the note on wide screens, and below it (as a sheet) on narrow ones
  const beside = R.left > vw * 0.55 && R.top < vh * 0.5;
  const right = beside ? R.left - 24 : vw - edge;
  const regionW = right - edge;
  const labels = vw > 820 ? 460 : 40;                       // room for a column of labels each side
  const top = document.querySelector('.masthead').getBoundingClientRect().bottom + 16;
  const bottom = beside ? vh - 104 : Math.min(vh - 104, R.top - 16);
  const availH = Math.max(160, bottom - top);
  // the note stands upright (70 x 158 mm, as the SNB shows it): its height decides the fit
  fit = clamp(Math.min(regionW / (NW / 2 + 40 + labels), availH / (NH / 2 + 24)), 0.3, 1.25);
  baseX = (edge + regionW / 2) - vw / 2;
  baseY = (top + availH / 2) - vh / 2;
}
function applyTransform(smooth) {
  const rx = state.rx + hover.y;
  const ry = state.ry + hover.x;
  const wobble = state.exploded ? 0 : Math.sin(ry * D2R) * 2;
  noteWrap.style.transition = smooth ? 'transform .8s cubic-bezier(.4,1.2,.4,1)'
    : (performance.now() < hover.smoothUntil ? noteWrap.style.transition : 'none');   // let a running zoom finish
  if (smooth) hover.smoothUntil = performance.now() + 800;
  const centred = document.body.classList.contains('intro');
  const bx = state.exploded ? 60 : (centred ? 0 : baseX);
  noteWrap.style.transform =
    `translate(${state.tx + bx}px, ${state.ty + (state.exploded || centred ? 0 : baseY)}px) rotateX(${rx}deg) rotateY(${ry}deg) rotateZ(${state.rz + wobble}deg) scale3d(${state.zoom * fit}, ${state.zoom * fit}, ${state.zoom * fit})`;   // 3D: depth scales with width
  const theta = updateOptics(rx, ry);
  const fromBack = Math.cos(ry * D2R) * Math.cos(rx * D2R) < 0;
  if (note.classList.contains('from-back') !== fromBack) note.classList.toggle('from-back', fromBack);
  const bent = updateBentMode();
  if (bent) renderStrips(rx, ry);
  const nb = normal(state.rx, state.ry);                // resting pose: hover tilt never hides the labels
  const restTheta = Math.acos(Math.min(1, Math.abs(nb[2]))) / D2R;
  // no labels until the intro is over and the note has reached its final position
  const annotate = !document.body.classList.contains('intro') && !document.body.classList.contains('intro-settle') && !state.exploded && !note.classList.contains('collapsing') && !bent && restTheta < 13 && state.zoom <= 1.15 && !state.zoomedFeature
    && !state.auto && !state.drag && spin.target === null && !spin.free
    && Math.hypot(state.tx, state.ty) < 40;          // panned away: labels would collide with the columns
  if (annotate !== document.body.classList.contains('annotate')) restNeedlesLater();
  document.body.classList.toggle('annotate', annotate);
  if (annotate) layoutAnnotations();
  // zoomed into a feature, and the camera has arrived: show its detail callouts
  const detailing = !!state.zoomedFeature && !state.drag && !state.exploded && !bent
    && performance.now() >= hover.smoothUntil;
  if (detailing && !document.body.classList.contains('detailing')) restNeedlesLater();
  if (detailing) { buildDetails(state.zoomedFeature); document.body.classList.toggle('detailing', layoutDetails()); }
  else document.body.classList.remove('detailing');
  document.body.classList.toggle('zoomed', state.zoom > 1.15);
}

/* =====================================================================
   Animation loop: pointer tilt, paper flex (a damped spring driven by
   how fast the note is moving), fold, auto-rotate
   ===================================================================== */
let raf = 0;
function kick() { if (!raf) raf = requestAnimationFrame(tick); }
function tick() {
  raf = 0;
  hover.x += (hover.tx - hover.x) * 0.14;
  hover.y += (hover.ty - hover.y) * 0.14;
  const lag = hover.tx - hover.x;
  // paper flex comes from flips and flick momentum only, never from just moving the pointer
  const target = (reduceMotion || state.exploded) ? 0 : clamp(phys.dragVel, -26, 26);
  phys.dragVel *= 0.86;
  phys.v += (target - phys.flex) * 0.15;
  phys.v *= 0.8;
  phys.flex += phys.v;
  phys.fold += (phys.foldT - phys.fold) * 0.09;
  // idle return: ease everything back to neutral (ry is handled by the flip spring)
  if (ret.on) {
    const e = 0.08;
    state.rx += -state.rx * e; state.rz += -state.rz * e;
    state.tx += -state.tx * e; state.ty += -state.ty * e;
    state.zoom += (1 - state.zoom) * e; state.bend += -state.bend * e;
    zoomSlider.value = Math.round(state.zoom * 100); bendSlider.value = Math.round(state.bend);
    if (Math.abs(state.rx) + Math.abs(state.rz) + Math.abs(state.tx) + Math.abs(state.ty)
        + Math.abs(state.zoom - 1) * 100 + Math.abs(state.bend) < 0.3 && spin.target === null) {
      Object.assign(state, { rx: 0, rz: 0, tx: 0, ty: 0, zoom: 1, bend: 0 });
      ret.on = false;
    }
  }
  // flip: a spring toward the target angle; the paper flexes against the turn
  if (spin.target !== null) {
    spin.v = (spin.v + (spin.target - state.ry) * 0.075) * 0.8;
    state.ry += spin.v;
    phys.dragVel = clamp(-spin.v * 2.4, -28, 28);
    if (Math.abs(spin.target - state.ry) < 0.05 && Math.abs(spin.v) < 0.05) {
      state.ry = spin.target; spin.target = null; spin.v = 0;
    }
    syncSide();
  } else if (spin.free) {
    // released drag carries on and slows down
    state.ry += spin.v;
    spin.v *= 0.93;
    phys.dragVel = clamp(-spin.v * 0.9, -8, 8);
    if (Math.abs(spin.v) < 0.03) { spin.free = false; spin.v = 0; state.homeRy = state.ry; }
    syncSide();
  }
  if (state.auto) {
    state.ry += 0.3;
    const norm = ((state.ry % 360) + 360) % 360;
    if (state.view !== 'uv') {
      const v = (norm > 90 && norm < 270) ? 'back' : 'front';
      if (v !== state.view) { state.view = v; syncUI(); }
    }
  }
  const settled = !state.auto && spin.target === null && !spin.free && !ret.on
    && Math.abs(hover.tx - hover.x) < 0.02 && Math.abs(hover.ty - hover.y) < 0.02
    && Math.abs(phys.v) < 0.01 && Math.abs(target - phys.flex) < 0.02
    && Math.abs(phys.foldT - phys.fold) < 0.05 && Math.abs(phys.dragVel) < 0.02;
  if (settled) {
    hover.x = hover.tx; hover.y = hover.ty;
    phys.flex = target; phys.v = 0; phys.fold = phys.foldT; phys.dragVel = 0;
  }
  if (performance.now() < hover.smoothUntil) {
    // a smooth (.8s) move is running: keep the optics and paper live without cancelling it
    const rx = state.rx + hover.y, ry = state.ry + hover.x;
    updateOptics(rx, ry);
    if (updateBentMode()) renderStrips(rx, ry);
  } else {
    applyTransform();
  }
  if (!settled) raf = requestAnimationFrame(tick);
}

/* =====================================================================
   Selection, hover, glow
   ===================================================================== */
function setHovered(id) {
  if (state.hovered === id) return;
  state.hovered = id;
  updateGlow();
}
function updateGlow() {
  const lit = (fid) => state.showAll || fid === state.hovered || fid === state.selected;
  glowPieces.forEach(p => {
    p.classList.toggle('lit', lit(p.dataset.f));
    p.classList.toggle('sel', p.dataset.f === state.selected);
  });
  note.classList.toggle('spot', !!(state.selected || state.hovered) && !state.showAll);
  annoEls.forEach(el => el.classList.toggle('on', lit(el.dataset.f)));
  note.classList.toggle('gold-flow', lit('hand'));       // a lilac light running through the engraved line-work
  note.querySelectorAll('.optic').forEach(o => o.classList.toggle('keep', lit(o.dataset.opt)));
}
function selectFeature(id) {
  if (state.exploded) {
    state.selected = id;
    focusLayer(LAYERS.find(l => l.feature === id)?.id || null, true);
    syncUI();
    return;
  }
  if (state.selected === id) { deselect(); return; }
  if (!featById(id)?.light) state.seethrough = false;
  state.selected = id;
  if (id === 'uv' && state.view !== 'uv') state.view = 'uv';   // the UV globe can only be seen under the lamp
  zoomToFeature(featById(id));
  syncUI();
}
function deselect() {
  state.selected = null;
  state.seethrough = false;
  if (state.zoomedFeature) resetZoom();
  syncUI();
}
function showTag(fid) {
  const f = featById(fid);
  cursorTag.style.transform = `translate(${lastPtr.x + 18}px, ${lastPtr.y + 14}px)`;
  cursorTag.innerHTML = `<span class="n">${String(featIndex(fid) + 1).padStart(2, '0')}</span>${f.name}`;
  cursorTag.classList.add('on');
}
function hideTag() { cursorTag.classList.remove('on'); }
document.addEventListener('pointermove', (e) => {
  lastPtr.x = e.clientX; lastPtr.y = e.clientY;
  if (cursorTag.classList.contains('on')) {
    cursorTag.style.transform = `translate(${e.clientX + 18}px, ${e.clientY + 14}px)`;
  }
});

/* =====================================================================
   Detail panel
   ===================================================================== */
function renderDetail() {
  const f = state.selected && featById(state.selected);
  if (!f) {
    // the overview follows the view: obverse, reverse or ultraviolet
    const OVERVIEW = {
      back: `
      <p class="d-eyebrow">Overview · Reverse</p>
      <h2>Parliament and <em>an open network.</em></h2>
      <p class="d-desc">On the back, Switzerland’s communicative side is represented by depictions of the
        country’s parliament, a forum for public debate, and an open network. Below the large 1000 is the
        triangle with its glittering thread; the serial number is printed twice, in two different fonts.</p>
      <dl class="facts">
        <div><dt>Motif</dt><dd>Parliament and an open network<small>a forum for public debate</small></dd></div>
        <div><dt>Triangle</dt><dd>A glittering security thread<small>a continuous line against the light</small></dd></div>
        <div><dt>Serial</dt><dd>One letter, nine numbers<small>printed twice, in different fonts</small></dd></div>
        <div><dt>Language</dt><dd>Tausend Franken · Milli Francs<small>German and Romansh on this side</small></dd></div>
      </dl>
`,
      uv: `
      <p class="d-eyebrow">Overview · Ultraviolet</p>
      <h2>Under the lamp, <em>a second globe.</em></h2>
      <p class="d-desc">Under ultraviolet light a globe that cannot be seen in daylight shows up brightly at the
        top right of the front, while the background remains dull. Flecks in the paper of both sides light up
        in different colours.</p>
      <dl class="facts">
        <div><dt>Globe</dt><dd>Top right of the front<small>visible only under UV</small></dd></div>
        <div><dt>Fibres</dt><dd>All over both sides<small>in different colours</small></dd></div>
        <div><dt>Infrared</dt><dd>Both sides<small>under an infrared camera some elements turn monochrome, others disappear</small></dd></div>
      </dl>
`,
    };
    detailCard.innerHTML = (OVERVIEW[state.view] || `
      <p class="d-eyebrow">Overview</p>
      <h2>CHF 1000. <em>The hands.</em></h2>
      <p class="d-desc">The highest denomination of the Swiss National Bank’s ninth series, issued on
        13 March 2019. Its theme is Switzerland’s communicative flair, with language as the key motif:
        a handshake on the front signifies interpersonal communication, and the symbols over the globe
        come from the phonetic alphabet.</p>
      <dl class="facts">
        <div><dt>Issued</dt><dd>13 March 2019<small>the fifth denomination of the ninth series</small></dd></div>
        <div><dt>Front</dt><dd>Handshake and globe<small>Mille Francs · Mille Franchi</small></dd></div>
        <div><dt>Back</dt><dd>Parliament and an open network<small>Tausend Franken · Milli Francs</small></dd></div>
        <div><dt>Substrate</dt><dd>Durasafe®, three layers<small>paper, polymer, paper</small></dd></div>
        <div><dt>Colour</dt><dd>Purple</dd></div>
        <div><dt>Size</dt><dd>70 × 158 mm<small>this page shows the specimen published by the SNB</small></dd></div>
      </dl>
`) + `
      <ul class="gestures">
        <li><kbd>Move</kbd><span>tilt the note toward the light</span></li>
        <li><kbd>Drag</kbd><span>rotate it</span><kbd>Right-drag</kbd><span>pan</span></li>
        <li><kbd>Drag an edge</kbd><span>bend the paper</span></li>
        <li><kbd>G</kbd><span>fold</span><kbd>E</kbd><span>explode</span><kbd>F</kbd><span>flip</span></li>
      </ul>`;
    return;
  }
  const i = featIndex(f.id);
  const extra = f.light
    ? `<button class="d-action" id="seeThroughBtn" aria-pressed="${state.seethrough}">
         ${state.seethrough ? 'Lower from the light' : 'Hold up to the light'}</button>` : '';
  detailCard.innerHTML = `
    <p class="d-eyebrow"><span class="n">${String(i + 1).padStart(2, '0')}</span> / ${String(FEATURES.length).padStart(2, '0')}</p>
    <h2>${f.name}</h2>
    <p class="d-short">${f.short}</p>
    <p class="d-desc">${f.desc}</p>
    <section class="d-how"><h3>How to check</h3><p>${f.how}</p></section>
    ${extra}
    <button class="d-back" id="detailBack">← All features</button>`;
  const stb = $('seeThroughBtn');
  if (stb) stb.addEventListener('click', () => { state.seethrough = !state.seethrough; syncUI(); });
  $('detailBack').addEventListener('click', deselect);
}

/* =====================================================================
   syncUI
   ===================================================================== */
function syncUI() {
  renderDetail();
  document.querySelectorAll('#viewSeg button').forEach(b => b.classList.toggle('active', b.dataset.view === state.view));

  if (state.view === 'uv') state.active.add('uv');
  const uv = state.view === 'uv';
  note.classList.toggle('uv', uv);
  document.body.classList.toggle('uv', uv);
  applyUv(uv);

  Object.keys(OPTICS).forEach(id => {
    const on = state.active.has(id);
    note.querySelectorAll(`[data-opt="${id}"]`).forEach(el => { el.style.display = on ? '' : 'none'; });
  });

  const seethroughOn = state.seethrough && !!featById(state.selected)?.light && state.view !== 'uv';
  note.classList.toggle('seethrough', seethroughOn);
  document.body.classList.toggle('seethrough', seethroughOn);
  lastWm = '';                                       // the watermark opacity follows at once

  $('allBtn').setAttribute('aria-pressed', state.showAll);
  updateGlow();
  applyTransform();
}

/* =====================================================================
   Camera moves
   ===================================================================== */
function zoomToFeature(f) {
  const side = state.view === 'back' ? 'back' : 'front';
  const pieces = GLOW[f.id] || [];
  // the thread is not selectable on the obverse (it only shows there when tilted): examine it on the reverse
  const p = pieces.find(x => x.side === side) || pieces[0];
  if (!p) return;
  if (p.side === 'back' && state.view !== 'back') { state.ry += 180; state.view = 'back'; }
  else if (p.side === 'front' && state.view === 'back') { state.ry += 180; state.view = 'front'; }
  // frame everything this feature has on this side: its pieces and its detail points
  const boxes = pieces.filter(q => q.side === p.side).map(q => q.box);
  (DETAILS[f.id] || []).filter(d => d[0] === p.side).forEach(d => d[1].forEach(([px, py]) => boxes.push([px - 6, py - 6, 12, 12])));
  const x = Math.min(...boxes.map(b => b[0])), y = Math.min(...boxes.map(b => b[1]));
  const w = Math.max(...boxes.map(b => b[0] + b[2])) - x, h = Math.max(...boxes.map(b => b[1] + b[3])) - y;
  const cx = x + w / 2, cy = y + h / 2;
  const S = stage.getBoundingClientRect();
  // room left for the callouts either side; a wide spread (e.g. both serials) stays near 1x
  const z = clamp(Math.min((S.width * 0.4) / (w * fit), (S.height * 0.5) / (h * KY * fit)), 1, 2.4);
  state.zoom = z;
  // (the back face is drawn rotateY(180) and the note turned 180, so it reads unmirrored)
  const dx = cx - VW / 2;
  state.tx = -dx * z * fit;
  state.ty = -(cy - VH / 2) * KY * z * fit;
  state.rx = 0;
  state.ry = (p.side === 'back' ? (Math.round(state.ry / 360) * 360 + 180) : Math.round(state.ry / 360) * 360);
  state.rz = 0;
  state.homeRy = state.ry;
  state.zoomedFeature = f.id;
  stopAuto();
  setTimeout(() => applyTransform(), 820);          // the camera has arrived: show the detail callouts
  zoomSlider.value = Math.round(z * 100);
  applyTransform(true);
}
function resetZoom() {
  state.zoom = 1; state.tx = 0; state.ty = 0;
  state.rx = REST.rx; state.rz = REST.rz;
  state.zoomedFeature = null;
  zoomSlider.value = 100;
  applyTransform(true);
}
function stopAuto() {
  state.auto = false;
  $('autoBtn').setAttribute('aria-pressed', 'false');
}

/* =====================================================================
   Pointer: tilt on hover, drag to rotate, drag an edge to bend, click a
   feature to select it
   ===================================================================== */
function hoverAmplitude() { return state.zoomedFeature ? 14 : (state.exploded ? 5 : 9); }
function setHoverTarget(nx, ny) {
  if (reduceMotion || state.drag || state.auto || document.body.classList.contains('intro')) { nx = 0; ny = 0; }
  const A = hoverAmplitude();
  hover.tx = clamp(nx, -1.25, 1.25) * A;
  hover.ty = -clamp(ny, -1.25, 1.25) * A;
  kick();
}
stage.addEventListener('pointermove', (e) => {
  if (e.pointerType === 'touch' || state.drag) return;
  // measured against the note itself, the same way on both axes: its edges give full tilt either way
  const r = note.getBoundingClientRect();
  setHoverTarget((e.clientX - (r.left + r.width / 2)) / (r.width * 0.5),
                 (e.clientY - (r.top + r.height / 2)) / (r.height * 0.5));
  noteWrap.classList.toggle('edge', !state.exploded && isEdge(e));
});
stage.addEventListener('pointerleave', () => setHoverTarget(0, 0));
stage.addEventListener('contextmenu', (e) => e.preventDefault());   // right button pans
if (window.DeviceOrientationEvent && !window.matchMedia('(pointer:fine)').matches
    && typeof DeviceOrientationEvent.requestPermission !== 'function') {
  window.addEventListener('deviceorientation', (e) => {
    if (e.gamma == null || state.drag) return;
    setHoverTarget(e.gamma / 30, (e.beta - 45) / 30);
  });
}

function edgeSide(e) {
  const r = note.getBoundingClientRect();
  const u = (e.clientX - r.left) / r.width;
  if (u < 0 || u > 1 || e.clientY < r.top || e.clientY > r.bottom) return null;
  return u < 0.5 ? 'left' : 'right';
}
function isEdge(e) {
  const r = note.getBoundingClientRect();
  const u = (e.clientX - r.left) / r.width;
  return e.clientY > r.top && e.clientY < r.bottom && ((u > 0 && u < 0.09) || (u > 0.91 && u < 1));
}
const ptr = { mode: null, x0: 0, y0: 0, moved: 0, fid: null, side: null, bend0: 0 };
noteWrap.addEventListener('pointerdown', (e) => {
  ptr.x0 = e.clientX; ptr.y0 = e.clientY; ptr.moved = 0;
  ptr.fid = e.target.closest && e.target.closest('.glow-piece')?.dataset.f || null;
  stopAuto();
  const label = e.target.closest && e.target.closest('.anno');
  if (label) { ptr.mode = 'click'; ptr.fid = label.dataset.f; return; }
  spin.target = null; spin.free = false; spin.v = 0;
  if (e.button === 2) {                               // right button: pan
    ptr.mode = 'pan';
    ptr.tx0 = state.tx; ptr.ty0 = state.ty;
    state.zoomedFeature = null;
    noteWrap.classList.add('panning');
    hideTag();
  } else if (!state.exploded && (e.shiftKey || isEdge(e))) {
    ptr.mode = 'bend';
    if (phys.foldT !== 0) setFold(false);              // bending undoes a fold
    ptr.side = edgeSide(e) || 'right';
    ptr.bend0 = state.bend;
    noteWrap.classList.add('bending');
  } else {
    ptr.mode = 'rotate';
    state.rx += hover.y; state.ry += hover.x;
    hover.x = hover.y = hover.tx = hover.ty = 0;
    state.drag = true;
    state.lastX = e.clientX; state.lastY = e.clientY;
    noteWrap.classList.add('grabbing');
    hideTag();
  }
  noteWrap.setPointerCapture(e.pointerId);
});
noteWrap.addEventListener('pointermove', (e) => {
  if (!ptr.mode || ptr.mode === 'click') return;
  ptr.moved = Math.max(ptr.moved, Math.hypot(e.clientX - ptr.x0, e.clientY - ptr.y0));
  if (ptr.mode === 'pan') {
    state.tx = ptr.tx0 + (e.clientX - ptr.x0);
    state.ty = ptr.ty0 + (e.clientY - ptr.y0);
    kick();
    return;
  }
  if (ptr.mode === 'bend') {
    const dx = e.clientX - ptr.x0;
    state.bend = clamp(ptr.bend0 + (ptr.side === 'right' ? -dx : dx) * 0.55 / fit, -170, 170);
    bendSlider.value = Math.round(state.bend);
    kick();
    return;
  }
  if (ptr.moved > 4) state.zoomedFeature = null;     // keep the zoom and pan; just stop calling it "focused"
  const dx = e.clientX - state.lastX, dy = e.clientY - state.lastY;
  state.ry += dx * 0.5;
  spin.v = spin.v * 0.5 + dx * 0.5 * 0.5;          // remembered for release momentum
  state.rx = clamp(state.rx - dy * 0.4, -75, 75);
  state.lastX = e.clientX; state.lastY = e.clientY;
  // (no paper flex while dragging: plain rotation stays on the single flat face, which is cheap)
  const norm = ((state.ry % 360) + 360) % 360;
  if (state.view !== 'uv') {
    const v = (norm > 90 && norm < 270) ? 'back' : 'front';
    if (v !== state.view) { state.view = v; syncUI(); }
  }
  kick();                                            // rendered once, in the next animation frame
});
window.addEventListener('pointerup', () => {
  if (!ptr.mode) return;
  const wasClick = ptr.moved < 5;
  if (ptr.mode === 'rotate') {
    state.drag = false;
    noteWrap.classList.remove('grabbing');
    if (!wasClick) {
      state.homeRy = state.ry;
      if (Math.abs(spin.v) > 0.4 && !reduceMotion) spin.free = true; else spin.v = 0;
    }
  }
  noteWrap.classList.remove('bending', 'panning');
  const mode = ptr.mode;
  ptr.mode = null;
  if (mode === 'pan') { kick(); return; }
  if (wasClick) {
    if (ptr.fid) selectFeature(ptr.fid);
    else if (state.selected && !state.exploded) deselect();
  }
  kick();
});

stage.addEventListener('wheel', (e) => {
  e.preventDefault();
  const next = clamp(state.zoom + state.zoom * (-e.deltaY * 0.0015), 0.5, 4);
  if (state.zoomedFeature) { state.zoomedFeature = null; state.tx = 0; state.ty = 0; }
  state.zoom = next;
  zoomSlider.value = Math.round(next * 100);
  applyTransform();
}, { passive: false });

/* =====================================================================
   Toolbar
   ===================================================================== */
function syncSide() {
  if (state.view === 'uv') return;
  const norm = ((state.ry % 360) + 360) % 360;
  const v = (norm > 90 && norm < 270) ? 'back' : 'front';
  if (v !== state.view) { state.view = v; syncUI(); }
}
function flipTo(target) {
  if (reduceMotion) { state.ry = target; syncSide(); applyTransform(true); return; }
  spin.free = false;
  spin.target = target;
  if (state.zoomedFeature) { state.zoomedFeature = null; state.tx = 0; state.ty = 0; state.zoom = 1; zoomSlider.value = 100; }
  kick();
}
$('flipBtn').addEventListener('click', () => {
  const from = spin.target ?? state.ry;
  state.homeRy = Math.round((from + 180) / 180) * 180;
  flipTo(state.homeRy);
});
function setFold(on) {
  if (on) {
    // a different fold each time: left or right half, toward or away from the viewer
    const options = ['right+', 'right-', 'left+', 'left-'].filter(o => o !== phys.lastFold);
    const pick = options[Math.floor(Math.random() * options.length)];
    phys.lastFold = pick;
    if (Math.abs(phys.fold) < 1) phys.foldSide = pick.startsWith('left') ? 'left' : 'right';
    phys.foldT = (pick.endsWith('+') ? 1 : -1) * 165;
  } else {
    phys.foldT = 0;
  }
  $('foldBtn').setAttribute('aria-pressed', on);
  if (on && state.bend !== 0) { state.bend = 0; bendSlider.value = 0; }   // fold and bend exclude each other
  if (on && state.exploded) setExploded(false);
  kick();
}
$('foldBtn').addEventListener('click', () => setFold(phys.foldT === 0));
bendSlider.addEventListener('input', () => {
  if (state.exploded) setExploded(false);
  if (phys.foldT !== 0) setFold(false);            // bending undoes a fold
  state.bend = +bendSlider.value;
  kick();
});
function resetAll() {
  if (state.exploded) setExploded(false, true);
  Object.assign(state, { rx: REST.rx, ry: REST.ry, rz: REST.rz, zoom: 1, tx: 0, ty: 0,
    zoomedFeature: null, view: 'front', homeRy: REST.ry, bend: 0, selected: null, seethrough: false, showAll: false });
  phys.foldT = 0;
  $('foldBtn').setAttribute('aria-pressed', 'false');
  zoomSlider.value = 100; bendSlider.value = 0;
  stopAuto();
  syncUI();
  applyTransform(true);
  kick();
}
$('resetBtn').addEventListener('click', resetAll);
$('autoBtn').addEventListener('click', () => {
  state.auto = !state.auto;
  $('autoBtn').setAttribute('aria-pressed', state.auto);
  if (state.auto) { state.zoomedFeature = null; state.tx = 0; state.ty = 0; hover.tx = hover.ty = 0; }
  kick();
});
zoomSlider.addEventListener('input', () => {
  state.zoom = zoomSlider.value / 100;
  if (state.zoomedFeature) { state.zoomedFeature = null; state.tx = 0; state.ty = 0; }
  applyTransform();
});
$('allBtn').addEventListener('click', () => { state.showAll = !state.showAll; syncUI(); });
document.querySelectorAll('#viewSeg button').forEach(b => {
  b.addEventListener('click', () => {
    const v = b.dataset.view;
    const norm = ((state.ry % 360) + 360) % 360;
    const showingBack = norm > 90 && norm < 270;
    if ((v === 'front' && showingBack) || (v === 'back' && !showingBack)) {
      state.homeRy = Math.round((state.ry + 180) / 180) * 180;
      if (state.view === 'uv') { state.view = v; syncUI(); }   // leave UV first: the flip keeps UV otherwise
      flipTo(state.homeRy);
      if (v === 'front' || v === 'back') return;
    }
    state.view = v;
    syncUI();
    applyTransform();
  });
});
window.addEventListener('keydown', (e) => {
  if (e.target.closest && e.target.closest('input')) return;
  const k = e.key.toLowerCase();
  if (k === 'f') $('flipBtn').click();
  else if (k === 'r') resetAll();
  else if (k === 'e') $('explodeBtn').click();
  else if (k === 'g') $('foldBtn').click();
  else if (k === ' ' && !e.target.closest('.feature')) { e.preventDefault(); $('autoBtn').click(); }
  else if (k === 'escape') { if (state.exploded) setExploded(false); else deselect(); }
});
window.addEventListener('resize', () => { computeFit(); applyTransform(); });
// the detail panel changes height with its content: refit when it does
new ResizeObserver(() => { computeFit(); applyTransform(); }).observe(document.querySelector('.col-right'));

/* =====================================================================
   Ultraviolet
   ===================================================================== */
function uvFibres(n, palette) {
  return Array.from({ length: n }).map(() => {
    const x = Math.random() * VW, y = Math.random() * VH;
    const a = Math.random() * Math.PI * 2, l = 5 + Math.random() * 8;
    const c = palette[Math.floor(Math.random() * palette.length)];
    return `<line x1="${x}" y1="${y}" x2="${x + Math.cos(a) * l}" y2="${y + Math.sin(a) * l}" stroke="${c}" stroke-width="0.9" class="glow" style="color:${c}" opacity=".95"/>`;
  }).join('');
}
// glowing print built from the feature's own cut-out, so it sits exactly on the printed shape
function uvInk(src, box, colour) {
  const b = pct(...box);
  return `<div class="uv-ink uvm-${src}" style="left:${b.left};top:${b.top};width:${b.width};height:${b.height};--c:${colour}"><i></i></div>`;
}
// a feature that lights up whole under the lamp: its own cut-out, recoloured to a fluorescent glow
function uvFluo(src, box, tone) {
  const b = pct(...box);
  return `<img class="uv-fluo${tone ? ' ' + tone : ''}" src="assets/layers/${src}.png" alt="" draggable="false" style="left:${b.left};top:${b.top};width:${b.width};height:${b.height}">`;
}
// built once and kept: switching to UV only reveals it, so nothing reloads or flashes
function applyUv(on) {
  if ($('uvOverlayFront')) return;
  // what the SNB says lights up: the globe at the top right of the front, and fibres in the paper
  // of both sides, in different colours (the fibres lie at random, as in the paper)
  const fib = ['#7fd0ff', '#fff2a8', '#ff6f8a', '#9fffcf', '#c9a2ff'];
  const fO = document.createElement('div');
  fO.id = 'uvOverlayFront';
  fO.className = 'uv-glow';
  fO.innerHTML = uvFluo('front-uvglobe', BX['front-uvglobe'] || [154, 26, 134, 134], 'globe')
    + `<svg viewBox="0 0 ${VW} ${VH}" preserveAspectRatio="none">${uvFibres(120, fib)}</svg>`;
  frontFace.appendChild(fO);
  const bO = document.createElement('div');
  bO.id = 'uvOverlayBack';
  bO.className = 'uv-glow';
  bO.innerHTML = `<svg viewBox="0 0 ${VW} ${VH}" preserveAspectRatio="none">${uvFibres(120, fib)}</svg>`;
  backFace.appendChild(bO);
}

/* =====================================================================
   Against the light: what transmitted light shows (Cross, Triangle,
   Microperf, Watermark and See-through register tests). Built once on
   each face; shown while "Hold up to the light" is on.
   ===================================================================== */
const css = (o) => Object.entries(o).map(([k, v]) => `${k}:${v}`).join(';');
function swissCross(x, y, s, cls) {        // a Swiss cross: arms a little longer than they are wide (SNB flag)
  const a = s / 2, b = s * 0.18;
  return `<path class="${cls}" d="M${x - b} ${y - a}h${2 * b}v${a - b}h${a - b}v${2 * b}h${-(a - b)}v${a - b}h${-2 * b}v${-(a - b)}h${-(a - b)}v${-2 * b}h${a - b}z"/>`;
}
function buildLight() {
  [frontFace, backFace].forEach((face, n) => {
    const back = n === 1, mx = (x) => back ? VW - x : x;
    const el = document.createElement('div');
    el.className = 'light-layer';
    const [tx, ty, tw, th] = BX['thread'] || [0, 271, 320, 12];
    const [px0, py0, pw, ph] = BX['front-microperf'] || [52, 462, 44, 44];
    el.innerHTML = `<svg viewBox="0 0 ${VW} ${VH}" preserveAspectRatio="none">`
      // cross test: the window cross becomes the Swiss flag (red square around the light cross)
      + `<rect class="flag" x="${mx(71.5) - 36}" y="${63.5 - 36}" width="72" height="72" rx="2"/>${swissCross(mx(71.5), 63.5, 55, 'flag-cross')}`
      // see-through register: the two incomplete crosses join into one complete outline
      + `${swissCross(mx(194), 554.5, 30, 'reg-line')}</svg>`
      + `<img class="lt-thread${back ? '' : ' mirror'}" src="assets/layers/thread.png" alt="" draggable="false" style="${css(pct(tx, ty, tw, th))}">`
      + `<img class="lt-perf${back ? ' mirror' : ''}" src="assets/layers/front-microperf.png" alt="" draggable="false" style="${css(pct(back ? VW - px0 - pw : px0, py0, pw, ph))}">`;
    face.querySelector('.glow-layer').after(el);   // above the highlights: against the light the window shows the flag
  });
}

/* =====================================================================
   Exploded view — the obverse pulled apart into its build layers
   ===================================================================== */
const LAYER_GAP = 64;
const layerStack = document.createElement('div');
layerStack.className = 'layer-stack';
note.appendChild(layerStack);
const layerEls = {};
LAYERS.forEach((L, i) => {
  const el = document.createElement('div');
  el.className = `layer layer-${L.kind}`;
  el.dataset.id = L.id;
  let inner = '';
  // offset print: the artwork with every separately layered feature removed (tools/isolate_features.py)
  if (L.kind === 'art') inner = `<img class="layer-art" src="${L.side === 'back' ? 'assets/offset-back.jpg' : 'assets/offset-front.jpg'}" alt="" draggable="false">`;
  else if (L.kind === 'pieces') {
    inner = L.pieces.map(([src, x, y, w, h, flag]) => {
      const b = pct(...(BX[src] || BX[src.replace(/-cut$/, '')] || [x, y, w, h]));   // cleaned (-cut) images share their feature's box
      return `<img class="piece${flag === 'mirror' ? ' mirror' : ''}" src="assets/layers/${src}.png" alt="" draggable="false"
        style="left:${b.left};top:${b.top};width:${b.width};height:${b.height}">`;
    }).join('');
  } else if (L.kind === 'uv') {
    inner = uvFluo('front-uvglobe', BX['front-uvglobe'] || [154, 26, 134, 134], 'globe');
  } else if (L.kind === 'paper' || L.kind === 'polymer') {
    // Durasafe: the window cross is cut out of both paper layers, so only the polymer core fills it
    inner = L.kind === 'paper' ? '<i class="paper-sheet"></i>' : '<i class="polymer-cross"></i>';
  }
  // reverse print faces the other way: seen from the obverse it reads mirrored
  el.innerHTML = `<div class="layer-content${L.side === 'back' ? ' rev' : ''}">${inner}</div>`
    + `<div class="layer-tag f"><span class="g">${L.group}</span>${L.name}</div>`
    + `<div class="layer-tag b"><span class="g">${L.group}</span>${L.name}</div>`;   // readable from behind
  if (L.core) el.classList.add('core');
  layerStack.appendChild(el);
  layerEls[L.id] = el;
});
if (layerEls.globe) mkOptics(layerEls.globe, 'globe');
if (layerEls.strip) mkOptics(layerEls.strip, 'strip');
const faceOptics = opticTargets;
const layerOptics = [...layerStack.querySelectorAll('.optic')];

const railList = $('layerRailList');
[...LAYERS].reverse().forEach(L => {
  const i = LAYERS.indexOf(L);
  const b = document.createElement('button');
  b.className = 'rail-item';
  b.dataset.id = L.id;
  b.innerHTML = `<span class="n">${L.group === 'Reverse' ? 'R' : L.group === 'Substrate' ? 'S' : 'O'}</span><span class="nm">${L.name}</span>`;
  if (i === LAYERS.length - 1 || LAYERS[i + 1]?.group !== L.group) {
    const h = document.createElement('div');
    h.className = 'rail-group';
    h.textContent = L.group;
    railList.appendChild(h);
  }
  b.addEventListener('mouseenter', () => focusLayer(L.id));
  b.addEventListener('mouseleave', () => focusLayer(state.pinnedLayer));
  b.addEventListener('focus', () => focusLayer(L.id));
  b.addEventListener('click', () => {
    focusLayer(state.pinnedLayer === L.id ? null : L.id, true);
    state.selected = state.pinnedLayer ? L.feature : null;
    syncUI();
  });
  railList.appendChild(b);
});
function focusLayer(id, pin) {
  if (pin) state.pinnedLayer = id;
  note.dataset.focus = id || '';
  Object.entries(layerEls).forEach(([k, el]) => el.classList.toggle('focus', k === id));
  railList.querySelectorAll('.rail-item').forEach(b => {
    b.classList.toggle('focus', b.dataset.id === id);
    b.classList.toggle('pinned', b.dataset.id === state.pinnedLayer);
  });
}
function setExploded(on, silent) {
  state.exploded = on;
  $('explodeBtn').setAttribute('aria-pressed', on);
  document.body.classList.toggle('exploded', on);
  // the paper is the core: reverse layers go one way, obverse layers the other
  const core = LAYERS.findIndex(L => L.core);
  const far = Math.max(...LAYERS.map((_, i) => Math.abs(i - core)));
  LAYERS.forEach((L, i) => {
    const el = layerEls[L.id];
    // in: inner layers lead outward; out: the exact reverse, outer layers lead back in
    const d = on ? Math.abs(i - core) : far - Math.abs(i - core);
    el.style.transitionDelay = d * 45 + 'ms';
    // closed, the layers keep a hairline gap so they always stack in order (obverse on top)
    // closed: the whole stack settles a few px *behind* the note face, so the face can fade in
    // over it cleanly (layers at the face's own depth z-fight and flicker)
    el.style.transform = `translateZ(${on ? (i - core) * LAYER_GAP : -12 + (i - core) * 3}px)`;
  });
  // closing mirrors opening: layers stay solid while they close onto the paper, then in the last
  // 300 ms the note fades back in as the layers fade out; labels wait until it is done
  clearTimeout(note._collapseT); clearTimeout(note._collapseEndT);
  note.classList.remove('collapse-end');
  note.classList.toggle('collapsing', !on);
  if (!on) {
    // swap to the note while the layers are still a few px apart: fully closed, coplanar layers flicker
    const T = 470 + far * 45;
    note._collapseT = setTimeout(() => { note.classList.remove('collapsing', 'collapse-end'); applyTransform(); }, T);
  }
  // the layer list appears only once the stack has finished opening, and leaves at once
  clearTimeout(document.body._railT);
  document.body.classList.remove('rail-in');
  // starts 0.5 s before the stack finishes opening, so it is in place as the motion settles
  if (on) document.body._railT = setTimeout(() => document.body.classList.add('rail-in'), Math.max(0, 750 + far * 45 - 500));
  note.classList.toggle('exploded', on);
  opticTargets = on ? [...faceOptics, ...layerOptics] : faceOptics;
  if (on) {
    stopAuto();
    state.bend = 0; bendSlider.value = 0;
    phys.foldT = 0; phys.fold = 0; phys.flex = 0;
    $('foldBtn').setAttribute('aria-pressed', 'false');
    state.zoomedFeature = null; state.tx = 0; state.ty = 0;
    // keep the side you were looking at (and ultraviolet): the stack opens facing you the same way
    const normNow = ((state.ry % 360) + 360) % 360;
    note._xBack = normNow > 90 && normNow < 270;
    // one fixed pose every time: clear pointer tilt, spin and flex, and take the nearest way round
    hover.x = hover.y = hover.tx = hover.ty = 0;
    spin.target = null; spin.free = false; spin.v = 0;
    phys.flex = 0; phys.v = 0; phys.dragVel = 0;
    const base = Math.round((state.ry - (note._xBack ? 180 : 0)) / 360) * 360 + (note._xBack ? 180 : 0);
    state.rx = -24; state.ry = base + (note._xBack ? 52 : -52); state.rz = 0; state.homeRy = state.ry;
    // fit the whole stack between the masthead and the toolbar
    state.zoom = clamp((window.innerHeight - 240) / 900, 0.4, 0.7);   // the upright note is tall
  } else {
    focusLayer(null, true);
    state.tx = 0; state.ty = 0;
    hover.x = hover.y = hover.tx = hover.ty = 0;
    if (!silent) {                                  // back to rest, on the same side it was opened from
      const back = !!note._xBack;
      const b = Math.round((state.ry - (back ? 180 : 0)) / 360) * 360 + (back ? 180 : 0);
      state.rx = REST.rx; state.ry = b + REST.ry; state.rz = REST.rz; state.zoom = 1; state.homeRy = state.ry;
      if (state.view !== 'uv') state.view = back ? 'back' : 'front';
    }
  }
  zoomSlider.value = Math.round(state.zoom * 100);
  syncUI();
  applyTransform(true);
}
$('explodeBtn').addEventListener('click', () => setExploded(!state.exploded));

/* =====================================================================
   Tweaks (host edit mode)
   ===================================================================== */
function setupTweaks() {
  let panel;
  window.addEventListener('message', (e) => {
    if (!e.data || !e.data.type) return;
    if (e.data.type === '__activate_edit_mode') showPanel();
    if (e.data.type === '__deactivate_edit_mode') hidePanel();
  });
  window.parent.postMessage({ type: '__edit_mode_available' }, '*');
  function showPanel() {
    if (panel) { panel.style.display = 'block'; return; }
    panel = document.createElement('div');
    panel.className = 'tweaks';
    panel.innerHTML = `<div class="tw-h">Tweaks</div>
      <div class="tw-p">Choose which optical effects are active when this design loads.</div>
      <div id="tweakFeatures" class="tw-chips"></div>`;
    document.body.appendChild(panel);
    const wrap = panel.querySelector('#tweakFeatures');
    FEATURES.forEach(f => {
      const chip = document.createElement('button');
      chip.textContent = f.name;
      chip.setAttribute('aria-pressed', TWEAK_DEFAULS.defaultActive.includes(f.id));
      chip.addEventListener('click', () => {
        const idx = TWEAK_DEFAULS.defaultActive.indexOf(f.id);
        if (idx >= 0) TWEAK_DEFAULS.defaultActive.splice(idx, 1);
        else TWEAK_DEFAULS.defaultActive.push(f.id);
        state.active = new Set(TWEAK_DEFAULS.defaultActive);
        syncUI();
        window.parent.postMessage({ type: '__edit_mode_set_keys', edits: { defaultActive: TWEAK_DEFAULS.defaultActive } }, '*');
        chip.setAttribute('aria-pressed', TWEAK_DEFAULS.defaultActive.includes(f.id));
      });
      wrap.appendChild(chip);
    });
  }
  function hidePanel() { if (panel) { panel.remove(); panel = null; } }
}

/* After 10 s without any input, ease back to the neutral pose (unless a feature is open
   for reading, or auto-rotate is on). Any input cancels the return. */
let idleTimer = 0;
function bumpIdle() {
  ret.on = false;
  clearTimeout(idleTimer);
  idleTimer = setTimeout(goNeutral, 10000);
}
function goNeutral() {
  if (state.selected || state.auto || state.drag) return;
  const ry0 = Math.round(state.ry / 360) * 360;
  const neutral = !state.exploded && !phys.foldT && Math.abs(state.bend) < 0.5 && state.zoom === 1
    && !state.tx && !state.ty && Math.abs(state.rx) < 0.5 && Math.abs(state.ry - ry0) < 0.5;
  if (neutral) return;
  if (state.exploded) setExploded(false, true);
  if (phys.foldT) setFold(false);
  state.zoomedFeature = null;
  if (state.view === 'back') state.view = 'front';
  state.homeRy = ry0;
  spin.free = false;
  spin.target = ry0;
  ret.on = true;
  syncUI();
  kick();
}
['pointermove', 'pointerdown', 'wheel', 'keydown', 'touchstart'].forEach(t =>
  window.addEventListener(t, bumpIdle, { passive: true }));
bumpIdle();

// overview/detail: a fade at the bottom while there is more to read below; gone at the end
function updateMoreFade() {
  const d = detailCard;
  d.classList.toggle('more', d.scrollHeight - d.scrollTop - d.clientHeight > 8);
}
detailCard.addEventListener('scroll', updateMoreFade, { passive: true });
new ResizeObserver(updateMoreFade).observe(detailCard);
new MutationObserver(() => requestAnimationFrame(updateMoreFade)).observe(detailCard, { childList: true, subtree: true });

/* "SWISS FRANCS" is letter-spaced to span exactly the width of the amount */
// the overview/detail panel is exactly as wide as the view tabs above it
function matchPanelToTabs() {
  const v = document.getElementById('viewSeg').getBoundingClientRect();
  document.documentElement.style.setProperty('--views-w', Math.round(v.width) + 'px');
}
window.addEventListener('resize', matchPanelToTabs);
(document.fonts ? document.fonts.ready : Promise.resolve()).then(() => { matchPanelToTabs(); computeFit(); applyTransform(); });

function fitSeries() {
  const amt = document.querySelector('.brand .amt'), ser = document.querySelector('.brand .series');
  if (!amt || !ser) return;
  ser.style.letterSpacing = '0px';
  ser.style.marginRight = '0px';
  ser.style.width = 'auto';
  const target = amt.getBoundingClientRect().width;
  const natural = ser.getBoundingClientRect().width;   // text width (h1 is a shrink-to-fit column)
  const gaps = Math.max(1, ser.textContent.length - 1);
  const ls = Math.max(0, (target - natural) / gaps);
  ser.style.letterSpacing = ls + 'px';
  ser.style.marginRight = -ls + 'px';          // no trailing space after the last letter
  // the language stack beside the amount spans exactly the amount's height
  const strap = document.querySelector('.title-row .strap');
  if (strap) {
    const r = amt.getBoundingClientRect();
    const glyphTop = r.top + r.height * 0.12, glyphBottom = r.bottom - r.height * 0.1;   // cap height, not line box
    strap.style.marginTop = (glyphTop - amt.parentElement.getBoundingClientRect().top) + 'px';
    strap.style.height = (glyphBottom - glyphTop) + 'px';
  }
}
/* strap: one language per line, longest (as rendered) on top, then fade/rise in */
function introStrap() {
  const strap = document.querySelector('.strap');
  if (!strap || strap.classList.contains('in')) return;
  [...strap.children]
    .map(el => [el, el.getBoundingClientRect().width])
    .sort((a, b) => b[1] - a[1])
    .forEach(([el]) => strap.appendChild(el));
  requestAnimationFrame(() => strap.classList.add('in'));
}
(document.fonts ? document.fonts.ready : Promise.resolve()).then(() => { fitSeries(); introStrap(); fitIntro(); });
// the intro starts as soon as the title's own font is in (or after 0.3 s): it does not wait for
// every other font file; those re-fit the layout whenever they arrive
Promise.race([
  document.fonts ? document.fonts.load("800 80px 'Fira Sans'") : Promise.resolve(),
  new Promise(r => setTimeout(r, 300)),
]).then(runIntro);
setTimeout(introStrap, 1500);                     // never leave it hidden if fonts stall
window.addEventListener('resize', fitSeries);

// decode every image up front (artworks, highlights, layers, optics): nothing pops in late the
// first time it is shown, and the bent-note strips never wait on a decode
['chf-1000-front.png', 'chf-1000-back.png'].forEach(src => { const i = new Image(); i.src = src; i.decode?.().catch(() => {}); });
window.addEventListener('load', () => {
  document.querySelectorAll('img').forEach(img => { img.decoding = 'sync'; img.decode?.().catch(() => {}); });
});

/* =====================================================================
   Intro: cover (title + four-language stack) -> cross-fade to the flat note,
   centred -> the note moves to its place and the rest of the page comes in.
   Click or any key skips it.
   ===================================================================== */
function fitIntro() {
  const amt = document.querySelector('.intro-title .amt'), ser = document.querySelector('.intro-title .series');
  const stack = $('introStack');
  if (!amt || !ser || !stack) return;
  ser.style.letterSpacing = '0px'; ser.style.marginRight = '0px';
  const ls = Math.max(0, (amt.getBoundingClientRect().width - ser.getBoundingClientRect().width) / Math.max(1, ser.textContent.length - 1));
  ser.style.letterSpacing = ls + 'px'; ser.style.marginRight = -ls + 'px';
  // longest line on top, then shorter ones (by rendered width)
  [...stack.children].map(el => [el, el.getBoundingClientRect().width]).sort((a, b) => b[1] - a[1])
    .forEach(([el]) => stack.appendChild(el));
  // the stack spans exactly the height of amount + series together
  stack.style.height = document.querySelector('.intro-title').getBoundingClientRect().height + 'px';
}
function runIntro() {
  const B = document.body;
  const steps = [];
  const at = (ms, fn) => steps.push(setTimeout(fn, ms));
  const off = () => { window.removeEventListener('pointerdown', skip, true); window.removeEventListener('keydown', skip, true); };
  const settle = () => {                                   // note to its place, page in
    B.classList.add('intro-settle');
    B.classList.remove('intro');
    computeFit(); applyTransform(true);
    // the note's move takes 0.8 s: once it has landed, the labels and needles draw in
    at(850, () => { B.classList.remove('intro-settle', 'intro-in', 'intro-out'); applyTransform(); });
  };
  function skip() {
    steps.forEach(clearTimeout); steps.length = 0;
    off();
    B.classList.add('intro-in', 'intro-out');
    settle();
  }
  window.addEventListener('pointerdown', skip, true);
  window.addEventListener('keydown', skip, true);
  fitIntro();
  if (reduceMotion) { skip(); return; }
  requestAnimationFrame(() => B.classList.add('intro-in'));   // languages translate in
  at(2300, () => B.classList.add('intro-out'));                // cover out, note in (centred)
  at(3500, () => { off(); settle(); });
}

/* =====================================================================
   Boot
   ===================================================================== */
applyUv(true);                         // build the (hidden) UV layers up front
buildLight();                          // and the (hidden) against-the-light layers
setupTweaks();
computeFit();
syncUI();
