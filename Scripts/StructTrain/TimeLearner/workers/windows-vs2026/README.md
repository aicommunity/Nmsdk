# Windows build bootstrap

This is a build profile, not an admitted scientific worker. The Linux process,
reservation, runtime-capture and publication implementations do not thereby
support Windows. Do not run the existing managed pipeline with weakened checks.

## Explicit C/D worker workspace (2026-11-28)

The maintained profile is also used with the installed VS2022 toolset on .8.
Its historical directory name does not choose the compiler: record the actual
Visual Studio root, compiler bytes, vcpkg revision and installed status in each
specification. The pinned Qt5 dependency manifest and triplet remain unchanged.

An absent `worker_root` retains `C:/Projects/TimeLearnerWorker` for existing .14
specifications. New .8 specifications explicitly set
`worker_root: "D:/Projects/TimeLearnerWorker"`. Build, closed-build audit and native
validation readers use that recorded root; an optional `--worker-root` must
agree. Source preparation accepts only these two private workspaces and keeps
its reparse, exact namespace, Git identity and existing-checkout checks.

For D, record `launcher_python` as the actual `{path,size,sha256}` of the installed
Python executable; the old C Python default stays unchanged. The optional
`launcher_logon_type` is 2 (the original default) or 3 (interactive token).
The launcher still refuses any active TimeLearner task; dependency preparation
must finish before a new SDK build starts. Put installed dependencies, buildtrees,
packages, downloads, binary cache, source, runtime and experiment outputs on D.
Do not update the global vcpkg installation or old runtime to prepare a new job.

Validate both the pure declaration controls and `WindowsWorkerRootActualTest`
on the actual worker with `TIMELEARNER_WORKER_METADATA_ROOT` set to its C/D root.
This is metadata validation, not a C++ build or scientific result.

The separate vcpkg manifest pins the inspected registry revision and uses Qt5
from the original Windows bootstrap. Current Linux workers also use Qt6;
record the actual Qt/compiler/runtime for cross-platform comparisons.
The manifest supplies the required Charts, Svg,
SerialPort and test libraries without installing optional Qt WebEngine, OpenCV,
Python or the embedded LLM. These exclusions concern build features, not neuron
physics. Configure with RDK_USE_LLM=OFF, QT_MAJOR=5 and BUILD_TESTING=ON.

Use a new source checkout with exact gitlinks, a new build/runtime/output root,
MSVC x64 from the declared VS2022/VS2026 toolset and Ninja. Set VCPKG_MANIFEST_DIR to this directory,
VCPKG_OVERLAY_TRIPLETS to its triplets directory and
VCPKG_TARGET_TRIPLET=x64-windows-tl. The triplet builds Release dependencies only;
use CMAKE_BUILD_TYPE=Release. This restriction applies to the target triplet.
The first bootstrap leaves VCPKG_HOST_TRIPLET at its native x64-windows default;
host tools can therefore build Debug and Release dependencies separately. These
host DLLs are not the declared application runtime. Record both resolved triplets
and do not describe the first bootstrap as a Release-only host dependency build.
VCPKG_ROOT and the toolchain must identify the same
registry. Record its actual commit, compiler version, commands and dependency
build logs. Begin with VCPKG_MAX_CONCURRENCY=1, CMAKE_BUILD_PARALLEL_LEVEL=1,
NMSDK_BUILD_PARALLEL_JOBS=1 and cmake --build --parallel 1.

Initial targets: NeuroModelerConsole, Test_PulseLib_ProbeAlgorithms and
Test_PulseLib_StorageComponents. A configured GUI target or a successful link is
not evidence of a working experiment. Keep the original C:/Projects/Nmsdk copy
and its branches unchanged. Transfer project sources and results through Git.

Before scientific use, independently verify executable and loaded DLL identity,
native lifecycle/storage and impulse response, complete observation windows,
model export/import, owned process containment/cancellation and the production
reader/publisher. Windows/Linux numerical comparisons need explicit tolerances;
do not replace a failed exact-waveform comparison with a silent tolerance.

Declare the compiled-platform test cohort before execution. The literal TEST
inventory intentionally does not interpret C++ preprocessor conditions. In
particular, `NativeJobSourceTransport/SymlinkSourceCannotReplaceTheOwnedSnapshot`
is guarded by `#ifndef Q_OS_WIN`: retain it on Linux and record its exact source
hash and guard as an explicit Windows exclusion. Keep this exclusion separate
from failed, skipped or missing tests; none is a PASS. A JUnit expected-set
mismatch rejects the gate and must not be repaired retrospectively. Preserve
the failed attempt, prepare a new declaration and run all declared cases.


## Private .14 preparation (2026-11-08)

Keep build acceptance and scientific-worker admission separate. The existing
root818dd80/Pulse3accbed private Release artifacts compiled successfully, but
the original owned execution was rejected for remaining descendants. A later
bounded Ninja check reported no work while the unchanged backend again rejected
remaining conhost/PowerShell processes. Preserve both failures.

The installed VS18 `Common7/Tools/VsDevCmd.bat` guards its asynchronous
`Send-VsDevShellTelemetry` PowerShell launch with `VSCMD_SKIP_SENDTELEMETRY`.
For a new controlled headless build, set `VSCMD_SKIP_SENDTELEMETRY=1` in the
owned batch **before** calling vcvars. Record this process-local environment
choice, the actual installed script hash and backend result. Do not alter
machine settings, ignore remaining descendants, or infer the old process's
command line from this script alone. The flag does not itself admit the worker.

A short existing-build diagnostic may use a separately declared memory budget;
it is not a full-build budget. The observed earlier no-op Job peak was
99,479,552 bytes. A separate diagnostic with the VS flag and 256 MiB of Job committed memory
passed with the unchanged 256 MiB host reserve: no work, no remaining descendants,
all processes closed and source/three runtime inventories unchanged. This changed
two declared conditions; it is not a single-factor causal experiment. Its 120 s
wall limit, source/runtime hashes and owned-process closure remained mandatory.
See `Docs/StructTrain/TimeLearner/WindowsDomainBoundedBuildA5Verification.json`. Do not use
that quota silently for native experiments or unexpected recompilation.

The prepared 18 native portability checks retain their distinct 3 GiB quota
and 256 MiB physical-memory reserve. Check actual free memory before dispatch:
a reading of 690,614,272 available bytes cannot admit that job. Do not stop
unrelated applications to make admission pass. Kernel closure, loaded DLL
identity, exact test inventory and original negative evidence remain required.
These checks target the root818/Pulse3acc snapshot, not the newer FCC matched-
omission implementation. They do not certify complete scientific experiments.

## Exact private SDK preparation

`GitPreparation.psm1` and `verify-sdk.ps1` validate an explicitly declared root
commit, its actual submodule closure and the complete physical source namespace
from a Git blob. They reject extra files, changed bytes, missing repositories and
reparse directories. `Complete-PreparedGitClone` only completes an unborn clone
inside the declared C/D `Projects/TimeLearnerWorker` workspace; it refuses an existing checkout and reads
long sparse specifications from Git blobs rather than a command-line JSON value.
Native exit codes must equal zero, including signed Windows failures. PowerShell
5.1 native stderr records are diagnostics, never part of an OID/JSON return value.

Run `test-git-preparation.ps1` with fresh `-OutputDirectory`, `-SdkRoot`,
`-SdkCommit` and `-SdkNamespaceBlob`. The actual .14 package6 preparation passed
11 checks, including 4052 SDK files/eight repositories and a 322-pattern fixture;
the two preceding negative attempts remain in the report. See
`Docs/StructTrain/TimeLearner/WindowsPackage6SDKPreparation-20261109.ru.md`.
These checks do not compile C++, run a model, or admit a scientific worker.

## Closed-build audit and native validation (2026-11-10)

`launch-sdk-build.ps1` dispatches one fresh scheduled attempt. Its optional
`-WorkerName` selects `sdk-build.py` (the default), `audit-closed-build.py`, or
`validate-native.py`. Every choice binds the exact tool commit, specification
Git blob and worker/Python hashes. The launcher refuses an existing attempt,
existing output, or another active TimeLearner task. Keep sources, resources,
build and runtime separate, and do not edit a running attempt.

`audit-closed-build.py` audits artifacts from a terminal owned build. It requires
the original main process and named Job to be absent, verifies the original
result and bound records, compares the entire physical SDK namespace,
dependency/tool inventories and runtime before/after, and checks the selected
executable hashes. It executes no compiled test. An independent successful audit
does not rewrite `build_accepted=false` or excuse remaining descendants.
It accepts a successful build only with `build_accepted=true`, execution
`completed`, integer exit code zero, valid observations and whole-Job closure.
Its historical recovery case remains restricted to the original negative
`descendants_remaining` result with zero exit code and subsequent kernel absence.
The audit records the actual original acceptance value in either case.

Audit specification version2 explicitly binds the build's `dependency_layout`.
It uses the same producer resolver for `short_readonly_D`; only the immutable
installed tree may be outside the private D worker. Source, runtime, output,
original build records and locks retain their private boundaries. Version1
keeps the original private dependency layout. The complete before/after
dependency inventory and the original layout binding remain mandatory.

`validate-native.py` consumes that exact audit and the unchanged source/runtime.
It invokes the **production schema4 native gate and Windows Job backend from the
compiled SDK**. It does not replace the backend with a test copy. Complete actual
JUnit inventory, cooperative loaded-module capture, owned-process closure and
source/runtime preservation are required. Its `native_checks_passed` remains
separate from scientific-worker admission and the original build outcome.
The backend reports Job committed-memory semantics; a thread-count limit is not
claimed. Specify the native wall/memory/process budgets for each new attempt.

The dedicated `prepared_count_training` launch declaration version1 retains
8 GiB for each preflight and16 GiB for Train. Version2 requires explicit integer
`preflight_memory_bytes` and `native_memory_bytes`, within the production Windows
backend's 32 MiB–64 GiB range. It changes no model, search, tolerance or wall-time
condition. There is no automatic fallback when memory is unavailable: the backend
still checks available physical memory and verifies Job limits before resuming
the process. Declare a fresh attempt when changing resource limits, preserving
any rejected predecessor. Record the actual phase limits with the attempt.

Initialize every new standalone controls Git repository with a tracked
`.gitattributes` containing `* -text` before its first add. System Git on
Windows can otherwise normalize CRLF metadata and command files. Preserve
actual archived bytes and Git blobs separately when auditing an older control
bundle; identify any exact EOL-only differences explicitly. Do not rewrite
the inputs or controls commit of a running experiment to repair its history.

Validation specification version2 declares `partitions`: each has a unique
safe name, exact `expected_test_ids` and `maximum_wall_seconds`. Their disjoint
union must equal the complete top-level test inventory, and their wall limits
must fit the top-level limit. Each partition uses a fresh native Job and output;
the worker stops at the first failed or invalid group. Version1 retains its
single-gate layout. This supports the declared SDK cohorts without combining
tests that were intended to run in separate processes.

Read-only Python observers must use `python -B` or set
`sys.dont_write_bytecode=True` before importing SDK modules. A generated
`__pycache__` changes the physical source namespace even when Git ignores it.
Do not weaken namespace verification to hide such files. Reconciliation is
allowed only after confirmed job closure and verification of every declared
source byte; preserve the failed audit and identify each removed cache file.

Actual scope on .14: Root `4eb58ccc62204c663dfe2815cda680534fb34353`, Pulse
`f1df2500d43ecab4723d2536cd4a7ce073416feb`. The closed-build audit passed with
4067 SDK files/eight repositories, 17287 dependency files and 62 runtime files
unchanged. A subsequent native gate passed **4/4** Classic/Branch bootstrap and
bound-C0 checks in 340.192 s, captured 48 loaded modules and closed its complete
Job. The original build remains rejected for remaining descendants. See the
[exact scope and receipts](https://github.com/aicommunity/Nmsdk/blob/d539de8cee0af7050eb39185f3b149b08c9318ff/Docs/StructTrain/TimeLearner/NativeRestStateArchive-20261110.ru.md).

These checks do not establish package6 roundtrip, complete Console Train-to-Test,
cross-platform numerical equivalence or classification performance. General
Linux managed-runner, reservation and publication support must not be inferred
from this dedicated Windows native gate. Full compressed audit inventories and
native primary data require publication and independent restoration in the
external M40 archive, with compact verified references in Git; the linked
metadata receipts alone do not constitute that full archive.


Long dependency queues must survive the controlling SSH connection. Use a
registered Scheduled Task with a saved XML definition and launcher, and verify
its owner PID/creation time again after the dispatch connection has returned.
A detached Popen receipt proves only that the process existed at dispatch;
it does not prove that the queue persisted. An unstarted lost queue may be
replaced only after its original owner is absent and both downstream attempt
names are proven unused. Never restart a model merely because an observer or
queue disappeared.

A waiting coordinator may use the distinct `TimeLearnerQueue-*` task prefix;
actual build/audit/native workers retain `TimeLearner-*` and the existing
launcher exclusion and worker lock. The prefix does not grant parallel model
capacity: verify the exact preceding Task, owner and all owned Windows Job
handles are closed before dispatching the next production worker. Preserve
original build rejections when a later independent closed-artifact audit passes.
