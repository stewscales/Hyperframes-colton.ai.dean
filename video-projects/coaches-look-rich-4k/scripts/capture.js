// Capture the caption layer of index.html as transparent 2160x3840 PNGs (the page is authored at 1080x1920 and captured at 2x).
//   node scripts/capture.js <outDir>      -> <outDir>/f00000.png ... and <outDir>/map.json (captured frame to show on each video frame)
// A frame is re-captured only while a tween is running. Prefer PLAYWRIGHT_PATH (the workspace's own Playwright mismatches the installed browser).
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const outDir = process.argv[2], scene = JSON.parse(fs.readFileSync('scene.json')), comp = scene.comp;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 2 });
  await page.goto('file://' + path.resolve('index.html'), { waitUntil: 'domcontentloaded' });
  await page.evaluate(async () => { document.querySelectorAll('video, audio').forEach(e => e.remove()); document.body.classList.add('capture');
    for (const w of [700, 800]) await document.fonts.load(w + ' 50px Montserrat'); await document.fonts.ready; });
  await page.waitForTimeout(300);
  if (await page.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').length) < 1) throw new Error('caption font did not load');
  const { nf, changed } = await page.evaluate((comp) => {
    const tl = window.__timelines[comp], nf = Math.round(tl.duration() * 30), eps = 1e-6;
    const iv = tl.getChildren(true, true, true).map(k => [k.startTime(), k.startTime() + k.totalDuration()]);
    const changed = new Uint8Array(nf);
    for (const [s, e] of iv) { const a = Math.max(0, Math.ceil((s - eps) * 30)), b = Math.min(nf - 1, Math.floor((e + eps) * 30) + 1); for (let f = a; f <= b; f++) changed[f] = 1; }
    changed[0] = 1;
    return { nf, changed: Array.from(changed) };
  }, comp);
  if (nf !== scene.frames) throw new Error(`timeline is ${nf} frames, scene is ${scene.frames}`);
  fs.mkdirSync(outDir, { recursive: true });
  const frames = changed.map((c, f) => c ? f : -1).filter(f => f >= 0);
  for (const f of frames) {
    await page.evaluate(([comp, t]) => { window.__timelines[comp].time(t, false); }, [comp, f / 30 + 1e-4]);
    await page.screenshot({ path: path.join(outDir, `f${String(f).padStart(5, '0')}.png`), omitBackground: true });
  }
  const map = []; let last = -1;
  for (let f = 0; f < nf; f++) { if (changed[f]) last = f; map.push(last); }
  fs.writeFileSync(path.join(outDir, 'map.json'), JSON.stringify({ map }));
  console.log(`frames ${nf}, captured ${frames.length}`);
  await browser.close();
})();
