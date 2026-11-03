# Repeated-N0 boundary baseline

All ten addressed native tests on m40 fail exactly two summary assertions: absent search_history_retained and absent candidate_repeat_groups after import. Other checks in these actual storage/scheduler/Train-Test/frozen/fresh-process/warm controls produce no separate assertion failures. This is a defect reproduction, not a passing training campaign or recognition verdict.

The original temporary runner also failed while JSON-serializing the Path returned by successful runtime verification. The separate terminal runtime-after-readback.json records the corrected hash readback. All attempts are retained without rewriting history. Fixed evidence is separate.


## Launcher retirement, 2026-11-03

The historical job.py/runner.sh launcher is available in root commit
`3bfb72a1fbe7712796e65bea59db343d507d48f4`. See
[retrieval manifest](../../../../Docs/StructTrain/TimeLearner/script_migration.json) and
[scope](../../../../Docs/StructTrain/TimeLearner/ReportLauncherRetirement.ru.md).
Current-tree directory checksums omit retired launchers and include this note;
the original checksums remain in that same archival commit. Primary results,
models, metrics and original test verdicts are preserved. This directory is
historical evidence, not an active experiment launcher.
