import struct
W=22;H=22;RB=11;GS=RB*H
def load(path):
    d=open(path,'rb').read()
    n=struct.unpack_from('<I',d,0)[0]
    offs=struct.unpack_from("<%dI"%(n-1),d,12);base=12+4*(n-1)
    return d,n,offs,base
def dec(d,base,off):
    out=bytearray();p=base+off
    while len(out)<GS:
        c=d[p];p+=1
        if c&0x80:
            k=c&0x7f;out+=d[p:p+k];p+=k
        else: out+=bytes(c)
    return bytes(out[:GS])
def enc(g):
    out=bytearray();i=0
    while i<len(g):
        j=i
        while j<len(g) and g[j]==0 and j-i<127: j+=1
        if j>i: out.append(j-i);i=j;continue
        j=i
        while j<len(g) and j-i<127 and not (g[j]==0 and (j+1>=len(g) or g[j+1]==0)): j+=1
        out.append(0x80|(j-i));out+=g[i:j];i=j
    return bytes(out)
