# Ограниченный поиск C: измеряемые предложения и оставшаяся интеграция

Новая ветка от develop, отдельная от ещё принимаемого automatic C₀ owner.
Реализован только production kernel предложений C-кандидатов и его тесты.
NativeTrainingService пока его не вызывает; SyncCapacitanceTrim On для V2
остаётся явно неподдержанным. Этот документ не объявляет этап7 завершённым.

## Реализованная математическая часть

Core/TimeLearner/MeasuredCapacitanceSearch задаёт абсолютный положительный
scale относительно immutable individual C₀. Сетка конечна: current, единица,
границы и dyadic subdivisions, с явным пределом числа кандидатов. Фиксированный
домен даёт ровно одно значение. Результат сетки не означает допустимость
интегратора, достижимость цели или сходимость.

Measured refinement принимает signed timing interval и comparisonScope
каждой реально измеренной точки. Scope обязан учитывать input, набор меняемых
membrane paths, исходные C₀ и всё остальное эффективное физическое состояние,
включая реальные banks/bindings, другие C, timestep и reset/stimulus protocol.
Его не заменяют L/Ns/Rs или raw model revision: при изменении C последняя
закономерно меняется. Наличие поля не доказывает правильность native provider;
его реализация и отрицательные native проверки ещё обязательны.

```text
validate explicit positive finite scale domain and refinement policy
reject mixed scope, nonfinite values or reversed measured timing intervals
discard points outside the currently declared domain
merge repeated scales using full interval union; never average away uncertainty
require three distinct scales with a consistent measured timing trend
if a measured interval already meets refinement tolerance: propose nothing
if measured neighboring intervals bracket zero:
    propose their unmeasured bounded midpoint
otherwise, for a one-sided non-flat measured trend:
    propose a damped secant scale, clamped to explicit bounds
otherwise: retain finite mesh fallback
```

Любое предложение ещё требует joint physical preview, свежего anchor/input
наблюдения и свежей all-input проверки. Отсутствующий bracket, некорректные
повторы, nonmonotonicity, clipping либо исчерпание сетки не являются
PhysicalInfeasible/Exact. Refinement tolerance не заменяет исходный SyncTolerance.

## Обязательные следующие изменения полного контроллера

1. BoundedTraining action/candidate/evidence должны переносить полный absolute
   per-membrane scale map, включая unchanged/dormant state, вместе с L/Ns/Rs.
   Одно scalar поле в InputParameters не описывает history после growth.
2. NativeTrainingService/adapter читают и сверяют фактическую C-карту; initial
   C₀ захватывается в объявленном исходном состоянии до первого C-search edit.
   Используется owner mechanism, а не повторный capture уже trimmed каналов.
3. Classic выбирает разрешённый путь; Branch — интервал L[k+1]+1..L[k].
   При совпадающих attach positions пустой interval не исправляется скрытым
   ростом. Anchor restrictions сохраняются; shared edits консервативно
   инвалидируют все affected observations и Rs domains.
4. Rs domain рассчитывается по тому же joint L/Ns/Rs/C preview, что затем
   применяется. Нельзя отвергать совместно допустимый кандидат из-за опасного
   промежуточного C-only edit при старой Rs. Проверяется actual integrator;
   legacy MinTau не подменяет его универсальным tau/dt правилом.
5. ConfiguredNativeTraining получает явную versioned optional C policy;
   старые schemas1/2 и default Off сохраняют прежнюю задачу. Legacy absolute-F
   DendriteCapacitance нельзя незаметно трактовать как dimensionless scale.
6. NativeTrainingProof/LearnedState/Python readers переносят полную policy,
   C-карту, измеренные candidate witnesses и итоговый model hash. Старые
   certificates не переживают эффективное изменение модели автоматически.
7. Принятие требует native Classic/Branch × N0/N1 ×2k/20k, heterogeneous C₀,
   Branch shared effects, integer normalization, unsafe joint candidates,
   rollback/interruption, active/dormant growth и fresh-process frozen transfer.
   Все временные реакции должны быть доступны в читаемых soma/input reports.

## Подготовленная проверка kernel

12 GTest cases вызывают production module: bounded finite mesh, fixed domain,
budget/invalid declarations, both timing directions, mixed full-physics scope,
inconsistent repeats, nonmonotonicity/flat response, plateau intervals, damped
extrapolation/clipping, changed domain, nonfinite values и extreme finite ranges.
Они входят в штатный Test_PulseLib_StorageComponents target. Серверная проверка
самого kernel готовится отдельно от длительных native owner/transport jobs;
её нельзя выдавать за выполненную интеграцию C-trim в controller.
