// Plain script (not a module) so the page also works when opened straight from disk (file://)
// Canadian $100 polymer note, Frontier series (issued 14 November 2011).
// Security-feature wording follows the Bank of Canada: bankofcanada.ca/banknotes/100-polymer-note-security-features/
// and its employee handbook "Canada's polymer notes" (bankofcanada.ca/wp-content/uploads/2012/05/employee_handbook.pdf).
// Design elements follow bankofcanada.ca/banknotes/100-polymer-note-security-features/100-polymer-note-design-elements/
// and the Bank's "The Design of Canada's $100 Polymer Note" (design_100.pdf).
const FEATURES = [
  {
    id:'polymer', name:'Polymer', short:'One piece of polymer, with clear areas',
    color:'#8a5a2b', color2:'#c99a6a',
    desc:'The note is made from a single piece of polymer with some transparent areas: the large window and the outline of the frosted maple leaf. It has a smooth, unique texture.',
    how:'<b>Feel</b> the smooth, unique texture of the note, and look for the transparent areas.',
    markers:[ { side:'front', x:40, y:140, ring:16, label:'Polymer' } ],
    icon:'<rect x="2" y="4" width="12" height="8" rx="1"/>'
  },
  {
    id:'raised', name:'Raised ink', short:'Large number, shoulders, Bank of Canada',
    color:'#6b3a1a', color2:'#b8743a',
    desc:'Raised ink can be felt on the large number, on the shoulders of the large portrait, and on the words “Bank of Canada” and “Banque du Canada”.',
    how:'<b>Feel</b> the raised ink on the large <b>100</b>, on Sir Robert Borden’s <b>shoulders</b>, and on the words <b>Bank of Canada / Banque du Canada</b>.',
    markers:[ { side:'front', x:80, y:230, ring:20, label:'Raised ink' } ],
    icon:'<path d="M2 12h12M4 9h8M6 6h4"/>'
  },
  {
    id:'window', name:'Large window', short:'Clear from top to bottom',
    color:'#3f6f8a', color2:'#8fc0da',
    desc:'A large transparent area runs from the top to the bottom of the note. It holds a detailed metallic portrait and building, the word “Canada”, which is transparent and feels slightly raised, and small numbers matching the note’s value.',
    how:'<b>Look</b> through the large window: it should be clear, with the metallic portrait and building, the transparent word Canada and the small 100s in it.',
    markers:[ { side:'front', x:500, y:230, ring:20, label:'Large window' }, { side:'back', x:220, y:230, ring:20, label:'Large window' } ],
    icon:'<rect x="5" y="1" width="6" height="14" rx="1"/>'
  },
  {
    id:'mportrait', name:'Metallic portrait', short:'Matches the large portrait',
    color:'#5f6f86', color2:'#b9c6da',
    desc:'A detailed metallic portrait in the large window. It should match the large portrait on the front. Tilt the note and it changes colour; flip it and the same image is repeated on the back in the same colours and detail. The Bank of Canada colourized it for adaptation as a holographic feature.',
    how:'<b>Look</b> at the details of the metallic portrait: it matches the large portrait. <b>Tilt</b> to see it change colour, and <b>flip</b> to see it repeated on the back.',
    markers:[ { side:'front', x:540, y:60, ring:22, label:'Metallic portrait' }, { side:'back', x:180, y:60, ring:22, label:'Metallic portrait' } ],
    icon:'<circle cx="8" cy="6" r="3"/><path d="M3 14c1-3 3-4 5-4s4 1 5 4"/>'
  },
  {
    id:'mbuilding', name:'Metallic building', short:'The East Block tower, sharp colour changes',
    color:'#6a5a8a', color2:'#c4b4e6',
    desc:'A detailed metallic image of the East Block of Parliament, with its tower, in the large window. Tilt the note to see sharp colour changes in the building. It is repeated on the back in the same colours and detail.',
    how:'<b>Look</b> at the details in the metallic building and <b>tilt</b> the note: the colours should change sharply. <b>Flip</b> it to see the same building on the back.',
    markers:[ { side:'front', x:540, y:270, ring:22, label:'Metallic building' }, { side:'back', x:180, y:270, ring:22, label:'Metallic building' } ],
    icon:'<path d="M8 1l3 5v9H5V6z"/>'
  },
  {
    id:'transtext', name:'Transparent text', short:'The word Canada, slightly raised',
    color:'#4f7f96', color2:'#a6d2e6',
    desc:'The word “Canada” runs across the large window. It is transparent and feels slightly raised.',
    how:'<b>Look</b> at the word <b>Canada</b> in the large window. It is transparent, and you can <b>feel</b> that it is slightly raised.',
    markers:[ { side:'front', x:511, y:131, ring:14, label:'Transparent text' }, { side:'back', x:209, y:131, ring:14, label:'Transparent text' } ],
    icon:'<path d="M3 4h10M8 4v9"/>'
  },
  {
    id:'smallnum', name:'Small numbers', short:'100s in and around the window',
    color:'#7a5a3a', color2:'#c9a47a',
    desc:'Small numbers matching the value of the note appear in and around the large window. Some of the numbers appear in reverse.',
    how:'<b>Look</b> at the small numbers in and around the window. They should read <b>100</b>, some of them in reverse.',
    markers:[ { side:'front', x:578, y:100, ring:14, label:'Small numbers' }, { side:'back', x:142, y:100, ring:14, label:'Small numbers' } ],
    icon:'<path d="M4 4v8M8 5a2 2 0 0 1 2 2v2a2 2 0 0 1-4 0V7a2 2 0 0 1 2-2z"/>'
  },
  {
    id:'leafborder', name:'Maple leaf border', short:'Leaves around the window, some cross in',
    color:'#8a2e14', color2:'#d4704a',
    desc:'Maple leaves border the large window, and some of the leaves cross into it.',
    how:'<b>Look</b> at the maple leaves that border the large window. Some of them cross into the window.',
    markers:[ { side:'front', x:458, y:40, ring:16, label:'Maple leaf border' }, { side:'back', x:262, y:46, ring:16, label:'Maple leaf border' } ],
    icon:'<path d="M8 1l1.5 3 2.5-1-1 3 3 1-3 2 1 2-3-.5L8 15l-1-4.5L4 11l1-2-3-2 3-1-1-3 2.5 1z"/>'
  },
  {
    id:'frosted', name:'Frosted maple leaf window', label:'Frosted maple leaf', short:'A transparent outline',
    color:'#5a7a8a', color2:'#b4d0dc',
    desc:'A frosted maple leaf with a transparent outline, on the left of the front (the right of the back).',
    how:'<b>Look</b> at the frosted maple leaf window to see that it has a <b>transparent outline</b>.',
    markers:[ { side:'front', x:78, y:99, ring:16, label:'Frosted maple leaf' }, { side:'back', x:642, y:99, ring:16, label:'Frosted maple leaf' } ],
    icon:'<path d="M8 2l1.5 3 2.5-1-1 3 3 1-3 2 1 2-3-.5L8 14l-1-2.5L4 12l1-2-3-2 3-1-1-3 2.5 1z"/>'
  },
  {
    id:'hidden', name:'Hidden numbers', short:'A circle of 100s, against a small light',
    color:'#6a6a7a', color2:'#c0c0d4',
    desc:'If you have checked the other features and are still not sure, look at a small light (an incandescent bulb or a pot light about a metre away) through the frosted maple leaf window, with the note right up to your eye. A circle of numbers matching the value of the note appears. It works only from the front of the note.',
    how:'Hold the note close to your eye and look at a <b>small light</b> through the frosted maple leaf. A <b>circle of 100s</b> should appear. Never use the sun, a laser or a bright LED.',
    markers:[ { side:'front', x:117, y:105, ring:12, label:'Hidden numbers' } ],
    icon:'<circle cx="8" cy="8" r="5"/><circle cx="8" cy="8" r="1.5"/>'
  },
  {
    id:'portrait', name:'Sir Robert L. Borden', short:'Prime Minister 1911–1920',
    color:'#7a5232', color2:'#c49a72',
    desc:'The large portrait is of Sir Robert L. Borden, Canada’s eighth Prime Minister (1911–1920), who led the country through the First World War. It is based on a photograph from Library and Archives Canada.',
    how:'Compare the large portrait with the <b>metallic portrait</b> in the window: they should match. Feel the <b>raised ink</b> on his shoulders.',
    markers:[ { side:'front', x:330, y:95, ring:30, label:'Portrait' } ],
    icon:'<circle cx="8" cy="6" r="3"/><path d="M3 14c1-3 3-4 5-4s4 1 5 4"/>'
  },
  {
    id:'researcher', name:'Researcher at a microscope', label:'Researcher', short:'Medical innovation',
    color:'#a8642a', color2:'#e0a468',
    desc:'The back celebrates Canadian medical innovation. The researcher, drawn by the bank note designers, represents Canada’s long-standing commitment to medical research; the microscope is based on a Carl Zeiss Axioplan 2 imaging microscope.',
    how:'Turn the note over. The researcher at the microscope fills the centre of the back.',
    markers:[ { side:'back', x:425, y:150, ring:30, label:'Researcher' } ],
    icon:'<circle cx="6" cy="5" r="2"/><path d="M3 14c0-4 2-6 4-6M10 3v6M9 9h4M11 9v5"/>'
  },
  {
    id:'insulin', name:'Insulin', short:'One of the earliest insulin bottles, 1923',
    color:'#9a6a2a', color2:'#d8a868',
    desc:'Based on a photograph of one of the earliest insulin bottles, dating from 1923. The discovery of insulin to treat diabetes was made by Canadian researchers Frederick Banting and Charles Best in 1921.',
    how:'Look for the small bottle labelled <b>INSULIN / INSULINE</b> to the left of the large 100 on the back.',
    markers:[ { side:'back', x:452, y:240, ring:16, label:'Insulin' } ],
    icon:'<path d="M6 2h4v3l1 2v7H5V7l1-2z"/>'
  },
  {
    id:'dna', name:'DNA strand', short:'Canadian genetic research',
    color:'#8a7a3a', color2:'#cfc07a',
    desc:'A stylized DNA strand, adapted from a computer-generated image made for the Bank of Canada by the University of Ottawa. It represents the role Canadian researchers have played in mapping our human genetic makeup; it is not meant to depict a specific DNA structure.',
    how:'Look for the faint double helix behind the microscope, running toward the frosted maple leaf.',
    markers:[ { side:'back', x:519, y:99, ring:16, label:'DNA strand' } ],
    icon:'<path d="M5 1c0 4 6 4 6 7s-6 3-6 7M11 1c0 4-6 4-6 7s6 3 6 7"/>'
  },
  {
    id:'ecg', name:'ECG', short:'A healthy heart rhythm',
    color:'#6a7a3a', color2:'#b4c47a',
    desc:'An electrocardiogram trace, drawn by the bank note designers with medical experts to show a pattern consistent with a healthy heart. It recognizes Canadian contributions to heart health, including the pacemaker.',
    how:'Follow the thin heartbeat line across the lower half of the back.',
    markers:[ { side:'back', x:48, y:225, ring:14, label:'ECG' } ],
    icon:'<path d="M1 9h4l1.5-5 2 9 1.5-4H15"/>'
  },
];

// Exploded view: the note pulled apart. The polymer film (with its clear windows) and the metallic
// images carried in the window are the core; the back is printed on one side, the front on the other.
const LAYERS = [
  { id:'r-print',    name:'Back print',        group:'Reverse', side:'back',  feature:'researcher', kind:'art' },
  { id:'r-metal',    name:'Metallic images',   group:'Polymer', side:'back',  feature:'mportrait', kind:'pieces',
    pieces:[ ['back-mportrait', 0,0,0,0], ['back-mbuilding', 0,0,0,0] ] },
  { id:'film',       name:'Polymer film',      group:'Polymer', side:'front', feature:'polymer',   kind:'film', core:true },
  { id:'metal',      name:'Metallic images',   group:'Polymer', side:'front', feature:'mbuilding', kind:'pieces',
    pieces:[ ['front-mportrait', 0,0,0,0], ['front-mbuilding', 0,0,0,0] ] },
  { id:'print',      name:'Front print',       group:'Obverse', side:'front', feature:'portrait',  kind:'art' },
  { id:'clear',      name:'Clear raised text', group:'Obverse', side:'front', feature:'transtext', kind:'pieces',
    pieces:[ ['front-canada', 0,0,0,0] ] },
  { id:'raised',     name:'Raised ink',        group:'Obverse', side:'front', feature:'raised',    kind:'pieces',
    pieces:[ ['front-100', 0,0,0,0], ['front-shoulders', 0,0,0,0], ['front-boc-fr', 0,0,0,0], ['front-boc-en', 0,0,0,0] ] },
];

const TWEAK_DEFAULS = {
  "defaultActive": ["polymer","raised","window","mportrait","mbuilding","transtext","smallnum","leafborder","frosted","hidden","portrait","researcher","insulin","dna","ecg"]
};

// Glow highlights: each feature's own cut-out (assets/layers/<src>.png) laid exactly over the artwork
// at its box [x, y, w, h] in 720x320 note space (boxes from assets/boxes.js).
const P = (side, src) => ({ side, src, box: BOXES[src], mirror:false });
const GLOW = {
  polymer:   [ P('front','front-clear'), P('back','back-clear') ],
  raised:    [ P('front','front-100'), P('front','front-shoulders'), P('front','front-boc-fr'), P('front','front-boc-en') ],
  window:    [ P('front','front-window'), P('back','back-window') ],
  mportrait: [ P('front','front-mportrait'), P('back','back-mportrait') ],
  mbuilding: [ P('front','front-mbuilding'), P('back','back-mbuilding') ],
  transtext: [ P('front','front-canada'), P('back','back-canada') ],
  smallnum:  [ P('front','front-smallnum'), P('back','back-smallnum') ],
  leafborder:[ P('front','front-leafborder'), P('back','back-leafborder') ],
  frosted:   [ P('front','front-leafwindow'), P('back','back-leafwindow') ],
  hidden:    [ P('front','front-frost') ],
  portrait:  [ P('front','front-portrait') ],
  researcher:[ P('back','back-researcher') ],
  insulin:   [ P('back','back-insulin') ],
  dna:       [ P('back','back-dna') ],
  ecg:       [ P('back','back-ecg') ],
};

// Detail callouts shown when a feature is zoomed into: [side, [[x, y], ...], label] in note units.
const DETAILS = {
  polymer:   [['front', [[500, 230]], 'Clear: the large window'], ['front', [[78, 99]], 'Clear: the leaf outline'],
              ['front', [[300, 60]], 'One piece of polymer']],
  raised:    [['front', [[80, 230]], 'Large number'], ['front', [[405, 265]], 'Shoulders'],
              ['front', [[443, 106]], 'Banque du Canada'], ['front', [[650, 235]], 'Bank of Canada']],
  window:    [['front', [[540, 60]], 'Metallic portrait'], ['front', [[511, 131]], 'Transparent “Canada”'],
              ['front', [[578, 100]], 'Small numbers'], ['front', [[540, 270]], 'Metallic building'],
              ['back', [[220, 230]], 'Clear from both sides']],
  mportrait: [['front', [[540, 60]], 'Matches the large portrait'], ['front', [[545, 120]], 'Tilt: it changes colour'],
              ['back', [[180, 60]], 'The same on the back']],
  mbuilding: [['front', [[540, 230]], 'East Block of Parliament'], ['front', [[540, 280]], 'Tilt: sharp colour changes'],
              ['back', [[180, 270]], 'The same on the back']],
  transtext: [['front', [[511, 131]], 'Transparent'], ['front', [[565, 166]], 'Feels slightly raised']],
  smallnum:  [['front', [[578, 100]], 'Numbers matching the value'], ['front', [[515, 160]], 'Some appear in reverse'],
              ['front', [[480, 180]], 'Around the window too']],
  leafborder:[['front', [[458, 40]], 'Leaves border the window'], ['front', [[490, 140]], 'Some cross into it']],
  frosted:   [['front', [[78, 99]], 'Transparent outline'], ['front', [[117, 105]], 'Frosted leaf']],
  hidden:    [['front', [[117, 105]], 'Look at a small light through here'], ['front', [[140, 125]], 'A circle of 100s appears']],
  portrait:  [['front', [[330, 95]], 'Sir Robert L. Borden'], ['front', [[405, 265]], 'Raised ink on the shoulders']],
  researcher:[['back', [[330, 120]], 'Researcher'], ['back', [[430, 110]], 'Carl Zeiss Axioplan 2 microscope']],
  insulin:   [['back', [[452, 240]], 'Insulin bottle, 1923']],
  dna:       [['back', [[519, 99]], 'Stylized DNA strand']],
  ecg:       [['back', [[48, 225]], 'Heartbeat trace'], ['back', [[329, 232]], 'Runs on across the back']],
};
