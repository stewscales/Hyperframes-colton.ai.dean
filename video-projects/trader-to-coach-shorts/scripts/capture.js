// Capture the caption layer of one clip (clips/<id>/index.html) as transparent PNGs of the caption band at 2x (4K).
//   node scripts/capture.js <clip id> <outDir>            every frame whose picture differs from the one before it
// Writes <outDir>/f00000.png ... and <outDir>/map.json = { band: [y0, y1] (4K rows), map: [captured frame to show per video frame] }.
// A frame is re-captured only when a tween is running on it, so a held caption costs one PNG.
// The workspace's own node_modules has a different Playwright than the installed browser, so prefer PLAYWRIGHT_PATH when set.
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const [id, outDir] = process.argv.slice(2), comp = 't2c-short-' + id, Y0 = 600, Y1 = 1080;
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2 });
  await page.goto('file://' + path.resolve('clips', id, 'index.html'), { waitUntil: 'domcontentloaded' });
  await page.evaluate(async () => { document.querySelectorAll('video, audio').forEach(e => e.remove()); document.body.classList.add('capture'); await document.fonts.load("800 76px Montserrat"); await document.fonts.load("900 106px Montserrat"); await document.fonts.ready; });
  await page.waitForTimeout(300);
  const fonts = await page.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').length);
  if (fonts < 1) throw new Error('caption font did not load');
  const { nf, changed } = await page.evaluate((comp) => {
    const tl = window.__timelines[comp], nf = Math.round(tl.duration() * 30), eps = 1e-6;
    const iv = tl.getChildren(true, true, true).map(k => [k.startTime(), k.startTime() + k.totalDuration()]);
    const changed = new Uint8Array(nf);
    for (const [s, e] of iv) {
      const a = Math.max(0, Math.ceil((s - eps) * 30)), b = Math.min(nf - 1, Math.floor((e + eps) * 30) + 1);
      for (let f = a; f <= b; f++) changed[f] = 1;
    }
    changed[0] = 1;
    return { nf, changed: Array.from(changed) };
  }, comp);
  const frames = changed.map((c, f) => c ? f : -1).filter(f => f >= 0);
  for (const f of frames) {
    await page.evaluate(([comp, t]) => { window.__timelines[comp].time(t, false); }, [comp, f / 30 + 1e-4]);   // return nothing: the timeline itself cannot be serialised
    await page.screenshot({ path: path.join(outDir, `f${String(f).padStart(5, '0')}.png`), omitBackground: true, clip: { x: 0, y: Y0, width: 1920, height: Y1 - Y0 } });
  }
  const map = []; let last = -1;
  for (let f = 0; f < nf; f++) { if (changed[f]) last = f; map.push(last); }
  fs.writeFileSync(path.join(outDir, 'map.json'), JSON.stringify({ band: [Y0 * 2, Y1 * 2], map }));
  console.log(`${id}: frames ${nf}, captured ${frames.length}`);
  await browser.close();
})();
