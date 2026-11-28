// Plain script (not a module) so the page also works when opened straight from disk (file://)
// US $100 Federal Reserve note (2013 design, this note Series 2021).
// Feature wording follows the U.S. Currency Education Program, uscurrency.gov/denominations/100.
const FEATURES = [
  {
    id:'ribbon', name:'3-D Security Ribbon', short:'Bells change to 100s as you tilt',
    color:'#2f5fb3', color2:'#7aa2e8',
    desc:'A blue ribbon woven into the paper, not printed on it. Tilt the note and the bells on it change to 100s as they move: tilt it back and forth and they move side to side; tilt it side to side and they move up and down.',
    how:'Tilt the note back and forth while watching the blue ribbon. The <b>bells should change to 100s</b> and move at right angles to the way you tilt.',
    markers:[ { side:'front', x:386, y:160, ring:20, label:'3-D ribbon', outline:{shape:'rect', x:371, y:0, w:31, h:320, rx:2} } ],
    icon:'<path d="M6 1v14M10 1v14M6 4h4M6 8h4M6 12h4"/>'
  },
  {
    id:'bell', name:'Bell in the Inkwell', short:'Copper to green, the bell appears and disappears',
    color:'#9a5a24', color2:'#d99a5c',
    desc:'A colour-shifting bell inside the copper inkwell. As the note tilts the bell changes from copper to green, which makes it seem to appear and disappear within the inkwell.',
    how:'Tilt the note and watch the inkwell. The <b>bell should shift from copper to green</b> and seem to fade in and out.',
    markers:[ { side:'front', x:450, y:240, ring:20, label:'Bell in the Inkwell', outline:{shape:'rect', x:413, y:198, w:74, h:86, rx:3} } ],
    icon:'<path d="M5 12h6M6 12V8a2 2 0 0 1 4 0v4M8 3v2"/>'
  },
  {
    id:'ovi', name:'Colour-shifting 100', short:'Lower right corner, copper to green',
    color:'#2f7a5a', color2:'#7ac79d',
    desc:'The numeral 100 in the lower right corner of the front is printed in colour-shifting ink. Tilt the note and it shifts from copper to green.',
    how:'Tilt the note and watch the <b>100</b> in the lower right corner. It should shift from copper to green. A flat copy keeps one colour.',
    markers:[ { side:'front', x:610, y:266, ring:22, label:'Colour-shifting 100', outline:{shape:'rect', x:545, y:243, w:130, h:46, rx:4} } ],
    icon:'<circle cx="8" cy="8" r="5"/><path d="M8 3v10M3 8h10"/>'
  },
  {
    id:'watermark', name:'Portrait watermark', short:'Franklin, visible from both sides',
    color:'#8a6a3a', color2:'#c7a878',
    desc:'A faint image of Benjamin Franklin formed in the paper itself, in the blank space to the right of the portrait. Hold the note to light to see it; it is visible from both sides of the note.',
    how:'Hold the note up to a light. A <b>faint Franklin</b> should appear in the blank space to the right of the portrait, from either side.',
    markers:[
      { side:'front', x:653, y:121, ring:30, label:'Watermark', outline:{shape:'ellipse', cx:653, cy:121, rx:40, ry:55} },
      { side:'back',  x:67,  y:121, ring:30, label:'Watermark (reverse)', outline:{shape:'ellipse', cx:67, cy:121, rx:40, ry:55} },
    ],
    icon:'<circle cx="8" cy="8" r="5"/><path d="M3 14c1-2 3-3 5-3s4 1 5 3"/>'
  },
  {
    id:'thread', name:'Security thread', short:'USA 100, glows pink under UV',
    color:'#b0408a', color2:'#e08ac0',
    desc:'An embedded thread runs vertically to the left of the portrait. It is imprinted with USA and 100 in an alternating pattern, is visible from both sides when the note is held to light, and glows pink under ultraviolet light.',
    how:'Hold the note to light to see the thread and read <b>USA 100</b> on it. Under a UV lamp it should <b>glow pink</b>.',
    markers:[ { side:'front', x:159, y:160, ring:14, label:'Security thread', outline:{shape:'rect', x:156, y:0, w:7, h:320, rx:2} } ],
    icon:'<path d="M8 1v14M5 3h6M5 7h6M5 11h6"/>'
  },
  {
    id:'intaglio', name:'Raised printing', short:'Franklin’s shoulder feels rough',
    color:'#c43a2b', color2:'#e88a7e',
    desc:'Enhanced intaglio printing leaves the ink standing up from the paper. Franklin’s shoulder on the left side of the note should feel rough to the touch, and traditional raised printing can be felt throughout the note.',
    how:'Move a finger up and down <b>Franklin’s shoulder</b> on the left side. It should feel rough, not smooth.',
    markers:[ { side:'front', x:200, y:262, ring:24, label:'Franklin’s shoulder', outline:{shape:'rect', x:108, y:230, w:200, h:62, rx:4} } ],
    icon:'<path d="M2 12h12M4 9h8M6 6h4"/>'
  },
  {
    id:'fineline', name:'Engraved portrait', short:'Benjamin Franklin, in line',
    color:'#8a4a3a', color2:'#c7886a',
    desc:'The portrait of Benjamin Franklin is engraved entirely in fine lines: every shade of his face, hair and coat comes from line spacing and cross-hatching. A scanner or office printer turns this line-work into dots and grey smears.',
    how:'Use a <b>10× loupe</b> on Franklin’s face and hair. Each line should be crisp and separate; blur or dots mean a printed reproduction.',
    markers:[ { side:'front', x:270, y:120, ring:40, label:'Engraved portrait', outline:{shape:'rect', x:160, y:14, w:212, h:200, rx:4} } ],
    icon:'<circle cx="8" cy="8" r="5" fill="none"/><circle cx="8" cy="8" r="3" fill="none"/>'
  },
  {
    id:'microprint', name:'Microprinting', short:'Tiny text in four places',
    color:'#6b4a22', color2:'#a87a40',
    desc:'Text too small to read without magnification: THE UNITED STATES OF AMERICA on Franklin’s jacket collar, USA 100 around the blank space that holds the watermark, ONE HUNDRED USA along the golden quill, and small 100s in the note borders.',
    how:'Use a magnifier on the four places: the <b>jacket collar</b>, around the <b>watermark space</b>, along the <b>golden quill</b>, and the <b>borders</b>. The letters should be sharp.',
    markers:[ { side:'front', x:480, y:170, ring:18, label:'Golden quill', outline:{shape:'rect', x:364, y:38, w:248, h:258, rx:4} } ],
    icon:'<path d="M2 4h12M2 8h12M2 12h8"/>'
  },
  {
    id:'gold100', name:'Large gold 100', short:'Back, for low vision',
    color:'#b07a1c', color2:'#e0b060',
    desc:'A large gold numeral 100 on the back of the note helps people with visual impairments tell the denomination.',
    how:'Turn the note over. The <b>large gold 100</b> fills the right side of the back.',
    markers:[ { side:'back', x:628, y:150, ring:30, label:'Large gold 100', outline:{shape:'rect', x:573, y:37, w:112, h:228, rx:4} } ],
    icon:'<path d="M4 3v10M8 4a2 2 0 0 1 2 2v4a2 2 0 0 1-4 0V6a2 2 0 0 1 2-2z"/>'
  },
  {
    id:'serial', name:'Serial numbers', short:'Printed twice on the front',
    color:'#2f7a3a', color2:'#7ac78a',
    desc:'A unique combination of eleven letters and numbers appears twice on the front of the note, printed in green: once at the upper left and once at the right.',
    how:'Both serials must match exactly. On this note both read <b>QC 02836101 A</b>.',
    markers:[
      { side:'front', x:110, y:72, ring:16, label:'Serial (left)', outline:{shape:'rect', x:29, y:61, w:165, h:23, rx:2} },
      { side:'front', x:596, y:219, ring:16, label:'Serial (right)', outline:{shape:'rect', x:500, y:204, w:193, h:29, rx:2} },
    ],
    icon:'<path d="M2 4h2v8H2zM6 4h2v8H6zM10 4h2v8h-2z"/>'
  },
  {
    id:'frb', name:'Federal Reserve seal', short:'And the issuing bank',
    color:'#3a3a3a', color2:'#8a8a8a',
    desc:'A black seal to the left of the portrait represents the entire Federal Reserve System. The letter and number beneath the left serial number identify the Federal Reserve Bank that distributed the note: here C3, the Federal Reserve Bank of Philadelphia, the third district.',
    how:'Check the seal is sharp and the <b>letter–number pair</b> below the left serial matches one Federal Reserve Bank (A1 Boston to L12 San Francisco).',
    markers:[
      { side:'front', x:119, y:153, ring:22, label:'Federal Reserve seal', outline:{shape:'ellipse', cx:119, cy:152.6, rx:37, ry:38.7} },
      { side:'front', x:45,  y:103, ring:12, label:'Bank indicator C3', outline:{shape:'rect', x:28, y:91, w:34, h:24, rx:2} },
    ],
    icon:'<circle cx="8" cy="8" r="5"/><circle cx="8" cy="8" r="2"/>'
  },
  {
    id:'treasury', name:'Treasury seal', short:'Green, right of the portrait',
    color:'#2f7a3a', color2:'#7ac78a',
    desc:'The seal of the Department of the Treasury, printed in green to the right of the portrait, over the large outlined 100.',
    how:'The seal’s points and lettering should be sharp, in a clean green.',
    markers:[ { side:'front', x:551, y:142, ring:22, label:'Treasury seal', outline:{shape:'ellipse', cx:551, cy:142, rx:44, ry:44} } ],
    icon:'<circle cx="8" cy="8" r="5"/><path d="M8 3v10"/>'
  },
  {
    id:'signature', name:'Signatures', short:'Treasurer and Secretary of the Treasury',
    color:'#6b4a22', color2:'#c7a270',
    desc:'Each note carries the signatures of the Secretary of the Treasury and the Treasurer of the United States in office for its series. This Series 2021 note is signed by Janet L. Yellen and Lynn Malerba.',
    how:'Check the signatures and titles match the <b>series year</b> printed on the front (here Series 2021).',
    markers:[ { side:'front', x:84, y:222, ring:16, label:'Signatures', outline:{shape:'rect', x:27, y:192, w:120, h:74, rx:2} } ],
    icon:'<path d="M2 11c2-3 3-6 4-6s0 6 2 6 2-4 3-4 1 3 3 3"/>'
  },
  {
    id:'eurion', name:'EURion constellation', short:'The small yellow 100s',
    color:'#b08a14', color2:'#e6c34d',
    desc:'The small yellow 100s scattered on both sides of the note. Their zeros form the EURion constellation, a fixed pattern of small rings that many colour copiers and some imaging software detect so that they refuse to reproduce the note.',
    how:'Look for the <b>small yellow 100s</b> around the Federal Reserve seal on the front and at the top of the back. Their zeros make up the ring pattern.',
    markers:[
      { side:'front', x:105, y:140, ring:20, label:'Yellow 100s', outline:{shape:'rect', x:24, y:86, w:168, h:114, rx:3} },
      { side:'back',  x:170, y:75,  ring:16, label:'Yellow 100s', outline:{shape:'rect', x:116, y:50, w:112, h:50, rx:3} },
      { side:'back',  x:520, y:76,  ring:16, label:'Yellow 100s', outline:{shape:'rect', x:474, y:50, w:94, h:52, rx:3} },
    ],
    icon:'<circle cx="4" cy="8" r="1.5"/><circle cx="8" cy="4" r="1.5"/><circle cx="12" cy="8" r="1.5"/><circle cx="10" cy="12" r="1.5"/><circle cx="5" cy="12" r="1.5"/>'
  },
  {
    id:'declaration', name:'Declaration text', short:'Text from the Declaration, right of the portrait',
    color:'#9a6a2a', color2:'#d4a866',
    desc:'Lines from the Declaration of Independence run across the right side of the front, in fine script, with the date July 4, 1776 and the words “States of America”. The golden quill lies across them. It is a design element of the note rather than one of the security features uscurrency.gov lists, but its fine script is hard to reproduce cleanly.',
    how:'Look to the right of the portrait. The script should be sharp and readable, for example “…political bands which have connected them with another…”.',
    markers:[ { side:'front', x:530, y:170, ring:26, label:'Declaration text', outline:{shape:'rect', x:366, y:108, w:336, h:192, rx:4} } ],
    icon:'<path d="M3 4h10M3 7h10M3 10h7M3 13h9"/>'
  },
];

// Exploded view: the note pulled apart in both directions. The paper (with the ribbon, thread and
// watermark inside it) is the core; the reverse is printed on one side and the obverse on the other.
const LAYERS = [
  { id:'r-gold',     name:'Large gold 100',   group:'Reverse', side:'back',  feature:'gold100',   kind:'pieces',
    pieces:[ ['back-gold-100', 566,34,122,246] ] },
  { id:'r-intaglio', name:'Intaglio ink',     group:'Reverse', side:'back',  feature:'intaglio',  kind:'pieces',
    pieces:[ ['back-hall', 91,44,486,220], ['back-motto', 255,53,232,36] ] },
  { id:'r-offset',   name:'Offset print',     group:'Reverse', side:'back',  feature:'fineline',  kind:'art' },
  { id:'thread',     name:'Security thread',  group:'Paper',   side:'front', feature:'thread',    kind:'pieces',
    pieces:[ ['front-thread', 152,0,15,320] ] },
  { id:'ribbon',     name:'3-D ribbon',       group:'Paper',   side:'front', feature:'ribbon',    kind:'pieces',
    pieces:[ ['front-ribbon-cut', 367,0,39,320] ] },
  { id:'substrate',  name:'Cotton-linen paper', group:'Paper', side:'front', feature:null,        kind:'paper', core:true },
  { id:'watermark',  name:'Watermark',        group:'Paper',   side:'front', feature:'watermark', kind:'pieces',
    pieces:[ ['watermark-ghost', 613,66,80,110] ] },
  { id:'offset',     name:'Offset print',     group:'Obverse', side:'front', feature:'fineline',  kind:'art' },
  { id:'intaglio',   name:'Intaglio ink',     group:'Obverse', side:'front', feature:'intaglio',  kind:'pieces',
    pieces:[ ['front-portrait', 104,10,276,286], ['front-frb-seal', 80,112,78,81.4] ] },
  { id:'ovi',        name:'Colour-shift ink', group:'Obverse', side:'front', feature:'ovi',       kind:'pieces',
    pieces:[ ['front-bell', 409,194,82,94], ['front-ovi-100', 541,239,138,54] ] },
  { id:'serial',     name:'Seals and serials', group:'Obverse', side:'front', feature:'serial',   kind:'pieces',
    pieces:[ ['front-treasury-seal', 503,94,96,96], ['front-serial-left', 25,57,173,31], ['front-serial-right', 495,202,203,33] ] },
  { id:'uv',         name:'UV: thread glows', group:'Obverse', side:'front', feature:'thread',    kind:'uv' },
];

const TWEAK_DEFAULS = {
  "defaultActive": ["ribbon","bell","ovi","watermark","thread","intaglio","fineline","microprint","gold100","serial","frb","treasury","signature","eurion","declaration"]
};

// Glow highlights: each feature's own cut-out (assets/layers/<src>.png) laid exactly over the artwork
// at its box [x, y, w, h] in 720x320 note space (boxes from assets/boxes.js when present).
const P = (side, src, x, y, w, h, mirror) => ({ side, src, box: (!mirror && !src.endsWith('.svg') && typeof BOXES !== 'undefined' && BOXES[src]) || [x, y, w, h], mirror:!!mirror });
const REGISTER_GHOST = { box: [0, 0, 0, 0] };
const GLOW = {
  ribbon:    [ P('front','front-ribbon',367,0,39,320) ],
  bell:      [ P('front','front-bell',409,194,82,94) ],
  ovi:       [ P('front','front-ovi-100',541,239,138,54) ],
  watermark: [ P('front','watermark-ghost',613,66,80,110), P('back','watermark-ghost',27,66,80,110,true) ],   // in the blank oval; the back mirrors it
  thread:    [ P('front','front-thread',152,0,15,320) ],
  intaglio:  [ P('front','front-portrait',104,10,276,286) ],
  fineline:  [ P('front','front-portrait',104,10,276,286), P('back','back-hall',91,44,486,220) ],
  microprint:[ P('front','front-quill',360,34,256,266) ],
  gold100:   [ P('back','back-gold-100',566,34,122,246) ],
  serial:    [ P('front','front-serial-left',25,57,173,31), P('front','front-serial-right',495,202,203,33) ],
  frb:       [ P('front','front-frb-seal',80,112,78,81.4), P('front','front-fed-indicator',24,87,42,32) ],
  treasury:  [ P('front','front-treasury-seal',503,94,96,96) ],
  signature: [ P('front','front-signatures',23,188,128,82) ],
  eurion:    [ P('front','front-eurion',20,82,176,122), P('back','back-eurion-tl',112,46,120,58), P('back','back-eurion-tr',470,46,102,60) ],
  declaration:[ P('front','front-declaration',362,104,344,200), P('front','front-quill',366,28,250,270) ],
};

// Detail callouts shown when a feature is zoomed into: [side, [[x, y], ...], label] in note units.
const DETAILS = {
  ribbon:    [['front', [[386, 60]], 'Woven into the paper'], ['front', [[386, 160]], 'Bells change to 100s'],
              ['front', [[386, 260]], 'Moves at right angles to the tilt']],
  bell:      [['front', [[450, 215]], 'Copper inkwell'], ['front', [[450, 245]], 'Bell: copper to green']],
  ovi:       [['front', [[570, 266]], 'Copper face-on'], ['front', [[650, 266]], 'Green when tilted']],
  watermark: [['front', [[653, 95]], 'Franklin, in the paper'], ['front', [[653, 170]], 'Seen only against the light'],
              ['back', [[95, 160]], 'Visible from the back too']],
  thread:    [['front', [[159, 60]], 'USA and 100, alternating'], ['front', [[159, 200]], 'Glows pink under UV']],
  intaglio:  [['front', [[170, 265]], 'Shoulder: rough to the touch'], ['front', [[300, 270]], 'Raised ink']],
  fineline:  [['front', [[270, 140]], 'Shading from line spacing'], ['front', [[205, 120]], 'Hair: engraved lines'],
              ['back', [[330, 150]], 'Independence Hall, engraved']],
  microprint:[['front', [[300, 255]], 'Collar: THE UNITED STATES OF AMERICA'], ['front', [[585, 80]], 'Around the watermark: USA 100'],
              ['front', [[470, 190]], 'Along the quill: ONE HUNDRED USA'], ['front', [[22, 160]], 'Borders: small 100s']],
  gold100:   [['back', [[628, 150]], 'Large gold numeral, for low vision']],
  serial:    [['front', [[45, 72]], 'Starts with two letters'], ['front', [[596, 218]], 'Same serial, right side']],
  frb:       [['front', [[119, 153]], 'Federal Reserve System'], ['front', [[45, 103]], 'C3: Philadelphia']],
  treasury:  [['front', [[551, 142]], 'Department of the Treasury']],
  signature: [['front', [[80, 205]], 'Secretary of the Treasury'], ['front', [[80, 240]], 'Treasurer of the United States']],
  eurion:    [['front', [[60, 110]], 'Small yellow 100s'], ['front', [[150, 190]], 'Their zeros form the ring pattern'],
              ['back', [[170, 75]], 'Top left cluster'], ['back', [[520, 76]], 'Top right cluster']],
  declaration:[['front', [[400, 118]], 'July 4, 1776'], ['front', [[420, 170]], 'States of America'],
              ['front', [[600, 196]], 'Lines of the Declaration']],
};
