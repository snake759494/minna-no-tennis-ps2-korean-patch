"""sjscan.py <file> : SJIS 문자열(전각 2자 이상 포함) 전수 검색 → 오프셋, 바이트길이, 텍스트"""
import sys, re
def scan(d, minj=2):
    out = []; i = 0; n = len(d)
    while i < n:
        j = i; s = []; jp = 0
        while j < n:
            b = d[j]
            if (0x81 <= b <= 0x9f or 0xe0 <= b <= 0xfc) and j + 1 < n and 0x40 <= d[j + 1] <= 0xfc and d[j + 1] != 0x7f:
                try: s.append(d[j:j + 2].decode('cp932')); jp += 1; j += 2; continue
                except UnicodeDecodeError: break
            if 0x20 <= b < 0x7f or b in (7, 10): s.append(chr(b)); j += 1; continue
            break
        if jp >= minj:
            # 앞쪽 ASCII 잡음 제거는 하지 않음 (원 위치 유지)
            out.append((i, j - i, ''.join(s)))
            i = j
        else: i += 1
    return out
if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read()
    for o, l, s in scan(d): print('%x\t%d\t%r' % (o, l, s))
