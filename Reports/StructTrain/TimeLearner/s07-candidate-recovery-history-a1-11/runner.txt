import json,pathlib,sys,unittest
modules=json.loads(sys.argv[1]); output=pathlib.Path(sys.argv[2])
suite=unittest.defaultTestLoader.loadTestsFromNames(modules)
def flatten(suite):
    for child in suite:
        if isinstance(child,unittest.TestSuite):yield from flatten(child)
        else:yield child.id()
ids=list(flatten(suite))
assert len(ids)==len(set(ids))==54,ids
result=unittest.TextTestRunner(verbosity=2).run(suite)
record={'expected_test_ids':ids,'tests_run':result.testsRun,'failures':len(result.failures),
        'errors':len(result.errors),'skipped':len(result.skipped),
        'unexpected_successes':len(result.unexpectedSuccesses),'expected_failures':len(result.expectedFailures),
        'successful':result.wasSuccessful()}
(output/'tests.json').write_text(json.dumps(record,indent=2)+'\n')
sys.exit(0 if record['successful'] and record['tests_run']==54 and not any(record[k] for k in
    ('failures','errors','skipped','unexpected_successes','expected_failures')) else 1)
