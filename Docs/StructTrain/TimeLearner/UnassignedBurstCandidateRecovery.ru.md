# Восстановление поиска после неидентифицируемой пачки — WIP

06.11.2026. Это незавершённый кандидат этапа7. Он не принят в develop и не
включён в эксперименты. Срез Pulse70f прошёл116 C++ controls на M40;
последующий typed recovery journal Pulsea34 ещё не проверен. Python/CLI audit и допуск schema5 ещё
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
Проверка отдельной пробы описана ниже. Её ещё нужно связать с каждым recovery
rejection, фазой поиска и общим бюджетом, затем интегрировать
completed/stopped/C-history readers. C++ tests и native recovery пока не
проверены; этот срез остаётся feature-кандидатом.

### Проверка первичной невалидной пробы: два сервера

Root `8815dea36` отдельно выделяет прежнюю строгую проверку часов CSV;
`0cf65d58f4880c283431c7652e8d63b08107bf55` добавляет
`candidate_recovery_evidence.audit_unassigned_burst`. Используются существующие
read_partial_probe и measured_wave_plateaus через wave diagnostics; второй
детектор волн не создаётся. Проверяются protocol/prepared/requested/spec,
размерность и выбранный канал, полное окно и максимальный шаг, конечные числа,
реальные фронты входа, точные причины отказа, отсутствие численных peak claims,
волны и соответствие их фактическим отсчётам CSV. Первичная проба остаётся
valid=false; результат явно содержит training_transition_verified=false.

На M40 и Elder прошли по48/48 tests без skips:9 declaration/budget availability,
12 общих ConditionSpec,13 pipeline-condition,5 новых primary mutation и9 прежних
stock boundary tests. Использованы те же четыре штатных исторических cold runs:
Classic/Branch при двух порогах; высокопороговые terminal probes имеют три волны
вместо четырёх, низкопороговые — дополнительные максимумы. Эти модели заново
не рассчитывались. Изменённые копии проверяют неполноту, nonfinite, часы,
входные импульсы, соматические отсчёты, clipping, identity/dimensions,
лишние причины и выдуманные peak fields.

Evidence commits: M40 `af10708979f48cd2bc7e95654bc94e73fbba72a9`,
Elder `3d5a5ef8b6f29c2e13edd2e8f514bafe9a3d79ab`.
[Проверка primary](CandidateRecoveryPrimaryVerification.json) сверяет14 source
files каждого сервера с exact Git source. Заново проверены все1370 members
исходного сжатого Git primary `e5fa71d745119af0d818059f497dd226f4c7c25d`;
все1212 M40 inputs и620 Elder inputs сверены с самим архивом, а не только
с серверным manifest. Elder восстановлен из Git выборочно: вся JSON chronology
и восемь выбранных CSV,102118568 bytes. Это повтор анализа исходных данных,
не независимое обучение и не результат применения новой политики.

PulseLib `70f4f27daa390bdd0f405d1ed9e3f01d47cd2394` добавляет getter общего
InvalidObservations и поле invalid_observations в summary5. При retained search
это фактический счётчик attempt, включая final sweeps; при отсутствии search
значение null. Нельзя выводить его из размера Rejected или подставлять ноль
после импорта без истории. Python проверяет availability и тип поля;
согласованность списания с переходами поиска ещё не принята.

На M40 завершена отдельная сборка root
`ef21547432ac60f49ba4af3038735ed96a9a6c8e` / Pulse70f с объявленными116 C++ cases:
13 новых classifier/controller/codec,4 invalid-budget,74 смежных и25 transport.
[Задание и наблюдаемый статус](CandidateRecoveryNativeJobs.json).
Все116 tests прошли без skips. Первичные данные опубликованы в
`bfd94563de9db25d9943ab930860113e63ee76cf`, дополнительная проверка различий —
`6b843ed8c7884d935e89513d1da894d5a73ff481`.
[Независимая проверка](CandidateRecoveryNativeVerification.json) подтверждает
все834 archive members,748 source hashes, exact116 JUnit IDs, actual runtime,
закрытие процессов и release lease. Проверен kernel cap4GiB/tasks128/swap0.
Общий default25 physical subset сопоставлен с прежним опубликованным архивом:
все284 CSV и451 JSON побайтно совпали. В18 startup JSON различаются только89
значений StepDuration/rdk_value — замеры длительности вычисления из
Rdk UContainer.cpp:2684. Иные поля не различаются; исходники/артефакты не
переписывались и эти поля не удалялись из первичных данных.

Сборка не содержит последующий Python primary classifier или typed journal
Pulsea34 и не подменяет их приёмку. Это не stock cold opt-in Train и не
независимый scientific Test. ASan A5 проверяет более ранний Pulse12d.

### Подготовленный typed journal: ещё не принят

PulseLib `a34be2868449e744e07a11f7687d9033ae0c7cf9` добавляет
CandidateRecoveryEvidence и summary5 candidate_recovery_events. Каждая запись
содержит action serial, run/trial, observed/candidate input, sweep, epoch,
base/effective model revision, phase anchor/input, validity, full L/Ns/Rs и C,
invalid_before/after, disposition и status/reason после решения. Отдельно
различаются cursor_advanced, invalid_budget_stop и restored_best_stop.
Финальные отказы не создают запись пропуска input; default retry не создаёт
recovery event. Это журнал решения, не новое измерение отсутствующего пика.

Корневой candidate_recovery_history.py связывает записи с actual JSON/CSV,
search trial IDs, точными rejections, фазой и bounds, проверяет приращения и
терминальные причины. C-history использует существующий witness registry.
Общий счётчик остаётся producer-reported: не все preparation/final failures
имеют отдельный CSV, поэтому all_invalid_observations_independently_recounted
остаётся false. Нельзя выдавать длину массива событий за полный счётчик.
Standalone validator не включён в full completed/stopped audit: публичные
читатели пока явно отклоняют schema5.

Подготовлены дополнительные C++ проверки журнала и Python mutation tests на
реальных старых пробах с гипотетическими decision metadata. Они не доказывают,
что исторический controller исполнял новую политику. Новый срез ещё не
выполнялся. Schema5 остаётся незавершённым feature-форматом; ранние codec
артефакты Pulse70f читаются в контексте своего exact source snapshot, без
достраивания отсутствующего журнала. Cold configuration5 при этом не меняется.

Добавлены controller regressions default-versus-opt-in, anchor/input failures,
missing/extra waves, общий budget, конечное исчерпание поиска, запрет final skip,
повреждённый контекст, незавершённые N0 repeats и отказ свежего restoringBest.
Четыре CandidateRecoveryConfiguration tests используют реальные storage rigs
Classic/Branch×N0/N1 для codec1..4→5, unknown/duplicate-field negatives и summary.
Эти13 controller/classifier/codec functions прошли в Pulse70f gate116;
добавленные позднее assertions typed journal ещё не проверены.

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
