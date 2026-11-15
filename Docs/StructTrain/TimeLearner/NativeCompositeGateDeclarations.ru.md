# Поддерживаемые перечни C++ проверок

Для `Test_PulseLib_StorageComponents` сохранены явные native-gate declarations:

- `Scripts/StructTrain/TimeLearner/specs/native-controller-scalar-regression-v1.json`:
  74 BoundedTraining +23 Final/Clock, 97 уникальных IDs;
- `Scripts/StructTrain/TimeLearner/specs/native-composite-training-core-v1.json`:
  46 новых `NativeCompositeTraining` IDs.

Первый перечень сверён с фактическим compiled inventory и JUnit принятой
mechanical A2 (`917b94627c1290517c61774698b16c01995c849c`). Второй закрепляет
объявленную матрицу нового алгоритма; её runtime-приёмка ещё не завершена.
Эти JSON не заменяют исходные runtime manifests и не запускают эксперименты.
Пути `REPLACE_WITH_ACTUAL_*` требуют действительных источников и runtime.

Не строить рабочий перечень одним regex по `TEST(...)`: тело макроса
`TEST(TrainingInvalidBudget,name)` не является реальным test ID, а четыре
его развёртки обязаны присутствовать по отдельности. Для любой сборки сверять
ожидаемый набор с фактическим `--gtest_list_tests`, затем с полным JUnit.
Пропуск, duplicate, failure или skipped не дают положительной приёмки.

Допускается независимый запуск случаев новым job spec на неизменном runtime
через существующий `native-gate`. Итоговый наблюдённый набор должен точно
покрывать объявленную матрицу; успех отдельных процессов не подменяет полноту.
При разделении сохранять все per-process manifests, логи, XML и closure.
Успех split-запусков не доказывает отдельный сценарий исполнения всей матрицы
в одном процессе.

Изменение source-кода, declaration и build/runtime создаёт новую попытку;
исторический отрицательный gate не исправляется задним числом. Список IDs
является постановкой проверки, а не доказательством выполнения тестов,
сходимости обучения или качества классификации.
