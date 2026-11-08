# Сверка актуальных статусов параметров, 06.11.2026

При повторной проверке найден устаревший раздел
[ParameterSearchContracts](ParameterSearchContracts.ru.md): он всё ещё считал
открытым дефект конечности timing setters и отсутствие measured length proposal.
Раздел исправлен по фактическому принятому коду; исторический
`parameter_search_contracts.json` с исходными commit/blob остаётся неизменным.

[Машиночитаемая сверка](ParameterContractStatusReconciliation.json) фиксирует:

| Пункт | Что подтверждено | Что не следует из проверки |
|---|---|---|
| PARAM-FINITE-001 | Все десять timing setters текущего принятого Pulse0ec9193 идентичны tested ecf35a6. Заново сверены normal71/ASan112 archive members, 120 отклонённых NaN/±Inf назначений на worker, actual gtest4+21 без failures/errors/skips. | Connected suppliers, SetDataDirect и XML parser не проверены этими property cases; полный runtime inventory не закрыт. |
| V2 measured length proposal | Оба файла MeasuredLengthSearch текущего принятого Pulse0ec9193 побайтно совпадают с tested a728d971; проверена Git ancestry исправления. Ранее принятые helper/controller/native A/B и их ограничения описаны в MeasuredLengthProposal. | Legacy EstDelayPerSeg не становится владельцем V2 policy. Новый прогноз не подтверждает отсутствующий пик, сходимость или научную классификацию. |
| LIFECYCLE-BOOL-001 | Статус не повышен: общий public bool-контракт Rdk и внутренние hooks различаются. | Pending shared-lifecycle SDK не объявляется принятой по совпадению двух helpers или десяти setters. |
| PARAM-NATIVE-FACTOR-001 | Остаётся открытым: effective factor зависит от версии контроллера и владельца параметра. | Наличие UProperty/setter или одинаковые исходы N0/N1 не подтверждают и не опровергают применение фактора. |

Это проверка неизменяемых Git blobs и существующих первичных артефактов,
не новый серверный численный прогон. Прежний ASan timeout сохранён в источнике;
последующая завершённая regression21 проверяется отдельно. Область полного
плана не сужается: этапы1–12 остаются частичными.

Дополнение 08.11: отдельно сверены 44 calibration/PostTune записи текущего
каталога, где ещё оставалась историческая фраза об отсутствии native реализации.
[Новая reconciliation](CalibrationPostTunePropertyReconciliation.ru.md) сохраняет
исходные evidence statuses и различает public legacy knobs, существующие typed
native phases и неполный support snapshot PulseLib fcc3fed0dc63fc0d8ae8dcfdb0f85bd5d004baf8.
Это metadata/source review без новых numerical runs и без повышения всей
property/mode/lifecycle matrix до accepted.
