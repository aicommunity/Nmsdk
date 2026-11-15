# Windows build bootstrap

This is a build profile, not an admitted scientific worker. The Linux process,
reservation, runtime-capture and publication implementations do not thereby
support Windows. Do not run the existing managed pipeline with weakened checks.

The separate vcpkg manifest pins the inspected registry revision and uses Qt5,
matching the current Linux experiments. It supplies the required Charts, Svg,
SerialPort and test libraries without installing optional Qt WebEngine, OpenCV,
Python or the embedded LLM. These exclusions concern build features, not neuron
physics. Configure with RDK_USE_LLM=OFF, QT_MAJOR=5 and BUILD_TESTING=ON.

Use a new source checkout with exact gitlinks, a new build/runtime/output root,
MSVC x64 from VS2026 and Ninja. Set VCPKG_MANIFEST_DIR to this directory,
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
inside `C:/Projects/TimeLearnerWorker`; it refuses an existing checkout and reads
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
negative result and bound records, compares the entire physical SDK namespace,
dependency/tool inventories and runtime before/after, and checks the selected
executable hashes. It executes no compiled test. An independent successful audit
does not rewrite `build_accepted=false` or excuse remaining descendants.

`validate-native.py` consumes that exact audit and the unchanged source/runtime.
It invokes the **production schema4 native gate and Windows Job backend from the
compiled SDK**. It does not replace the backend with a test copy. Complete actual
JUnit inventory, cooperative loaded-module capture, owned-process closure and
source/runtime preservation are required. Its `native_checks_passed` remains
separate from scientific-worker admission and the original build outcome.
The backend reports Job committed-memory semantics; a thread-count limit is not
claimed. Specify the native wall/memory/process budgets for each new attempt.

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
native primary data still require their separate Git publication; the linked
metadata receipts alone do not constitute that full archive.
