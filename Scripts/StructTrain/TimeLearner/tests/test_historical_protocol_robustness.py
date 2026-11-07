"""Protocol mutations of actual archived native configs; execute on workers."""
import os
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from ..historical_model import serialized_neuron
from ..historical_phasea_native import prepare_case, parameter_export
from ..historical_protocol_robustness import (CASE, prepare_protocol, effective_protocol)
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


if __name__ == "__main__":
    unittest.main()
