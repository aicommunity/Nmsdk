import numpy as np, subprocess, itertools, json, sys, os
import os
SIM=os.environ.get('CABLE_SIM', os.path.join(os.path.dirname(os.path.abspath(__file__)),'cable'))
F=20000; SUB=2; DT=SUB/F
def sim(n, syns, tau, D, T, f=F, Rm=1e7, sub=SUB):
    C=tau/Rm
    inp=f"{n}\n{len(syns)}\n"+"".join(f"{p} {rs} {len(ts)} "+" ".join(map(str,ts))+"\n" for p,rs,ts in syns)
    out=subprocess.run([SIM,str(f),str(C),str(Rm),str(D),'0.001','0.001',str(T),str(sub)],input=inp,capture_output=True,text=True).stdout
    return np.array(out.split(),float)
def kernels(tau,D,Lmax=100):
    T=min(4.0, 0.03+ (Lmax*tau)*1.0 + 8*tau*np.sqrt(Lmax)+0.05)
    K=[None]
    for L in range(1,Lmax+1):
        K.append(sim(L,[(L,8.6e7,[0.0])],tau,D,T))
    return K
pats_isi=[0.000520833,0.00416667,0.00833333,0.0125,0.000520833,0.0125,0.00833333,0.00416667,0.000520833,0.00833333,0.00416667,0.0125,0.000520833,0.00833333,0.00833333,0.00833333,0.000520833,0.00104167,0.0114583,0.0125,0.000520833,0.0125,0.0114583,0.00104167,0.000520833,0.00208333,0.00208333,0.0208333,0.000520833,0.0208333,0.00208333,0.00208333]
def patterns(S):
    out=[]
    for i in range(8):
        isi=pats_isi[i*4+1:(i+1)*4]
        t=np.concatenate([[0],np.cumsum(isi)])/0.025*S
        out.append(t)
    return out
def response(K,Ls,w,t_spikes):
    n=max(len(K[L]) for L in Ls)+int(max(t_spikes)/DT)+2
    R=np.zeros(n)
    for k,L in enumerate(Ls):
        for tj in t_spikes:
            s=int(round(tj/DT)); kk=K[L]; R[s:s+len(kk)]+=w[k]*kk
    return R
def margin(K,Ls,w,pats):
    P=[response(K,Ls,w,p).max() for p in pats]
    return (P[0]-max(P[1:]))/P[0], P
def analyze(tau,D,spans=(25,50,100,200,480),Lmax=100,Rmin_ratio=86/20):
    K=kernels(tau,D,Lmax)
    pk=np.array([0]+[K[L].max() for L in range(1,Lmax+1)])
    tp=np.array([0]+[K[L].argmax()*DT for L in range(1,Lmax+1)])
    fw=[0]
    for L in range(1,Lmax+1):
        a=np.where(K[L]>=K[L].max()/2)[0]; fw.append((a[-1]-a[0])*DT)
    fw=np.array(fw)
    res={'tau':tau,'D':D,'delta_ms':float((tp[Lmax]-tp[1])/(Lmax-1)*1000),'fwhm1_ms':float(fw[1]*1000),'fwhm50_ms':float(fw[min(50,Lmax)]*1000),'amp50_rel':float(pk[min(50,Lmax)]/pk[1]),'spans':{}}
    for S in spans:
        S=S/1000; pats=patterns(S); t=pats[0]
        target=t[3]+tp[1]
        Ls=[];ok=True;resid=[]
        for k in range(3):
            need=target-t[k]
            L=int(np.argmin(np.abs(tp[1:]-need)))+1
            if abs(tp[L]-need)>0.5*(tp[2]-tp[1])+1e-9 and L==Lmax: ok=False
            Ls.append(L); resid.append(tp[L]-need)
        Ls.append(1)
        w_eq=[min(pk[1]/pk[L],Rmin_ratio) for L in Ls]
        m_eq,_=margin(K,Ls,[1]*4,pats)
        m_nm,_=margin(K,Ls,w_eq,pats)
        # oracle around
        best=(-9,None)
        rng=[range(max(1,L-3),min(Lmax,L+3)+1) for L in Ls[:3]]
        for combo in itertools.product(*rng):
            LL=list(combo)+[1]; ww=[min(pk[1]/pk[L],Rmin_ratio) for L in LL]
            m,_=margin(K,LL,ww,pats)
            if m>best[0]: best=(m,LL)
        res['spans'][int(round(S*1000))]={'feasible':ok,'L':Ls,'resid_ms':[round(r*1000,2) for r in resid],'fwhm_longest_ms':round(fw[Ls[0]]*1000,1),'margin_equalRs':round(m_eq,4),'margin_ampnorm':round(m_nm,4),'oracle':round(best[0],4),'oracle_L':best[1]}
    return res
if __name__=='__main__':
    tau=float(sys.argv[1]); D=float(sys.argv[2])
    print(json.dumps(analyze(tau,D)))
