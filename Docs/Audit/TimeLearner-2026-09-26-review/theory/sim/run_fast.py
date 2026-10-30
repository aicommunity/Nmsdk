import numpy as np, json, sys, model as m, evalset as e
def fastset(S,c=0.007,f=20000,Lcap=260):
    k=S/0.025; tau=c*S
    return m.base(f=f,Ce=tau/1e7,Ci=tau/1e7,Rmi=1e7,FBR=1e7,td=0.001*k,ts=0.0005*k,tp=0.0005*k,Tw=0.02*k+S+Lcap*tau*1.3), tau
out=[]
for S,c,Lcap in [(0.025,0.007,230),(0.05,0.007,200),(0.1,0.007,180),(0.025,0.012,100),(0.05,0.012,100),(0.1,0.012,100)]:
    p,tau=fastset(S,c,Lcap=Lcap)
    tpk,apk,fw=m.peak_table(p,Lcap)
    tgt=m.patterns(S)[0]; Ls=m.sync_L(tpk,tgt); Rs=m.amp_eq(apk,Ls,Rmin=2e7)
    for topo in ('classic','branch'):
        r=e.evaluate(p,S,Ls,Rs,topo=topo)
        row=dict(S_ms=S*1e3,c=c,tau_ms=round(tau*1e3,4),Cm=tau/1e7,Ls=Ls,Rs=[round(x/1e6,1) for x in Rs],topo=topo,m8=round(r['m8'],4),shiftS4=round(r['shift0.250'],4),shiftS8=round(r['shift0.125'],4),per=[round(x,3) for x in r['per']],fwhm_ms=round(fw[Ls[0]-1]*1e3,2))
        print(json.dumps(row),flush=True); out.append(row)
json.dump(out,open('../data/run_fast.json','w'),indent=1)
