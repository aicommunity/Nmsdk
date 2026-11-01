import numpy as np, json, model as m
def fastset(S,c=0.007,f=20000,Lcap=230):
    k=S/0.025; tau=c*S
    return m.base(f=f,Ce=tau/1e7,Ci=tau/1e7,Rmi=1e7,FBR=1e7,td=0.001*k,ts=0.0005*k,tp=0.0005*k,Tw=0.02*k+S+Lcap*tau*1.3), tau
S=0.025; pats=m.patterns(S); out={}
p,tau=fastset(S); Ls=[197,164,98,1]; Rs=[24.1e6,26.0e6,32.0e6,86e6]
syn=[(L,1,R) for L,R in zip(Ls,Rs)]
P0=m.run(p,max(Ls),syn,[list(pats[0])])[0,0]
th=0.97*P0
for ITIs in (0.0, 0.5, 1.0, 2.0, 4.0):
    q=m.P(dict(p)); q['th']=th; q['ITI']=ITIs*S; q['Tw']=1.5*S
    seq=[list(pats[i]) for i in (0,0,1,0,4,0,5,0)]
    r=m.run(q,max(Ls),syn,seq)
    out[str(ITIs)]=dict(period_over_S=(q['Tw']+q['ITI'])/S,start=[float('%.3g'%x) for x in r[:,2]],peaks=[round(x/P0,4) for x in r[:,0]],nspk=[int(x) for x in r[:,3]])
    print('ITI/S',ITIs,out[str(ITIs)])
# trace with spike for figure
q=m.P(dict(p)); q['th']=th; q['Tw']=4*S
tr=m.run(q,max(Ls),syn,[list(pats[0])],mode=1); np.save('../data/trace_fast_spike.npy',tr[:,1:])
q['th']=100; tr2=m.run(q,max(Ls),syn,[list(pats[0])],mode=1); np.save('../data/trace_fast_nospike.npy',tr2[:,1:])
out['P0']=P0; out['theta']=th
json.dump(out,open('../data/run_iti_fast.json','w'),indent=1)
