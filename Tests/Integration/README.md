# Integration Tests Quick Memo

## RU

## Non-Interactive Default (recommended)

Use this mode for CI/local checks without GUI windows:

```bash
cd /path/to/Nmsdk
mkdir -p build/Debug
cd build/Debug
cmake /path/to/Nmsdk \
  -DCMAKE_BUILD_TYPE=Debug \
  -DBUILD_TESTS=ON \
  -DBUILD_TESTING=ON \
  -DRDK_BUILD_LEGACY_ENGINE_UNIT_TESTS=ON \
  -DNMSDK_ENABLE_INTERACTIVE_GUI_TESTS=OFF
cmake --build . --parallel
ctest --output-on-failure -j8
```

## Full Run With GUI Tests

Enable only when you explicitly need GUI integration coverage:

```bash
cd /path/to/Nmsdk/build/Debug
cmake /path/to/Nmsdk -DNMSDK_ENABLE_INTERACTIVE_GUI_TESTS=ON
cmake --build . --parallel
ctest --output-on-failure -R "MenuBarTest|QMessageBox|PluginLoadingTest|UModernDiagramWidgetMovementTest"
```

GUI tests can open windows and may require a real desktop session.

## Useful Focused Runs

```bash
# PulseLib integration
ctest --output-on-failure -R "PulseLib_StorageComponents"

# Config validation only
ctest --output-on-failure -R "ConfigValidationTests"
```

---

## EN

## Non-Interactive Default (recommended)

Use this mode for CI/local checks without GUI windows:

```bash
cd /path/to/Nmsdk
mkdir -p build/Debug
cd build/Debug
cmake /path/to/Nmsdk \
  -DCMAKE_BUILD_TYPE=Debug \
  -DBUILD_TESTS=ON \
  -DBUILD_TESTING=ON \
  -DRDK_BUILD_LEGACY_ENGINE_UNIT_TESTS=ON \
  -DNMSDK_ENABLE_INTERACTIVE_GUI_TESTS=OFF
cmake --build . --parallel
ctest --output-on-failure -j8
```

## Full Run With GUI Tests

Enable only when you explicitly need GUI integration coverage:

```bash
cd /path/to/Nmsdk/build/Debug
cmake /path/to/Nmsdk -DNMSDK_ENABLE_INTERACTIVE_GUI_TESTS=ON
cmake --build . --parallel
ctest --output-on-failure -R "MenuBarTest|QMessageBox|PluginLoadingTest|UModernDiagramWidgetMovementTest"
```

GUI tests can open windows and may require a real desktop session.

## Useful Focused Runs

```bash
# PulseLib integration
ctest --output-on-failure -R "PulseLib_StorageComponents"

# Config validation only
ctest --output-on-failure -R "ConfigValidationTests"
```
