import sys,os;sys.path.insert(0,os.path.dirname(__file__));import iso
f=open(sys.argv[1],'rb');r=iso.records(f)
for k,v in r.items():
    if k.endswith('.PSS') or k.startswith('SND/'):continue
    p=os.path.join(sys.argv[2],k);os.makedirs(os.path.dirname(p) or '.',exist_ok=True);open(p,'wb').write(iso.read(f,v))
