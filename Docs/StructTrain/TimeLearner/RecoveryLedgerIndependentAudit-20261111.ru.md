# Независимый аудит переносимого recovery ledger

Поддерживаемый читатель: `Scripts/StructTrain/TimeLearner/candidate_window_recovery_ledger.py`.
Это проверка сохранённых DATA, а не выполнение модели или восстановление контроллера.

Порядок проверки:

```text
validate exact ledger schema, finite values and content hash
bind source, owner and full measurement archive document ID
replay archive2 primary even when deliveries is empty
require unique event/group IDs in actual archive order
group deliveries by original attempt; require one immutable runtime per attempt
for each attempt:
    validate original runtime3 against initial configuration and protocol
    bind each event to actual rejected group and effective physical parameters
    check assignment, timing, counters, ordering and declared search budgets
return checks performed, with coverage/authority/certificate claims false
```

Warm retry может оставить в archive предыдущую попытку с runtime3 и перейти
на runtime2 в текущей попытке. Проверять старые события по новой policy нельзя.
`audit_candidate_window_recovery_events` поэтому принимает явный `attempt_id`:
он должен совпадать с run_id исходного runtime и присутствовать в архиве.
Без этого аргумента сохраняется прежняя проверка только текущей попытки.
Архив, его current_attempt_id и исходные bytes не переписываются.

Первый адресный набор состоит из прежних восьми event tests и восьми новых
ledger tests. На Elder он завершён **16/16 PASS**, без failures/errors/skips;
owned cgroup закрыта. Условия и первичные результаты находятся в
[ElderRecoveryLedger16G1](ValidationPlans/ElderRecoveryLedger16G1-20261111/).
Они проверяют пустой ledger на реальном production reader с synthetic DATA,
неизменность входов, повреждение первичных данных, ложные claims, чужие bindings,
дубликаты и запрет выдавать valid peak за rejected recovery delivery.
Положительные joins непустого ledger из нового C++ service и перенос между
попытками с фактическим warm retry требуют отдельной проверки. Эти восемь
новых тестов их не заменяют.

Первое обращение к runner отклонено до создания job: в декларации было имя
Elder вместо фактического Elder-1. Отказ сохранён; исправленная декларация
передана отдельным Git control checkout, runtime/source не менялись.
В process diagnostics остались два предупреждения Git о выключенной lazy
fetch в partial clone. Они сохранены в stderr; утверждение о полностью чистом
diagnostic status не делается. Проверка исходников и все тесты завершились.

Пока reader не подключён к package7/summary8, Console и frozen recognition.
Ни принятие формата, ни связность всех переданных событий не доказывают
полноту журнала действий, Exact или качество классификации. Отсутствующие
события нельзя восстановить по одному списку supplied deliveries.
