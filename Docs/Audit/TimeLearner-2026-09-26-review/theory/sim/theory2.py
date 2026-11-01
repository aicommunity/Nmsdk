"""(a) ideal (dispersionless) delays + PSP k(t)=biexp(tau_s,tau_m) [- beta*undershoot]: linear margins.
   (b) coincidence-gated chain (segment threshold) on the same single channel."""
import numpy as np, json, model as m, evalset as e, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
S=1.0; pats=m.patterns(S); tgt=pats[0]; d=tgt[3]-tgt
x=np.linspace(-0.5,3.0,14001)
def biexp(t,ts,tm):
    t=np.maximum(t,0); k=np.exp(-t/tm)-np.exp(-t/ts) if ts<tm*0.999 else (t/tm)*np.exp(1-t/tm)
    return k
def mk(ts,tm,beta=0.0,th=None):
    tpk=x[np.argmax(biexp(x,ts,tm))]
    def k(t):
        v=biexp(t+tpk,ts,tm); v=v/ v.max() if v.max()>0 else v
        if beta>0:
            u=biexp(t+tpk,tm,th); v=v-beta*u/u.max()
        return v
    return k
_norm={}
def resp(pt,k):
    y=np.zeros_like(x)
    for dk in d:
        for tj in pt: y+=k(x-(tj+dk))
    return y.max()
def margins(k):
    P0=resp(tgt,k); m8=min((P0-resp(p,k))/P0 for p in pats[1:])
    s4=min((P0-resp(q,k))/P0 for q in e.foils_shift(tgt,0.25)); s8=min((P0-resp(q,k))/P0 for q in e.foils_shift(tgt,0.125))
    return m8,s4,s8
TM=[0.01,0.02,0.03,0.05,0.07,0.1,0.15,0.2,0.3]; TS=[0.002,0.01,0.02,0.04]
grid={}
for ts in TS:
    for tm in TM:
        if ts>=tm: continue
        grid[(ts,tm)]=margins(mk(ts,tm)); print('ts',ts,'tm',tm,'m8 %.3f s4 %.3f s8 %.3f'%grid[(ts,tm)])
und={}
for beta in (0.0,0.2,0.4,0.6):
    for th in (0.1,0.3):
        und[(beta,th)]=margins(mk(0.01,0.1,beta,th)); print('undershoot tm=0.1 beta',beta,'th',th,'m8 %.3f s4 %.3f s8 %.3f'%und[(beta,th)])
json.dump({'grid':{f'{a}_{b}':v for (a,b),v in grid.items()},'undershoot':{f'{a}_{b}':v for (a,b),v in und.items()}},open('../data/theory2_psp.json','w'),indent=1)
fig,ax=plt.subplots(1,2,figsize=(12,4.3))
for ts in TS:
    tms=[tm for tm in TM if tm>ts]
    ax[0].plot(tms,[grid[(ts,tm)][1] for tm in tms],'-o',ms=3,label=f'τs/S={ts}')
    ax[1].plot(tms,[grid[(ts,tm)][0] for tm in tms],'-o',ms=3,label=f'τs/S={ts}')
for a,tt in zip(ax,['сдвиг S/4 (идеальные задержки)','8 паттернов MatrixData (идеальные задержки)']):
    a.axhline(0.1,ls='--',c='r'); a.axhline(0.25,ls=':',c='gray'); a.set_xscale('log'); a.set_xlabel(r'$\tau_m/S$'); a.set_title(tt); a.grid(alpha=.3); a.legend(fontsize=8); a.set_ylim(-0.15,0.3)
ax[0].set_ylabel('sep margin'); plt.tight_layout(); plt.savefig('../fig3_psp_shape_ideal_delay.png',dpi=130)

# (b) gate chain: sites k=1..4 (tap k must see spike t_k); site1 fires on any spike; site k fires if the wave from site k-1
# (fired at time a, arriving at a+(t_k-t_{k-1})) coincides with a local spike: u = k(t-a')+k(t-tj) >= theta (2-input sum).
def gate_chain(pt,tm,theta=1.6,ts=0.002):
    kk=lambda t: biexp(np.atleast_1d(t)+0.0,ts,tm)
    tt=np.linspace(0,10*tm+0.01,4001); kn=biexp(tt,ts,tm); kn=kn/kn.max()
    def coinc(dt):  # peak of k(t)+k(t-dt)
        sh=np.interp(tt-abs(dt),tt,kn,left=0); return (kn+sh).max()
    best=0
    for a0 in pt:                      # chain started by any spike
        a=a0; ok=1
        for k in range(1,4):
            arr=a+(tgt[k]-tgt[k-1])
            c=max(coinc(arr-tj) for tj in pt)
            if c>=theta: a=arr+0; ok+=1
            else: break
        best=max(best,ok)
    return best
rows=[]
for tm in (0.01,0.02,0.04,0.08,0.15,0.3):
    P0=gate_chain(tgt,tm); Pf=[gate_chain(p,tm) for p in pats[1:]]
    s4=max(gate_chain(q,tm) for q in e.foils_shift(tgt,0.25)); s8=max(gate_chain(q,tm) for q in e.foils_shift(tgt,0.125)); s24=max(gate_chain(q,tm) for q in e.foils_shift(tgt,1/24))
    rows.append((tm,P0,Pf,s4,s8,s24)); print('gate tm',tm,'target stages',P0,'foils',Pf,'shift S/4,S/8,S/24 max stages',s4,s8,s24)
json.dump(rows,open('../data/theory2_gate.json','w'))
