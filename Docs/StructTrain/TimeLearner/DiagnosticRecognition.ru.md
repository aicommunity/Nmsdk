# Явная диагностика модели после остановленного Train

Этот подэтап продолжает незакрытый public diagnostic evaluation этапов5/8/10.
Обычный pipeline не должен принимать stopped package как completed Train.
Новый native API создаёт отдельный diagnostic recognition package, сохраняющий
исходный stopped state, outcome/reason и null certificate. Никакой подстановки
шаблонного Test или нового обучения. Все входы включаются общим conversion
кодом с проверкой storage, связей, Rs/C, model identity и интегратора.

Pulse feature427bf9300a5caeab2ece6dffb0b76c82f6096025 добавляет явные
ConvertNativeStoppedToDiagnosticRecognition, PrepareNativeDiagnosticRecognitionState
и ImportNativeDiagnosticRecognitionState обоих learner. Kind и state_kind
отличаются от ordinary recognition. Обычный import/threshold candidate и
попытка переименовать diagnostic в completed должны отвергаться. Статус
обучения не меняется после диагностических frozen full-pattern проб.

В native-diagnostic-recognition-v1.json заявлены18 серверных cases:
8 новых partial/budget Classic/Branch N0/N1,2 ordinary completed controls,
4 sweep-budget regressions и4 native archive regressions. Полные input/soma
samples сохраняются для reference/search и target/foil evaluation, включая
cancelled/gap пробы. Положительные ordinary controls явно используют0.2;
исходные negative cases сохраняют0.02, амплитудные допуски не меняются.

Это пока непроверенный feature candidate. Build и адресные normal/ASan gates,
проверка первичных наблюдений и temporal reports обязательны. Публичный
Console job, Python CLI/runner, строгий diagnostic-only scorer и portable
provenance ещё не реализованы: native API не подменяет их приёмку.
Производить scientific verdict из этих8 fixtures запрещено; они проверяют
корректность переноса/режима измерения, не разделимость всех паттернов.

Исходный ASan163 и full407 render на M40 не изменять. Новый build выполнять
на свободном Elder в отдельном deploy root, после проверки завершённости
предыдущего source/build задания. Не merge в develop до приёмки подэтапа.

## Проверенные и рабочие слои

На numeric rootecf3a18876df175b012ad2e9a02797fb243fcf1c/Pulse427bf930
Elder normal прошёл18/18 native cases. Все8 diagnostic cases сохранили
budget_exhausted/null certificate,32 complete full-pattern observations и16
cancelled/gap observations. Import/metadata/ordinary/threshold guards прошли.
Это same-process native API; fresh-process diagnostic import ещё не проверен.

Первый Python readerb4439f851:7/8, одна ошибка fixture-протокола: ordinary
paired-impulse controls не пишут full-pattern files. Данные не подменены.
В bb9666e248 добавлены2 отдельных ordinary full-pattern controls; gate20
на Elder запущен отдельно, без изменения Pulse Core. Previous result сохранён:
proof5de3b6b3eba87a2b76a27a526141e23f065e9095,323 verified members,
2360973 compressed bytes. Эта попытка не объявлена Python PASS.

Следующий непроверенный слой добавляет Console flag
`--timelearner-diagnostic-evaluate` и root CLI `diagnostic-evaluate` с
`--source-stopped` (штатный *_stopped_state.json и его исходные summary/CSV).
Job kind=timelearner_native_diagnostic_evaluation_job, source_stopped и
conversion_spec задаются явно. Model/evaluation/execution имеют отдельные
diagnostic kinds; execution сохраняет training_outcome/reason. Native fresh
owner использует штатный import/build/reset и full-pattern executor, без
вложенного расчёта. Порог наследуется из исходной модели, не калибруется.

Pipeline run-manifest schema3 предназначен только diagnostic-evaluate;
исторические schema1/2 остаются ordinary. Source primaries копируются и
аудируются через stopped adapter. Оценка использует общий label/ID/window
scorer, но только после полного diagnostic-source audit, с явными
diagnostic_only=true, training_completed=false и evaluation_verdict=null.
Обычный scorer, loader и calibration не принимают diagnostic schemas.
Остановленный diagnostic evaluation может сохранить partial execution,
но не становится completed Train. C++/Python production path, fresh-process
проверки и temporal reports этого CLI ещё требуют серверной приёмки.
