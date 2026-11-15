# Ограниченный поиск C: измеряемые предложения и оставшаяся интеграция

Новая ветка от develop, отдельная от ещё принимаемого automatic C₀ owner.
Реализованы production kernel предложений C и полный pure candidate C-state.
Подготовлен [native bridge чтения/совместного применения](NativeTrainingCapacitanceBridge.ru.md);
его runtime-приёмка ещё не выполнена.
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
Они включены в штатный Test_PulseLib_StorageComponents target; его полная
сборка/прогон с новым модулем ещё не выполнены. Отдельная серверная unit-проверка
состоялась:23/23 на Elder normal и23/23 на M40 ASan — новые12 плюс6 length
и5 resistance regressions. Компилировались полные production .cpp и полные
штатные test files из Git, а не извлечённые тела функций. Изолированная сборка
не касается leased native source/build/runtime. GTest dependency paths/hashes,
compiler flags/version, binary SHA, loader diagnostics и stdout/JUnit сохранены.

Root test snapshot `b951fb3d44eb713a21d5aefd69b13f0e9440ac77`, Pulse
`0832d3ea17fa0a224a332d802f0cee00514c7cec`. Normal proof
`e311c97eeb0eb44270a027b9e2aec68ca16fdeb6`, ASan proof
`6da55382f2600db42ed69073da281cb67e5626a5`: проверены13 members каждого архива,
outer hashes и совпадение всех9 production/test file hashes с Git sources.
Archives7904/7224 bytes; active source_closure до/после совпали. ASan loader
init libasan подтверждён. Полный SDK target, native provider comparisonScope,
контроллер C-trim, model transfer, waveform tests и scientific verdict этим
unit gate не подтверждаются. В develop модуль пока не принят.

Documentation child closure — `36641d2a309165ed2a28efd3670a3670a1bf1a18`;
Core tree `c1cd832a243750c421e8c9fb4e12690f3aab140f` совпадает с tested0832d3e.
После child push feature-root gitlink обновлён. Численные owner/transport jobs
не переключались на этот kernel; их данные/исходные SHA сохранены отдельно.

## Рабочая интеграция полной карты в decision controller

В эту feature через merge commits включена зависимость automatic C₀ owner;
её native/ASan/transport приёмка остаётся отдельной pending работой. Это не
объединение owner в develop и не переключение работающих jobs.

Новый pure TrainingCapacitance хранит origin hash, bound policy и полную карту
абсолютных per-membrane scales, включая dormant paths. BoundedTrainingSession
принимает её явно: actions, candidate evidence и repeat groups удерживают карту;
Applied сверяет C readback наряду с L/Ns/Rs; derived Rs assessment не может
опустить или заменить C context. Growth допускает только новые unit entries;
известные entries не исчезают. Restore historical best сохраняет полный
накопленный C₀ path inventory, но возвращает отсутствующие в old best новые
поправки к1, не заимствуя более поздний trim. Origin/policy не переопределяются.
Сравнение timing proposals допускает разницу только в дополнительных unit
entries; равенство C-карты не означает равенства полного физического графа.

Это подготовленное изменение pure decision path. NativeTrainingService и
BindNativeTraining ещё не передают новую карту; versioned summary codec/readers,
configured C policy и сам поиск C пока не подключены. Нельзя объявлять этот
срез working C-trim On. Добавлены6 state-level и5 production-session unit
controls; проверки на серверах подготавливаются. Старые callers без C-карты
сохраняют None/unknown provenance, а не получают вымышленный C₀.

Первая strict unit сборка B1 на root629876c13/Pulse31f27af остановилась до
исполнения84 tests: четыре прежних conditional GTest assertions требовали
явных braces. Normal failure proof16eb145511bda89e6503a20962cc15f0227a2679,
ASan d33f8027425004bbf7f993e21615af8d9c18777d; все8 members каждого архива
проверены, observed_tests=0. Test-only исправление4f4d5f5ad не меняет assertions.

B2 затем выявил прежние implicit empty optionals PeakObservation и misleading
indentation в independent Stop/reset statements. Failure proofs:
normal4d267c9134189828b3baae732709eb176a5235e6,
ASan8c6bec8af49ebfc73dd53531eb3d510d66320b5d. Численные tests не выполнялись.
Это compile diagnostics, не научные FAIL и не подтверждение C-state behavior.
Отдельные Pulse refactor commits3ee9975 и9d95f05 явно задают прежние nullopt
defaults и границы независимых statements, не заменяя unknown measurements
нулевыми числами. Следующий strict gate включает27 observation и19 final
verification regressions дополнительно к84 controller/proposal/state cases:
итого130 tests. Полный native C-trim pipeline по-прежнему не включён.

B3 сохранил старую разметку изолированной unit сборки production/Core; два
добавленных прежних теста используют repo-relative includes SDK, поэтому до
исполнения tests получен header-not-found. Это ошибка harness layout, не
ошибка алгоритма. Повтор сохраняет реальные пути Libraries/Nmsdk-PulseLib/Core
и Tests/Integration/Libraries; source/test файлы целиком берутся из Git.
Ещё один conditional GTest assertion observation fixture получает явные
braces без изменения смысла. Native sources/runtimes текущих jobs не меняются.

Unit B5 завершён на root `0a3c5b0f10b0b0448b21dddb9d3ee6bb483d876d`,
Pulse `9d95f05790b04a4505541d398fd039fa56e6a65f`:130/130 normal и130/130 ASan.
Proofs `8214f20625b5287d72f388f7f7005e86eabfd59f` и
`88e96182c184b242e2185eeca76a095c8666e294`; каждый архив13 members,
13 692/13 136 compressed bytes. Проверены outer/member hashes и соответствие
всех24 production/test files Git sources. Actual loader init libasan и
неизменность active source_closure подтверждены. Это pure controller/state/
observation/final-gate unit scope, не native adapter или рабочий C-trim On.
B1–B4 build failures сохранены отдельно с0 выполненных численных tests;
все8 members каждого отрицательного архива проверены. B4 исправляет copy
range element в прежнем observation test, не меняя численных условий.

Prerequisite уточнён после native diagnostics E1–E8: исходные четыре dormant
fixtures нарушали owning-tree load lifecycle и затем initial search-domain.
Исправленный explicit-graph setup прошёл4/4 normal same/fresh-process transports;
independent readers3/3 проверили actual packages и semantic negative controls.
[Текущая приёмка owner](CapacitanceOwnership.ru.md) всё ещё требует normal43 и
ASan owner8/transport43. Следующий механический bridge описан отдельно; service,
versioned codecs/readers и bounded C search ещё не подключены. В develop эта
feature не принята; общий план0–12 не завершён.
