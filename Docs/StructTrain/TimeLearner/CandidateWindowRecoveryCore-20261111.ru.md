# Переход bounded search после закрытого отказа candidate-window

Статус: новый код ядра, серверная проверка впереди. Предыдущий фундамент
допуска проверен на root9d51f808047f08e0cbfa0e440061f9bf04e8ba88 / Pulseaf612ba:
Elder и M40 выполнили29/29 cases,29 отдельных leaf gates; outer+29child groups
закрыты, reservations released, record_errors=[] на каждом сервере.
Это приёмка sealed measurement/rejection factory, не нового перехода поиска.
Полный compact primary M40 сохранён в
[Reports](../../../Reports/StructTrain/TimeLearner/RejectionFactory29B1-M40-20261111/artifact-inventory.json):
1267 исходных файлов и3 observer members,87095233bytes expanded,
2776140bytes XZ, SHA256ef485b91f9e3e3586681d9351d3905b628c00c9c3cdeb2f470c9c040a4c9d12b.
Commit214bf5888665c9bc15d9e1a514aa09e30571d07a включён через merge commit.
После Git-переноса сверены hashes всех4 payload artifacts; независимый
семантический replay ещё не выполнен. Elder1267files инвентаризированы,
но collector получил reservation_capacity_exhausted при занятом C1;
полный Elder compact primary остаётся открытым пунктом.

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

Следующее отдельное изменение реализует
[cold8/runtime3 и их readers](CandidateWindowRecoveryWire-20261111.ru.md).
Оно следует после frozen C1 и не входит в работающие145 проверок.
Описанные ниже serializer guards относятся к снимку C1;
в текущем дереве сохраняется service guard до готовности persistence/replay.

Service delivery, versioned package/archive codecs, ordered events
и независимый Python replay ещё не реализованы. Cold1..7/runtime2/package6
не должны молча терять новую policy. Native service пока явно отвергает её,
а новый core API проверяется отдельно. В снимке C1 serializer также отвергает
policy; в следующем wire commit этот guard-test заменён проверкой cold8/runtime3
roundtrip с сохранённым запретом service. Отдельный последующий
commit должен включить factory opt-in и доставку закрытого отказа после
beforeConsume/generation/revision/budget проверок, затем persistence/replay.

Пока эти части не готовы, новый дорогой Train с этой policy не запускать.
Финальная приёмка требует реального Console пути и исходного stock N4 A/B;
успех отдельного core gate не завершает этап7 или план0–12.
