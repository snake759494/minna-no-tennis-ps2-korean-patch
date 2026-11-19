"""TIM2 이미지 속 일본어 → 한국어 교체.
- detect(rgba): 알파 기준 텍스트 덩어리 상자 검출(검토용)
- apply(pic, entries): 상자별로 원본 색(행별 본체색/외곽선색) 샘플 → 지우기 → 한국어 렌더 → 원 팔레트로 재매핑
엔트리: dict(box=(x0,y0,x1,y1), text='..', font='h'|'b'|'g9'|'g11', align='c'|'l'|'r', ow=외곽선px, fill=None|(r,g,b),
             line=None|(r,g,b), clear='a'(투명)|'s'(주변색으로 채움)|'n', size=None(자동), vpad=0, marks={'단어':(r,g,b)})"""
import os, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = {'h': os.path.join(R, 'NanumSquareNeo-eHv.ttf'), 'b': os.path.join(R, 'NanumSquareNeo-dEb.ttf'),
         'm': os.path.join(R, 'NanumSquareNeo-cBd.ttf'),
         'g9': os.path.join(R, 'work', 'fonts', 'Galmuri9.ttf'), 'g11': os.path.join(R, 'work', 'fonts', 'Galmuri11.ttf'),
         'g11b': os.path.join(R, 'work', 'fonts', 'Galmuri11-Bold.ttf'), 'sh': os.path.join(R, 'SeoulHangangEB.ttf')}
_fc = {}
def font(k, px):
    key = (k, px)
    if key not in _fc: _fc[key] = ImageFont.truetype(FONTS[k], px)
    return _fc[key]

def detect(rgba, dx=6, dy=1, amin=24):
    from scipy import ndimage
    m = rgba[..., 3] > amin
    st = np.ones((2 * dy + 1, 2 * dx + 1), bool)
    lab, n = ndimage.label(ndimage.binary_dilation(m, st))
    out = []
    for sl in ndimage.find_objects(lab):
        y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        sub = m[y0:y1, x0:x1]
        if not sub.any(): continue
        ys, xs = np.nonzero(sub)
        out.append((x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1))
    out.sort(key=lambda b: (b[1] // 4, b[0]))
    return out

def sample(rgba, box):
    """본체색(행별), 외곽선색, 외곽선 두께 추정"""
    from scipy import ndimage
    x0, y0, x1, y1 = box; sub = rgba[y0:y1, x0:x1].astype(np.float32)
    a = sub[..., 3] > 128
    if not a.any(): return None, None, 2
    lum = sub[..., :3] @ [0.3, 0.59, 0.11]
    er = ndimage.binary_erosion(a, iterations=1)
    ring = a & ~ndimage.binary_erosion(a, iterations=1)
    line = np.median(sub[ring][:, :3], 0) if ring.any() else np.array([0, 0, 0])
    # 본체 = 불투명 & 외곽선색과 충분히 다른 픽셀
    dist = np.abs(sub[..., :3] - line).sum(-1)
    body = a & (dist > 90)
    if not body.any(): body = er if er.any() else a
    rows = []
    for y in range(sub.shape[0]):
        b = body[y]
        rows.append(np.median(sub[y][b][:, :3], 0) if b.any() else None)
    # 비어있는 행은 보간
    idx = [i for i, r in enumerate(rows) if r is not None]
    if not idx: return None, line, 2
    for i in range(len(rows)):
        if rows[i] is None:
            j = min(idx, key=lambda k: abs(k - i)); rows[i] = rows[j]
    # 외곽선 두께: 본체에서 투명까지 최소 거리 중앙값
    dt = ndimage.distance_transform_edt(~a)  # 투명 픽셀의 불투명까지 거리 (사용 안 함)
    db = ndimage.distance_transform_edt(~body)
    ow = np.median(db[ring]) if ring.any() else 1
    return np.array(rows), line, max(0.0, float(ow))

def _parse(text, marks):
    """'{색이름|글자}' 마크업 → [(글자, 색 또는 None)]"""
    out = []
    for m in re.finditer(r'\{([^|}]+)\|([^}]*)\}|([^{]+)', text):
        if m.group(3): out.append((m.group(3), None))
        else: out.append((m.group(2), marks.get(m.group(1))))
    return out

def render(e, rgba):
    x0, y0, x1, y1 = e['box']; W, H = x1 - x0, y1 - y0
    rows, line, ow = sample(rgba, e.get('sbox', e['box']))
    if e.get('fill') is not None:
        fl = np.array(e['fill'], np.float32)
        if fl.ndim == 1: rows = np.tile(fl, (H, 1))
        else:
            t = np.clip((np.arange(H) - ow) / max(1, H - 2 * ow - 1), 0, 1) * (len(fl) - 1)
            i0 = np.floor(t).astype(int); i1 = np.minimum(i0 + 1, len(fl) - 1); f_ = (t - i0)[:, None]
            rows = fl[i0] * (1 - f_) + fl[i1] * f_
    if e.get('line') is not None: line = np.array(e['line'], np.float32)
    if rows is None: rows = np.tile(np.array([255, 255, 255], np.float32), (H, 1))
    if line is None: line = np.array([0, 0, 0], np.float32)
    if len(rows) != H:
        rows = np.array([rows[min(len(rows) - 1, int(i * len(rows) / H))] for i in range(H)])
    ow = e.get('ow', round(ow))
    SS = 4; lines = e['text'].split('\n'); n = len(lines)
    fk = e.get('font', 'h'); pix = fk.startswith('g')
    lh = (H - 2 * ow) / n
    size = e.get('size') or max(6, int(round(lh * (0.92 if not pix else 1.0))))
    def measure(s):
        f = font(fk, s * (1 if pix else SS))
        return [(f.getbbox(re.sub(r'\{[^|}]+\|([^}]*)\}', r'\1', L) or ' ')) for L in lines], f
    # 너비 맞춤: 넘치면 가로 압축(최대 60%) 후 크기 축소
    bbs, f = measure(size)
    scale = 1 if pix else SS
    maxw = max(b[2] - b[0] for b in bbs) / scale
    sx = 1.0
    avail = W - 2 * ow
    if maxw > avail:
        sx = avail / maxw
        if sx < e.get('minsx', 0.62):
            size = max(6, int(size * sx / e.get('minsx', 0.62))); bbs, f = measure(size); maxw = max(b[2] - b[0] for b in bbs) / scale
            sx = min(1.0, avail / maxw)
    # 고해상도 캔버스에 줄별 렌더 (색 마크 지원)
    S = 1 if pix else SS
    cw = int(maxw * S / 1) + 8 * S; chh = int(H * S)
    body = Image.new('L', (int(W * S / sx) + 8 * S, chh), 0)
    colmask = {}
    asc = f.getbbox('한')
    for i, L in enumerate(lines):
        segs = _parse(L, e.get('marks', {}))
        plain = ''.join(s for s, _ in segs)
        bb = f.getbbox(plain or ' ')
        tw = bb[2] - bb[0]
        al = e.get('align', 'c')
        if al == 'c': x = (body.width - tw) / 2 - bb[0]
        elif al == 'l': x = ow * S / sx - bb[0]
        else: x = body.width - tw - ow * S / sx - bb[0]
        cy = (ow + lh * (i + 0.5) + e.get('vpad', 0)) * S
        y = cy - (asc[1] + asc[3]) / 2
        for s, c in segs:
            d = ImageDraw.Draw(body); d.text((x, y), s, 255, font=f)
            if c is not None:
                m = Image.new('L', body.size, 0); ImageDraw.Draw(m).text((x, y), s, 255, font=f)
                colmask.setdefault(tuple(c), []).append(m)
            x += f.getlength(s)
    tw = int(round(body.width * sx / S)); th = H
    def down(img):
        if S == 1:
            return np.asarray(img.resize((tw, th), Image.BILINEAR if sx < 1 else Image.NEAREST), np.float32) / 255
        return np.asarray(img.resize((tw, th), Image.LANCZOS), np.float32) / 255
    a = np.clip(down(body), 0, 1)
    if pix: a = (a > 0.45).astype(np.float32)
    from scipy import ndimage
    if ow > 0:
        o = ndimage.grey_dilation(a, footprint=_disk(ow))
    else: o = a.copy()
    # 결과 RGBA (상자 크기로 가운데 맞춤 잘라내기)
    out = np.zeros((th, tw, 4), np.float32)
    col = np.repeat(rows[:, None, :], tw, 1)
    for c, ms in colmask.items():
        mm = sum(down(m) for m in ms); mm = np.clip(mm, 0, 1)
        if pix: mm = (mm > 0.45).astype(np.float32)
        mm = ndimage.grey_dilation(mm, size=(1, 1))
        col = col * (1 - mm[..., None]) + np.array(c, np.float32) * mm[..., None]
    rgb = col * a[..., None] + line * (1 - a[..., None])
    alpha = np.maximum(a, o)
    if e.get('shadow'):
        sdx, sdy, sc, sa = e['shadow']
        sh = np.zeros_like(alpha); sh[sdy:, sdx:] = alpha[:alpha.shape[0] - sdy, :alpha.shape[1] - sdx] * sa
        tot = alpha + sh * (1 - alpha)
        rgb = (rgb * alpha[..., None] + np.array(sc, np.float32) * (sh * (1 - alpha))[..., None]) / np.maximum(tot, 1e-6)[..., None]
        alpha = tot
    alpha = alpha * 255
    out[..., :3] = rgb; out[..., 3] = alpha
    if tw > W:
        al = e.get('align', 'c')
        cx = (tw - W) // 2 if al == 'c' else (0 if al == 'l' else tw - W); out = out[:, cx:cx + W]
    elif tw < W:
        pad = np.zeros((th, W, 4), np.float32); px = (W - tw) // 2 if e.get('align', 'c') == 'c' else (0 if e.get('align') == 'l' else W - tw)
        pad[:, px:px + tw] = out; out = pad
    return out

def _fit(t, rgba, e):
    """원본 글자 잉크의 가로 범위(cbox 안) 밖으로 새 글자가 나가면 이동/가로 압축해 그 안에 맞춤"""
    bx0, by0, bx1, by1 = e['box']; cx0, cy0, cx1, cy1 = e.get('cbox', e['box'])
    om = rgba[cy0:cy1, cx0:cx1, 3] > 24
    nm = t[..., 3] > 24
    if not om.any() or not nm.any(): return t
    cols = np.nonzero(om.any(0))[0]; ox0, ox1 = cx0 + cols[0] - bx0, cx0 + cols[-1] - bx0   # box 좌표계
    ncols = np.nonzero(nm.any(0))[0]; nx0, nx1 = ncols[0], ncols[-1]
    lo, hi = max(0, ox0 - e.get('fitpad', 1)), min(t.shape[1] - 1, ox1 + e.get('fitpad', 1))
    if nx0 >= lo and nx1 <= hi: return t
    ink = t[:, nx0:nx1 + 1]; w = nx1 - nx0 + 1; avail = hi - lo + 1
    if w > avail:
        from PIL import Image as _I
        ink = np.asarray(_I.fromarray(np.clip(ink, 0, 255).astype(np.uint8), 'RGBA').resize((avail, ink.shape[0]), _I.LANCZOS)).astype(np.float32)
        w = avail; px = lo
    else:
        px = min(max(nx0, lo), hi - w + 1)
    out = np.zeros_like(t); out[:, px:px + w] = ink
    return out

def _disk(r):
    r2 = int(np.ceil(r)); y, x = np.mgrid[-r2:r2 + 1, -r2:r2 + 1]
    return (x * x + y * y) <= r * r + 0.5

def compose(rgba, entries):
    img = rgba.astype(np.float32).copy()
    for e in entries:
        x0, y0, x1, y1 = e.get('cbox', e['box'])
        cl = e.get('clear', 'a')
        if cl == 'a': img[y0:y1, x0:x1] = 0
        elif cl == 'row':   # 행마다 깨끗한 열(sx)의 색으로 채움 (가로 줄무늬 배경)
            sx = e.get('sx', max(0, x0 - 3))
            img[y0:y1, x0:x1] = rgba[y0:y1, sx:sx + 1].astype(np.float32)
        elif cl == 'col':   # 열마다 깨끗한 행(sy)의 색
            sy = e.get('sy', max(0, y0 - 2))
            img[y0:y1, x0:x1] = rgba[sy:sy + 1, x0:x1].astype(np.float32)
        elif cl == 'mask':  # 마스크 내부 픽셀을 그 행의 유채색 중앙값으로
            mk = e['mask']; sub = img[y0:y1, x0:x1]; mm = mk[y0:y1, x0:x1]
            for yy in range(sub.shape[0]):
                row = img[y0 + yy]; s2 = row[..., :3].max(-1) - row[..., :3].min(-1)
                sel = mk[y0 + yy] & (s2 > 40)
                if sel.any(): sub[yy][mm[yy]] = np.median(row[sel], 0)
        elif cl == 'inpaint':  # 사진 위 글자: 상자 내부를 주변으로 인페인팅
            import cv2
            msk = np.zeros(img.shape[:2], np.uint8); msk[y0:y1, x0:x1] = 255
            rgb = np.clip(img[..., :3], 0, 255).astype(np.uint8)
            img[..., :3] = cv2.inpaint(rgb, msk, 3, cv2.INPAINT_TELEA).astype(np.float32)
        elif cl == 'tinpaint':  # 상자 안 글자 픽셀(흰 본체·어두운 외곽)만 인페인팅
            import cv2
            rgb = np.clip(img[..., :3], 0, 255).astype(np.uint8)
            sub = rgb[y0:y1, x0:x1].astype(int); lum = sub.mean(-1); sat = sub.max(-1) - sub.min(-1)
            m = ((lum > e.get('hi', 200)) & (sat < 40)) | ((lum < e.get('lo', 110)) & (sat < 50))
            for c in e.get('tcols', []):
                m |= (np.abs(sub - np.array(c)).sum(-1) < e.get('ctol', 90))
            msk = np.zeros(img.shape[:2], np.uint8); msk[y0:y1, x0:x1] = m * 255
            msk = cv2.dilate(msk, np.ones((3, 3), np.uint8), iterations=e.get('dil', 1))
            img[..., :3] = cv2.inpaint(rgb, msk, 4, cv2.INPAINT_TELEA).astype(np.float32)
        elif cl == 'grayw':  # 밝기 lo~hi 무채색(글자) 픽셀만 흰색으로 (흰 스티커 위 글자)
            sub = img[y0:y1, x0:x1]; lum = sub[..., :3].mean(-1)
            m = (lum > e.get('lo', 60)) & (lum < e.get('hi', 238))
            sub[m, :3] = e.get('bg', (250, 250, 250))
        elif cl == 'bar':   # 채도 낮은(글자) 픽셀만 그 행의 유채색 중앙값으로
            sub = img[y0:y1, x0:x1]
            rgb = sub[..., :3]; sat = rgb.max(-1) - rgb.min(-1)
            for yy in range(sub.shape[0]):
                ok = sat[yy] > e.get('sat', 40)
                src = img[y0 + yy, e.get('bx0', 0):e.get('bx1', img.shape[1])]
                s2 = src[..., :3].max(-1) - src[..., :3].min(-1)
                if (s2 > e.get('sat', 40)).any():
                    c = np.median(src[s2 > e.get('sat', 40)], 0)
                    sub[yy][~ok] = c
        elif cl == 's':
            c = e.get('bg')
            if c is None:
                ring = np.concatenate([img[max(0, y0 - 1), x0:x1], img[min(img.shape[0] - 1, y1), x0:x1]])
                c = np.median(ring, 0)
            img[y0:y1, x0:x1] = c
        if e.get('text', '') == '': continue
        x0, y0, x1, y1 = e['box']
        t = render(e, rgba)
        if not e.get('nofit') and not e.get('rot'): t = _fit(t, rgba, e)
        if e.get('rot'):
            from PIL import Image as _I
            t = np.asarray(_I.fromarray(t.astype(np.uint8), 'RGBA').rotate(e['rot'], resample=_I.BICUBIC)).astype(np.float32)
        reg = img[y0:y1, x0:x1]
        a = t[..., 3:4] / 255
        reg[..., :3] = t[..., :3] * a + reg[..., :3] * (1 - a)
        reg[..., 3] = np.maximum(reg[..., 3], t[..., 3])
    return np.clip(np.rint(img), 0, 255).astype(np.uint8)
