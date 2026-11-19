import sys, glob, os, collections
sys.path.insert(0, os.path.dirname(__file__)); import tim2
from PIL import Image
c = collections.Counter(); err = 0
os.makedirs('png', exist_ok=True)
for fn in glob.glob('xb/data/**/*.tm2', recursive=True):
    fn = fn.replace(os.sep, '/')
    if '/face' in fn: continue
    try: pics = tim2.read(open(fn, 'rb').read())
    except Exception as e: err += 1; print(fn, e); continue
    for i, p in enumerate(pics):
        c[(p['itype'], p['ctype'] & 0x1f)] += 1
        out = 'png/' + fn[8:].replace('/', '_') + ('_%d' % i if len(pics) > 1 else '') + '.png'
        Image.fromarray(p['rgba']).save(out)
print(c, err)
