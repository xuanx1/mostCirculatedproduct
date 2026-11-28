// Plain script (not a module) so the page also works when opened straight from disk (file://)
// EUR 500 banknote, first series (2002), signed by Jean-Claude Trichet.
// Feature wording follows the ECB (Quick Guide and Trainer's Guide to the euro banknotes) and the
// Deutsche Bundesbank's pages on the first-series EUR 500; sources are listed in README.md.
const FEATURES = [
  {
    id:'hologram', name:'Hologram patch', short:'The value and a window or doorway',
    color:'#6a4fb3', color2:'#a994e8',
    desc:'A foil patch on the right of the front. Tilt the note and the hologram image changes between the value, 500, and a window or doorway. In the background, rainbow-coloured concentric circles of tiny letters move from the centre to the edges of the patch. Held against the light, perforations in the patch form the € symbol, and small numbers show the value.',
    how:'Tilt the note. The <b>500 and a window or doorway</b> should take turns, with rainbow circles moving across the patch. Against the light, look for the <b>€ symbol</b> in tiny holes.',
    markers:[ { side:'front', x:657, y:245 } ],
    icon:''
  },
  {
    id:'ovi', name:'Colour-changing number', short:'On the back: purple to olive green or brown',
    color:'#5b2a86', color2:'#9d6cc8',
    desc:'The value numeral in the lower right corner of the back is printed in colour-changing ink (silk-screen printed). Tilt the note and it changes colour from purple to olive green or brown.',
    how:'Turn the note over and tilt it. The <b>500</b> in the lower right corner should change from <b>purple to olive green or brown</b>. A copy keeps one colour.',
    markers:[ { side:'back', x:640, y:282 } ],
    icon:''
  },
  {
    id:'watermark', name:'Watermark', short:'A window and the value, in the paper',
    color:'#7a6a8a', color2:'#b9a8c9',
    desc:'Made by varying the thickness of the paper, in the blank area on the left of the front. Hold the note against the light and the main motif, a window, and the value 500 become visible; the 500 is brighter than the paper around it. The transitions between light and dark are smooth. Put the note on a dark surface and the light areas become darker. It can be seen from both sides.',
    how:'Hold the note <b>against the light</b>: a <b>window and the value 500</b> should appear in the blank area, with smooth shading. On a dark surface the light parts turn darker.',
    markers:[ { side:'front', x:85, y:150 }, { side:'back', x:635, y:150 } ],
    icon:''
  },
  {
    id:'thread', name:'Security thread', short:'A dark line, “EURO” and “500” on it',
    color:'#4b3a6e', color2:'#8d7ab8',
    desc:'A thread embedded in the paper, in the middle third of the note. Held against the light it appears as a dark stripe, with “500 EURO” in small letters and “500” in microletters, alternating in normal and mirror writing. It can be seen from the front and the back.',
    how:'Hold the note <b>against the light</b>. A <b>dark stripe</b> should run from top to bottom, and with good eyes or a magnifier you can read <b>EURO</b> and <b>500</b> on it.',
    markers:[ { side:'front', x:323, y:160 } ],
    icon:''
  },
  {
    id:'register', name:'See-through number', short:'Front and back marks join into 500',
    color:'#b0408a', color2:'#e08ac0',
    desc:'Irregular marks printed in the top corner, on both sides of the note: top left on the front, top right on the back. Hold the note against the light and the marks combine perfectly to form the value numeral, 500 (read in mirror writing from the back).',
    how:'Hold the note <b>against the light</b> and look at the top corner. The marks on the front and back should join into a complete <b>500</b>, with no gaps or overlaps.',
    markers:[ { side:'front', x:52, y:38 }, { side:'back', x:668, y:38 } ],
    icon:''
  },
  {
    id:'intaglio', name:'Raised print', short:'Main image, lettering and large 500',
    color:'#7a2a4a', color2:'#c07090',
    desc:'Intaglio printing: the ink is pressed into the paper from engraved plates, so it stands up from the surface. On the front, the main image (the window and gateway), the lettering (the copyright line with the ECB’s initials BCE ECB EZB EKT EKP and the year 2002) and the large value numeral feel thicker. Intaglio is printed on the front only.',
    how:'Run a fingernail or fingertip over the <b>large 500</b>, the <b>initials line</b> and the <b>main image</b>. The ink should feel <b>raised</b>, not flat.',
    markers:[ { side:'front', x:530, y:60 } ],
    icon:''
  },
  {
    id:'tactile', name:'Tactile marks', short:'Raised lines along the right edge',
    color:'#2f3a8a', color2:'#7a86d8',
    desc:'The €200 and €500 notes carry extra tactile marks near their edges, to help blind and visually impaired people tell them apart. On the €500 they are short diagonal raised lines along the right edge of the front.',
    how:'Run a finger along the <b>right edge of the front</b>. You should feel the <b>short raised lines</b>, in two groups.',
    markers:[ { side:'front', x:690, y:90 } ],
    icon:''
  },
  {
    id:'architecture', name:'Architecture', short:'Gateway and bridge: modern 20th-century',
    color:'#8a3a6a', color2:'#c87aa8',
    desc:'Every first-series note shows one period of Europe’s architectural history; the €500’s is modern 20th-century architecture. The front shows windows and a gateway, symbols of the spirit of openness and cooperation in Europe; the back shows a bridge, a metaphor for communication between the people of Europe and with the rest of the world. None depicts a real building or bridge.',
    how:'With a <b>magnifier</b>, the engraved lines of the main image should be sharp and continuous; a printed copy turns them into dots.',
    markers:[ { side:'front', x:450, y:220 }, { side:'back', x:270, y:90 } ],
    icon:''
  },
  {
    id:'signature', name:'Signature', short:'The ECB President: Jean-Claude Trichet',
    color:'#3a3a8a', color2:'#8a8ad0',
    desc:'Euro banknotes bear the signature of the President of the European Central Bank: Willem F. Duisenberg, the first President, or Jean-Claude Trichet, who succeeded him on 1 November 2003 This note is signed by Jean-Claude Trichet. Notes with either signature are valid. Under ultraviolet light the signature turns green.',
    how:'The signature should be <b>sharp</b>, printed in dark blue, and turn <b>green under a UV lamp</b>.',
    markers:[ { side:'front', x:255, y:65 } ],
    icon:''
  },
  {
    id:'eurion', name:'Small circles', short:'They glow under UV; EURion pattern',
    color:'#b08a14', color2:'#e6c34d',
    desc:'Small yellow circles are scattered on both sides of the note. The ECB lists the small circles among the parts of the front that glow under ultraviolet light. Independent research (Markus Kuhn, University of Cambridge, 2002) found that such circles form the EURion constellation, which many colour copiers and imaging programs detect so as to refuse to copy a note; the ECB does not document this.',
    how:'Under a <b>UV lamp</b>, the small circles on the front should <b>glow</b>.',
    markers:[ { side:'front', x:195, y:150 }, { side:'back', x:400, y:35 } ],
    icon:''
  },
  {
    id:'serial', name:'Serial numbers', short:'Twice on the back, letterpress',
    color:'#2a2a2a', color2:'#8a8a8a',
    desc:'Each note has a unique serial number, printed twice on the back by letterpress, with numbering boxes: horizontally at the top right and again at the lower left. Under an infrared viewer the number at the top right can still be read. This note reads S00000004795.',
    how:'Both numbers must <b>match exactly</b>. With an <b>infrared viewer</b> the top-right number stays readable.',
    markers:[ { side:'back', x:545, y:42 } ],
    icon:''
  },
  {
    id:'map', name:'Map of Europe', short:'Back; glows yellow or green under UV',
    color:'#8a3a7a', color2:'#c87ab8',
    desc:'The back shows a map of Europe beside the bridge. Under ultraviolet light the map, the bridge and the value numeral on the back appear in yellow or green, while the paper itself stays dull.',
    how:'Under a <b>UV lamp</b>, the map, the bridge and the 500 at the lower left of the back should glow <b>yellow or green</b>.',
    markers:[ { side:'back', x:450, y:230 } ],
    icon:''
  },
  {
    id:'ir', name:'Infrared', short:'Only parts of the design remain',
    color:'#7a3a2a', color2:'#c8806a',
    desc:'Through an infrared viewer most of the print disappears. On the front, parts of the motif can be seen in the right third of the note; on the back, the serial number at the top right can be read. (This page has no infrared view: the issuers do not say which parts of the motif remain.)',
    how:'With an <b>IR viewer</b>: parts of the front’s <b>right third</b>, and the <b>top-right serial number</b> on the back.',
    markers:[ { side:'front', x:600, y:150 }, { side:'back', x:545, y:42 } ],
    icon:''
  },
];

// Exploded view: the note pulled apart in both directions, in printing order (ECB Trainer's Guide):
// offset on both sides, intaglio on the front only, silk-screen (colour-changing number), hot-stamped
// foil (hologram patch), letterpress (serial numbers). The cotton paper, with watermark and thread, is the core.
const LAYERS = [
  { id:'r-serial',  name:'Serial numbers',      group:'Reverse', side:'back',  feature:'serial',    kind:'pieces',
    pieces:[ ['back-serial-top'], ['back-serial-left'] ] },
  { id:'r-ovi',     name:'Colour-changing ink', group:'Reverse', side:'back',  feature:'ovi',       kind:'pieces',
    pieces:[ ['back-ovi'] ] },
  { id:'r-offset',  name:'Offset print',        group:'Reverse', side:'back',  feature:'architecture', kind:'art' },
  { id:'thread',    name:'Security thread',     group:'Paper',   side:'front', feature:'thread',    kind:'pieces',
    pieces:[ ['front-thread'] ] },
  { id:'substrate', name:'Cotton paper',        group:'Paper',   side:'front', feature:null,        kind:'paper', core:true },
  { id:'watermark', name:'Watermark',           group:'Paper',   side:'front', feature:'watermark', kind:'pieces',
    pieces:[ ['watermark-ghost'] ] },
  { id:'offset',    name:'Offset print',        group:'Obverse', side:'front', feature:'architecture', kind:'art' },
  { id:'intaglio',  name:'Intaglio ink',        group:'Obverse', side:'front', feature:'intaglio',  kind:'pieces',
    pieces:[ ['front-architecture'], ['front-numeral'], ['front-initials'], ['front-bar'], ['front-tactile-top'], ['front-tactile-bottom'] ] },
  { id:'foil',      name:'Hologram foil',       group:'Obverse', side:'front', feature:'hologram',  kind:'pieces',
    pieces:[ ['front-hologram'] ] },
  { id:'uv',        name:'UV: what glows',      group:'Obverse', side:'front', feature:'map',       kind:'uv' },
];

const TWEAK_DEFAULS = {
  "defaultActive": ["hologram","ovi","watermark","thread","register","intaglio","tactile","architecture","signature","eurion","serial","map","ir"]
};

// Glow highlights: each feature's own cut-out (assets/layers/<src>.png) laid exactly over the artwork
// at its box [x, y, w, h] in 720x320 note units (boxes from assets/boxes.js).
const B_ = (src) => (typeof BOXES !== 'undefined' && BOXES[src]) || [0, 0, 0, 0];
const P = (side, src, mirror) => {
  const b = B_(src);
  return { side, src, box: mirror ? [720 - b[0] - b[2], b[1], b[2], b[3]] : b, mirror: !!mirror };
};
const GLOW = {
  hologram:    [ P('front','front-hologram') ],
  ovi:         [ P('back','back-ovi') ],
  watermark:   [ P('front','watermark-ghost'), P('back','watermark-ghost',true) ],     // in the paper: mirrored from the back
  thread:      [ P('front','front-thread'), P('back','front-thread',true) ],
  register:    [ P('front','front-register'), P('back','back-register-b') ],
  intaglio:    [ P('front','front-numeral'), P('front','front-initials'), P('front','front-architecture'), P('front','front-bar') ],
  tactile:     [ P('front','front-tactile-top'), P('front','front-tactile-bottom') ],
  architecture:[ P('front','front-architecture'), P('back','back-bridge') ],
  signature:   [ P('front','front-signature') ],
  eurion:      [ P('front','front-eurion'), P('back','back-eurion-b') ],
  serial:      [ P('back','back-serial-top'), P('back','back-serial-left') ],
  map:         [ P('back','back-map') ],
  ir:          [ P('front','front-ir-right'), P('back','back-serial-top') ],
};

// Detail callouts shown when a feature is zoomed into: [side, [[x, y], ...], label] in note units.
const DETAILS = {
  hologram:   [['front', [[657, 222]], 'Value 500 or a window / doorway'], ['front', [[628, 262]], 'Rainbow circles of tiny letters'],
               ['front', [[690, 258]], 'Against the light: € in tiny holes']],
  ovi:        [['back', [[600, 282]], 'Purple face-on'], ['back', [[675, 282]], 'Olive green or brown when tilted']],
  watermark:  [['front', [[80, 120]], 'Window: the main motif'], ['front', [[80, 222]], 'Value 500, brighter against the light'],
               ['back', [[640, 150]], 'Seen from the back, mirrored']],
  thread:     [['front', [[323, 70]], '“500 EURO” and “500”'], ['front', [[323, 250]], 'A dark stripe against the light']],
  register:   [['front', [[30, 40]], 'Front: part of the 500'], ['front', [[78, 30]], 'Completed by the back’s marks'],
               ['back', [[668, 38]], 'Back: the other part']],
  intaglio:   [['front', [[285, 18]], 'Copyright line and initials'], ['front', [[530, 45]], 'Large value numeral'],
               ['front', [[470, 230]], 'Main image']],
  tactile:    [['front', [[690, 90]], 'Raised lines, upper right'], ['front', [[690, 285]], 'Raised lines, lower right']],
  architecture:[['front', [[400, 200]], 'Gateway and windows'], ['front', [[540, 170]], 'Modern 20th-century'],
               ['back', [[270, 90]], 'Bridge'], ['back', [[100, 70]], 'A metaphor for communication']],
  signature:  [['front', [[240, 70]], 'Jean-Claude Trichet'], ['front', [[310, 50]], 'Green under UV']],
  eurion:     [['front', [[195, 150]], 'Small circles'], ['front', [[630, 145]], 'Glow under UV'],
               ['back', [[400, 35]], 'Top of the back'], ['back', [[372, 230]], 'Beside the map']],
  serial:     [['back', [[545, 42]], 'Top right: IR-readable'], ['back', [[195, 245]], 'Same number, lower left']],
  map:        [['back', [[470, 200]], 'Map of Europe'], ['back', [[420, 290]], 'Yellow or green under UV']],
  ir:         [['front', [[600, 150]], 'Right third: parts of the motif']],
};
