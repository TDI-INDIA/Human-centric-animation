// node render.js scene.html out.mp4 [fps] [audio.mp3]
const { chromium } = require('playwright-core');
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');
const [,, html = 'scene.html', out = 'out.mp4', fpsArg = '30', audio] = process.argv;
const fps = +fpsArg;
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.resolve(html));
  await p.evaluate(async () => { await document.fonts.ready; await window.assetsReady; });
  const dur = await p.evaluate(() => window.DUR);
  fs.rmSync('frames', { recursive: true, force: true }); fs.mkdirSync('frames');
  const n = Math.round(dur * fps);
  for (let i = 0; i < n; i++) {
    await p.evaluate(t => window.seek(t), i / fps);
    await p.evaluate(() => Promise.all([...document.images].map(im => im.decode().catch(() => {}))));
    await p.locator('#stage').screenshot({ path: `frames/f${String(i).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 92 });
    if (i % 150 === 0) console.log(`frame ${i}/${n}`);
  }
  await b.close();
  const args = ['-y', '-framerate', String(fps), '-i', 'frames/f%05d.jpg'];
  if (audio && fs.existsSync(audio)) args.push('-i', audio, '-af', 'apad', '-c:a', 'aac', '-b:a', '192k', '-shortest');
  args.push('-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out);
  execFileSync('ffmpeg', args, { stdio: ['ignore', 'ignore', 'inherit'] });
  console.log('wrote', out);
})();
