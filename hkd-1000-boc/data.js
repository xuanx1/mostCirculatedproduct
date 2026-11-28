// Plain script (not a module) so the page also works when opened straight from disk (file://)
// HK$1,000, Bank of China (Hong Kong) Limited (BOCHK), 2018 Series.
// Feature wording follows the Hong Kong Monetary Authority (hkma.gov.hk, 2018 Series Banknotes)
// and BOCHK's own 2018 New Series page (bochk.com); sources are listed in README.md.
// tag: the short name on the labels around the note; name: the full official name
const FEATURES = [
  {
    id:'shimmer', tag:'Shimmering pattern', name:'Dynamic shimmering pattern', zh:'動感光亮圖案', short:'A ring of light moves as you tilt',
    color:'#1d6b3a', color2:'#6fc28c',
    desc:'The green bauhinia with the numeral 1000 at the top right of the front. When the note is tilted, the shimmering ring in the pattern moves correspondingly.',
    how:'Tilt the note slightly. A <b>shimmering ring</b> should move across the green bauhinia with your movement. A copy stays flat and dull.',
    markers:[ { side:'front', x:603, y:62, ring:30, label:'Dynamic shimmering pattern' } ],
    icon:'<circle cx="8" cy="8" r="5"/><ellipse cx="8" cy="8" rx="5" ry="2"/>'
  },
  {
    id:'thread', tag:'Metallic thread', name:'Windowed metallic thread', zh:'開窗金屬線', short:'Large and small rings move',
    color:'#1f6f4a', color2:'#7ccf9e',
    desc:'A metallic thread woven into the paper surfaces in three green windows to the right of the bauhinia flower. When the note is tilted, the large and small rings on the metallic thread move correspondingly.',
    how:'Tilt the note and watch the <b>three green windows</b> beside the flower. The <b>large and small rings</b> on the thread should move as you tilt.',
    markers:[ { side:'front', x:466, y:180, ring:16, label:'Windowed metallic thread' } ],
    icon:'<path d="M8 1v14M5 3h6v3H5zM5 7h6v3H5zM5 11h6v3H5z"/>'
  },
  {
    id:'emboss', tag:'Embossed feel', name:'Embossed feel', zh:'凹凸手感', short:'Raised ink you can feel',
    color:'#c0391f', color2:'#ef8a6a',
    desc:'Raised printing gives the note a strong embossed feel by touch; BOCHK’s Chinese text names it intaglio printing (凹版印刷). The HKMA’s close-up for this feature shows the large 1000 at the top left of the front.',
    how:'Run a fingertip over the <b>large 1000</b> at the top left. The ink should feel <b>raised and rough</b>, not smooth like a print-out.',
    markers:[ { side:'front', x:110, y:48, ring:30, label:'Embossed feel' } ],
    icon:'<path d="M2 12h12M4 9h8M6 6h4"/>'
  },
  {
    id:'latent', tag:'Concealed 1000', name:'Concealed denomination', zh:'隱藏銀碼', short:'1000 appears when tilted',
    color:'#9a1f1a', color2:'#e06a5a',
    desc:'A denomination numeral hidden in the background. On this note it lies in the red diamond lattice of the Bank of China Tower, as the HKMA’s close-up shows. When the note is tilted under the light, the hidden numeral 1000 can be seen.',
    how:'Hold the note almost flat at eye level under a light and tilt it slowly. A <b>1000</b> should appear in the red lattice of the tower. (Here it is drawn: tilt the note well up or down.)',
    markers:[ { side:'front', x:230, y:219, ring:20, label:'Concealed denomination' } ],
    icon:'<path d="M2 11l6-6 6 6"/><path d="M5 11h6"/>'
  },
  {
    id:'watermark', tag:'Watermark', name:'Enhanced watermark', zh:'高透光水印', short:'Bauhinia flower, leaves, bud and 1000',
    color:'#8a6a3a', color2:'#c7a878',
    desc:'A watermark on the theme of the bauhinia flower, in the clear area at the right of the front, beside the vertical serial number. When the note is held up to the light, the flower, leaves, bud and the denomination numeral can be seen.',
    how:'Hold the note up to a light. In the plain area on the right you should see the <b>bauhinia flower, its leaves, a bud</b> and a bright <b>1000</b>, from either side.',
    markers:[
      { side:'front', x:585, y:165, ring:30, label:'Enhanced watermark' },
      { side:'back',  x:135, y:165, ring:30, label:'Watermark (reverse)' },
    ],
    icon:'<path d="M8 3c2 2 2 5 0 7-2-2-2-5 0-7zM3 8c2-1 4 0 5 2M13 8c-2-1-4 0-5 2"/>'
  },
  {
    id:'register', tag:'See-through 1000', name:'Fluorescent see-through denomination', zh:'熒光透視銀碼', short:'Two halves make 1000 against the light',
    color:'#d58a12', color2:'#f5c35a',
    desc:'Patterns on the front and back, each of a single colour under normal light. Seen from either side only part of the pattern shows; held up to the light, the front and back patterns fit perfectly to form the denomination numeral 1000. Under ultraviolet light the patterns appear as two fluorescent colours.',
    how:'Press <b>Hold up to the light</b>: the orange pieces at the bottom right of the front join the pieces printed on the back into a complete <b>1000</b>. Under a UV lamp they glow in two colours.',
    markers:[
      { side:'front', x:598, y:284, ring:24, label:'See-through denomination' },
      { side:'back',  x:118, y:284, ring:24, label:'See-through (back half)' },
    ],
    icon:'<path d="M3 4h3v8M9 4c3 0 4 2 4 4s-1 4-4 4"/>'
  },
  {
    id:'braille', tag:'Braille', name:'Braille', zh:'點字', short:'Bottom left corner',
    color:'#c0281e', color2:'#ee7a6e',
    desc:'Braille dots at the bottom left of the front. BOCHK keeps braille and tactile lines in the new series so that people with visual impairment can tell the denominations apart.',
    how:'Feel the <b>bottom left corner</b> of the front for the raised <b>braille dots</b>.',
    markers:[ { side:'front', x:96, y:296, ring:14, label:'Braille' } ],
    icon:'<circle cx="5" cy="4" r="1.3"/><circle cx="5" cy="8" r="1.3"/><circle cx="11" cy="8" r="1.3"/><circle cx="11" cy="12" r="1.3"/>'
  },
  {
    id:'tactile', tag:'Tactile lines', name:'Tactile lines', zh:'手感線', short:'Raised lines at both edges',
    color:'#c0281e', color2:'#ee7a6e',
    desc:'Rows of short slanting red lines near the left and right edges of the front, the other accessibility feature BOCHK keeps for people with visual impairment.',
    how:'Run a finger along the <b>left and right edges</b> of the front. The <b>red slanting lines</b> should feel raised.',
    markers:[ { side:'front', x:12, y:215, ring:14, label:'Tactile lines' } ],
    icon:'<path d="M3 4l4-2M3 8l4-2M3 12l4-2M9 6l4-2M9 10l4-2M9 14l4-2"/>'
  },
  {
    id:'serial', tag:'Serial numbers', name:'Serial numbers', zh:'號碼', short:'Twice on the front',
    color:'#2a2a2a', color2:'#8a8a8a',
    desc:'Every note carries its serial number twice on the front: horizontally at the bottom left and vertically on the right. The artwork shown carries a sample number, AB123456 (the HKMA’s marked images show AA000000).',
    how:'Both serials must match exactly, character for character.',
    markers:[
      { side:'front', x:94, y:270, ring:14, label:'Serial (horizontal)' },
      { side:'front', x:676, y:186, ring:14, label:'Serial (vertical)' },
    ],
    icon:'<path d="M2 4h2v8H2zM6 4h2v8H6zM10 4h2v8h-2z"/>'
  },
  {
    id:'tower', tag:'Bank of China Tower', name:'Bank of China Tower', zh:'中銀大廈', short:'The landmark, on diamond patterns',
    color:'#b4162a', color2:'#ee7a7a',
    desc:'Every BOCHK note of the 2018 Series shows the city’s landmark Bank of China Tower with a bauhinia on the front, in a new pattern for each note. On the HK$1,000 the background is diamond patterns, and the silhouette of a human head left in white on the right echoes the note’s theme of Hong Kong as a smart metropolis.',
    how:'Look at the tower’s lattice and its white cross-bracing: the lines should be fine, sharp and continuous, with no dot screen.',
    markers:[ { side:'front', x:210, y:150, ring:40, label:'Bank of China Tower' } ],
    icon:'<path d="M5 15V5l3-4 3 4v10M5 9l6-4M5 5l6 4M5 13l6-4"/>'
  },
  {
    id:'flower', tag:'Bauhinia', name:'Bauhinia flower', zh:'紫荊花', short:'Hong Kong’s floral emblem',
    color:'#d0602a', color2:'#f5a26a',
    desc:'The bauhinia, Hong Kong’s floral emblem, shown large beside the Bank of China Tower. BOCHK pairs the flower and the tower on the front of every note of its new series.',
    how:'The flower should be finely shaded, its petals crisp at the edges where they cross the tower and the diamond pattern.',
    markers:[ { side:'front', x:345, y:140, ring:36, label:'Bauhinia' } ],
    icon:'<path d="M8 2c2 2 2 4 0 6-2-2-2-4 0-6zM8 8c3-1 5 0 6 2-3 1-5 0-6-2zM8 8c-3-1-5 0-6 2 3 1 5 0 6-2zM8 8v6"/>'
  },
  {
    id:'signature', tag:'Signature', name:'Signature and date', zh:'簽名及日期', short:'Chief Executive · 1 January 2018',
    color:'#7a3a2a', color2:'#c78870',
    desc:'The note promises to pay the bearer on demand at the bank’s office here (憑票即付), by order of the Board of Directors (承董事會命), and is signed in red by the bank’s Chief Executive (總裁, as printed under the signature). It is dated Hong Kong, 1 January 2018 (香港 二〇一八年一月一日).',
    how:'The signature and the printed date and title should be sharp and complete.',
    markers:[ { side:'front', x:90, y:195, ring:16, label:'Signature' } ],
    icon:'<path d="M2 11c2-3 3-6 4-6s0 6 2 6 2-4 3-4 1 3 3 3"/>'
  },
  {
    id:'smart', tag:'A Smart Metropolis', name:'A Smart Metropolis', zh:'智慧都會', short:'The reverse, printed upright',
    color:'#d0602a', color2:'#f5a26a',
    desc:'The reverse of every 2018 Series HK$1,000 note shows Hong Kong as an international financial centre. BOCHK’s design, “A Smart Metropolis”, shows two people in profile with their brain structure made up of the digits 0 and 1, and a globe: human wisdom, the city’s talent and global vision, and its success as a world-class smart metropolis. Like the whole series, the reverse is laid out vertically.',
    how:'Turn the note over and a quarter turn. The 0s and 1s in the head should be clear and evenly printed, with clean edges against the plain paper.',
    markers:[ { side:'back', x:370, y:150, ring:40, label:'A Smart Metropolis' } ],
    icon:'<circle cx="7" cy="7" r="5"/><path d="M12 7c2 1 2 3 1 5M5 6h1M8 6h1M5 9h4"/>'
  },
];

// Exploded view: the note pulled apart in both directions. The paper (with the thread and the
// watermark inside it) is the core; the reverse is printed on one side and the obverse on the other.
const LAYERS = [
  { id:'r-seethrough', name:'See-through (back half)', group:'Reverse', side:'back', feature:'register', kind:'pieces',
    pieces:[ ['back-seethrough', 46,254,140,60] ] },
  { id:'r-offset',   name:'Printed reverse',  group:'Reverse', side:'back',  feature:'smart',     kind:'art' },
  { id:'thread',     name:'Metallic thread',  group:'Paper',   side:'front', feature:'thread',    kind:'pieces',
    pieces:[ ['front-thread', 448,52,36,256] ] },
  { id:'substrate',  name:'Banknote paper',   group:'Paper',   side:'front', feature:null,        kind:'paper', core:true },
  { id:'watermark',  name:'Watermark',        group:'Paper',   side:'front', feature:'watermark', kind:'pieces',
    pieces:[ ['watermark-ghost', 527.99,108.43,135.44,146.19] ] },
  { id:'offset',     name:'Printed front',    group:'Obverse', side:'front', feature:'tower',     kind:'art' },
  { id:'raised',     name:'Raised ink',       group:'Obverse', side:'front', feature:'emboss',    kind:'pieces',
    pieces:[ ['front-numeral', 10,10,210,82], ['front-tactile-l', 0,132,24,166], ['front-tactile-r', 694,136,26,178],
             ['front-braille', 40,282,116,26] ] },
  { id:'shimmer',    name:'Shimmering ink',   group:'Obverse', side:'front', feature:'shimmer',   kind:'pieces',
    pieces:[ ['front-shimmer', 544,12,118,100] ] },
  { id:'seethrough', name:'See-through (front half)', group:'Obverse', side:'front', feature:'register', kind:'pieces',
    pieces:[ ['front-seethrough', 526,254,148,60] ] },
  { id:'serial',     name:'Serial numbers',   group:'Obverse', side:'front', feature:'serial',    kind:'pieces',
    pieces:[ ['front-serial-h', 38,258,112,24], ['front-serial-v', 664,122,24,128] ] },
  { id:'uv',         name:'UV: two colours',  group:'Obverse', side:'front', feature:'register',  kind:'uv' },
];

const TWEAK_DEFAULS = {
  "defaultActive": ["shimmer","thread","emboss","latent","watermark","register","braille","tactile","serial","tower","flower","signature","smart"]
};

// Glow highlights: each feature's own cut-out (assets/layers/<src>.png) laid exactly over the artwork
// at its box [x, y, w, h] in 720x320 note space (boxes from assets/boxes.js when present).
const P = (side, src, x, y, w, h, mirror) => ({ side, src, box: (!mirror && typeof BOXES !== 'undefined' && BOXES[src]) || [x, y, w, h], mirror:!!mirror });
const WMB = (typeof BOXES !== 'undefined' && BOXES['watermark-ghost']) || [527.99, 108.43, 135.44, 146.19];
const GLOW = {
  shimmer:   [ P('front','front-shimmer',544,12,118,100) ],
  thread:    [ P('front','front-thread',448,52,36,256) ],
  emboss:    [ P('front','front-numeral',10,10,210,82) ],
  latent:    [ P('front','front-latent',188,206,84,26) ],
  watermark: [ P('front','watermark-ghost',...WMB), P('back','watermark-ghost',720 - WMB[0] - WMB[2],WMB[1],WMB[2],WMB[3],true) ],   // the back sees it mirrored
  register:  [ P('front','front-seethrough',526,254,148,60), P('back','back-seethrough',46,254,140,60) ],
  braille:   [ P('front','front-braille',40,282,116,26) ],
  tactile:   [ P('front','front-tactile-l',0,132,24,166), P('front','front-tactile-r',694,136,26,178) ],
  serial:    [ P('front','front-serial-h',38,258,112,24), P('front','front-serial-v',664,122,24,128) ],
  tower:     [ P('front','front-tower',158,40,170,280) ],
  flower:    [ P('front','front-flower',255,55,170,195) ],
  signature: [ P('front','front-signature',62,183,60,23) ],
  smart:     [ P('back','back-smart',225,18,370,274) ],
};
// pieces shared with another feature: they light up, but hovering them names the other feature
const NO_HOVER = new Set([]);

// Detail callouts shown when a feature is zoomed into: [side, [[x, y], ...], label] in note units.
const DETAILS = {
  shimmer:   [['front', [[603, 30]], 'Green bauhinia'], ['front', [[603, 62]], 'Numeral 1000'],
              ['front', [[603, 98]], 'Ring of light moves with the tilt']],
  thread:    [['front', [[466, 90]], 'Woven in: three windows'], ['front', [[466, 178]], 'Large and small rings'],
              ['front', [[466, 272]], 'Rings move as you tilt']],
  emboss:    [['front', [[36, 50]], 'Raised ink'], ['front', [[178, 48]], 'Large 1000, top left']],
  latent:    [['front', [[215, 219]], 'Hidden 1000'], ['front', [[262, 230]], 'In the tower’s red lattice']],
  watermark: [['front', [[575, 150]], 'Bauhinia flower, leaves, bud'], ['front', [[577, 230]], 'Bright numeral 1000'],
              ['back', [[145, 170]], 'Seen from the back too']],
  register:  [['front', [[545, 270]], 'Front half, one colour'], ['front', [[650, 300]], 'Joins the back half'],
              ['back', [[90, 290]], 'Back half']],
  braille:   [['front', [[96, 296]], 'Raised braille dots']],
  tactile:   [['front', [[12, 215]], 'Left edge'], ['front', [[707, 225]], 'Right edge']],
  serial:    [['front', [[94, 270]], 'Horizontal, bottom left'], ['front', [[676, 186]], 'Vertical, right']],
  tower:     [['front', [[205, 120]], 'Bank of China Tower'], ['front', [[250, 270]], 'White cross-bracing']],
  flower:    [['front', [[340, 110]], 'Bauhinia, the floral emblem'], ['front', [[395, 215]], 'Over the diamond pattern']],
  signature: [['front', [[90, 195]], 'Chief Executive'], ['front', [[100, 228]], 'Hong Kong, 1 January 2018']],
  smart:     [['back', [[340, 140]], 'A brain of 0s and 1s'], ['back', [[425, 250]], 'A globe: global vision'],
              ['back', [[530, 170]], 'Two people in profile']],
};
