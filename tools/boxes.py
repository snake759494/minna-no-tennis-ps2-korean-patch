"""검토용: tm2 의 텍스트 덩어리 상자 번호 표시. boxes.py <tm2경로(xb/ 기준)> [pic] [dx] [dy] [scale]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__)); import tim2, imgtext
from PIL import Image, ImageDraw
p = sys.argv[1]; pi = int(sys.argv[2]) if len(sys.argv) > 2 else 0
dx = int(sys.argv[3]) if len(sys.argv) > 3 else 6; dy = int(sys.argv[4]) if len(sys.argv) > 4 else 1
sc = int(sys.argv[5]) if len(sys.argv) > 5 else 2
pic = tim2.read(open(os.path.join('xb', p), 'rb').read())[pi]
rgba = pic['rgba']; bs = imgtext.detect(rgba, dx, dy)
bg = Image.new('RGBA', (rgba.shape[1], rgba.shape[0]), (70, 70, 120, 255)); bg.alpha_composite(Image.fromarray(rgba))
im = bg.convert('RGB').resize((rgba.shape[1] * sc, rgba.shape[0] * sc), Image.NEAREST); dr = ImageDraw.Draw(im)
for i, (x0, y0, x1, y1) in enumerate(bs):
    dr.rectangle((x0 * sc, y0 * sc, x1 * sc - 1, y1 * sc - 1), outline=(255, 0, 0))
    dr.text((x0 * sc + 1, y0 * sc), str(i), (0, 255, 0))
    print(i, (x0, y0, x1, y1))
os.makedirs('ann', exist_ok=True)
out = 'ann/' + p.replace('/', '_') + '_%d.png' % pi; im.save(out); print(out, rgba.shape, pic['itype'])
