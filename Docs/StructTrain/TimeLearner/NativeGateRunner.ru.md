# Декларативный запуск native CI checks

Команда native-gate SPEC.json --output NEW_DIRECTORY использует production
owned process_runner и неизменяемый заранее собранный runtime. Она не выполняет
checkout, сборку, изменение конфигурации либо восстановление модели. SPECschema1
kind timelearner_native_test_gate содержит runtime_manifest, source_root,
expected_test_ids (Suite/Case), maximum_wall_seconds и asan_options.
Input paths разрешаются относительно SPEC; output не может пересекать source
или runtime. Loader environment берётся из runtime manifest и восстанавливается
после операции. Фильтр строится из exactIDs, без shell и glob-инференции.

Проверяются реальные loaded-file capture, exitcode/JUnit agreement, точное
множество всех случаев, totals и отсутствие skipped/uncompleted cases. Полный
failed JUnit является валидным наблюдением неуспешного тестирования; timeout,
обрыв или missing case не становятся PASS. Assertion status, execution и
validity разделены. Scientific verdict всегда null. Источники сверяются с
runtime source_closure до и после процесса. Нельзя менять их пока job работает.

Spec search-termination-configured-native-v1.json объявляет34 source-reviewed
IDs; пути-заполнители нужно заменить на действительные runtime/source. Это
native service, configured/XML/Copy, repeatedN0 и четыре completed-boundary
transfer controls. Набор нужен для обнаружения регрессий, а не для заявления
сходимости всех моделей.
Параметризованные/slash-containing GTest IDs пока явно не поддерживаются;
unknown/дублирующие IDs отвергаются. Generated Python launchers не нужны.

## Приёмка запускателя 2026-11-02

Код запуска: `96c74a899e85e1a105b131855161d749e10f7ea4`; код reader tests:
`fcf8a3e424289adf6bd6c3ca7079dfb1fe358449`. Численный runtime имеет другую,
явно записанную source closure: root `24d1beba2bb58982931a62668a3019dd053e20f8`,
PulseLib `63fd7a9fecbc567fb8e5c690ae58fc73a896de65`. Запускатель не пересобирал его.

- Elder: полный JUnit из 34 случаев, 30 passed / 4 failed. Runner сохранил
  `execution=process_error`, `validity=valid`, `assertion_status=failed`;
  положительного verdict нет. Четыре `NativeLearnedState` случая остановились
  на обязательном сертификате после `maximum_sweeps_exhausted`.
- На обоих workers отдельно прошли два быстрых source-declared native случая
  (nonfinite evidence / invalid search domain), с `completed/valid/passed`.
- Reader: 7/7 на каждом worker, без skipped. На Elder использован реальный
  failed JUnit из 34 случаев; на M40 — реальный passed JUnit положительного
  контроля. Проверены перестановка декларации, повреждённые/дублирующиеся ID,
  skipped/unfinished, totals, обрыв XML, валидное наблюдение assertion failure,
  восстановление присутствующих и отсутствующих env после исключения.
- M40 loaded-file receipt содержит настоящий libasan. Полный ASan набор из
  34 случаев на момент этой приёмки ещё выполнялся и в неё не включён.

Первичные данные и все member hashes доступны через Git:

| Данные | Полный commit | Архив |
|---|---|---|
| Elder 34 + positive 2 + reader 7 | `946fbb10ec11d19d1677547501023db29d7634b8` | `Reports/StructTrain/TimeLearner/s07-native-gate-configured-normal-a1`, 643 members, 1,693,314 bytes |
| M40 positive 2 + reader 7 | `9ce3f8e7d0b3262dd6970bd39168cb34443cb842` | `Reports/StructTrain/TimeLearner/s07-native-gate-asan-reader-a1`, 20 members, 22,518 bytes |

После fetch обе публикации проверены локально по SHA256SUMS, hash архива и
полному множеству member hashes. Неудачная подготовка Elder с abbreviated
remote SHA сохранена отдельно; она не запускала native tests.

Это приёмка ограниченного инструмента выполнения/чтения. Четыре failed
transport fixtures остаются открытым результатом алгоритмической ветки.
Изменение их контракта должно сохранить исходные допуски, фактический граф,
диагностический статус и проверку переноса с временными откликами; нельзя
обойти guard completed-Train recognition либо объявить BudgetExhausted Exact.
Читатель запускается на workers так:
`TIMELEARNER_NATIVE_GATE_DIR=/path/to/actual/result python3 -m unittest Scripts.StructTrain.TimeLearner.tests.test_native_gate`.
Произвольные XML dialects, parameterized IDs, scheduler/leases и полная
матрица алгоритмов этим подэтапом не принимаются.


## Явная изоляция тестов по процессам (кандидат)

`python -m Scripts.StructTrain.TimeLearner.native_partition declaration.json --output /absolute/fresh-output` принимает отдельную схему `timelearner_partitioned_native_gate`, schema_version=1. Поля: native_gate (полная исходная schema2 cooperative gate declaration), maximum_total_wall_seconds и maximum_case_wall_seconds. Все ожидаемые test IDs задаются явно; автоматических повторов, пропусков и переноса PASS из другой попытки нет. На этом этапе принимается только child schema2 с cooperative_runtime_capture=true; schema1/3 для нового режима не заявлены.

Каждый ID выполняется существующим production run_native_gate в отдельном процессе. Сохраняются cases/NNNN/native.xml, native traces, process identity, loaded files и process result, точная declaration и progress. Исходная монолитная схема и исходные тесты не меняются. Общий и индивидуальный wall budget записаны явно, численные tolerances не меняются. Runtime проверяется каждым child gate и после всех partitions.

Производный native.xml объединяет только полные индивидуальные XML, с точным множеством IDs и без повторного использования process identity. junit-sources.json связывает каждый test ID с исходным XML/hash/PID/start/boot. Итог имеет отдельный kind timelearner_partitioned_native_gate_result; общего process/result.json не создаётся. Пропуски, повреждённые XML и invalid runtime запрещают PASS.

native/ — lossless hardlink-представление для существующих readers, native-projection.json хранит происхождение каждого файла. Одинаковые имена с различающимся содержимым вызывают явный отказ; перезаписи и выбора «последнего» нет. Первичными остаются отдельные cases/NNNN. Даже при отказе формирования reader view индивидуальные наблюдения сохраняются.

Режим предназначен для повторной полной ASan304 проверки после internal StackStore CHECK длинного процесса; это изменение протокола запуска, не доказательство исправления алгоритма или отсутствия утечек. Требуются реальные двухпроцессные адресные проверки и полная304 матрица на M40. До них модуль — непроверенный кандидат.
