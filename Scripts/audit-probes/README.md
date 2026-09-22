# Воспроизведение аудита TimeLearner

[Отчёт](../../Docs/Audit/TimeLearner-2026-09-22/README.md). Производственные алгоритмы не исправляются этим набором. На аудированном HEAD ожидаются 13 PASS существующих GUI-тестов и 10 FAIL контрпримеров первичного среза (A12 теперь отдельно трактуется как большой шаг вне принятого предположения; исправления не требует).

## C++

Требуются CMake >=3.19, C++17, Qt5 Core/Gui, Python3 и локальные исходники GoogleTest. Загрузок из сети нет. Пример из developer shell MSVC, рабочая директория — корень superproject:

```powershell
cmake -S Scripts/audit-probes -B build/audit-timelearner-ninja -G Ninja -DCMAKE_BUILD_TYPE=Release -DQt5_DIR=C:/Qt/5.15.2/msvc2019_64/lib/cmake/Qt5
cmake --build build/audit-timelearner-ninja --parallel 4
$env:PATH = 'C:/Qt/5.15.2/msvc2019_64/bin;' + $env:PATH
& build/audit-timelearner-ninja/audit_existing_gui.exe --gtest_output=xml:Docs/Audit/TimeLearner-2026-09-22/gui-tests.xml
& build/audit-timelearner-ninja/audit_counterexamples.exe --gtest_output=xml:Docs/Audit/TimeLearner-2026-09-22/cpp-counterexamples.xml
```

GTEST_SOURCE по умолчанию указывает на уже имеющийся build/win-vs2019-release/_deps/googletest-src. На другой машине передать -DGTEST_SOURCE=<путь-к-исходникам-googletest>. Пути Qt и генератор также адаптировать к окружению.

Последняя команда возвращает ненулевой код, пока дефекты не исправлены. Это ожидаемый результат контрпримеров, не PASS. Не подключать их как разрешающий quality gate с инверсией результата: после исправления они должны стать PASS.

counterexamples.cpp линкуется с реальными NNeuronPostTrainTune.cpp и UModernDiagramLinkRouter.cpp. generate_probes.py извлекает неизменённые тела analyzer/axon-функций в generated C++ с SHA256 исходников; properties, environment и контейнеры сигналов заменены минимальными адаптерами. Такие проверки подтверждают локальную логику, но не lifecycle/Storage/многоканальную интеграцию Rdk. CMake следит за исходниками и повторно генерирует probes при их изменении.

## Python / документация / сохранённые CSV

```powershell
python Scripts/audit_timelearner.py --out Docs/Audit/TimeLearner-2026-09-22/after
```

Скрипт импортирует текущие производственные функции классификации; симулятор и исследовательские harness не запускает. Вывод: inventory.json, counterexamples.json, stored_metrics.json. Выборка CSV: Selectivity*/**/Test/SelectivityLog/results.csv; архивные Test_* исключены.

Markdown-сканирование: tracked .md восьми репозиториев плюс новые документы именно этого аудита. Проверяются inline ссылки на существующие локальные файлы вне fenced/inline code; внешние URL и anchors не проверяются. Файл verification.json — итог фактически выполненного аудита, а не автоматический результат этой команды.


## Повторная проверка Branch 9a6cee0b

Добавлена цель audit_branch_update. После обычной сборки запустить build/audit-timelearner-ninja/audit_branch_update.exe с --gtest_output=xml:Docs/Audit/TimeLearner-2026-09-22/updates/0a7e65c/branch-tests.xml.

Ожидаемый результат проверенного среза: 5 PASS и 3 FAIL (NaN, setup failure, метрики после fallback). generate_branch_update_probes.py извлекает FinalizePostTuneMid и HandlePostTuneFinishIteration без изменения их тел; lifecycle/IO/setup заменены минимальными адаптерами. Тест с failed finite inference фиксирует silent+Complete+InferenceMidDone как фактическое поведение, не как quality PASS.

A07 принят владельцем как контракт текущей калибровки. A12 отложен при предположении малого шага. Эти пункты не входят в обязательный план исправлений.
