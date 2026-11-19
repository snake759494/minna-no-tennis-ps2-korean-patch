import re,sys,json
d=open(sys.argv[1],'rb').read()
pat=re.compile(rb'(?<=\x00)(?:[\x81-\x9f\xe0-\xef][\x40-\xfc]|[\x01-\x7e])+\x00')
out=[]
for m in pat.finditer(d,0x67300):
    s=m.group()[:-1]
    try:t=s.decode('cp932')
    except:continue
    jp=re.findall('[　-ヿ一-鿿＀-￯]',t)
    kana=re.findall('[぀-ヿ０-ｚ]',t)
    if not (len(kana)>=1 or len(jp)>=2): continue
    out.append([m.start(),len(s),t])
json.dump(out,open(sys.argv[2],'w',encoding='utf-8'),ensure_ascii=False,indent=0)
open(sys.argv[2].replace('.json','.txt'),'w',encoding='utf-8').write('\n'.join('%x %d %r'%(a,l,t) for a,l,t in out))
print(len(out),sum(len(x[2]) for x in out))
