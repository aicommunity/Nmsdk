import numpy as np, json, model as m, evalset as e, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
S=0.025; pats=m.patterns(S)
out={}
def branch_syn(Ls,Rs,inh=None):
    syn=[(L,1,R) for L,R in zip(Ls,Rs)]
    if inh: syn+= [(L+1,-1,inh) for L in Ls]
    return syn
# Baseline C1e9 (Console rate 2000 Hz)
pb=m.base(f=2000,Tw=0.4)
tpk,apk,fw=m.peak_table(pb,20)
Lphys=m.sync_L(tpk,pats[0])
for name,Ls,Rs,inh in [('C1e9_trained_L13_11_7_1',[13,11,7,1],[2e7,2e7,2e7,8.6e7],None),
                       ('C1e9_trained_nextseg',[13,11,7,1],[2e7,2e7,2e7,8.6e7],8.6e7),
                       ('C1e9_island_L7_6_4_1',[7,6,4,1],[2e7,2e7,2e7,8.6e7],None),
                       ('C1e9_island_nextseg',[7,6,4,1],[2e7,2e7,2e7,8.6e7],8.6e7),
                       ('C1e9_physsync',Lphys,m.amp_eq(apk,Lphys),None)]:
    n=max(Ls)+(1 if inh else 0)
    P=[m.run(pb,n,branch_syn(Ls,Rs,inh),[list(pt)])[0,0] for pt in pats]
    out[name]=dict(L=Ls,peaks=[round(x,5) for x in P],m8=round(m.margin(P),4))
    print(name,out[name])
# carry-over: sequence of 8 trials, ITI from list; report start potential of each trial (no spikes), nextseg island
for name,p,Ls,Rs,inh in [('C1e9_island_nextseg',pb,[7,6,4,1],[2e7,2e7,2e7,8.6e7],8.6e7)]:
    for ITI in (0.5,1.5,6.0):
        q=dict(p); q['ITI']=ITI; q['Tw']=0.4; q=m.P(q)
        r=m.run(q,max(Ls)+1,branch_syn(Ls,Rs,inh),[list(pt) for pt in pats])
        out[f'{name}_ITI{ITI}']=dict(start=[float('%.4g'%x) for x in r[:,2]],peaks=[round(x,5) for x in r[:,0]])
        print(name,'ITI',ITI,out[f'{name}_ITI{ITI}'])
# traces of the inh tail for single target trial (island nextseg), long window
q=m.P(dict(pb)); q['Tw']=2.0
tr=m.run(q,8,branch_syn([7,6,4,1],[2e7,2e7,2e7,8.6e7],8.6e7),[list(pats[0])],mode=1)
t=tr[:,1]; v=tr[:,2]
for tt in (0.1,0.5,1.0,1.5,2.0):
    i=np.argmin(abs(t-tt)); print('tail t=%.1f s: %.4g'%(tt,v[i]))
out['tail_island_nextseg']={str(tt):float(v[np.argmin(abs(t-tt))]) for tt in (0.1,0.25,0.5,1.0,1.5,2.0)}
json.dump(out,open('../data/run_base.json','w'),indent=1)
np.save('../data/tail_base.npy',np.c_[t,v])
