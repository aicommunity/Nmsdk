"""Identity controls on actual cold-trained and archived historical native XML."""
import os
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from ..historical_model import serialized_neuron
from ..native_evidence import EvidenceError


class HistoricalModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(os.environ["TL_HISTORICAL_COLDTRAIN"])
        cls.cold = cls.root/"s11-august-coldtrain-elder-a2/train/work/Model_00.xml"
        cls.original = cls.root/"references/original-train/Model_00.xml"
        cls.reference = serialized_neuron(cls.cold)

    def changed(self, mutate):
        with tempfile.TemporaryDirectory() as temp:
            tree = ET.parse(self.cold);mutate(tree.getroot())
            path = Path(temp)/"Model_00.xml";tree.write(path, encoding="utf-8")
            return serialized_neuron(path)

    def test_actual_cold_and_both_original_graphs_identical(self):
        for path in (self.original, self.root/"references/original-test/Model_00.xml"):
            self.assertEqual(serialized_neuron(path), self.reference)
        self.assertEqual(self.reference["nodes"], 604)
        self.assertEqual(self.reference["inbound_edges"], 496)
        self.assertEqual(self.reference["sha256"], "ed11c257e5b0e01c5ed3ccfc5bd397f93984cf6e544ab4ab87681627d445c474")

    def test_individual_resistance_detected(self):
        result = self.changed(lambda r: setattr(r.find('.//Dendrite1_49/Components/ExcSynapse1/Parameters/Resistance'), 'text', '25847871'))
        self.assertNotEqual(result["sha256"], self.reference["sha256"])

    def test_individual_capacity_detected(self):
        result = self.changed(lambda r: setattr(r.find('.//Dendrite1_49/Components/ExcChannel/Parameters/Capacity'), 'text', '2e-9'))
        self.assertNotEqual(result["sha256"], self.reference["sha256"])

    def test_component_class_detected(self):
        result = self.changed(lambda r: r.find('.//Dendrite1_49/Components/ExcSynapse1').set('Class', 'DifferentSynapse'))
        self.assertNotEqual(result["sha256"], self.reference["sha256"])

    def test_component_order_preserved(self):
        def reorder(root):
            children = root.find('.//NeuronTimeLearner/Components/Neuron/Components')
            first = children[0];children.remove(first);children.append(first)
        self.assertNotEqual(self.changed(reorder)["sha256"], self.reference["sha256"])

    def test_missing_component_rejected(self):
        def remove(root):
            children = root.find('.//NeuronTimeLearner/Components/Neuron/Components')
            children.remove(children.find('./Soma1'))
        with self.assertRaisesRegex(EvidenceError, "historical_link_(source|destination)_not_in_graph"):
            self.changed(remove)

    def test_missing_external_source_rejected(self):
        def change(root):
            for item in root.findall('./Model/Links/elem/Item'):
                if item.text == 'NeuronTimeLearner.DatasetMatrix.Generator1':item.text = 'MissingGenerator'
        with self.assertRaisesRegex(EvidenceError, "historical_link_source_not_in_graph"):
            self.changed(change)

    def test_native_decimal_comma_normalized(self):
        result = self.changed(lambda r: setattr(r.find('.//Dendrite1_49/Components/ExcChannel/Parameters/Capacity'), 'text', '0,000000001'))
        self.assertEqual(result["sha256"], self.reference["sha256"])

    def test_nonfinite_rejected(self):
        with self.assertRaisesRegex(EvidenceError, "nonfinite_historical_model_parameter"):
            self.changed(lambda r: setattr(r.find('.//Dendrite1_49/Components/ExcChannel/Parameters/Capacity'), 'text', 'NaN'))

    def test_integer_precision_preserved(self):
        def number(value):
            return lambda r: setattr(r.find('.//NeuronTimeLearner/Components/Neuron/Parameters/MaxCalculationDuration'), 'text', str(value))
        self.assertNotEqual(self.changed(number(2**60))["sha256"], self.changed(number(2**60+1))["sha256"])


if __name__ == "__main__":
    unittest.main()
