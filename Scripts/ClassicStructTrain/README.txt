Classic structural training experiments on autoPreset

The replay controller uses the actual NNeuronLearner and NNeuronTrainer classes.
Their production training implementations are not modified. DataFromFile is not
restored. All Python and PowerShell scripts and the controller source live here,
in Scripts of the main repository; Bin contains configurations and input data.

Preparation and provenance

Run prepare.py with Python 3.10 or later. It reads the local archive under
Docs/ClassicStructTrainExperiments, verifies the 22 verbatim configuration files
under Bin/Configs/StructTrainClassic, extracts cached spreadsheet observations,
and writes Prepared/manifest.json plus Reports/StructTrainClassic/archive-evidence.json.
No source Office file or verbatim configuration is edited. Prepared/learner and
Prepared/trainer are documented reconstructions from archived scalar settings,
with fresh native structures instead of previously trained saved states.

The historical data contain 150 Iris examples, 60 cold-training references,
270 directed-retraining references, 32 mode cases and 22 recognition columns.
The 91-pattern archived input sequence covers all 90 directed transitions.
Incomplete worksheet cells and incomplete final output recordings are not filled.
The preliminary erroneous 0/(1(2)+4) implementation cannot be recovered uniquely;
its source gap is reported instead of substituting the corrected algorithm.

Build

Use build.ps1 with the installed Qt root and a bootstrapped vcpkg checkout whose
versions database contains the manifest baseline. A stale checkout can know the
baseline commit while still lacking its package versions in its working tree.
This execution uses an isolated dependency checkout at .deps/vcpkg-tool, at the
manifest baseline 5cad485d1ddb649c8fa1022bf0b3908555e6e6ba. The existing E:\vcpkg
working tree is preserved. Z_VCPKG_ROOT_DIR must be cleared when changing the
toolchain root in an already configured build directory; build.ps1 handles it.

The native binary is built with the same runtime libraries as NeuroModelerConsole
and is placed in Bin/Platform/Win. Executables are run with that working directory,
as expected by existing system resources and the shared test initialization.
Object files remain in the preset's build directory. build.ps1 enables the
Release-only NMSDK_CLASSIC_RUNTIME_DIR override for the three relevant targets.
Before replacing the existing runtime, this execution saved binaries, settings
and relevant DLLs under .git/classic-struct-train/runtime-backup.
Release is mandatory. build.ps1 rejects Debug presets and a Debug build of the
controller refuses to run experiments, even when invoked directly.

Commands from the repository root

  python Scripts/ClassicStructTrain/prepare.py
  python Scripts/ClassicStructTrain/test_archive.py
  powershell -File Scripts/ClassicStructTrain/build.ps1
  python Scripts/ClassicStructTrain/run.py --suite smoke --repeats 1
  python Scripts/ClassicStructTrain/run.py --suite all --repeats 3 --jobs 4 --output Reports/StructTrainClassic/run-unique
  python Scripts/ClassicStructTrain/evaluate.py Reports/StructTrainClassic/run-unique
  python Scripts/ClassicStructTrain/plot.py Reports/StructTrainClassic/run-unique
  python Scripts/ClassicStructTrain/audit.py Reports/StructTrainClassic/run-unique

Use the bundled Python executable in Codex. On this machine -I ignores an
incompatible inherited PYTHONHOME; extraction and supervision need no third-party
packages. plot.py uses the task-local .deps/classic-plot-python packages:
matplotlib==3.10.0, numpy==2.2.6, contourpy==1.3.2 (plus wheel dependencies).
It never recomputes or substitutes simulation measurements.

Evidence and interpretation

Every job preserves its binary and manifest hashes, exact command, stdout,
stderr, exit code, runtime and timeout status. results.jsonl records cases;
iterations.jsonl records iteration boundaries. waveforms.jsonl captures the
learner-111 soma trace for control plots. An existing output folder is not reused.
The watchdog detects a lack of measurement progress rather than counting log spam.
Up to four independent processes can run in parallel. Recognition is split by
input model to keep jobs bounded. Each process has its own application history
name, and shuts down AppCore before Qt is destroyed. Preliminary interrupted
or failed probes are preserved separately from the final matrix.

The controller records actual physical segments, synapses and source links in
addition to public structural counters. Observer access uses legal Base::* member
pointers formed in a derived test-only access class; objects remain the original
native classes and there is no unsafe downcast or overridden training method.
After each native iteration it checks IsInit on input segments and their
synapses. Encountering an inert dynamic component is recorded immediately as
uninitialized_dynamic_structure; continuing to adjust counts on that graph
cannot establish a valid training result. The unmodified console reproduced the
same divergent structure in the independent 24-model-second control probe.
Archived frozen recognition variants are explicitly labelled reconstructed
structures and are separate from newly trained native models.
All 22 recognition columns have an individual archived structure reference.
This additional deterministic frozen-structure control runs once; native cold,
warm, structure, recognition-training, mode and two-example attempts use the
requested repeat count. A static reconstruction activates requested synapses
and completes an UnInit/Init lifecycle before recognizing; it does not repair
the production algorithm's dynamic training path.

DataFromFile and runtime blockers

The target PulseLib revision is 9f3c5131192521d23b77be062ebd9b97298f50d9.
In this revision, native training adds synapses without initializing them.
The available history includes a later change addressing this problem:
fcaa96964567f8d26d13ce27b32624ed4029817b, 2026-09-27,
"Initialize dynamically added training synapses". It was not cherry-picked:
it also contains algorithm changes, which are outside the agreed replay scope.
The full report records failed prerequisites rather than claimed convergence.

Classification meanings in report.html and comparison.csv:
  match       the checked result matches an archived variant or a control
  difference  a completed measurement differs from its reference or control
  recorded    an actual trace has been preserved without a scalar pass claim
  source_gap  the historical reference or implementation is insufficient
  incomplete  a native case failed, timed out or produced no complete result

The primary acceptance criterion is the final trained structure: dendrite
lengths and synapse counts, backed by a consistent initialized physical graph.
Iteration counts and recognition answers are secondary measurements and do
not change a structural match into a difference. structure-comparison.csv
places observed vectors next to their archived references and explicitly marks
intermediate_at_stop, final_trained, unavailable and reference_reconstruction.
An incomplete training attempt never establishes a final structural match,
even if its intermediate counters happen to equal an archived structure.
Frozen archive models verify a supplied reconstruction; they are not counted
as structures obtained by the training algorithm. Exact 150-answer differences
are retained separately in answer_mismatches_min for diagnostic use.

Accuracy and balanced accuracy are separate. The historical (TP%+TN%)/2 is
balanced accuracy. Empirical risk is (FP+FN)/N. Model time from iteration count is
I/f, not I*f. Per-pattern stopping limits are 1000 iterations and 600 wall seconds.
Differences are reported without tuning the production algorithm to archive values.

Git history of DataFromFile

NNeuronLearner was first added in PulseLib commit
0b03edb48b74dc5c5bef22405fef209ece4a9b0e on 2023-10-10, already without
DataFromFile/TreatDataFromFile and with ExperimentMode/ExperimentNum. Searches of
the available full repository history do not identify a removal commit or its
reason. The older archive preserves a sequential training implementation and
several scenario-specific file-reader variants. ExperimentNum=1 remains a file
recognition path on autoPreset; it is not equivalent to sequential retraining.

Saved-state checks and scientific comparisons (23 November 2026)

The final scientific report is ScientificComparisons.docx and its editable
comparison workbook is ScientificComparisons.xlsx, both under
Reports/StructTrainClassic/outputs/01a20798-0fce-7661-bd9d-b3506770ffc9/ScientificComparisons.
These supersede the earlier LegacyChecks report for interpretation of the
historical scientific graphs. The final report contains 15 direct historical
comparisons and three explicitly conditional waveform comparisons.

Source [1] is the unchanged local workbook
Docs/ClassicStructTrainExperiments/Эксперименты/Инофрмация о длинах дендритов и числе синапсов.xlsx.
Its 145 structural records and variants include 14 complete reconstructions
and 131 records with insufficient synapse counts. It supplies structures;
historical recognition measurements have separate source references.

The versioned evidence includes extracted source data, aggregate assessments,
completed-process records, chart source images, native Excel chart exports,
and the final audit results. Full runtime XML copies, waveform logs, dependency
directories and document rendering caches remain local. The unchanged source
archive is also local; preparation/source-inventory.json records its hashes.
Office regeneration uses the bundled artifact-tool runtime, Python document
libraries and Microsoft Excel. Recorded absolute paths describe this execution.

The 335 completed processes, nine original states and 70 reconstructions were
measured on the recorded autoPreset revisions. Commit packaging is on the
separate classic-structtrain-validation branches in this repository and Bin.
The execution audits retain their original strict checkout requirements;
their recorded results describe that execution, not a newly trained model.
Additional studies of training and physical causes of discrepancies are deferred.
