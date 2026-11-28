// Plain script (not a module) so the page also works when opened straight from disk (file://)
// Swiss 1000-franc note, ninth series (issued 13 March 2019).
// Feature wording follows the Swiss National Bank: the brochure "The new 1000-franc note" (2019,
// snb.ch/1000, copy in source/found/nb_1000.en.pdf) and snb.ch, cash, series 9.
// Note space: 320 x 722 units over the whole note (70 x 158 mm, portrait), the back in its own
// coordinates as you look at it. Numbering follows the SNB brochure (1 Globe test ... 13 UV globe).
const FEATURES = [
  {
    id:'globe', name:'Globe test', short:'A golden arc moves across the globe',
    color:'#b8862a', color2:'#e8c46a', light:false,
    desc:'In the centre of the front is a shimmering globe. Tilt the note from left to right and a golden arc moves across the globe; hold it in front of you and tilt it backwards, and the colour of the globe changes. The symbols around the globe are taken from the phonetic alphabet, which enables the correct pronunciation of words in different languages.',
    how:'Tilt the note <b>from left to right</b>: a golden arc should move across the globe. Tilt it <b>backwards</b>: the globe should change colour.',
    markers:[ { side:'front', x:221, y:400, ring:30, label:'Globe', outline:{shape:'ellipse', cx:221.5, cy:400.5, rx:68.5, ry:68.5} } ],
    icon:'<circle cx="8" cy="8" r="6"/><path d="M2 8h12M8 2c2 2 2 10 0 12M8 2c-2 2-2 10 0 12"/>'
  },
  {
    id:'strip', name:'Security strip test', short:'Moving numbers, a rainbow map of the language regions',
    color:'#6d8fd0', color2:'#a8c4f2', light:false,
    desc:'A security strip runs across the lower half of the front. Held in front of you it shows, in silver, a map of Switzerland with the language regions of the Swiss Confederation and its neighbouring countries, a list of all Swiss cantons, and the number 1000. Tilt the note from left to right: red and green numbers appear on four lines and move in opposite directions. Tilt it slowly backwards: the outline of Switzerland and the language regions appear in rainbow colours, and little shining Swiss crosses are visible inside the number 1000.',
    how:'Tilt <b>left to right</b>: red and green numbers should move in opposite directions on four lines. Tilt <b>backwards</b>: the map should turn to rainbow colours.',
    markers:[ { side:'front', x:220, y:484, ring:24, label:'Security strip', outline:{shape:'rect', x:0, y:449, w:320, h:70, rx:1} } ],
    icon:'<path d="M1 6h14v4H1z"/><path d="M4 8h3M9 8h3"/>'
  },
  {
    id:'cross', name:'Cross test', short:'A transparent Swiss cross becomes the Swiss flag',
    color:'#c0392b', color2:'#ef8a7e', light:true,
    desc:'At the top left of the front (position A) is a transparent Swiss cross: a window through the note, which can also be seen from the back. Hold the Swiss cross up to the light and it turns into the Swiss flag.',
    how:'Hold the note <b>up to the light</b>: the Swiss cross should turn into the <b>Swiss flag</b>.',
    markers:[
      { side:'front', x:71, y:63, ring:18, label:'Swiss cross', outline:{shape:'rect', x:45, y:36, w:53, h:55, rx:2} },
      { side:'back',  x:249, y:63, ring:18, label:'Swiss cross (back)', outline:{shape:'rect', x:222, y:36, w:53, h:55, rx:2} },
    ],
    icon:'<path d="M6 2h4v4h4v4h-4v4H6v-4H2V6h4z"/>'
  },
  {
    id:'triangle', name:'Triangle test', short:'A glittering thread that becomes a continuous line',
    color:'#8a7a5a', color2:'#cbb98e', light:true,
    desc:'On the back of the note, below the number 1000, is a triangle containing a glittering security thread. Hold the note up to the light: the security thread appears as a continuous line, with the Swiss flag and the number 1000 at regular intervals along it.',
    how:'Hold the note <b>up to the light</b>: the thread should run as one <b>continuous line</b>, with the Swiss flag and <b>1000</b> repeating along it.',
    markers:[ { side:'back', x:64, y:276, ring:18, label:'Triangle', outline:{shape:'rect', x:38, y:247, w:52, h:46, rx:2} } ],
    icon:'<path d="M8 2l6 12H2z"/><path d="M3 10h10"/>'
  },
  {
    id:'hand', name:'Hand test', short:'Raised print you can feel and rub off',
    color:'#6a4fb0', color2:'#a991e0', light:false,
    desc:'The hand, the number 1000 and the bank’s name are printed in intaglio, so the ink stands up from the note. On the 1000-franc note the hand is a handshake, which signifies interpersonal communication. Run your fingers over them and you can feel the raised print; rubbed onto a piece of light-coloured paper, they leave behind traces of colour.',
    how:'Run your fingers over <b>the hand</b>, <b>the number 1000</b> or <b>the bank’s name</b>: you should feel the raised print. Rubbed on light paper, they leave traces of colour.',
    markers:[
      { side:'front', x:170, y:210, ring:40, label:'Handshake', outline:{shape:'rect', x:0, y:84, w:320, h:238, rx:3} },
      { side:'front', x:115, y:616, ring:24, label:'1000', outline:{shape:'rect', x:16, y:572, w:202, h:89, rx:3} },
      { side:'back',  x:97,  y:53,  ring:24, label:'1000 (back)', outline:{shape:'rect', x:6, y:16, w:186, h:76, rx:3} },
    ],
    icon:'<path d="M3 9l3-3 2 1 3-3 2 2-4 4-2-1-2 2z"/>'
  },
  {
    id:'microperf', name:'Microperf®', short:'A Swiss cross of tiny holes',
    color:'#7d6a3c', color2:'#c8b27a', light:true,
    desc:'On the front of the note (position D) is a perforated Swiss cross, made up of a grid of equidistant holes. Hold the note up to the light and the finely perforated cross appears especially clearly.',
    how:'Hold the note <b>up to the light</b> near the letter D: a <b>Swiss cross of fine holes</b> should shine through.',
    markers:[ { side:'front', x:74, y:484, ring:16, label:'Microperf', outline:{shape:'rect', x:52, y:462, w:44, h:44, rx:2} } ],
    icon:'<circle cx="8" cy="4" r=".8"/><circle cx="8" cy="8" r=".8"/><circle cx="8" cy="12" r=".8"/><circle cx="4" cy="8" r=".8"/><circle cx="12" cy="8" r=".8"/>'
  },
  {
    id:'tactile', name:'Tactile elements', short:'Six blocks of raised lines on each long edge',
    color:'#4b3a7a', color2:'#8c7ac0', light:false,
    desc:'Along the long edges of the front are blocks of short, raised lines for the visually impaired. The number of blocks varies for each denomination: the 1000-franc note has six blocks on each side.',
    how:'Run your fingers along the <b>long edges</b> of the note: you should feel <b>six blocks</b> of raised lines on each side.',
    markers:[ { side:'front', x:314, y:300, ring:14, label:'Tactile lines', outline:{shape:'rect', x:0, y:34, w:320, h:660, rx:1} } ],
    icon:'<path d="M2 4h4M2 7h4M2 10h4M10 4h4M10 7h4M10 10h4"/>'
  },
  {
    id:'watermark', name:'Watermark', short:'The Swiss flag and the globe, against the light',
    color:'#8a7a90', color2:'#c4b6cc', light:true,
    desc:'Two watermarks, the Swiss flag and the globe, are incorporated into the note (position E). Hold the note up to the light: on the left you can see the outline of the Swiss flag and, on the right, the globe.',
    how:'Hold the note <b>up to the light</b>: the <b>outline of the Swiss flag</b> on the left and the <b>globe</b> on the right should appear in the paper.',
    markers:[
      { side:'front', x:160, y:592, ring:30, label:'Watermark', outline:{shape:'rect', x:62, y:526, w:216, h:132, rx:3} },
      { side:'back',  x:160, y:592, ring:30, label:'Watermark (back)', outline:{shape:'rect', x:42, y:526, w:216, h:132, rx:3} },
    ],
    icon:'<rect x="2" y="4" width="6" height="6"/><circle cx="12" cy="9" r="3"/>'
  },
  {
    id:'tilt', name:'Tilt effect', short:'A Swiss cross seen only at an angle',
    color:'#c79a1a', color2:'#ecd06a', light:false,
    desc:'On the front of the note (position C) the Swiss cross is printed in such a way that it can only be seen from a particular angle. Hold the note in front of you and tilt it backwards: the Swiss cross stands out from the background.',
    how:'Hold the note in front of you and <b>tilt it backwards</b>: a <b>Swiss cross</b> should stand out in the yellow area at C.',
    markers:[ { side:'front', x:80, y:344, ring:18, label:'Tilt cross', outline:{shape:'rect', x:32, y:323, w:93, h:43, rx:2} } ],
    icon:'<path d="M6 3h4v3h3v4h-3v3H6v-3H3V6h3z"/><path d="M1 15l14-3"/>'
  },
  {
    id:'register', name:'See-through register', short:'Two halves make a whole Swiss cross',
    color:'#d4782a', color2:'#f0b070', light:true,
    desc:'On both sides of the note an incomplete Swiss cross is printed in the lower section. Hold the note up to the light and the two halves combine: a complete Swiss cross appears in outline.',
    how:'Hold the note <b>up to the light</b>: the corner marks on the front and back should join into <b>one complete cross outline</b>.',
    markers:[
      { side:'front', x:194, y:554, ring:16, label:'Register (front)', outline:{shape:'rect', x:176, y:537, w:36, h:35, rx:2} },
      { side:'back',  x:131, y:549, ring:16, label:'Register (back)', outline:{shape:'rect', x:112, y:531, w:38, h:36, rx:2} },
    ],
    icon:'<path d="M5 2v3H2M11 2v3h3M5 14v-3H2M11 14v-3h3"/>'
  },
  {
    id:'serial', name:'Serial number', short:'Printed twice on the back, in two fonts',
    color:'#2c3e70', color2:'#7d8fc4', light:false,
    desc:'An identical number, consisting of one letter and nine numbers, is printed on the back of the note in two places, in different fonts. On this specimen both read 17C6215816.',
    how:'Examine the back: the serial number appears <b>in two places, in different fonts</b>, and both must be <b>identical</b>.',
    markers:[
      { side:'back', x:285, y:280, ring:14, label:'Serial (right)', outline:{shape:'rect', x:274, y:204, w:22, h:150, rx:2} },
      { side:'back', x:79,  y:524, ring:14, label:'Serial (left)',  outline:{shape:'rect', x:68, y:460, w:22, h:128, rx:2} },
    ],
    icon:'<path d="M2 4h2v8H2zM6 4h2v8H6zM10 4h2v8h-2z"/>'
  },
  {
    id:'microtext', name:'Microtext', short:'Four national languages, under a magnifier',
    color:'#5b4a8a', color2:'#9c8acb', light:false,
    desc:'On the front of the note (position B), inside the Swiss flag, is a piece of text written in the four national languages. With a magnifying glass you can make out the microlettering: some of the text is in dark letters on a light background and some in light-coloured letters on a dark background.',
    how:'Use a <b>magnifying glass</b> near the letter B: the lines of tiny text should be sharp and readable, in <b>German, French, Italian and Romansh</b>.',
    markers:[ { side:'front', x:64, y:196, ring:16, label:'Microtext', outline:{shape:'rect', x:26, y:158, w:78, h:76, rx:2} } ],
    icon:'<path d="M2 4h12M2 7h12M2 10h12M2 13h8"/>'
  },
  {
    id:'uv', name:'Ultraviolet globe', short:'A globe and fibres that glow under UV',
    color:'#7a5cff', color2:'#b9a6ff', light:false,
    desc:'At the top right of the front is a globe which only becomes visible under ultraviolet light: it shows up brightly while the background remains dull. The paper on both sides also contains flecks (fibres) that light up in different colours under ultraviolet light.',
    how:'Examine the note under a <b>UV lamp</b>: the <b>globe</b> at the top right should glow brightly, and <b>coloured fibres</b> should light up all over both sides.',
    markers:[ { side:'front', x:221, y:93, ring:26, label:'UV globe', outline:{shape:'ellipse', cx:221, cy:93, rx:67, ry:67} } ],
    icon:'<circle cx="8" cy="8" r="5"/><path d="M8 1v2M8 13v2M1 8h2M13 8h2"/>'
  },
];

// Exploded view: the note pulled apart. The three-layer Durasafe® substrate (paper, polymer,
// paper) is the core; the reverse is printed on one paper layer and the obverse on the other.
const LAYERS = [
  { id:'r-intaglio', name:'Intaglio ink',      group:'Reverse', side:'back',  feature:'hand',      kind:'pieces',
    pieces:[ ['back-numeral', 6,16,186,76], ['back-bankname', 10,420,48,284] ] },
  { id:'r-serial',   name:'Serial numbers',    group:'Reverse', side:'back',  feature:'serial',    kind:'pieces',
    pieces:[ ['back-serial-a', 277,207,18,139], ['back-serial-b', 70,466,17,121], ['back-register', 112,531,38,36] ] },
  { id:'r-offset',   name:'Offset print',      group:'Reverse', side:'back',  feature:null,        kind:'art' },
  { id:'paper-back', name:'Paper (back)',      group:'Substrate', side:'back', feature:null,       kind:'paper' },
  { id:'thread',     name:'Security thread',   group:'Substrate', side:'back', feature:'triangle', kind:'pieces',
    pieces:[ ['thread', 0,271,320,12] ] },
  { id:'polymer',    name:'Polymer core',      group:'Substrate', side:'front', feature:'cross',   kind:'polymer', core:true },
  { id:'watermark',  name:'Watermarks',        group:'Substrate', side:'front', feature:'watermark', kind:'pieces',
    pieces:[ ['watermark-ghost', 62,526,216,132] ] },
  { id:'paper-front',name:'Paper (front)',     group:'Substrate', side:'front', feature:null,      kind:'paper' },
  { id:'offset',     name:'Offset print',      group:'Obverse', side:'front', feature:null,        kind:'art' },
  { id:'strip',      name:'Security strip',    group:'Obverse', side:'front', feature:'strip',     kind:'pieces',
    pieces:[ ['front-strip', 0,449,320,70] ] },
  { id:'globe',      name:'Shimmering globe',  group:'Obverse', side:'front', feature:'globe',     kind:'pieces',
    pieces:[ ['front-globe', 150,329,143,143] ] },
  { id:'intaglio',   name:'Intaglio ink',      group:'Obverse', side:'front', feature:'hand',      kind:'pieces',
    pieces:[ ['front-hand', 0,84,320,238], ['front-numeral', 16,572,202,89], ['front-bankname', 16,657,252,45], ['front-tactile', 0,34,320,660] ] },
  { id:'uv',         name:'UV ink: globe',     group:'Obverse', side:'front', feature:'uv',        kind:'uv' },
];

const TWEAK_DEFAULS = {
  "defaultActive": ["globe","strip","cross","triangle","hand","microperf","tactile","watermark","tilt","register","serial","microtext","uv"]
};

// Glow highlights: each feature's own cut-out (assets/layers/<src>.png) laid exactly over the artwork
// at its box [x, y, w, h] in 320 x 722 note space (boxes from assets/boxes.js when present).
const P = (side, src, x, y, w, h, mirror) => ({ side, src, box: (!mirror && typeof BOXES !== 'undefined' && BOXES[src]) || [x, y, w, h], mirror:!!mirror });
const GLOW = {
  globe:     [ P('front','front-globe',150,329,143,143) ],
  strip:     [ P('front','front-strip',0,449,320,70) ],
  cross:     [ P('front','front-cross',42,33,59,61), P('back','back-cross',219,33,59,61) ],
  triangle:  [ P('back','back-triangle',36,244,56,52) ],
  hand:      [ P('front','front-hand',0,84,320,238), P('front','front-numeral',16,572,202,89), P('front','front-bankname',16,657,252,45),
               P('back','back-numeral',6,16,186,76), P('back','back-bankname',10,420,48,284) ],
  microperf: [ P('front','front-microperf',52,462,44,44) ],
  tactile:   [ P('front','front-tactile',0,34,320,660) ],
  watermark: [ P('front','watermark-ghost',62,526,216,132), P('back','watermark-ghost',42,526,216,132,true) ],   // in the paper: the back mirrors it
  tilt:      [ P('front','front-tilt',32,323,93,43) ],
  register:  [ P('front','front-register',176,537,36,35), P('back','back-register',112,531,38,36) ],
  serial:    [ P('back','back-serial-a',277,207,18,139), P('back','back-serial-b',70,466,17,121) ],
  microtext: [ P('front','front-microtext',26,158,78,76) ],
  uv:        [ P('front','front-uvglobe',154,26,134,134) ],
};

// Detail callouts shown when a feature is zoomed into: [side, [[x, y], ...], label] in note units.
const DETAILS = {
  globe:     [['front', [[205, 365]], 'Golden arc: tilt left to right'], ['front', [[250, 430]], 'Colour changes: tilt backwards'],
              ['front', [[285, 345]], 'Phonetic symbols']],
  strip:     [['front', [[70, 486]], 'Map of the language regions'], ['front', [[165, 486]], 'All Swiss cantons'],
              ['front', [[222, 492]], 'Red and green numbers, four lines'], ['front', [[276, 497]], 'Shining crosses in the 1000']],
  cross:     [['front', [[71, 45]], 'A window through the note'], ['front', [[71, 82]], 'Against the light: the Swiss flag'],
              ['back', [[249, 63]], 'Seen from the back too']],
  triangle:  [['back', [[64, 255]], 'The triangle'], ['back', [[64, 277]], 'Glittering thread'],
              ['back', [[160, 277]], 'Against the light: one continuous line']],
  hand:      [['front', [[120, 160]], 'Handshake: raised intaglio'], ['front', [[240, 230]], 'Feel it with your fingers'],
              ['front', [[60, 616]], 'The number 1000'], ['front', [[140, 680]], 'The bank’s name']],
  microperf: [['front', [[74, 484]], 'A grid of equidistant holes'], ['front', [[30, 482]], 'Position D']],
  tactile:   [['front', [[6, 60]], 'Left edge: six blocks'], ['front', [[314, 180]], 'Right edge: six blocks'],
              ['front', [[314, 548]], 'Short raised lines']],
  watermark: [['front', [[97, 622]], 'Outline of the Swiss flag'], ['front', [[218, 586]], 'The globe'],
              ['back', [[218, 586]], 'Seen from the back, mirrored']],
  tilt:      [['front', [[80, 344]], 'Tilt backwards: a Swiss cross'], ['front', [[26, 343]], 'Position C']],
  register:  [['front', [[194, 554]], 'Front: half the cross'], ['back', [[131, 549]], 'Back: the other half']],
  serial:    [['back', [[285, 250]], 'One letter, nine numbers'], ['back', [[79, 500]], 'Same number, different font']],
  microtext: [['front', [[45, 175]], 'Dark letters on light'], ['front', [[70, 222]], 'Light letters on dark'],
              ['front', [[25, 205]], 'Position B']],
  uv:        [['front', [[221, 60]], 'Glows only under UV'], ['front', [[250, 130]], 'The background stays dull']],
};
