import os
import numpy as np, sys, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from library import sim, patterns, DT
def classic(tau,D,S_ms,Ls,Rs=(8.6e7,)*4,T=None):
    pats=patterns(S_ms/1000)
    if T is None: T=S_ms/1000+max(Ls)*tau*1.6+10*tau+0.05
    P=[];Pl=[]
    for p in pats:
        tot=0; lin=0
        for L,rs in zip(Ls,Rs):
            tr=sim(L,[(L,rs,list(p))],tau,D,T); tot=tot+tr
        P.append(tot.max())
    return P
if __name__=='__main__':
    tau=float(sys.argv[1]);D=float(sys.argv[2]);S=float(sys.argv[3]);Ls=[int(x) for x in sys.argv[4].split(',')]
    Rs=[float(x) for x in sys.argv[5].split(',')] if len(sys.argv)>5 else [8.6e7]*4
    P=classic(tau,D,S,Ls,Rs)
    print(json.dumps({'P':[round(x,6) for x in P],'margin':round((P[0]-max(P[1:]))/P[0],4),'worst':int(np.argmax(P[1:]))+1}))
