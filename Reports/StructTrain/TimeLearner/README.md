# TimeLearner reproducibility artifacts

This maintained subtree is explicitly tracked in Git. Store a run manifest,
complete trial observations, learned-model export and verification evidence here.
Necessary large text traces may be compressed with their content digest and file
listing. A server-only absolute path or a digest without the artifact is insufficient.

Do not store credentials, binaries or working directories. Distinguish execution,
validity, convergence, calibration and scientific evaluation. An implementation
test report is not a trained-model result.

## Implementation evidence

| Validation | Artifact directories |
|---|---|
| Isolated runtime, Qt5/Qt6, observations | [Elder-1](s02-elder1/README.md), [M40](s02-m40/README.md) |
| Frequency/lifecycle and native CSV collector | [Elder-1](s03-s04-elder1/README.md) |
| Effective model graph and indexed property bindings | [Elder-1](s04-inspection-elder1/README.md), [M40](s04-inspection-m40/README.md) |
| Native Copy/XML, explicit order and impulse traces | [Elder-1](s04-roundtrip-elder1/README.md), [M40](s04-roundtrip-m40/README.md) |
| Rest outputs and warm/fresh Reset equivalence | [Elder-1](s04-reset-elder1/README.md), [M40](s04-reset-m40/README.md) |

Acceptance scope and pending controls are tracked in
[Stage04-Progress](../../../Docs/StructTrain/TimeLearner/Stage04-Progress.ru.md).
Source commits in manifests describe the tested source closure; subsequent merge
commits are not substituted into historical manifests.
