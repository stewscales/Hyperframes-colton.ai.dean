// Render thumbnail.html to PNG at 2x (2560x1440). Usage: node thumbnail/render.js <out.png>
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 2 });
  await page.goto('file://' + path.resolve(__dirname, 'thumbnail.html'));
  await page.evaluate(async () => { await document.fonts.ready; await document.querySelector('#person').decode(); });
  const loaded = await page.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').length);
  if (loaded < 2) throw new Error('fonts did not load');
  await (await page.$('#thumb')).screenshot({ path: process.argv[2] });
  await browser.close();
})();
