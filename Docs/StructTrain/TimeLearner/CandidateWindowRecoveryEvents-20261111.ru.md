# Сохранение событий recovery candidate-window

Статус: C++ serializer и адресные native producer controls добавлены;
ещё не скомпилированы и не приняты на workers. Frozen C2 source root5643f8319
предшествует этому изменению и его не проверяет.

Добавлен Python reader candidate_window_recovery_events: отдельная проверка
wire shape и audit поставленного набора событий через полный independent
archive2 primary replay. Новый content ID отвергнутой группы включает полную
selection и тот же native/CSV инвентарь, что C++ rejection factory. Сохраняемый
valid proof2 hash не меняется: общий content builder выделен без смены полей.

Audit связывает source/owner/candidate/group, exact logical trial/action/epoch,
effective revision, физические параметры/C, validity, current runtime3 budgets,
порядок событий и принятые измерения до отказа. Валидная геометрия без
опубликованного measurement не становится разрешением recovery. Восемь новых
DATA tests проверяют форму, mutations, старую runtime version, отрицательные
primary joins и честное отсутствие доказательства полноты пустого event set.
Серверные проверки этого Python изменения ещё впереди.

Проверка supplied events не подтверждает полноту service ledger: невозможно
восстановить все generic отказы/declined edits из одних групп измерений.
Reader явно возвращает service_ledger_completeness_verified=false и не
объявляет независимый пересчёт всех edits/invalids. Положительные native
Missing/Ambiguous event joins, полная coverage и terminal replay остаются
обязательными для подключения service/package; отрицательные DATA controls
не заменяют эту приёмку.

EncodeCandidateWindowRecoveryEvidence сохраняет отдельный документ
timelearner_candidate_window_recovery_event / schema1. Он содержит полный
transition прежнего decision serializer, group ID, rejected content ID,
source origin, owner scope, candidate witness ID, число issued probes,
applied edits и accepted composite observations на границе отказа.
event_id — canonical DATA hash всего документа без самого event_id.

Serializer проверяет finite/положительные параметры, точные счётчики,
invalid_after=invalid_before+1, непустые identity bindings, форму content hashes,
размерность индексов и согласованность disposition/status. Документ не содержит
амплитудного/временного residual, допустимого пика либо нового сертификата.
Публичный hash не является live capability.

В существующие реальные core recovery cases добавлены сохранение event JSON
и mutation controls: потерянная группа, неверный invalid increment, невалидный
content ID, NaN, невозможный accepted counter и изменение owner scope.
Каждое событие сохраняется отдельно, по action serial, рядом с полными
исходными window5 groups. Нет повторного физического прогона ради serializer.

Отдельный SDK translation unit сохраняет зависимости чистого target
Test_PulseLib_TrainingAlgorithms: тот по-прежнему собирает прежний
CandidateRecoveryEvidenceJson без зависимости от ModelIdentity/SDK.

До подключения service остаются обязательными: независимый Python replay
rejected content из всех primary, привязка события к exact prepared/logical
request и runtime3, ordered ledger без повторов, сверка общих budgets и
terminal status, versioned package/archive/summary, импорт и Save/Load.
DATA serializer сам по себе эти пункты не закрывает. Mid-probe checkpoint
и восстановление live authority из JSON не поддерживаются.
