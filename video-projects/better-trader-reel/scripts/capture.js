// Capture the caption layer of index.html as transparent 1080x1920 PNGs.  node scripts/capture.js <outDir>  -> f00000.png ... + map.json
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const outDir = process.argv[2], scene = JSON.parse(fs.readFileSync('scene.json')), comp = scene.comp;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve('index.html'), { waitUntil: 'domcontentloaded' });
  await page.evaluate(async () => { document.querySelectorAll('video, audio').forEach(e => e.remove()); document.body.classList.add('capture');
    for (const w of [800, 900]) await document.fonts.load(w + ' 50px Montserrat'); await document.fonts.ready; });
  await page.waitForTimeout(300);
  const { nf, changed } = await page.evaluate((comp) => {
    const tl = window.__timelines[comp], nf = Math.round(tl.duration() * 30), eps = 1e-6;
    const changed = new Uint8Array(nf);
    for (const k of tl.getChildren(true, true, true)) { const s = k.startTime(), e = s + k.totalDuration();
      for (let f = Math.max(0, Math.ceil((s - eps) * 30)); f <= Math.min(nf - 1, Math.floor((e + eps) * 30) + 1); f++) changed[f] = 1; }
    changed[0] = 1; return { nf, changed: Array.from(changed) };
  }, comp);
  if (nf !== scene.frames) throw new Error(`timeline is ${nf} frames, scene is ${scene.frames}`);
  fs.mkdirSync(outDir, { recursive: true });
  const frames = changed.map((c, f) => c ? f : -1).filter(f => f >= 0);
  for (const f of frames) {
    await page.evaluate(([comp, t]) => { window.__timelines[comp].time(t, false); }, [comp, f / 30 + 1e-4]);
    await page.screenshot({ path: path.join(outDir, `f${String(f).padStart(5, '0')}.png`), omitBackground: true });
  }
  const map = []; let last = -1; for (let f = 0; f < nf; f++) { if (changed[f]) last = f; map.push(last); }
  fs.writeFileSync(path.join(outDir, 'map.json'), JSON.stringify({ map })); console.log(`frames ${nf}, captured ${frames.length}`); await browser.close();
})();
