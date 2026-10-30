#!/usr/bin/env python3
"""normsync stage2 specs (SyncCapacitanceTrim, with ResyncAfterNormalization=1). usage: gen_nsc.py GROUP"""
import json,sys
sys.path.insert(0,"/home/user/normsync")
import gen_nsr as R
C=sys.argv[2] if len(sys.argv)>2 else "/home/user/normsync/build_rs2b/NeuroModelerConsole.rs2"
def spec(e,k,mode,trim,base=""):
    lab=f"NSC_{e}_{k[0]}_{mode}_t{trim}"
    s=dict(R.P[e]); s.update(label=lab,series="NSC",owner="normsync-2026-10-25",kind=k,mod="preinh",mode=mode,jitter=0.0,dlog=R.DL,console=C,
        exp=f"stage2 SyncCapacitanceTrim={trim} +Resync=1; compare {base}")
    s["lset"]={"ResyncAfterNormalization":[1,"i"],"SyncCapacitanceTrim":[trim,"i"]}
    return lab+"\t"+json.dumps(s)
G={"S11":[spec("E1","classic","N1",1,"NSR_E1_c_N1_f1")],
   "C11":[spec("E2","classic","N0",1,"NSR_E2_c_N0_f1"),spec("E5","classic","N0",1,"NSR_E5_c_N0_f1"),spec("E5","classic","N0",0,"NSR_E5_c_N0_f1 (rs2 bit-identity)")],
   "C17":[spec("E1","branch","N0",1,"NSR_E1_b_N0_f1"),spec("E5","branch","N0",1,"NSR_E5_b_N0_f1"),spec("E1","branch","N0",0,"NSR_E1_b_N0_f1 (rs2 bit-identity)")]}
if __name__=="__main__": print("\n".join(G[sys.argv[1]]))
