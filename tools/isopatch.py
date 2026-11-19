"""원본 ISO 복사 후 파일 교체. 원래 할당 공간(다음 파일 LBA 전까지)에 들어가면 제자리, 아니면 ISO 끝에 추가.
디렉터리 레코드(LBA/크기 LE+BE)와 PVD 볼륨 크기 갱신."""
import struct, shutil, os, sys
sys.path.insert(0, os.path.dirname(__file__)); import iso as I

def patch(src, dst, files):
    if os.path.abspath(src) != os.path.abspath(dst): shutil.copyfile(src, dst)
    f = open(dst, 'r+b'); recs = I.records(f)
    starts = sorted(v[0] for v in recs.values())
    f.seek(0, 2); end = (f.tell() + 2047) // 2048
    for path, data in files.items():
        lba, size, roff = recs[path]
        nxt = min([s for s in starts if s > lba] + [end])
        if (len(data) + 2047) // 2048 <= nxt - lba:
            newlba = lba
        else:
            newlba = end; end += (len(data) + 2047) // 2048
        f.seek(newlba * 2048); f.write(data + b'\0' * ((-len(data)) % 2048))
        if newlba == lba and size > len(data):
            pass
        f.seek(roff + 2); f.write(struct.pack('<I', newlba) + struct.pack('>I', newlba) + struct.pack('<I', len(data)) + struct.pack('>I', len(data)))
    f.seek(0, 2); tot = f.tell() // 2048
    f.seek(16 * 2048 + 80); f.write(struct.pack('<I', tot) + struct.pack('>I', tot))
    f.close()
