---
name: "collage-character-set"
description: "Use when the user wants to create an original, consistent photo-collage character (or cast) with a full pose set of transparent cutouts for animation, reels, or scroll sites."
---

# Collage Character Set

Builds an original, reusable character in the surreal photo-collage style: photo-real person, flat studio light, one bold signature outfit, cut out on transparent background, posed like stop-motion. Output is a character folder that the `collage-reel-animator` skill (or any page) can animate.

## Hard rules
- Original characters only. Never imitate a real, identifiable person, a celebrity, or an existing brand/film/game character, and never copy another site's character.
- Every pose of one character must look like the SAME person in the SAME outfit. Consistency beats variety.

## 1. Ask (one short round, skip what the user already said)
- What is the character for (brand mascot, narrator, customer persona, cast of 3-5)?
- Vibe in 3 words (e.g. deadpan, editorial, playful).
- Wall/background color the character will usually stand on (outfit must contrast with it).

## 2. Write the character bible (show it to the user before generating)
For each character, fill in:
- name, role in the story, age range
- silhouette hook: one thing recognizable in shadow (bob haircut, huge coat, tiny hat)
- signature outfit: ONE bold pattern or color block (stripes, gingham, solid red suit) + one accent (red socks, yellow gloves)
- palette: 2-3 colors that contrast with the wall color
- signature prop (mug, laptop, phone, shopping bag)
- personality -> pose vocabulary (deadpan = small, stiff poses; playful = big reaches, hops)

For a cast: give each character a different silhouette hook and outfit color so they read apart at thumbnail size.

## 3. Generate the master reference
One front-facing full-body image first. Prompt template:

> Full-body photograph of [age] [person description], [hair], wearing [exact outfit, same words every time], holding [prop], standing straight facing camera, neutral deadpan expression, flat soft studio lighting, plain light-grey seamless background, entire body visible head to shoes, centered, editorial fashion photography, sharp focus, no text

Tools, in order of preference:
1. An image-generation tool connected in this session (e.g. an ElevenLabs `creative_generate_image` tool): use it directly, passing the master image as reference for later poses where supported.
2. Otherwise produce a prompt pack (markdown) for the user to run in Midjourney (`--cref <master> --cw 100`), Flux + LoRA, Nano Banana or Seedream, then ask them to upload the results.

Keep the outfit wording identical across every prompt. Same framing and camera distance every time.

## 4. Generate the pose set
Standard poses and filenames (generate at least the first 6):

| file | pose |
|---|---|
| idle | standing, arms relaxed |
| hold | holding prop at chest |
| point | pointing to the side (toward where text/product will be) |
| wave | one hand raised, waving |
| reach | arm stretched up/out, reaching |
| bow | small bow / head tilt |
| surprised | hands up, mouth open |
| walk-a, walk-b | two walking frames (alternate for a stop-motion walk) |
| blink | idle with eyes closed (swap briefly with idle for a blink) |

Prompt each pose as: master prompt with the pose sentence swapped, plus the master as character reference.

Drift check before accepting a pose: same face, same hair, same outfit pattern/colors, same shoes, same prop, full body in frame. Regenerate any pose that fails; do not 'fix' drift in animation.

## 5. Cut out and normalize
Save raw images to `raw/<character>/`. Write and run this script (needs `pip install rembg pillow --break-system-packages`):

```python
# normalize_poses.py raw_dir out_dir [height]
import sys, json, pathlib
from PIL import Image, ImageDraw, ImageFilter
from rembg import remove
src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
H = int(sys.argv[3]) if len(sys.argv) > 3 else 1200
PAD = 40
dst.mkdir(parents=True, exist_ok=True)
files = sorted(p for p in src.iterdir() if p.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp'})
cuts = {}
for f in files:
    im = Image.open(f).convert('RGBA')
    if im.getextrema()[3][0] == 255:  # no transparency yet
        im = remove(im)
    cuts[f.stem] = im.crop(im.getbbox())
# one scale for every pose, taken from idle, so the body size never jumps
ref = cuts.get('idle') or next(iter(cuts.values()))
scale = H / ref.height
poses = []
for name, im in cuts.items():
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    canvas = Image.new('RGBA', (im.width + 2 * PAD, im.height + PAD), (0, 0, 0, 0))
    canvas.paste(im, (PAD, 0), im)  # feet sit PAD px above the bottom edge
    canvas.save(dst / f'{name}.webp', 'WEBP', quality=90)
    poses.append({'name': name, 'file': f'{name}.webp', 'w': canvas.width, 'h': canvas.height})
# contact shadow
sh = Image.new('RGBA', (640, 140), (0, 0, 0, 0))
ImageDraw.Draw(sh).ellipse((40, 35, 600, 105), fill=(0, 0, 0, 120))
sh.filter(ImageFilter.GaussianBlur(20)).save(dst / 'shadow.webp', 'WEBP')
# contact sheet for review
thumbs = [Image.open(dst / p['file']) for p in poses]
th = 600
thumbs = [t.resize((round(t.width * th / t.height), th)) for t in thumbs]
sheet = Image.new('RGB', (sum(t.width for t in thumbs) + 20 * (len(thumbs) + 1), th + 80), (31, 63, 209))
x = 20
for t, p in zip(thumbs, poses):
    sheet.paste(t, (x, 20), t)
    ImageDraw.Draw(sheet).text((x, th + 40), p['name'], fill='white')
    x += t.width + 20
sheet.save(dst / 'contact-sheet.png')
json.dump({'poses': poses, 'baseline_px_from_bottom': PAD, 'height': H}, open(dst / 'poses.json', 'w'), indent=2)
print(f'{len(poses)} poses -> {dst}')
```

If a pose comes out visibly larger or smaller than idle (different camera distance), add a per-pose `scale` override in `character.json` rather than regenerating everything.

## 6. Write character.json
In `characters/<name>/`:

```json
{
  "name": "Mira",
  "role": "narrator",
  "bible": { "outfit": "...", "palette": ["#..."], "prop": "mug", "personality": "deadpan" },
  "poses": ["idle", "hold", "point", "wave", "reach", "bow", "surprised", "walk-a", "walk-b", "blink"],
  "scale": { "reach": 1.0 },
  "facing": "front",
  "best_on_walls": ["#1f3fd1", "#f2c94c"]
}
```

## 7. Check and deliver
- Open `contact-sheet.png` and look at it: consistent face/outfit, same scale, feet aligned, clean edges (no grey halo from the old background). Fix and re-run if not.
- Send the contact sheet to the user, and the zipped `characters/<name>/` folder.
- Offer the next step: animate the character with `collage-reel-animator`.
## Field notes (from the first production run)
- **Gemini web app works well for pose sets.** Generate the master first, then every pose in the SAME chat ("Create an image of the exact same man: same face, ... Change only the pose: ..."). Consistency held across 8 poses.
- **Chrome blocks multiple automatic downloads** from one site after the first. Before batch-downloading, have the user allow "multiple downloads" for gemini.google.com, or download each image by hand from its download button.
- **Use `scripts/cutout.py` instead of the inline script above** when poses share the same framing: it cuts every pose with ONE shared crop box, so feet, scale and horizontal position never jump between poses. It also paints over the Gemini sparkle watermark (bottom-right) before background removal and uses rembg's `isnet-general-use` model.
- `scripts/make_placeholders.py` makes stand-in blocks with the same filenames so the reel can be timed before the real images exist. Never ship them, and tell the user they are placeholders.
- With only one image of a character, act with movement instead of poses: flinch-hop, nervous wobble, lean-in (see the Priya code in the reel template).
