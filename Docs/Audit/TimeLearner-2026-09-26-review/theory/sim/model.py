# NOTE: parameter f everywhere = integration steps per second (NMSDK DefaultTimeStep), dt = 1/f. It is NOT a spike rate.
"""Driver for segsim.c (NMSDK-faithful Branch/Classic segment neuron, one input channel)."""
import subprocess, numpy as np, os, functools
HERE=os.path.dirname(os.path.abspath(__file__)); SIM=os.path.join(HERE,'segsim')
ISI=[[0.000520833,0.00416667,0.00833333,0.0125],[0.000520833,0.0125,0.00833333,0.00416667],
     [0.000520833,0.00833333,0.00416667,0.0125],[0.000520833,0.00833333,0.00833333,0.00833333],
     [0.000520833,0.00104167,0.0114583,0.0125],[0.000520833,0.0125,0.0114583,0.00104167],
     [0.000520833,0.00208333,0.00208333,0.0208333],[0.000520833,0.0208333,0.00208333,0.00208333]]
def patterns(S=0.025):
    """8 MatrixData patterns, relative spike times (first spike at 0), scaled to span S."""
    return [np.concatenate([[0],np.cumsum(i[1:])])/0.025*S for i in ISI]
class P(dict):
    __getattr__=dict.get
def base(**kw):
    p=P(f=2000,Ce=1e-9,Rme=1e7,Ci=1e-9,Rmi=1e8,FBR=1e7,th=100.0,FG=2.0,td=0.001,ts=0.001,tp=0.001,ITI=0.0,Tw=0.4)
    p.update(kw); return p
def run(p,n,syns,trials,mode=0,off=0.002):
    inp=f"{n} {len(syns)}\n"+"".join(f"{a} {t} {r:.6g}\n" for a,t,r in syns)+f"{len(trials)}\n"
    inp+="".join(f"{len(tr)} "+" ".join(f"{x+off:.7f}" for x in tr)+"\n" for tr in trials)
    args=[SIM]+[str(p[k]) for k in ['f','Ce','Rme','Ci','Rmi','FBR','th','FG','td','ts','tp','ITI','Tw']]+[str(mode)]
    out=subprocess.run(args,input=inp,capture_output=True,text=True).stdout
    a=np.array(out.split(),float)
    return a.reshape(-1,4) if mode==0 else a.reshape(-1,3)
def kernel(p,L,typ=1,Rs=8.6e7):
    tr=run(p,L,[(L,typ,Rs)],[[0.0]],mode=1)
    return tr[:,1],tr[:,2]
def peak_table(p,Lmax,Rs=8.6e7):
    t=[];a=[];w=[]
    for L in range(1,Lmax+1):
        tt,v=kernel(p,L,1,Rs); i=v.argmax(); t.append(tt[i]); a.append(v[i])
        h=np.where(v>=v[i]/2)[0]; w.append(tt[h[-1]]-tt[h[0]])
    return np.array(t),np.array(a),np.array(w)
def sync_L(tpk,tgt):
    """choose L_k so kernel peak times align: tpk[L-1]-tpk[0] ~ t4-t_k"""
    Ls=[]
    for k in range(3):
        need=tgt[3]-tgt[k]; Ls.append(int(np.argmin(np.abs((tpk-tpk[0])-need)))+1)
    return Ls+[1]
def amp_eq(apk,Ls,Rbase=8.6e7,Rmin=2e7,Rmax=1e11):
    a1=apk[0]; return [float(np.clip(Rbase*apk[L-1]/a1,Rmin,Rmax)) for L in Ls]
def margin(peaks):
    peaks=np.asarray(peaks); return (peaks[0]-peaks[1:].max())/peaks[0]
