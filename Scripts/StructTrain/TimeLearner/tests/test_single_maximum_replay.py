"""Admission controls for immutable single-maximum replay declarations."""
from copy import deepcopy
import unittest

from ..native_evidence import EvidenceError
from ..single_maximum_replay import validate_design


class SingleMaximumReplayDesignTest(unittest.TestCase):
    def design(self):
        return {'kind':'timelearner_single_maximum_replay','schema_version':1,
                'source':{'repository':'/readonly/data','commit':'a'*40,'bundle_path':'Reports/bundle.json',
                          'archive_path':'Reports/primary.tar.xz'},
                'cases':[{'id':'Classic','member_prefix':'study/Classic-single'},
                         {'id':'Branch','member_prefix':'study/Branch-single'}]}

    def test_explicit_cases_are_data_without_import_or_execution(self):
        design=self.design();self.assertIs(validate_design(design),design)

    def test_unknown_fields_versions_and_unpinned_source_fail(self):
        for factor in ('extra','version','commit'):
            design=self.design()
            if factor=='extra':design['resume_old_jobs']=True
            elif factor=='version':design['schema_version']=2
            else:design['source']['commit']='develop'
            with self.assertRaises(EvidenceError):validate_design(design)

    def test_noncanonical_and_escaping_member_paths_fail(self):
        for value in ('../outside','/absolute','C:/outside','study\\case','study/./case','.','study//case'):
            design=self.design();design['cases'][0]['member_prefix']=value
            with self.assertRaises(EvidenceError):validate_design(design)

    def test_duplicate_ids_and_overlapping_prefixes_fail(self):
        for case in ({'id':'Classic','member_prefix':'other'},
                     {'id':'Other','member_prefix':'study/Classic-single'},
                     {'id':'Other','member_prefix':'study/Classic-single/child'}):
            design=self.design();design['cases'].append(deepcopy(case))
            with self.assertRaises(EvidenceError):validate_design(design)

    def test_repository_cannot_depend_on_an_implicit_working_directory(self):
        design=self.design();design['source']['repository']='relative/data'
        with self.assertRaises(EvidenceError):validate_design(design)
