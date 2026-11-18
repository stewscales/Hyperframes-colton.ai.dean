// Capture the graphics layer of index.html as transparent PNGs.
//   node scripts/capture.js all <outDir> [scale=2]         every frame whose picture differs from the one before it
//   node scripts/capture.js <f1,f2,...> <outDir> [scale=1]  just these frames (for checking)
// With "all" it also writes <outDir>/map.json: for each video frame, which captured frame to show (-1 = none).
// A frame is re-captured only when a tween is running on it, so held graphics cost one PNG.
// The workspace's own node_modules has a different Playwright than the installed browser, so prefer PLAYWRIGHT_PATH when set.
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const [mode, outDir, scaleArg] = process.argv.slice(2);
  const all = mode === 'all', scale = Number(scaleArg || (all ? 2 : 1));
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: scale });
  // don't wait for the proxy video: only the graphics are captured
  await page.goto('file://' + path.resolve('index.html'), { waitUntil: 'domcontentloaded' });
  await page.evaluate(async () => { document.querySelectorAll('video, audio').forEach(e => e.remove()); document.body.classList.add('capture'); await document.fonts.ready; });
  await page.waitForTimeout(300);
  const fonts = await page.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').length);
  if (fonts < 4) throw new Error('fonts did not load: ' + fonts);
  const { nf, changed } = await page.evaluate(() => {
    const tl = window.__timelines['trader-to-coach'], nf = Math.round(tl.duration() * 30), eps = 1e-6;
    const iv = tl.getChildren(true, true, true).map(k => [k.startTime(), k.startTime() + k.totalDuration()]);
    const changed = new Uint8Array(nf);
    for (const [s, e] of iv) {
      const a = Math.max(0, Math.ceil((s - eps) * 30)), b = Math.min(nf - 1, Math.floor((e + eps) * 30) + 1);
      for (let f = a; f <= b; f++) changed[f] = 1;
    }
    changed[0] = 1;
    return { nf, changed: Array.from(changed) };
  });
  const frames = all ? changed.map((c, f) => c ? f : -1).filter(f => f >= 0) : mode.split(',').map(Number);
  const t0 = Date.now();
  for (let i = 0; i < frames.length; i++) {
    const f = frames[i];
    await page.evaluate(t => { window.__timelines['trader-to-coach'].time(t, false); }, f / 30 + 1e-4);   // return nothing: the timeline itself cannot be serialised
    await page.screenshot({ path: path.join(outDir, `f${String(f).padStart(5, '0')}.png`), omitBackground: true });
    if (all && i % 250 === 0) console.log(`captured ${i}/${frames.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  }
  if (all) {
    const map = []; let last = -1;
    for (let f = 0; f < nf; f++) { if (changed[f]) last = f; map.push(last); }
    fs.writeFileSync(path.join(outDir, 'map.json'), JSON.stringify(map));
  }
  console.log(`frames ${nf}, animated ${changed.reduce((a, b) => a + b, 0)}, captured ${frames.length} in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  await browser.close();
})();
