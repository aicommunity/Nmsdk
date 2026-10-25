import os
import numpy as np, sys, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from library import kernels, patterns, DT
def oracle(tau,D,S_ms,Lcap=40,ds=5,wmode='equal'):
    K=kernels(tau,D,Lcap)
    pats=patterns(S_ms/1000)
    Tn=max(len(K[L]) for L in range(1,Lcap+1))+int(S_ms/1000/DT)+5
    Tn=(Tn//ds+1)*ds
    r=np.zeros((Lcap+1,8,Tn//ds))
    for L in range(1,Lcap+1):
        for pi,p in enumerate(pats):
            R=np.zeros(Tn)
            for tj in p:
                s=int(round(tj/DT)); R[s:s+len(K[L])]+=K[L][:Tn-s]
            r[L,pi]=R.reshape(-1,ds).max(1)
    pk=np.array([1]+[K[L].max() for L in range(1,Lcap+1)])
    w=np.ones(Lcap+1) if wmode=='equal' else np.minimum(pk[1]/pk,86/20)
    base=w[1]*r[1]  # anchor L=1, shape 8xT
    best=(-9,None); allm=[]
    Ls=np.arange(1,Lcap+1)
    for L0 in Ls:
        A=base+w[L0]*r[L0]
        # combos L1,L2 vectorized
        B=A[None,None]+ (w[Ls,None,None]*r[Ls])[:,None] + (w[Ls,None,None]*r[Ls])[None,:]  # L1 x L2 x 8 x T
        P=B.max(-1)
        m=(P[...,0]-P[...,1:].max(-1))/P[...,0]
        i=np.unravel_index(np.argmax(m),m.shape)
        if m[i]>best[0]: best=(float(m[i]),[int(L0),int(Ls[i[0]]),int(Ls[i[1]]),1])
        allm.append(m)
    allm=np.array(allm)
    return {'tau_ms':tau*1000,'D_ms':D*1000,'S_ms':S_ms,'w':wmode,'best_margin':round(best[0],4),'best_L':best[1],'frac_combos_positive':round(float((allm>0).mean()),4)}
if __name__=='__main__':
    print(json.dumps(oracle(float(sys.argv[1]),float(sys.argv[2]),float(sys.argv[3]),int(sys.argv[4]) if len(sys.argv)>4 else 40, wmode=sys.argv[5] if len(sys.argv)>5 else 'equal')))
