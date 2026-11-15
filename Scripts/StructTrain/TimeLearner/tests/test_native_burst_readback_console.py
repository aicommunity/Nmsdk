"""Actual Console schema7 probes on declared native stopped N1 fixtures."""
import os
from pathlib import Path
import unittest

from ..composite_package_evidence import audit_composite_package
from ..composite_primary import capture_primary_blobs, filesystem_primary_resolver, write_primary_snapshot
from ..contained_process import inspect
from ..matched_resistance_analysis import _trace, compare_probe_inputs
from ..n1_protocol_robustness import _inventory
from ..native_calibration_worker import _write
from ..native_characterization import prepare_burst_readback_job
from ..native_evidence import load, number, parse_json_bytes, require
from ..native_pipeline_worker import audit_run_manifest, run_job
from ..native_process_policy import policy_for_reservation
from ..process_runner import verify_runtime
from ..resource_reservations import Reservations


class NativeBurstReadbackConsoleTest(unittest.TestCase):
    def test_real_classic_branch_replays_and_time_matched_rs_controls(self):
        controls = Path(os.environ['TIMELEARNER_BURST_READBACK_CONTROLS']).resolve(strict=True)
        fixture = Path(os.environ['TIMELEARNER_BURST_READBACK_SOURCE']).resolve(strict=True)
        spec = load(controls/'declaration.json')
        require(set(spec) == {'cases', 'runtime', 'controller', 'output'}, 'burst_console_control_fields')
        runtime_path = controls/'runtime.json';runtime = load(runtime_path)
        require(runtime == spec['runtime'], 'burst_console_runtime_changed')
        verify_runtime(runtime)
        require(type(spec['cases']) is list and len(spec['cases']) == 2 and
                all(type(r) is dict and set(r) == {'name', 'branch', 'directory'} and
                    type(r['branch']) is bool and r['name'] in ('Classic', 'Branch') for r in spec['cases']) and
                {r['name'] for r in spec['cases']} == {'Classic', 'Branch'} and
                {r['branch'] for r in spec['cases']} == {False, True}, 'burst_console_native_case_inventory')
        output = Path(spec['output']).resolve()
        require(output.is_relative_to(Path(os.environ['TMPDIR']).resolve(strict=True)) and not output.exists(),
                'burst_console_requires_owned_fresh_output')
        output.mkdir(parents=True)
        controller = Path(spec['controller']).resolve(strict=True)
        live = inspect(controller)
        require(live['execution'] == 'running' and live['binding']['initial_main_pid'] == os.getpid(),
                'burst_console_requires_contained_controller')
        memory = live['memory_max'];leaf_memory = 1024**3
        registry = Reservations(output/'leases.sqlite3', managed_units=True,
            capacity=dict(slots=1, memory_bytes=memory+2*leaf_memory, disk_bytes=2*1024**3, tasks=512))
        lease = registry.reserve('burst-console-six-native-probes',
            [dict(path=str(output/'runs'), access='write')], ttl_seconds=3600,
            demands=dict(slots=1, memory_bytes=memory+leaf_memory, disk_bytes=1024**3, tasks=256),
            controller_directory=str(controller))
        policy = policy_for_reservation(registry, lease['token'], memory_bytes=leaf_memory, tasks=64)
        source_before = _inventory(fixture)
        records = []
        try:
            for row in spec['cases']:
                name = row['name'];origin = (fixture/row['directory']).resolve(strict=True)
                require(origin.is_relative_to(fixture), 'burst_console_source_escapes_fixture')
                raw = (origin/'source-package.json').read_bytes()
                summary_raw = (origin/'source-summary.json').read_bytes()
                package, summary = parse_json_bytes(raw), parse_json_bytes(summary_raw)
                require(package['schema_version'] == 7 and package['certificate'] is None and
                        package['configuration']['model']['branch'] is row['branch'] and
                        package['configuration']['model']['normalization'] == 'N1' and
                        len(package['trained_inputs']) == 2, 'burst_console_requires_real_stopped_n1')
                audit_composite_package(package, summary, external_resolver=filesystem_primary_resolver(origin))
                archive = package['measurement_archive']
                references = [t['primary_ref'] for g in archive['records'] for t in g['raw_trials']]
                primary = capture_primary_blobs(archive['primary_blobs'], references,
                                                archive['maximum_total_primary_bytes'])
                source = output/name/'source';source.parent.mkdir()
                write_primary_snapshot(primary, source);del primary
                source_path = source/'train_stopped_state.json';source_path.write_bytes(raw)
                (source/'train_stopped_summary.json').write_bytes(summary_raw)
                case = (package, summary, {}, {})
                parameters = package['trained_inputs'];selected = parameters[0]
                owners = [i for i, p in enumerate(parameters) if (not row['branch'] and i == 0) or
                          (row['branch'] and p['length'] == selected['length'])]
                folders = {}
                for variant, factor in (('replay', None), ('matched', 1.), ('changed', .75)):
                    changes = [] if factor is None else [dict(input_index=i,
                        resistance=number(parameters[i]['resistance'])*factor) for i in owners]
                    job = prepare_burst_readback_job(case, 0, name+'/'+variant,
                        resistance_intervention=changes, maximum_wall_seconds=120, channel_diagnostics=True)
                    job_path = output/name/(variant+'-job.json');_write(job_path, job)
                    folder = output/'runs'/(name+'-'+variant);folder.parent.mkdir(exist_ok=True)
                    registry.heartbeat(lease['token'], ttl_seconds=3600)
                    result = run_job('probe', job_path, source_path, runtime_path, folder, 180., process_policy=policy)
                    self.assertEqual((result['execution'], result['validity']), ('completed', 'valid'))
                    self.assertTrue(inspect(folder/'process/contained')['all_processes_closed'])
                    self.assertTrue(audit_run_manifest(folder/'run-manifest.json')['run_evidence_consistent'])
                    self.assertEqual(load(folder/'native/execution.json')['schema_version'], 7)
                    self.assertEqual(load(folder/'native/job.json')['probe']['peak_selection'], 'none')
                    folders[variant] = folder/'native'
                control, control_spec, a = _trace(folders['matched'])
                changed, changed_spec, b = _trace(folders['changed'])
                inputs = compare_probe_inputs(control, control_spec, a, changed, changed_spec, b)
                self.assertTrue(all(inputs.values()))
                self.assertEqual((folders['replay']/'probe_trial_1.csv').read_bytes(),
                                 (folders['matched']/'baseline_trial_1.csv').read_bytes())
                self.assertEqual((folders['matched']/'baseline_trial_1.csv').read_bytes(),
                                 (folders['changed']/'baseline_trial_1.csv').read_bytes())
                before, after = [load(folders[v]/'initial-state.json') for v in ('matched', 'changed')]
                self.assertEqual(before['identity']['sha256'], package['model_revision'])
                self.assertNotEqual(before['identity']['sha256'], after['identity']['sha256'])
                self.assertEqual([p['length'] for p in before['parameters']],
                                 [p['length'] for p in after['parameters']])
                delta = max(abs(y-x) for left, right in zip(a, b)
                            for x, y in zip(left['soma'], right['soma']))
                self.assertGreater(delta, 0.)
                records.append(dict(name=name, branch=row['branch'], source_revision=package['model_revision'],
                    changed_revision=after['identity']['sha256'], bank_owners=owners,
                    matched_inputs=inputs, maximum_potential_difference=delta,
                    training_executed=False, assigned_peak_measured=False, scientific_verdict=None))
            self.assertEqual(source_before, _inventory(fixture))
            _write(output/'result.json', dict(kind='native_burst_readback_console_acceptance', schema_version=1,
                cases=records, native_probes=6, scientific_verdict=None))
        finally:
            registry.release(lease['token'], note='All managed Console probe groups closed; no training verdict.')
            _write(output/'leases-final.json', registry.inspect())
