"""TIM2 읽기/쓰기 (픽처 여러 장, 4/8bpp CLUT(CSM1 스위즐 처리), 16/24/32bpp). 알파 0x80=불투명 -> 255 로 확장."""
import struct
import numpy as np

def _a(a): return np.minimum(255, a.astype(np.int32) * 2).astype(np.uint8)

def _clut_order(n):
    idx = np.arange(n)
    if n == 256:
        b = idx & 0x18
        idx = (idx & ~0x18) | ((b & 8) << 1) | ((b & 0x10) >> 1)
    return idx

def _pal(raw, ctype, n):
    t = ctype & 0x1f
    if t == 3:
        p = np.frombuffer(raw, np.uint8, n * 4).reshape(n, 4).copy(); p[:, 3] = _a(p[:, 3])
    elif t == 2:
        p = np.frombuffer(raw, np.uint8, n * 3).reshape(n, 3); p = np.concatenate([p, np.full((n, 1), 255, np.uint8)], 1)
    else:
        v = np.frombuffer(raw, '<u2', n).astype(np.uint32)
        p = np.stack([(v & 31) << 3, (v >> 5 & 31) << 3, (v >> 10 & 31) << 3, np.where(v >> 15, 255, 0)], 1).astype(np.uint8)
    if not (ctype & 0x80): p = p[_clut_order(n)]
    return p

def read(d):
    assert d[:4] == b'TIM2', d[:4]
    cnt = struct.unpack_from('<H', d, 6)[0]
    p = 0x10 if d[5] == 0 else 0x80
    pics = []
    for _ in range(cnt):
        tot, csz, isz, hsz, ccol, fmt, mip, ctype, itype, w, h = struct.unpack_from('<IIIHHBBBBHH', d, p)
        img = d[p + hsz:p + hsz + isz]; cl = d[p + hsz + isz:p + hsz + isz + csz]
        if itype == 4:
            a = np.frombuffer(img, np.uint8, w * h // 2); idx = np.stack([a & 15, a >> 4], 1).reshape(h, w)
            rgba = _pal(cl, ctype, 16)[idx]
        elif itype == 5:
            idx = np.frombuffer(img, np.uint8, w * h).reshape(h, w); rgba = _pal(cl, ctype, 256)[idx]
        elif itype == 3:
            rgba = np.frombuffer(img, np.uint8, w * h * 4).reshape(h, w, 4).copy(); rgba[..., 3] = _a(rgba[..., 3])
        elif itype == 2:
            rgb = np.frombuffer(img, np.uint8, w * h * 3).reshape(h, w, 3); rgba = np.concatenate([rgb, np.full((h, w, 1), 255, np.uint8)], 2)
        else:
            v = np.frombuffer(img, '<u2', w * h).astype(np.uint32).reshape(h, w)
            rgba = np.stack([(v & 31) << 3, (v >> 5 & 31) << 3, (v >> 10 & 31) << 3, np.where(v >> 15, 255, 0)], 2).astype(np.uint8)
        pics.append(dict(off=p, hsz=hsz, isz=isz, csz=csz, w=w, h=h, itype=itype, ctype=ctype, rgba=rgba))
        p += tot
    return pics

def write(d, pic, rgba, orig=None):
    """rgba 를 원래 팔레트로 재매핑해 TIM2 바이트(d) 안의 해당 픽처 이미지 데이터 교체. 바뀐 픽셀만 재계산."""
    d = bytearray(d); w, h, it = pic['w'], pic['h'], pic['itype']
    st = pic['off'] + pic['hsz']
    if it in (4, 5):
        n = 16 if it == 4 else 256
        cl = bytes(d[st + pic['isz']:st + pic['isz'] + pic['csz']])
        pal = _pal(cl, pic['ctype'], n).astype(np.int32)
        if it == 4:
            a = np.frombuffer(bytes(d[st:st + w * h // 2]), np.uint8); idx = np.stack([a & 15, a >> 4], 1).reshape(h, w).copy()
        else:
            idx = np.frombuffer(bytes(d[st:st + w * h]), np.uint8).reshape(h, w).copy()
        cur = pal[idx]
        chg = np.any(cur != rgba.astype(np.int32), -1)
        ys, xs = np.nonzero(chg)
        if len(ys):
            for k in range(0, len(ys), 8000):
                yy, xx = ys[k:k + 8000], xs[k:k + 8000]
                px = rgba[yy, xx].astype(np.int32)
                # 알파 가중 거리 (투명이면 색 무시)
                dif = px[:, None, :3] - pal[None, :, :3]
                dc = (dif * dif).sum(-1) * (np.minimum(px[:, None, 3], pal[None, :, 3]) / 255.0)
                da = (px[:, None, 3] - pal[None, :, 3]) ** 2 * 3.0
                cost = dc + da
                if (pic['ctype'] & 0x1f) == 3:      # 불투명 픽셀은 원 팔레트의 대표 알파(raw)를 가진 색만 사용 (게임이 알파값으로 합성)
                    ra = np.frombuffer(cl, np.uint8, n * 4).reshape(n, 4)[:, 3]
                    if not (pic['ctype'] & 0x80): ra = ra[_clut_order(n)]
                    op = ra >= 0x80
                    if op.any():
                        main = np.bincount(ra[op]).argmax()
                        bad = (ra != main) & op
                        cost = cost + np.where((px[:, None, 3] >= 250) & bad[None, :], 1e9, 0)
                idx[yy, xx] = np.argmin(cost, 1)
        if it == 4:
            f = idx.reshape(-1); raw = (f[0::2] | (f[1::2] << 4)).astype(np.uint8)
        else: raw = idx.astype(np.uint8).reshape(-1)
        d[st:st + len(raw)] = raw.tobytes()
    elif it == 3:
        r = rgba.copy(); r[..., 3] = (r[..., 3].astype(np.int32) + 1) // 2
        d[st:st + w * h * 4] = r.tobytes()
    else:
        raise NotImplementedError(it)
    return bytes(d)
