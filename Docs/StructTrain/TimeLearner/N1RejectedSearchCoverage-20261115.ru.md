# N1: покрытие поиска после неоднозначного отклика — 15.11.2026

Статус: подтверждённое ограничение порядка поиска, исправление ещё не реализовано. Источник: s11-uniform-profile0-N1-train-m40-a1, source043c36cf4253956c9806d715dd0852e8a3508688, Pulse5052cfe1683ca38920b514aedfc3c37f4bd41aef. Полный primary — external archive3eb998b76c8263940988ea7d219be44189b695a66af90bf68b91221c774017ec; см. FastProfilePhysicsAcceptance-20261115.json и научный отчёт текущей пары.

После locally jointly-ready input2 (L27/Rs21.232304307596028МОм) input1 реально проверен на следующих полных структурах:

| Последовательность | Полные L | Rs input1, МОм | Результат |
|---|---|---:|---|
|1|28,28,27,1|86|ambiguous|
|2|29,28,27,1|86|ambiguous|
|3|29,29,27,1|86|ambiguous|
|4|30,29,27,1|86|ambiguous|
|5|28,27,27,1|21.232304307596028|ambiguous; stop|

Заявленная верхняя граница256 не означает, что здесь исследованы длины выше29 у активного входа1. Последняя структура меняет вход1 и общий bank: её нельзя называть моделью измеренного успешного input2, который проверялся на L[28,28,27,1]/Rs[86,86,21.232304307596028,86]МОм. AcceptedParameters означает фактически принятое редактирование, а не научную готовность. Это должно оставаться явным в отчётах.

Компоненты: Core/TimeLearner/BoundedTraining.cpp: NextDomainCandidate, AdvanceDomainGeometry, PrioritizeMeasuredLength, обработка rejected candidate window; MeasuredLengthSearch.cpp и per-candidate ResistanceDomainAssessment. PrioritizeRejectedN0BranchLength явно исключает N1 и работает с отдельной N0-очередью. Механическое снятие этого условия неправильно: N1 обязан заново оценивать реальную область Rs после каждой смены геометрии.

## Следующая адресная правка алгоритма

Цель: в ограниченном восстановлении после ambiguous/missing peak исследовать новые законные области совместного L/Rs, не расходуя все попытки лишь на соседние attach/layout-варианты. Математическая цель, допуски, бюджет probes/edits и штатный native protocol сохраняются.

    after rejected assigned-peak observation:
        retain the rejection and its exact geometry/revision
        select an unissued legal recovery proposal in the current search family
        vary layout/length and allowed normalizer using a bounded declared order
        preserve committed downstream inputs and required Branch bank equality
        request a new native ResistanceDomainAssessment for a new geometry
        choose only a finite positive Rs inside that actual per-input domain
        apply through the native adapter at a legal boundary
        obtain fresh anchor and input observations
        never turn missing/ambiguous responses into residuals or a bracket

Сначала воспроизвести текущий узкий порядок на production BoundedTrainingSession. Изменение N1 держать отдельным от уже принятого N0 recovery; отдельно проверить, что обычная valid-observation последовательность и N0 не изменились. Решить и зафиксировать конечный порядок покрытия осей L/Rs, включая зависимые upstream attach positions; не предполагать монотонности validity по L или Rs. Дальние L и границы Rs — гипотезы для измерения, не доказательство физической невозможности.

Обязательные проверки: исходный неоднозначный N1-сценарий, per-input Rmin/Rmax и shared-bank lock; разные upstream Rs; недоступная/неподдерживаемая область; запрет повторного использования старого assessment; конечные/минимальные диапазоны L; исчерпание общего бюджета; unchanged N0 и valid N1 prefix. Затем isolated native SDK и same-condition cold Branch N1 A/B с полными waveform/omission/repeat отчётами. Нельзя увеличением лимитов скрывать ошибку порядка поиска.

Текущая семантика maximum_invalid_observations=4 допускает четыре восстановления, затем пятое неверное наблюдение останавливает поиск. Фактический счёт не скрывать под фразой «всего4 invalid». Если менять этот контракт на жёсткий предел общего числа наблюдений, сделать отдельное версионированное изменение и сохранить чтение исторических ledger.

## Отдельное ограничение быстрого профиля

s11-uniform-profile3-N1-train-m40-a2 достиг timing-ready L121/Rs86МОм лишь к концу native wall1800с: остаток времени0, амплитудный−0.02347230991428706 при допуске1e-5. Измерены16 scalar candidates; исходный профиль успел22. Это BudgetExhausted, не PhysicalInfeasible. Дополнительный cold run с явно большим wall allowance может проверить амплитудную нормализацию этой области, но будет отдельным exploratory условием; его нельзя выдавать за первоначальную пару с прежним бюджетом. Начальные per-input targets захватывать заново, не переопределять по уже выросшей структуре и не имитировать unsupported checkpoint.
