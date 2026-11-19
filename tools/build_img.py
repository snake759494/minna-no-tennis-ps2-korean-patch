"""translation/images.py 의 SPEC 적용 → xb_ko/ 에 수정 tm2 저장, 미리보기 prev/ 생성.
build_img.py [필터문자열]"""
import sys, os, importlib.util
sys.path.insert(0, os.path.dirname(__file__)); import tim2, imgtext
import numpy as np
from PIL import Image
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(R, 'translation'))
def load_spec():
    spec = {}
    import glob
    for fn in sorted(glob.glob(os.path.join(R, 'translation', 'img_*.py'))):
        s = importlib.util.spec_from_file_location('m', fn); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
        spec.update(m.SPEC)
    return spec
def build(flt=None, prev=True):
    spec = load_spec(); out = {}
    for path, pics in spec.items():
        if flt and flt not in path: continue
        src = os.path.join(R, 'work', 'xb', path); d = open(src, 'rb').read()
        P = tim2.read(d)
        if isinstance(pics, list): pics = {0: pics}
        for pi, ents in pics.items():
            pic = P[pi]
            new = imgtext.compose(pic['rgba'], ents)
            d = tim2.write(d, pic, new)
        out[path] = d
        if prev:
            P2 = tim2.read(d)
            os.makedirs(os.path.join(R, 'work', 'prev'), exist_ok=True)
            for pi in pics:
                a, b = P[pi]['rgba'], P2[pi]['rgba']
                def flat(x):
                    bg = Image.new('RGBA', (x.shape[1], x.shape[0]), (70, 70, 120, 255)); bg.alpha_composite(Image.fromarray(x)); return bg.convert('RGB')
                im = Image.new('RGB', (a.shape[1], a.shape[0] * 2 + 2), (255, 0, 0))
                im.paste(flat(a), (0, 0)); im.paste(flat(b), (0, a.shape[0] + 2))
                sc = 2 if a.shape[1] <= 512 else 1
                im = im.resize((im.width * sc, im.height * sc), Image.NEAREST)
                im.save(os.path.join(R, 'work', 'prev', path.replace('/', '_') + '_%d.png' % pi))
    return out
if __name__ == '__main__':
    o = build(sys.argv[1] if len(sys.argv) > 1 else None)
    print(len(o), 'files')
