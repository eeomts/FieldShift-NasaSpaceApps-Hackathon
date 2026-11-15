// node render.js <index.html> <out.mp4> <music.wav> [fps] [onlyTimes...]
const puppeteer = require("puppeteer-core");
const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

const [, , html, out, music, fpsArg, ...stills] = process.argv;
const FPS = +(fpsArg || 24), D = 30;

(async () => {
  const browser = await puppeteer.launch({ executablePath: "/usr/bin/chromium", headless: true, args: ["--no-sandbox", "--hide-scrollbars", "--font-render-hinting=none"] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  await page.goto("file://" + path.resolve(html) + "?capture=1", { waitUntil: "networkidle0" });
  await page.evaluate(() => window.ready);
  await new Promise(r => setTimeout(r, 400));

  if (stills.length) {
    for (const s of stills) {
      await page.evaluate(t => window.renderAt(t), +s);
      await page.screenshot({ path: `${out}-${s}.png`, type: "png" });
    }
    await browser.close(); return;
  }

  const ff = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(FPS), "-i", "-",
    "-i", music, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "18",
    "-c:a", "aac", "-b:a", "192k", "-t", String(D), "-movflags", "+faststart", out], { stdio: ["pipe", "inherit", "inherit"] });
  const total = FPS * D;
  for (let i = 0; i < total; i++) {
    await page.evaluate(t => window.renderAt(t), i / FPS);
    const buf = await page.screenshot({ type: "jpeg", quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
    if (i % 48 === 0) process.stdout.write(`frame ${i}/${total}\n`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on("close", r));
  await browser.close();
  console.log("done", out);
})();
