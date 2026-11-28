// Plain script (not a module) so the page also works when opened straight from disk (file://)
// HK$1,000, Standard Chartered Bank (Hong Kong) Limited, 2018 Series.
// Feature wording follows the Hong Kong Monetary Authority (hkma.gov.hk, 2018 Series Banknotes and its
// leaflet) and Standard Chartered's own pages (sc.com/hk, 2018 Banknotes Series); sources in README.md.
// tag: the short name on the labels around the note; name: the full official name
const FEATURES = [
  {
    id:'shimmer', tag:'Shimmering pattern', name:'Dynamic shimmering pattern', zh:'動感光亮圖案', short:'A ring of light moves as you tilt',
    color:'#1d6b3a', color2:'#6fc28c',
    desc:'The green bauhinia with the numeral 1000 at the top right of the front. When the note is tilted, the shimmering ring in the pattern moves correspondingly.',
    how:'Tilt the note up and down, then side to side. A <b>ring of light</b> should travel across the green bauhinia with your movement. A copy stays flat and dull.',
    markers:[ { side:'front', x:601, y:66, ring:30, label:'Dynamic shimmering pattern' } ],
    icon:'<circle cx="8" cy="8" r="5"/><ellipse cx="8" cy="8" rx="5" ry="2"/>'
  },
  {
    id:'thread', tag:'Metallic thread', name:'Windowed metallic thread', zh:'開窗金屬線', short:'Large and small rings move',
    color:'#1f6f4a', color2:'#7ccf9e',
    desc:'A metallic thread woven into the paper surfaces in three windows down the middle of the front. When the note is tilted, the large and small rings on the metallic thread move correspondingly.',
    how:'Tilt the note and watch the <b>three green windows</b> in the middle of the front. The <b>large and small rings</b> on the thread should move as you tilt.',
    markers:[ { side:'front', x:466, y:90, ring:16, label:'Windowed metallic thread' } ],
    icon:'<path d="M8 1v14M5 3h6v3H5zM5 7h6v3H5zM5 11h6v3H5z"/>'
  },
  {
    id:'emboss', tag:'Embossed feel', name:'Embossed feel', zh:'凹凸手感', short:'Raised ink you can feel',
    color:'#c0391f', color2:'#ef8a6a',
    desc:'Raised printing gives the note a strong embossed feel by touch. The HKMA’s close-up of this note shows it on the large 1000 at the top left of the front. High-tactility numerals are among the accessibility features the 2018 Series keeps.',
    how:'Run a fingertip over the <b>large 1000</b> at the top left. The ink should feel <b>raised and rough</b>, not smooth like a print-out.',
    markers:[ { side:'front', x:150, y:46, ring:30, label:'Embossed feel' } ],
    icon:'<path d="M2 12h12M4 9h8M6 6h4"/>'
  },
  {
    id:'latent', tag:'Concealed 1000', name:'Concealed denomination', zh:'隱藏銀碼', short:'1000 appears when tilted',
    color:'#9a1f1a', color2:'#e06a5a',
    desc:'A denomination numeral hidden in the background. When the note is tilted under the light, the hidden numeral 1000 can be seen. The HKMA marks it in the red print at the foot of the Standard Chartered Bank Building, and its close-up shows a red 1000 in fine lines there.',
    how:'Hold the note almost flat at eye level under a light and tilt it slowly. A <b>1000</b> should appear in the red print of the bank building. (Here it is drawn: tilt the note well up or down.)',
    markers:[ { side:'front', x:355, y:231, ring:20, label:'Concealed denomination' } ],
    icon:'<path d="M2 11l6-6 6 6"/><path d="M5 11h6"/>'
  },
  {
    id:'watermark', tag:'Watermark', name:'Enhanced watermark', zh:'高透光水印', short:'Bauhinia flower, leaves, bud and 1000',
    color:'#8a6a3a', color2:'#c7a878',
    desc:'A watermark on the theme of the bauhinia flower, in the clear area on the right side of the front. When the note is held up to the light, the flower, leaves, bud and the denomination numeral can be seen.',
    how:'Hold the note up to a light. In the plain area on the right you should see the <b>bauhinia flower, its leaves, a bud</b> and a bright <b>1000</b>, from either side.',
    markers:[
      { side:'front', x:590, y:170, ring:30, label:'Enhanced watermark' },
      { side:'back',  x:130, y:170, ring:30, label:'Watermark (reverse)' },
    ],
    icon:'<path d="M8 3c2 2 2 5 0 7-2-2-2-5 0-7zM3 8c2-1 4 0 5 2M13 8c-2-1-4 0-5 2"/>'
  },
  {
    id:'register', tag:'See-through 1000', name:'Fluorescent see-through denomination', zh:'熒光透視銀碼', short:'Two halves make 1000 against the light',
    color:'#d58a12', color2:'#f5c35a',
    desc:'Patterns on the front and back, each of a single colour under normal light. Seen from either side only part of the pattern shows; held up to the light, the front and back patterns fit perfectly to form the denomination numeral 1000. Under ultraviolet light the patterns appear as two fluorescent colours.',
    how:'Press <b>Hold up to the light</b>: the orange pieces at the bottom right of the front join the pieces printed on the back into a complete <b>1000</b>. Under a UV lamp they glow in two colours.',
    markers:[
      { side:'front', x:600, y:285, ring:24, label:'See-through denomination' },
      { side:'back',  x:116, y:285, ring:24, label:'See-through (back half)' },
    ],
    icon:'<path d="M3 4h3v8M9 4c3 0 4 2 4 4s-1 4-4 4"/>'
  },
  {
    id:'braille', tag:'Braille', name:'Braille', zh:'點字', short:'Bottom left corner',
    color:'#c0281e', color2:'#ee7a6e',
    desc:'Braille dots in the bottom left corner of the front, one of the accessibility features the 2018 Series keeps so that people with visual impairments can tell the denominations apart.',
    how:'Feel the <b>bottom left corner</b> of the front for the raised <b>braille dots</b>.',
    markers:[ { side:'front', x:96, y:296, ring:14, label:'Braille' } ],
    icon:'<circle cx="5" cy="4" r="1.3"/><circle cx="5" cy="8" r="1.3"/><circle cx="11" cy="8" r="1.3"/><circle cx="11" cy="12" r="1.3"/>'
  },
  {
    id:'tactile', tag:'Tactile lines', name:'Tactile lines', zh:'手感線', short:'Raised lines near the edges',
    color:'#c0281e', color2:'#ee7a6e',
    desc:'Rows of short slanting lines printed near the left and right edges of the front, another of the accessibility features the 2018 Series keeps for people with visual impairments.',
    how:'Run a finger along the <b>left and right edges</b> of the front. The <b>red slanting lines</b> should feel raised.',
    markers:[ { side:'front', x:12, y:220, ring:14, label:'Tactile lines' } ],
    icon:'<path d="M3 4l4-2M3 8l4-2M3 12l4-2M9 6l4-2M9 10l4-2M9 14l4-2"/>'
  },
  {
    id:'serial', tag:'Serial numbers', name:'Serial numbers', zh:'號碼', short:'Twice on the front',
    color:'#2a2a2a', color2:'#8a8a8a',
    desc:'Every note carries its serial number twice on the front: horizontally at the bottom left and vertically on the right. The artwork shown is the HKMA’s, with the sample number AB123456.',
    how:'Both serials must match exactly, character for character.',
    markers:[
      { side:'front', x:95, y:272, ring:14, label:'Serial (horizontal)' },
      { side:'front', x:676, y:186, ring:14, label:'Serial (vertical)' },
    ],
    icon:'<path d="M2 4h2v8H2zM6 4h2v8H6zM10 4h2v8h-2z"/>'
  },
  {
    id:'building', tag:'The Bank Building', name:'The Standard Chartered Bank Building and the Forum', zh:'渣打銀行大廈與渣打財富管理中心', short:'Standard Chartered in Central',
    color:'#c4502a', color2:'#f09a6a',
    desc:'The front of every Standard Chartered note of the 2018 Series features the Standard Chartered Bank Building and the Forum in Central. The bank says they stand for its commitment to the city, having worked side by side with Hong Kong for nearly 160 years. The background’s geometric cut is inspired by the glass façade of the Forum, and the Standard Chartered logo at the centre takes a different motif on each denomination, echoing the back.',
    how:'Look at the two buildings and the angled cuts behind them: the lines should be crisp and continuous, with no dot screen.',
    markers:[ { side:'front', x:355, y:165, ring:40, label:'The Bank Building' } ],
    icon:'<path d="M3 14V7h4v7M7 14V2h5v12M2 14h12"/>'
  },
  {
    id:'signature', tag:'Signatures', name:'Signatures and date', zh:'簽名及日期', short:'Chief Financial Officer and Chief Executive · 1 January 2018',
    color:'#7a3a2a', color2:'#c78870',
    desc:'The note promises to pay the bearer on demand at its office here (憑票即付), by order of the Board of Directors (承董事會命), and carries two signatures, over the titles Chief Financial Officer (財務總裁) and Chief Executive (行政總裁). It is dated Hong Kong, 1 January 2018 (香港 二〇一八年一月一日).',
    how:'The signatures and the printed titles and date should be sharp and complete.',
    markers:[ { side:'front', x:110, y:194, ring:16, label:'Signatures' } ],
    icon:'<path d="M2 11c2-3 3-6 4-6s0 6 2 6 2-4 3-4 1 3 3 3"/>'
  },
  {
    id:'skyline', tag:'Central skyline', name:'Wit and Wisdom: the Central skyline', zh:'靈活睿智', short:'The reverse, printed upright',
    color:'#d0602a', color2:'#f5a26a',
    desc:'Standard Chartered calls its HK$1,000 “Wit and Wisdom”. The signature Central skyline is the key visual, highlighting Hong Kong’s position as an international financial centre, and symbols of technology and the stock market show the wit and dynamics of its financial industry. Placed side by side, the backgrounds of the bank’s five 2018 notes form a silhouette of Lion Rock, the symbol of the “Hong Kong Spirit” the series is themed on. Like the whole series, the reverse is laid out vertically: turn the note a quarter turn to read it.',
    how:'Turn the note over and a quarter turn. The towers should be finely detailed down to their rows of tiny digits, with clean edges against the pale background.',
    markers:[ { side:'back', x:420, y:160, ring:40, label:'Central skyline' } ],
    icon:'<path d="M3 13V8h2v5M7 13V4h2v9M11 13V6h2v7M2 13h12"/>'
  },
];

// Exploded view: the note pulled apart in both directions. The paper (with the thread and the
// watermark inside it) is the core; the reverse is printed on one side and the obverse on the other.
const LAYERS = [
  { id:'r-seethrough', name:'See-through (back half)', group:'Reverse', side:'back', feature:'register', kind:'pieces',
    pieces:[ ['back-seethrough', 46,256,140,58] ] },
  { id:'r-offset',   name:'Printed reverse',  group:'Reverse', side:'back',  feature:'skyline',   kind:'art' },
  { id:'thread',     name:'Metallic thread',  group:'Paper',   side:'front', feature:'thread',    kind:'pieces',
    pieces:[ ['front-thread', 449,54,34,254] ] },
  { id:'substrate',  name:'Banknote paper',   group:'Paper',   side:'front', feature:null,        kind:'paper', core:true },
  { id:'watermark',  name:'Watermark',        group:'Paper',   side:'front', feature:'watermark', kind:'pieces',
    pieces:[ ['watermark-ghost', 529.84,102.15,137.86,149.69] ] },
  { id:'offset',     name:'Printed front',    group:'Obverse', side:'front', feature:'building',  kind:'art' },
  { id:'raised',     name:'Raised ink',       group:'Obverse', side:'front', feature:'emboss',    kind:'pieces',
    pieces:[ ['front-numeral', 10,10,204,78], ['front-tactile-l', 0,130,24,180], ['front-tactile-r', 696,136,24,174],
             ['front-braille', 40,282,112,26] ] },
  { id:'shimmer',    name:'Shimmering ink',   group:'Obverse', side:'front', feature:'shimmer',   kind:'pieces',
    pieces:[ ['front-shimmer', 544,16,116,100] ] },
  { id:'seethrough', name:'See-through (front half)', group:'Obverse', side:'front', feature:'register', kind:'pieces',
    pieces:[ ['front-seethrough', 526,256,146,58] ] },
  { id:'serial',     name:'Serial numbers',   group:'Obverse', side:'front', feature:'serial',    kind:'pieces',
    pieces:[ ['front-serial-h', 40,260,108,24], ['front-serial-v', 664,122,24,126] ] },
  { id:'uv',         name:'UV: two colours',  group:'Obverse', side:'front', feature:'register',  kind:'uv' },
];

const TWEAK_DEFAULS = {
  "defaultActive": ["shimmer","thread","emboss","latent","watermark","register","braille","tactile","serial","building","signature","skyline"]
};

// Glow highlights: each feature's own cut-out (assets/layers/<src>.png) laid exactly over the artwork
// at its box [x, y, w, h] in 720x320 note space (boxes from assets/boxes.js when present).
const P = (side, src, x, y, w, h, mirror) => ({ side, src, box: (!mirror && typeof BOXES !== 'undefined' && BOXES[src]) || [x, y, w, h], mirror:!!mirror });
const WMB = (typeof BOXES !== 'undefined' && BOXES['watermark-ghost']) || [529.84, 102.15, 137.86, 149.69];
const GLOW = {
  shimmer:   [ P('front','front-shimmer',544,16,116,100) ],
  thread:    [ P('front','front-thread',449,54,34,254) ],
  emboss:    [ P('front','front-numeral',10,10,204,78) ],
  latent:    [ P('front','front-latent',334,218,62,26) ],
  watermark: [ P('front','watermark-ghost',...WMB), P('back','watermark-ghost',720 - WMB[0] - WMB[2],WMB[1],WMB[2],WMB[3],true) ],   // the back sees it mirrored
  register:  [ P('front','front-seethrough',526,256,146,58), P('back','back-seethrough',46,256,140,58) ],
  braille:   [ P('front','front-braille',40,282,112,26) ],
  tactile:   [ P('front','front-tactile-l',0,130,24,180), P('front','front-tactile-r',696,136,24,174) ],
  serial:    [ P('front','front-serial-h',40,260,108,24), P('front','front-serial-v',664,122,24,126) ],
  building:  [ P('front','front-building',186,50,236,270) ],
  signature: [ P('front','front-signature',36,176,166,34) ],
  skyline:   [ P('back','back-skyline',160,0,375,320) ],
};
// pieces shared with another feature: they light up, but hovering them names the other feature
const NO_HOVER = new Set([]);

// Detail callouts shown when a feature is zoomed into: [side, [[x, y], ...], label] in note units.
const DETAILS = {
  shimmer:   [['front', [[601, 32]], 'Green bauhinia'], ['front', [[601, 66]], 'Numeral 1000'],
              ['front', [[601, 100]], 'Ring of light moves with the tilt']],
  thread:    [['front', [[466, 90]], 'Woven in: three windows'], ['front', [[466, 178]], 'Large and small rings'],
              ['front', [[466, 266]], 'Rings move as you tilt']],
  emboss:    [['front', [[40, 50]], 'Raised ink'], ['front', [[178, 48]], 'The large 1000']],
  latent:    [['front', [[352, 231]], 'Hidden 1000'], ['front', [[390, 248]], 'Seen only when tilted']],
  watermark: [['front', [[585, 156]], 'Bauhinia flower, leaves, bud'], ['front', [[612, 213]], 'Bright numeral 1000'],
              ['back', [[135, 170]], 'Seen from the back too']],
  register:  [['front', [[548, 272]], 'Front half, one colour'], ['front', [[650, 300]], 'Joins the back half'],
              ['back', [[90, 290]], 'Back half']],
  braille:   [['front', [[96, 296]], 'Raised braille dots']],
  tactile:   [['front', [[12, 220]], 'Left edge'], ['front', [[708, 220]], 'Right edge']],
  serial:    [['front', [[95, 272]], 'Horizontal, bottom left'], ['front', [[676, 186]], 'Vertical, right']],
  building:  [['front', [[356, 100]], 'Standard Chartered Bank Building'], ['front', [[262, 250]], 'The Forum']],
  signature: [['front', [[66, 196]], 'Chief Financial Officer'], ['front', [[160, 196]], 'Chief Executive'],
              ['front', [[90, 241]], 'Hong Kong, 1 January 2018']],
  skyline:   [['back', [[300, 80]], 'Towers drawn in tiny digits'], ['back', [[460, 230]], 'The Central skyline'],
              ['back', [[622, 240]], 'Read upright: turn a quarter turn']],
};
