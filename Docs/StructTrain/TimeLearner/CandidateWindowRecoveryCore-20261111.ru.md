# Переход bounded search после закрытого отказа candidate-window

Статус: новый код ядра, серверная проверка впереди. Предыдущий фундамент
допуска проверен на root9d51f808047f08e0cbfa0e440061f9bf04e8ba88 / Pulseaf612ba:
Elder и M40 выполнили29/29 cases,29 отдельных leaf gates; outer+29child groups
закрыты, reservations released, record_errors=[] на каждом сервере.
Это приёмка sealed measurement/rejection factory, не нового перехода поиска.
Полный compact primary этих Linux запусков ещё требуется опубликовать.

## Изменения ядра

В BoundedTrainingSession добавлена отдельная C++ policy
AdvanceRejectedCandidateWindow и перегрузка RejectCandidateWindow с закрытым
RejectedCompositeMeasurement. Scalar AdvanceUnassignedBurst сохраняет прежний
смысл. RetrySameCandidate остаётся default.

Перед переходом проверяются активная фаза Search, pending probe и его точная
Prepared identity, актуальный native lease, source/owner/model/proposal,
all-input references, epoch, run/trial и одноразовость content ID. Несовпавший
actual revision останавливает управление как InvalidModel; external stop и
deadline сохраняют свои отдельные статусы. Reference/Final этим путём не идут.

Arm уже списал logical probe. Reject списывает прежний общий invalid allowance;
повторная доставка той же группы не списывает и не восстанавливает бюджет.
Не создаются scalar, residual, reference или certificate. Сохраняются полные
параметры/C context и контрольные counters в CandidateWindowRecoveryEvidence.
Незавершённые repeats, anchor и anchor witness отбрасываются; конечный cursor
продолжает поиск через обычные domain/edit/probe действия. Сам приём отказа
не изменяет модель. RestoreBest с таким отказом даёт SearchUnresolved.

Строковый RejectCandidateWindow остаётся обычным отказом без разрешения
продвинуть cursor, в том числе при выбранной новой policy.

## Проверки, которые добавлены в исходник

18 real-component integration cases NativeCandidateWindowRecovery проверяют
Classic/Branch, N0/N1 с actual native domains, повторные N0 candidates и свежий
anchor, Missing/Ambiguous, default и строковую причину, replay, общий invalid/
probe/edit budgets, external stop и неверную revision. Выполняются штатные
native probes и реальные изменения графа, а не копия тела контроллера.
Количество18 — декларация, пока не результат выполнения.

Этот набор не доказывает native-сценарий потери ранее валидной точки именно
при RestoreBest, частичный N0 repeat с последующим изменившимся откликом,
C-context recovery, новый checkpoint или полную матрицу размерностей/физики.
Эти ограничения не отменяют соответствующие пункты общего плана.

## Незавершённые обязательные части

Service delivery, versioned cold/runtime/package/archive codecs, ordered events
и независимый Python replay ещё не реализованы. Cold1..7/runtime2/package6
не должны молча терять новую policy. Поэтому конфигурационный serializer и
native service пока явно отвергают её, а новый core API проверяется отдельно.
Guard-test является промежуточным ограничением и должен быть заменён проверкой
нового versioned roundtrip при подключении wire/service. Отдельный последующий
commit должен включить factory opt-in и доставку закрытого отказа после
beforeConsume/generation/revision/budget проверок, затем persistence/replay.

Пока эти части не готовы, новый дорогой Train с этой policy не запускать.
Финальная приёмка требует реального Console пути и исходного stock N4 A/B;
успех отдельного core gate не завершает этап7 или план0–12.
