// Plain script (not a module) so the page also works when opened straight from disk (file://)
// Australian $100 banknote, next generation series (first issued 29 October 2020).
// Feature wording follows the Reserve Bank of Australia's banknote site: banknotes.rba.gov.au
// (Banknote Features > Explore, the list of security features, and the $100 security features flyer).
// Side names follow the RBA: the Melba side is the "signature side", the Monash side the "serial number side".
const FEATURES = [
  {
    id:'window', name:'Top-to-bottom window', short:'Clear polymer, several features inside',
    color:'#2f7d5a', color2:'#8fd0b0',
    desc:'A clear window runs from the top of the banknote to the bottom, framed by golden wattle. It holds several dynamic security features: the 3D fan, the flying owl, the colourful owl and the reversing 100 within the Shrine of Remembrance. The polymer is clear here, so you see straight through the note.',
    how:'Look for <b>multiple security features</b> in the clear top-to-bottom window, and check that they <b>cannot be easily rubbed off</b>.',
    markers:[ { side:'front', x:255, y:160, ring:30, label:'Top-to-bottom window' } ],
    icon:'<path d="M6 1v14M10 1v14"/>'
  },
  {
    id:'fan3d', name:'3D fan', short:'Raised or recessed, with colourful lines',
    color:'#b07a1c', color2:'#e6c36a',
    desc:'At the top of the window, a fan that looks three-dimensional. As the banknote tilts it appears raised or recessed, with a colourful border of lines.',
    how:'Tilt the banknote to see a <b>three-dimensional fan with colourful lines</b>.',
    markers:[ { side:'front', x:251, y:34, ring:18, label:'3D fan' } ],
    icon:'<path d="M2 12L8 4l6 8M8 4v9M5 8l3 5 3-5"/>'
  },
  {
    id:'flyingowl', name:'Flying owl', short:'Moves its wings and changes colour',
    color:'#3d7fb8', color2:'#9cc6ea',
    desc:'An Australian Masked Owl in flight, in the top-to-bottom window. As the banknote tilts the owl moves its wings and changes colour.',
    how:'Tilt the banknote to see <b>the owl move its wings and change colour</b>.',
    markers:[ { side:'front', x:254, y:72, ring:20, label:'Flying owl' } ],
    icon:'<path d="M1 6c3 0 5 2 7 5 2-3 4-5 7-5M8 11v3"/>'
  },
  {
    id:'colourowl', name:'Colourful owl', short:'Colours change within its wings',
    color:'#b0567a', color2:'#e6a2c0',
    desc:'A perched Australian Masked Owl in the window. Tilt the banknote and the colours change within the owl’s wings.',
    how:'Tilt the banknote to see <b>colours change within the owl’s wings</b>.',
    markers:[ { side:'front', x:246, y:178, ring:20, label:'Colourful owl' } ],
    icon:'<path d="M8 2c3 0 4 3 4 6s-1 6-4 6-4-3-4-6 1-6 4-6z"/>'
  },
  {
    id:'reversing', name:'Reversing 100', short:'Within the Shrine of Remembrance',
    color:'#8a6a3a', color2:'#d2b07a',
    desc:'At the foot of the window is the Shrine of Remembrance. Tilt the banknote and the number 100 within the building changes direction: it alternately appears forwards, disappears, then appears backwards.',
    how:'Tilt the banknote to see the <b>number ‘100’ change direction</b> within the Shrine.',
    markers:[ { side:'front', x:250, y:280, ring:20, label:'Reversing 100' } ],
    icon:'<path d="M3 13h10M4 13V8h8v5M5 8l3-4 3 4"/>'
  },
  {
    id:'rolling', name:'Rolling colour effect', short:'Visible on both sides',
    color:'#a0306a', color2:'#e07ab0',
    desc:'Tilt the banknote and a band of colour rolls across this feature, which is visible on both sides. On the Melba side it lies within a bird shape near the top left corner; on the Monash side it is a prominent patch near the top right corner.',
    how:'Tilt the banknote to see a <b>rolling colour effect</b>, then turn it over: it shows on both sides.',
    markers:[
      { side:'front', x:86, y:70, ring:22, label:'Rolling colour (bird shape)' },
      { side:'back',  x:634, y:92, ring:24, label:'Rolling colour (patch)' },
    ],
    icon:'<circle cx="8" cy="8" r="5"/><path d="M3 8h10"/>'
  },
  {
    id:'fanwindow', name:'Fan in a small window', short:'Embossed, light and dark',
    color:'#4f7f8f', color2:'#a2cad6',
    desc:'A fan in a small clear window, with wattle flowers around it. The image is embossed and has a light and dark effect. The window should be an integral part of the banknote, not an addition.',
    how:'Look for a <b>fan in a small clear window</b>. The window must be part of the banknote itself.',
    markers:[
      { side:'front', x:637, y:252, ring:26, label:'Small window' },
      { side:'back',  x:83,  y:252, ring:26, label:'Small window' },
    ],
    icon:'<circle cx="8" cy="8" r="5"/><path d="M5 10l3-5 3 5"/>'
  },
  {
    id:'intaglio', name:'Intaglio print', short:'Raised, dark printing you can feel',
    color:'#5a4a2a', color2:'#b09a6a',
    desc:'The portraits of Dame Nellie Melba and Sir John Monash, the large numerals and other dark printing stand slightly raised from the polymer. On the Monash side the engraved Shrine of Remembrance is in intaglio too.',
    how:'Feel the <b>distinctive texture</b> of the dark printing: run a finger across the portraits and the large 100s.',
    markers:[
      { side:'front', x:440, y:150, ring:40, label:'Dame Nellie Melba' },
      { side:'back',  x:245, y:150, ring:40, label:'Sir John Monash' },
    ],
    icon:'<path d="M2 12h12M4 9h8M6 6h4"/>'
  },
  {
    id:'microprint', name:'Microprint', short:'Melba’s autobiography, Monash’s letter',
    color:'#6b5a2a', color2:'#c4ad6a',
    desc:'Tiny, clearly defined text in several places. On the Melba side it includes an excerpt from her autobiography <i>Melodies and Memories</i>, here below the La Bohème score: “If you wish to understand me at all, you must understand first and foremost that I am an Australian.” On the Monash side it includes an excerpt from a letter he wrote, here curving through the window: “Adopt as your fundamental creed that you will equip yourself for life, not solely for your own benefit…”',
    how:'Use a magnifier: the letters should be <b>sharp and clearly defined</b>, not blurred or broken.',
    markers:[
      { side:'front', x:614, y:164, ring:16, label:'Melodies and Memories' },
      { side:'back',  x:466, y:200, ring:16, label:'Monash letter' },
    ],
    icon:'<path d="M2 4h12M2 8h12M2 12h8"/>'
  },
  {
    id:'background', name:'Background print', short:'Multicoloured fine-line patterns',
    color:'#3f8f4f', color2:'#a6d68a',
    desc:'Multicoloured, multi-directional fine-line patterns are printed on each side of the banknote. This background printing should be very sharp.',
    how:'Look closely at the fine lines. Watch for <b>less clearly defined patterns, thicker or thinner lines, or colour differences</b>.',
    markers:[
      { side:'front', x:341, y:120, ring:20, label:'Background print' },
      { side:'back',  x:366, y:100, ring:20, label:'Background print' },
    ],
    icon:'<path d="M1 5c3-3 5 3 7 0s5 3 7 0M1 11c3-3 5 3 7 0s5 3 7 0"/>'
  },
  {
    id:'fluoro', name:'Fluorescent ink', short:'Glows under a UV lamp',
    color:'#6a3ab0', color2:'#b89ae6',
    desc:'Under ultraviolet light an owl and a wattle branch fluoresce on the Melba side, and the serial number and year of print on the Monash side. Use a UV light centred around 365 nm, in low ambient light.',
    how:'Switch to <b>Ultraviolet</b>, or hold the note under a 365 nm lamp: look for the <b>owl and wattle branch</b>, then turn it over for the <b>serial number</b>.',
    markers:[ { side:'front', x:60, y:140, ring:22, label:'Owl and wattle under UV' } ],
    icon:'<circle cx="8" cy="8" r="3"/><path d="M8 1v2M8 13v2M1 8h2M13 8h2"/>'
  },
  {
    id:'tactile', name:'Tactile feature', short:'Five raised bumps on each long edge',
    color:'#2f6a8a', color2:'#8ac0dc',
    desc:'Five raised bumps on each of the long edges of the banknote. On this scan the row along the top edge shows as small round reliefs at the left; the row along the bottom edge is not resolved in the scan.',
    how:'Feel for <b>five raised bumps</b> on each of the long edges of the banknote.',
    markers:[ { side:'front', x:90, y:18, ring:16, label:'Tactile bumps' } ],
    icon:'<circle cx="3" cy="8" r="1.5"/><circle cx="8" cy="8" r="1.5"/><circle cx="13" cy="8" r="1.5"/>'
  },
  {
    id:'serial', name:'Serial number', short:'Vertical, on the Monash side',
    color:'#2f5f3a', color2:'#7ab88a',
    desc:'Each banknote carries its own serial number, printed vertically at the left of the Monash side. It is one of the features that fluoresce under UV light. On this note it reads DK204519478.',
    how:'Check the serial is sharp and evenly printed; under a UV lamp it should <b>fluoresce</b>.',
    markers:[ { side:'back', x:15, y:124, ring:16, label:'Serial number' } ],
    icon:'<path d="M2 4h2v8H2zM6 4h2v8H6zM10 4h2v8h-2z"/>'
  },
];

// Exploded view: from the Monash side (first) to the Melba side (last). The polymer, with its clear
// windows, is the core. The order of the print layers is illustrative.
const LAYERS = [
  { id:'r-intaglio', name:'Intaglio ink',     group:'Monash side', side:'back',  feature:'intaglio',  kind:'pieces',
    pieces:[ ['back-portrait'], ['back-shrine'], ['back-100'] ] },
  { id:'r-serial',   name:'Serial number',    group:'Monash side', side:'back',  feature:'serial',    kind:'pieces',
    pieces:[ ['back-serial'] ] },
  { id:'r-offset',   name:'Background print', group:'Monash side', side:'back',  feature:'background', kind:'art' },
  { id:'r-rolling',  name:'Rolling colour patch', group:'Monash side', side:'back', feature:'rolling', kind:'pieces',
    pieces:[ ['back-rolling'] ] },
  { id:'substrate',  name:'Polymer, clear windows', group:'Polymer', side:'front', feature:'window', kind:'polymer', core:true },
  { id:'window',     name:'Window features',  group:'Polymer',     side:'front', feature:'window',    kind:'pieces',
    pieces:[ ['front-window'], ['front-fanwin'] ] },
  { id:'rolling',    name:'Rolling colour (bird)', group:'Melba side', side:'front', feature:'rolling', kind:'pieces',
    pieces:[ ['front-rolling'] ] },
  { id:'offset',     name:'Background print', group:'Melba side',  side:'front', feature:'background', kind:'art' },
  { id:'intaglio',   name:'Intaglio ink',     group:'Melba side',  side:'front', feature:'intaglio',  kind:'pieces',
    pieces:[ ['front-portrait'], ['front-rosina'], ['front-100'] ] },
  { id:'uv',         name:'UV: owl and wattle', group:'Melba side', side:'front', feature:'fluoro',   kind:'uv' },
];

const TWEAK_DEFAULS = {
  "defaultActive": ["window","fan3d","flyingowl","colourowl","reversing","rolling","fanwindow","intaglio","microprint","background","fluoro","tactile","serial"]
};

// Glow highlights: each feature's own cut-out (assets/layers/<src>.png) laid exactly over the artwork
// at its box [x, y, w, h] in 720x320 note space (boxes from assets/boxes.js).
const P = (side, src, x, y, w, h) => ({ side, src, box: (typeof BOXES !== 'undefined' && BOXES[src]) || [x, y, w, h] });
const GLOW = {
  window:    [ P('front','front-window',168,0,164,320), P('back','back-window',387,0,164,320) ],
  fan3d:     [ P('front','front-fan3d',226,13,52,41) ],
  flyingowl: [ P('front','front-flyingowl',230,46,48,53) ],
  colourowl: [ P('front','front-colourowl',230,141,34,83) ],
  reversing: [ P('front','front-shrine',222,254,57,50) ],
  rolling:   [ P('front','front-rolling',28,30,94,70), P('back','back-rolling',585,35,105,115) ],
  fanwindow: [ P('front','front-fanwin',581,194,109,119), P('back','back-fanwin',35,202,92,95) ],
  intaglio:  [ P('front','front-portrait',350,10,180,285), P('front','front-100',546,18,161,88), P('front','front-rosina',520,100,85,170),
               P('back','back-portrait',140,30,212,270), P('back','back-shrine',36,34,136,120), P('back','back-100',541,212,161,93) ],
  microprint:[ P('front','front-microprint',590,150,45,30), P('back','back-window-text',442,139,53,122) ],
  background:[ P('front','front-lines',328,4,26,232), P('back','back-lines',346,4,40,258) ],
  fluoro:    [ P('front','front-wattle',16,92,148,97), P('front','front-flyingowl',230,46,48,53) ],
  tactile:   [ P('front','front-tactile',20,13,139,11) ],
  serial:    [ P('back','back-serial',8,56,15,135) ],
};

// Detail callouts shown when a feature is zoomed into: [side, [[x, y], ...], label] in note units.
const DETAILS = {
  window:    [['front', [[251, 34]], '3D fan'], ['front', [[254, 72]], 'Flying owl'], ['front', [[246, 178]], 'Colourful owl'],
              ['front', [[250, 280]], 'Shrine: reversing 100'], ['front', [[200, 120]], 'Golden wattle frames the edges']],
  fan3d:     [['front', [[251, 30]], 'Appears raised or recessed'], ['front', [[232, 22]], 'Colourful lines']],
  flyingowl: [['front', [[268, 60]], 'Wings move as you tilt'], ['front', [[252, 82]], 'Changes colour']],
  colourowl: [['front', [[240, 175]], 'Colours change in the wings'], ['front', [[252, 150]], 'Australian Masked Owl']],
  reversing: [['front', [[250, 284]], '100: forwards, gone, backwards'], ['front', [[250, 262]], 'Shrine of Remembrance']],
  rolling:   [['front', [[90, 78]], 'Within a bird shape'], ['back', [[634, 92]], 'A patch near the top corner']],
  fanwindow: [['front', [[625, 255]], 'Embossed fan, light and dark'], ['front', [[660, 225]], 'Wattle flowers']],
  intaglio:  [['front', [[440, 150]], 'Portrait: raised ink'], ['front', [[620, 60]], 'Large numeral'],
              ['back', [[245, 150]], 'Sir John Monash'], ['back', [[100, 90]], 'Shrine of Remembrance']],
  microprint:[['front', [[606, 156]], '“If you wish to understand me…”'], ['front', [[626, 172]], 'Melodies and Memories'],
              ['back', [[452, 175]], 'A letter by Monash'], ['back', [[488, 236]], '“Adopt as your fundamental creed…”']],
  background:[['front', [[341, 60]], 'Fine lines, many directions'], ['front', [[341, 200]], 'Should be very sharp'],
              ['back', [[366, 100]], 'On each side of the note']],
  fluoro:    [['front', [[60, 140]], 'Wattle branch'], ['front', [[254, 72]], 'Owl'], ['back', [[15, 124]], 'Serial and year of print']],
  tactile:   [['front', [[25, 18]], 'One'], ['front', [[154, 18]], 'Five bumps, top edge']],
  serial:    [['back', [[15, 70]], 'Two letters, then nine digits'], ['back', [[15, 170]], 'Fluoresces under UV']],
};
