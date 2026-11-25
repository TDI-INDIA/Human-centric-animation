# Human-centric-animation

Two Claude skills that work as a pipeline for making stop-motion style reels, ads and scroll pages starring original photo-real cutout characters.

| Skill | What it does |
|---|---|
| [`collage-character-set`](skills/collage-character-set/SKILL.md) | Designs an original character (or cast), generates a consistent pose set, cuts the poses out and normalizes them into `characters/<name>/` |
| [`collage-reel-animator`](skills/collage-reel-animator/SKILL.md) | Turns those characters plus a script into a 9:16 reel (MP4) or a scroll-driven web page: beat sheet, pose swaps, word stamps, voiceover, render |

## Pipeline
```
script ─► character bible ─► master image ─► pose set (same chat / char ref)
       ─► cutout.py (shared crop, watermark-safe) ─► characters/<name>/*.webp
       ─► beat sheet + scene.html (seek(t)) ─► voiceover ─► render.js ─► reel.mp4
```

## Install
Upload each folder under `skills/` as a skill in Claude (Settings → Capabilities → Skills), or copy it into `~/.claude/skills/` for Claude Code.

Script requirements:
- `pip install rembg onnxruntime pillow`
- `npm i playwright-core`, plus Chrome or Chromium
- ffmpeg
- optional: `pip install piper-tts` for offline voice

## Example
[`examples/selltheclick-founder-rant`](examples/selltheclick-founder-rant): a 41s reel in which a furious SaaS founder rants at his ad agency, ending on a soft sell for tryselltheclick.com. It includes the scene file and the character prompt pack.

## Rules baked in
- Original characters only: no real people, celebrities, or existing brand or film characters.
- Every pose must be the same person in the same outfit. Regenerate any pose that drifts.
