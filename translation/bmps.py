"""8bpp BMP(640x448) 한글화: 타이틀 로고 자막, 게임오버 말풍선, 개발 경고문. 원 팔레트 유지(최근접 색)."""
import os, sys, struct, numpy as np
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, 'tools')); import imgtext
M = 'data/menu/2d/'
def edit(path, ents):
    d = bytearray(open(os.path.join(R, 'work', 'xb', path), 'rb').read())
    off, = struct.unpack_from('<I', d, 10); w, h = struct.unpack_from('<ii', d, 18); bpp, = struct.unpack_from('<H', d, 28)
    assert bpp == 8
    pal = np.frombuffer(bytes(d[54:off]), np.uint8).reshape(-1, 4)[:, [2, 1, 0]].astype(np.float32)
    stride = (w + 3) & ~3
    idx = np.frombuffer(bytes(d[off:off + stride * h]), np.uint8).reshape(h, stride)[::-1, :w].copy()
    rgba = np.concatenate([pal[idx], np.full((h, w, 1), 255, np.float32)], -1).astype(np.uint8)
    new = imgtext.compose(rgba, ents)
    ch = np.any(new != rgba, -1); ys, xs = np.nonzero(ch)
    for y, x in zip(ys, xs):
        idx[y, x] = ((pal - new[y, x, :3].astype(np.float32)) ** 2).sum(-1).argmin()
    rows = np.zeros((h, stride), np.uint8); rows[:, :w] = idx
    d[off:off + stride * h] = rows[::-1].tobytes()
    return bytes(d)
def build():
    out = {}
    cap = [dict(box=(150, 290, 490, 334), text='모두의 테니스', font='h', size=32, fill=(255, 255, 255), line=(20, 70, 160), ow=3, clear='n')]
    for k in range(11):
        p = M + 'wall/title_bg%02d.bmp' % k; out[p] = edit(p, cap)
    out[M + 'gameover.bmp'] = edit(M + 'gameover.bmp', [dict(cbox=(212, 128, 528, 178), clear='inpaint', box=(220, 134, 520, 172),
                                                          text='수고하셨습니다!', font='h', size=28, fill=(70, 70, 70))])
    lines = ['이 소프트웨어는 현재 개발 중이므로', '정상적으로 동작하지 않는 등, 예기치 못한 문제가', '발견될 가능성이 있습니다.',
             '만일 오작동 등이 발생하더라도', '디스크 교환은 해 드릴 수 없으니 양해 바랍니다.']
    ents = [dict(cbox=(60, 196, 586, 362), clear='tinpaint', hi=200, lo=90, dil=2, box=(60, 196, 586, 362), text='')]
    for i, t in enumerate(lines):
        ents.append(dict(box=(60, 198 + 32 * i, 586, 226 + 32 * i), text=t, font='h', fill=(255, 255, 255), line=(20, 20, 20), ow=2, clear='n'))
    out[M + 'warning.bmp'] = edit(M + 'warning.bmp', ents)
    return out
if __name__ == '__main__':
    from PIL import Image
    o = build(); s = Image.new('RGB', (1280, 896))
    for i, k in enumerate([M + 'wall/title_bg00.bmp', M + 'wall/title_bg05.bmp', M + 'gameover.bmp', M + 'warning.bmp']):
        import io; s.paste(Image.open(io.BytesIO(o[k])).convert('RGB'), ((i % 2) * 640, (i // 2) * 448))
    s.save(os.path.join(R, 'work', 'png', 'bmps_ko.png'))
