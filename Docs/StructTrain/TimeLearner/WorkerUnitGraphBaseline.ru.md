# Воспроизведённый дефект lifetime: worker и отдельная managed unit

Статус: дефект подтверждён, исправление ещё не реализовано. Новый native worker
backend source1fd77d34f остаётся вне develop до исправления и runtime-приёмки.
Это инфраструктурный дефект этапа10; физика и алгоритмы learner не менялись.

M40, isolated SQLite ledger, API sourceadc1f6227144360097b378a33e1db564794e0442:

1. Parent worker резервирует тестовое runtime-tree и запускает отдельно
   управляемую Python unit через настоящий contained_process.start.
2. Parent завершается. Его kernel cgroup закрыта, но managed child находится
   в другой cgroup и продолжает работать.
3. recover_closed_worker принимает закрытие parent, освобождает runtime lease.
   Свежая проверка после recovery подтверждает, что child всё ещё работает.
4. Обе точно принадлежащие тесту unit явно остановлены; closure подтверждена.

Результат подтверждён JSON records, signed requests/bindings, kernel readbacks
и фактической строкой SQLite state=released. Proof
0fc2341b198d1995bd5304198ee49f18c95ffdf6,
[независимый receipt](WorkerUnitGraphBaselineVerification.json):37 members,
5 исходных blobs и4 signed records. Primary archive7636 bytes. Основной
реестр ресурсов, работающие SDK/задания, модели и данные не изменялись.
Новых neural/model computations0. Это не сбой SSH или заполнение диска.

Существующая проверка корректно подтверждает closure конкретной parent unit,
но не полного логического графа созданных ею managed units. Простая смена
process scope в manifest или повторная проверка parent PID проблему не решает.

## Обязательное исправление перед promotion нового pipeline backend

Компоненты: resource_reservations.py, contained_process.py, contained_runner.py,
native_process_policy.py, оба native workers и scheduler/producer integration.

```text
reserve immutable source/runtime and declared aggregate resources
register durable owned launch intent, linked to this lease, BEFORE native launch
launch exact managed unit; bind intent to actual invocation/PID/start/cgroup
hold resources through every managed unit and its descendants
on ordinary release or crash recovery:
    resolve ALL registered intents, including incomplete launch/bind boundaries
    fresh-check every managed unit / whole owned execution group
    if any live/unknown owner or incomplete closure remains: keep reservation held
    otherwise release atomically and retain all ownership/closure records
```

Нельзя выводить граф из имени executable, текущего PID либо отсутствия heartbeat.
Следует выбрать и проверить явный registry графа или общую управляемую job-группу;
решение должно охватывать units, создаваемые через user manager, и обычные forked
processes. Учесть суммарную RAM/slots/disk: caps отдельных sibling units не
являются агрегатным cap worker. Политика ресурсов не входит в научный hash
условия, но её фактическое применение обязано быть в execution evidence.

Обязательные fault cases: parent closed/managed child live; frontend crash до
request/после request/до binding; failed launch; parent+child fully closed;
дубли/чужой lease; runtime alias; повторная recovery; timeout/cancel всего графа;
aggregate cap; legacy schema/API и запрет обхода нового графа старым release.
Сначала воспроизвести этот же baseline, затем получить отказ release при живом
child и успешный release только после closure всего графа. Сохранить оба исхода.
Не мигрировать registry или runtime работающего ASan K1/normal304 задания.

Прежние15 portable policy checks и77+2 contained runner checks остаются
доказательствами своего охвата. Они не проверяли этот lease-owner/managed-unit
разрыв и не являются его исправлением. Build/Calculate/Reset bool-контракт Rdk,
CapturedPerInput, физические параметры и научные критерии не затронуты.

Последующая проверка: schema3 implementation source34394c301 прошла
[M4061/61 tests](ManagedUnitsM40Acceptance.ru.md), включая отказ recovery
при живой отдельной child и успешное освобождение после closure всего графа.
Это исправление в отдельной ветке с M40 evidence; Elder и production integration
ещё pending. Первоначальный baseline/API sourceADC не менялся и не считается
исправленным задним числом.
