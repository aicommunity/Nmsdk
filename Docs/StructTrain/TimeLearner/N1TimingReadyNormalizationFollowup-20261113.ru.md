# N1: адресное продолжение после полной Branch истории

Статус: постановка следующего исправления; код и научная приёмка ещё не выполнены. Основание — exact summary8 полного Branch N4 Train,51 consumed candidates/52 domains. Из52 assessments27 locked и25 unlocked; все51 измерения при86M. Четыре timing-ready, в том числе unlocked [26,26,25,1] и [27,27,26,1], но вне амплитудного допуска. Это не отсутствие физически разрешённого Rs и не доказанная недостижимость амплитуды.

Первое изменение следует направить в Core/TimeLearner/BoundedTraining.cpp: NextDomainCandidate, AssessedDomain, AcceptValidatedScalar; состояние bounded priority — CandidateCursor в BoundedTraining.h. NativeModelEditor.cpp должен сохранить запрет несогласованной правки общего банка. Уже реализованный вариант разделения upstream bank сохраняется. Групповой edit — отдельная возможность, а не обязательное решение для unlocked геометрий.

Ограниченный локальный поиск должен использовать измеренную готовность, без смены CapturedPerInput и исходных tolerances:

~~~text
consume complete valid candidate for current revision
if timing-ready and amplitude outside tolerance:
    enqueue a bounded local normalization turn for this full geometry
    keep the broad geometry cursor and remaining global budgets

local turn:
    reassess effective native Rs domain on the current physical context
    intersect only the active input's declared box and physical domain
    propose an unissued legal Rs; no global monotonicity assumption
    apply at the native edit boundary; invalidate affected observations
    remeasure anchor and assigned impulse through the native burst
    rank measured residuals using original rules
    return to broad traversal after the finite local-turn allowance

finalize only through a fresh all-input verification
~~~

Не подставлять общий максимум пачки. Не сохранять stale anchor/certificates после Rs edit. Не объявлять PhysicalInfeasible из отсутствующего bracket/локального stall. Исчерпание бюджета остаётся BudgetExhausted. Нельзя исправлять controller, просто удалив shared-bank lock: источник и все владельцы физического банка должны оставаться согласованными.

Проверки: существующий dense-Rs fairness control должен сохранять достижение других длин; новый production session control должен показать рассмотрение другого Rs до полного прохода всех длин на timing-ready unlocked геометрии. Нужны отдельные случаи singleton domain/граница, немонотонный отклик, invalid observation, external stop и исчерпание local/global budget. Поддельный provider используется только для адресного controller unit test; физический эффект подтверждается настоящим native component probe/Train.

Физический контроль на [27,27,27,1] (replay, matched86M, all-bank21.5M) уже поставлен отдельно. Он проверяет изменение отклика при согласованной правке owners0/1/2, но не доказывает сходимость, не измеряет всех input certificates и не заменяет контроль unlocked-normalization scheduling. Выбор локального proposer/allowance окончательно фиксировать по измеренному контролю и конечному A/B с теми же исходными бюджетами; не увеличивать бюджеты и не ослаблять амплитудный допуск ради PASS.

## Реализация ограниченного локального хода

В рабочей ветке реализован один дополнительный Rs-кандидат на геометрию за проход после полного valid timing-ready/amplitude-miss измерения. Повторное улучшение не пополняет allowance; invalid observation его не создаёт. Затем обход обязательно продолжает другие геометрии. Native domain заново оценивается, visited candidates исключаются, после edit заново измеряются anchor и закреплённый импульс. Состояние allowance принадлежит C-контексту. Численные бюджеты и математические цели не изменены. Это ограниченный первый шаг; гарантии достижения амплитудной цели или глобальной монотонности не заявляются.

Добавлены production-session controls для Classic/Branch, потери timing после Rs, изменившейся нижней границы, singleton domain и global probe exhaustion; прежние dense-mesh fairness и refinement controls сохраняются. До серверной проверки изменение считается только реализованным в коде; научный A/B с теми же исходными бюджетами ещё требуется.

## Серверная приёмка контроллера

[Изолированная сборка и77/77 native controller checks приняты](ValidationPlans/M40N1LocalTurnSdkA1-20261113/RESULT.ru.md) на root4acc1f0ec/Pulse9656b420. В том числе production session подтверждает другой Rs перед новым L при timing-ready miss, обязательный свежий domain/anchor, singleton/global budgets и сохранение dense-mesh fairness. Это адресная инженерная приёмка. [Научный same-budget Branch Train A3 завершён](N1LocalTurnScientificReport-20261113.ru.md): BudgetExhausted, найден измеренный Rs sign bracket при допустимом timing, amplitude convergence не достигнута. A1 был отклонён до моделирования из-за runtime-привязки; защита сохранена. A2 подготовлен, но не запускался; production rebind принят в A3. [Следующая coupled-search версия](N1CoupledProposalReview-20261113.ru.md) проходит самостоятельную native приёмку.
