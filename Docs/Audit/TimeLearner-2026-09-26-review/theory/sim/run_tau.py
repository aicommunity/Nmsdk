import numpy as np, json, sys, model as m, evalset as e
S=float(sys.argv[1]); f=float(sys.argv[2]); Lmax=int(sys.argv[3]); topo=sys.argv[4]
taus=[float(x) for x in sys.argv[5].split(',')]
rows=[]
for tau in taus:
    sc=S/0.025
    p=m.base(f=f,Ce=tau/1e7,Ci=tau/1e7,Rmi=1e7,td=0.001*min(1,sc),ts=0.0005,tp=0.0005,Tw=0.03+S+Lmax*tau*1.3)
    tpk,apk,fw=m.peak_table(p,Lmax)
    tgt=m.patterns(S)[0]; Ls=m.sync_L(tpk,tgt); Rs=m.amp_eq(apk,Ls,Rmin=1e6)
    res=e.evaluate(p,S,Ls,Rs,topo=topo)
    r=dict(S_ms=S*1e3,f=f,tau_ms=tau*1e3,c=tau/S,Ls=Ls,fwhm_longest_ms=float(fw[Ls[0]-1]*1e3),sync_err_ms=[float((tpk[L-1]-tpk[0]-(tgt[3]-tgt[k]))*1e3) for k,L in enumerate(Ls)],
           m8=round(res['m8'],4),s4=round(res['shift0.250'],4),s8=round(res['shift0.125'],4),per=[round(x,3) for x in res['per']])
    print(json.dumps(r,ensure_ascii=False),flush=True); rows.append(r)
json.dump(rows,open(f'../data/runtau_S{int(S*1e3)}_dt{1e3/f:g}ms_L{Lmax}_{topo}.json','w'),indent=1)  # f = steps per second (DefaultTimeStep), dt=1/f
