// Plain script (not a module) so the page also works when opened straight from disk (file://)
// HK$1,000, The Hongkong and Shanghai Banking Corporation Limited (HSBC), 2018 Series.
// Feature wording follows the Hong Kong Monetary Authority (hkma.gov.hk, 2018 Series Banknotes)
// and HSBC's own page (hsbc.com.hk/banknotes-2018); sources are listed in README.md.
// tag: the short name on the labels around the note; name: the full official name
const FEATURES = [
  {
    id:'shimmer', tag:'Shimmering pattern', name:'Dynamic shimmering pattern', zh:'動感光亮圖案', short:'A ring of light moves as you tilt',
    color:'#1d6b3a', color2:'#6fc28c',
    desc:'The green bauhinia with the numeral 1000 at the top right of the front. When the note is tilted, the shimmering ring in the pattern moves correspondingly; HSBC describes it as a shimmering horizontal circle that appears to rotate around the numeral as the note is tilted.',
    how:'Tilt the note up and down, then side to side. A <b>ring of light</b> should travel across the green bauhinia with your movement. A copy stays flat and dull.',
    markers:[ { side:'front', x:603, y:63, ring:30, label:'Dynamic shimmering pattern' } ],
    icon:'<circle cx="8" cy="8" r="5"/><ellipse cx="8" cy="8" rx="5" ry="2"/>'
  },
  {
    id:'thread', tag:'Metallic thread', name:'Windowed metallic thread', zh:'開窗金屬線', short:'Large and small rings move',
    color:'#1f6f4a', color2:'#7ccf9e',
    desc:'A metallic thread woven into the paper surfaces in three windows down the middle of the front. When the note is tilted, the large and small rings on the metallic thread move correspondingly.',
    how:'Tilt the note and watch the <b>three green windows</b> in the middle of the front. The <b>large and small rings</b> on the thread should move as you tilt.',
    markers:[ { side:'front', x:466, y:180, ring:16, label:'Windowed metallic thread' } ],
    icon:'<path d="M8 1v14M5 3h6v3H5zM5 7h6v3H5zM5 11h6v3H5z"/>'
  },
  {
    id:'emboss', tag:'Embossed feel', name:'Embossed feel', zh:'凹凸手感', short:'Raised ink you can feel',
    color:'#c0391f', color2:'#ef8a6a',
    desc:'Raised printing gives the note a strong embossed feel by touch (the HKMA’s Chinese text names it intaglio printing). The large numerals at the top left of the front are a high-tactility numeral: HSBC lists them among the features that help people with visual impairments.',
    how:'Run a fingertip over the <b>large 1000</b> at the top left. The ink should feel <b>raised and rough</b>, not smooth like a print-out.',
    markers:[ { side:'front', x:150, y:48, ring:30, label:'Embossed feel' } ],
    icon:'<path d="M2 12h12M4 9h8M6 6h4"/>'
  },
  {
    id:'latent', tag:'Concealed 1000', name:'Concealed denomination', zh:'隱藏銀碼', short:'1000 appears when tilted',
    color:'#9a1f1a', color2:'#e06a5a',
    desc:'A denomination numeral hidden in the background at the bottom of the note, in the red area below the lion. When the note is tilted under the light, the hidden numeral 1000 can be seen.',
    how:'Hold the note almost flat at eye level under a light and tilt it slowly. A <b>1000</b> should appear in the red area below the lion. (Here it is drawn: tilt the note well up or down.)',
    markers:[ { side:'front', x:401, y:272, ring:20, label:'Concealed denomination' } ],
    icon:'<path d="M2 11l6-6 6 6"/><path d="M5 11h6"/>'
  },
  {
    id:'watermark', tag:'Watermark', name:'Enhanced watermark', zh:'高透光水印', short:'Bauhinia flower, leaves, bud and 1000',
    color:'#8a6a3a', color2:'#c7a878',
    desc:'A watermark on the theme of the bauhinia flower, in the clear area on the right side of the front. When the note is held up to the light, the flower, leaves, bud and the denomination numeral can be seen.',
    how:'Hold the note up to a light. In the plain area on the right you should see the <b>bauhinia flower, its leaves, a bud</b> and a bright <b>1000</b>, from either side.',
    markers:[
      { side:'front', x:590, y:175, ring:30, label:'Enhanced watermark' },
      { side:'back',  x:130, y:175, ring:30, label:'Watermark (reverse)' },
    ],
    icon:'<path d="M8 3c2 2 2 5 0 7-2-2-2-5 0-7zM3 8c2-1 4 0 5 2M13 8c-2-1-4 0-5 2"/>'
  },
  {
    id:'register', tag:'See-through 1000', name:'Fluorescent see-through denomination', zh:'熒光透視銀碼', short:'Two halves make 1000 against the light',
    color:'#d58a12', color2:'#f5c35a',
    desc:'Patterns on the front and back, each of a single colour under normal light. Seen from either side only part of the pattern shows; held up to the light, the front and back patterns fit perfectly to form the denomination numeral 1000. Under ultraviolet light the patterns appear as two fluorescent colours.',
    how:'Press <b>Hold up to the light</b>: the orange pieces at the bottom right of the front join the pieces printed on the back into a complete <b>1000</b>. Under a UV lamp they glow in two colours.',
    markers:[
      { side:'front', x:590, y:285, ring:24, label:'See-through denomination' },
      { side:'back',  x:116, y:285, ring:24, label:'See-through (back half)' },
    ],
    icon:'<path d="M3 4h3v8M9 4c3 0 4 2 4 4s-1 4-4 4"/>'
  },
  {
    id:'iridescent', tag:'Iridescent mane', name:'Iridescent pattern', zh:'珠光圖案', short:'On the lion’s mane, under bright light',
    color:'#b05a8a', color2:'#e3a6c8',
    desc:'An iridescent pattern on the mane of “Stitt”, the HSBC lion on the front. It shimmers when the note is tilted under bright light. HSBC prints it on all five notes of the 2018 Series.',
    how:'Tilt the note under a bright light and watch the <b>lion’s mane</b>. A pale, pearly sheen should flash across it.',
    markers:[ { side:'front', x:232, y:178, ring:26, label:'Iridescent pattern' } ],
    icon:'<path d="M3 12c1-5 4-8 10-9M5 13c1-4 3-6 8-7"/>'
  },
  {
    id:'microtext', tag:'Microtext', name:'Microtext', zh:'微縮字', short:'HSBC and hexagons, in the large 1000',
    color:'#a43a2a', color2:'#e08a70',
    desc:'The large numerals at the top left corner of the front carry microtext: a hexagon pattern and the letters “HSBC”, too small to read without magnification.',
    how:'Use a <b>magnifier</b> on the large 1000 at the top left. Inside the digits you should find tiny <b>hexagons</b> and the letters <b>HSBC</b>, sharp-edged.',
    markers:[ { side:'front', x:40, y:52, ring:16, label:'Microtext' } ],
    icon:'<path d="M2 4h12M2 8h12M2 12h8"/>'
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
    desc:'Rows of short slanting lines printed in raised ink near the left and right edges of the front, another accessibility feature for people with visual impairments.',
    how:'Run a finger along the <b>left and right edges</b> of the front. The <b>red slanting lines</b> should feel raised.',
    markers:[ { side:'front', x:12, y:220, ring:14, label:'Tactile lines' } ],
    icon:'<path d="M3 4l4-2M3 8l4-2M3 12l4-2M9 6l4-2M9 10l4-2M9 14l4-2"/>'
  },
  {
    id:'serial', tag:'Serial numbers', name:'Serial numbers', zh:'號碼', short:'Twice on the front',
    color:'#2a2a2a', color2:'#8a8a8a',
    desc:'Every note carries its serial number twice on the front: horizontally at the bottom left and vertically on the right. HSBC’s new series started at the prefix AA in every denomination. The artwork shown carries a sample number, AB123456.',
    how:'Both serials must match exactly, character for character.',
    markers:[
      { side:'front', x:95, y:270, ring:14, label:'Serial (horizontal)' },
      { side:'front', x:678, y:188, ring:14, label:'Serial (vertical)' },
    ],
    icon:'<path d="M2 4h2v8H2zM6 4h2v8H6zM10 4h2v8h-2z"/>'
  },
  {
    id:'lion', tag:'Stitt the lion', name:'Stitt, the HSBC lion', zh:'銅獅「施迪」', short:'And the Main Building, in watercolour',
    color:'#c4502a', color2:'#f09a6a',
    desc:'The front of every HSBC note bears the bank’s traditional elements: the bronze lion “Stitt”, an icon of HSBC’s notes since 1972 and a guard of its Hong Kong headquarters since 1935, and the Main Building at 1 Queen’s Road Central. The 2018 Series is the first Hong Kong banknote design painted in watercolour; traditional banknote engraving techniques are retained.',
    how:'Look at the lion and the building behind it: the painting should be crisp and continuous, with no dot screen.',
    markers:[ { side:'front', x:330, y:150, ring:40, label:'Stitt' } ],
    icon:'<circle cx="8" cy="7" r="4"/><path d="M4 14c1-2 3-3 4-3s3 1 4 3"/>'
  },
  {
    id:'signature', tag:'Signature', name:'Signature and date', zh:'簽名及日期', short:'Chief Executive · 1 January 2018',
    color:'#7a3a2a', color2:'#c78870',
    desc:'The note promises to pay the bearer on demand at the bank’s office here, by order of the Board of Directors, and is signed by HSBC’s Chief Executive (行政總裁). It is dated Hong Kong, 1 January 2018 (香港 二〇一八年一月一日).',
    how:'The signature and the printed date and title should be sharp and complete.',
    markers:[ { side:'front', x:88, y:190, ring:16, label:'Signature' } ],
    icon:'<path d="M2 11c2-3 3-6 4-6s0 6 2 6 2-4 3-4 1 3 3 3"/>'
  },
  {
    id:'metropolis', tag:'Financial Metropolis', name:'Financial Metropolis', zh:'金融都會', short:'The reverse, printed upright',
    color:'#d0602a', color2:'#f5a26a',
    desc:'The reverse of every 2018 Series HK$1,000 note shows Hong Kong as an international financial centre. HSBC’s design is a panoramic fisheye view of the Central business district, the harbour and the mountain range with Lion Rock behind. Like the whole series, the reverse is laid out vertically: turn the note a quarter turn to read it.',
    how:'Turn the note over and a quarter turn. The picture should be finely detailed, with clean edges against the plain paper above it.',
    markers:[ { side:'back', x:430, y:160, ring:40, label:'Financial Metropolis' } ],
    icon:'<path d="M3 13V8h2v5M7 13V4h2v9M11 13V6h2v7M2 13h12"/>'
  },
];

// Exploded view: the note pulled apart in both directions. The paper (with the thread and the
// watermark inside it) is the core; the reverse is printed on one side and the obverse on the other.
const LAYERS = [
  { id:'r-seethrough', name:'See-through (back half)', group:'Reverse', side:'back', feature:'register', kind:'pieces',
    pieces:[ ['back-seethrough', 46,256,142,56] ] },
  { id:'r-offset',   name:'Printed reverse',  group:'Reverse', side:'back',  feature:'metropolis', kind:'art' },
  { id:'thread',     name:'Metallic thread',  group:'Paper',   side:'front', feature:'thread',    kind:'pieces',
    pieces:[ ['front-thread', 449,52,34,256] ] },
  { id:'substrate',  name:'Banknote paper',   group:'Paper',   side:'front', feature:null,        kind:'paper', core:true },
  { id:'watermark',  name:'Watermark',        group:'Paper',   side:'front', feature:'watermark', kind:'pieces',
    pieces:[ ['watermark-ghost', 502.65,126.34,168.78,102.47] ] },
  { id:'offset',     name:'Printed front',    group:'Obverse', side:'front', feature:'lion',      kind:'art' },
  { id:'raised',     name:'Raised ink',       group:'Obverse', side:'front', feature:'emboss',    kind:'pieces',
    pieces:[ ['front-numeral', 10,10,208,80], ['front-tactile-l', 0,128,25,181], ['front-tactile-r', 694,134,26,175],
             ['front-braille', 42,284,112,24] ] },
  { id:'shimmer',    name:'Shimmering ink',   group:'Obverse', side:'front', feature:'shimmer',   kind:'pieces',
    pieces:[ ['front-shimmer', 546,14,114,98] ] },
  { id:'pearl',      name:'Iridescent ink',   group:'Obverse', side:'front', feature:'iridescent', kind:'pieces',
    pieces:[ ['front-mane', 160,46,270,226] ] },
  { id:'seethrough', name:'See-through (front half)', group:'Obverse', side:'front', feature:'register', kind:'pieces',
    pieces:[ ['front-seethrough', 526,256,144,56] ] },
  { id:'serial',     name:'Serial numbers',   group:'Obverse', side:'front', feature:'serial',    kind:'pieces',
    pieces:[ ['front-serial-h', 41,259,108,22], ['front-serial-v', 667,124,23,127] ] },
  { id:'uv',         name:'UV: two colours',  group:'Obverse', side:'front', feature:'register',  kind:'uv' },
];

const TWEAK_DEFAULS = {
  "defaultActive": ["shimmer","thread","emboss","latent","watermark","register","iridescent","microtext","braille","tactile","serial","lion","signature","metropolis"]
};

// Glow highlights: each feature's own cut-out (assets/layers/<src>.png) laid exactly over the artwork
// at its box [x, y, w, h] in 720x320 note space (boxes from assets/boxes.js when present).
const P = (side, src, x, y, w, h, mirror) => ({ side, src, box: (!mirror && typeof BOXES !== 'undefined' && BOXES[src]) || [x, y, w, h], mirror:!!mirror });
const WMB = (typeof BOXES !== 'undefined' && BOXES['watermark-ghost']) || [502.65, 126.34, 168.78, 102.47];
const GLOW = {
  shimmer:   [ P('front','front-shimmer',546,14,114,98) ],
  thread:    [ P('front','front-thread',449,52,34,256) ],
  emboss:    [ P('front','front-numeral',10,10,208,80) ],
  latent:    [ P('front','front-latent',355,252,92,40) ],
  watermark: [ P('front','watermark-ghost',...WMB), P('back','watermark-ghost',720 - WMB[0] - WMB[2],WMB[1],WMB[2],WMB[3],true) ],   // the back sees it mirrored
  register:  [ P('front','front-seethrough',526,256,144,56), P('back','back-seethrough',46,256,142,56) ],
  iridescent:[ P('front','front-mane',160,46,270,226) ],
  microtext: [ P('front','front-numeral',10,10,208,80) ],
  braille:   [ P('front','front-braille',42,284,112,24) ],
  tactile:   [ P('front','front-tactile-l',0,128,25,181), P('front','front-tactile-r',694,134,26,175) ],
  serial:    [ P('front','front-serial-h',41,259,108,22), P('front','front-serial-v',667,124,23,127) ],
  lion:      [ P('front','front-lion',160,46,270,226) ],
  signature: [ P('front','front-signature',54,174,76,32) ],
  metropolis:[ P('back','back-metropolis',262,0,334,320) ],
};
// pieces shared with another feature: they light up, but hovering them names the other feature
const NO_HOVER = new Set(['microtext']);

// Detail callouts shown when a feature is zoomed into: [side, [[x, y], ...], label] in note units.
const DETAILS = {
  shimmer:   [['front', [[603, 30]], 'Green bauhinia'], ['front', [[603, 60]], 'Numeral 1000'],
              ['front', [[603, 96]], 'Ring of light moves with the tilt']],
  thread:    [['front', [[466, 90]], 'Woven in: three windows'], ['front', [[466, 178]], 'Large and small rings'],
              ['front', [[466, 270]], 'Rings move as you tilt']],
  emboss:    [['front', [[36, 50]], 'Raised ink'], ['front', [[178, 48]], 'High-tactility numeral']],
  latent:    [['front', [[380, 272]], 'Hidden 1000'], ['front', [[430, 290]], 'Seen only when tilted']],
  watermark: [['front', [[565, 165]], 'Bauhinia flower, leaves, bud'], ['front', [[592, 213]], 'Bright numeral 1000'],
              ['back', [[150, 170]], 'Seen from the back too']],
  register:  [['front', [[540, 272]], 'Front half, one colour'], ['front', [[640, 300]], 'Joins the back half'],
              ['back', [[90, 290]], 'Back half']],
  iridescent:[['front', [[215, 150]], 'Stitt’s mane'], ['front', [[260, 235]], 'Pearly sheen when tilted']],
  microtext: [['front', [[36, 50]], 'HSBC in microtext'], ['front', [[180, 28]], 'Hexagon pattern']],
  braille:   [['front', [[96, 296]], 'Raised braille dots']],
  tactile:   [['front', [[12, 220]], 'Left edge'], ['front', [[707, 220]], 'Right edge']],
  serial:    [['front', [[95, 270]], 'Horizontal, bottom left'], ['front', [[678, 188]], 'Vertical, right']],
  lion:      [['front', [[360, 160]], 'Stitt, in watercolour'], ['front', [[155, 140]], 'HSBC Main Building']],
  signature: [['front', [[88, 190]], 'Chief Executive'], ['front', [[100, 228]], 'Hong Kong, 1 January 2018']],
  metropolis:[['back', [[440, 150]], 'Central, through a fisheye lens'], ['back', [[288, 150]], 'Hills and Lion Rock'],
              ['back', [[620, 240]], 'Read upright: turn a quarter turn']],
};
