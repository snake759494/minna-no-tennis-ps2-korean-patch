"""검증 전용: work/emu/pcsx2-tennis.exe 를 최소화·비활성으로 실행. PINE(28247)으로 메모리/상태저장,
상태저장 속 Screenshot.png 로 화면 확인. 입력은 가상패드: 0x187484 (xori a3,a3,0xffff) 후킹 → VPAD OR.
사용: emu.py launch <iso> [state] | stop | snap <tag> | press X 1.0 U ... | save n | load n"""
import subprocess, sys, os, time, glob, zipfile, struct, ctypes, socket
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMU = os.path.join(R, 'work', 'emu'); EXE = os.path.join(EMU, 'pcsx2-tennis.exe'); PORT = 28247
VPAD = 0x000ff000; CAVE = 0x000ff100; HOOK = 0x187484
BTN = dict(SELECT=1, L3=2, R3=4, START=8, U=0x10, R=0x20, D=0x40, L=0x80, L2=0x100, R2=0x200, L1=0x400, R1=0x800,
           T=0x1000, O=0x2000, X=0x4000, S=0x8000)
def j(a): return (2 << 26) | (a >> 2)
def pnach():
    code = [0x38e7ffff,                                  # xori a3,a3,0xffff
            0x3c010000 | ((VPAD + 0x8000) >> 16),        # lui at
            0x8c210000 | (VPAD & 0xffff),                # lw at,lo(at)
            0x00e13825,                                  # or a3,a3,at
            j(HOOK + 8),
            0xa4670000]                                  # sh a3,0(v1)
    out = ['gametitle=Minna no Tennis (dev vpad)']
    out += ['patch=1,EE,%08x,word,%08x' % (CAVE + 4 * i, c) for i, c in enumerate(code)]
    out += ['patch=1,EE,%08x,word,%08x' % (HOOK, j(CAVE)), 'patch=1,EE,%08x,word,00000000' % (HOOK + 4)]
    if os.environ.get('WIDE'): out += [l for l in open(os.path.join(R, 'SCPS-15113_A35F1A97.pnach'), encoding='utf8').read().splitlines() if l.startswith('patch=')]
    return '\n'.join(out) + '\n'
def elf_crc(iso):
    sys.path.insert(0, os.path.dirname(__file__)); import iso as I
    f = open(iso, 'rb'); r = I.records(f)['SCPS_151.13']; d = I.read(f, r); c = 0
    for (x,) in struct.iter_unpack('<I', d[:len(d)//4*4]): c ^= x
    return c
def launch(iso, state=None):
    stop(); crc = elf_crc(iso)
    for f in glob.glob(os.path.join(EMU, 'cheats', '*.pnach')): os.remove(f)
    open(os.path.join(EMU, 'cheats', '%08X.pnach' % crc), 'w').write(pnach())
    si = subprocess.STARTUPINFO(); si.dwFlags = 1; si.wShowWindow = 7   # SW_SHOWMINNOACTIVE
    args = [EXE, '-batch', '-nogui']
    if state: args += ['-statefile', state]
    p = subprocess.Popen(args + ['--', os.path.abspath(iso)], cwd=EMU, startupinfo=si)
    print('pid', p.pid, 'crc %08X' % crc); hide(p.pid)
def wins(pid):
    u = ctypes.windll.user32; hs = []
    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def cb(h, l):
        pp = ctypes.c_ulong(); u.GetWindowThreadProcessId(ctypes.c_void_p(h), ctypes.byref(pp))
        if pp.value == pid and u.IsWindowVisible(ctypes.c_void_p(h)): hs.append(h)
        return True
    u.EnumWindows(cb, 0); return hs
def hide(pid):
    u = ctypes.windll.user32
    for _ in range(150):
        hs = wins(pid)
        if hs:
            time.sleep(1.0)
            for h in hs: u.ShowWindow(ctypes.c_void_p(h), 7)
            return
        time.sleep(0.2)
def stop():
    for _ in range(30):
        r = subprocess.run(['tasklist', '/fi', 'imagename eq pcsx2-tennis.exe'], capture_output=True, text=True)
        if 'pcsx2-tennis.exe' not in r.stdout: return
        subprocess.run(['taskkill', '/F', '/T', '/IM', 'pcsx2-tennis.exe'], capture_output=True); time.sleep(1)
_S = [None]
def pine(payload):
    try: return _pine(payload)
    except (OSError, EOFError):
        _S[0] = None; return _pine(payload)
def _pine(payload):
    if _S[0] is None: _S[0] = socket.create_connection(('127.0.0.1', PORT), timeout=30)
    s = _S[0]
    s.sendall(struct.pack('<I', len(payload) + 4) + payload)
    def rv(n):
        b = b''
        while len(b) < n:
            c = s.recv(n - len(b))
            if not c: raise EOFError
            b += c
        return b
    n = struct.unpack('<I', rv(4))[0]; return rv(n - 4)
def w32(a, v): return pine(struct.pack('<BII', 6, a, v))
def r32(a): return struct.unpack_from('<I', pine(struct.pack('<BI', 2, a)), 1)[0]
def press(names, ms=180):
    m = 0
    for n in names.split('+'): m |= BTN[n]
    w32(VPAD, m); time.sleep(ms / 1000); w32(VPAD, 0); time.sleep(0.3)
def member(p, name):
    import zstandard
    with zipfile.ZipFile(p) as z: i = z.getinfo(name)
    with open(p, 'rb') as f:
        f.seek(i.header_offset); h = f.read(30); n, e = struct.unpack_from('<HH', h, 26); f.seek(n + e, 1)
        raw = f.read(i.compress_size)
    if i.compress_type == 0: return raw
    if i.compress_type == 93: return zstandard.ZstdDecompressor().decompress(raw, max_output_size=i.file_size)
    with zipfile.ZipFile(p) as z: return z.read(name)
def latest():
    ps = glob.glob(os.path.join(EMU, 'sstates', '*.p2s'))
    return max(ps, key=os.path.getmtime) if ps else None
def save(slot=9):
    old = latest(); t = os.path.getmtime(old) if old else 0
    pine(struct.pack('<BB', 9, slot))
    for _ in range(300):
        p = latest()
        if p and os.path.getmtime(p) > t: time.sleep(1.0); return p
        time.sleep(0.1)
def snap(tag, slot=9):
    p = save(slot)
    os.makedirs(os.path.join(R, 'work', 'shots'), exist_ok=True)
    out = os.path.join(R, 'work', 'shots', '%s.png' % tag)
    open(out, 'wb').write(member(p, 'Screenshot.png')); print(out); return p
if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'launch': launch(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif c == 'stop': stop()
    elif c == 'snap': snap(sys.argv[2])
    elif c == 'press':
        for k in sys.argv[2:]:
            try: time.sleep(float(k))
            except ValueError: press(k)
    elif c == 'save': print(pine(struct.pack('<BB', 9, int(sys.argv[2]))))
    elif c == 'load': print(pine(struct.pack('<BB', 0xa, int(sys.argv[2]))))
    elif c == 'rd':
        a = int(sys.argv[2], 16); print(' '.join('%08x' % r32(a + 4 * k) for k in range(int(sys.argv[3]))))
