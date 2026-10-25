# Superposition model of the trainer's per-dendrite peak measurement (NNeuronTimeLearner.cpp ~4290-4340):
# soma V(t) = sum_k A_k K_{L_k}(t - e_k); dendrite i peak = argmax V in [e_i+d_i-m, min(e_i+d_i+m, e_{i+1}+d_{i+1}-guard)].
# Lengths synced by kernel peak table; then amplitude of one other dendrite (or own) is changed by factor f
# (= a normalization step: N1 Rs ratio, N0 N->N+1) and the shift of the measured delay of dendrite i is recorded.
import numpy as np, model as M, json
M.SIM='./segsim'
import os
FACT=[float(x) for x in os.environ.get('FACT','0.5,0.67,1.5,2.0').split(',')]
TAG=os.environ.get('TAG','n0like')
cfgs=[("classic_tau10_S480",1e-9,0.48,0.020,0.028,0.01,60),("classic_tau10_S100",1e-9,0.10,0.00417,0.00583,0.01,30),
      ("classic_tau10_S50",1e-9,0.05,0.00208,0.00292,0.01,20),
      ("E2_tau0.75_S100",7.5e-11,0.10,0.00417,0.00583,0.00025,450),("E5_tau0.75_S50",7.5e-11,0.05,0.00208,0.00292,0.00025,450),
      ("E4_tau1.0_S100",1e-10,0.10,0.00417,0.00583,0.0005,250),("tau3.4_S480(c=0.007)",3.4e-10,0.48,0.020,0.028,0.003,250)]
res=[]
for name,C,S,tol,m,est,Lmax in cfgs:
    p=M.base(Ce=C,Tw=min(2.0,S+0.4))
    f=p.f; tk={}
    def K(L):
        if L not in tk:
            tr=M.run(p,L,[(L,1,8.6e7)],[[0.0]],mode=1); v=tr[:,2]-tr[0,2]; tk[L]=v/v.max()
        return tk[L]
    tpk=np.array([K(L).argmax()/f for L in range(1,Lmax+1)])
    e=np.array([0,1/6,1/2,1.0])*S
    Ls=[int(np.argmin(np.abs((tpk-tpk[0])-(e[3]-e[k]))))+1 for k in range(3)]+[1]
    n=int((S+0.4)*f); t=np.arange(n)/f
    def V(A):
        out=np.zeros(n)
        for k in range(4):
            ker=K(Ls[k]); s=int(round(e[k]*f)); ln=min(len(ker),n-s); out[s:s+ln]+=A[k]*ker[:ln]
        return out
    def meas(A):
        v=V(A); d=[]
        for i in range(4):
            de=(Ls[i]-1)*est; lo=e[i]+de-m; hi=e[i]+de+m
            if i<3:
                nd=(Ls[i+1]-1)*est; guard=min(0.002,max(1e-4,0.25*est)); hi=min(hi,e[i+1]+nd-guard)
            if hi<=lo+1e-9: hi=lo+0.01
            a,b=max(0,int(np.ceil(lo*f))),min(n-1,int(np.floor(hi*f)))
            b=max(b,a); j=a+int(np.argmax(v[a:b+1])); d.append(j/f-e[i])
        return np.array(d)
    Lsync=list(Ls); dseg=max(C*1e7-1/f,1e-6); q=max(1,int(round(tol/dseg)))
    shifts=[]; errs=[]; rng=np.random.default_rng(1)
    for trial in range(40):
        Ls=[max(1,Lsync[k]+int(rng.integers(-q,q+1))) for k in range(3)]+[1]
        A0=np.ones(4); d0=meas(A0); arr0=e+d0; errs.append(np.abs(arr0[:3]-arr0[3]).max()*1e3)
        for fct in FACT:
            for j in range(4):
                A=A0.copy(); A[j]*=fct; d=meas(A); arr=e+d
                for i in range(3):
                    if j==i: continue
                    shifts.append(abs(((arr[i]-arr[3])-(arr0[i]-arr0[3]))*1e3))
    Ls=Lsync; shifts=np.array(shifts); err0=[float(np.median(errs))]
    fw=[]
    for L in Ls[:3]:
        k=K(L); h=np.where(k>=0.5)[0]; fw.append((h[-1]-h[0])/f*1e3)
    r=dict(cfg=name,C=C,tau_ms=C*1e7*1e3,S_ms=S*1e3,tol_ms=tol*1e3,L=Ls,fwhm_ms=[round(x,1) for x in fw],err0_ms=[round(x,2) for x in err0],
           shift_med_ms=float(np.median(shifts)),shift_p90_ms=float(np.percentile(shifts,90)),shift_max_ms=float(shifts.max()),
           max_over_tol=float(shifts.max()/(tol*1e3)),max_over_S=float(shifts.max()/(S*1e3)),c=C*1e7/S)
    res.append(r); print(json.dumps(r),flush=True)
json.dump(res,open(f'window_shift_sim_{TAG}.json','w'),indent=1)
