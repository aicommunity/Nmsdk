"""Adversarial verifier fixtures; external simulator/gates are mocked."""
from pathlib import Path
import sys, json, tempfile, importlib.util, time, io, contextlib
from unittest.mock import patch
ROOT=next(p for p in Path(__file__).resolve().parents if (p / ".gitmodules").exists())
OUT=ROOT/'build/audit-review-20260924/research'
OUT.mkdir(parents=True, exist_ok=True)
sys.dont_write_bytecode = True
S=ROOT/'Bin/Configs/SpikeSamples/StructTrain/scripts'
sys.path.insert(0,str(S))
import posttune_verify as pv
spec=importlib.util.spec_from_file_location('phase9_review', S.parent/'SelectivityAsymRm/scripts/phase9_preinh_bc_gate.py')
p9=importlib.util.module_from_spec(spec);spec.loader.exec_module(p9)

def xml(tipr='2 3 4 5', need='0', fixed='1'):
    return '<root>'+''.join(f'<{k}>{v}</{k}>' for k,v in {'TipSynapseResistance':tipr,'IsNeedToTrain':need,'FixedLTZThreshold':fixed,'LTZThreshold':fixed,'DendriteLength':'1 1 1 1','ResistanceMin':'20000000','EnablePostTrainTuning':'1','EnablePostTrainMidThreshold':'1','PostTrainTipResistanceMode':'4','PostTrainSilentThreshold':'1','IterationGap':'1','AutoScaleIterationGap':'1'}.items())+'</root>'

results={}
def case_fixture(name, train_status='done', snapshot='20000000 30000000 40000000 90000000', reverted='1', final='30000000 40000000 50000000 100000000', need='0', fires='10000000'):
    with tempfile.TemporaryDirectory(dir=OUT) as td:
        base=Path(td); root=base/'case'; gold=base/'gold'; rd=base/'run'
        for d in (root/'Train',root/'Test',gold/'Test',rd/'Train',rd/'Test'):d.mkdir(parents=True)
        for side in ('Train','Test'):
            (root/side/'Parameters_00.xml').write_text(xml(final,need),encoding='utf-8')
        (gold/'Test'/'Parameters_00.xml').write_text(xml(),encoding='utf-8')
        (root/'Test'/'posttune_complete.flag').write_text('mid=0.05 landscape_ok=1 inference=1 result=1\n',encoding='utf-8')
        if snapshot is not None:
            (root/'Train'/'posttune_complete.flag').write_text(f'mid=1 landscape_ok=1 inference=0 result=1 search_reverted={reverted}\ntipr={final}\ntipr_snapshot={snapshot}\n',encoding='utf-8')
        case={**pv.CASES[name],'root':root,'gold':gold}
        gate=pv.GateResult(fires,'ok=1 n=8 acc=8',0,None,time.time(),True)
        with patch.dict(pv.CASES,{name:case}), patch.object(pv,'soft_cold_reset_train'),patch.object(pv,'wait_need0',return_value=train_status),patch.object(pv,'flush_posttune_artifacts',return_value='none'),patch.object(pv,'run_gate',return_value=gate),contextlib.redirect_stdout(io.StringIO()):
            row=pv.run_case(name,run_dir=rd)
        return {k:row[k] for k in ('row_fail','train_status','mid_source','tipr_vs_snapshot','tipr_class','fail_notes')}|{'verdict_exit':pv.verdict_rows([row]),'need':row['after']['IsNeedToTrain']}

results['search_revert_changed_own_snapshot']=case_fixture('br100_search')
results['search_no_train_flag_or_snapshot']=case_fixture('br100_search',snapshot=None,train_status='exited',need='1')
results['keep_arbitrary_weights_incomplete_train']=case_fixture('br100_keep',snapshot=None,train_status='incomplete',need='1',final='30000000 40000000 50000000 100000000')
results['empty_fires_not_rejected']=case_fixture('br25_on',snapshot=None,final='20000000 20000000 20000000 86000000',fires='')
results['nonfinite_numeric_equal']=pv.tipr_close([float('nan')]*4,[1,2,3,4])
results['nonfinite_negative_mid_cpp']=pv.mid_source_of({'mid':'-inf','inference':'1','landscape_ok':'1','result':'1'},'1')
with tempfile.TemporaryDirectory(dir=OUT) as td:
    root=Path(td);train=root/'Train';test=root/'Test';train.mkdir();test.mkdir()
    (train/'Parameters_00.xml').write_text(xml('20000000 20000000 20000000 86000000'),encoding='utf-8')
    (test/'Parameters_00.xml').write_text(xml(),encoding='utf-8')
    flag=test/'posttune_complete.flag';flag.write_bytes((S.parent/'SelectivityAsymRm/EXP_span50ms_packA_gen_posttune/Test/posttune_complete.flag').read_bytes())
    old_bytes=flag.read_bytes()
    thr=p9.overlay_train_params(train,test)
    results['stale_test_flag_in_phase9']={'returned_threshold':thr,'flag_retained':flag.read_bytes()==old_bytes,'test_threshold':pv.get_tag((test/'Parameters_00.xml').read_text(),'FixedLTZThreshold'),'will_skip_fresh_inference':float(thr)<0.9,'reported_mid_source':pv.mid_source_of(pv.parse_flag_file(flag),thr),'fixture_source':'tracked Asym50 Test flag, last commit b8cef72 (2026-09-22)'}
with tempfile.TemporaryDirectory(dir=OUT) as td:
    train=Path(td);(train/'Parameters_00.xml').write_text(xml(need='1'),encoding='utf-8')
    (train/'posttune_tipr_live.txt').write_text('tipr=91 92 93 94\nL=9 8 7 1\n',encoding='utf-8')
    class Exited:
        def poll(self):return 9
    def start_proc(*args,**kwargs):
        kwargs['stdout'].close()
        return Exited()
    with patch.object(pv,'assert_disk_for_train'),patch.object(pv,'free_gib',return_value=100),patch.object(pv.subprocess,'Popen',side_effect=start_proc),patch.object(pv.time,'sleep'),contextlib.redirect_stdout(io.StringIO()):
        st=pv.wait_need0(train,1,train/'log',max_polls=1)
    t=(train/'Parameters_00.xml').read_text()
    results['stale_live_after_train_crash']={'train_status':st,'tipr':pv.get_tag(t,'TipSynapseResistance'),'lengths':pv.get_tag(t,'DendriteLength'),'need':pv.get_tag(t,'IsNeedToTrain')}
(OUT/'a16-boundary-fixtures.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
print(json.dumps(results,indent=2))
