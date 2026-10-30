"""Линейная модель запаса селективности TimeLearner (matched filter на линии задержки).
Набор паттернов W10/W01, нормирован на span=1. Запуск: python3 timelearner_margin_model.py"""
import numpy as np
d=[0.000520833,0.00416667,0.00833333,0.0125,0.000520833,0.0125,0.00833333,0.00416667,0.000520833,0.00833333,0.00416667,0.0125,0.000520833,0.00833333,0.00833333,0.00833333,0.000520833,0.00104167,0.0114583,0.0125,0.000520833,0.0125,0.0114583,0.00104167,0.000520833,0.00208333,0.00208333,0.0208333,0.000520833,0.0208333,0.00208333,0.00208333]
pats=[np.cumsum([0]+d[i*4+1:(i+1)*4])/0.025 for i in range(8)]  # normalized to span=1
T=pats[0]
t=np.linspace(-0.5,4,9001)
def kern(x,tau):
    x=np.maximum(x,0)/tau
    return x*np.exp(1-x)
def resp(p,w,dly,taus):
    R=np.zeros_like(t)
    for k in range(4):
        for tj in p:
            R+=w[k]*kern(t-tj-dly[k],taus[k])
    return R.max()
def margin(tau0,disp=0.0,w=None,derr=None):
    w=np.ones(4) if w is None else np.asarray(w)
    dly=1.0-T + (0 if derr is None else np.asarray(derr))
    taus=tau0+disp*(1.0-T)
    P=[resp(p,w,dly,taus) for p in pats]
    return (P[0]-max(P[1:]))/P[0], int(np.argmax(P[1:]))+1
print("== equal taps, no dispersion: margin vs tau/span")
for tau in [0.005,0.01,0.02,0.04,0.06,0.08,0.12,0.2]:
    m,f=margin(tau); print(f"tau/span={tau:<6} margin={m:+.3f} worst_foil={f}")
print("== with dispersion tau_k = tau0 + c*d_k (tau0=0.02)")
for c in [0,0.05,0.1,0.2,0.4]:
    m,f=margin(0.02,c); print(f"c={c:<5} margin={m:+.3f} worst_foil={f}")
print("== amplitude imbalance (tau=0.04): tap k scaled")
for k in range(4):
  for s in [0.7,1.3]:
    w=np.ones(4); w[k]=s; m,f=margin(0.04,0,w); print(f"tap{k} x{s}: margin={m:+.3f} foil={f}")
print("== delay error within SyncTol (=1/24 span) worst case search, tau=0.04")
import itertools
tol=1/24
worst=(1,None)
for e in itertools.product([-tol,0,tol],repeat=3):
    m,f=margin(0.04,0,None,list(e)+[0])
    if m<worst[0]: worst=(m,e,f)
print("worst margin",worst)
for tau in [0.02,0.04,0.08]:
    rng=np.random.default_rng(0); ms=[]
    for _ in range(200):
        e=list(rng.uniform(-tol,tol,3))+[0]; ms.append(margin(tau,0,None,e)[0])
    ms=np.array(ms); print(f"tau={tau} random |err|<=tol: median margin={np.median(ms):+.3f} P(margin<0)={np.mean(ms<0):.2f}")
