import numpy as np, json, sys, model as m, evalset as e
rows=[]
f=20000
for S in (0.025,0.1):
    k=S/0.025; eta=1/f/S
    for c in (0.004,0.005,0.006,0.008,0.01,0.012,0.016,0.024,0.04,0.08):
        Lcap=int(np.ceil(1.12/(c-eta)))+2
        if Lcap>600: continue
        tau=c*S
        p=m.base(f=f,Ce=tau/1e7,Ci=tau/1e7,Rmi=1e7,td=0.001*k,ts=0.0005*k,tp=0.0005*k,Tw=0.02*k+S+Lcap*tau*1.4)
        tpk,apk,fw=m.peak_table(p,Lcap); tgt=m.patterns(S)[0]; Ls=m.sync_L(tpk,tgt); Rs=m.amp_eq(apk,Ls,Rmin=2e7)
        r=e.evaluate(p,S,Ls,Rs,topo='classic',shifts=(1/4,1/8,1/12))
        row=dict(S_ms=S*1e3,c=c,eta=eta,L1=Ls[0],sigma_over_S=None,fwhm_over_S=float(fw[Ls[0]-1]/S),m8=r['m8'],s4=r['shift0.250'],s8=r['shift0.125'],s12=r['shift0.083'])
        print(json.dumps(row),flush=True); rows.append(row)
json.dump(rows,open('../data/run_collapse.json','w'),indent=1)
