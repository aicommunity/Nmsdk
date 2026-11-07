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
