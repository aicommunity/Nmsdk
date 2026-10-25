---
name: nmsdk-build
description: >-
  Builds Nmsdk PulseLib and NeuroModelerConsole with CMake presets
  (linux-gcc-debug-local). Use when the user asks to compile, rebuild Console,
  PulseLib, cmake --preset, or prepare runtime before StructTrain cold runs.
---

# Nmsdk: сборка Console / PulseLib

## Быстрый путь (StructTrain / cold)

Из корня репозитория Nmsdk:

```bash
# configure once if needed
cmake --preset linux-gcc-debug-local

cmake --build build/linux-gcc-debug-local \
  --target Nmsdk-PulseLib.qt NeuroModelerConsole -j2
```

Полный preset:

```bash
cmake --build --preset linux-gcc-debug
```

## Выходы

- Binary: `<binaryDir>/runtime/NeuroModelerConsole` by default. Experiments use
  an isolated checkout and explicit `-DNMSDK_DEPLOY_ROOT=/path/to/runtime`.
- Resources: `-DNMSDK_RESOURCE_ROOT=/checkout/Bin`; Console accepts `--app-ini`.
- TimeLearner builds/experiments run only on 10.245.1.11/10.245.1.17 via
  10.245.1.12, login `user`. Sources/results are synchronized through Git.
- После сборки для provenance/реестра:

```bash
sha256sum build/linux-gcc-debug-local/runtime/NeuroModelerConsole | cut -c1-16
# или полный SHA-256
sha256sum build/linux-gcc-debug-local/runtime/NeuroModelerConsole
```

Также зафиксировать commit PulseLib (`Libraries/Nmsdk-PulseLib`) и Bin при обновлении реестра.

## Документация

- [`README.md`](../../../README.md) — Build (quick)
- [`Docs/Build-And-Deploy/`](../../../Docs/Build-And-Deploy/) — платформы

## Замечания

- Для cold PASS нужен Console, собранный **после** актуального PulseLib.
- Windows: см. Docs/Build-And-Deploy и vcpkg notes; этот скилл по умолчанию ориентирован на Linux preset.
