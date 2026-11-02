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
