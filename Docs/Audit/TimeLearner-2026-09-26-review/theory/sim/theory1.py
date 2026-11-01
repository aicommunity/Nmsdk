"""Linear one-channel theory: y_p(t)=sum_k w_k sum_j h_k(t-t_j); synced taps d_k=t4-t_k.
Margin per foil vs kernel width (units of S). Gaussian kernels (ideal) and discrete-GS cascades."""
import numpy as np, json, model as m, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
S=1.0; pats=m.patterns(S); tgt=pats[0]; d=tgt[3]-tgt
x=np.linspace(-1.5,3.5,20001); dx=x[1]-x[0]
def resp(pt,kern):  # kern(t_rel_to_peak)
    y=np.zeros_like(x)
    for dk in d:
        for tj in pt: y+=kern(x-(tj+dk))
    return y.max()
def shift_foils(D):
    out=[]
    for j in (1,2):           # inner spikes (as in PLAN_2026-10-25): shift one inner spike
        for s in (-1,1):
            q=tgt.copy(); q[j]+=s*D; out.append(q)
    return out
def margins(kern):
    P0=resp(tgt,kern); per=[(P0-resp(p,kern))/P0 for p in pats[1:]]
    sh={D:min((P0-resp(q,kern))/P0 for q in shift_foils(D)) for D in (1/24,1/12,1/8,1/4)}
    return per,sh
sig=np.array([0.005,0.01,0.02,0.03,0.04,0.05,0.06,0.08,0.10,0.125,0.15,0.2,0.25,0.3])
res=[]
for s in sig:
    g=lambda t,s=s: np.exp(-t*t/(2*s*s))
    per,sh=margins(g); res.append((s,per,sh))
    print(f"sigma/S={s:.3f} foils="+" ".join(f"{v:+.3f}" for v in per)+f"  m8={min(per):+.3f}  shift:"+" ".join(f"{k:.3f}:{v:+.3f}" for k,v in sh.items()))
json.dump([[float(s),[float(v) for v in per],{str(k):float(v) for k,v in sh.items()}] for s,per,sh in res],open('../data/theory1_gauss.json','w'),indent=1)
fig,ax=plt.subplots(1,2,figsize=(12,4.5))
for i in range(7): ax[0].plot(sig,[r[1][i] for r in res],'-o',ms=3,label=f's{i+1}')
ax[0].plot(sig,[min(r[1]) for r in res],'k-',lw=2.5,label='min (m8)')
for a in ax: a.axhline(0.25,ls=':',c='gray'); a.axhline(0.10,ls='--',c='r'); a.set_xlabel(r'$\sigma/S$ (гауссово ядро)'); a.grid(alpha=.3)
ax[0].set_ylabel('sep margin'); ax[0].set_title('8 паттернов MatrixData, линейная схема, 1 канал'); ax[0].legend(fontsize=7,ncol=2)
for k in (1/24,1/12,1/8,1/4): ax[1].plot(sig,[r[2][k] for r in res],'-o',ms=3,label=f'сдвиг Δ=S·{k:.3f}')
ax[1].set_title('сдвиг одного внутреннего спайка (худший знак)'); ax[1].legend(fontsize=8)
for a in ax: a.set_ylim(-0.1,0.3)
plt.tight_layout(); plt.savefig('../fig1_linear_margin_vs_width.png',dpi=130)
