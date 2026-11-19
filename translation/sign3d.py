"""메인 메뉴 3D 간판 (data/menu/3d/proto_01.MTI 텍스처 1~5, 128x85 8bpp). 원 팔레트 유지, 최근접 색 인덱스로 재그림."""
import os, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as nd
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, 'tools')); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import mti
FONT = os.path.join(R, 'NanumSquareNeo-eHv.ttf')
KEY = 'data/menu/3d/proto_01.MTI'
SIGNS = {1: ['트레이닝', '모드'], 2: ['모두의 테니스'], 3: ['데이터'], 4: ['옵션'], 5: ['챌린지', '모드']}
def render(lines, box, W, H, ss=4):
    x0, y0, x1, y1 = box; bw, bh = (x1 - x0) * ss, (y1 - y0) * ss
    n = len(lines); lh = bh / n; sz = int(lh * 1.6)
    while True:
        f = ImageFont.truetype(FONT, sz)
        bbs = [f.getbbox(t) for t in lines]
        if (max(b[2] - b[0] for b in bbs) <= bw and max(b[3] - b[1] for b in bbs) <= lh) or sz < 8: break
        sz -= 2
    im = Image.new('L', (W * ss, H * ss), 0); d = ImageDraw.Draw(im)
    for k, t in enumerate(lines):
        bb = f.getbbox(t); cx = x0 * ss + bw / 2; cy = y0 * ss + lh * (k + .5)
        d.text((cx - (bb[0] + bb[2]) / 2, cy - (bb[1] + bb[3]) / 2), t, font=f, fill=255)
    return np.asarray(im.resize((W, H), Image.LANCZOS)).astype(float) / 255
def sign(idx, pal, lines):
    H, W = idx.shape; body = idx[:84]
    a = pal[body][..., 3]; mk = a > 128
    ys, xs = np.nonzero(mk); box = (max(xs.min(), 3), ys.min() + 1, min(xs.max() + 1, W - 3), ys.max())
    inn = nd.binary_erosion(mk, iterations=2)
    fill = np.median(pal[body[inn]][:, :3], 0); edge = np.median(pal[body[mk & ~inn]][:, :3], 0)
    g = render(lines, box, W, 84)
    ol = np.clip(nd.maximum_filter(g, size=5) * 1.0, 0, 1)            # 외곽선 범위
    rgb = fill * g[..., None] + edge * (1 - g[..., None])
    alpha = np.maximum(ol, g) * 255
    tgt = np.concatenate([rgb, alpha[..., None]], -1)
    P = pal.astype(float); bg = int(np.argmin(P[:, 3]))
    dist = ((tgt[:, :, None, :] - P[None, None]) ** 2 * np.array([1, 1, 1, 2])).sum(-1)
    new = dist.argmin(-1).astype(np.uint8); new[alpha < 20] = idx[0, 0] if pal[idx[0, 0]][3] < 20 else bg
    out = idx.copy(); out[:84] = new; return out
def banner(idx, pal, text, ow=4, glow=False):
    """행별 채움색(원본 내부 중앙값) 유지, 외곽선색=원본 외곽 중앙값"""
    H, W = idx.shape; a = pal[idx][..., 3]; mk = a > 128
    ys, xs = np.nonzero(mk); box = (xs.min() + 2, ys.min() + 2, xs.max() - 1, ys.max() - 1)
    inn = nd.binary_erosion(mk, iterations=3)
    edge = np.median(pal[idx[mk & ~nd.binary_erosion(mk, iterations=1)]][:, :3], 0)
    rows = np.zeros((H, 3)); last = None
    for y in range(H):
        r = pal[idx[y][inn[y]]][:, :3]
        if len(r): last = np.median(r, 0)
        rows[y] = last if last is not None else edge
    for y in range(H - 1, -1, -1):
        if not inn[y].any() and y + 1 < H and not inn[:y + 1].any(): rows[y] = rows[y + 1]
    g = render([text], box, W, H)
    if glow:                                        # 단색 글로우 레이어
        op = np.bincount(idx[mk]).argmax(); bg = np.bincount(idx[~mk]).argmax() if (~mk).any() else 0
        sh = nd.maximum_filter(g, size=ow * 2 + 1) > 0.35
        return np.where(sh, op, bg).astype(np.uint8)
    ol = np.clip(nd.maximum_filter(g, size=ow * 2 + 1), 0, 1)
    rgb = rows[:, None, :] * g[..., None] + edge * (1 - g[..., None])
    alpha = np.maximum(ol, g) * 255
    tgt = np.concatenate([rgb, alpha[..., None]], -1); P = pal.astype(float)
    dist = ((tgt[:, :, None, :] - P[None, None]) ** 2 * np.array([1, 1, 1, 3])).sum(-1)
    return dist.argmin(-1).astype(np.uint8)
def put4(m, e, new):
    if e['psm'] == 0x14:
        f = new.reshape(-1); b = (f[0::2] & 15) | (f[1::2] << 4); m[e['pix']:e['pix'] + len(b)] = b.astype(np.uint8).tobytes()
    else: m[e['pix']:e['pix'] + e['sz']] = new.tobytes()
GS = 'data/azuma/inpane/CourtPreview/i_gamestart_00'
def build(dir_=None):
    out = build_signs(dir_)
    base = os.path.join(R, 'work', 'xb', GS)
    es = mti.parse(open(base + '.MTL', 'rb').read()); m = bytearray(open(base + '.MTI', 'rb').read())
    idx, pal = mti.get(bytes(m), es[0]); put4(m, es[0], banner(idx, pal, '시합 시작!'))
    out[GS + '.MTI'] = bytes(m)
    for f, texts in CALLS.items():
        base = os.path.join(R, 'work', 'xb', f)
        es = mti.parse(open(base + '.MTL', 'rb').read()); m = bytearray(open(base + '.MTI', 'rb').read())
        for i, t in texts.items():
            idx, pal = mti.get(bytes(m), es[i])
            if isinstance(t, tuple):        # 위아래 두 줄 (각 줄 색 유지)
                h = idx.shape[0] // 2
                new = np.concatenate([banner(idx[:h], pal, t[0]), banner(idx[h:], pal, t[1])], 0)
            elif isinstance(t, list): new = banner(idx, pal, t[0], glow=True)
            else: new = banner(idx, pal, t)
            put4(m, es[i], new)
        out[f + '.MTI'] = bytes(m)
    build_prize(out)
    return out
def quant(rgba, pal):
    P = pal.astype(np.float32); out = np.empty(rgba.shape[:2], np.uint8); w = np.array([1, 1, 1, 2], np.float32)
    for y in range(rgba.shape[0]):
        out[y] = (((rgba[y].astype(np.float32)[:, None] - P[None]) ** 2) * w).sum(-1).argmin(-1)
    return out
def edit2d(m, e, ents):
    import imgtext
    idx, pal = mti.get(bytes(m), e); new = imgtext.compose(pal[idx], ents)
    q = quant(new, pal); changed = np.any(new != pal[idx], -1); q = np.where(changed, q, idx); put4(m, e, q.astype(np.uint8))
PZ = 'data/azuma/inpane/mdl/prize/'
def build_prize(out):
    from img_menu1 import DAN, RANKS
    BR = (95, 60, 50)
    for k, dan in enumerate(DAN):
        f = PZ + 'letter_dani%02d' % k; base = os.path.join(R, 'work', 'xb', f)
        es = mti.parse(open(base + '.MTL', 'rb').read()); m = bytearray(open(base + '.MTI', 'rb').read())
        edit2d(m, es[0], [dict(cbox=(12, 5, 237, 31), clear='inpaint', box=(14, 6, 235, 30), text='모두의 테니스 단위 인정증', font='h', fill=(255, 255, 255), line=BR, ow=2),
                          dict(cbox=(22, 66, 238, 107), clear='inpaint', box=(24, 67, 234, 105), text=dan, font='sh', fill=(70, 42, 36)),
                          dict(cbox=(36, 113, 224, 136), clear='inpaint', box=(40, 115, 220, 134), text='모두의 테니스 단위 인정 위원회', font='b', fill=BR)])
        out[f + '.MTI'] = bytes(m)
    for k, rk in enumerate(RANKS):
        f = PZ + 'r%02d' % k; base = os.path.join(R, 'work', 'xb', f)
        es = mti.parse(open(base + '.MTL', 'rb').read()); m = bytearray(open(base + '.MTI', 'rb').read())
        for i, gl in ((1, False), (2, True)):
            idx, pal = mti.get(bytes(m), es[i]); put4(m, es[i], banner(idx, pal, rk, ow=3, glow=gl))
        out[f + '.MTI'] = bytes(m)
    f = PZ + 'RankUp_kiroku'; base = os.path.join(R, 'work', 'xb', f)
    es = mti.parse(open(base + '.MTL', 'rb').read()); m = bytearray(open(base + '.MTI', 'rb').read())
    idx, pal = mti.get(bytes(m), es[0]); put4(m, es[0], banner(idx, pal, '기록 갱신!!')); out[f + '.MTI'] = bytes(m)
I = 'data/azuma/inpane/mdl/'
CALLS = {I + 'i_coatchange_00': {0: ('체인지', '코트')}, I + 'i_doublefault_00': {0: '더블 폴트'}, I + 'i_fault_00': {0: '폴트'},
         I + 'i_gameset_00': {0: '게임 세트', 1: ['게임 세트']}, I + 'i_let_00': {0: '렛'}, I + 'i_net_00': {0: '네트'}, I + 'i_out_00': {0: '아웃'}}
def build_signs(dir_=None):
    D = dir_ or os.path.join(R, 'work', 'xb', 'data', 'menu', '3d')
    es = mti.parse(open(os.path.join(D, 'proto_01.MTL'), 'rb').read()); m = bytearray(open(os.path.join(D, 'proto_01.MTI'), 'rb').read())
    for i, lines in SIGNS.items():
        e = es[i]; idx, pal = mti.get(bytes(m), e)
        new = sign(idx, pal, lines); m[e['pix']:e['pix'] + e['sz']] = new.tobytes()
    return {KEY: bytes(m)}
if __name__ == '__main__':
    d = build()[KEY]; D = os.path.join(R, 'work', 'xb', 'data', 'menu', '3d')
    es = mti.parse(open(os.path.join(D, 'proto_01.MTL'), 'rb').read()); rows = []
    for i in SIGNS:
        idx, p = mti.get(d, es[i]); a = p[idx].astype(float); al = a[..., 3:] / 255
        rows.append((a[..., :3] * al + 60 * (1 - al)).astype(np.uint8))
    Image.fromarray(np.concatenate(rows, 0)).resize((256, 850), Image.NEAREST).save(os.path.join(R, 'work', 'png', 'signs_ko.png'))
