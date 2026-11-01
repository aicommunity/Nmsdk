#!/usr/bin/env python3
"""normsync stage1 comparison specs (ResyncAfterNormalization). usage: gen_nsr.py GROUP -> label\tjson lines"""
import json,sys
C="/home/user/normsync/build_rs/NeuroModelerConsole.rs1"
DL={"DynamicsLogHead":2000,"DynamicsLogEvery":50,"DynamicsLogComponentState":0}
OV={"OverrideMembraneCapacity":7.5e-11,"OverrideInhMembraneResistance":1e7,"OverrideInhSynapseResistance":8.6e7}
P={"E1":dict(span=100,maxdl=100,L_expect="51 43 26 1",ov={}),
   "E2":dict(span=100,maxdl=450,est=0.00025,L_expect="400 334 200 1",ov=OV),
   "E5":dict(span=50,maxdl=500,est=0.00025,L_expect="200 166 100 1",ov=OV)}
def spec(e,k,mode,flag,frz=False,tests=None,base=""):
    lab=f"NSR_{e}_{k[0]}_{mode}_f{flag}"+("_frz" if frz else "")
    s=dict(P[e]); s.update(label=lab,series="NSR",owner="normsync-2026-10-25",kind=k,mod="preinh",mode=mode,jitter=0.0,dlog=DL,console=C,
        exp=f"stage1 ResyncAfterNormalization={flag}{' +FreezeTipR' if frz else ''}; flag0 baseline {base}")
    s["lset"]={"ResyncAfterNormalization":[flag,"i"]}
    if frz: s["lset"]["FreezeTipResistanceAfterFirstSync"]=[1,"b"]
    if tests: s["tests"]=tests
    return lab+"\t"+json.dumps(s)
G={"A11":[spec("E1","classic","N1",1,base="E1_c_s1"),spec("E1","classic","N1",0,base="E1_c_s1 (bit-identity check)"),spec("E1","branch","N1",1,base="E1_b_s1")],
   "B11":[spec("E2","classic","N1",1,base="E2_c_s1"),spec("E5","classic","N1",1,base="NS_E5_c_N1"),spec("E2","classic","N0",1,base="NS_E2_c_N0"),
          spec("E5","classic","N0",1,base="NS_E5_c_N0"),spec("E1","classic","N1",1,frz=True,base="E1_c_s1"),spec("E1","classic","N1",2,base="E1_c_s1")],
   "B17":[spec("E1","branch","N1",0,base="E1_b_s1 (bit-identity check)"),spec("E1","branch","N1",2,base="E1_b_s1"),spec("E2","branch","N1",1,base="E2_b_s1"),
          spec("E5","branch","N1",1,base="A0_E5_b_dbg/A1"),spec("E1","branch","N0",1,base="NSR_E1_b_N0_f0"),spec("E1","branch","N0",0,base="-"),
          spec("E5","branch","N0",1,base="NSR_E5_b_N0_f0"),spec("E5","branch","N0",0,base="-"),spec("E1","branch","N1",1,frz=True,base="E1_b_s1")]}
if __name__=="__main__": print("\n".join(G[sys.argv[1]]))
