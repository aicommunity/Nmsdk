# Отрицательный metadata66 A1 и узкая правка тестовой обвязки

Оригинальный A1: source `382180add59275c9c8bcc449a973cc0577015918`,
plan `5d64cf11535ff28443f335c10194c2713c49897c`,
FP `f4be7a0f06f2e2fd32a67b4035f74c161464c16d365f1c48ae47092f0bd6d329`.
Все 66 tests исполнены: **65 passed, 1 error, 0 failures/skips**.
Результат отрицательный и не переклассифицируется после исправления.

Ошибка:
`Scripts.StructTrain.TimeLearner.tests.test_closed_python_validation.ReadonlyReservationsSnapshotTest.test_real_valid_ledger_read_uses_ro_deferred_select_without_writer`.
Spy `connect(uri,*args,**kwargs)` получил первый positional database и
keyword `uri=True` штатного SQLite API, поэтому Python выдал
`TypeError: ...connect() got multiple values for argument 'uri'` до вызова
настоящего SQLite connection в этом тесте.

Правка ТОЛЬКО теста: имя первого параметра стало `database`, этот же объект
передаётся original connect; `*args/**kwargs`, реальный SQL trace, запрет
writer `_transaction`, проверки valid released ledger и неизменных DB bytes
сохранены. `closed_python_validation.py` и `resource_reservations.py` не меняются.
24 collector metadata cases, 3 остальных readonly cases и 38 существующих
regressions прошли; это не заменяет требование нового полного positive66.

Исходный unit `timelearner-b249392e-bb73-4e43-9540-e2259faa3d26.service`,
invocation `b028d558eacf4c7d9f4d56864e1d676a`, PID1358765/start329753937,
binding SHA `6a2d4e60aef04389ead26af0984359aaf021d8f4b135618d87ef2719c99b6e89`.
Lease `72c60723-e936-48a6-af2c-cf893979e439` released; unit closed.
Root original `ClosedPython66RootTerminalReadback.json` SHA256
`20e7c30f5957e71dad0b8f9d07bcbe8f83fd7279cc5b75c10c5392b32f53c2ea`.
Root сохраняет исходные observations; этот документ не заменяет raw metadata.

Следующая попытка — отдельные source/plan/job A2 с теми же 66 IDs и лимитами,
обновлённым source/package fingerprint и direct nested Git controls.
Существующие40/73 не запускались заново и ещё не collected этим CLI.
Локально выполнялись только Git/JSON/AST действия; tests исполняются только
после отдельного Root review/dispatch на Linux. Научных выводов здесь нет.
