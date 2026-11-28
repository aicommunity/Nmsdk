"""Validate sealed node-recovery controls on .15 through shared evidence helpers."""
from __future__ import annotations
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import sys
import traceback

def require(value,reason):
    if not value:raise RuntimeError(reason)
def read(path):return json.loads(path.read_bytes())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def module(path,expected,name):
    path=path.resolve(strict=True);require(sha(path)==expected,'analysis_dependency_changed')
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
def write(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')

def analyze_case(case,metadata,folder,protocol,helpers,events,canonical):
    frequency=case['frequency_hz'];gap=case['gap_ms']/1000.
    require(metadata['kind']=='axone_recovery_diagnostic' and metadata['schema_version']==1 and
            metadata['id']==case['id'] and metadata['frequency_hz']==frequency and metadata['gap_ms']==case['gap_ms'] and
            metadata['capacity_f']==case['capacity_f'] and metadata['lt_time_constant_s']==case['lt_time_constant_s'] and
            metadata['window_s']==.25,'recovery_case_identity_mismatch')
    identity=metadata['axon_identity_before']
    require(identity['valid'] is True and identity['diagnostics']==[] and
            identity['sha256']==canonical(identity['model']),'unverified_recovery_identity')
    nodes={node['path']:node for node in identity['model']['nodes']}
    require(len(nodes)==len(identity['model']['nodes']) and all(int(node['frequency_hz'])==frequency for node in nodes.values()),
            'recovery_descendant_clock_mismatch')
    for name in ('ExcChannel','InhChannel'):
        require(helpers.scalar(nodes['$.Soma.'+name],'Capacity','binary64')==case['capacity_f'],'recovery_channel_capacity_mismatch')
    zone=nodes['$.LTZone']
    for name,kind,value in (('Threshold','binary64',.02),('ThresholdOff','binary64',0.),('PulseAmplitude','binary64',1.),
                            ('TimeConstant','binary64',case['lt_time_constant_s']),('UseLTZIntegtation','boolean',True),('UseSpikeStabilizer','boolean',True)):
        require(helpers.scalar(zone,name,kind)==value,'recovery_lt_profile_mismatch:'+name)
    phases=metadata['phases'];names=protocol['phase_order']
    require(len(phases)==4 and [phase['phase'] for phase in phases]==names,'recovery_phase_inventory_mismatch')
    observed={};records=[]
    for phase,expected_count in zip(phases,protocol['source_count_assertions']):
        name=phase['phase'];stem=folder/(case['id']+'_'+name)
        require(read(stem.with_suffix('.json'))==phase and phase['complete'] is True and phase['error']=='' and
                phase['expected_source_events']==expected_count and phase['axon_identity_after']==identity,'incomplete_or_changed_recovery_phase')
        trace=helpers.trace(stem.with_suffix('.csv'),frequency,.25,protocol['recorded_columns'])
        inputs=helpers.checked_events(trace['source'],phase['source_events'],frequency,events)
        outputs=helpers.checked_events(trace['output'],phase['output_events'],frequency,events)
        require(len(inputs)==expected_count and all(event['peak']==1 and not event['right_censored'] for event in inputs),'recovery_source_control_failed')
        if inputs:
            first=.01+gap if name=='second_only' else .01
            require(abs(inputs[0]['onset_tick']/frequency-first)<=2/frequency,'recovery_actual_first_source_time_mismatch')
            require(all(abs(event['width_s']-.001)<=2/frequency for event in inputs),'recovery_actual_source_width_mismatch')
            if name=='pair':require(abs((inputs[1]['onset_tick']-inputs[0]['onset_tick'])/frequency-gap)<=2/frequency,'recovery_actual_source_gap_mismatch')
            require(phase['association_status']=='assessed','recovery_nonempty_pairing_not_assessed')
            association=helpers.assignment(phase['temporal_association'],inputs,outputs,frequency)
        else:
            require(phase['temporal_association'] is None and phase['association_status']=='not_assessed_without_input_events',
                    'silent_control_has_fabricated_assignment')
            association=None
        observed[name]={'source_events':inputs,'output_events':outputs,'association':association,
                        'csv_sha256':sha(stem.with_suffix('.csv')),'metadata_sha256':sha(stem.with_suffix('.json'))}
        records.append(stem.with_suffix('.json').name)
    clean=(not observed['silent']['output_events'] and
           len(observed['first_only']['output_events'])==len(observed['second_only']['output_events'])==1 and
           observed['pair']['association']['complete_one_to_one'] and
           all(not event['right_censored'] for phase in observed.values() for event in phase['output_events']))
    normalized=copy.deepcopy(identity['model'])
    for node in normalized['nodes']:
        if node['path'] in ('$.Soma.ExcChannel','$.Soma.InhChannel'):del node['parameters']['Capacity']
        if node['path']=='$.LTZone':del node['parameters']['TimeConstant'];node['class']='declared_recovery_ltzone'
        if node['path']=='$':del node['parameters']['LTZoneClassName']
    return {'id':case['id'],'capture_valid':True,'frequency_hz':frequency,'gap_ms':case['gap_ms'],
            'capacity_f':case['capacity_f'],'lt_time_constant_s':case['lt_time_constant_s'],
            'model_sha256':identity['sha256'],'nonfactor_model_sha256':canonical(normalized),'phases':observed,
            'operational_clean_pair':clean,
            'second_control_minus_pair_source_ticks':observed['second_only']['source_events'][0]['onset_tick']-observed['pair']['source_events'][1]['onset_tick'],
            'metadata_sha256':sha(folder/(case['id']+'.json'))}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('data-root','gate-pointer','archive-adapter','conduction-helper','event-helper','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    for name in ('archive-id','archive-adapter-sha256','conduction-helper-sha256','event-helper-sha256'):
        parser.add_argument('--'+name,required=True)
    args=parser.parse_args();sys.dont_write_bytecode=True
    require(os.name=='nt' and socket.gethostname().upper()=='AQUA3060','server15_required')
    adapter=module(args.archive_adapter,args.archive_adapter_sha256,'axon_recovery_archive')
    data,_,_=adapter.root_identity(args.data_root,args.archive_id);output=args.output.resolve()
    require(output.is_relative_to(data/'Experiments') and not output.exists(),'fresh_recovery_analysis_output_required')
    output.mkdir(parents=True,exist_ok=False)
    result={'kind':'axone_recovery_matrix_analysis','schema_version':1,'analysis_complete':False,
            'producer_sha256':sha(Path(__file__)),'archive_id':args.archive_id,'scientific_verdict':None,
            'model_executed':False,'training':False,'full_P1_accepted':False,'carrier_selected':False}
    try:
        adapter.verify(argparse.Namespace(data_root=data,archive_id=args.archive_id,verify_pointer=args.gate_pointer,
                                         maximum_bytes=4*1024**3,maximum_files=20000))
        pointer=read(args.gate_pointer);status=pointer['status']
        require(status['role']=='native' and status['validity']=='valid' and status['process_closure']=='bound_windows_job_closed' and
                status['process_evidence']['runtime_provenance']=='loaded_files_captured' and
                status['process_evidence']['cooperative_capture']=='completed','valid_captured_recovery_gate_required')
        gate=(data/pointer['attempt_relative']).resolve(strict=True)
        verdict=read(gate/'result.json');protocol=read(gate/'source-protocol.json');runtime=read(gate/'runtime.json')
        require(protocol['kind']=='axone_recovery_diagnostic_contract' and protocol['schema_version']==1 and
                verdict['expected_cases']==len(protocol['cases'])==72,'full_recovery_matrix_required')
        source=Path(runtime['windows_source_root']).resolve(strict=True);sys.path.insert(0,str(source))
        from Scripts.StructTrain.TimeLearner.runtime import source_closure
        from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256
        closure=source_closure(source);require(closure==runtime['source_closure'],'source_closure_changed')
        helpers=module(args.conduction_helper,args.conduction_helper_sha256,'axon_recovery_shared_conduction')
        events=module(args.event_helper,args.event_helper_sha256,'axon_recovery_shared_events')
        folder=gate/'native-gate/native/AxoneRecoveryDiagnostic';failed=set(verdict['gate']['inventory']['failed_test_ids'])
        expected_json={case['id']+'.json' for case in protocol['cases']}
        expected_phases={case['id']+'_'+name for case in protocol['cases'] for name in protocol['phase_order']}
        require({p.name for p in folder.glob('*.json')}.issubset(expected_json|{name+'.json' for name in expected_phases}) and
                {p.stem for p in folder.glob('*.csv')}.issubset(expected_phases),'unexpected_recovery_artifact')
        rows=[]
        for case in protocol['cases']:
            try:
                row=analyze_case(case,read(folder/(case['id']+'.json')),folder,protocol,helpers,events,canonical_model_sha256)
                row['native_assertions_passed']=case['expected_test_id'] not in failed
                if not row['native_assertions_passed']:row.update(capture_valid=False,reason='native_case_assertion_failure')
            except (ValueError,RuntimeError,OSError,KeyError,TypeError,IndexError) as error:
                row={'id':case['id'],'capture_valid':False,'reason':str(error)}
            rows.append(row)
        checks={}
        for row in rows:
            if row['capture_valid']:checks.setdefault(row['frequency_hz'],set()).add(row['nonfactor_model_sha256'])
        factor_scope=all(len(values)==1 for values in checks.values()) and len(checks)==2
        require(source_closure(source)==closure,'analysis_changed_source_files')
        result.update(source_commit=verdict['source_commit'],source_archive_manifest_sha256=pointer['manifest']['sha256'],
            rows=rows,nonfactor_physics_unchanged=factor_scope,analysis_complete=all(row['capture_valid'] for row in rows) and factor_scope,
            failed_native_test_ids=sorted(failed),dependency_sha256={name:getattr(args,name+'_sha256') for name in ('archive_adapter','conduction_helper','event_helper')},
            operational_pair_criterion='Silent output=0, each isolated pulse output=1, pair has complete unambiguous shared temporal association, no censored output.',
            claim_scope='Observed pair response and matched controls on one node; no causal assignment, chain conduction, exact physiological refractory period, learning or final carrier acceptance.')
    except BaseException as error:result.update(error=str(error),traceback=traceback.format_exc())
    write(output/'result.json',result)
    print(json.dumps({'analysis_complete':result['analysis_complete'],'cases':len(result.get('rows',[])),
        'invalid':[row['id'] for row in result.get('rows',[]) if not row['capture_valid']],
        'nonfactor_physics_unchanged':result.get('nonfactor_physics_unchanged'),'error':result.get('error')}))
    return 0 if result['analysis_complete'] else 1

if __name__=='__main__':raise SystemExit(main())
