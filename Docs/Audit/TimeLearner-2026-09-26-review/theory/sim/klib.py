import numpy as np, model as m, evalset as e
def lib(p,Lmax,Rs=8.6e7):
    K=[None]
    for L in range(1,Lmax+1):
        K.append(m.kernel(p,L,1,Rs)[1])
    return K
def resp(Ks,w,pt,dt):
    n=max(len(k) for k in Ks)+int(max(pt)/dt)+3; y=np.zeros(n)
    for k,ww in zip(Ks,w):
        for t in pt:
            s=int(round(t/dt)); y[s:s+len(k)]+=ww*k
    return y.max()
def evalK(Ks,w,S,dt,shifts=(1/4,1/8)):
    pats=m.patterns(S); tgt=pats[0]
    P=[resp(Ks,w,pt,dt) for pt in pats]
    out={'m8':m.margin(P),'per':[(P[0]-x)/P[0] for x in P[1:]]}
    for D in shifts: out[D]=min((P[0]-resp(Ks,w,q,dt))/P[0] for q in e.foils_shift(tgt,D*S))
    return out
def sync(Ks,tgt,dt,cands):
    tp={c:Ks[c].argmax()*dt for c in cands}
    t1=tp[cands[0]]
    return [min(cands,key=lambda c: abs(tp[c]-t1-(tgt[3]-tgt[k]))) for k in range(3)]+[cands[0]]
