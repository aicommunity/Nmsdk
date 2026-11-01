# Сборка и проверки C++-проб TimeLearner на удалённом Linux

Дата: 2026-10-08. Сборка выполнена только на сервере `10.245.1.11`, в изолированном audit checkout `/home/user/Nmsdk_timelearner_audit_20261008`. Локальная машина для сборки и экспериментов не использовалась.

## Проверенная область

Проверки компилируют неизменённые тела C++-гейтов и регуляторов с узкими тестовыми адаптерами. Python-генератор лишь извлекает C++-фрагменты для компиляции; решения обучения и состояние тренеров в скрипты не переносились.

Канонические SHA-256 после нормализации только переводов строк совпали с зафиксированным PulseLib commit `1ff482cb08af70c1acc22ec1c80dcb4c7359206c`:

| C++-файл | SHA-256 |
|----------|---------|
| `NNeuronTimeLearner.cpp` | `352d6a7eb78a296648d34cbb620319206855e64b851a071f84201dc5214b6236` |
| `NNeuronTimeLearner.h` | `b1a9abb22b6dbedb138501ec0da3eccaa4afbe32773fe71b5a11eeb94b9ba613` |
| `NNeuronTimeLearnerBranch.cpp` | `dc317826ebef0d87446b99fb3b1a918a2bbff91b5216ede63df6b3aded210d5f` |
| `NNeuronTimeLearnerBranch.h` | `ccb6966b6466080bfa6e06431663bdceb630cb3514df8a295967918054498629` |

Использованные файлы audit-probes взяты из зафиксированного root checkout; CMakeLists SHA-256 `8ac1e651b55f395952e43bba7021ae82b789b0ab78faa3a2c1feeaef6e61aaa3`, генератора training probes — `f7012246de7f1cead7e2d50abf893c9f05267ce9db782a5bf89650ae3303a7ee`.

## Сборка и результат

```bash
cmake -S Scripts/audit-probes -B build/timelearner-audit-20261008 \
  -G 'Unix Makefiles' -DCMAKE_BUILD_TYPE=Release \
  -DGTEST_SOURCE=/home/user/Nmsdk_timelearner_audit_20261008/build/linux-gcc-release-local/_deps/googletest-src \
  -DQt5_DIR=/usr/lib/x86_64-linux-gnu/cmake/Qt5

cmake --build build/timelearner-audit-20261008 \
  --target audit_training_core audit_branch_update audit_existing_gui audit_counterexamples \
  --parallel 8

ctest --test-dir build/timelearner-audit-20261008 --output-on-failure \
  -R '^(existing_gui|training_core|branch_update)$'

build/timelearner-audit-20261008/audit_counterexamples \
  --gtest_filter=-AxonAudit.PositiveTauShouldNotDivergeWithoutAStabilityGuard
```

Все четыре targets собраны. CTest: **3/3 группы PASS** (`existing_gui`, `training_core`, `branch_update`). `audit_counterexamples`: **12/12 PASS**. Единственный отфильтрованный A12 (`PositiveTauShouldNotDivergeWithoutAStabilityGuard`) остаётся заранее известным диагностическим случаем без stability guard; фильтр указан в существующем README и не маскирует результат обязательного набора.

`training_core` покрывает Classic epsilon и SyncTol/invalid peak, границу Rmin length slack, требование peak attempt для dead-tip gate, направление/границы TipR и однократное применение роста длины; Branch — reverse-order выбора, EOL по всем импульсам, настройку только активного импульса, направление TipR, ограниченный рост длины и нормализацию reference `L=0` в физический `L=1`. **11/11 этих проверок PASS**. В `branch_update` **8/8 PASS**, включая fallback и недопуск NaN/setup failure в опубликованные метрики.

## Вывод и границы

В проверенных контрактах не обнаружен дефект epsilon, границ допуска, validity peak, TipR, применения роста длины, active-pulse/reverse-order или reference anchor. Это не доказывает корректность полного production lifecycle и не объясняет 26 исторических `Need=1`: тесты не заменяют ограниченные runtime-прогоны. Поэтому алгоритм и quality gates не менялись; незавершённые D-кейсы остаются «недостаточно данных».

