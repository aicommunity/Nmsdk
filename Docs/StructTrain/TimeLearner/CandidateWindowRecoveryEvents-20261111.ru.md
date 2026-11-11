# Сохранение событий recovery candidate-window

Статус: C++ serializer и адресные native producer controls добавлены;
ещё не скомпилированы и не приняты на workers. Frozen C2 source root5643f8319
предшествует этому изменению и его не проверяет.

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
