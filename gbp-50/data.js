// Plain script (not a module) so the page also works when opened straight from disk (file://)
// Bank of England £50 polymer note (Alan Turing; issued 23 June 2021). The note shown is the
// Queen Elizabeth II version, from the Bank of England's own specimen images.
// Feature wording follows the Bank of England, bankofengland.co.uk/banknotes/polymer-50-pound-note.
// The Bank calls the monarch's side the front and the Turing side the back.
const FEATURES = [
  {
    id:'hologram', name:'Hologram', short:'“Fifty” changes to “Pounds” as you tilt',
    desc:'A metallic hologram at the foot of the front of the note. The word changes between “Fifty” and “Pounds” when the note is tilted from side to side.',
    how:'Tilt the note from side to side. Check the words change between <b>“Fifty”</b> and <b>“Pounds”</b>.',
  },
  {
    id:'window', name:'See-through windows', short:'Gold and green foil in front, silver behind',
    desc:'The main window is a clear area of the polymer with a metallic image over it. The foil is gold and green on the front of the note and silver on the back. Within the two gold foil squares, the image changes between “50” and a “£” symbol when the note is tilted.',
    how:'Look at the metallic image over the main window. Check the foil is <b>gold and green on the front</b> and <b>silver on the back</b>, and tilt the note: the two squares swap <b>“50”</b> and <b>“£”</b>.',
  },
  {
    id:'portrait', name:'Portrait in the window', short:'The monarch, printed on the clear window',
    desc:'A portrait of the monarch is printed on the window, with “£50 Bank of England” printed twice around the edge. Because it is on a clear window it can be seen from both sides of the note.',
    how:'Look through the main window: the <b>portrait</b> and the words <b>“£50 Bank of England”</b> (twice, around the edge) should be sharp, and visible from both sides.',
  },
  {
    id:'crown', name:'Silver foil patch', short:'A 3D image of the coronation crown',
    desc:'A silver foil patch above the main see-through window on the front of the note contains a 3D image of the coronation crown.',
    how:'Look above the main window on the front. The <b>silver patch</b> should show a <b>3D crown</b> that shifts and catches the light as you tilt.',
  },
  {
    id:'redfoil', name:'Red foil patch', short:'Flower-shaped, with the letters “AT”',
    desc:'A metallic, red foil patch on the back of the note contains the letters “AT”. It is directly behind the silver crown on the front. Its flower shape is based on the image of a sunflower head, linked to Turing’s morphogenetic work (the study of patterns in nature) in later life.',
    how:'Turn the note over. Directly behind the silver crown you should find a <b>metallic red patch</b> with the letters <b>“AT”</b>.',
  },
  {
    id:'smallwindow', name:'Second, smaller window', short:'Bottom corner, with raised print over it',
    desc:'A second, smaller see-through window is in the bottom corner of the note. On the front you can feel raised print over it.',
    how:'Look for the <b>small clear window</b> in the bottom corner (bottom right on the front, bottom left on the back).',
  },
  {
    id:'raised', name:'Raised print', short:'On “Bank of England” and over the small window',
    desc:'The note is printed on polymer, a thin and flexible plastic. On the front of the note you can feel raised print, for example on the words “Bank of England” and in the bottom right corner, over the smaller window.',
    how:'Run a finger over the words <b>“Bank of England”</b> on the front: the print should feel <b>raised</b> against the smooth polymer.',
  },
  {
    id:'tactile', name:'Raised dots', short:'Four clusters, top left of the front',
    desc:'On the front of the note (the side with raised print) there are four clusters of raised dots in the top left hand corner. This tactile feature helps blind and partially sighted people identify the value of the note.',
    how:'Feel the <b>top left corner</b> of the front: there are <b>four clusters</b> of raised dots on the £50.',
  },
  {
    id:'uv', name:'Ultraviolet number', short:'A bright red and green 50 under UV',
    desc:'Under a good quality ultraviolet light, the number “50” appears in bright red and green on the front of the note, against a duller background.',
    how:'Under a <b>UV lamp</b>, look at the front: a <b>“50”</b> should appear in <b>bright red and green</b> while the rest of the note stays dull.',
  },
  {
    id:'microprint', name:'Print quality', short:'Sharp lines, and microlettering under the portrait',
    desc:'The printed lines and colours on the note are sharp, clear and free from smudges or blurred edges. With a magnifying glass you will see the value of the note written in tiny letters and numbers below the monarch’s portrait.',
    how:'Use a <b>magnifying glass</b> below the portrait: the value should be written in <b>tiny letters and numbers</b>, crisp, not blurred.',
  },
  {
    id:'serial', name:'Unique numbering', short:'Printed twice on the back',
    desc:'A unique serial number is printed horizontally and vertically on the back of the note. The horizontal number, in the bottom right corner, is made up of multi-coloured letters and numbers which increase in height from left to right. The vertical number runs down the left-hand side; its numbers and letters are the same height and colour.',
    how:'Both numbers must match. Here both read <b>AA44 699671</b>: the horizontal one <b>multi-coloured and growing</b> in height, the vertical one <b>even</b>.',
  },
  {
    id:'turing', name:'Alan Turing', short:'Portrait based on a 1951 photograph',
    desc:'Alan Turing’s portrait is based on a photo taken in 1951 by Elliott & Fry, part of the Photographs Collection at the National Portrait Gallery. Turing provided the theoretical underpinnings for the modern computer, and played a pivotal role in the development of early computers at the National Physical Laboratory and later at the University of Manchester.',
    how:'The portrait is a design feature, not a check in itself. Its fine line-work should be <b>sharp and clear</b>, like all the print on a genuine note.',
  },
  {
    id:'artwork', name:'Turing’s work', short:'Table and formulae, ticker tape, machines',
    desc:'The design on the back celebrates Turing and his pioneering work with computers: a mathematical table and formulae from his 1936 paper “On Computable Numbers, with an application to the Entscheidungsproblem”; ticker tape depicting his birth date (23 June 1912) in binary code; the ACE Pilot Machine; technical drawings for the British Bombe; and technical drawings from the ACE Progress Report in the background.',
    how:'A design feature. The table’s letters and the binary digits on the <b>ticker tape</b> should be crisp and readable.',
  },
  {
    id:'quote', name:'The quote', short:'The Times, 11 June 1949',
    desc:'“This is only a foretaste of what is to come and only the shadow of what is going to be”: a quote from Alan Turing, given in an interview to The Times newspaper on 11 June 1949.',
    how:'A design feature. The lettering should be sharp, with clean edges.',
  },
  {
    id:'signature', name:'Turing’s signature', short:'From a 1947 visitors’ book',
    desc:'Turing’s signature has been taken from the visitor’s signature book on display at Bletchley Park Trust, signed in 1947.',
    how:'A design feature, printed in white over the jacket. Its strokes should be clean and unbroken.',
  },
  {
    id:'cashier', name:'Chief Cashier’s signature', short:'Sarah John',
    desc:'The note carries the signature of Sarah John, the Bank of England’s Chief Cashier, under the promise “for the Governor and Company of the Bank of England”.',
    how:'A design feature. The red signature and the words <b>CHIEF CASHIER</b> should be sharp.',
  },
];

// Exploded view: the polymer note pulled apart. The polymer film (white except for its two clear
// windows) is the core; the reverse is printed on one side and the obverse on the other.
const LAYERS = [
  { id:'r-serial',  name:'Serial numbers',     group:'Reverse',   side:'back',  feature:'serial',   kind:'pieces',
    pieces:[ ['back-serial-v'], ['back-serial-h'] ] },
  { id:'r-foil',    name:'Red foil patch',     group:'Reverse',   side:'back',  feature:'redfoil',  kind:'pieces',
    pieces:[ ['back-redfoil'] ] },
  { id:'r-print',   name:'Reverse print',      group:'Reverse',   side:'back',  feature:'turing',   kind:'art' },
  { id:'substrate', name:'Polymer, two clear windows', group:'Substrate', side:'front', feature:'window', kind:'paper', core:true },
  { id:'o-print',   name:'Obverse print',      group:'Obverse',   side:'front', feature:'portrait', kind:'art' },
  { id:'o-foil',    name:'Foils and hologram', group:'Obverse',   side:'front', feature:'hologram', kind:'pieces',
    pieces:[ ['front-windowfoil'], ['front-crown'], ['front-hologram'] ] },
  { id:'o-raised',  name:'Raised print',       group:'Obverse',   side:'front', feature:'raised',   kind:'pieces',
    pieces:[ ['front-raised'], ['front-tactile'] ] },
  { id:'uv',        name:'UV: the 50 glows',   group:'Obverse',   side:'front', feature:'uv',       kind:'uv' },
];

const TWEAK_DEFAULS = {
  "defaultActive": ["hologram","window","windowb","portrait","crown","redfoil","smallwindow","raised","tactile","uv","microprint","serial","turing","artwork","quote","signature","cashier"]
};

// Glow highlights: each feature's own cut-out (assets/layers/<src>.png) laid exactly over the artwork
// at its box [x, y, w, h] in 720x320 note space (boxes from assets/boxes.js).
const P = (side, src, mirror) => ({ side, src, box: BOXES[src], mirror: !!mirror });
const GLOW = {
  hologram:   [ P('front','front-hologram') ],
  window:     [ P('front','front-window'), P('back','back-window') ],
  portrait:   [ P('front','front-portrait'), P('back','back-portrait') ],
  crown:      [ P('front','front-crown') ],
  redfoil:    [ P('back','back-redfoil') ],
  smallwindow:[ P('front','front-smallwindow'), P('back','back-smallwindow') ],
  raised:     [ P('front','front-raised') ],
  tactile:    [ P('front','front-tactile') ],
  uv:         [ P('front','uv-50') ],
  microprint: [ P('front','front-microprint') ],
  serial:     [ P('back','back-serial-v'), P('back','back-serial-h') ],
  turing:     [ P('back','back-turing') ],
  artwork:    [ P('back','back-table'), P('back','back-tape') ],
  quote:      [ P('back','back-quote') ],
  signature:  [ P('back','back-signature') ],
  cashier:    [ P('front','front-cashier') ],
};

// Detail callouts shown when a feature is zoomed into: [side, [[x, y], ...], label] in note units.
const DETAILS = {
  hologram:  [['front', [[163, 289]], '“Fifty” face-on'], ['front', [[190, 300]], '“Pounds” tilted side to side']],
  window:    [['front', [[162, 108]], 'Green foil'], ['front', [[162, 152]], 'Gold square: £ ↔ 50'],
              ['front', [[162, 193]], 'Gold square: 50 ↔ £'], ['front', [[118, 150]], 'Clear polymer'],
              ['back', [[560, 165]], 'Silver from the back']],
  portrait:  [['front', [[76, 160]], 'The monarch'], ['front', [[50, 120]], '£50 Bank of England, twice'],
              ['back', [[643, 160]], 'Seen from the back too']],
  crown:     [['front', [[163, 38]], '3D coronation crown'], ['front', [[163, 70]], 'Above the main window']],
  redfoil:   [['back', [[556, 40]], 'The letters AT'], ['back', [[580, 24]], 'Sunflower head']],
  smallwindow:[['front', [[652, 262]], 'Clear window'], ['front', [[652, 285]], 'Raised print over it'],
              ['back', [[64, 262]], 'Bottom left, from the back']],
  raised:    [['front', [[300, 45]], '“Bank of England”'], ['front', [[430, 45]], 'Raised, feel it']],
  tactile:   [['front', [[35, 24]], 'Cluster 1'], ['front', [[35, 84]], 'Cluster 2'],
              ['front', [[35, 144]], 'Cluster 3'], ['front', [[35, 204]], 'Cluster 4']],
  uv:        [['front', [[350, 40]], 'Bright red and green'], ['front', [[395, 60]], 'Only under UV']],
  microprint:[['front', [[500, 284]], 'The value, in tiny figures'], ['front', [[600, 284]], 'Below the portrait']],
  serial:    [['back', [[41, 80]], 'Vertical: even height'], ['back', [[615, 281]], 'Horizontal: grows, multi-coloured']],
  turing:    [['back', [[372, 125]], 'Elliott & Fry, 1951'], ['back', [[400, 220]], 'Engraved line-work']],
  artwork:   [['back', [[160, 82]], '1936 paper: table'], ['back', [[160, 170]], 'Formulae'],
              ['back', [[110, 205]], '23 June 1912 in binary']],
  quote:     [['back', [[340, 270]], 'The Times, 11 June 1949']],
  signature: [['back', [[420, 245]], 'Bletchley Park visitors’ book, 1947']],
  cashier:   [['front', [[40, 88]], 'Sarah John'], ['front', [[30, 100]], 'Chief Cashier']],
};
