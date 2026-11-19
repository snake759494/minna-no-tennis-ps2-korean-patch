"""MENU.BIN 도움말 문자열 제자리 교체 (슬롯 = 다음 비0 바이트 전까지)"""
import sys,os
sys.path.insert(0,os.path.dirname(__file__));import kfont
def build(src,tsv):
    d=bytearray(open(src,'rb').read());bad=[]
    for line in open(tsv,encoding='utf-8'):
        if not line.strip():continue
        a,t=line.rstrip('\n').split('\t');a=int(a,16)
        t=t.replace(chr(92)+'x07',chr(7))
        b=kfont.encode(t)
        e=a
        while d[e]!=0:e+=1
        while e<len(d) and d[e]==0:e+=1
        cap=e-a
        if len(b)+1>cap: bad.append((hex(a),len(b)+1,cap,t));continue
        d[a:e]=b+bytes(cap-len(b))
    return bytes(d),bad
if __name__=='__main__':
    d,bad=build(sys.argv[1],sys.argv[2])
    for x in bad:print('OVER',x)
