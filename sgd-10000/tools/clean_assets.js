// Deletes generated layer images the page does not reference (run at the end of every extraction).
// Never touches assets/overrides/. Usage: node tools/clean_assets.js
const fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..');
const read = f => fs.readFileSync(path.join(root, f), 'utf8');
global.BOXES = {};
eval(read('data.js') + ';global.G = GLOW; global.L = LAYERS;');
const script = read('script.js');
const text = new Set(eval(script.match(/const TEXT_GLOW = new Set\((\[[^\]]*\])\)/)[1]));
const used = new Set();
for (const ps of Object.values(G)) for (const p of ps) used.add(p.src.endsWith('.svg') ? p.src : text.has(p.src) ? p.src + '.png' : p.src + '-cut.png');
for (const l of L) for (const pc of (l.pieces || [])) used.add(pc[0] + '.png');
for (const src of [script, read('index.html')]) for (const m of src.matchAll(/assets\/layers\/([\w-]+\.png)/g)) used.add(m[1]);
// also kept: sources the build tools read (tools/build_partial.py reuses the reverse 10000)
['back-intaglio-10000-cut.png'].forEach(f => used.add(f));
const dir = path.join(root, 'assets', 'layers');
const removed = fs.readdirSync(dir).filter(f => !used.has(f));
removed.forEach(f => fs.unlinkSync(path.join(dir, f)));
console.log(`clean_assets: kept ${used.size}, removed ${removed.length}${removed.length ? ': ' + removed.join(' ') : ''}`);
