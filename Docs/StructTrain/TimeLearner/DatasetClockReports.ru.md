# Проверка и визуализация dataset-clock observations

`dataset_clock_reports.audit_dataset_clock` читает настоящие C++ record/CSV,
полный declared JUnit и gate result. Проверяет схему, все ожидаемые origins,
условия f/mode/gap/ISI/cutoff, model identities, finite samples, полную grid,
согласованность реальных rising edges и пика/вариации сомы. Сравнение input/soma между
origins не использует численный допуск; типизированная проверка absolute
timestamp допускает только roundoff double. Schema2 явно объявляет contract
origin_and_pulse_program_v1: источник должен сохранить onset, ширину, repeat и
cutoff наряду с origin invariance. Все эти выводы обязаны совпасть с C++ case.
Historical schema1 не объявляла полный набор assertions: её дополнительные
необъяснённые C++ failures остаются unknown, а не превращаются в PASS.
Повреждённая либо неполная матрица
не получает положительный результат. Unknown schema и boolean version запрещены.

Это data-consistency adapter, не native import и не classification scorer.
Baseline failures имеют полные и валидные записи и должны оставаться видимыми
в отчёте. Failed fixture с отсутствующими origins не становится такой матрицей.

```text
python3 -m Scripts.StructTrain.TimeLearner report \
  Scripts/StructTrain/TimeLearner/specs/native-dataset-clock-v1.json \
  --format dataset-clock --artifacts NATIVE_GATE_RESULT --output NEW_CACHE
```

Для расширенных20 cases использовать native-dataset-clock-extended-v1.json.
Первый contract требует36 recordings, второй76. Допускается исходный combined
gate с дополнительными cases: отчёт явно перечисляет свой subset и сохраняет
полный source gate inventory; all_gate_tests_reported в этом случае false.
Прочие14 transfer cases этим отчётом не объявляются визуально проверенными.

Каждая запись имеет полный soma/input overview и tiles без downsampling:
1920×960 PNG, SVG, PDF, не менее14px на native tick в zoom. Y одинаковый для
origins одного условия; нужны также автоматически создаваемые local-detail
виды слабого отклика. Вход — реально измеренный generator output поверх
потенциала сомы. LT events здесь не собирались и не выдаются за отсутствие
спайков. Рисунки не участвуют в численном scorer.

Report cache хранит portable primary copies, JUnit/runtime/result, contract,
manifest, hashes renderer files/backend и всех созданных файлов. Полные
рисунки хранить в M40 Data cache; Git содержит сжатые исходные native данные,
метрики и отдельно выбранные/непосредственно просмотренные рисунки. Генерация
не присваивает global_visual_acceptance. Code/root/data references публикации
должны указывать точные commits; один абсолютный путь не является evidence.

`tests.test_dataset_clock_reports` использует реальные gate artifacts из
TIMELEARNER_DATASET_CLOCK_ARTIFACTS. Для extended выставить
TIMELEARNER_DATASET_CLOCK_EXTENDED=1. Проверки включают неизвестную/bool schema,
incomplete window, неверный origin, потерю events/model digest, NaN и пропуск
native tick. Серверная приёмка нового adapter и визуальный review ещё требуются.

Baseline reader evidence `bdabaa6cea61250014051f6da7757fa6f9dec1df` подтвердил9/9
на36 полных исходных записях и повреждающих мутациях; SHA256 всех6 файлов
проверены. Fixed normal B3 прошёл34/34 native (20 clock +14 transfer). Его
unit-процесс реально выполнил9 тестов, но завершился до capture /proc mappings;
unit gate остаётся incomplete_test_observation, общий запуск не принят. Нельзя
подменять фактическую provenance сведениями ldd или hash executable. Publisher
также обнаружил nullable inventory; исходный failure сохранён отдельно.

Для быстрых PulseLib native tests добавлен явный gate schema2 с
`cooperative_runtime_capture=true`. Test main после RUN_ALL_TESTS удерживает
тот же процесс через существующий Console RuntimeCapture ready/ack contract.
Supervisor проверяет PID/start_ticks и фактически загруженные файлы до ack.
Схема1 не меняется; неизвестный режим, числовой/строковый true или boolean
schema запрещены. Source/model ticks и Reset при ожидании не выполняются.
Это не поддержка такого handshake в Rdk gtest_main: ему schema2 не назначать.
Новый handshake и file/scheduling fixtures ещё требуют серверной проверки.
