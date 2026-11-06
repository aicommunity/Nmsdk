# Восстановление поиска после неидентифицируемой пачки — WIP

06.11.2026. Это незавершённый кандидат этапа7. Он не принят в develop и не
включён в эксперименты. Классификатор подключён к явно выбираемой C++ политике;
её серверные тесты ещё не выполнены. Python/CLI audit и допуск schema5 ещё
не завершены: новый режим нельзя выдавать за поддержанный сквозной pipeline.
Текущие задания используют неизменяемые более ранние SDK и не подтверждают код.

## Основание

[Исходные stock traces](StockFailureBoundaryReports.ru.md) и
[matched Rs controls](StoppedStateResistanceControls.ru.md) показывают закрытые
конечные пробы с тремя волнами вместо четырёх, либо с дополнительными
положительными максимумами. Изменение Rs меняет отклик, но в проверенных
терминальных геометриях не вернуло четыре отдельно определяемые волны.
Эти наблюдения не доказывают физическую невозможность обучения.

Текущий BoundedTrainingSession::Reject повторяет ту же пробу до исчерпания
maximumInvalidObservations. При нуле останавливается на первой невалидной
пробе. Простое увеличение бюджета не исследует другую геометрию и не
устраняет детерминированное слияние волн.

Необходимо сохранить прежнюю политику для существующих конфигураций, а
переход к другому кандидату сделать явно объявленным режимом. Он не может
подставлять прогноз времени вместо отсутствующего пика, ослаблять критерий
whole burst или автоматически повышать minimum amplitude.

## Уже подготовленный код

В PulseLib `4689a3c8652cfdd411a5734d86c1914b9b949f69` отдельно выделяет
CheckedProbeContext из CheckedMeasurement. Старый измеритель вызывает его
с прежним требованием valid/complete; порядок оставшихся проверок сохранён.
Это механическое выделение, runtime-эквивалентность ещё требует проверки.

Следующий commit `1edf9ac90d299594bcdc7552b8743aa50e560105` добавляет
CanAdvanceUnassignedBurstCandidate. Он только классифицирует отказ и не
выдаёт измерение, residual или сертификат. Область соответствует native
training probe: один выбранный input/window, полная штатная пачка, schema3.
Размерность дерева не ограничена четырьмя.

Положительный результат требует одновременно:

- корректного protocol/prepared/spec контекста, физической размерности,
  profile/hash/revision и достаточного declared sampling;
- полного закрытого окна с endReason=window_closed и valid=false;
- фактического полного строго упорядоченного множества стимулов;
- ровно одного Missing/Ambiguous burst assignment и соответствующего peak
  без выдуманных численных полей;
- точного набора причин burst_missing/peak_missing либо
  burst_ambiguous/peak_ambiguous; дополнительные причины запрещены;
- конечных ordered wave timestamps/amplitudes, согласованности с baseline
  и физически возможного относительно sample count числа локальных максимумов;
- согласованных spike flags, размерности, границ времени и бюджета.

Неполнота, nonfinite, повреждённый контекст, clipped window, лишние причины,
ложные peak fields и неизвестные состояния не разрешают переход. Первичная
проба остаётся невалидной; классификатор не изменяет её поля.

## Подготовленные тесты и обязательная дальнейшая работа

### C++ controller/codec: подготовленный следующий срез

PulseLib `e19c2dba39dc3fd51119d1b5d04ee023d1e7cf2d` добавляет
InvalidMeasurementRecovery: RetrySameCandidate по умолчанию и opt-in
AdvanceUnassignedBurst. Последний требует ненулевого объявленного invalid
allowance. Допустимый unassigned burst списывается с общего attempt budget;
после разрешённого отказа очищаются anchor/partial repeats и используется
следующий кандидат существующего bounded cursor, включая C-context rotation.
Неидентифицируемый restoringBest завершает SearchUnresolved, без повторного
использования старого измерения и без бесконечного возврата. Capture references
не изменены, final verification остаётся независимой и не пропускает входы.
Текущий последующий срез `a7220af9840c776d675533f170fbce8e4eaa18b9`
также копирует значение базовой JSON schema перед добавлением новых ключей.

Cold configuration и training summary имеют opt-in envelope schema5:
base_schema_version=1..4 и invalid_measurement_recovery=advance_unassigned_burst.
Все прежние поля остаются полями указанной базовой схемы; её строгий codec
повторно проверяет исходные ограничения. Base5/неизвестные поля/режимы/нулевой
allowance запрещены. Старые схемы1..4 по-прежнему означают RetrySameCandidate.
Это версия cold/summary данных, а не ControllerVersion=5: component version
по-прежнему выбирается существующим ControllerVersion=1/2.
Это сохраняет CPP export/import declaration через существующий configuration
codec, но complete/stopped roundtrip нового режима ещё требует runtime-проверки.

### Python declaration/preflight: адресная проверка на двух серверах

Root `7e06a570236563a332722ff0357017dfcfd90401` добавляет
`candidate_recovery.py`: строгую проверку плоского envelope5, выбор прежней
базовой схемы только для проверки, связывание declared/measured режима и
ненулевого invalid allowance. Схемы1..4 с новыми полями отклоняются, отсутствие
этих полей означает прежний RetrySameCandidate. Неизвестные поля базовой схемы
сохраняются для последующей проверки штатным C++ codec; Python projection не
выдаётся за полный native preflight. Исходный JSON не изменяется и остаётся
источником job hash, native execution и ConditionSpec.

На Elder и M40 прошли по33/33 Python tests без skips:8 envelope/binding,
12 общих ConditionSpec и13 pipeline-condition tests. Новый pipeline test
использует четыре сохранённые реальные Classic/Branch declarations, проверяет
изменение научной идентичности при выборе режима и отказ неизвестного режима,
вложенной base5 и нулевого allowance. Это проверка декларации, без нового
физического Train. Девять файлов source каждого сервера сверены с Git.
Первичные logs/receipts сохранены отдельными Git evidence commits:

- Elder: `0128f0ee58615c3f7645473d4bb97c6e0b5a4dc8`;
- M40: `7eefe1a8ad55c3a50dfd201a921cd864d1f44e52`.

[Проверка артефактов](CandidateRecoveryDeclarationVerification.json) содержит
пути, размеры, hashes и точные versions. Первая A1 попытка остановилась на
ошибке экранирования строки в проверочном runner до запуска tests; её log
сохранён. A2 tests прошли, затем публикация из частичного Git snapshot
потребовала `write-tree --missing-ok` для неизменённых исторических blobs.
Повторного запуска tests для публикации не было. Текст runner хранится как
`runner.txt`, без действующего launcher в Reports.

**Полный Python audit schema5 ещё не реализован.** `audit_training_summary`
и `audit_stopped_state` явно завершаются причиной
`candidate_recovery_primary_audit_not_implemented`. Успешная проверка envelope
не разрешает принять missing/ambiguous observation или выдать сертификат.
Следующий шаг — проверка каждого recovery rejection по actual JSON/CSV,
protocol/context, закрытому окну и общему бюджету, затем полная интеграция
completed/stopped/C-history readers. C++ tests и native recovery пока не
проверены; этот срез остаётся feature-кандидатом.

Добавлены controller regressions default-versus-opt-in, anchor/input failures,
missing/extra waves, общий budget, конечное исчерпание поиска, запрет final skip,
повреждённый контекст, незавершённые N0 repeats и отказ свежего restoringBest.
Четыре CandidateRecoveryConfiguration tests используют реальные storage rigs
Classic/Branch×N0/N1 для codec1..4→5, unknown/duplicate-field negatives и summary.
Наличие этих исходников не означает прохождения тестов.

В production Test_PulseLib_StorageComponents добавлены два теста
UnassignedBurstCandidate. Настоящий ProbeRecorder получает управляемые
waveforms, включая реальный дополнительный поздний максимум. Проверяются
Classic/Branch, N=1/2/4/6, valid/missing/extra-wave и повреждения контекста,
времени, чисел, flags и причин. Это алгоритмические recorder tests, а не
вычисление физического Rdk-нейрона. Локально они не запускались.

Для завершения подэтапа необходимо:

1. Проверить механическое выделение на прежних production measurement tests;
   затем выполнить два новых classifier tests на серверах.
2. Проверить подготовленную типизированную opt-in политику. После
   разрешённого отказа списать общий attempt budget, закрыть незавершённые
   N0 repeats, инвалидировать anchor/input и перейти к следующему легальному
   кандидату штатного cursor. Не создавать CandidateEvidence для отсутствующего
   измерения. Порядок Classic/Branch, ограничения физических общих банков,
   bounded N1 domains и C-context fairness должны сохраняться.
3. Отдельно определить отказ повторного измерения restoringBest: прежняя
   положительная история не заменяет свежую валидную пробу. Не допустить
   бесконечного возврата к той же неидентифицируемой точке.
4. Не применять skip к capture references или final all-input certificate.
   Недопустимы пропуск входа при final и перенос старого Exact после edit.
5. Проверить подготовленную C++ версионизацию cold configuration/summary и
   completed/stopped export/import; добавить strict Python parser/auditor, CLI capability и
   ConditionSpec binding. Отсутствие поля сохраняет прежнюю политику. Пока это
   не сделано, новый режим нельзя объявлять действующим фактором эксперимента.
6. Проверить default A/B, разрешённый переход, no-candidate/budget outcomes,
   bad context/nonfinite/incomplete/clipped negatives, N0 repeats, N1 bounds,
   shared Branch cable, C-contexts, retarget/reset и state roundtrip.
7. Выполнить реальные native cold controls в исходной физике с читаемыми
   временными графиками и полным provenance. Только после них переходить
   к stock cold retrain и frozen восьмипаттерновой оценке.

Завершение поиска остаётся Exact только после новой независимой проверки всех
входов конкретной модели. Исчерпание конечного поиска или бюджета не означает
PhysicalInfeasible. Августовские4/8–6/8 и прежние отрицательные измерения
сохраняются; этот подэтап не является новой научной серией.
