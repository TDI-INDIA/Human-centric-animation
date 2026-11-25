# Stand-in cutouts (same filenames/sizes as the real ones) so the reel can be timed and rendered now.
import pathlib
from PIL import Image, ImageDraw, ImageFont

FONT = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Bold.otf', 44)
CAST = {
    'gary': dict(h=1200, w=520, top=(37, 84, 199), legs=(196, 178, 140), skin=(222, 184, 150),
                 poses=['idle', 'point', 'shout', 'facepalm', 'hold', 'shrug', 'count', 'blink']),
    'priya': dict(h=1120, w=460, top=(236, 226, 205), legs=(25, 25, 25), skin=(176, 128, 96),
                  poses=['idle', 'nervous', 'show', 'smile', 'blink']),
}
for name, c in CAST.items():
    out = pathlib.Path('characters') / name
    out.mkdir(parents=True, exist_ok=True)
    for pose in c['poses']:
        W, H, PAD = c['w'], c['h'], 40
        im = Image.new('RGBA', (W, H + PAD), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        cx = W // 2
        d.ellipse((cx - 85, 10, cx + 85, 200), fill=c['skin'])                      # head
        d.rounded_rectangle((cx - 170, 210, cx + 170, 700), 60, fill=c['top'])      # torso
        d.rectangle((cx - 140, 690, cx - 15, H - 40), fill=c['legs'])               # legs
        d.rectangle((cx + 15, 690, cx + 140, H - 40), fill=c['legs'])
        d.rounded_rectangle((cx - 160, H - 50, cx - 5, H), 20, fill=(245, 245, 245))  # shoes
        d.rounded_rectangle((cx + 5, H - 50, cx + 160, H), 20, fill=(245, 245, 245))
        arm = c['top']
        if pose in ('shout', 'show', 'count'):
            d.line((cx - 160, 260, cx - 240, 40), fill=arm, width=60)
            d.line((cx + 160, 260, cx + 240, 40), fill=arm, width=60)
        elif pose == 'point':
            d.line((cx + 160, 280, W - 5, 200), fill=arm, width=60)
        elif pose == 'facepalm':
            d.line((cx + 150, 300, cx + 20, 120), fill=arm, width=60)
        label = f'{name}\n{pose}\n(placeholder)'
        d.multiline_text((cx, 440), label, font=FONT, fill=(255, 255, 255) if name == 'gary' else (40, 40, 40),
                         anchor='mm', align='center')
        im.save(out / f'{pose}.webp', 'WEBP', quality=90)
    sh = Image.new('RGBA', (640, 140), (0, 0, 0, 0))
    from PIL import ImageFilter
    ImageDraw.Draw(sh).ellipse((40, 35, 600, 105), fill=(0, 0, 0, 120))
    sh.filter(ImageFilter.GaussianBlur(20)).save(out / 'shadow.webp', 'WEBP')
print('placeholders done')
