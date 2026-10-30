#!/usr/bin/env python3
"""B2: repair A15 wiring of TimeLearnerMatrix Test inputs IN PLACE and update their input manifests.

Run ONLY on a dedicated Bin git branch (task B2).  For every case dir given:
  1. Test/Model_00.xml is repaired by repair_model_wiring.repair() using Test/Parameters_00.xml DendriteLength;
  2. the matching source_files entry (side=Test, file=Model_00.xml) in matrix_input_manifest.json gets the new sha256;
     a top-level key "a15_wiring_repair" records old/new sha and the tool version;
  3. the result is re-checked (check_model_wiring) and validated with timelearner_matrix.verify_prepared_input_snapshot.
Usage: repair_matrix_inputs.py <StructTrain dir> <list.tsv: first column = case dir relative to StructTrain> [--dry-run]
Exit 1 if any case fails; nothing is written for a case that fails its pre-checks.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_model_wiring  # noqa: E402
import repair_model_wiring  # noqa: E402

TOOL_SHA = hashlib.sha256((HERE / 'repair_model_wiring.py').read_bytes()).hexdigest()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    st, lst = Path(argv[0]).resolve(), Path(argv[1])
    dry = '--dry-run' in argv
    sys.path.insert(0, str(st / 'scripts'))
    import timelearner_matrix as tm  # noqa: E402
    cases = [l.split('\t')[0].strip() for l in lst.read_text(encoding='utf-8').splitlines()
             if l.strip() and not l.startswith('case_dir')]
    bad = 0
    for rel in cases:
        root = st / rel
        model, params, man_p = root / 'Test' / 'Model_00.xml', root / 'Test' / 'Parameters_00.xml', root / 'matrix_input_manifest.json'
        try:
            raw_man = man_p.read_text(encoding='utf-8')
            man = json.loads(raw_man)
            fmt = next((kw for kw in ({'indent': 2}, {'indent': 2, 'ensure_ascii': False})
                        if json.dumps(man, **kw) + '\n' == raw_man), None)
            if fmt is None:
                raise RuntimeError('manifest formatting is not reproducible by json.dumps; refusing to rewrite')
            tm.verify_prepared_input_snapshot(root, man)  # inputs must match manifest BEFORE repair
            old_b = model.read_bytes()
            text = old_b.decode('utf-8')
            pt = params.read_text(encoding='utf-8', errors='replace')
            import re
            m = re.search(r'<DendriteLength [^>]*>([^<]*)<', pt)
            lengths = [int(x) for x in m.group(1).split()]
            new_text, st_rep = repair_model_wiring.repair(text, lengths)
            new_b = new_text.encode('utf-8')
            entries = [e for e in man['source_files'] if e.get('side') == 'Test' and e.get('file') == 'Model_00.xml']
            if len(entries) != 1 or entries[0]['sha256'] not in tm.sha256_text_line_ending_variants(model):
                raise RuntimeError('manifest entry for Test/Model_00.xml missing or stale')
            if new_b == old_b:
                print(f'UNCHANGED\t{rel}')
                continue
            tmp = model.with_suffix('.xml.a15tmp')
            tmp.write_bytes(new_b)
            chk = check_model_wiring.analyze(str(tmp), str(params))
            tmp.unlink()
            if not chk['ok']:
                raise RuntimeError(f"repair did not pass check: {chk['violations'][:3]}")
            if dry:
                print(f'WOULD_REPAIR\t{rel}\t{json.dumps(st_rep)}')
                continue
            entries[0]['sha256'] = sha(new_b)
            man['a15_wiring_repair'] = {'file': 'Test/Model_00.xml', 'sha256_before': sha(old_b), 'sha256_after': sha(new_b),
                                        'tool': 'AGENT_PLAN_2026-10-20/tools/repair_model_wiring.py', 'tool_sha256': TOOL_SHA,
                                        'stats': st_rep}
            model.write_bytes(new_b)
            man_p.write_text(json.dumps(man, **fmt) + '\n', encoding='utf-8')
            tm.verify_prepared_input_snapshot(root, man)
            print(f'REPAIRED\t{rel}\t{sha(old_b)[:12]}->{sha(new_b)[:12]}')
        except Exception as e:  # report and continue with the next case
            bad += 1
            print(f'FAILED\t{rel}\t{e!r}')
    print(f'SUMMARY cases={len(cases)} failed={bad} dry_run={dry}')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main(sys.argv[1:])
