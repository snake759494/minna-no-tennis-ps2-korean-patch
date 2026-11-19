"""gffont16.bin(22x22 4bpp, 바이트 RLE, 글리프번호 = JIS선형-2) 의 한자 영역에 KS X 1001 한글 2,350자를 그린다.
값: 0=투명, 1~4=외곽선(바깥쪽 페이드), 4+11a=본체.  한글 k번째 → JIS 선형 1410+k (亜 자리부터)."""
import os, sys, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(__file__)); import gffont as F
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(R, 'NanumSquareNeo-dEb.ttf'); SIZE = 18.5; SS = 4; G = 22
LIN0 = 1410

def hangul():
    return [bytes([hi, lo]).decode('cp949') for hi in range(0xb0, 0xc9) for lo in range(0xa1, 0xff)]

def lin2sjis(L):
    ku, ten = L // 94 + 1, L % 94 + 1
    j1, j2 = ku + 0x20, ten + 0x20
    s1 = (j1 + 1) // 2 + (0x70 if j1 <= 0x5e else 0xb0)
    s2 = j2 + (0x1f if j1 & 1 else 0x7e)
    if j1 & 1 and s2 >= 0x7f: s2 += 1
    return bytes([s1, s2])

def charmap():
    return {ch: lin2sjis(LIN0 + k) for k, ch in enumerate(hangul())}

def encode(s):
    """한국어 문자열 → 게임 SJIS 바이트 (한글은 한자 슬롯, 나머지 cp932)"""
    cm = charmap(); out = bytearray()
    for ch in s:
        if ch in cm: out += cm[ch]
        else: out += ch.encode('cp932')
    return bytes(out)

def render(ch, font):
    S = G * SS
    im = Image.new('L', (S, S), 0); dr = ImageDraw.Draw(im)
    bb = dr.textbbox((0, 0), '한', font=font); w = dr.textbbox((0, 0), ch, font=font)
    x = (S - (w[2] - w[0])) / 2 - w[0]; y = (S - (bb[3] - bb[1])) / 2 - bb[1]
    dr.text((x, y), ch, 255, font=font)
    o1 = im.filter(ImageFilter.MaxFilter(9))                      # ~1px
    o2 = o1.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2))   # 바깥 페이드
    f = lambda m: np.asarray(m, np.float32).reshape(G, SS, G, SS).mean((1, 3)) / 255
    a, b, c = f(im), f(o1), f(o2)
    v = np.where(a > 0.03, 4 + 11 * a, np.where(b > 0.5, 4 * b, 3 * c))
    return np.clip(np.rint(v), 0, 15).astype(np.uint8)

def build(src, dst, sheet=None):
    d, n, offs, base = F.load(src)
    glyphs = [bytearray(F.dec(d, base, offs[i])) if i < len(offs) - 1 else None for i in range(len(offs))]
    font = ImageFont.truetype(FONT, int(SIZE * SS))
    for k, ch in enumerate(hangul()):
        v = render(ch, font).reshape(-1)
        glyphs[LIN0 - 2 + k] = bytearray((v[0::2] | (v[1::2] << 4)).astype(np.uint8).tobytes())
    body = bytearray(d[base:base + offs[0]]); newoffs = []
    for i, g in enumerate(glyphs):
        if g is None: newoffs.append(len(body)); body += d[base + offs[i]:]; continue
        newoffs.append(len(body)); body += F.enc(bytes(g))
    out = d[:12] + struct.pack('<%dI' % len(newoffs), *newoffs) + bytes(body)
    open(dst, 'wb').write(out)
    if sheet:
        d2, n2, o2, b2 = F.load(dst); txt = '모두의테니스한글패치亜あア셀렉트'
        cm = charmap(); ims = []
        for ch in txt:
            code = cm[ch] if ch in cm else ch.encode('cp932')
            j = code.decode('cp932').encode('euc_jp'); L = (j[0] - 0xa1) * 94 + (j[1] - 0xa1)
            g = np.frombuffer(F.dec(d2, b2, o2[L - 2]), np.uint8)
            ims.append(np.stack([g & 15, g >> 4], 1).reshape(G, G))
        im = np.concatenate(ims, 1) * 17
        Image.fromarray(im.astype(np.uint8)).resize((im.shape[1] * 3, G * 3), 0).save(sheet)

if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
