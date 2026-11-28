// Plain script (not a module) so the page also works when opened straight from disk (file://)
// ¥10,000 Bank of Japan note, issued from 3 July 2024 (the 2024 series, "F" notes).
// Feature facts and wording follow the Bank of Japan (boj.or.jp/note_tfjgs/note/n_note/security.htm)
// and the National Printing Bureau (npb.go.jp/ja/n_banknote/design10/).
const FEATURES = [
  {
    id:'hologram', name:'3D hologram', short:'The portrait turns as you tilt',
    color:'#7a5aa8', color2:'#b9a2e0',
    desc:'A stripe hologram on the left of the front. Its portrait of Shibusawa Eiichi is shown in three dimensions and turns as the note is tilted, and the other images on the stripe change with the viewing angle. The Bank of Japan says this is the first use of this kind of hologram on a banknote anywhere in the world.',
    how:'Tilt the note. The <b>portrait in the stripe should turn</b> to follow you, and the other images on the stripe should change.',
    markers:[ { side:'front', x:93, y:160, ring:20, label:'3D hologram', outline:{shape:'rect', x:70, y:21, w:45.5, h:278, rx:6} } ],
    icon:'<path d="M5 2h6v12H5z"/><circle cx="8" cy="6" r="1.6"/>'
  },
  {
    id:'watermark', name:'High-definition watermark', short:'Shibusawa Eiichi, formed in the paper',
    color:'#8a6a3a', color2:'#c7a878',
    desc:'Formed in the paper, not printed. Besides the traditional watermark portrait of Shibusawa Eiichi, the paper carries a high-definition watermark: a continuous pattern of very fine lines around the portrait, in a diamond motif on the ¥10,000. Hold the note up to the light to see it, from either side.',
    how:'Hold the note up to a light. The <b>portrait</b> should appear in the blank oval, surrounded by a <b>fine diamond pattern</b>.',
    markers:[
      { side:'front', x:383, y:148, ring:34, label:'Watermark', outline:{shape:'ellipse', cx:383, cy:148, rx:66, ry:80} },
      { side:'back',  x:337, y:148, ring:34, label:'Watermark (reverse)', outline:{shape:'ellipse', cx:337, cy:148, rx:66, ry:80} },
    ],
    icon:'<circle cx="8" cy="8" r="5"/><path d="M3 14c1-2 3-3 5-3s4 1 5 3"/>'
  },
  {
    id:'bars', name:'Bar-pattern watermark', short:'Three vertical bars against the light',
    color:'#6a5a46', color2:'#b2a28a',
    desc:'Bar-shaped watermarks are also formed in the paper. Held up to the light, the ¥10,000 shows three vertical bars, to the right of the portrait (the ¥5,000 has two, the ¥1,000 one).',
    how:'Hold the note up to a light and look to the right of the portrait: you should see <b>three vertical bars</b>.',
    markers:[ { side:'front', x:637, y:156, ring:20, label:'Bar pattern', outline:{shape:'rect', x:619, y:124, w:36, h:64, rx:3} } ],
    icon:'<path d="M4 3v10M8 3v10M12 3v10"/>'
  },
  {
    id:'latent', name:'Latent images', short:'10000 on the front, NIPPON on the back',
    color:'#4e4a6a', color2:'#9a96bc',
    desc:'Images engraved into the line pattern that show only at an angle. Tilt the note and the face value 10000 appears in the engraved cartouche at the bottom of the front, and the letters NIPPON appear on the back, right of the watermark.',
    how:'Hold the note almost level with your eye and tilt it. <b>10000</b> should appear in the cartouche below the watermark, and <b>NIPPON</b> on the back.',
    markers:[
      { side:'front', x:359, y:279, ring:20, label:'Latent 10000', outline:{shape:'rect', x:290, y:255, w:138, h:50, rx:8} },
      { side:'back',  x:500, y:160, ring:20, label:'Latent NIPPON', outline:{shape:'rect', x:440, y:134, w:120, h:52, rx:4} },
    ],
    icon:'<path d="M2 12l6-8 6 8"/><path d="M5 9h6"/>'
  },
  {
    id:'pearl', name:'Pearl ink', short:'A pink sheen at both ends',
    color:'#c7568a', color2:'#f2a6c8',
    desc:'A clear pearlescent ink over the blank margins at the left and right ends of the note. Face on it is almost invisible; tilt the note and a pink sheen appears.',
    how:'Tilt the note under a light and watch its <b>left and right ends</b>. A <b>pink sheen</b> should appear and move.',
    markers:[
      { side:'front', x:30,  y:156, ring:18, label:'Pearl ink (left)', outline:{shape:'rect', x:2, y:76, w:60, h:162, rx:6} },
      { side:'front', x:688, y:156, ring:18, label:'Pearl ink (right)', outline:{shape:'rect', x:654, y:76, w:64, h:162, rx:6} },
    ],
    icon:'<path d="M3 3v10M13 3v10"/><circle cx="8" cy="8" r="2"/>'
  },
  {
    id:'microprint', name:'Microprinting', short:'NIPPONGINKO, too small to read unaided',
    color:'#6b4a22', color2:'#a87a40',
    desc:'The words NIPPONGINKO are printed in letters too small to read without a magnifier, and too small for colour copiers to reproduce. The Bank of Japan marks them beside the lower-right 10000 on the front, and beside the left border on the back.',
    how:'Use a <b>magnifier</b> on the places marked. The letters NIPPONGINKO should be sharp and complete, not dots or a blur.',
    markers:[
      { side:'front', x:604, y:264, ring:14, label:'Microprinting', outline:{shape:'rect', x:582, y:244, w:44, h:42, rx:3} },
      { side:'back',  x:31,  y:190, ring:14, label:'Microprinting', outline:{shape:'rect', x:9, y:168, w:46, h:43, rx:3} },
    ],
    icon:'<path d="M2 4h12M2 8h12M2 12h8"/>'
  },
  {
    id:'intaglio', name:'Deep intaglio printing', short:'The 10000 feels rough',
    color:'#3f3346', color2:'#8d7f96',
    desc:'The portrait and the main designs are printed by intaglio, which leaves the ink standing up from the paper. The face value numeral and the identification marks use deep intaglio, with the ink piled especially high, so they feel rough to the touch.',
    how:'Run a finger over the <b>10000</b> left of the watermark and over the <b>identification marks</b> at either end. They should feel rough, not smooth.',
    markers:[ { side:'front', x:217, y:148, ring:24, label:'Face value 10000', outline:{shape:'rect', x:128, y:110, w:184, h:70, rx:4} } ],
    icon:'<path d="M2 12h12M4 9h8M6 6h4"/>'
  },
  {
    id:'tactile', name:'Identification marks', short:'Eleven raised lines, for touch',
    color:'#2f5a46', color2:'#7aa892',
    desc:'Raised marks that people with impaired sight can feel to tell the denomination. On the 2024 notes every mark is the same shape, eleven diagonal lines, which is easier to feel, and the position differs by denomination: on the ¥10,000 they sit at the middle of the left and right ends of the front.',
    how:'Feel the <b>middle of each end</b> of the front: <b>eleven diagonal lines</b>, rough to the touch.',
    markers:[
      { side:'front', x:35,  y:165, ring:16, label:'Identification mark', outline:{shape:'rect', x:14, y:114, w:42, h:102, rx:3} },
      { side:'front', x:683, y:165, ring:16, label:'Identification mark', outline:{shape:'rect', x:660, y:114, w:46, h:102, rx:3} },
    ],
    icon:'<path d="M3 13l4-10M6 13l4-10M9 13l4-10"/>'
  },
  {
    id:'uv', name:'Luminescent ink', short:'The seal and parts of the pattern glow',
    color:'#b84a2a', color2:'#ee9a70',
    desc:'Special ink that glows under ultraviolet light. Under a UV lamp the seal of the Governor of the Bank of Japan on the front glows orange, and parts of the pattern around the portrait and along the left end glow yellow-green. The National Printing Bureau says parts of the back’s pattern glow too.',
    how:'Under a <b>UV lamp</b> the <b>seal</b> should glow orange and parts of the pattern yellow-green. The paper itself should stay dark.',
    markers:[ { side:'front', x:251, y:246, ring:20, label:'Governor’s seal', outline:{shape:'ellipse', cx:251, cy:246.5, rx:33, ry:31} } ],
    icon:'<circle cx="8" cy="8" r="3"/><path d="M8 1v2M8 13v2M1 8h2M13 8h2"/>'
  },
  {
    id:'fineline', name:'Intaglio portrait', short:'Shibusawa Eiichi · Tokyo Station',
    color:'#5a4652', color2:'#a8909c',
    desc:'The front shows Shibusawa Eiichi, the industrialist said to have helped found some 500 companies. The back shows the Marunouchi building of Tokyo Station, the red-brick station building and an Important Cultural Property. Both are engraved and printed by intaglio: every tone is made of fine lines.',
    how:'Use a <b>magnifier</b> on the face and on the station’s brickwork. The lines should be crisp and separate; dots or blur mean a printed copy.',
    markers:[
      { side:'front', x:530, y:150, ring:40, label:'Shibusawa Eiichi', outline:{shape:'rect', x:414, y:38, w:240, h:240, rx:4} },
      { side:'back',  x:150, y:150, ring:40, label:'Tokyo Station', outline:{shape:'rect', x:16, y:22, w:276, h:260, rx:4} },
    ],
    icon:'<circle cx="8" cy="8" r="5" fill="none"/><circle cx="8" cy="8" r="3" fill="none"/>'
  },
  {
    id:'numerals', name:'Larger numerals', short:'Universal design',
    color:'#c8463c', color2:'#f09a8c',
    desc:'To make the denomination easier to read, the Arabic numerals on both sides are larger than on the notes issued from 2004. The back carries a large 10000 in vermilion across its top right.',
    how:'Check the <b>10000</b> at the lower right of the front and the <b>large 10000</b> on the back.',
    markers:[
      { side:'front', x:649, y:282, ring:18, label:'10000', outline:{shape:'rect', x:596, y:256, w:106, h:52, rx:4} },
      { side:'back',  x:582, y:68, ring:30, label:'Large 10000', outline:{shape:'rect', x:460, y:20, w:244, h:96, rx:4} },
    ],
    icon:'<path d="M4 3v10M8 4a2 2 0 0 1 2 2v4a2 2 0 0 1-4 0V6a2 2 0 0 1 2-2z"/>'
  },
];

// Exploded view: the note pulled apart in both directions. The paper (with its watermarks) is the core;
// the reverse print is on one side, the obverse print, foil and pearl coat on the other.
const LAYERS = [
  { id:'r-numeral',  name:'Large 10000',      group:'Reverse', side:'back',  feature:'numerals',  kind:'pieces',
    pieces:[ ['back-numeral-big', 456,16,252,104] ] },
  { id:'r-intaglio', name:'Intaglio ink',     group:'Reverse', side:'back',  feature:'fineline',  kind:'pieces',
    pieces:[ ['back-station', 16,22,276,260], ['back-numeral-small', 14,258,158,54] ] },
  { id:'r-offset',   name:'Offset print',     group:'Reverse', side:'back',  feature:null,        kind:'art' },
  { id:'bars',       name:'Bar watermark',    group:'Paper',   side:'front', feature:'bars',      kind:'pieces',
    pieces:[ ['watermark-bars', 619,124,36,64] ] },
  { id:'substrate',  name:'Paper',            group:'Paper',   side:'front', feature:null,        kind:'paper', core:true },
  { id:'watermark',  name:'Watermark',        group:'Paper',   side:'front', feature:'watermark', kind:'pieces',
    pieces:[ ['watermark-ghost', 313,62,158,171] ] },
  { id:'offset',     name:'Offset print',     group:'Obverse', side:'front', feature:null,        kind:'art' },
  { id:'intaglio',   name:'Intaglio ink',     group:'Obverse', side:'front', feature:'intaglio',  kind:'pieces',
    pieces:[ ['front-portrait', 414,38,240,240], ['front-numeral', 124,106,192,78], ['front-numeral-br', 596,256,106,52],
             ['front-cartouche', 286,252,146,56], ['front-tactile-left', 14,114,42,102], ['front-tactile-right', 660,114,46,102] ] },
  { id:'seal',       name:'Luminescent ink',  group:'Obverse', side:'front', feature:'uv',        kind:'pieces',
    pieces:[ ['front-seal', 214,211.5,74,70] ] },
  { id:'hologram',   name:'Hologram foil',    group:'Obverse', side:'front', feature:'hologram',  kind:'pieces',
    pieces:[ ['front-hologram-cut', 70,21,45.5,278] ] },
  { id:'pearl',      name:'Pearl ink',        group:'Obverse', side:'front', feature:'pearl',     kind:'pieces',
    pieces:[ ['front-pearl', 0,70,720,176] ] },
  { id:'uv',         name:'UV: seal and pattern', group:'Obverse', side:'front', feature:'uv',    kind:'uv' },
];

const TWEAK_DEFAULS = {
  "defaultActive": ["hologram","holoface","watermark","bars","latent","latentb","pearl","microprint","intaglio","tactile","uv","fineline","numerals"]
};

// Glow highlights: each feature's own cut-out (assets/layers/<src>.png) laid exactly over the artwork
// at its box [x, y, w, h] in 720x320 note space (boxes from assets/boxes.js when present).
const P = (side, src, x, y, w, h, mirror) => ({ side, src, box: (!mirror && !src.endsWith('.svg') && typeof BOXES !== 'undefined' && BOXES[src]) || [x, y, w, h], mirror:!!mirror });
const GLOW = {
  hologram:  [ P('front','front-hologram',70,21,45.5,278) ],
  watermark: [ P('front','watermark-ghost',313,62,158,171), P('back','watermark-ghost',249,62,158,171,true) ],   // the back mirrors it
  bars:      [ P('front','watermark-bars',619,124,36,64) ],
  latent:    [ P('front','front-cartouche',286,252,146,56), P('back','latent-back',443,137,113,45) ],
  pearl:     [ P('front','front-pearl',0,70,720,176) ],
  microprint:[ P('front','front-numeral-br',596,256,106,52), P('back','back-station',4,18,300,272) ],
  intaglio:  [ P('front','front-numeral',124,106,192,78), P('front','front-tactile-left',14,114,42,102), P('front','front-tactile-right',660,114,46,102) ],
  tactile:   [ P('front','front-tactile-left',14,114,42,102), P('front','front-tactile-right',660,114,46,102) ],
  uv:        [ P('front','front-seal',214,211.5,74,70) ],
  fineline:  [ P('front','front-portrait',414,38,240,240), P('back','back-station',16,22,276,260) ],
  numerals:  [ P('front','front-numeral-br',596,256,106,52), P('back','back-numeral-big',456,16,252,104), P('back','back-numeral-small',14,258,158,54) ],
};

// Detail callouts shown when a feature is zoomed into: [side, [[x, y], ...], label] in note units.
const DETAILS = {
  hologram:  [['front', [[93, 62]], 'Portrait turns in 3D'], ['front', [[93, 150]], 'Cherry blossoms'],
              ['front', [[93, 270]], '10000 on the foil']],
  watermark: [['front', [[392, 120]], 'Portrait, in the paper'],
              ['back', [[328, 150]], 'Seen from the back too']],
  bars:      [['front', [[637, 140]], 'Three vertical bars'], ['front', [[637, 180]], 'Only against the light']],
  latent:    [['front', [[330, 279]], 'Tilt: 10000 appears'], ['front', [[395, 279]], 'Horizontal lines in vertical ones'],
              ['back', [[500, 160]], 'Tilt: NIPPON appears']],
  pearl:     [['front', [[30, 120]], 'Pink sheen, left end'], ['front', [[688, 200]], 'Pink sheen, right end']],
  microprint:[['front', [[604, 264]], 'NIPPONGINKO'], ['back', [[31, 190]], 'NIPPONGINKO']],
  intaglio:  [['front', [[217, 148]], 'Deep intaglio: rough'], ['front', [[35, 165]], 'Identification mark'],
              ['front', [[683, 165]], 'Identification mark']],
  tactile:   [['front', [[35, 140]], 'Eleven diagonal lines'], ['front', [[683, 190]], 'Same on the right']],
  uv:        [['front', [[251, 246]], 'Governor’s seal glows orange']],
  fineline:  [['front', [[530, 130]], 'Shibusawa Eiichi'], ['front', [[600, 245]], 'Shading from line spacing'],
              ['back', [[150, 120]], 'Tokyo Station, Marunouchi'], ['back', [[200, 230]], 'Engraved brickwork']],
  numerals:  [['front', [[649, 282]], '10000, lower right'], ['back', [[582, 68]], 'Large vermilion 10000'],
              ['back', [[70, 288]], '10000 YEN']],
};
