"""Certificate2 residual DATA regression; no native/waveform attestation.

The certificate function assumes independently audited groups at its caller.
These deliberately minimal records exercise that residual-only contract;
actual package5 corpus regression remains a separate required integration.
"""
from copy import deepcopy
import unittest

from ..composite_certificate_evidence import audit_composite_certificate
from ..composite_configuration import METHOD
from ..model_identity import canonical_model_sha256 as digest
from ..native_evidence import EvidenceError


def residual_case(*, nonanchor=False, point=False):
    # Exact binary fractions make the signed interval expectation independent
    # of display rounding. No copied C++ body or physical model is evaluated.
    times=[(.125,.1875 if nonanchor else .125),(.25,.3125)] if nonanchor else [(.125,.125),(.125,.1875)]
    if point:times[1]=(times[1][0],times[1][0])
    records=[]
    for purpose in ('reference','final'):
        for i in range(2):
            group=purpose+str(i);arrival,end=times[i]
            records.append(dict(group_id=group,logical_request=dict(input_id='input'+str(i),trial_id=group,
                base_model_revision='initial' if purpose=='reference' else 'current',model_epoch=0),
                measurement=dict(raw_potential=1.,arrival=arrival,plateau_end=end,semantic_proof_id=digest(group)),
                native_group=dict(specification=dict(effective_model_revision='current')),
                training_requested_at_consume=True))
    tolerances=dict(amplitude_absolute=1e-5,amplitude_relative=0.,sync=.125)
    expected=[]
    intervals=[(-.1875,-.0625),(0.,0.)] if nonanchor else [(0.,0.) if point else (-.0625,0.),(0.,0.)]
    for i,(low,high) in enumerate(intervals):
        expected.append(dict(input_id='input'+str(i),trial_id='final'+str(i),effective_model_revision='current',
            target_raw_potential=1.,measured_raw_potential=1.,amplitude_residual=0.,amplitude_tolerance=1e-5,
            timing_low=low,timing_high=high,within_timing=not nonanchor or i==1,within_amplitude=True))
    certificate=dict(schema_version=2,method_id=METHOD,exact=not nonanchor,model_revision='current',model_epoch=0,
        protocol_revision='protocol',source_origin='source',owner_family_binding='family',reference_model_revision='initial',
        reference_model_epoch=0,reference_semantic_proof_ids=[digest('reference0'),digest('reference1')],
        final_semantic_proof_ids=[digest('final0'),digest('final1')],tolerances=tolerances,residuals=expected)
    certificate['semantic_certificate_id']=digest(certificate)
    package=dict(certificate=certificate,measurement_archive=dict(source_origin='source',owner_family_binding='family',
        records=records,reference_group_ids=['reference0','reference1'],
        final_group_ids=['final0','final1']),protocol=dict(inputs=[dict(id='input0'),dict(id='input1')],revision='protocol'),
        runtime_plan=dict(search=dict(tolerances=tolerances)),model_revision='current',model_epoch=0,capture_revision='initial',
        capture_epoch=0,training_outcome='search_unresolved' if nonanchor else 'exact')
    audit=dict(groups=[dict(group_id=r['group_id'],native_closure_recomputed=True,geometry_recomputed=True,
                            measured=True,consumed=True) for r in records])
    return package,audit


class CompositeCertificateAnchorPlateauTest(unittest.TestCase):
    def test_anchor_plateau_self_residual_is_zero(self):
        package,audit=residual_case();result=audit_composite_certificate(package,audit)
        self.assertTrue(result['certificate_consistent']);self.assertFalse(result['native_execution_verified'])
        self.assertEqual(package['certificate']['residuals'][-1]['timing_low'],0.)
        self.assertEqual(package['certificate']['residuals'][-1]['timing_high'],0.)

    def test_nonanchor_signed_interval_is_preserved(self):
        package,audit=residual_case(nonanchor=True);result=audit_composite_certificate(package,audit)
        self.assertFalse(result['exact'])
        self.assertEqual((package['certificate']['residuals'][0]['timing_low'],
                          package['certificate']['residuals'][0]['timing_high']),(-.1875,-.0625))

    def test_nonzero_anchor_width_cannot_be_claimed_as_self_timing_error(self):
        package,audit=residual_case();bad=deepcopy(package)
        bad['certificate']['residuals'][-1].update(timing_low=-.0625,timing_high=.0625)
        bad['certificate']['semantic_certificate_id']=digest({k:v for k,v in bad['certificate'].items() if k!='semantic_certificate_id'})
        with self.assertRaises(EvidenceError):audit_composite_certificate(bad,audit)

    def test_single_sample_anchor_remains_compatible(self):
        package,audit=residual_case(point=True)
        self.assertTrue(audit_composite_certificate(package,audit)['exact'])
