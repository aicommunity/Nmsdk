# TimeLearner reproducibility artifacts

Current whole-plan status: [01.11.2026 audit](../../../Docs/StructTrain/TimeLearner/PlanCompletionAudit-2026-11-01.ru.md).
Scoped engineering evidence below does not establish full mode/physics coverage or scientific classification success.

Feature stock training failure diagnostics (04.11; full native feature acceptance pending):
[contracts, observed boundaries and limits](../../../Docs/StructTrain/TimeLearner/StockFailureBoundaryReports.ru.md),
[Elder twelve data checks](s07-stock-failure-boundary-elder-a1/README.ru.md),
[M40 initial twenty probe/soma pairs](s07-stock-failure-boundary-m40-a1/README.ru.md),
[readable local peaks, four report checks and twelve selected originals](s07-stock-failure-boundary-m40-a2/README.ru.md).
Same original four cold conditions; no models rerun or classification claimed.
1021 cached views, including25 local peak views, stay on M40. Compressed primary
metadata and selected PNG originals are retained in Git. All twelve selected
originals reviewed; the whole image cache has not been manually reviewed.

Accepted explicit Rdk working-directory startup (04.11):
[native normal](s02-native-event-log-normal-a3/README.ru.md),
[native ASan](s02-native-event-log-asan-a3/README.ru.md),
[ordinary default normal](s02-rdk-default-startup-normal-a1/README.ru.md),
[ordinary default ASan](s02-rdk-default-startup-asan-a1/README.ru.md),
[calibration normal](s02-native-event-calibration-normal-a1/README.ru.md),
[calibration ASan](s02-native-event-calibration-asan-a1/README.ru.md).
Each worker: four preflights, four frozen imports (16 trials), four actual
calibrations, nine artifact-reader tests, three early refusals and one
concurrent duplicate0/2. Old/new runtime inventories unchanged; same ordinary
startup default. All1011 archived members and315 source hashes verified.
[Scope, exact code and accepted merges](../../../Docs/StructTrain/TimeLearner/RdkStartupWorkDirectoryAcceptance-2026-11-04.ru.md).
Engineering same-matrix LT profiles; no stock classification or full-plan verdict.

Accepted scoped native timing property correction:
[baseline4 failures /84 accepted nonfinite values](s01-timing-finite-baseline-normal-a1/README.md),
[normal4+21](s01-timing-finite-current-normal-a1/README.md),
[ASan4+21 with original timeout retained](s01-timing-finite-current-asan-a1/README.md).
Each worker rejected120 invalid assignments and preserved previous finite values.
The retry used the same frozen runtime; no scientific result or whole-stage
acceptance follows. [Scope](../../../Docs/StructTrain/TimeLearner/TimingFiniteValidation.ru.md).

Accepted scoped floating matrix serialization / native ModelArchive correction:
[normal unit10/archive16/XML32/regression21](s05-archive-f64-current-normal-a1/README.md),
[ASan unit10/archive16/XML32 and crossworker verification](s05-archive-f64-current-asan-a1/README.md),
[262 cached figures /28 selected originals directly reviewed](s05-archive-f64-visual-a1/README.md).
All24 transfer files have equal numeric arrays and semantic model/image identities;
all64 XML CSVs are byte-identical. The short normal unit mapping limitation is
retained explicitly. [Full scope and limits](../../../Docs/StructTrain/TimeLearner/ArchiveF64Precision.ru.md).

Accepted scoped legacy warm Reset correction:
[normal8+32+21](s04-hot-readout-current-normal-a1/README.md),
[ASan8+32+21 and readers16+16](s04-hot-readout-current-asan-a1/README.md),
[178 temporal figures /18 selected directly reviewed](s04-hot-readout-visual-a1/README.md).
All40 CSVs are byte-identical across workers; hashes and complete native/runtime
evidence are retained. [Scope and remaining gates](../../../Docs/StructTrain/TimeLearner/HotLearnerReset.ru.md).

Historical baselines of the accepted scoped loaded legacy graph correction:
[normal32/32 detected failures](s04-loaded-readout-baseline-normal-a1/README.md),
[ASan32/32](s04-loaded-readout-baseline-asan-a1/README.md).
Twelve parameter-only N>1 cases keep a two-row buffer; twenty stateful/N1 cases
keep a zero learner readout while the physical soma responds. Complete native
XML/graph/dimension dumps and setup/compile attempts are retained compactly.
[Scope and native lifecycle cause](../../../Docs/StructTrain/TimeLearner/LoadedLearnerReadout.ru.md).
No scientific selectivity verdict or full stage4 acceptance is implied.

Accepted native hot XML Load/Init/Reset scope:
[normal32/32 and readers18/16/16](s04-hot-xml-current-normal-a1/README.md),
[ASan32/32 and readers18/16/16](s04-hot-xml-current-asan-a1/README.md),
[1476 cached figures /26 directly reviewed originals](s04-hot-xml-visual-a1/README.md).
All64 warm/replay CSVs are byte-identical across workers. Arbitrary-precision
matrix parameters and full lifecycle/profile coverage remain separate requirements.

Actual August original-protocol saved-state replay:
[three fresh native Test runs, exact historical closure](s11-august-phasea-replay-elder-a1/README.md)
reproduce4/8,5/8,6/8 (TP1, FP4/3/2).
[Historical CSV adapter Elder29/29](s03-august-csv-adapter-elder-a1/README.md),
[M4029/29](s03-august-csv-adapter-m40-a1/README.md).
[Passive observer raw traces](s11-august-phasea-temporal-primary-elder-a2/README.md)
preserve all three untouched CSVs byte-for-byte;7/7 actual reader checks per worker.
[Final temporal/visual evidence](s11-august-phasea-temporal-visual-m40-a3/SELECTED_VISUAL_REVIEW.ru.md):
96 PNGs for all24 presentations,15 selected directly reviewed at1920x1200;
full feedback range plus explicit amplitude-focused companions and100ms detail.
Order/ITI controls remain open. Legacy CSV completeness and
strict verdict remain unknown; new raw traces provide separate coverage evidence.

[Native cold-start controls](s11-august-coldstart-elder-a2/README.md) reject
parent-only cold overlays and verify the original State-file reset before input.
[Actual cold Train](s11-august-coldtrain-elder-a2/README.md) completes160 model
seconds with original L49/41/25/1, Rs and newly captured references.
The entire serialized neuron matches original Train/Test:604 nodes,8333 parameters,
496 inbound edges. [Elder10/10 identity checks](s11-august-model-reader-elder-a1/README.md),
[M4010/10](s11-august-model-reader-m40-a1/README.md).
This is legacy_done_uncertified.
[Full cold-model frozen Test](s11-august-coldtest-elder-a2/README.md) passes three
native prestimulus gates and three full matrices:4/8,5/8,6/8, all CSVs and36 raw
streams byte-equal to the accepted saved-state observer. The96 existing temporal
diagrams/15 selected reviewed PNG apply through explicit data equivalence;
no duplicate figures are added. [Elder7/7 temporal checks](s11-august-coldtest-reader-elder-a1/README.md),
[M407/7](s11-august-coldtest-reader-m40-a1/README.md).
[Failed earlier mode0 import](s11-august-coldtest-failed-elder-a1/README.md)
is retained as process_error, never counted as a successful classification result.
Historical same-matrix evaluation does not establish independent robustness.

Active Branch telemetry analyzer moved from Bin to the root package:
[Elder20/20 Python checks](s09-branch-dynamics-migration-elder-a2/README.md),
[M4020/20](s09-branch-dynamics-migration-m40-a2/README.md);
[initial M40 invalid fixture and corrected19-check attempt retained](s09-branch-dynamics-migration-m40-a1/README.md).
Whole original-module parity on valid format, CLI/source preservation and corruption controls;
no new C++ calculations, no ASan instrumentation or classification claim.
[Actual archived C++ trace parity](s09-branch-dynamics-actual-native-a1/README.md):
32 selected raw records, including180 channels/90 membranes; original595MB log
hashed and unchanged. Selected raw primary and complete CLI summaries reproduce
the comparison; complete experiment windows are not claimed.

Actual positive N1 calibration: [normal primary](s08-positive-n1-calibration-normal-a1/README.md),
[ASan primary](s08-positive-n1-calibration-asan-a1/README.md),
[all-pattern temporal proof and28 directly reviewed PNGs](s08-positive-n1-calibration-visual-a1/SELECTED_VISUAL_REVIEW.ru.md).
Each worker measured20 matrices/160 complete trials,4/4 reader checks.
Best target-detecting candidate: TP1/FP3/FN0/TN4 (5/8), both topologies.
All declared grids nonseparable; original threshold1 restored, no calibrated package.
This is historical same-matrix candidate evidence, not independent frozen Test.

Additional authorized build-object cleanup: [Elder](s02-unused-build-objects-elder-20261101-a1/README.md)
and [M40](s02-unused-build-objects-m40-20261101-a1/README.md).
19358 unused object/dependency files removed (5319965370 logical bytes);
current executable/ini/library hashes verified unchanged. Sources, test logs and primary data retained.

Latest production N0 evidence:

- [Normal primary: two protocols,28 operations,7 checks per protocol](s07-n0-production-worker-normal-a2/README.md).
- [ASan primary: the same declared coverage](s07-n0-production-worker-asan-a1/README.md).
- [ASan temporal:28 reports,16 directly reviewed selected PNGs](s07-n0-production-visual-asan-a1/README.md).
- [Normal temporal:32 exact references to those reviewed images](s07-n0-production-visual-normal-a1/README.md).
- [Separate ASan Console build](s07-n0-production-build-asan-a1/README.md) and [normal build/resource-cancelled first attempt](s07-n0-production-normal-preparation-a1/README.md).
- [Authorized Elder cleanup](s02-storage-cleanup-elder-20261101-a1/README.md) and [M40 cleanup](s02-storage-cleanup-m40-20261101-a1/README.md): scientific primary data retained; optional debug caches excluded from Git.

All16 full N0 Train executions across the two workers remain SearchUnresolved.
Complete refers to declared windows; selected traces still decay at their end.
Independent Test and the full physical matrix remain open; see the separate August replay above.

Earlier scoped PostTune milestones (open items describe their historical snapshots):

[Original request bound to finalization: normal](s08-native-training-intent-binding-normal-a1/README.md),
[ASan](s08-native-training-intent-binding-asan-a1/README.md): 61/61 native, 3/3 reader, actual successful import and 20 schema compatibility checks per worker.
Configured automatic phase dispatch remains open.

[Live training request provenance: normal 61/61](s08-native-training-intent-normal-a1/README.md),
[ASan 61/61](s08-native-training-intent-asan-a1/README.md), independent 24-snapshot/32-corruption readers.
[Readable positive LTZ crossing and actual threshold, four reviewed PNGs](s08-native-training-threshold-visual-asan-a3/README.md).
Automatic phase dispatch and intent checkpoints remain open.

[Target-only threshold formulas and actual selected-threshold Solo burst: normal](s08-native-training-threshold-reference-normal-a2/README.md),
[ASan](s08-native-training-threshold-reference-asan-a1/README.md);
[soma/input and LTZ visual reports](s08-native-training-threshold-visual-asan-a1/README.md).
Final parallel recognition, foil evaluation and configured phase orchestration remain open;
positive LTZ amplitude-detail is supplied by a3 above.

[Fresh Solo LTZ burst traces: normal 33/33 and independent reader](s08-native-solo-threshold-trace-normal-a1/README.md),
[ASan 33/33 and independent reader](s08-native-solo-threshold-trace-asan-a1/README.md).
Eight actual controls per worker; source replay, not new Train. Threshold proposal,
confirmation and automatic dispatch remain open.
[Solo soma/LTZ temporal reports: all recorded channels and actual input](s08-native-solo-threshold-visual-asan-a1/README.md);
eight selected PNGs reviewed, remaining views have automated coverage.

Artifact publication prerequisite: [Elder 16 Git tests](s10-artifact-publication-elder-a1/README.md),
[M40 16 Git tests](s10-artifact-publication-m40-a1/README.md). Schema 2 verifies
declared committed blobs; upstream scientific completeness and full producer migration remain open.

[Actual production eight-repository closure, primary/visual artifact checks and receipts](s10-production-closure-publication-a1/README.md)
exercise schema 2 beyond fixtures; the complete stage 10 remains open.

- [Native phase lifecycle detach: 16 normal controls, 12 regressions and compatibility](s08-native-phase-lifecycle-interrupt-normal-a1/README.md).
- [The same lifecycle detach under ASan](s08-native-phase-lifecycle-interrupt-asan-a1/README.md).
- [Lifecycle diagnostics and all 20 complete soma/input reactions; 8 reviewed PNG](s08-native-phase-lifecycle-visual-normal-a1/README.md).
- [All six production schema-1/2 ASan visual reports: 62 complete trial-soma pairs](s08-native-posttune-fixed-console-visual-asan-a1/README.md).
- [Production schema-2 fixed/calibrate and legacy: six owned normal jobs plus rejection gates](s08-native-posttune-fixed-console-normal-a1/README.md).
- [The same production controls under ASan, with all 18 original portable regressions](s08-native-posttune-fixed-console-asan-a1/README.md).
- [Fixed-threshold soma/input reports: 32 trial-soma pairs and 12 reviewed PNG](s08-native-posttune-fixed-visual-normal-a3/README.md).
- [Fixed-threshold native PostTune: normal, repaired complete portable source closure](s08-native-posttune-fixed-normal-a2/README.md).
- [Fixed-threshold native PostTune: 12 ASan cases, legacy A/B and latest reader gates](s08-native-posttune-fixed-asan-a1/README.md).
- [N0 Classic/Branch PostTune: completed ASan and independent readers](s08-native-posttune-controller-n0-asan-a1/README.md).
- [Shared PostTune codec: completed ASan and byte-exact owned Console A/B](s08-native-posttune-codec-asan-a1/README.md).
- [Production measured PostTune: 18 jobs and shared calibration regressions](s08-native-posttune-console-normal-a2/README.md).
- [Production measured PostTune: completed ASan corpus](s08-native-posttune-console-asan-a1/README.md).
- [All 18 production run-bound soma/input reports: 59 matrices, 178 trial-soma pairs](s08-native-posttune-console-visual-normal-a1/README.md).
- [New controller: all 24 visual reports, 61 matrices, 184 trial-soma pairs](s08-native-posttune-controller-visual-normal-a3/README.md).
- [Measured native search, real calibration and rollback: normal A2](s08-native-posttune-controller-normal-a2/README.md).
- [The same native controller: ASan 10 native, 19 original and 20 later reader checks](s08-native-posttune-controller-asan-a2/README.md).
- [N0 Classic/Branch measured PostTune: two native cases and 12 evidence checks](s08-native-posttune-controller-n0-normal-a1/README.md).
- [Shared PostTune controls: all 18 original job declarations and two byte-exact Console A/B jobs](s08-native-posttune-codec-normal-a1/README.md).
- [Verified duplicate-only Elder cache cleanup with retained Git and M40 primaries](s02-storage-dedup-elder-20261031-a1/README.md).
- [All five typed candidate modes: normal](s08-native-posttune-candidates-normal-a2/README.md), [ASan](s08-native-posttune-candidates-asan-a1/README.md).
- [Forty actual Console export/frozen-evaluation operations](s08-native-posttune-worker-normal-a1/README.md).
- [Complete old candidate/transfer soma-input visual caches and selected figures](s08-native-posttune-visual-normal-a1/README.md).
- [TL-037 additional 37 ASan regressions](s08-posttune-observation-regression-asan-a1/README.md).

These gates do not accept the full mode/profile/frequency matrix or the complete
refactoring plan. Old all-silent candidate evaluations and later calibrated
two-pattern controller controls are distinct snapshots; neither establishes
eight-pattern scientific classification.

This maintained subtree is explicitly tracked in Git. Store a run manifest,
complete trial observations, learned-model export and verification evidence here.
Necessary large text traces may be compressed with their content digest and file
listing. A server-only absolute path or a digest without the artifact is insufficient.

Do not store credentials, binaries or working directories. Distinguish execution,
validity, convergence, calibration and scientific evaluation. An implementation
test report is not a trained-model result.

Current storage policy: keep compressed lossless primary data, models, metrics,
runtime/provenance receipts and selected figures in Git. Reproduce full readable
PNG/SVG/PDF reports in the M40 cache. A cache path is supplementary; it does not
replace the primary data needed to reproduce a published result. Selected visual
review does not imply acceptance of an entire report collection.

## Implementation evidence

| Validation | Artifact directories |
|---|---|
| Standard production Console calibration: six jobs per worker, portable owned CLI/model/full-grid binding, bounded stop/parser controls and runtime flags; full experiment pipeline remains open | [Normal](s08-calibration-worker-normal-a1/README.md), [normal controls](s08-calibration-worker-controls-normal-a1/README.md), [ASan](s08-calibration-worker-asan-a1/README.md) |
| Production calibration soma/input reports: 10 reports, 22 complete matrices, 66 trial/soma pairs, 19 checks; eleven selected overview/rise/peak PNG reviewed, full collection not accepted | [M40 report metadata and selected PNG](s08-calibration-worker-report-normal-a1/README.md) |
| Saved-model calibration ownership: six reproduced baseline failures; fixed 8 native + 4 independent checks per worker; source training remains unresolved | [Normal](s08-calibration-ownership-normal-a1/README.md), [ASan](s08-calibration-ownership-asan-a1/README.md) |
| Ownership control soma/input reports: six complete matrices, 18 trial/soma pairs plus three complete externally consumed probe/soma plots; 9 overlapping checks, four selected overviews reviewed | [M40 cache receipt and selected PNG](s08-calibration-ownership-report-normal-a2/README.md) |
| Native threshold-grid transaction, commit/rollback and context controls: 2 native + 17 independent per worker; full worker/PostTune matrix remains open | [Normal](s08-calibration-grid-normal-a2/README.md), [ASan](s08-calibration-grid-asan-a3/README.md) |
| All-grid soma/input report metadata and selected figures: 16 reports, 10 complete matrices, 30 trial/soma pairs per dataset; full cache on M40 | [Normal](s08-calibration-grid-report-normal-a1/README.md), [ASan](s08-calibration-grid-report-asan-a1/README.md) |
| Addressed absolute-clock correction: 52 native cases at seeded 131 s, 25 corrected data tests, 8 clock / 84 learned / 66 stopped primary trials; full gate pending | [Elder-1](s07-clock-fixed-elder1/README.md) |
| Failed full gate: 22/430 failures per worker; real absolute-clock baseline 9/10 expected failures, mapped-process manifests retained | [Elder-1](s07-clock-failure-elder1/README.md), [M40 + ASan baseline](s07-clock-failure-m40/README.md) |
| Physical domain schema 2: 22 native / 15 Python per worker; independent a/b/endpoints; aligned byte-exact 68 normal / 44 ASan trial controls | [Elder-1](s07-domain-physics-elder1/README.md), [M40 ASan](s07-domain-physics-m40/README.md), [aligned 2/20 kHz](s07-domain-physics-matrix-elder1/README.md) |
| Maintained native analyze CLI: 20 tests and 27 actual calls per worker; I/O vs evidence status and explicit legacy adapter | [Elder-1 A2](s07-domain-cli-status-elder1/README.md), [M40 A2](s07-domain-cli-status-m40/README.md) |
| Earlier read-only API/editor ASan A2 now terminal: all 12 pass; distinct from later controller/serialization sources | [M40 terminal supplement](s07-domain-preview-full-m40/README.md) |
| Effective N1 controller: 20/20 normal cases and 68 primary trials per worker; 18/18 ASan cases and 44 primary trials on M40 | [Elder-1](s07-domain-controller-elder1/README.md), [M40](s07-domain-controller-m40/README.md), [ASan](s07-domain-asan-m40/README.md) |
| Effective-domain controller learning/export regressions: 22 native, 9 Python, five completed packages / 62 original trials per worker | [Elder-1](s07-domain-learning-elder1/README.md), [M40](s07-domain-learning-m40/README.md) |
| Read-only physical domain preview: normal API/editor checks and scoped ASan; earlier compile failure retained | [Elder-1](s07-domain-preview-elder1/README.md), [M40](s07-domain-preview-m40/README.md) |
| Post-fix maintained gate: 4/4 suites per worker, PulseLib 387 pass + 10 skip, 16 completed packages / 208 primary trials per worker | [Elder-1](s05-pooled-full-elder1/README.md), [M40](s05-pooled-full-m40/README.md) |
| N1 mesh ignores effective Rs domain: two expected native failures and 20 verified primary trials per worker; fix pending | [Elder-1](s07-domain-baseline-elder1/README.md), [M40 ASan](s07-domain-baseline-m40/README.md) |
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

- [Elder-1 full native clock-regression gate](s07-clock-full-elder1/README.md), [M40 full gate](s07-clock-full-m40/README.md): 4/4 CTest groups, PulseLib 442 cases (10 helper skips), 58 independent Python tests per worker.

- [Elder-1 recognition conversion](s08-recognition-elder1/README.md), [M40 ASan](s08-recognition-m40/README.md): 11 native / 23 Python; 108 source trials and 3528 complete paired samples per worker; scientific verdict null.

- [Elder-1 fresh-process recognition replay](s08-recognition-replay-elder1/README.md), [M40 cross-Qt ASan replay](s08-recognition-replay-m40/README.md): eight child imports, 29 Python tests, 3528 byte-exact samples per worker; failed A1/A2 setup preserved.
- [Accepted clock-regression recursive source closure](s07-accepted-closure-m40/README.md): root b6212753, seven exact clean submodules; metadata only.

- [Elder native PostTune reconstruction](s08-posttune-rebuild-elder1/README.md), [M40 ASan](s08-posttune-rebuild-m40/README.md): 10 native / 7 Python tests and 10090 waveform pairs per worker; eight pre-fix baseline failures; failed fixtures and one-pass stimulus evidence preserved.

- [Elder transient PostTune goal](s08-transient-elder1/README.md), [M40 ASan](s08-transient-m40/README.md): four native cases, eight Python tests, eight complete presentations / 19368 samples per worker; corrected pre-fix baseline and byte-exact common waveforms.

Native production additions: [cold Train/export/frozen evaluation normal](s09-native-pipeline-normal-a1/README.md), [separate mechanical worker support extraction](s08-worker-support-normal-a1/README.md). The terminal older [threshold assessment ASan 16+35 gate](s08-threshold-assessment-asan-a1/README.md) is published separately; it does not accept later source versions.

Owned cold pipeline: [normal 12 phases + controls](s09-native-pipeline-owned-normal-a1/README.md), [ASan](s09-native-pipeline-owned-asan-a1/README.md), [all-pattern fixed-evaluation temporal soma/input reports](s09-native-pipeline-report-normal-a2/README.md) (4 matrices, all somas, eight manually reviewed selected PNG). Training is SearchUnresolved; full-cache visual acceptance and full original stages remain open.

Cold pipeline interoperation and stronger stopped-state controls: [normal](s09-native-pipeline-interoperation-normal-a1/README.md), [ASan](s09-native-pipeline-interoperation-asan-a1/README.md). Seven controls pass per worker; actual cold N1 calibration remains NonSeparable on the declared grids, with valid frozen negative evaluation. New calibration-grid visual acceptance remains open.

TL-037 legacy inference observation: [normal expected failures](s08-posttune-observation-baseline-normal-a1/README.md), [ASan expected failures](s08-posttune-observation-baseline-asan-a1/README.md). Six failing controls per worker reproduce stale attempt status/evidence and missing-foil false Success; two NaN controls pass. These are baseline failure receipts, not passing fix gates.

TL-037 corrected [normal A2 primary gate](s08-posttune-observation-fixed-normal-a2/README.md): 12 native and 5 independent data checks; four actual legacy free-runs Classic/Branch x 2000/20000 Hz. Separate full-regression, ASan and visual gates remain open.

TL-037 follow-up: [normal 37 regressions and six peak replay checks](s08-posttune-observation-regression-normal-a1/README.md), [ASan addressed 12+6 gate](s08-posttune-observation-fixed-asan-a2/README.md), [complete recorded soma/input report metadata and eleven manually reviewed selected panels](s08-posttune-observation-report-normal-a1/README.md). All four ASan CSVs equal normal primaries; reuse the waveform cache, without claiming independent scientific repetitions. Additional ASan 37-case regression remains open.


- [Owned native PostTune, normal](s08-native-owned-posttune-normal-a1/README.md):
  75/75 C++ checks, 2/2 independent reader checks, ten actual phase records and
  100 corrupt-receipt controls. All 836 archive members verified; compressed
  primary 4095348 bytes, original source closure two runs / 84 artifacts.
  [ASan](s08-native-owned-posttune-asan-a1/README.md) also passed 75/75;
  [selected visual acceptance](s08-native-owned-posttune-visual-asan-a1/README.md)
  is published. Configured live-Train dispatch remains pending.


- Production owned PostTune Console:
  [normal](s08-native-owned-posttune-worker-normal-a1/README.md),
  [ASan](s08-native-owned-posttune-worker-asan-a1/README.md): 20 PostTune + 6
  standalone calibration controls per worker, ordered 19/19 checks, no skips.
  Initial setup skips remain recorded. Complete 28-run closures / 1196 artifacts
  each; all compressed archive members verified.
  [All 26 production temporal reports](s08-native-owned-posttune-worker-visual-asan-a1/README.md)
  passed five checks; compact metadata and eight byte-identical previously reviewed
  selected PNGs are published. Live Train handoff and full stage8 are not accepted.

- Clock-only finalization seam:
  [normal](s08-native-finalization-clock-handoff-normal-a2/README.md),
  [ASan](s08-native-finalization-clock-handoff-asan-a2/README.md): 24/24 native
  and 3/3 independent reader tests per worker. Four actual topology/mode records,
  exact full boundary preservation after one outer-clock step without Calculate,
  32 malformed-record and 16 re-signed projection controls. This uses imported
  finished Solo state; it does not implement live Train dispatch.

- [Actual cold live Train handoff, normal](s08-native-live-finalization-normal-a1/README.md):
  31 native cases plus two stopped-primary serialization follow-ups, four complete
  reader tests, 16 live records and 92 malformed-payload controls. All 599 archive
  members verified; compressed primary 1943492 bytes. Mixed fixture provenance
  is explicit per file. All four frozen target/foil pairs are silent; this is
  functional pipeline evidence, without classification success. Broad ASan,
  temporal reports and full original stages remain open.

- [Live Train handoff temporal reports](s08-native-live-finalization-visual-normal-a2/README.md):
  corrected chronological order,16 reports,3/3 checks,213 training and42
  recognition trial-soma pairs. All440 metadata members and eight selected PNG
  verified; selected images directly reviewed at1920x960. Full derived cache on
  M40, no full-cache manual or scientific acceptance. Initial chronology error
  retained; production Train-job declaration remains open.

- [Full live finalization ASan scope](s08-native-live-finalization-asan-a2/README.md):
  95 native tests, six independent checks,548 unchanged producer files;792
  verified archive members /3343244 compressed bytes. Predates explicit Cancel,
  persisted codec and production Train schema2. Leak detection disabled.
- [Explicit live cancellation, normal](s08-native-live-finalization-cancel-normal-a1/README.md):
  eight native and eight independent checks; real partial Train data, queued
  cancellation and owned PostTune rollback.252 verified primary members /752596
  compressed bytes. No frozen recognition evaluation after cancellation.

- [Cancel and persisted codec, ASan](s08-native-live-finalization-cancel-codec-asan-a1/README.md):
  nine native tests, eight independent checks;253 verified members /765044
  compressed bytes. Predates production Train schema2.
- [Production cold Train with live finalization, normal](s09-native-live-training-worker-normal-a2/README.md):
  14 actual operations, one codec test, three original and four overlapping
  complete-reader checks.14 portable run closures /446 artifacts; all member
  hashes verified. Four frozen same-matrix evaluations are silent target misses,
  not classifier success. Initial codec-output and packaging failures retained.
  Production ASan, visual reports and full original stages remain open.

- [Production live Train, ASan](s09-native-live-training-worker-asan-a1/README.md):
  14 operations, one codec, original three and overlapping complete four reader
  checks.521 verified members /1225484 compressed bytes,14 portable runs /446
  artifacts. Leak detection disabled; all frozen pairs remain silent target misses.
- [Production temporal reports, normal](s09-native-live-training-worker-visual-normal-a1/README.md):
  14 reports, three checks,93 training and42 recognition trial-soma pairs.272
  metadata members /190348 compressed bytes and ten selected PNG /1500834bytes.
  All ten directly reviewed1920x960; full-cache manual acceptance remains false.
  Source543 files unchanged; ASan temporal rendering is still pending.

- [Production temporal reports, ASan](s09-native-live-training-worker-visual-asan-a1/README.md):
  14 reports, three checks,521 unchanged primary members.272 verified metadata
  members /190708 compressed bytes; ten exact references to directly reviewed
  normal PNG, no image copies. Legibility scope inherited only by actual PNG
  equality; full-cache manual acceptance remains false.

- [N0 candidate ordering baseline](s07-n0-candidate-order-baseline-asan-a1/README.md):
  two controlled-kernel expected failures on unchanged Core, actual native XML
  and process/runtime receipts;21 archived members,10724 compressed bytes.
  This reproduces proposal-budget loss, not physical infeasibility.

- [N0 ASan wall-budget attempt](s07-n0-candidate-order-timeout-asan-a1/README.md):
  actual300-second timeout,25 completed cases before termination; no complete
  JUnit or full acceptance.40 verified members,46552 compressed bytes.

- [N0 normal wall-budget attempt](s07-n0-candidate-order-timeout-normal-a1/README.md):
  actual300-second timeout,26 completed stdout cases;61 verified archived
  members,225672 compressed bytes. Includes exact duplicate cleanup and an
  inactive compiler-cache receipt; no complete regression acceptance.

- [N0 normal regression](s07-n0-candidate-order-normal-a2/README.md):31/31 native
  cases and4/4 independent checks,56 real probes,188 unchanged source files.
  205 verified members,346080 compressed bytes; temporal acceptance pending.

- [N0 native temporal reports](s07-n0-candidate-order-visual-normal-a1/README.md):
  all56 declared training trials /84 soma pairs,3 N0 visual checks and3 shared
  historical regression checks. Eight selected1920x960 PNG directly reviewed;
  full derived cache remains on M40 Data, no full-cache manual acceptance.

- [N0 ASan regression](s07-n0-candidate-order-asan-a2/README.md):31/31 native
  and4/4 primary-data checks,56 probes;201 verified members/348832 bytes.
- [Configured N0 repeats, normal](s07-n0-candidate-order-repeated-normal-a1/README.md)
  and [ASan](s07-n0-candidate-order-repeated-asan-a1/README.md):each3 native +3
  primary checks,48 actual probes/10 groups.125 members per proof.
- [N0 ASan temporal](s07-n0-candidate-order-visual-asan-a2/README.md):56/84,3 checks,
  eight exact reviewed normal PNG references; no new image copies.
- [Repeated N0 temporal, normal](s07-n0-candidate-order-repeated-visual-normal-a1/README.md)
  and [ASan](s07-n0-candidate-order-repeated-visual-asan-a1/README.md):each48/72,
  three checks. Four normal PNG directly reviewed;four exact ASan references.

Дополнение: проверка совместимости N0-шаблона перед приёмкой подэтапа. Исправление 0980f23309e099cb7cc73a1355a2dd25c7f788ab сохраняет полную конфигурацию при вызове подготовителя без новых факторов; раньше такой вызов ошибочно требовал повторного задания диапазона Ns. Проверено исходниками 54382334754986c574c7ccbcd5ded5b55f1b638e на Elder и M40: исходная ошибка воспроизведена через прежний публичный make_job; по 9 проверок для repeat=1/2, по 10 фактических Train-заданий на протокол регенерированы идентично, 1147 исходных файлов каждого корпуса не изменились. Численные прогоны и отрисовка повторно не выполнялись. Исходные отчёты с 7 проверками остаются отчётами своего снимка. Новые квитанции: Reports/StructTrain/TimeLearner/s07-n0-template-contract-normal-a2 (7aeb9655afdc3aec7ef607664393318fe290d1a3), s07-n0-template-contract-asan-a2 (0689def9d7a056bc9e9464d5ba647fcb8e30cbf9). Первые попытки настройки a1 завершились SyntaxError до выполнения проверок и также сохранены. Это приёмка совместимости подготовителя, а не положительный результат физического обучения и не закрытие полного этапа 7.

Новые native controls (адресная temporal приёмка завершена):
[normal dimensions](s07-native-dimension-normal-a1/README.md),
[ASan dimensions](s07-native-dimension-asan-a1/README.md),
[normal N0 proposal path](s07-native-proposal-normal-a1/README.md).
Сходимость N=1 проверяет неизменённую модель свежим final gate; scientific
classification verdict отсутствует. Полная постановка и ограничения:
[NativeDimensionControls](../../../Docs/StructTrain/TimeLearner/NativeDimensionControls.ru.md).

[ASan N0 physical proposal path](s07-native-proposal-asan-a1/README.md): завершён, reader 2/2; temporal приёмка включена в следующий proof.

[Native controls temporal proof](s07-native-controls-visual-a1/README.md): 18 reports, 610 trial-soma pairs, shared counterpart primary equality, 20 selected PNG directly reviewed; full cache manual review is not claimed.

Measured N1 resistance refinement, scoped controls:

- [Original normal finite mesh](s07-native-n1-mesh-normal-a1/README.md) and
  [ASan counterpart](s07-native-n1-mesh-asan-a1/README.md): two actual cold jobs
  per worker, both SearchUnresolved; measured amplitude brackets retained.
- [Current normal build](s07-n1-refinement-build-normal-a1/README.md): a3 passes40
  selected C++ cases; earlier prototype and failed optional-profile compile
  attempt preserved separately.
- [Current ASan build](s07-n1-refinement-build-asan-a1/README.md): a2 passes32
  selected C++ cases; earlier a1 passes40 on its distinct source; detect_leaks=0.
- [Current normal physical A/B](s07-native-n1-refined-normal-a1/README.md) and
  [ASan counterpart](s07-native-n1-refined-asan-a1/README.md): Classic and Branch
  each Exact after actual L/Rs changes, same cold jobs and original tolerances;
  2/2 primary-data checks per worker. Two inputs,2000Hz,CapturedPerInput.
- [Full baseline/refined temporal evidence](s07-native-n1-visual-a1/README.md):
  434 probe/soma pairs,6 production report checks,24 selected PNG directly
  reviewed1920x960. All536 original trial JSON/CSV files compare equal in value
  across normal/ASan; runtime provenance remains distinct. Full cache on M40.

These are V2 finite-mesh versus V2 refinement controls. They do not establish
legacy V1 equivalence, August replay, classification, nonzero-refinement at
20000Hz or completion of the full original plan.

[Normal native-domain regression temporal evidence](s07-native-domain-visual-normal-a1/README.md):
four depth0 fixtures,48 actual probes/72 soma pairs,2000/20000Hz, all source samples
and production rendering checks. Six selected PNG directly reviewed1920x960.
Historical ASan a1 differs in absolute clock and contains a censored final
Classic20000 probe; no identical/full-window ASan counterpart is asserted.

Positive N1 Solo to frozen recognition:

- [Normal native handoff](s05-positive-n1-handoff-normal-a1/README.md) and
  [ASan native handoff](s05-positive-n1-handoff-asan-a1/README.md):4 actual owned
  operations/128 complete trials/4 reader checks per worker. Eight patterns,
  target in all8 positions, identity export, unchanged source threshold1.
  Both topologies give TP0/FP0/FN8/TN56: silence, not successful detection.
- [Every frozen soma/input response](s05-positive-n1-handoff-visual-a1/README.md):
  192 trial/soma pairs,3 production report checks,22 selected PNG directly
  reviewed1920x960. All134 normal/ASan trial/model JSON values match;
  full derived cache remains on M40. No full-cache manual review or independent
  scientific replicate claim. Initial environment-only rejection receipts retained.

[Current native loaded-learner normal a4](s04-loaded-readout-current-normal-a1/README.md):
production MDMatrix10/10, native serialized learner32/32, regression21/21,
production reader16/16; full graph projection and68 case/soma pairs audited.
All32 trace CSVs are byte-identical to normal a3. Compact archive336 members,
388052 bytes, all member hashes verified. ASan regression and visual acceptance
remain separate pending gates; no selectivity verdict or full-stage acceptance.

[Current native loaded-learner ASan a4](s04-loaded-readout-current-asan-a1/README.md):
MDMatrix10/10, native32/32, regression21/21 without skipped, reader16/16.
340 exact primary members/394220 bytes; outer and member hashes verified after
Git retrieval. All32 CSVs byte-identical to current normal. Together with normal
primary and30 directly reviewed selected PNGs this accepts only the scoped
loaded graph/readout and MDMatrix correction. Full stages4/11 remain open.

Warm learner Reset controls (separate from the accepted loaded-buffer correction):

- [Current normal native evidence](s04-hot-readout-current-normal-a1/README.md):
  8 warm Reset,32 loaded-graph and21 regression tests pass without skipped;
  current loaded reader16/16 and earlier warm baseline/fixed16+16 checks.
  All40 warm/loaded CSVs are byte-identical to the respective pre-fix controls.
  The change is in the public soma readout immediately after Reset.
- [Warm temporal evidence](s04-hot-readout-visual-a1/README.md):178 automatically
  verified PNGs/16 case-soma pairs;18 selected originals directly reviewed.
  Curves show the response before Reset; the reset boundary is checked in native
  JSON and tests. ASan warm8/loaded32 passed; its full regression/data checks
  and joint acceptance remain pending.

Native warm XML Load/Init/Reset/replay:

- [Initial16-case controls](s04-hot-xml-initial-normal-a1/README.md) preserve the
  first50ms/schema1 scope and the earlier preparation error (zero tests).
- [Current normal32-case primary](s04-hot-xml-current-normal-a1/README.md):
  Classic/Branch,inputs1/2/4/6,2000/20000Hz,Parameters-only/Parameters+State,
  full100ms traces. Schema3 compares source-rest and loaded-rest full graphs;
  the warm graph and saved state are retained with dynamic TimeConstant marked
  separately. All68 case/soma pairs audited; reader18/18 plus16+16 compatibility
  checks pass.536 primary members/501960 compressed bytes, all hashes verified.
  ASan32 and temporal visual acceptance remain pending. No mid-probe checkpoint,
  scientific selectivity verdict or full-stage completion is asserted.


Native cold preflight and production matrix preparation (scoped acceptance):

- [Normal primary](s09-native-preflight-current-normal-a2/README.md):14 positive,
  6 negative,2 stopped one-tick Train controls,20 reader/prepare checks,32 native
  dimension cases;824 verified members/258004 compressed bytes. Includes the
  preceding rejected argv audit; it is not an accepted run.
- [ASan primary and crossworker comparison](s09-native-preflight-current-asan-a1/README.md):
  same coverage,820 verified members/257144 bytes. All46 initial models/parameters
  and32 prepared job hashes equal normal. Actual libasan in all52 process snapshots.
- [Preserved setup failures](s09-native-preflight-setup-baselines-normal-a1/README.md):
  128 verified members, including exact restoration of earlier setup metadata.

Preflight runs zero model ticks; these are configuration/runtime checks, not
completed learning or classification. Full physical/mode/scheduler coverage is
still open. Contract and precise limits: Docs/StructTrain/TimeLearner/NativePreflight.ru.md.

Scoped metadata acceptance 2026-11-01: [Elder property/migration](s09-resumed-static-elder-a1/validation.json), [M40 property/migration](s09-resumed-static-m40-a1/validation.json), [Elder worktree guard](s02-source-worktree-identity-normal-a1/validation.json), [M40 worktree guard](s02-source-worktree-identity-asan-a1/validation.json). Actual Git fixtures; no numerical or full-stage claim. Elder Bin alias diagnosis is preserved in its report.

Measured length scoped acceptance2026-11-02: [normal67 after source repair](s07-measured-length-gate-normal-a2/README.md), [ASan remaining24 plus original39+4](s07-measured-length-gate-asan-a2/README.md), [selected ASan rerender16/16](s07-measured-length-selected-asan-a1/README.md), [scope and source limitations](../../../Docs/StructTrain/TimeLearner/MeasuredLengthProposal.ru.md). Full stages6/7/11 remain open.

- 04.11: s10-resource-reservations-elder-a2 и s10-resource-reservations-m40-a2 — по15 реальных SQLite/process/path controls. Принят только reservation API; полная очередь/worker integration остаются открытыми. См. Docs/StructTrain/TimeLearner/ResourceReservations.ru.md.


04.11: worker resource budget controls,30/30 на каждом сервере:
[Elder](s10-resource-budgets-elder-a2/README.ru.md),
[M40](s10-resource-budgets-m40-a2/README.ru.md). Atomic path+slot+RAM+disk
accounting с привязкой к filesystem; исходные schema1 controls сохранены.
Это адресная проверка API, не полный scheduler или численный результат.

- 04.11: s05-calibration-preconditions-elder-a1 —8 native и7 primary readers;4 настоящих Exact→calibration,4 сохранённых legacy stopped controls. ASan counterpart pending. См. Docs/StructTrain/TimeLearner/CalibrationFixturePreconditions.ru.md.

- 04.11: s05-calibration-preconditions-m40-a2 — ASan8/8 и readers7/7; первые отказы guard/prerequisite сохранены отдельно. См. CalibrationFixturePreconditions и ASanVerification в Docs/StructTrain/TimeLearner.

## Native characterization без Train, 04.11.2026

Source111d0b578566342a6159a50977c6bcdab9f9c647. Восемь проб Classic/Branch ModelSpec1/2 на каждом worker; пять ранних отказов и пять primary readers на каждом. Обе холодные Train-регрессии дали по121 побайтно совпадающему первичному файлу. Это инженерные controls с LT-мембраной; нет научного verdict классификации.

- [Elder normal](s03-native-characterization-elder-a6/README.ru.md), proof76d62276a33e271b0320f13d899a4be4c806f96d, primary634052B.
- [M40 ASan](s03-native-characterization-m40-a3/README.ru.md), proof692961f9ae587242e39a44b23827c2133a122725, primary548656B, detect_leaks=0.

[Назначение, команды и ограничения](../../../Docs/StructTrain/TimeLearner/NativeCharacterizationProbe.ru.md). Cancel/wall controls и stock Rs interventions ещё открыты.

Native probe interruption controls (source07ff1081f88dd020eafa345c3dc0cf4594a0941c): six real executions and nine primary readers on each worker. Exact external cancel requests and actual partial traces retained; ordinary complete observations unchanged. [Elder](s03-native-probe-interruptions-elder-a1/README.ru.md), [M40 ASan](s03-native-probe-interruptions-m40-a1/README.ru.md), [verification](../../../Docs/StructTrain/TimeLearner/NativeProbeInterruptionsVerification.json).

Stock fixed-geometry resistance gate: two real Elder zero-tick cold preflights had equal L/Ns/Rs but different full graphs (three extra excitation synapses Classic, thirteen Branch). No resistance probes were run. Four readers passed; full stopped-state import is required before causal controls. [Primary evidence](s07-stock-fixed-geometry-elder-a2/README.ru.md), [scope and next step](../../../Docs/StructTrain/TimeLearner/FixedGeometryResistanceControl.ru.md). No scientific classification verdict.

- 04.11: s03-stopped-resistance-elder-a1 и s03-stopped-resistance-m40-a1 — полный native stopped import, matched Rs controls, compact primary reuse; s03-stopped-resistance-visual-m40-a1 — девять выбранных waveform PNG. Проверка: Docs/StructTrain/TimeLearner/StoppedStateResistanceVerification.json. Один исходный паттерн, без научного verdict.

- 04.11: s03-native-probe-phases-elder-a1 и s03-native-probe-phases-m40-a1 — imported baseline/main interruption,12 jobs и7 readers на worker,2 cold regressions, compact reuse7362 primary files. См. Docs/StructTrain/TimeLearner/NativeProbePhases.ru.md.


04.11: [исправленный временной preview stock stopped Train](s11-stock-stopped-title-preview-a4/preview.png)
и [его provenance](s11-stock-stopped-title-preview-a4/preview.json). Полный trial ID
больше не обрезан;1920×960, фактический soma potential и входные импульсы.
Визуально проверено только это изображение. Полный новый80-pair кэш A4 ещё
формируется на M40; прежний A3 прошёл3 readers, но не принят визуально из-за
обрезанных заголовков. Это незавершённый Train, не классификационный PASS.


04.11 завершён [временной отчёт stock stopped A4](s11-stock-stopped-phasea-visual-a4/REPORT.ru.md):
32 полных пробы,80 trial-soma pairs, реальные входы,6+3 checks;20 выбранных
PNG просмотрены. Низкий порог:TP1/FP7; порог100:FN1/TN7. Train остановлен;
это diagnostic evidence без сертификата или научного PASS. Полный кэш на M40.


04.11: [origin-only recursive checkout](s00-current-develop-checkout-m40-a1/README.ru.md),
100534 tracked files; без build/numerical claim.
User-systemd/cgroup controls12/12 на worker:
[Elder](s10-contained-process-elder-a1/README.ru.md),
[M40](s10-contained-process-m40-a1/README.ru.md). Это lifecycle primitive,
без automatic lease recovery или complete scheduler claim.


Contained-process итоговый gate13/13:
[Elder A2](s10-contained-process-elder-a2/README.ru.md),
[M40 A2](s10-contained-process-m40-a2/README.ru.md). Добавлен ранний отказ
подстановки bootstrap paths; первые12-case primary сохранены. Автоматический
lease recovery и production pipeline integration остаются открытыми.

- Совместный normal44: [44/44 native checks и ограничения](../../../Docs/StructTrain/TimeLearner/Joint44Acceptance.ru.md),
  [сжатые первичные данные](s07-csearch-threshold-joint-normal-a4/README.ru.md).
  Это инженерная приёмка исправления test expectations; full304/readers/ASan
  совместного среза ещё не приняты, научная классификация не заявлена.
