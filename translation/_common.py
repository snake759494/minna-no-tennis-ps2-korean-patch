import os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, 'tools')); import tim2, imgtext
_cache = {}
def boxes(path, dx=4, dy=1, pi=0):
    k = (path, dx, dy, pi)
    if k not in _cache:
        rgba = tim2.read(open(os.path.join(R, 'work', 'xb', path), 'rb').read())[pi]['rgba']
        _cache[k] = [tuple(int(v) for v in b) for b in imgtext.detect(rgba, dx, dy)]
    return _cache[k]
def by_id(path, items, dx=4, dy=1, pi=0, **kw):
    """items: {박스번호 또는 (x0,y0,x1,y1): 텍스트 또는 (텍스트, {옵션})}"""
    bs = boxes(path, dx, dy, pi); out = []
    for k, v in items.items():
        box = bs[k] if isinstance(k, int) else k
        if isinstance(v, tuple): t, o = v
        else: t, o = v, {}
        e = dict(box=box, text=t); e.update(kw); e.update(o); out.append(e)
    return out
def padl(ents, px=3, W=None):
    for e in ents:
        if e.get('align') == 'l':
            b = e['box']; e.setdefault('cbox', b); e['box'] = (b[0] + px, b[1], b[2] + px if W is None else min(W, b[2] + px), b[3])
    return ents
