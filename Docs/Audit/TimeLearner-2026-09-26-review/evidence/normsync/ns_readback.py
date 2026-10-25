#!/usr/bin/env python3
"""normsync stage1/2 readback: flags in Train/Test XML (+ PostTune audit records) for an e05 job dir."""
import sys,re,json,glob,os
KEYS=["ResyncAfterNormalization","ResyncAfterNormalizationCount","FreezeTipResistanceAfterFirstSync","NormalizationMode",
      "SyncCapacitanceTrim","DendriteCapacitance","OverrideMembraneCapacity","DefaultTimeStep"]
def tags(p):
    out={}
    try: t=open(p,encoding='utf-8',errors='replace').read()
    except Exception: return out
    for k in KEYS:
        m=re.findall(r'<%s\b[^>]*>([^<]*)</%s>'%(k,k),t)
        if m: out[k]=sorted(set(x.strip().replace('\n',' ')[:120] for x in m))
    return out
for jd in sys.argv[1:]:
    r={}
    try: r=json.load(open(jd+'/result.json'))
    except Exception: pass
    w=r.get('work') or (sorted(glob.glob(jd+'/work/*_work'))[-1:] or [''])[0]
    print('==',os.path.basename(jd.rstrip('/')),'console=',r.get('console',''),'work=',w)
    for sub in ('Train','Test'):
        for f in ('Parameters_00.xml','Model_00.xml'):
            print(' ',sub,f,tags(f'{w}/{sub}/{f}'))
    for ini in glob.glob(f'{w}/Train/Project.ini')+glob.glob(f'{w}/Test/Project.ini'):
        m=re.search(r'<DefaultTimeStep>(\d+)',open(ini,errors='replace').read()); print(' ',ini.split('/')[-2],'DefaultTimeStep',m and m.group(1))
    a=f'{w}/Train/TimeLearnerTrainingAudit.log'
    if os.path.exists(a):
        rs=set(); cnt=0; n=0; pt=0; pt_rs=set(); cap=set()
        for l in open(a,errors='replace'):
            n+=1
            m=re.search(r';resync_after_norm=(-?\d+)',l); m2=re.search(r';resync_count=(\d+)',l)
            if m: rs.add(m.group(1))
            if m2: cnt=max(cnt,int(m2.group(1)))
            if re.search(r'phase=(post|kPhasePostTune|3\b)',l,re.I):
                pt+=1
                if m: pt_rs.add(m.group(1))
            m3=re.search(r';sync_cap_trim=([^;]*)',l)
            if m3: cap.add(m3.group(1))
        print('  audit records',n,'resync_after_norm',sorted(rs),'max resync_count',cnt,'posttune records',pt,'posttune flag',sorted(pt_rs),'sync_cap_trim',sorted(cap)[:3])
    for k in ('final_L','test_L','train_valid','sep_margin','m_S4','m_S8','m8_iti6','m8_gate05','detection','done_be'):
        if k in r: print('  ',k,r[k])
