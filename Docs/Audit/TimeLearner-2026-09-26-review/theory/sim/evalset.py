import numpy as np, model as m
def foils_shift(tgt,D):
    out=[]
    for j in (1,2):
        for s in (-1,1):
            q=tgt.copy(); q[j]+=s*D; out.append(np.sort(q-min(0,q.min())))
    return out
def trace_sum(p,parts,pt):
    """parts: list of (n,syns) independent dendrites (Classic); returns summed soma trace"""
    y=None
    for n,syns in parts:
        tr=m.run(p,n,syns,[list(pt)],mode=1)[:,2]
        y=tr if y is None else y+tr
    return y
def evaluate(p,S,Ls,Rs,topo='classic',inh=None,shifts=(1/4,1/8)):
    """inh: None or (dL, Rs_inh_list) -> inh synapse at L_k+dL on the inh chain of the same dendrite."""
    pats=m.patterns(S); tgt=pats[0]
    def parts():
        if topo=='classic':
            pr=[]
            for k,(L,R) in enumerate(zip(Ls,Rs)):
                syn=[(L,1,R)]; n=L
                if inh: Li=L+inh[0]; syn.append((Li,-1,inh[1][k])); n=max(n,Li)
                pr.append((n,syn))
            return pr
        syn=[(L,1,R) for L,R in zip(Ls,Rs)]; n=max(Ls)
        if inh:
            for k,L in enumerate(Ls): syn.append((L+inh[0],-1,inh[1][k])); n=max(n,L+inh[0])
        return [(n,syn)]
    pr=parts()
    pk=lambda pt: trace_sum(p,pr,pt).max()
    P=[pk(pt) for pt in pats]
    out={'m8':m.margin(P),'per':[(P[0]-x)/P[0] for x in P[1:]],'P0':P[0]}
    for D in shifts:
        out[f'shift{D:.3f}']=min((P[0]-pk(q))/P[0] for q in foils_shift(tgt,D*S))
    return out
