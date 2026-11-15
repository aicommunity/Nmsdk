"""Protocol mutations of actual archived native configs; execute on workers."""
import os
import json
import copy
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from ..historical_model import serialized_neuron
from ..historical_phasea_native import prepare_case, parameter_export, write
from ..historical_protocol_robustness import (CASE, prepare_protocol, effective_protocol,
                                              analyze_case, read_observations)
from ..native_evidence import EvidenceError


class HistoricalProtocolPreparation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bin = Path(os.environ["TL_HISTORICAL_BIN"]).resolve(strict=True)

    def fixture(self, directory):
        return prepare_case(self.bin, CASE, Path(directory)/"case")[1]

    def test_all_orders_and_gaps_preserve_actual_neuron_and_labels(self):
        positions = {1.5: set(), 3.: set()}
        for gap in (1.5, 3.):
            for rotation in range(8):
                with tempfile.TemporaryDirectory() as temp:
                    work = self.fixture(temp);before = serialized_neuron(work/"Model_00.xml")
                    order = [(i+rotation) % 8 for i in range(8)]
                    declared = prepare_protocol(work, order, gap)
                    write(work.parent/"protocol.json", declared)
                    self.assertEqual(json.loads((work.parent/"protocol.json").read_text()), declared)
                    self.assertEqual(serialized_neuron(work/"Model_00.xml"), before)
                    for name in ("Model_00.xml", "Parameters_00.xml"):
                        effective_protocol(work/name, declared)
                    self.assertEqual([s["original_index"] for s in declared["samples"]], order)
                    targets = [i for i, s in enumerate(declared["samples"]) if s["label"] == "target"]
                    self.assertEqual(len(targets), 1);positions[gap].update(targets)
                    self.assertEqual(len({s["sample_id"] for s in declared["samples"]}), 8)
        self.assertEqual(positions, {1.5: set(range(8)), 3.: set(range(8))})

    def corrupt(self, change, reason):
        with tempfile.TemporaryDirectory() as temp:
            work = self.fixture(temp);path = work/"Parameters_00.xml";tree = ET.parse(path)
            change(tree.getroot());tree.write(path, encoding="utf-8")
            before = {p.name: p.read_bytes() for p in (work/"Model_00.xml", path)}
            with self.assertRaisesRegex(EvidenceError, reason):prepare_protocol(work, list(reversed(range(8))), 3.)
            self.assertEqual({p.name: p.read_bytes() for p in (work/"Model_00.xml", path)}, before)

    def test_unknown_flat_layout_fails_before_editing_either_file(self):
        self.corrupt(lambda r: r.find(".//DatasetMatrix/Parameters/MatrixData").set("Rows", "8"),
                     "unsupported_historical_flat_matrix")

    def test_model_and_parameter_labels_must_agree(self):
        self.corrupt(lambda r: setattr(r.find(".//DatasetMatrix/Parameters/MatrixClasses"), "text", "0 1 0 0 0 0 0 0"),
                     "historical_protocol_model_parameter_data_disagree")

    def test_nonfinite_pattern_rejected_before_either_file_is_edited(self):
        def change(root):
            p = root.find(".//DatasetMatrix/Parameters/MatrixData");p.text = "nan "+p.text.split(maxsplit=1)[1]
        self.corrupt(change, "invalid_historical_protocol_isi")

    def test_unsafe_legacy_load_mode_rejected_before_native_execution(self):
        self.corrupt(lambda r: setattr(r.find(".//NeuronTimeLearner/Parameters/StructureBuildMode"), "text", "1"),
                     "historical_protocol_unsafe_native_load_modes")

    def test_ambiguous_property_is_not_patched_as_a_single_match(self):
        def change(root):
            parent = root.find(".//DatasetMatrix/Parameters")
            ET.SubElement(parent, "Delay", {"Type": "d"}).text = "1.5"
        self.corrupt(change, "historical_protocol_property_not_unique")

    def test_equivalent_native_decimal_spellings_are_not_a_data_change(self):
        with tempfile.TemporaryDirectory() as temp:
            work = self.fixture(temp);path = work/"Parameters_00.xml";tree = ET.parse(path)
            p = tree.getroot().find(".//DatasetMatrix/Parameters/MatrixData")
            p.text = "\n".join(format(float(v), ".8f") for v in p.text.split());tree.write(path, encoding="utf-8")
            declared = prepare_protocol(work, list(range(8)), 1.5)
            effective_protocol(path, declared)

    def test_noop_or_incorrect_effective_factor_does_not_pass_readback(self):
        with tempfile.TemporaryDirectory() as temp:
            work = self.fixture(temp);declared = prepare_protocol(work, list(range(8)), 3.)
            path = work/"Model_00.xml";tree = ET.parse(path)
            tree.getroot().find(".//DatasetMatrix/Parameters/Delay").text = "1.5";tree.write(path, encoding="utf-8")
            with self.assertRaisesRegex(EvidenceError, "historical_protocol_effective_iti_changed"):
                effective_protocol(path, declared)

    def test_existing_native_parameter_export_preserves_the_prepared_protocol(self):
        with tempfile.TemporaryDirectory() as temp:
            work = self.fixture(temp);declared = prepare_protocol(work, [3, 4, 5, 6, 7, 0, 1, 2], 3.)
            parameter_export(work);effective_protocol(work/"Parameters_00.xml", declared)

    def test_evaluation_does_not_silently_retarget_the_learner(self):
        with tempfile.TemporaryDirectory() as temp:
            work = self.fixture(temp);declared = prepare_protocol(work, list(range(8)), 1.5)
            path = work/"Model_00.xml";tree = ET.parse(path)
            target = tree.getroot().find(".//NeuronTimeLearner/Parameters/InputPattern")
            target.text = ".02 .08 .16 .24";tree.write(path, encoding="utf-8")
            with self.assertRaisesRegex(EvidenceError, "historical_protocol_training_target_changed"):
                effective_protocol(path, declared)

    def test_invalid_orders_and_intervals_are_not_silently_normalized(self):
        with tempfile.TemporaryDirectory() as temp:
            work = self.fixture(temp)
            for order in ([0]*8, [True]+list(range(1, 8)), list(range(7))):
                with self.assertRaisesRegex(EvidenceError, "invalid_historical_protocol_permutation"):
                    prepare_protocol(work, order, 1.5)
            with self.assertRaisesRegex(EvidenceError, "unsupported_historical_protocol_iti"):
                prepare_protocol(work, list(range(8)), float("nan"))


class HistoricalProtocolNativeObservation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = Path(os.environ["TL_HISTORICAL_PROTOCOL_CASE"]).resolve(strict=True)
        cls.declared = json.loads((cls.case/"protocol.json").read_text())

    def test_actual_complete_original_control(self):
        result = analyze_case(self.case)
        self.assertEqual(result["native_correct"], 6)
        self.assertEqual(result["native_counts"], {"TP": 1, "FP": 2, "FN": 0, "TN": 5})
        self.assertEqual(len(result["trials"]), 8);self.assertEqual(result["samples"], 80000)
        self.assertTrue(result["all_recorded_windows_complete"])
        self.assertTrue(result["original_control_csv_equal"])
        self.assertIsNone(result["scientific_verdict"])

    def test_missing_declared_sample_does_not_make_a_partial_matrix_complete(self):
        declared = copy.deepcopy(self.declared);declared["samples"].pop()
        with self.assertRaisesRegex(EvidenceError, "historical_protocol_declared_sample_set"):
            read_observations(self.case, declared)

    def test_label_changes_do_not_reassign_target_to_another_pattern(self):
        declared = copy.deepcopy(self.declared)
        declared["samples"][0]["label"] = "foil";declared["samples"][1]["label"] = "target"
        with self.assertRaisesRegex(EvidenceError, "historical_protocol_declared_sample_identity"):
            read_observations(self.case, declared)

    def bad_manifest(self, change, reason):
        records = json.loads((self.case/"trace-files.json").read_text())
        changed = change(records)
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp);(folder/"trace-files.json").write_text(json.dumps(changed))
            with self.assertRaisesRegex(EvidenceError, reason):read_observations(folder, self.declared)

    def test_trace_array_is_not_read_as_an_object_envelope(self):
        self.bad_manifest(lambda r: {"records": r}, "historical_protocol_unknown_trace_manifest")

    def test_source_role_binding_is_checked_before_reading_a_trace(self):
        def change(records):
            records[0]["source"] = "DifferentNeuron.Output";return records
        self.bad_manifest(change, "historical_protocol_trace_source_mismatch")

    def test_duplicate_trace_cannot_replace_required_coverage(self):
        self.bad_manifest(lambda r: r+[r[0]], "historical_protocol_trace_set")


if __name__ == "__main__":
    unittest.main()
