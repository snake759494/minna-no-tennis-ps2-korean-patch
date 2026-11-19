"""contact.py <out_prefix> <glob...> : tm2 들을 원본 크기로 모아 시트 생성 (각 이미지 위에 파일명)"""
import sys, os, glob
sys.path.insert(0, os.path.dirname(__file__)); import tim2
from PIL import Image, ImageDraw
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = sys.argv[1]; fs = []
for g in sys.argv[2:]: fs += sorted(glob.glob(os.path.join(R, 'work', 'xb', g)))
items = []
for f in fs:
    try: P = tim2.read(open(f, 'rb').read())
    except Exception: continue
    for i, p in enumerate(P):
        im = Image.new('RGBA', (p['w'], p['h']), (60, 60, 110, 255)); im.alpha_composite(Image.fromarray(p['rgba']))
        if im.width > 512: im = im.resize((im.width // 2, im.height // 2))
        items.append(('%s#%d %dx%d' % (os.path.basename(f), i, p['w'], p['h']), im.convert('RGB')))
W = 1024; x = y = h = 0; pos = []
for n, im in items:
    if x + im.width > W: x = 0; y += h + 14; h = 0
    pos.append((x, y)); x += im.width + 4; h = max(h, im.height)
H = y + h + 14; page = 0; ps = 2000
for pg in range(0, H, ps):
    o = Image.new('RGB', (W, min(ps, H - pg) + 14), (0, 0, 0)); d = ImageDraw.Draw(o)
    for (n, im), (px, py) in zip(items, pos):
        if pg <= py < pg + ps - 14:
            o.paste(im, (px, py - pg + 12)); d.text((px, py - pg), n, fill=(255, 255, 0))
    o.save(os.path.join(R, 'work', 'ann', '%s_%d.png' % (out, page))); page += 1
print(page, 'pages', len(items))
