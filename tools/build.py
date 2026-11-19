"""전체 빌드: 폰트·이미지 → XB 재패킹, MENU.BIN 번역, ISO 패치"""
import sys, os, glob
sys.path.insert(0, os.path.dirname(__file__))
import xb, menubin, isopatch, build_img, iso as I
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(R, 'Minna no Tennis (Japan, Asia).iso')
DST = os.path.join(R, 'Minna no Tennis (Japan, Asia) (Korean).iso')
def norm(nm): return nm.replace(chr(92), '/').replace('../', '')
def main(dst=DST):
    mod = build_img.build(prev=False)
    sys.path.insert(0, os.path.join(R, 'translation')); import sign3d, bmps; mod.update(sign3d.build()); mod.update(bmps.build())
    for k in os.environ.get('SKIP', '').split(','):
        [mod.pop(x) for x in [x for x in mod if k and k in x]]
    mod['data/common/gffont16.bin'] = open(os.path.join(R, 'work', 'gffont16_ko.bin'), 'rb').read()
    files = {}; used = set()
    orig = os.path.join(R, 'work', 'orig')
    for fn in glob.glob(os.path.join(orig, '**', '*.XB'), recursive=True):
        d = open(fn, 'rb').read()
        try: ents, names = xb.unpack(d)
        except Exception: continue
        hit = False; new = []
        for nm, data, m in ents:
            k = norm(nm)
            if k in mod: data = mod[k]; hit = True; used.add(k)
            new.append((nm, data, m))
        if hit:
            files[os.path.relpath(fn, orig).replace(os.sep, '/').upper()] = xb.pack(new, names, d)
    miss = set(mod) - used
    if miss: print('미사용:', sorted(miss))
    mb, bad = menubin.build(os.path.join(orig, 'ZZBIN', 'MENU.BIN'), os.path.join(R, 'translation', 'menu_bin.tsv'))
    tmp = os.path.join(R, 'work', '_menu_tmp.bin'); open(tmp, 'wb').write(mb)
    mb, bad2 = (menubin.build(tmp, os.path.join(R, 'translation', 'menu_bin2.tsv')) if not os.environ.get('NO_MB2') else (mb, [])); os.remove(tmp)
    if bad or bad2: print('MENU.BIN 초과:', bad, bad2)
    if not os.environ.get('NO_MB'): files['ZZBIN/MENU.BIN'] = mb
    with open(SRC, 'rb') as f: keys = I.records(f).keys()
    fx = {}
    for k, v in files.items():
        m = [x for x in keys if x.upper().lstrip('/').split(';')[0] == k]
        if not m: print('ISO 경로 없음', k); continue
        fx[m[0]] = v
    isopatch.patch(SRC, dst, fx)
    # ELF 내부 파일 LBA 테이블 갱신 (엔트리 32B: name, lba, lba+섹터수, 섹터수)
    import struct
    with open(SRC, 'rb') as f: a = I.records(f)
    with open(dst, 'r+b') as f:
        b = I.records(f); el, es, _ = b['SCPS_151.13']
        f.seek(el * 2048); elf = bytearray(f.read(es)); n = 0
        for k in fx:
            ol = a[k][0]; nl, ns = b[k][0], b[k][1]; cnt = (ns + 2047) // 2048
            for o in range(0, len(elf) - 32, 4):
                if struct.unpack_from('<I', elf, o + 8)[0] == ol and struct.unpack_from('<I', elf, o + 16)[0] == ol + struct.unpack_from('<I', elf, o + 24)[0] - 1:
                    struct.pack_into('<I', elf, o + 8, nl); struct.pack_into('<I', elf, o + 16, nl + cnt - 1); struct.pack_into('<I', elf, o + 24, cnt); n += 1
        import kfont
        ES = ((0xcfd18, '올'), (0xcfd20, '네트'), (0xcfd28, '베이스'), (0xcfd30, '빅'))
        for off, t in (ES if os.environ.get('ELF_STR') else ()):
            b = kfont.encode(t); assert len(b) < 8; elf[off:off + 8] = b + bytes(8 - len(b))
        f.seek(el * 2048); f.write(elf)
    print('ELF 테이블 갱신', n)
    print(len(fx), 'files ->', dst)
if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else DST)
