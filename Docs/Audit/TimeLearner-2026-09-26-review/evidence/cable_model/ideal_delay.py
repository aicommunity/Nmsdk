import os
import numpy as np, sys, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import library as lib
def margin_pure_delay(tau,D,S_ms):
    K1=lib.sim(1,[(1,8.6e7,[0.0])],tau,D,max(0.05,12*tau+0.02))
    a=np.where(K1>=K1.max()/2)[0]; fw=(a[-1]-a[0])*lib.DT
    pats=lib.patterns(S_ms/1000); t=pats[0]
    d=[t[3]-tk for tk in t]
    P=[]
    for p in pats:
        n=len(K1)+int((S_ms/1000*2)/lib.DT)+10; R=np.zeros(n)
        for dk in d:
            for tj in p:
                s=int(round((tj+dk)/lib.DT)); R[s:s+len(K1)]+=K1
        P.append(R.max())
    return fw*1e3, (P[0]-max(P[1:]))/P[0]
rows=[]
for D in [0.001,0.005]:
  for tau in [0.00025,0.0005,0.001,0.0025,0.005,0.01]:
    for S in [25,50,100,200,480]:
        fw,m=margin_pure_delay(tau,D,S); rows.append(dict(D_ms=D*1e3,tau_ms=tau*1e3,S_ms=S,fwhm_ms=round(fw,2),fw_over_S=round(fw/S,3),margin=round(m,4)))
for r in rows: print(json.dumps(r))
