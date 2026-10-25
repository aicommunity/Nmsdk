# peak time of the soma kernel vs tip synapse resistance Rs (N1) and synapse count N (N0), segsim (E0-verified vs Console)
import numpy as np, model as M, sys, json
M.SIM='./segsim'
out=[]
def tpk(p,L,syns):
    tr=M.run(p,L,syns,[[0.0]],mode=1); t,v=tr[:,1],tr[:,2]; i=v.argmax(); return t[i]*1e3, v[i]+1  # ms, amplitude above rest(-1)+1(inh)
for name,C,Ls in [("tau0.75ms_E2E5",7.5e-11,[1,25,100,200,400]),("tau1.0ms_E4",1e-10,[1,100,200]),("tau10ms_class",1e-9,[1,10,25,51])]:
    p=M.base(Ce=C,Tw=0.25 if C<1e-9 else 0.8)
    for L in Ls:
        row=dict(cfg=name,C=C,L=L)
        for Rs in [1e6,5e6,2e7,4.4e7,8.6e7,4e8,2e9,1e10]:
            row[f"Rs{Rs:.0e}"]=tpk(p,L,[(L,1,Rs)])
        for N in [1,2,4,8]:
            row[f"N{N}"]=tpk(p,L,[(L,1,8.6e7)]*N)
        out.append(row)
        print(name,"L",L," ".join(f"{k}:{v[0]:.2f}" for k,v in row.items() if isinstance(v,tuple)),flush=True)
json.dump(out,open('rs_delay_sim.json','w'))
