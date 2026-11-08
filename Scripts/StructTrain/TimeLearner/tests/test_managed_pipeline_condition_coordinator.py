"""Full schema2 cold/boundary/calibration/frozen and stopped native coordinator matrix."""
from . import test_managed_pipeline_coordinator as baseline


class ManagedPipelineConditionCoordinatorTest(baseline.ManagedPipelineCoordinatorTest):
    # Reuse actual jobs, native runtime and owning reservations. No phase mock,
    # synthetic observation or rewritten historical model enters this matrix.
    pipeline_schema_version = 2
