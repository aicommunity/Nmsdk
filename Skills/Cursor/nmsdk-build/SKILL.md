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
  --target Nmsdk-PulseLib.core NeuroModelerConsole -j"$(nproc)"
```

Полный preset:

```bash
cmake --build --preset linux-gcc-debug
```

## Выходы

- Binary: `Bin/Platform/Linux/NeuroModelerConsole`
- После сборки для provenance/реестра:

```bash
sha256sum Bin/Platform/Linux/NeuroModelerConsole | cut -c1-16
# или полный SHA-256
sha256sum Bin/Platform/Linux/NeuroModelerConsole
```

Также зафиксировать commit PulseLib (`Libraries/Nmsdk-PulseLib`) и Bin при обновлении реестра.

## Документация

- [`README.md`](../../../README.md) — Build (quick)
- [`Docs/Build-And-Deploy/`](../../../Docs/Build-And-Deploy/) — платформы

## Замечания

- Для cold PASS нужен Console, собранный **после** актуального PulseLib.
- Windows: см. Docs/Build-And-Deploy и vcpkg notes; этот скилл по умолчанию ориентирован на Linux preset.
