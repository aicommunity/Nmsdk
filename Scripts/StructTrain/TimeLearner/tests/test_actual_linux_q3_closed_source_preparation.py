"""Admission of the actual same-runtime q3 Train; no recalculation of its model."""
from . import test_actual_linux_closed_source_preparation as sequential
from ..linux_physical_recognition_sequence import original_projection_source


class ActualLinuxQ3ClosedSourcePreparation(sequential.ActualLinuxClosedSourcePreparation):
    def test_real_closed_groups_and_full_primary_audit_bind_the_actual_stopped_package(self):
        source = original_projection_source(self.plan)
        self.assertEqual(source['execution']['model_revision'],
            'c114c8c2a34d6757ef62bef03eb52be938143c40d54ed1984fe20cbfd7af518a')
        self.assertEqual(source['execution']['training_outcome'], 'budget_exhausted')
        self.assertIs(source['execution']['completed_boundary'], False)
        self.assertEqual(source['package']['size'], 1265970945)
        self.assertEqual(source['package']['sha256'],
            '82233436899e34c47939a8f7ec187cf7538565067bc29557b5e63834b41f2c27')
        self.assertIs(source['terminal']['native_import_verified'], False)
