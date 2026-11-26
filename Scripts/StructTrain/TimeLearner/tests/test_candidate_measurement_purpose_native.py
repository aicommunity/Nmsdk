"""Replay current C++ exports and primary data; labels add no measurement proof.

The component fixture embeds its complete raw primary in the original package.
It does not publish separate mirrored files; the production auditor verifies
those embedded bytes rather than inventing an external filesystem mirror.
"""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..candidate_measurement_purpose import PURPOSES
from ..terminal_package_evidence import audit_terminal_package
from ..model_identity import canonical_model_sha256 as digest
from ..native_evidence import EvidenceError, audit_probe, audit_training_summary, load, require


class NativeCandidateMeasurementPurposeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        plain=Path(os.environ['TIMELEARNER_PURPOSE_PLAIN']).resolve(strict=True)
        composite=Path(os.environ['TIMELEARNER_PURPOSE_COMPOSITE']).resolve(strict=True)
        cls.plain=[];cls.composite=[]
        for topology in ('Classic','Branch'):
            prefix=topology+'_2000_N0_learned_boundary_explicit_tolerance_inputs6'
            summary=load(plain/(prefix+'_learned_summary.json'));packets={}
            for p in sorted(plain.glob(prefix+'_state_trial_[0-9]*.json')):
                packet=load(p);audit_probe(packet,p.with_suffix('.csv'))
                identity=packet['requested_specification']['trial_id']
                require(identity not in packets,'purpose_fixture_duplicate_trial');packets[identity]=packet
            require(summary['candidates'] and all(c.get('measurement_purpose')=='exploration'for c in summary['candidates']),
                    'actual_new_plain_producer_labels_required')
            origin=load(plain/(prefix+'_learned_state.json'))['protocol']['origin_stimulus_id']
            cls.plain.append((summary,packets,origin))
            directory=composite/(topology.lower()+'-terminal-window5-N0-stopped')
            package=load(directory/'terminal-state8.json');summary=load(directory/'terminal-summary9.json')
            history=summary['historical_summary']
            require(history['candidates'] and all(c.get('measurement_purpose')in PURPOSES for c in history['candidates']),
                    'actual_new_composite_producer_labels_required')
            cls.composite.append((package,summary,directory))

    def test_actual_plain_exports_bind_all_primary_and_count_measurement_records(self):
        for summary,packets,origin in self.plain:
            result=audit_training_summary(summary,packets,origin)
            inventory=result['candidate_measurement_purpose_inventory']
            self.assertEqual(inventory['records_by_purpose']['exploration'],len(summary['candidates']))
            self.assertIsNone(result['evaluation_verdict'])

    def test_actual_composite_exports_replay_measurement_and_terminal_bindings(self):
        for package,summary,directory in self.composite:
            result=audit_terminal_package(package,summary,{}, {})
            self.assertIsNone(result['evaluation_verdict'])
            self.assertFalse(result['native_execution_verified'])
            inventory=result['source_audit']['summary']['candidate_measurement_purpose_inventory']
            self.assertEqual(inventory['records_by_purpose']['selected_state_restore'],1)
            self.assertEqual(inventory['measurement_records'],len(summary['historical_summary']['candidates']))

    def test_plain_legacy_absence_is_accepted_without_inventing_phase_labels(self):
        for summary,packets,origin in self.plain:
            changed=deepcopy(summary)
            for c in changed['candidates']:del c['measurement_purpose']
            result=audit_training_summary(changed,packets,origin)
            self.assertNotIn('candidate_measurement_purpose_inventory',result)

    def test_plain_labels_do_not_hide_missing_primary_or_bad_residual(self):
        for summary,packets,origin in self.plain:
            missing=dict(packets);del missing[summary['candidates'][0]['trial_id']]
            with self.assertRaises(EvidenceError):audit_training_summary(summary,missing,origin)
            changed=deepcopy(summary);changed['candidates'][0]['amplitude_residual']+=.001
            with self.assertRaises(EvidenceError):audit_training_summary(changed,packets,origin)

    def test_plain_mixed_and_unknown_purpose_are_rejected(self):
        for summary,packets,origin in self.plain:
            for value in ('ABSENT','unknown'):
                changed=deepcopy(summary)
                if value=='ABSENT':del changed['candidates'][0]['measurement_purpose']
                else:changed['candidates'][0]['measurement_purpose']=value
                with self.assertRaises(EvidenceError):audit_training_summary(changed,packets,origin)

    def test_composite_label_does_not_bypass_candidate_binding(self):
        for package,summary,directory in self.composite:
            changed=deepcopy(summary);changed['historical_summary']['candidates'][0]['amplitude_residual']+=.001
            changed['sha256']=digest({k:v for k,v in changed.items()if k!='sha256'})
            with self.assertRaises(EvidenceError):
                audit_terminal_package(package,changed,{}, {})

    def test_composite_unknown_purpose_rejected_after_valid_primary_binding(self):
        for package,summary,directory in self.composite:
            changed=deepcopy(summary);changed['historical_summary']['candidates'][0]['measurement_purpose']='unknown'
            changed['sha256']=digest({k:v for k,v in changed.items()if k!='sha256'})
            with self.assertRaisesRegex(EvidenceError,'unknown_candidate_measurement_purpose'):
                audit_terminal_package(package,changed,{}, {})

    def test_composite_legacy_absence_keeps_primary_checks_without_phase_claims(self):
        for package,summary,directory in self.composite:
            changed=deepcopy(summary)
            for candidate in changed['historical_summary']['candidates']:del candidate['measurement_purpose']
            changed['sha256']=digest({k:v for k,v in changed.items()if k!='sha256'})
            result=audit_terminal_package(package,changed,{}, {})
            self.assertNotIn('candidate_measurement_purpose_inventory',result['source_audit']['summary'])
