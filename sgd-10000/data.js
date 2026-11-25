// Plain script (not a module) so the page also works when opened straight from disk (file://)
const FEATURES = [
  {
    id:'watermark', name:'Watermark', short:'Yusof bin Ishak ghost portrait',
    color:'#8a6a3a', color2:'#c7a878',
    desc:'A second portrait of Yusof bin Ishak formed by varying paper thickness during manufacture. Visible only when held against light; impossible to photocopy because it lives inside the substrate, not on it.',
    how:'Hold the note up to a bright source. A <b>ghost portrait of Yusof bin Ishak</b> should appear in the blank left panel.',
    markers:[
      { side:'front', x:97, y:190, ring:32, label:'Ghost portrait',
        outline:{shape:'ellipse', cx:97, cy:190, rx:70, ry:80} },
      { side:'back',  x:640, y:200, ring:32, label:'Watermark (reverse)',
        outline:{shape:'ellipse', cx:640, cy:200, rx:62, ry:74} },
    ],
    icon:'<circle cx="8" cy="8" r="5"/><path d="M3 14c1-2 3-3 5-3s4 1 5 3"/>'
  },
  {
    id:'thread', name:'Security thread', short:'Embedded windowed stripe',
    color:'#3e5ba8', color2:'#6d8bd6',
    desc:'A narrow metallic thread woven into the paper, reading "10000 SINGAPORE" in microtext. It surfaces as a broken "windowed" stripe on the reverse and reads as one continuous dark line when the obverse is held to the light — proof of depth, not just ink.',
    how:'Tilt the note side to side. The metal windows should glint, and the micro-text inside them should appear to slide up and down as you tilt.',
    markers:[
      { side:'front', x:306, y:160, ring:14, label:'Embedded (hold to light)',
        outline:{shape:'rect', x:300, y:36, w:12, h:284, rx:2} },
      { side:'back',  x:414, y:190, ring:14, label:'Windowed thread',
        outline:{shape:'rect', x:405, y:40, w:18, h:280, rx:2} },
    ],
    icon:'<path d="M8 1v14M5 3h6M5 7h6M5 11h6"/>'
  },
  {
    id:'holo', name:'Kinegram', short:'Optically variable device',
    color:'#8a5ea8', color2:'#c79ad6',
    desc:'A stamped foil patch with an octagonal motif. The Kinegram shifts between the denomination "10K" and the Singapore lion head as the note is tilted — achievable only with diffractive optics, not printing.',
    how:'Rock the note side to side. The lion head and the denomination should swap, with rainbow fringes sweeping across the foil.',
    markers:[
      { side:'front', x:270, y:79, ring:30, label:'Kinegram foil',
        outline:{shape:'rect', x:214, y:30, w:112, h:98, rx:6} },
    ],
    icon:'<rect x="3" y="2" width="10" height="12" rx="1"/><path d="M3 6h10M3 10h10"/>'
  },
  {
    id:'ovi', name:'Colour-shift ink', short:'OVI denomination',
    color:'#2f7a5a', color2:'#7ac79d',
    desc:'Optically Variable Ink on the "10000" at the lower-right of the obverse. Interference flakes shift the hue from copper to green as viewing angle changes — a flat shade is a counterfeit tell.',
    how:'Tilt the note until the <b>10000</b> at the lower-right corner changes colour. Flat shade = fake.',
    markers:[
      { side:'front', x:640, y:283, ring:22, label:'Colour-shift 10000',
        outline:{shape:'rect', x:568, y:258, w:144, h:50, rx:4} },
    ],
    icon:'<circle cx="8" cy="8" r="5"/><path d="M8 3v10M3 8h10"/>'
  },
  {
    id:'intaglio', name:'Intaglio relief', short:'Raised engraved printing',
    color:'#c43a2b', color2:'#e88a7e',
    desc:'Intaglio presses ink into valleys of an engraved plate under enormous pressure. On this note the portrait of Yusof bin Ishak, the large "10000" numerals, and the wordmark all sit physically above the paper — feel them with a fingernail.',
    how:'Run a finger across the portrait, the large <b>10000</b> and the <b>TEN THOUSAND DOLLARS</b> wordmark. They should feel textured, not flat.',
    markers:[
      { side:'front', x:538, y:158, ring:42, label:'Engraved portrait',
        outline:{shape:'ellipse', cx:538, cy:158, rx:118, ry:142} },
      { side:'front', x:306, y:154, ring:24, label:'Raised "10000"',
        outline:{shape:'rect', x:210, y:126, w:192, h:57, rx:4} },
      { side:'front', x:290, y:206, ring:20, label:'Wordmark',
        outline:{shape:'rect', x:214, y:182, w:184, h:48, rx:3} },
    ],
    icon:'<path d="M2 12h12M4 9h8M6 6h4M8 3h0"/>'
  },
  {
    id:'microprint', name:'Quadrilingual title', short:'SINGAPURA · 新加坡 · சிங்கப்பூர் · SINGAPORE',
    color:'#6b4a22', color2:'#a87a40',
    desc:'The country name runs across the top of the obverse in all four official languages: Malay, Chinese, Tamil and English. The fine rule above it and the lettering are printed at a precision that blurs under a scanner or office printer.',
    how:'Use a loupe on the title and the rule above it. The Chinese and Tamil characters should be crisp, with no broken or bleeding strokes.',
    markers:[ { side:'front', x:340, y:21, ring:16, label:'Quadrilingual title', outline:{shape:'rect', x:212, y:15, w:260, h:12, rx:1} } ],
    icon:'<path d="M2 4h12M2 8h12M2 12h8"/>'
  },
  {
    id:'latent', name:'Latent image', short:'Tilt-revealed denomination',
    color:'#7a5930', color2:'#c7a270',
    desc:'A motif engraved at an angle that only reveals itself when the note is tilted into grazing light. Created by directional etching that the eye integrates differently at each angle.',
    how:'Bring the note to eye-level and tilt it away from you. A faint <b>10K</b> should emerge inside the gold wave patch beside <b>DOLLARS</b>.',
    markers:[
      { side:'front', x:370, y:244, ring:18, label:'Latent 10K',
        outline:{shape:'rect', x:327, y:208, w:87, h:73, rx:3} },
    ],
    icon:'<path d="M1 8c2-4 5-5 7-5s5 1 7 5c-2 4-5 5-7 5s-5-1-7-5z"/><circle cx="8" cy="8" r="2"/>'
  },
  {
    id:'register', name:'See-through register', short:'Merlion emblem aligns front/back',
    color:'#6b4a22', color2:'#c7a270',
    desc:'A Merlion emblem is printed as an outline on the obverse and as a gold head on the reverse, exactly back to back. Held up to the light, the two must register into one emblem: front and back are printed in separate passes, so near-perfect alignment is very hard to fake.',
    how:'Press <b>Hold up to the light</b>. The gold Merlion from the reverse should show through and sit exactly inside the outline on the obverse.',
    markers:[
      { side:'front', x:189, y:250, ring:14, label:'Merlion outline (obverse)',
        outline:{shape:'rect', x:160, y:220, w:58, h:60, rx:4} },
      { side:'back',  x:544, y:259, ring:14, label:'Gold Merlion (reverse)',
        outline:{shape:'rect', x:513, y:220, w:62, h:82, rx:4} },
    ],
    icon:'<circle cx="8" cy="8" r="5"/><circle cx="8" cy="8" r="2"/>'
  },
  {
    id:'serial', name:'Serial numbers', short:'Two printings, ascending size',
    color:'#c43a2b', color2:'#e88a7e',
    desc:'Each note carries its serial number twice. Along the lower left it runs horizontally in black; down the right edge it runs vertically in red-brown. In both, the characters grow progressively larger as they run: small at the start, largest at the end. This ascending-size printing is hard to reproduce or alter one digit at a time. Under ultraviolet light the serials fluoresce.',
    how:'Read both serials. They must carry the same number, and in each one every character should be a little larger than the one before it. Uneven sizes, or two serials that disagree, are warning signs.',
    markers:[
      { side:'front', x:102, y:286, ring:16, label:'Horizontal serial',
        outline:{shape:'rect', x:48, y:275, w:108, h:22, rx:2} },
      { side:'front', x:678, y:139, ring:16, label:'Vertical serial',
        outline:{shape:'rect', x:668, y:64, w:20, h:150, rx:2} },
    ],
    icon:'<path d="M2 4h2v8H2zM6 4h2v8H6zM10 4h2v8h-2z"/>'
  },
  {
    id:'uv', name:'UV fluorescence', short:'Invisible inks & fibres',
    color:'#7a3ea8', color2:'#b47fd6',
    desc:'Inks and embedded paper fibres invisible under normal light but luminescent under ultraviolet. Random fibres scatter across the note in several colours; printed motifs and serials glow in patterns.',
    how:'Switch to <b>UV Light</b> on the top bar. Random fibres, glowing serials and a hidden authentication motif should appear.',
    markers:[
      { side:'front', x:270, y:79, ring:30, label:'UV motif zone',
        outline:{shape:'rect', x:214, y:30, w:112, h:98, rx:6} },
      { side:'front', x:102, y:286, ring:16, label:'UV serial',
        outline:{shape:'rect', x:48, y:275, w:108, h:22, rx:2} },
    ],
    icon:'<path d="M3 3l10 10M13 3L3 13M8 2v12"/>'
  },
  {
    id:'signature', name:"Chairman's signature", short:'Signed by the issuing authority',
    color:'#6b4a22', color2:'#c7a270',
    desc:"Every note carries the signature of whoever chaired the issuing authority when it was printed. This first-issue note, from September 1999, is signed by Dr Richard Hu Tsu Tau as Chairman of the Board of Commissioners of Currency, Singapore. Later print runs carry later signatures, so the signature helps date a note. Beside it, a red Chinese seal carries the same chairman’s name in seal script.",
    how:'Check that the signature and the title beneath it match the issuing authority for the note’s year of issue. A 1999 note should read <b>Chairman, Board of Commissioners of Currency, Singapore</b>.',
    markers:[ { side:'front', x:262, y:240, ring:16, label:'Signature', outline:{shape:'rect', x:236, y:234, w:90, h:46, rx:2} } ],
    icon:'<path d="M2 11c2-3 3-6 4-6s0 6 2 6 2-4 3-4 1 3 3 3"/>'
  },
  {
    id:'crest', name:'State crest', short:'Singapore coat of arms, top left',
    color:'#6b4a22', color2:'#c7a270',
    desc:'Singapore’s coat of arms in the top-left corner of the obverse: a shield with a crescent and five stars, held by a lion and a tiger, above the motto MAJULAH SINGAPURA (“Onward Singapore”). It is printed in raised intaglio ink, pressed into the paper so hard that its impression shows through on the reverse, mirrored, where it can be seen and felt as a blind embossing.',
    how:'Run a fingertip over the crest: the intaglio lines feel raised. Turn the note over: the same crest is pressed into the reverse, mirrored, and you can feel it there too. A flat print has no impression on the back.',
    markers:[ { side:'front', x:109, y:50, ring:18, label:'State crest', outline:{shape:'rect', x:46, y:8, w:126, h:94, rx:4} },
              { side:'back', x:620, y:54, ring:18, label:'Crest impression (reverse)', outline:{shape:'rect', x:562, y:12, w:116, h:84, rx:4} } ],
    icon:'<path d="M4 3h8v5c0 3-2 5-4 6-2-1-4-3-4-6z"/>'
  },
  {
    id:'seal', name:'Chinese seal', short:'The chairman’s name in seal script',
    color:'#a33a2b', color2:'#d77a6a',
    desc:'A traditional Chinese seal in red, printed beside the signature. Written in ancient Chinese seal script, it bears the name of the chairman of the issuing authority, the same person who signs the note, and acts as an official seal of authority. On this 1999 note that is Dr Richard Hu Tsu Tau, Chairman of the Board of Commissioners of Currency, Singapore.',
    how:'The seal should belong to the same chairman as the <b>signature</b> next to it. Under a loupe, its square border and seal-script characters should be sharp-edged, in a clean red that does not bleed into the gold around it.',
    markers:[ { side:'front', x:338, y:242, ring:12, label:'Chinese seal', outline:{shape:'rect', x:326, y:231, w:24, h:22, rx:1} } ],
    icon:'<rect x="4" y="4" width="8" height="8"/><path d="M6 6h4v4H6z"/>'
  },
  {
    id:'tactile', name:'Tactile mark', short:'Raised dots, top right',
    color:'#6b4a22', color2:'#c7a270',
    desc:'Four raised dots in the top-right corner of the obverse, printed in thick intaglio ink so they can be felt. They are a tactile mark to help identify the note by touch. They are not Braille characters.',
    how:'Run a fingertip over the top-right corner. The four dots should feel distinctly raised. On a flat print they feel like the rest of the paper.',
    markers:[ { side:'front', x:695, y:20, ring:14, label:'Tactile dots', outline:{shape:'rect', x:680, y:6, w:30, h:28, rx:2} } ],
    icon:'<circle cx="5" cy="5" r="1.6"/><circle cx="11" cy="5" r="1.6"/><circle cx="5" cy="11" r="1.6"/><circle cx="11" cy="11" r="1.6"/>'
  },
  {
    id:'cowrie', name:'Onyx cowrie', short:'Spotted shell, top right',
    color:'#8a6a3a', color2:'#c7a878',
    desc:'Every Portrait Series note carries a cowrie shell in its background print, a different one for each denomination. On the S$10,000 it is the Onyx Cowrie: the spotted oval shell in the top right, drawn in fine lines and rings and running behind the portrait’s hair.',
    how:'Look at the top right, beside the tactile dots. The shell’s spots and rings are built from many fine, evenly spaced lines. On a copy they merge into flat tone.',
    markers:[ { side:'front', x:630, y:45, ring:24, label:'Onyx cowrie', outline:{shape:'rect', x:568, y:0, w:108, h:110, rx:4} } ],
    icon:'<path d="M8 2c3 0 5 3 5 6s-2 6-5 6-5-3-5-6 2-6 5-6zM8 4v8"/>'
  },
  {
    id:'fineline', name:'Guilloche portrait', short:'Yusof bin Ishak, drawn entirely in lines',
    color:'#8a4a3a', color2:'#c7886a',
    desc:'The portrait of Yusof bin Ishak, Singapore’s first president, is engraved entirely in fine lines: there is no continuous tone anywhere in it. Every shade of his face, hair and coat is built from line spacing, line thickness and cross-hatching, with lines of 30–60 microns that follow the contours of the face. The same precision runs through the guilloche rosettes, the border lattices and the molecular structure on the reverse. A scanner or office printer turns this line-work into dots and grey smears.',
    how:'Use a <b>10× loupe</b> on the portrait’s cheek and eyes. Each engraved line should be crisp and separate, swelling and thinning to make the shading. Dots, blur or flat tone means a printed reproduction. Check the molecular structure on the reverse the same way.',
    markers:[
      { side:'back',  x:236, y:130, ring:38, label:'Molecular fine-line',
        outline:{shape:'rect', x:70, y:92, w:332, h:76, rx:6} },
      { side:'front', x:538, y:158, ring:42, label:'Portrait line-work',
        outline:{shape:'ellipse', cx:538, cy:158, rx:118, ry:142} },
    ],
    icon:'<circle cx="8" cy="8" r="5" fill="none"/><circle cx="8" cy="8" r="3" fill="none"/><circle cx="8" cy="8" r="1" fill="none"/>'
  },
];

// Exploded view: the note pulled apart in both directions. The paper (with the
// watermark and thread formed inside it) is the core; the reverse is printed on one
// side of it and the obverse on the other. Listed from the reverse surface to the
// obverse surface. Each piece is a cut-out made by tools/extract_features.py, placed at
// its crop box [x, y, w, h] in 720x320 note space of its own side.
const LAYERS = [
  { id:'r-serial',   name:'Serial numbers',   group:'Reverse', side:'back',  feature:'serial',    kind:'pieces',
    pieces:[ ['back-serial', 576,273,130,28] ] },
  { id:'r-intaglio', name:'Intaglio ink',     group:'Reverse', side:'back',  feature:'intaglio',  kind:'pieces',
    pieces:[ ['back-intaglio-10000', 24,10,222,78], ['back-small-10000-cut', 374,226,132,45], ['back-lion-head', 509,216,70,90] ] },
  { id:'r-offset',   name:'Offset print',     group:'Reverse', side:'back',  feature:'fineline',  kind:'art' },
  { id:'thread',     name:'Security thread',  group:'Paper',   side:'front', feature:'thread',    kind:'pieces',
    pieces:[ ['back-thread', 293,36,26,284, 'mirror'] ] },
  { id:'substrate',  name:'Cotton substrate', group:'Paper',   side:'front', feature:null,        kind:'paper', core:true },
  { id:'watermark',  name:'Watermark',        group:'Paper',   side:'front', feature:'watermark', kind:'pieces',
    pieces:[ ['watermark-ghost', 23,106,148,168] ] },
  { id:'offset',     name:'Offset print',     group:'Obverse', side:'front', feature:'fineline',  kind:'art' },
  { id:'intaglio',   name:'Intaglio ink',     group:'Obverse', side:'front', feature:'intaglio',  kind:'pieces',
    pieces:[ ['front-portrait-cut', 405,4,261,306],          // hand-cleaned (assets/overrides) ['front-intaglio-10000', 206,122,200,65],
             ['front-wordmark', 210,178,192,56], ['front-coat-of-arms', 42,4,134,102],
             ['front-tactile-dots', 676,2,38,36] ] },
  { id:'latent',     name:'Latent image',     group:'Obverse', side:'front', feature:'latent',    kind:'pieces',
    pieces:[ ['front-latent-patch-cut', 323,204,95,81] ] },   // hand-cleaned
  { id:'seal',       name:'Chinese seal',     group:'Obverse', side:'front', feature:'seal',      kind:'pieces',
    pieces:[ ['front-seal-cut', 322,227,32,30] ] },        // hand-cleaned
  { id:'ovi',        name:'Colour-shift ink', group:'Obverse', side:'front', feature:'ovi',       kind:'pieces',
    pieces:[ ['front-ovi-10000', 564,254,152,58] ] },
  { id:'serial',     name:'Serial numbers',   group:'Obverse', side:'front', feature:'serial',    kind:'pieces',
    pieces:[ ['front-serial-horizontal', 44,271,116,30], ['front-serial-vertical', 664,60,28,158] ] },
  { id:'foil',       name:'Kinegram foil',    group:'Obverse', side:'front', feature:'holo',      kind:'pieces',
    pieces:[ ['front-kinegram', 217,30,102,92] ] },
  { id:'uv',         name:'UV fluorescence',  group:'Obverse', side:'front', feature:'uv',        kind:'uv' },
];

const TWEAK_DEFAULS = {
  "defaultActive": [
    "watermark",
    "thread",
    "holo",
    "ovi",
    "intaglio",
    "microprint",
    "latent",
    "register",
    "serial",
    "uv",
    "fineline",
    "signature",
    "tactile",
    "seal",
    "crest",
    "cowrie"
  ]
};


// Glow highlights: each feature's own cut-out (assets/layers/<src>.png) laid exactly
// over the artwork at its box [x, y, w, h] in 720x320 note space. On hover/selection
// the piece lights up in its own shape — no boxes or rings.
// the reverse gold Merlion, mirrored and fitted to the front outline: what shows through when held to light
const REGISTER_GHOST = { box: [164.2, 223.1, 50.7, 55.3] };
// boxes come from assets/boxes.js (written with the crops), so a highlight always sits on its print
const P = (side, src, x, y, w, h, mirror) => ({ side, src, box: (!mirror && !src.endsWith('.svg') && typeof BOXES !== 'undefined' && BOXES[src]) || [x, y, w, h], mirror:!!mirror });
const GLOW = {
  watermark: [ P('front','watermark-ghost',23,106,148,168), P('back','watermark-ghost',549,106,148,168,true) ],
  thread:    [ P('back','back-thread',401,36,26,284) ],          // obverse: the embedded line, built in script.js
  holo:      [ P('front','front-kinegram',217,30,102,92) ],
  ovi:       [ P('front','front-ovi-10000',564,254,152,58) ],
  intaglio:  [ P('front','front-portrait',416,6,250,304), P('front','front-intaglio-10000',206,122,200,65),
               P('front','front-wordmark',210,178,192,56) ],
  microprint:[ P('front','front-microprint',208,11,268,20) ],
  tactile:   [ P('front','front-tactile-dots',676,2,38,36) ],
  seal:      [ P('front','front-seal',322,227,32,30) ],
  // the reverse shows the obverse crest's impression, mirrored: so it glows as the same crest, mirrored
  crest:     [ P('front','front-coat-of-arms',42,4,134,102), P('back','front-coat-of-arms',553,3,134,102,true) ],
  cowrie:    [ P('front','front-cowrie-lines',562,0,118,114) ],   // its own line-work (tools/cowrie_lines.py)
  latent:    [ P('front','front-latent-patch',323,204,95,81) ],
  register:  [ P('front','front-lion-head-outline',160.2,219.1,58.7,63.3), P('back','back-lion-head',513,217.9,63.7,70.4) ],
  signature: [ P('front','front-signature',232,230,98,54) ],
  serial:    [ P('front','front-serial-horizontal',44,271,116,30), P('front','front-serial-vertical',664,60,28,158),
               P('back','back-serial',576,273,130,28) ],
  uv:        [ P('front','front-kinegram',217,30,102,92), P('front','front-serial-horizontal',44,271,116,30) ],
  fineline:  [ P('back','back-molecular',66,88,340,84), P('front','front-portrait',416,6,250,304) ],
};


// Detail callouts shown when a feature is zoomed into: [side, [[x, y], ...], label] in note units.
const DETAILS = {
  serial:    [['front', [[46, 284]], 'Prefix letters'], ['front', [[132, 286]], 'Characters grow larger, left to right'],
              ['front', [[676, 72]], 'Vertical serial, top: smallest'], ['front', [[676, 198]], 'Red-brown, largest at the bottom'],
              ['back', [[640, 286]], 'Serial on the reverse']],
  ovi:       [['front', [[582, 283]], 'Copper, seen face-on'], ['front', [[700, 283]], 'Turns green as the note tilts'],
              ['front', [[640, 303]], 'Base: ordinary ink, does not shift']],
  holo:      [['front', [[268, 36]], 'Octagonal foil, hot-stamped on'], ['front', [[268, 79]], 'Lion head ↔ 10K as you rock it'],
              ['front', [[305, 108]], 'Rainbow fringes: diffraction, not ink']],
  watermark: [['front', [[97, 150]], 'Head formed by paper thickness'], ['front', [[97, 240]], 'Visible only against the light'],
              ['back', [[623, 190]], 'Same watermark, mirrored, from the reverse']],
  intaglio:  [['front', [[520, 80]], 'Portrait: engraved, raised ink'], ['front', [[300, 150]], 'Raised 10000'],
              ['front', [[290, 206]], 'Raised TEN THOUSAND DOLLARS']],
  microprint:[['front', [[236, 21]], 'Malay: SINGAPURA'], ['front', [[281, 21]], 'Chinese: 新加坡'],
              ['front', [[337, 21]], 'Tamil: சிங்கப்பூர்'], ['front', [[421, 21]], 'English: SINGAPORE'],
              ['front', [[340, 8]], 'Fine rule above the title']],
  latent:    [['front', [[372, 236]], 'Hidden 10K in the wave lines'], ['front', [[400, 272]], 'Gold patch, seen at a grazing angle']],
  register:  [['front', [[180, 232]], 'Outline on the obverse'], ['front', [[195, 262]], 'Gold fill from the reverse shows through'],
              ['back', [[544, 259]], 'Gold fill on the reverse']],
  signature: [['front', [[262, 240]], 'Signature'], ['front', [[262, 262]], 'Chairman, Board of Commissioners of Currency']],
  seal:      [['front', [[338, 242]], 'Chairman’s name in seal script']],
  crest:     [['front', [[109, 48]], 'Shield: crescent and five stars'], ['front', [[66, 42]], 'Lion'],
              ['front', [[152, 42]], 'Tiger'], ['front', [[109, 93]], 'Motto: MAJULAH SINGAPURA'],
              ['back', [[620, 54]], 'Mirrored impression, felt on the reverse']],
  tactile:   [['front', [[688, 13], [702, 13], [688, 26], [702, 26]], 'Four raised dots']],
  cowrie:    [['front', [[632, 40]], 'Spots in fine line'], ['front', [[610, 14]], 'Rings of wavy line'],
              ['front', [[670, 40]], 'Oval shell edge'], ['front', [[600, 34]], 'Runs behind the portrait']],
  thread:    [['back', [[414, 56]], 'Metal window'], ['back', [[414, 150]], 'Microtext: 10000 SINGAPORE'],
              ['back', [[414, 250]], 'Embedded between the windows']],
  fineline:  [['front', [[505, 150]], 'Shading from line spacing only'], ['front', [[565, 100]], 'Lines follow the face'],
              ['front', [[470, 40]], 'Hair: parallel engraved lines'], ['back', [[236, 130]], 'Molecular structure in fine line']],
  uv:        [['front', [[102, 286]], 'Serial fluoresces'], ['front', [[270, 79]], 'Hidden motif in the foil area']],
};
