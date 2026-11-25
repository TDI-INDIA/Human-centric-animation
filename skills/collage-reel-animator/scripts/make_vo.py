# Synthesize the voiceover line by line (one line per beat) and record exact timings.
import json, wave, subprocess, pathlib
from piper import PiperVoice
from piper.config import SynthesisConfig

LINES = [
    "I don't give a damn about the explanations you give me on Wednesday morning.",
    "I didn't hire you to explain why things aren't working.",
    "Fucking C.A.C. C.T.R. Ad fatigue.",
    "Do you think I care what that shit is?",
    "Man, I need sales!",
    "My SaaS is twenty five bucks a month. I've already spent five thousand dollars on ads.",
    "Zero paid sign ups. Ten free ones.",
    "Even if we get lucky, and eight percent go paid, we make a hundred bucks.",
    "I just wanna know when we make three X our spend. Period.",
    "What are my odds of selling in seven days? Fourteen? Twenty one?",
    "Why don't you just talk to these guys? Try sell the click dot com. They cracked the code.",
]
GAP = 0.28
out = pathlib.Path('vo'); out.mkdir(exist_ok=True)
v = PiperVoice.load('/home/claude/voices/en-us-ryan-high.onnx', config_path='/home/claude/voices/en-us-ryan-high.onnx.json')
cfg = SynthesisConfig(length_scale=0.9, noise_scale=0.75, noise_w_scale=0.9)
t, timings, parts = 0.4, [], []
for i, line in enumerate(LINES):
    p = out / f'l{i:02d}.wav'
    with wave.open(str(p), 'wb') as w:
        v.synthesize_wav(line, w, syn_config=cfg)
    with wave.open(str(p)) as w:
        d = w.getnframes() / w.getframerate()
    timings.append({'t': round(t, 2), 'dur': round(d, 2)})
    parts.append((p, t))
    t += d + GAP
total = t
json.dump({'lines': timings, 'total': round(total, 2)}, open('vo/timings.json', 'w'), indent=1)
# place each line at its start time, then a little punch: lower pitch slightly, compress, EQ presence
inputs, filt = [], []
for k, (p, st) in enumerate(parts):
    inputs += ['-i', str(p)]
    filt.append(f'[{k}:a]adelay={int(st*1000)}|{int(st*1000)}[a{k}]')
mix = ''.join(f'[a{k}]' for k in range(len(parts)))
filt.append(f'{mix}amix=inputs={len(parts)}:normalize=0,'
            'asetrate=22050*0.94,aresample=44100,atempo=1/0.94,'
            'highpass=f=80,equalizer=f=3000:t=q:w=1:g=3,acompressor=threshold=-18dB:ratio=4:attack=5:release=80,'
            'loudnorm=I=-14:TP=-1.5[out]')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *inputs, '-filter_complex', ';'.join(filt), '-map', '[out]',
                '-c:a', 'libmp3lame', '-b:a', '192k', 'voiceover.mp3'], check=True)
print(json.dumps(timings), 'total', round(total, 2))
