"""Owned native readback of immutable profile archives before expensive Train.

Legacy parent-default fast images are intentionally not admitted by V2.
The original refused A1 remains evidence, never a passing factor check.
"""
from copy import deepcopy
import os
from pathlib import Path
import re
import unittest
from unittest.mock import patch

from ..domain_evidence import _property
from ..model_identity import canonical_model_sha256
from ..native_calibration_worker import _write
from ..native_evidence import EvidenceError, load, require
from ..native_pipeline_worker import run_job, audit_run_manifest
from ..n1_protocol_robustness import _signed

PROFILES = [('NSPNeuronGen', 1e-9, .005),
            ('NSPNeuronGenD005C5e10', 5e-10, .005),
            ('NSPNeuronGenD005C25e11', 2.5e-10, .005),
            ('NSPNeuronGenD002C25e11', 2.5e-10, .002)]


def inspect_profile(identity, name, capacity, dissociation):
    require(identity['valid'] and identity['diagnostics'] == [] and
            identity['sha256'] == canonical_model_sha256(identity['model']), 'fast_profile_invalid_identity')
    nodes = {n['path']: n for n in identity['model']['nodes']}
    require(nodes['$']['class'] == name and len(nodes) == len(identity['model']['nodes']),
            'fast_profile_class_or_node_inventory')
    require(not any(p.startswith('$.LTMembrane') for p in nodes), 'fast_profile_unexpected_LT_membrane')
    require(all(n['frequency_hz'] == '2000' for n in nodes.values()), 'fast_profile_frequency')
    membranes = {p for p in nodes if re.fullmatch(r'\$\.(?:Soma\d+|Dendrite\d+_\d+)', p)}
    require(membranes == {'$.Soma1', '$.Dendrite1_1'}, 'fast_profile_cold_branch_graph')
    capacities, kinetics = [], []
    for p in sorted(membranes):
        require(nodes[p]['class'] == 'NPMembraneBio' or nodes[p]['class'].endswith('_Body_Membrane'), 'fast_profile_membrane_class')
        for role in ('Exc', 'Inh'):
            node = nodes[p+'.'+role+'Channel']
            require(_property(node, 'Type') == (-1 if role=='Exc' else 1), 'fast_profile_channel_role')
            for field in ('Resistance', 'RestingResistance', 'FBResistance'):
                require(_property(node, field) == 1e7, 'fast_profile_other_channel_physics:'+field)
            capacities.append(_property(node, 'Capacity'))
        synapses = [n for path, n in nodes.items() if path.startswith(p+'.') and
                    re.fullmatch(re.escape(p)+r'\.(?:Exc|Inh)Synapse\d+',path)]
        require(bool(synapses), 'fast_profile_synapses_missing')
        for node in synapses:
            for field, expected in {'Resistance': 86e6, 'SecretionTC': .001,
                    'TypicalPulseDuration': .001, 'UsePresynapticInhibition': False, 'InhibitionCoeff': 0.}.items():
                require(_property(node, field) == expected, 'fast_profile_other_synaptic_physics:'+field)
            kinetics.append(_property(node, 'DissociationTC'))
    require(set(kinetics) == {dissociation}, 'fast_profile_dissociation_mismatch')
    return dict(neuron_class=name, declared_capacity=capacity, effective_capacities=capacities,
                capacity_applied=set(capacities)=={capacity}, dissociation=kinetics,
                lt_membrane=False, model_revision=identity['sha256'], training_started=False)


class FastProfilePhysicsPreflightTest(unittest.TestCase):
    def test_actual_registered_children_apply_the_declared_factor(self):
        controls = Path(os.environ['TIMELEARNER_FAST_PROFILE_CONTROLS']).resolve(strict=True)
        declaration = load(controls/'declaration.json')
        require(set(declaration)=={'runtime', 'profiles'} and len(declaration['profiles'])==4,
                'fast_profile_controls')
        template = load(controls/'template.json')
        output = Path(os.environ['TMPDIR'])/'fast-profile-native-preflight';output.mkdir(exist_ok=False)
        cases=[('NSPNeuronGen',1e-9,.005,[])]
        for index, (capacity,tc) in enumerate([(1e-9,.005),(5e-10,.005),(2.5e-10,.005),(2.5e-10,.002)]):
            archive=load(controls/declaration['profiles'][index])
            cases.append(('TLNativeFast'+str(index)+'F2000_Neuron',capacity,tc,[archive]))
        jobs=[]
        for name, capacity, dissociation, archives in cases:
            job=deepcopy(template);job['configuration']['run_id']='fast-profile-'+name
            job['configuration']['model']['neuron_class']=name
            job['profile_archives']=archives
            job=_signed({k:v for k,v in job.items() if k!='sha256'})
            path=output/(name+'.json');_write(path,job);jobs.append((path,name,capacity,dissociation))
        rows=[]
        for path,name,capacity,dissociation in jobs:
            run=output/name
            with patch.dict(os.environ, load(Path(declaration['runtime']))['loader_environment']):
                result=run_job('preflight',path,None,Path(declaration['runtime']),run,180.)
                self.assertEqual(result['execution'],'completed');self.assertEqual(result['validity'],'valid')
                audit=audit_run_manifest(run/'run-manifest.json')
            row=inspect_profile(load(run/'native/initial-state.json')['identity'],name,capacity,dissociation)
            self.assertTrue(row['capacity_applied'])
            rows.append(dict(physics=row,run_audit=audit))
        _write(output/'comparison.json',dict(kind='timelearner_fast_profile_native_readback',schema_version=1,
            rows=rows,all_factors_applied=all(r['physics']['capacity_applied'] for r in rows),
            training_authorized=all(r['physics']['capacity_applied'] for r in rows),
            new_model_calculation=False,scientific_verdict=None))
