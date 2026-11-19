// Capture the two graphic layers of a stacked short (clips/<id>/index.html) as transparent 1080x1920 PNGs.
//   node scripts/stack/capture.js <clip id> <outDir>
// Writes <outDir>/behind/f00000.png ..., <outDir>/front/f00000.png ... and <outDir>/map.json (captured frame to show per video frame).
// A frame is re-captured only when a tween is running on it. Prefer PLAYWRIGHT_PATH (the workspace's own Playwright mismatches the installed browser).
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const [id, outDir] = process.argv.slice(2), comp = 't2c-short-' + id;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve('clips', id, 'index.html'), { waitUntil: 'domcontentloaded' });
  await page.evaluate(async () => { document.querySelectorAll('video, audio').forEach(e => e.remove()); document.body.classList.add('capture');
    for (const w of [600, 700, 800, 900]) await document.fonts.load(w + ' 50px Montserrat'); await document.fonts.ready; });
  await page.waitForTimeout(300);
  if (await page.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').length) < 1) throw new Error('caption font did not load');
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
  for (const pass of ['behind', 'front']) {
    fs.mkdirSync(path.join(outDir, pass), { recursive: true });
    await page.evaluate((p) => { document.body.classList.remove('pass-behind', 'pass-front'); document.body.classList.add('pass-' + p); }, pass);
    for (const f of frames) {
      await page.evaluate(([comp, t]) => { window.__timelines[comp].time(t, false); }, [comp, f / 30 + 1e-4]);   // return nothing: the timeline itself cannot be serialised
      await page.screenshot({ path: path.join(outDir, pass, `f${String(f).padStart(5, '0')}.png`), omitBackground: true });
    }
  }
  const map = []; let last = -1;
  for (let f = 0; f < nf; f++) { if (changed[f]) last = f; map.push(last); }
  fs.writeFileSync(path.join(outDir, 'map.json'), JSON.stringify({ map }));
  console.log(`${id}: frames ${nf}, captured ${frames.length} per layer`);
  await browser.close();
})();
