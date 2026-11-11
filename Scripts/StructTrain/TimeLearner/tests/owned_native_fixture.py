"""Tiny real-kernel supervision fixture. No C++, neuron, training or science.

Only private orchestration tests use this module; production owned-native JSON
cannot choose a worker module or arbitrary command.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import time
from unittest.mock import patch

from Scripts.StructTrain.TimeLearner import contained_process
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('exit0','exit7','wait','nested','unbound','partial','child'))
    parser.add_argument('root',type=Path)
    parser.add_argument('--reserve',action='store_true')
    args=parser.parse_args(argv)
    root=args.root.resolve(strict=True)
    if args.mode=='child':
        time.sleep(20);return 0
    output=root/'native-output';output.mkdir(exist_ok=False)
    if args.reserve:
        registry=Reservations.open_existing(root/'registry.sqlite3')
        lease=registry.reserve(root.name,[{'path':str(output),'access':'write'}],ttl_seconds=120)
        (output/'reservation.json').write_text(json.dumps(lease),encoding='utf-8')
    (output/'fixture-started.json').write_text(json.dumps({'pid':os.getpid(),'mode':args.mode,
        'Cpp_or_model_execution':False}),encoding='utf-8')
    if args.mode=='wait':
        time.sleep(20)
    if args.mode in ('nested','unbound','partial'):
        child=output/'leaf/process/contained'
        if args.mode=='partial':
            child.mkdir(parents=True);(child/'request.json').write_bytes(b'{')
        else:
            runtime=json.loads((root/'fixture-runtime.json').read_bytes())
            # Fixed maintained fixture module; no generated program or public override.
            arguments=['-B','-m','Scripts.StructTrain.TimeLearner.tests.owned_native_fixture','child',str(root)]
            if args.mode=='unbound':
                original=contained_process._write
                def fail_binding(path,value):
                    if Path(path).name=='owned-unit.json':
                        raise OSError('injected_fixture_binding_write_failure')
                    return original(path,value)
                with patch.object(contained_process,'_write',side_effect=fail_binding):
                    try:
                        contained_process.start(runtime,arguments,Path(__file__).resolve().parents[4],child,
                            memory_bytes=128*1024**2,tasks=16,maximum_wall_seconds=15)
                    except OSError as error:
                        (output/'injected-unbound.json').write_text(json.dumps({'reason':str(error),
                            'fault_injection':True,'actual_nested_unit_intent':True}),encoding='utf-8')
            else:
                contained_process.start(runtime,arguments,Path(__file__).resolve().parents[4],child,
                    memory_bytes=128*1024**2,tasks=16,maximum_wall_seconds=15)
    (output/'terminal.json').write_text(json.dumps({'fixture_only':True,'mode':args.mode,
        'contains_native_acceptance_verdict':False,'scientific_verdict':None}),encoding='utf-8')
    return 7 if args.mode=='exit7' else 0


if __name__=='__main__':
    raise SystemExit(main())
