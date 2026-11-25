# Cut out same-framing poses with ONE shared crop box so feet/scale never jump between poses.
import sys, pathlib
from PIL import Image, ImageDraw, ImageFilter
from rembg import remove, new_session

src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
H = int(sys.argv[3]) if len(sys.argv) > 3 else 1400
dst.mkdir(parents=True, exist_ok=True)
sess = new_session('isnet-general-use')
cuts = {}
for f in sorted(src.glob('*.png')):
    im = Image.open(f).convert('RGB')
    w, h = im.size
    # paint over the Gemini sparkle watermark (bottom-right) with backdrop grey
    ImageDraw.Draw(im).rectangle((int(w * .86), int(h * .88), w, h), fill=im.getpixel((int(w * .8), int(h * .95))))
    cut = remove(im, session=sess, post_process_mask=True)
    # drop faint alpha noise
    a = cut.getchannel('A').point(lambda v: 0 if v < 40 else v)
    cut.putalpha(a)
    cuts[f.stem] = cut
    print(f.stem, cut.getbbox())
boxes = [c.getbbox() for c in cuts.values()]
union = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
pad = 20
union = (max(0, union[0] - pad), max(0, union[1] - pad), union[2] + pad, union[3])
scale = H / (union[3] - union[1])
for name, c in cuts.items():
    c = c.crop(union)
    c = c.resize((round(c.width * scale), H), Image.LANCZOS)
    c.save(dst / f'{name}.webp', 'WEBP', quality=92)
print('size', c.size)
sh = Image.new('RGBA', (640, 140), (0, 0, 0, 0))
ImageDraw.Draw(sh).ellipse((40, 35, 600, 105), fill=(0, 0, 0, 120))
sh.filter(ImageFilter.GaussianBlur(20)).save(dst / 'shadow.webp', 'WEBP')
