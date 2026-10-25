import numpy as np, json, sys, model as m, klib
S=0.025; f=20000; dt=1/f; Lmax=100; tau=float(sys.argv[1]) if len(sys.argv)>1 else 0.0003
p=m.base(f=f,Ce=tau/1e7,Ci=tau/1e7,Rmi=1e7,td=0.001,ts=0.0005,tp=0.0005,Tw=0.03+S+Lmax*tau*1.6)
K=klib.lib(p,Lmax); tgt=m.patterns(S)[0]
# exc only baseline
Ls=klib.sync(K,tgt,dt,list(range(1,Lmax+1)))
w=[K[1].max()/K[L].max() for L in Ls]
b=klib.evalK([K[L] for L in Ls],w,S,dt); print('exc-only',Ls,{k:(round(v,4) if not isinstance(v,list) else [round(x,3) for x in v]) for k,v in b.items()})
best=[]
for d in (1,2,3,5,8,12,16,24):
    for a in (0.3,0.5,0.7,0.85,1.0):
        C={}
        for L in range(1,Lmax+1-d):
            k=K[L].copy(); ki=K[L+d]; n=max(len(k),len(ki)); c=np.zeros(n); c[:len(k)]+=k; c[:len(ki)]-=a*ki*(K[L].max()/ki.max()) if False else a*ki; C[L]=c
        cands=[L for L in C if C[L].max()>0.2*K[L].max()]
        if len(cands)<10: continue
        LL=klib.sync(C,tgt,dt,cands)
        w=[C[LL[3]].max()/C[L].max() for L in LL]
        r=klib.evalK([C[L] for L in LL],w,S,dt)
        best.append((min(r['m8'],r[0.25]),d,a,LL,round(r['m8'],4),round(r[0.25],4),round(r[0.125],4),[round(x,3) for x in r['per']]))
best.sort(key=lambda x:-x[0])
for x in best[:6]: print(x)
