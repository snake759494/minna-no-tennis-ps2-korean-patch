"""모두의테니스 XB 아카이브.
헤더: 'xe' u16 ver(0x100) u32 count, 엔트리 count*(u32 출력크기, u32 (method<<28)|(off/4)),
이어서 이름표 블록. 블록 = u32 원본크기, u32 압축크기(0=무압축), 데이터.
method 0=허프만→LZ, 1=허프만, 2=LZ, 3=무압축(블록 헤더 없이 raw).
이름 레코드: u8 len, u8 hash(rotl8^c), name, NUL  (크기 len+3)
"""
import struct, sys, os

def lz_dec(src, n):
    out = bytearray(); p = 0
    while len(out) < n:
        t = src[p]; p += 1
        if t & 3 == 0:
            l = (t >> 2) + 1; out += src[p:p+l]; p += l
        elif t & 1:
            v = t | src[p] << 8; p += 1
            l = ((v >> 1) & 7) + 3; dist = v >> 4
            for _ in range(l): out.append(out[-dist])
        else:
            v = t | src[p] << 8 | src[p+1] << 16; p += 2
            l = ((v >> 2) & 0x3ff) + 3; dist = v >> 12
            for _ in range(l): out.append(out[-dist])
    return bytes(out[:n])

def lz_enc(data, chain=256):
    """해시 체인 LZ + 1단계 lazy. 거리 1..4095, 길이 3..1026 (2바이트: 길이3~10, 3바이트: ~1026)"""
    out = bytearray(); lit = bytearray(); n = len(data)
    head = {}
    def flush():
        nonlocal lit
        while lit:
            c = lit[:64]; lit = lit[64:]
            out.append((len(c) - 1) << 2); out.extend(c)
    def ins(k):
        if k + 3 <= n: head.setdefault(data[k:k+3], []).append(k)
    def find(i):
        best = 0; bd = 0
        if i + 3 > n: return 0, 0
        cand = head.get(data[i:i+3])
        if not cand: return 0, 0
        m = min(1026, n - i)
        for j in reversed(cand[-chain:]):
            d = i - j
            if d > 4095: break
            if best >= m: break
            if data[j + best] != data[i + best]: continue
            l = 3
            while l < m and data[j+l] == data[i+l]: l += 1
            if l > best: best, bd = l, d
            if l == m: break
        return best, bd
    i = 0
    while i < n:
        best, bd = find(i); pre = False
        if 3 <= best < 1026 and i + 1 < n:
            ins(i); pre = True
            nb, nd = find(i + 1)
            if nb > best + (1 if best >= 11 or nb <= 10 else 0):
                lit.append(data[i]); i += 1; best, bd = nb, nd; pre = False
        if best >= 3:
            flush()
            if best <= 10:
                v = (bd << 4) | ((best - 3) << 1) | 1
                out += bytes((v & 0xff, v >> 8))
            else:
                v = (bd << 12) | ((best - 3) << 2) | 2
                out += bytes((v & 0xff, (v >> 8) & 0xff, v >> 16))
            for k in range(i + (1 if pre else 0), i + best): ins(k)
            i += best
        else:
            lit.append(data[i])
            if not pre: ins(i)
            i += 1
    flush()
    return bytes(out)

def huf_dec(blk, n):
    N = blk[0]; p = 1; tab = [None] * 1024; code = 0
    for L in range(1, N + 1):
        c = blk[p]; p += 1
        for _ in range(c):
            s = blk[p]; p += 1
            r = int(format(code, '0%db' % L)[::-1], 2) if L else 0
            if L <= 10:
                for k in range(r, 1024, 1 << L): tab[k] = (L, s)
            if L < 11: code += 1
        code <<= 1
    if p & 1: p += 1
    out = bytearray(); bits = 0; nb = 0
    while len(out) < n:
        if nb < 16:
            bits |= (blk[p] | blk[p+1] << 8) << nb if p + 1 < len(blk) else 0; p += 2; nb += 16
        e = tab[bits & 0x3ff]
        if e:
            out.append(e[1]); bits >>= e[0]; nb -= e[0]
        else:
            bits >>= 10; nb -= 10
            if nb < 16:
                bits |= (blk[p] | blk[p+1] << 8) << nb if p + 1 < len(blk) else 0; p += 2; nb += 16
            out.append(bits & 0xff); bits >>= 8; nb -= 8
    return bytes(out)

def block(d, off):
    n, c = struct.unpack_from('<II', d, off)
    return (d[off+8:off+8+n] if c == 0 else None), n, c, off + 8

def unpack(d):
    assert d[:2] == b'xe'
    cnt = struct.unpack_from('<I', d, 4)[0]
    nb = 8 + cnt * 8
    n, c = struct.unpack_from('<II', d, nb)
    names_raw = d[nb+8:nb+8+n] if c == 0 else lz_dec(d[nb+8:], n)
    names = []; p = 0
    for _ in range(cnt):
        l = names_raw[p]; names.append(names_raw[p+2:p+2+l].decode('latin1')); p += l + 3
    ents = []
    for i in range(cnt):
        size, w = struct.unpack_from('<II', d, 8 + i * 8)
        m = w >> 28; off = (w & 0xfffffff) * 4
        if m == 3:
            data = d[off:off+size]
        else:
            n, c = struct.unpack_from('<II', d, off)
            raw = d[off+8:]
            if c == 0: mid = raw[:n]
            elif m in (0, 1): mid = huf_dec(raw, n)
            else: mid = raw
            if m == 0:
                n2, c2 = struct.unpack_from('<II', mid, 0)
                data = mid[8:8+n2] if c2 == 0 else lz_dec(mid[8:], n2)
            elif m == 2: data = lz_dec(mid, size)
            else: data = mid[:size]
        ents.append((names[i], data, m))
    return ents, names_raw

def pack(ents, names_raw, orig=None):
    """orig 지정 시 데이터가 같은 엔트리는 원본 블록(다음 엔트리 오프셋까지)을 그대로 복사"""
    keep = {}
    if orig is not None:
        oe, _ = unpack(orig)
        offs = sorted(set((struct.unpack_from('<I', orig, 12 + k * 8)[0] & 0xfffffff) * 4 for k in range(len(oe)))) + [len(orig)]
        for i, (nm, data, m) in enumerate(oe):
            off = (struct.unpack_from('<I', orig, 12 + i * 8)[0] & 0xfffffff) * 4
            end = min(x for x in offs if x > off); blk = orig[off:end]
            while len(blk) % 4: blk += bytes(1)
            keep[i] = (data, m, blk)
    cnt = len(ents)
    hdr = bytearray(b'xe\x00\x01' + struct.pack('<I', cnt) + bytes(cnt * 8))
    body = bytearray(hdr)
    body += struct.pack('<II', len(names_raw), 0) + names_raw
    while len(body) % 4: body.append(0)
    for i, (nm, data, m) in enumerate(ents):
        off = len(body)
        if i in keep and keep[i][0] == data:
            m = keep[i][1]; body += keep[i][2]
        elif m == 3:
            body += data
        else:
            c = lz_enc(data)
            body += struct.pack('<II', len(data), len(c)) + c
            m = 2
        while len(body) % 4: body.append(0)
        struct.pack_into('<II', body, 8 + i * 8, len(data), (m << 28) | (off // 4))
    return bytes(body)

if __name__ == '__main__':
    ents, _ = unpack(open(sys.argv[1], 'rb').read())
    for nm, data, m in ents: print(m, len(data), nm)
