"""MTL/MTI (메뉴 3D 텍스처): MTL 0x20부터 0x50 엔트리. MTI = 전 텍스처 픽셀(+밉) 순서대로, 텍스처마다 픽셀(+밉) 다음 팔레트(32bit)."""
import struct, numpy as np
from tim2 import _pal
def parse(mtl):
    n = struct.unpack_from('<I', mtl, 0x10)[0]; ents = []; po = 0
    for i in range(n):
        e = mtl[0x20 + i * 0x50: 0x70 + i * 0x50]
        nc, w, h = struct.unpack_from('<HHH', e, 0); psm = e[12]; nm = e[15]
        sz = struct.unpack_from('<I', e, 16)[0]
        ms = sum(struct.unpack_from('<I', e, 24 + 8 * k)[0] for k in range(nm))
        ents.append(dict(nc=nc, w=w, h=h, psm=psm, sz=sz, pix=po, tot=sz + ms, nm=nm, pal=po + sz + ms)); po += sz + ms + nc * 4
    return ents
def get(mti, e):
    raw = np.frombuffer(mti, np.uint8, e['sz'], e['pix'])
    if e['psm'] == 0x14: raw = np.stack([raw & 15, raw >> 4], 1).reshape(-1)
    idx = raw[:e['w'] * e['h']].reshape(e['h'], e['w'])
    pal = _pal(mti[e['pal']:e['pal'] + e['nc'] * 4], 3, e['nc'])
    return idx, pal
