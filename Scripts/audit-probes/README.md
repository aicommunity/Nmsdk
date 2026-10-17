# Воспроизведение аудита TimeLearner

**Уточнение 2026-09-24:** ожидаемые PASS ниже воспроизведены, но не закрывают все A01–A16. [Дополнительные контрпримеры](review-20260924/README.md) проверяют непокрытые boundaries/live sampling/verifier.

[Отчёт](../../Docs/Audit/TimeLearner-2026-09-22/README.md). После remediation A01–A11/A13–A16 на текущем HEAD ожидается:

| Цель | Ожидание |
|------|----------|
| `audit_existing_gui` | 13 PASS |
| `audit_counterexamples` без A12 | 9 PASS |
| `AxonAudit.PositiveTau…` (A12) | **FAIL diagnostic** — Euler guard отложен, не quality gate |
| `audit_branch_update` | 8/8 PASS |

Исторический срез аудита (до фиксов): 13 PASS GUI + 10 FAIL CE + 5 PASS/3 FAIL Branch. Не использовать как текущую норму.

## C++ (Linux)

Требуются CMake >=3.19, C++17, Qt5 Core/Gui, Python3, локальные исходники GoogleTest (без сетевых загрузок). Корень superproject:

```bash
cmake -S Scripts/audit-probes -B build/audit-timelearner-make -G "Unix Makefiles" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/usr/bin/gcc -DCMAKE_CXX_COMPILER=/usr/bin/g++ \
  -DGTEST_SOURCE=/home/user/Nmsdk/build/linux-gcc-release-local/_deps/googletest-src \
  -DQt5_DIR=/usr/lib/x86_64-linux-gnu/cmake/Qt5
cmake --build build/audit-timelearner-make --parallel "$(nproc)"

./build/audit-timelearner-make/audit_existing_gui \
  --gtest_output=xml:Docs/Audit/TimeLearner-2026-09-22/after-fixes/gui-tests.xml
./build/audit-timelearner-make/audit_counterexamples \
  --gtest_output=xml:Docs/Audit/TimeLearner-2026-09-22/after-fixes/cpp-counterexamples.xml
# обязательный gate без A12:
./build/audit-timelearner-make/audit_counterexamples \
  --gtest_filter=-AxonAudit.PositiveTauShouldNotDivergeWithoutAStabilityGuard
./build/audit-timelearner-make/audit_branch_update \
  --gtest_output=xml:Docs/Audit/TimeLearner-2026-09-22/after-fixes/branch-tests.xml
./build/audit-timelearner-make/audit_training_core \
  --gtest_output=xml:Docs/Audit/TimeLearner-2026-09-26-review/evidence/training-core-tests.xml
```

`GTEST_SOURCE` на другой машине — путь к исходникам googletest. При наличии Ninja можно `-G Ninja` и каталог `build/audit-timelearner-ninja`.

## C++ (Windows / исторический пример)

```powershell
cmake -S Scripts/audit-probes -B build/audit-timelearner-ninja -G Ninja -DCMAKE_BUILD_TYPE=Release -DQt5_DIR=C:/Qt/5.15.2/msvc2019_64/lib/cmake/Qt5
cmake --build build/audit-timelearner-ninja --parallel 4
```

`counterexamples.cpp` линкуется с реальными `NNeuronPostTrainTune.cpp` и `UModernDiagramLinkRouter.cpp`. `generate_probes.py` / `generate_branch_update_probes.py` извлекают тела функций с SHA256 исходников; lifecycle/IO заменены минимальными адаптерами. CMake перегенерирует probes при изменении исходников.

`audit_training_core` выполняет неизменённые C++-тела EOL-гейтов, TipR-регуляторов, выбора Branch и циклов применения длины через узкие адаптеры. Проверяются epsilon/SyncTol, валидность пика, Rmin/Rmax направления, рост длины и эквивалентность reference `L=0` и физического сегмента `L=1` после `BuildStructure`. Python-генератор только извлекает C++-фрагменты для тестовой компиляции; состояние и логика обучения остаются в C++-тренерах.

## Python

```bash
python3 Scripts/audit_timelearner.py --out Docs/Audit/TimeLearner-2026-09-22/after-fixes/py
```

Импортирует производственные функции классификации; симулятор не запускает. Вывод: inventory.json, counterexamples.json, stored_metrics.json.

### Фиксированный threshold sweep для готовой Test-модели

`run_fixed_threshold_grid.py` клонирует уже подготовленный каталог `Test`, меняет только фиксированный LTZ threshold и запускает отдельный C++ Console на каждую точку. Обучение и PostTune отключены; скрипт не содержит логики тренера. В уникальном `--output-dir` остаются параметры каждой копии, CSV, хэши и сводка `results.json`. После анализа удаляются только крупные сгенерированные `StatisticLog`/`EventsLog` внутри этих копий.

```bash
python3 Scripts/audit-probes/run_fixed_threshold_grid.py \
  --source-test /path/to/prepared/Test \
  --console "$PWD/Bin/Platform/Linux/NeuroModelerConsole" \
  --output-dir /path/to/new-unique-run-dir \
  --analyzer Bin/Configs/SpikeSamples/StructTrain/scripts/selectivity_metrics.py \
  --thresholds 0.1070,0.1075,0.1080,0.1083,0.1086,0.1089,0.1092,0.1095 \
  --parallel 8 --time-s 40
```

Каталог результата должен ещё не существовать. Каждый Console работает в отдельной копии проекта; запускать на машине, предназначенной для экспериментов.

## Branch update

Цель `audit_branch_update`: FinalizePostTuneMid / HandlePostTuneFinishIteration. После remediation — 8/8 PASS (включая NaN, setup failure, fallback metrics).

A07 = calibration-quality контракт. A12 отложен (малый шаг Euler). Они не входят в обязательный план исправлений.
