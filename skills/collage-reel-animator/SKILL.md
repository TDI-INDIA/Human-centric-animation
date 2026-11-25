---
name: "collage-reel-animator"
description: "Use when the user wants a reel, short video, or scroll-animated web page starring photo-collage cutout characters with stop-motion pose swaps, props and bold type."
---

# Collage Reel Animator

Animates characters made with `collage-character-set` (a `characters/<name>/` folder with pose WebPs, `shadow.webp`, `character.json`) in a surreal editorial collage scene: flat colored wall, floor strip, cutout props with shadows, big type, film grain. Motion is stop-motion style: characters swap poses instead of tweening smoothly.

If no character folder exists yet, run `collage-character-set` first.

## 1. Ask (one short round, skip what's known)
- Output: 9:16 reel (1080x1920, default), 1:1, 16:9, or a scroll-driven web page
- Duration (default 8-12s) and the message/script
- Which character(s), wall color, any product image to feature

## 2. Beat sheet (show it before building)
Map time to pose + text + prop. Default reel structure:
- 0-1.5s hook: character enters or is already mid-gesture, big word drops in
- 1.5-7s value: 2-4 pose changes, each tied to one short line of text
- last 2s CTA: character points at CTA text/product, holds
Hold each pose at least 0.5s. A pose change should land on a text change.

## 3. Motion vocabulary
- pose swap: change image + 3-frame squash pop (scale 1.04,0.96 then back)
- breathe: scaleY 1 -> 1.012, origin at feet, 3s cycle, always on
- blink: swap to `blink` pose for 0.12s every 3-5s
- hop: translateY up 30px and back over 0.3s; shadow shrinks to 80% at the top
- enter/exit: slide from off-frame with walk-a/walk-b alternating every 0.17s
- props: slide/drop in with a hard ease-out and a small overshoot; each prop has its own shadow
- type: letters drop in one by one on a stagger, slight rotation; photo-in-type via `background-clip:text` with a photo
- stop-motion feel: quantize character motion to 12 fps (`tq = Math.floor(t*12)/12`); text and camera can stay at 30 fps

## 4. Build the scene as one HTML file driven by time
Everything must be computed from `t` (seconds) inside `seek(t)`; no CSS animations or timers, so rendering is frame-exact. Template:

```html
<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;background:#000}
#stage{position:relative;width:1080px;height:1920px;overflow:hidden;background:#1f3fd1;font-family:system-ui,sans-serif}
#floor{position:absolute;left:0;right:0;bottom:0;height:430px;background:#d8cab4}
.char{position:absolute;bottom:330px;left:50%;transform-origin:50% 100%}
.char img.pose{display:block;height:1100px}
.char img.shadow{position:absolute;left:50%;bottom:-40px;width:75%;transform:translateX(-50%)}
.line{position:absolute;left:80px;right:80px;top:300px;color:#f4efe6;font-size:120px;font-weight:800;line-height:.95;letter-spacing:-.02em}
#grain{position:absolute;inset:0;pointer-events:none;opacity:.18;mix-blend-mode:multiply}
</style></head><body>
<div id="stage">
  <div id="floor"></div>
  <div class="char" id="c1"><img class="shadow" src="characters/mira/shadow.webp"><img class="pose" id="c1pose" src="characters/mira/idle.webp"></div>
  <div class="line" id="txt"></div>
  <svg id="grain" width="1080" height="1920"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2"/></filter><rect width="100%" height="100%" filter="url(#n)"/></svg>
</div>
<script>
const DUR = 10;
const CHAR = 'characters/mira/';
// beat sheet: [startSec, pose, text]
const BEATS = [[0,'idle','Your ads'],[1.5,'point','die in 3 days.'],[4,'surprised','We tell you why.'],[7,'hold','SellTheClick']];
// preload every pose
const cache = {}; for (const [,p] of BEATS) { cache[p] = new Image(); cache[p].src = CHAR + p + '.webp'; }
window.assetsReady = Promise.all(Object.values(cache).map(i => i.decode()));
const ease = x => 1 - Math.pow(1 - x, 3);
function seek(t) {
  const tq = Math.floor(t * 12) / 12;               // stop-motion clock
  let i = 0; while (i + 1 < BEATS.length && BEATS[i + 1][0] <= t) i++;
  const [start, pose, text] = BEATS[i];
  const since = tq - start;
  const blinking = pose === 'idle' && (tq % 4) > 3.85;
  document.getElementById('c1pose').src = CHAR + (blinking ? 'blink' : pose) + '.webp';
  const pop = since < 0.25 ? [1.04, 0.96] : [1, 1];
  const breathe = 1 + 0.012 * Math.sin(tq * Math.PI * 2 / 3);
  document.getElementById('c1').style.transform = `translateX(-50%) scale(${pop[0]}, ${pop[1] * breathe})`;
  const el = document.getElementById('txt');
  el.innerHTML = [...text].map((ch, k) => { const p = Math.min(1, Math.max(0, (t - start - k * 0.03) / 0.25)); return `<span style="display:inline-block;opacity:${p};transform:translateY(${(1 - ease(p)) * -80}px) rotate(${(1 - p) * -6}deg)">${ch === ' ' ? ' ' : ch}</span>`; }).join('');
}
window.seek = seek; window.DUR = DUR;
if (!navigator.webdriver) { const s = performance.now(); (function loop(){ seek(((performance.now() - s) / 1000) % DUR); requestAnimationFrame(loop); })(); }
</script></body></html>
```

Keep reel safe zones clear of key text: top 250px and bottom 420px (platform UI), and ~120px on the right edge.

## 5. Render to MP4
Install once: `npm i playwright && npx playwright install chromium`. Write and run:

```js
// render.js scene.html out.mp4 [fps]
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');
const [,, html, out = 'out.mp4', fpsArg = '30'] = process.argv;
const fps = +fpsArg;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.resolve(html));
  await p.evaluate(async () => { await document.fonts.ready; await window.assetsReady; });
  const dur = await p.evaluate(() => window.DUR);
  fs.rmSync('frames', { recursive: true, force: true }); fs.mkdirSync('frames');
  for (let i = 0; i < Math.round(dur * fps); i++) {
    await p.evaluate(t => window.seek(t), i / fps);
    await p.evaluate(() => Promise.all([...document.images].map(im => im.decode().catch(() => {}))));
    await p.locator('#stage').screenshot({ path: `frames/f${String(i).padStart(5, '0')}.png` });
  }
  await b.close();
  execFileSync('ffmpeg', ['-y', '-framerate', String(fps), '-i', 'frames/f%05d.png', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out], { stdio: 'inherit' });
})();
```

For audio, mux afterwards: `ffmpeg -i out.mp4 -i music.mp3 -c:v copy -shortest final.mp4`. If a voice/sound tool is connected (e.g. ElevenLabs), offer a voiceover or SFX on pose changes.

## 6. Scroll-driven web page mode
Same `seek()` scene, but drive it from scroll instead of time: `addEventListener('scroll', () => seek(DUR * scrollY / (document.body.scrollHeight - innerHeight)))` with the stage `position:sticky; top:0` inside a tall (e.g. 500vh) container, scaled to fit the viewport. Publish it as an artifact.

## 7. Check before delivering
- Extract frames at start, each beat change, and the end (`ffmpeg -ss <t> -i out.mp4 -frames:v 1 check_<t>.png`) and look at them.
- Check: character feet on the floor line, no pose size jumps, text inside safe zones and readable at phone size, no missing images, the CTA held for at least 1.5s.
- Deliver the MP4 (and the HTML scene so it can be re-edited), with one line on what to tweak next.
## Field notes (from the first production run)
- **Use `scripts/render.js`** (playwright-core + an installed Chrome via `executablePath`, JPEG frames, ffmpeg). It pads the audio with `apad` so a voiceover shorter than the video never cuts off the end card.
- **`templates/scene.html`** is a working two-character scene: beat sheet, word stamps, punch-in camera, dashboard panel, end card, grain, and a `MAP` that falls back to the closest pose when one is missing.
- **Voice, best to worst:** a real phone recording; ElevenLabs v3/v4 (needs credits); Google AI Studio "Generate speech" (free with a Google account: pick a voice, write a Style direction like "furious founder ranting, building to shouting", download the WAV); Piper offline TTS via `scripts/make_vo.py` (flat, no emotion; voices download from GitHub release v0.0.2 when HuggingFace is blocked).
- **Timing a single-take voiceover:** run ffmpeg `silencedetect=noise=-35dB:d=0.18` to find the pauses, allocate lines to the speech segments by syllable count, and snap beat starts to segment starts or RMS dips. Retime word-stamp offsets in proportion to each beat's new length.
- Keep captions in the top 250–600px and word stamps over the lower body (y 1080–1400) so they never cover faces; the bottom 420px is reserved for platform UI.
- Swearing in the VO is fine for organic posts; offer a bleeped cut for paid Meta ads.
