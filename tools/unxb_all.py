import sys,glob,os,collections
sys.path.insert(0,os.path.dirname(__file__));import xb
cnt=collections.Counter();bad=[]
for fn in glob.glob('orig/**/*.XB',recursive=True):
    try:
        ents,_=xb.unpack(open(fn,'rb').read())
        for nm,data,m in ents:
            cnt[os.path.splitext(nm)[1].lower()]+=1
            p=os.path.join('xb',nm.replace(chr(92),'/').replace('../',''))
            os.makedirs(os.path.dirname(p),exist_ok=True);open(p,'wb').write(data)
    except Exception as e: bad.append((fn,repr(e)))
print(cnt);print(bad[:10])
