"""Byte-exact recipes for actual Python and Console job files, no new model run."""
import base64
import copy
import json
import os
from pathlib import Path
import unittest

from ..source_job_envelope import factor, record, reference_encodings, restore


class SourceJobEnvelopeRecordedTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(os.environ['TIMELEARNER_SOURCE_ENVELOPE_RECORDED']).resolve(strict=True)
        cls.cases=[];cls.references={}
        folders=sorted(cls.root.iterdir())
        if {p.name for p in folders} != {n+'-'+v for n in ('Classic','Branch')
                for v in ('replay','matched','changed')}:
            raise AssertionError('requires all six actual closed Console runs')
        for folder in folders:
            raw=(folder/'input/source/train_stopped_state.json').read_bytes()
            key=record(raw)['sha256']
            if key not in cls.references:cls.references[key]=(raw,reference_encodings(raw))
            for path in (folder/'input/job.json',folder/'native/job.json'):
                cls.cases.append((path,path.read_bytes(),key))

    def test_actual_python_and_qt_jobs_restore_every_original_byte(self):
        codecs=set();sizes=[]
        for path,original,key in self.cases:
            reference,prepared=self.references[key]
            recipe=factor(original,reference,prepared_reference=prepared)
            with self.subTest(path=str(path)):
                self.assertIsNotNone(recipe)
                codecs.add(recipe['codec'])
                self.assertEqual(restore(recipe,reference,prepared_reference=prepared),original)
                size=len(json.dumps(recipe).encode('utf-8'))
                self.assertLess(size,len(original)//2)
                sizes.append(dict(path=path.relative_to(self.root).as_posix(),
                                  original_bytes=len(original),recipe_bytes=size))
        self.assertEqual(codecs,{'python-indent2','qt-indent4'})
        print(json.dumps(dict(kind='actual_source_envelope_byte_roundtrip',files=sizes,
            native_execution_attested=False,scientific_verdict=None)))

    def test_changed_reference_and_prepared_reference_are_rejected(self):
        _,original,key=self.cases[0];reference,prepared=self.references[key]
        recipe=factor(original,reference,prepared_reference=prepared)
        with self.assertRaises(ValueError):restore(recipe,reference+b'\n')
        wrong=copy.deepcopy(prepared);wrong['source']['sha256']='0'*64
        with self.assertRaises(ValueError):restore(recipe,reference,prepared_reference=wrong)

    def test_corrupt_literals_original_digest_and_unknown_schema_are_rejected(self):
        _,original,key=self.cases[0];reference,prepared=self.references[key]
        recipe=factor(original,reference,prepared_reference=prepared)
        for mutation in ('prefix','suffix','digest','schema','extra','base64'):
            changed=copy.deepcopy(recipe)
            if mutation in ('prefix','suffix'):
                k=mutation+'_base64';changed[k]=base64.b64encode(base64.b64decode(changed[k])+b' ').decode('ascii')
            elif mutation=='digest':changed['original']['sha256']='0'*64
            elif mutation=='schema':changed['schema_version']=True
            elif mutation=='extra':changed['execute']='not allowed'
            else:changed['prefix_base64']='!'
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):
                restore(changed,reference,prepared_reference=prepared)

    def test_unsupported_layout_or_missing_source_stays_literal(self):
        _,original,key=self.cases[0];reference,prepared=self.references[key]
        for raw in (original.replace(b'"source_stopped":',b'"different_source":',1),original.lstrip(b'{')):
            self.assertIsNone(factor(raw,reference,prepared_reference=prepared))
        self.assertEqual(record(original),record(self.cases[0][0].read_bytes()))
