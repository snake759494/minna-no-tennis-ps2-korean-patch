"""ISO9660 재귀 목록/추출. records(f) -> {경로: (lba, size, 레코드오프셋)}"""
import struct, sys, os
def _dir(f, lba, size, pre, out):
    f.seek(lba*2048); d = f.read(size); p = 0
    while p < len(d):
        n = d[p]
        if n == 0: p = (p//2048+1)*2048; continue
        l, s = struct.unpack_from('<I', d, p+2)[0], struct.unpack_from('<I', d, p+10)[0]
        fl = d[p+25]; nm = d[p+33:p+33+d[p+32]].decode('latin1').split(';')[0]
        if nm not in ('\x00', '\x01'):
            path = pre + nm
            if fl & 2: _dir(f, l, s, path + '/', out)
            else: out[path] = (l, s, lba*2048+p)
        p += n
def records(f):
    f.seek(16*2048); pvd = f.read(2048)
    out = {}; _dir(f, struct.unpack_from('<I', pvd, 158)[0], struct.unpack_from('<I', pvd, 166)[0], '', out)
    return out
def read(f, rec):
    f.seek(rec[0]*2048); return f.read(rec[1])
if __name__ == '__main__':
    f = open(sys.argv[1], 'rb')
    for k, v in sorted(records(f).items(), key=lambda x: x[1][0]): print(v[0], v[1], k)
