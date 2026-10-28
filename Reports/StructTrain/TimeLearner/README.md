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
| Diagnostic stopped solo state: new-guard regression, 20 native cases and 66 primary trials per worker, fresh-process/bidirectional Git replay and completed-state regressions | [M40 + ASan](s05-stopped-m40/README.md), [Elder-1](s05-stopped-elder1/README.md) |
| Configured ControllerVersion=2 cold JSON/XML dispatch, saved-state guards and policy-independent corruption controls | [Elder-1](s06-configured-controller-elder1/README.md), [M40 + ASan](s06-configured-controller-m40/README.md) |
| Explicit cold native builder/adoption, preserved forced Build, multi-synapse and inhibition routing; A1/A2/A3 | [Elder-1](s06-native-builder-elder1/README.md), [M40 + ASan](s06-native-builder-m40/README.md) |
| Actual typed revision observer, lifecycle/property replacement and native full-provider A/B | [Elder-1](s06-model-observer-elder1/README.md), [M40](s06-model-observer-m40/README.md) |
| Explicit assigned-wave selection, native wide-window traces and backward evidence audit | [Elder-1](s07-assigned-selection-elder1/README.md), [M40](s07-assigned-selection-m40/README.md) |
| Isolated runtime, Qt5/Qt6, observations | [Elder-1](s02-elder1/README.md), [M40](s02-m40/README.md) |
| Frequency/lifecycle and native CSV collector | [Elder-1](s03-s04-elder1/README.md) |
| Effective model graph and indexed property bindings | [Elder-1](s04-inspection-elder1/README.md), [M40](s04-inspection-m40/README.md) |
| Native Copy/XML, explicit order and impulse traces | [Elder-1](s04-roundtrip-elder1/README.md), [M40](s04-roundtrip-m40/README.md) |
| Rest outputs and warm/fresh Reset equivalence | [Elder-1](s04-reset-elder1/README.md), [M40](s04-reset-m40/README.md) |
| Checked class images and common Copy lifecycle | [Elder-1](s04-images-elder1/README.md), [M40](s04-images-m40/README.md) |
| Physical profiles, role-specific synapses, growth and scalar XML | [Elder-1](s04-profiles-elder1/README.md), [M40](s04-profiles-m40/README.md) |
| Channel shutdown lifetime and ownership cleanup | [Elder-1 final](s04-shutdown-elder1/README.md), [M40 ASan before/after](s04-profiles-m40/README.md) |
| Semantic identity, native XML and cross-Qt fingerprints | [Elder-1](s05-identity-elder1/README.md), [M40](s05-identity-m40/README.md) |
| Native archive, image definitions and fresh-process/cross-host replay | [Elder-1 + Git transfer](s05-archive-elder1/README.md), [M40 source](s05-archive-m40/README.md) |
| Native image deletion and two heap-use-after-free regressions | [Elder-1](s05-cleanup-elder1/README.md), [M40 ASan before/after](s05-cleanup-m40/README.md) |
| Typed stimulus ports and cross-host native replay | [Elder-1 source](s05-ports-elder1/README.md), [M40 ASan + Git replay](s05-ports-m40/README.md) |
| Silent Classic live replacement: baseline | [Elder-1](s04-live-init-baseline-elder1/README.md), [M40 graph diagnostic](s04-live-init-baseline-m40/README.md) |
| Native replacement Init fix; legacy mixed rates disclosed | [Elder-1](s04-live-init-fixed-elder1/README.md), [M40](s04-live-init-fixed-m40/README.md) |
| Final cold-reset initialization/response regressions | [Elder-1](s04-live-init-final-elder1/README.md), [M40 + targeted ASan](s04-live-init-final-m40/README.md) |
| Global-rate replacement defect baseline | [M40: two failures and two individual controls](s04-frequency-baseline-m40/README.md) |
| Global/individual runtime policy, detached Copy and N1 growth | [Elder-1](s04-frequency-final-elder1/README.md), [M40](s04-frequency-final-m40/README.md) |
| Shared legacy policies: eight native baseline/A-B cases and graph comparisons | [Elder-1](s06-shared-elder1/README.md), [M40](s06-shared-m40/README.md) |
| Bounded probe observations, raw native soma and storage metadata regressions | [Elder-1](s06-probe-elder1/README.md), [M40 + targeted ASan](s06-probe-m40/README.md) |
| Fresh all-input verification API and native N=1 reference/verification certificates | [Elder-1](s07-verification-elder1/README.md), [M40 + targeted ASan](s07-verification-m40/README.md) |
| Native repeated probes, actual emission history and Multi dimensions | [Elder-1](s07-pulse-elder1/README.md), [M40 + targeted ASan](s07-pulse-m40/README.md) |
| Native learner probe execution, lifecycle invalidation and final-verification chain; legacy A/B | [Elder-1](s07-native-executor-elder1/README.md), [M40 + targeted ASan](s07-native-executor-m40/README.md) |
| Sole PulseLib owner of native graph identity/readback/archive; addressed linkage and process controls | [Elder-1](s06-model-owner-elder1/README.md), [M40](s06-model-owner-m40/README.md) |
| Whole-burst schema 3, merged-response counterexample and physical input ownership | [Elder-1 full](s07-burst-final-elder1/README.md), [M40 full/ASan](s07-burst-final-m40/README.md) |
| Combined shared model API and schema-3 observations: native waveform/identity checks | [Elder-1](s07-burst-combined-elder1/README.md), [M40](s07-burst-combined-m40/README.md) |
| Bounded candidate controller, actual R normalization and shared Branch bank readback | [Elder-1](s07-bounded-elder1/README.md), [M40 + targeted ASan](s07-bounded-m40/README.md) |
| Native structural preview/apply, observer/foreign-bank preservation and coupled cold Branch edit | [Elder-1](s07-native-edits-elder1/README.md), [M40 + targeted ASan](s07-native-edits-m40/README.md) |
| Shared native reference/search/final-verification API and independent primary-data audit | [Elder-1](s06-native-service-elder1/README.md), [M40 + targeted ASan](s06-native-service-m40/README.md) |

Acceptance scope and pending controls are tracked in
[Stage04-Progress](../../../Docs/StructTrain/TimeLearner/Stage04-Progress.ru.md) and
[Stage05-Progress](../../../Docs/StructTrain/TimeLearner/Stage05-Progress.ru.md).
Source commits in manifests describe the tested source closure; subsequent merge
commits are not substituted into historical manifests.
