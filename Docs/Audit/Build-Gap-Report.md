# Build Documentation Gap Report

Generated: 2026-07-27 (Track 6 refresh)

## Documented targets in Build-System.md

- `rdk.static.qt`: doc=yes, cmake=n/a
- `Rdk-BasicLib.qt`: doc=yes, cmake=n/a
- `Rdk-CvBasicLib.qt`: doc=yes, cmake=n/a
- `Rdk-HardwareLib.qt`: doc=yes, cmake=n/a
- `Nmsdk-MotionControlLib.qt`: doc=yes, cmake=n/a
- `Nmsdk-PulseLib.qt`: doc=yes, cmake=n/a
- `NeuroModeler`: doc=yes, cmake=yes
- `NeuroModelerConsole`: doc=yes, cmake=yes
- `llm-index-pack`: doc=yes, cmake=n/a

## Documented options in Build-System.md

Source of truth: `cmake/RdkDefines.cmake` (+ root/`Libraries` `option()`).

- `RDK_USE_LLM`: doc=yes, cmake=yes (`cmake/RdkDefines.cmake`)
- `RDK_USE_OPENCV`: doc=yes, cmake=yes (`cmake/RdkDefines.cmake`, default OFF)
- `NO_MOTION_CONTROL`: doc=yes, cmake=yes (`cmake/RdkDefines.cmake`, default ON)
- `RDK_LLM_BUILD_EMBEDDED`: doc=yes, cmake=yes (`cmake/RdkDefines.cmake`; preset may set OFF)
- `NMSDK_MOTIONCONTROLLIB_BUILD_CORE_ONLY`: doc=yes, cmake=yes
- `NMSDK_PULSELIB_BUILD_CORE_ONLY`: doc=yes, cmake=yes
- `BUILD_TESTS`: doc=yes, cmake=yes
- `NMSDK_FORCE_QT_FROM_VCPKG`: doc=yes, cmake=yes

## Notes

Prior audit (2026-06-06) marked `RDK_USE_LLM` / `RDK_USE_OPENCV` / `NO_MOTION_CONTROL` as `cmake=no` because the scanner missed `cmake/RdkDefines.cmake`. Build-System.md defaults were synced to `option()` on 2026-07-27.
