"""Primary storage invariants only; these byte fixtures are not native evidence."""
import base64
from copy import deepcopy
import hashlib
from pathlib import Path
import tempfile
import unittest

from ..composite_primary import (capture_primary_blobs, filesystem_primary_resolver,
                                 primary_path, write_primary_snapshot)
from ..native_evidence import EvidenceError


def inventory(values):
    blobs={};references=[]
    for path,raw in values.items():
        digest=hashlib.sha256(raw).hexdigest()
        blobs[digest]={'bytes':len(raw),'base64':base64.b64encode(raw).decode('ascii')}
        references.append({'relative_path':path,'bytes':len(raw),'sha256':digest})
    return blobs,references


class CompositePrimaryTest(unittest.TestCase):
    def test_all_n_plus_two_distinct_files_survive_self_contained_roundtrip(self):
        values={'composite-measurements/group-000001/'+name: ('actual-byte-fixture-'+str(i)).encode()
                for i,name in enumerate(('full-before.csv','omit-0.csv','omit-1.csv','full-after.csv'))}
        blobs,refs=inventory(values);before=deepcopy((blobs,refs))
        self.assertEqual(capture_primary_blobs(blobs,refs,1000),values)
        self.assertEqual((blobs,refs),before)
        with tempfile.TemporaryDirectory() as folder:
            root=write_primary_snapshot(values,Path(folder)/'fresh')
            self.assertEqual(capture_primary_blobs(blobs,refs,1000,external_resolver=filesystem_primary_resolver(root)),values)
            self.assertEqual({p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()},set(values))

    def test_supplied_resolver_is_additional_requirement_never_missing_blob_fallback(self):
        blobs,refs=inventory({'one.csv':b'primary'})
        for mirror in ({},{'one.csv':b'changed'},{'one.csv':'primary'}):
            with self.subTest(mirror=mirror),self.assertRaises(EvidenceError):
                capture_primary_blobs(blobs,refs,1000,external_resolver=mirror)
        with self.assertRaisesRegex(EvidenceError,'missing_or_unreferenced_blob'):
            capture_primary_blobs({},refs,1000,external_resolver={'one.csv':b'primary'})

    def test_content_hash_size_and_exact_blob_inventory_are_required(self):
        original,refs=inventory({'one.csv':b'primary'})
        for edit in ('hash','bytes','missing','extra','field'):
            blobs=deepcopy(original);key=next(iter(blobs))
            if edit=='hash':blobs[key]['base64']=base64.b64encode(b'changed').decode('ascii')
            elif edit=='bytes':blobs[key]['bytes']+=1
            elif edit=='missing':blobs={}
            elif edit=='extra':blobs['0'*64]={'bytes':0,'base64':''}
            else:blobs[key]['unversioned_field']=1
            with self.subTest(edit=edit),self.assertRaises(EvidenceError):capture_primary_blobs(blobs,refs,1000)

    def test_noncanonical_and_malformed_base64_are_rejected(self):
        for encoded in ('cHJpbWFyeQ==\n','!!!!!!!!!!!!','cHJpbWFyeR==','é'*12):
            blobs,refs=inventory({'one.csv':b'primary'});blobs[next(iter(blobs))]['base64']=encoded
            with self.subTest(encoded=encoded),self.assertRaises(EvidenceError):capture_primary_blobs(blobs,refs,1000)

    def test_materialized_budget_counts_equal_content_at_each_declared_path(self):
        values={'one.csv':b'same','two.csv':b'same'};blobs,refs=inventory(values)
        self.assertEqual(len(blobs),1)
        with self.assertRaisesRegex(EvidenceError,'materialized_budget_exhausted'):
            capture_primary_blobs(blobs,refs,7)
        self.assertEqual(capture_primary_blobs(blobs,refs,8),values)

    def test_integral_counts_are_normalized_and_boolean_or_fractional_counts_fail(self):
        blobs,refs=inventory({'one.csv':b'x'});key=next(iter(blobs))
        blobs[key]['bytes']=1.;refs[0]['bytes']=1.
        self.assertEqual(capture_primary_blobs(blobs,refs,1.),{'one.csv':b'x'})
        for value in (True,-1,.5,float('nan'),float('inf'),2**53,'1'):
            changed=deepcopy(refs);changed[0]['bytes']=value
            with self.subTest(value=value),self.assertRaises(EvidenceError):capture_primary_blobs(blobs,changed,1000)

    def test_paths_cannot_escape_or_have_multiple_spellings(self):
        for path in ('','../trace.csv','/absolute.csv','C:trace.csv','a\\trace.csv','a//trace.csv','a/./trace.csv','a/../trace.csv'):
            with self.subTest(path=path),self.assertRaises(EvidenceError):primary_path(path)

    def test_case_collisions_duplicate_paths_and_file_directory_aliases_fail(self):
        for names in (['one.csv','ONE.CSV'],['Folder/one.csv','folder/ONE.CSV'],
                      ['one.csv','one.csv'],['one.csv','one.csv/two.csv']):
            blobs,refs=inventory({'one.csv':b'primary'});refs=[{**refs[0],'relative_path':name} for name in names]
            with self.subTest(names=names),self.assertRaises(EvidenceError):capture_primary_blobs(blobs,refs,1000)

    def test_windows_device_aliases_controls_and_trailing_segments_fail_before_io(self):
        invalid = ['one\0.csv','dir\n/trace.csv','one\x7f.csv','dir\x85/trace.csv',
            'folder./trace.csv','folder /trace.csv','trace.csv.','trace.csv ',
            'CON','safe/nUl.csv','Aux/trace.csv','PRN.txt','COM1.csv','lPt9/trace.csv',
            'COM¹.csv','lpt²/trace.csv','CONIN$.csv','CONOUT$/trace.csv','CON .txt',
            'bad?/trace.csv','one*.csv','a<b.csv','a|b.csv','a"b.csv']
        with tempfile.TemporaryDirectory() as directory:
            for path in invalid:
                output=Path(directory)/'must-not-exist'
                with self.subTest(path=repr(path)),self.assertRaises(EvidenceError):
                    write_primary_snapshot({path:b'raw'},output)
                self.assertFalse(output.exists())
        for path in ('native/полный-ответ.csv','native/.hidden','native/com10.csv','native/console.csv'):
            self.assertEqual(primary_path(path),path)

    def test_parent_or_file_symlink_never_supplies_primary(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'root';root.mkdir();outside=Path(folder)/'outside';outside.mkdir();(outside/'trace.csv').write_bytes(b'outside')
            (root/'link').symlink_to(outside,target_is_directory=True)
            (root/'file.csv').symlink_to(outside/'trace.csv')
            resolver=filesystem_primary_resolver(root)
            for path in ('link/trace.csv','file.csv'):
                with self.subTest(path=path),self.assertRaisesRegex(EvidenceError,'symlink'):resolver(path)

    def test_invalid_snapshot_inventory_creates_nothing_and_existing_output_is_unchanged(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'new'
            with self.assertRaises(EvidenceError):write_primary_snapshot({'../bad':b'x'},output)
            self.assertFalse(output.exists());output.mkdir();(output/'keep').write_bytes(b'old')
            with self.assertRaises(EvidenceError):write_primary_snapshot({'good.csv':b'new'},output)
            self.assertEqual((output/'keep').read_bytes(),b'old');self.assertFalse((output/'good.csv').exists())

    def test_renaming_csv_changes_only_transport_name_and_does_not_rewrite_bytes(self):
        blobs,refs=inventory({'old.csv':b'primary'});changed=deepcopy(refs);changed[0]['relative_path']='renamed/nested.csv'
        before=capture_primary_blobs(blobs,refs,1000);after=capture_primary_blobs(blobs,changed,1000)
        self.assertEqual(before['old.csv'],after['renamed/nested.csv'])
        self.assertEqual(refs[0]['sha256'],changed[0]['sha256'])

    def test_empty_stopped_inventory_remains_empty_without_fabricated_csv(self):
        self.assertEqual(capture_primary_blobs({},[],1),{})


if __name__=='__main__':unittest.main()
