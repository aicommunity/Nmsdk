import json, sys, statistics as st, math, collections, re
runs=[]
for f in sys.argv[1:]: runs+=json.load(open(f))
G=collections.defaultdict(list); R=collections.defaultdict(list)
for r in runs:
    if not r.get('span'): continue
    S=round(r['span']*1000); key=(r['trainer'], 'N'+str(r['mode']), S)
    R[key].append(r)
    for p in r['pairs']:
        G[key].append(p)
print("trainer mode S_ms | runs pairs | Rs-only pairs: med|dD| p90|dD| max|dD| ms, med|dD|/tol, med|dD|/S | N-change pairs: n med|dD| p90 | med|ln Rs ratio|")
for key in sorted(G, key=lambda k:(k[0],k[1],k[2])):
    ps=G[key]; rs=[p for p in ps if p['dN']==0]; ns=[p for p in ps if p['dN']!=0]
    def q(v,a): v=sorted(v); return v[min(len(v)-1,int(a*len(v)))] if v else float('nan')
    a=[abs(p['dDelay_ms']) for p in rs]; b=[abs(p['dDelay_ms']) for p in ns]
    tol=[abs(p['dDelay_ms'])/p['tol_ms'] for p in rs if p['tol_ms']>0]
    lr=[abs(math.log(p['ratio'])) for p in rs if p['ratio']>0]
    print(f"{key[0]:7s} {key[1]} {key[2]:4d} | {len(R[key]):3d} {len(ps):5d} | n={len(a)} {q(a,.5):.3f} {q(a,.9):.3f} {max(a) if a else float('nan'):.3f} | {q(tol,.5):.3f} {q(a,.5)/key[2]:.5f} | n={len(b)} {q(b,.5):.3f} {q(b,.9):.3f} | {q(lr,.5):.3f}")
