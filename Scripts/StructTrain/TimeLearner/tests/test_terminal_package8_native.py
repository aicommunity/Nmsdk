"""Package8 DATA audit against declared real native component fixtures."""
import copy
import os
from pathlib import Path
import unittest

from ..learned_evidence import audit_learned_state
from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError, load, require

TERMINAL = {
    'ClassicN0DeadlineRestoresFullMeasuredModel','BranchN0DeadlineRestoresFullMeasuredModel',
    'ClassicN1DeadlineRestoresFullMeasuredModel','BranchN1DeadlineRestoresFullMeasuredModel',
    'ClassicExternalStopDoesNotRestore','BranchExternalStopDoesNotRestore',
    'ClassicCapacitanceStateAndWaveformAreRestored','BranchCapacitanceStateAndWaveformAreRestored',
    'ClassicInsufficientEditReservationDoesNotMutate','BranchInsufficientEditReservationDoesNotMutate',
    'ClassicFailedAttachmentRetainsOriginalModel','BranchFailedAttachmentRetainsOriginalModel'}
EXPECTED = ({'NativeTerminalSelection/'+name for name in TERMINAL} |
    {'NativeTerminalPlainPackage/'+topology+'Completed'+norm+'WithoutTransition'
     for topology in ('Classic','Branch') for norm in ('N0','N1')} |
    {'NativeTerminalCompositePackage/'+topology+mode+norm+'Stopped'
     for topology in ('Classic','Branch') for mode in ('Fixed','Window') for norm in ('N0','N1')} |
    {'NativeTerminalCompositePackage/'+topology+mode+'CompletedWithoutTransition'
     for topology in ('Classic','Branch') for mode in ('Fixed','Window')})


def _artifact(root, relative):
    require(type(relative) is str and relative and '\\' not in relative and ':' not in relative
            and not Path(relative).is_absolute() and '..' not in Path(relative).parts,'terminal_fixture_relative_path')
    original=root/relative;path=original.resolve(strict=True)
    require(path.is_relative_to(root.resolve()) and path.is_file() and not original.is_symlink(),
            'terminal_fixture_artifact')
    return path


def _packets(folder, prefix):
    packets={};traces={}
    if prefix is not None:
        require(type(prefix) is str and prefix and not any(c in prefix for c in '/\\:*?[]'),
                'terminal_fixture_primary_prefix')
        # Native source_graph.json is a distinct graph snapshot sharing this
        # prefix. Trial IDs are decimal suffixes; the summary still requires
        # every declared trial and rejects missing or contradictory primary.
        for path in sorted(folder.glob(prefix+'[0-9]*.json')):
            require(path.stem[len(prefix):].isdigit(),'terminal_fixture_unexpected_trial_name')
            packet=load(path);trial=packet['requested_specification']['trial_id']
            require(trial not in packets,'terminal_fixture_duplicate_primary')
            packets[trial]=packet;traces[trial]=_artifact(folder,path.with_suffix('.csv').name)
    return packets,traces


def _resign(value):
    value.pop('sha256',None);value['sha256']=canonical_model_sha256(value)


class NativeTerminalPackage8Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(os.environ['TIMELEARNER_NATIVE_TERMINAL_PACKAGE8']).resolve(strict=True)
        descriptors=list((cls.root/'native').glob('*_terminal_case.json'))
        descriptors+=list((cls.root/'native-composite').glob('*/terminal-case.json'))
        cls.cases={}
        for path in descriptors:
            row=load(path)
            require(set(row)=={'kind','schema_version','test_id','package','summary','primary_prefix','warm_folder'}
                    and row['kind']=='native_terminal_portable_case' and type(row['schema_version']) is int and row['schema_version']==1,
                    'terminal_fixture_descriptor')
            identity=row['test_id'];require(identity in EXPECTED and identity not in cls.cases,'terminal_fixture_unknown_or_duplicate_case')
            cls.cases[identity]=(path.parent,row)
            if row['warm_folder'] is not None:
                value=row['warm_folder']
                require(type(value) is str and value and not Path(value).is_absolute() and '..' not in Path(value).parts
                        and '\\' not in value and ':' not in value and (cls.root/value).resolve().is_relative_to(cls.root),
                        'terminal_fixture_warm_folder')
        require(len(EXPECTED)==28 and set(cls.cases)==EXPECTED,'terminal_fixture_declared_population_incomplete')

    def case(self, identity):
        folder,row=self.cases[identity]
        p=load(_artifact(folder,row['package']));s=load(_artifact(folder,row['summary']))
        packets,traces=_packets(folder,row['primary_prefix'])
        return p,s,packets,traces

    def restored(self):
        return next(name for name in sorted(self.cases) if 'ClassicN0Deadline' in name)

    def test_real_branch_muted_banks_require_explicit_scope_and_valid_native_links(self):
        from ..training_capacitance_witness import validate_graph_input_parameters
        p,_,_,_=self.case('NativeTerminalPlainPackage/BranchCompletedN0WithoutTransition')
        declaration=p['configuration']['model'];identity=p['neuron']['graph']['identity']
        self.assertTrue(declaration['allow_muted_input_baseline'])
        validate_graph_input_parameters(declaration,identity,p['trained_inputs'])
        strict=copy.deepcopy(declaration);strict['allow_muted_input_baseline']=False
        with self.assertRaisesRegex(EvidenceError,'stimulus_bank_mismatch'):
            validate_graph_input_parameters(strict,identity,p['trained_inputs'])
        for mutation in ('foreign_source','duplicate_link','wrong_slot'):
            changed=copy.deepcopy(identity)
            link=next(x for x in changed['model']['bindings'] if x['kind']=='stimulus_port' and
                      '.ExcSynapse' in x['target'] and x['target'].endswith(':Input'))
            if mutation=='foreign_source':link['source']='unowned-stimulus'
            elif mutation=='duplicate_link':changed['model']['bindings'].append(copy.deepcopy(link))
            else:link['slot']='1'
            with self.subTest(mutation=mutation),self.assertRaisesRegex(EvidenceError,'stimulus_bank_mismatch'):
                validate_graph_input_parameters(declaration,changed,p['trained_inputs'])

    def test_declared_28_native_boundaries(self):
        for identity in sorted(self.cases):
            with self.subTest(case=identity):
                p,s,packets,traces=self.case(identity)
                report=audit_learned_state(p,s,packets,traces)
                self.assertEqual(report['package_schema_version'],8)
                self.assertEqual(report['model_revision'],p['model_revision'])
                self.assertFalse(report['native_import_verified'])
                self.assertFalse(report['live_authority_restored'])
                self.assertIsNone(report['evaluation_verdict'])
                if 'Completed' not in identity:self.assertIsNone(p['certificate'])

    def test_actual_restoration_does_not_relabel_measurements(self):
        restored=0
        for identity in sorted(self.cases):
            p,s,_,_=self.case(identity);event=p['terminal_event']
            if event is None or event['status']!='restored':continue
            restored+=1
            self.assertGreater(p['model_epoch'],s['historical_summary']['model_epoch'])
            self.assertNotEqual(p['model_revision'],p['historical_state']['model_revision'])
            self.assertIsNone(p['certificate']);self.assertFalse(event['fresh_all_input_verification'])
        self.assertEqual(restored,6)

    def test_12_real_warm_imports_preserve_journal(self):
        warm_count=0
        for identity,(folder,row) in sorted(self.cases.items()):
            if row['warm_folder'] is None:continue
            warm_count+=1
            original,_,packets,traces=self.case(identity)
            warm=self.root/row['warm_folder']
            p=load(_artifact(warm,'terminal_imported_warm_control.json'))
            s=load(_artifact(warm,'terminal_imported_warm_summary.json'))
            current,raw=_packets(warm,'terminal_imported_warm_trial_')
            require(not (set(current)&set(packets)),'terminal_warm_reused_trial_id')
            packets.update(current);traces.update(raw)
            history=p['historical_state']
            needed={q['requested_specification']['trial_id'] for q in
                    history['reference_packets']+history['final_packets']+history['observed_packets']}
            needed.update(q['requested_specification']['trial_id'] for event in p['terminal_journal']
                          for q in event['selected_probe_packets'])
            require(needed<=set(packets),'terminal_warm_primary_missing')
            report=audit_learned_state(p,s,{k:packets[k] for k in needed},{k:traces[k] for k in needed})
            self.assertEqual(p['terminal_journal'],original['terminal_journal'])
            self.assertEqual(p['model_revision'],original['model_revision'])
            self.assertEqual(p['session_attempt'],original['session_attempt']+1)
            self.assertEqual(report['training_outcome'],'external_stop');self.assertIsNone(report['evaluation_verdict'])
        self.assertEqual(warm_count,12)

    def test_resigning_cannot_replace_actual_epoch_or_parameters(self):
        p,s,packets,traces=self.case(self.restored())
        for field in ('epoch','parameters'):
            with self.subTest(field=field):
                changed=copy.deepcopy(p);summary=copy.deepcopy(s)
                if field=='epoch':
                    changed['model_epoch']+=1;summary['model_epoch']=changed['model_epoch']
                else:
                    changed['trained_inputs'][0]['resistance']*=1.01;summary['parameters']=changed['trained_inputs']
                _resign(changed);_resign(summary)
                with self.assertRaises(EvidenceError):audit_learned_state(changed,summary,packets,traces)

    def test_8_composite_warm_boundaries_replay_original_groups(self):
        count=0
        for identity,(folder,row) in sorted(self.cases.items()):
            if not identity.startswith('NativeTerminalCompositePackage/') or not identity.endswith('Stopped'):continue
            count+=1
            original,_,_,_=self.case(identity)
            p=load(_artifact(folder,'terminal-warm-state8.json'))
            s=load(_artifact(folder,'terminal-warm-summary9.json'))
            report=audit_learned_state(p,s,{},{})
            self.assertEqual(p['terminal_journal'],original['terminal_journal'])
            self.assertEqual(p['model_revision'],original['model_revision'])
            self.assertEqual(p['session_attempt'],original['session_attempt']+1)
            self.assertEqual(report['training_outcome'],'external_stop');self.assertIsNone(report['evaluation_verdict'])
        self.assertEqual(count,8)

    def test_missing_primary_and_forged_live_authority_rejected(self):
        p,s,packets,traces=self.case(self.restored())
        missing=dict(traces);missing.pop(next(iter(missing)))
        with self.assertRaises(EvidenceError):audit_learned_state(p,s,packets,missing)
        summary=copy.deepcopy(s);summary['restored_live_authority']=True;_resign(summary)
        with self.assertRaises(EvidenceError):audit_learned_state(p,summary,packets,traces)
        summary=copy.deepcopy(s);summary['schema_version']=10;_resign(summary)
        with self.assertRaises(EvidenceError):audit_learned_state(p,summary,packets,traces)
