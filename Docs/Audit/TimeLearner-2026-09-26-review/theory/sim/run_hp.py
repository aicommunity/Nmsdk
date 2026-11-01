import numpy as np, json, model as m, klib
S=0.025; f=20000; dt=1/f; Lmax=100; tau=0.0003
p=m.base(f=f,Ce=tau/1e7,Ci=tau/1e7,Rmi=1e7,td=0.001,ts=0.0005,tp=0.0005,Tw=0.03+S+Lmax*tau*1.6)
K=klib.lib(p,Lmax); tgt=m.patterns(S)[0]
Ls=klib.sync(K,tgt,dt,list(range(1,Lmax+1))); w=[K[1].max()/K[L].max() for L in Ls]
res=[]
for th in (0.02,0.05,0.1,0.2):
    tt=np.arange(0,8*th*S,dt); h=np.exp(-tt/(th*S)); h/=h.sum()
    for beta in (0.0,0.3,0.5,0.7,0.9,1.0):
        Ks=[]
        for L in Ls:
            k=K[L]; kk=np.concatenate([k,np.zeros(len(h))]); kk=kk-beta*np.convolve(kk,h)[:len(kk)]; Ks.append(kk)
        r=klib.evalK(Ks,w,S,dt)
        # undershoot depth relative to peak for the longest kernel
        und=-Ks[0].min()/Ks[0].max()
        res.append(dict(tau_h_over_S=th,beta=beta,m8=round(r['m8'],4),s4=round(r[0.25],4),s8=round(r[0.125],4),undershoot=round(und,3)))
        print(res[-1])
json.dump(res,open('../data/run_hp.json','w'),indent=1)
