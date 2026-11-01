import os
import numpy as np, sys, json, itertools
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import library as lib
def run(tau,D,spans,Lmax=100,win=3):
    K=lib.kernels(tau,D,Lmax)
    pk=np.array([1]+[K[L].max() for L in range(1,Lmax+1)])
    tp=np.array([0]+[K[L].argmax()*lib.DT for L in range(1,Lmax+1)])
    fw=np.array([0]+[ (lambda a:(a[-1]-a[0])*lib.DT)(np.where(K[L]>=K[L].max()/2)[0]) for L in range(1,Lmax+1)])
    out=[]
    for S in spans:
        pats=lib.patterns(S/1000); t=pats[0]; target=t[3]+tp[1]
        Ls=[];resid=[];feas=True
        for k in range(3):
            need=target-t[k]
            if need>tp[Lmax]+0.5*tau: feas=False
            L=int(np.argmin(np.abs(tp[1:]-need)))+1; Ls.append(L); resid.append(tp[L]-need)
        Ls.append(1)
        m_eq=lib.margin(K,Ls,[1]*4,pats)[0]
        w=[pk[1]/pk[L] for L in Ls]
        m_w=lib.margin(K,Ls,w,pats)[0]
        best=-9;bL=None
        for combo in itertools.product(*[range(max(1,L-win),min(Lmax,L+win)+1) for L in Ls[:3]]):
            LL=list(combo)+[1]
            for ww in ([1]*4,[pk[1]/pk[L] for L in LL]):
                m=lib.margin(K,LL,ww,pats)[0]
                if m>best: best=m;bL=LL
        out.append(dict(tau_ms=tau*1e3,D_ms=D*1e3,S_ms=S,feasible=feas,L=Ls,resid_ms=[round(r*1e3,2) for r in resid],fwhm_long_ms=round(fw[Ls[0]]*1e3,1),fwhm_over_S=round(fw[Ls[0]]*1e3/S,3),m_equal=round(m_eq,4),m_ampnorm=round(m_w,4),m_oracle=round(best,4),oracle_L=bL))
    return out
if __name__=='__main__':
    tau=float(sys.argv[1]);D=float(sys.argv[2]); spans=[float(x) for x in sys.argv[3].split(',')]
    for r in run(tau,D,spans): print(json.dumps(r))
