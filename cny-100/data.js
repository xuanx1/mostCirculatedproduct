// Plain script (not a module) so the page also works when opened straight from disk (file://)
// ¥100 renminbi, fifth series, 2015 edition (issued 12 November 2015).
// Feature wording follows the People's Bank of China (PBC):
//   pbc.gov.cn/rmyh/xbrmb/index_english.html (the PBC's own 2015 ¥100 feature page, English)
//   pbc.gov.cn/huobijinyinju/147948/147954/148021/3871273/3871275/index.html (2015年版第五套人民币100元纸币)
//   PBC Q&A on the issue of the 2015 ¥100 (…/147956/8a1e3c51c8b44cfebb59feae8177a21f/index.html)
// Microprinting is listed by PBC for the 1999 and 2005 editions (…/176741/2025080619260380847/,
// …/176764/2820779/) and can be seen on PBC's 2015 specimen image.
const FEATURES = [
  {
    id:'ovmi', name:'Colour-shifting numeral', short:'光彩光变数字 · gold to green, a bright bar rolls',
    color:'#a8841c', color2:'#e3c25a',
    desc:'The numeral 100 in the middle of the front is printed in colour-shifting ink (PBC: “numeral in OVMI”). Viewed straight on it is golden; viewed at a low angle it turns green. As the viewing angle changes the colour alternates between gold and green, and a bright bar can be seen rolling up and down across the numeral.',
    how:'Tilt the note top-to-bottom. The <b>100 should turn from gold to green</b> and a <b>bright bar should roll up and down</b> it. A flat copy keeps one colour and has no moving bar.',
    markers:[ { side:'front', x:278, y:122, ring:24, label:'Colour-shifting 100' } ],
    icon:'<circle cx="8" cy="8" r="5"/><path d="M3 8h10"/>'
  },
  {
    id:'thread', name:'Windowed thread', short:'光变镂空开窗安全线 · colour-shifting: magenta to green',
    color:'#a0288a', color2:'#e07ac8',
    desc:'An optically variable, demetallised security thread, 4 mm wide, runs down the right side of the front and surfaces in five windows. Viewed straight on it is magenta; at an angle it turns green. Held against the light, the characters “¥100” can be read in it, alternately the right way round and mirrored. (A second, fully embedded magnetic thread for machine reading lies on the other side of the note; PBC does not publish its position, so it is not drawn here.)',
    how:'Tilt the note: the <b>windows should change from magenta to green</b>. Hold it to the light: the thread shows <b>“¥100”</b>, alternately mirrored.',
    markers:[ { side:'front', x:602, y:80, ring:16, label:'Windowed thread' } ],
    icon:'<path d="M8 1v14M6 3h4v3H6zM6 10h4v3H6z"/>'
  },
  {
    id:'watermark', name:'Portrait watermark', short:'人像水印 · Mao Zedong, in the paper',
    color:'#7a6a5e', color2:'#c2b0a2',
    desc:'A watermark portrait of Mao Zedong is formed in the paper itself, in the blank area on the left of the front. Hold the note against the light to see it. The 2015 edition’s watermark is clearer and has more tonal levels than before.',
    how:'Hold the note up to a light. A <b>portrait of Mao Zedong</b> should appear in the blank area on the left, soft and continuous-tone, with no printed dots or lines.',
    markers:[ { side:'front', x:90, y:150, ring:30, label:'Watermark' } ],
    icon:'<circle cx="8" cy="7" r="4"/><path d="M3 15c1-3 3-4 5-4s4 1 5 4"/>'
  },
  {
    id:'register', name:'See-through numeral', short:'胶印对印图案 · two halves make one 100',
    color:'#e0582c', color2:'#f5a07c',
    desc:'Part of the numeral 100 is printed in the lower left corner of the front and part in the lower right corner of the back. Held against the light, the two partial patterns combine to form the complete numeral 100. In the 2015 edition this see-through register changed from an antique coin to the numeral, and moved to the lower corner.',
    how:'Hold the note to the light: the pieces on both sides must <b>join exactly into one complete 100</b>. Use the button below to see it here.',
    markers:[ { side:'front', x:55, y:281, ring:16, label:'See-through numeral' } ],
    icon:'<path d="M3 4v8M7 4a2 3 0 1 1 0 .01M12 4a2 3 0 1 1 0 .01"/>'
  },
  {
    id:'serial', name:'Serial numbers', short:'横竖双号码 · horizontal and vertical',
    color:'#2c55b0', color2:'#7a9be0',
    desc:'Each note carries its serial number twice. The horizontal number, at the lower left of the front, begins with two letters followed by eight digits: the two letters and the first two digits are printed in dark red and the next six digits in black. The vertical number, on the right side, is printed in blue. Two numbers guard against notes pieced together from parts of different notes, and help machines read the serial.',
    how:'Both numbers must be <b>identical</b>. Check the colours: horizontal <b>dark red then black</b>, vertical <b>blue</b>. (This PBC specimen reads AA00000000.)',
    markers:[
      { side:'front', x:85, y:241, ring:14, label:'Horizontal serial' },
      { side:'front', x:673, y:180, ring:14, label:'Vertical serial' },
    ],
    icon:'<path d="M2 5h12M2 11h12M5 3v10M11 3v10"/>'
  },
  {
    id:'whitewm', name:'White watermark', short:'白水印 · a bright 100 under the serial',
    color:'#8a8a8a', color2:'#d8d8d8',
    desc:'Below the horizontal serial number, a highlight watermark shows the numeral 100. Against the light it is strongly translucent, so it reads brighter than the paper around it.',
    how:'Hold the note up to a light and look <b>just below the horizontal serial number</b>: a bright, sharp-edged <b>100</b> should appear.',
    markers:[ { side:'front', x:127, y:273, ring:14, label:'White watermark' } ],
    icon:'<path d="M4 4v8M8 4a2 4 0 1 1 0 .01M12 4a2 4 0 1 1 0 .01"/>'
  },
  {
    id:'intaglio', name:'Intaglio printing', short:'雕刻凹印 · raised ink you can feel',
    color:'#b8142a', color2:'#e9707e',
    desc:'The issuer’s name 中国人民银行 (People’s Bank of China), the National Emblem, the decorative rosette, the numeral 100 in the upper right corner, the Braille mark and the portrait on the front, and the Great Hall of the People on the back are printed by intaglio. The ink stands up from the paper and can be felt with the fingertips.',
    how:'Run a fingertip over <b>中国人民银行</b>, the <b>National Emblem</b> or the <b>upper-right 100</b>: it should feel <b>raised and rough</b>, not smooth.',
    markers:[ { side:'front', x:275, y:36, ring:18, label:'Intaglio' } ],
    icon:'<path d="M2 12h12M4 9h8M6 6h4"/>'
  },
  {
    id:'fineline', name:'Portrait of Mao Zedong', short:'毛泽东头像 · engraved, in intaglio',
    color:'#a01c2c', color2:'#e0808a',
    desc:'The portrait of Mao Zedong is engraved and printed by intaglio: every tone of the face, hair and jacket is built from engraved lines and cross-hatching, and the ink can be felt. Printed copies turn this line-work into dots or a blur.',
    how:'Use a <b>magnifier</b> on the face: the lines should be <b>crisp and separate</b>. Feel the jacket: it should be raised.',
    markers:[ { side:'front', x:470, y:120, ring:40, label:'Portrait' } ],
    icon:'<circle cx="8" cy="6" r="3.5"/><path d="M2.5 15c1-3.5 3-5 5.5-5s4.5 1.5 5.5 5"/>'
  },
  {
    id:'braille', name:'Braille mark', short:'盲文面额标记 · the denomination, in raised intaglio',
    color:'#b8142a', color2:'#e9707e',
    desc:'The Braille denomination mark at the lower right of the front is printed by intaglio, so it can be felt with the fingertips and helps people with visual impairments tell the denomination.',
    how:'Feel the <b>lower right corner</b> of the front: the <b>dot and the two corner marks</b> should stand up from the paper.',
    markers:[ { side:'front', x:645, y:287, ring:16, label:'Braille' } ],
    icon:'<circle cx="5" cy="6" r="1.6"/><path d="M8 12h4V7"/>'
  },
  {
    id:'microprint', name:'Microprinting', short:'胶印缩微文字 · RMB and RMB100',
    color:'#c43a4a', color2:'#ec8c98',
    desc:'In the oval pattern at the top of the front, the fine lines are microprinted lettering: “RMB” and “RMB100”, repeated, too small to read without magnification. Here they fill the outline of a large 100 beside the National Emblem.',
    how:'Use a <b>magnifier</b> on the pattern to the left of 中国: the lines should resolve into sharp letters <b>RMB100</b>.',
    markers:[ { side:'front', x:118, y:48, ring:20, label:'Microprinting' } ],
    icon:'<path d="M2 4h12M2 8h12M2 12h8"/>'
  },
];

// Exploded view: the note pulled apart in both directions. The paper (with the thread and the
// watermarks inside it) is the core; the reverse is printed on one side and the obverse on the other.
const LAYERS = [
  { id:'r-intaglio', name:'Intaglio ink',      group:'Reverse', side:'back',  feature:'intaglio',  kind:'pieces',
    pieces:[ ['back-hall', 130,131.5,386,85.5] ] },
  { id:'r-offset',   name:'Offset print',      group:'Reverse', side:'back',  feature:'register',  kind:'art' },
  { id:'thread',     name:'Windowed thread',   group:'Paper',   side:'front', feature:'thread',    kind:'pieces',
    pieces:[ ['thread-full', 592.5,0,20,320] ] },
  { id:'substrate',  name:'Banknote paper',    group:'Paper',   side:'front', feature:null,        kind:'paper', core:true },
  { id:'watermark',  name:'Portrait watermark', group:'Paper',  side:'front', feature:'watermark', kind:'pieces',
    pieces:[ ['watermark-ghost', 24.28,75.28,134.64,145.2] ] },
  { id:'whitewm',    name:'White watermark',   group:'Paper',   side:'front', feature:'whitewm',   kind:'pieces',
    pieces:[ ['white-watermark', 93.39,253.52,66.79,41.07] ] },
  { id:'offset',     name:'Offset print',      group:'Obverse', side:'front', feature:'register',  kind:'art' },
  { id:'intaglio',   name:'Intaglio ink',      group:'Obverse', side:'front', feature:'intaglio',  kind:'pieces',
    pieces:[ ['front-portrait', 348,6,311,298], ['front-emblem', 22,15,76,74], ['front-bank-name', 148,16,257,42],
             ['front-numeral', 656,14,46,89], ['front-braille', 594,270,103,34] ] },
  { id:'ovmi',       name:'Colour-shift ink',  group:'Obverse', side:'front', feature:'ovmi',      kind:'pieces',
    pieces:[ ['front-ovmi', 199,91,160,65] ] },
  { id:'serial',     name:'Serial numbers',    group:'Obverse', side:'front', feature:'serial',    kind:'pieces',
    pieces:[ ['front-serial-h', 16,227,144,30], ['front-serial-v', 658,108,30,144] ] },
  { id:'uv',         name:'UV: fibres glow',   group:'Obverse', side:'front', feature:null,        kind:'uv' },
];

const TWEAK_DEFAULS = {
  "defaultActive": ["ovmi","thread","watermark","register","serial","whitewm","intaglio","fineline","braille","microprint"]
};

// Glow highlights: each feature's own cut-out (assets/layers/<src>.png) laid exactly over the artwork
// at its box [x, y, w, h] in 720x320 note space (boxes from assets/boxes.js when present).
const P = (side, src, x, y, w, h, mirror) => ({ side, src, box: (!mirror && typeof BOXES !== 'undefined' && BOXES[src]) || [x, y, w, h], mirror:!!mirror });
// the reverse's see-through pieces, mirrored (as seen through the paper) and fitted onto the obverse
// pieces so the two close into one 100 (tools/make_watermarks.py: register_fit)
const REGISTER_GHOST = { box: [20.75, 263.5, 74, 38] };
const GLOW = {
  ovmi:      [ P('front','front-ovmi',199,91,160,65) ],
  thread:    [ P('front','front-thread',587,10,31,241) ],
  watermark: [ P('front','watermark-ghost',24.28,75.28,134.64,145.2), P('back','watermark-ghost',561.08,75.28,134.64,145.2,true) ],
  register:  [ P('front','front-register',22,262,72,38), P('back','back-register',628,266,74,38) ],
  serial:    [ P('front','front-serial-h',16,227,144,30), P('front','front-serial-v',658,108,30,144) ],
  whitewm:   [ P('front','white-watermark',93.39,253.52,66.79,41.07), P('back','white-watermark',559.82,253.52,66.79,41.07,true) ],
  intaglio:  [ P('front','front-bank-name',148,16,257,42), P('front','front-emblem',22,15,76,74),
               P('front','front-numeral',656,14,46,89), P('back','back-hall',130,131.5,386,85.5) ],
  fineline:  [ P('front','front-portrait',348,6,311,298) ],
  braille:   [ P('front','front-braille',594,270,103,34) ],
  microprint:[ P('front','front-micro',80,18,76,60) ],
};

// Detail callouts shown when a feature is zoomed into: [side, [[x, y], ...], label] in note units.
const DETAILS = {
  ovmi:      [['front', [[222, 122]], 'Gold, seen straight on'], ['front', [[332, 122]], 'Green at a low angle'],
              ['front', [[278, 100]], 'A bright bar rolls up and down']],
  thread:    [['front', [[602, 30]], 'Magenta face-on, green tilted'], ['front', [[602, 130]], '4 mm wide, five windows'],
              ['front', [[602, 230]], 'Against the light: ¥100, alternately mirrored']],
  watermark: [['front', [[90, 110]], 'Mao Zedong, in the paper'], ['front', [[90, 190]], 'Seen against the light'],
              ['back', [[630, 150]], 'Seen from the back too, mirrored']],
  register:  [['front', [[35, 288]], 'Front: part of the 100'], ['front', [[80, 272]], 'Against the light: one whole 100'],
              ['back', [[665, 284]], 'Back: the other part']],
  serial:    [['front', [[42, 241]], 'AA + two digits: dark red'], ['front', [[118, 241]], 'Six digits: black'],
              ['front', [[673, 180]], 'Vertical number: blue']],
  whitewm:   [['front', [[127, 273]], 'Bright 100, against the light']],
  intaglio:  [['front', [[275, 36]], '中国人民银行'], ['front', [[60, 50]], 'National Emblem'],
              ['front', [[676, 58]], 'Upper-right 100'], ['back', [[323, 175]], 'Great Hall of the People']],
  fineline:  [['front', [[470, 120]], 'Engraved lines and cross-hatching'], ['front', [[460, 255]], 'Jacket: raised ink']],
  braille:   [['front', [[604, 282]], 'Raised dot'], ['front', [[668, 288]], 'Raised corner marks']],
  microprint:[['front', [[105, 48]], 'RMB100, repeated'], ['front', [[135, 30]], 'Fills the outline of a large 100']],
};
