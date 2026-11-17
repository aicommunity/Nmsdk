"""Complete byte/alias/closure guard for the recorded four-condition corpus."""
import os
from pathlib import Path

from ..closed_primary_bundle import verify_sources
from ..native_evidence import load,require


def verify_closed_protocol_fixture():
    manifest=load(Path(os.environ['TIMELEARNER_FROZEN_PROTOCOL_COLLECTION'])/'collection-manifest.json')
    expected={Path(os.environ[name]).resolve(strict=True) for name in (
        'TIMELEARNER_COMMON_WINDOW_BASELINE','TIMELEARNER_COMMON_WINDOW_STUDY',
        'TIMELEARNER_FROZEN_PROTOCOL_CONTROLLER','TIMELEARNER_FROZEN_PROTOCOL_CONTRACTS9')}
    require({Path(row['directory']).resolve(strict=True) for row in manifest['roots']}==expected,
            'frozen_protocol_collection_scope_changed')
    return verify_sources(manifest)
