"""png 폴더 이미지들을 번호 붙인 시트로 (검토용). sheet.py <glob> <out_prefix> [per=30]"""
import sys, glob, os
from PIL import Image, ImageDraw
fs = sorted(glob.glob(sys.argv[1])); pre = sys.argv[2]; per = int(sys.argv[3]) if len(sys.argv) > 3 else 30
TW, TH = 300, 150
for s in range(0, len(fs), per):
    grp = fs[s:s + per]; cols = 5; rows = (len(grp) + cols - 1) // cols
    sh = Image.new('RGB', (cols * TW, rows * (TH + 14)), (60, 60, 90)); dr = ImageDraw.Draw(sh)
    for k, f in enumerate(grp):
        im = Image.open(f).convert('RGBA'); bg = Image.new('RGBA', im.size, (90, 90, 140, 255)); bg.alpha_composite(im)
        im = bg.convert('RGB'); im.thumbnail((TW - 4, TH - 4))
        x, y = (k % cols) * TW, (k // cols) * (TH + 14)
        sh.paste(im, (x + 2, y + 2)); dr.text((x + 2, y + TH), '%d %s' % (s + k, os.path.basename(f)[:44]), (255, 255, 0))
    sh.save('%s_%02d.png' % (pre, s // per))
    print('%s_%02d.png' % (pre, s // per))
