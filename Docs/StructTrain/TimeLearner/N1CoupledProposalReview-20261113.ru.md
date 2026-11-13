# N1: следующие адресные вопросы после текущего A3

Ниже сохранена постановка, составленная до завершения A3; его окончательный исход приведён в следующем разделе и [научном отчёте](N1LocalTurnScientificReport-20261113.ru.md). Проверенный runtime A3 не меняется. Следующая реализация проходит отдельную native приёмку.

1. MeasuredResistanceSearch.cpp требует >=3 различных измеренных Rs в одном физическом scope перед bracket refinement. Один дополнительный local turn даёт новое измерение, но сам по себе не гарантирует трёх точек до возврата в общий обход. После A3 проверить число уникальных Rs на каждой timing-ready геометрии и реальные residuals. Если refinement так и не достигается, оформить конечный local normalization turn с явным allowance, используя прежние global budgets; измерять каждый кандидат, не выводить сходимость из bracket.

2. BoundedTraining.cpp::PrioritizeMeasuredLength заменяет только active length в историческом full vector, после чего требует полного совпадения с текущим vector. В Branch рост одновременно перемещает ещё не посещённые upstream attach positions. Поэтому реально соседние точки одного детерминированного семейства могут не попасть в length proposer. MeasuredLengthSearch.cpp уже умеет предлагать bounded extrapolated candidate по измеренному тренду; вопрос в допуске точек к нему.

Предлагаемая проверка/реализация: выделить штатный builder полного семейства из background, input, length, topology variant и C-context; предыдущая и текущая точки допустимы для proposal только если обе точно воспроизводятся этим builder, inactive Rs/Ns/profile/C совпадают, anchor/committed downstream неизменны. Варианты общего банка не смешивать. Прогноз служит только порядку легальных кандидатов, никогда сертификатом: новый domain, edit, fresh anchor и assigned-burst probe обязательны. Ограничить дальность предложения и сохранить конечный широкий обход; конкретное allowance/step policy фиксировать до следующего A/B.

Проверки: реальный production session с N4 upstream propagation, separate variants, неподходящее C/Rs/physics, немонотонный measured trend, invalid/missing probe, finite global budget, неспособность локального успеха заменить all-input final verification. Затем native same-budget Branch comparison; положительный эффект не требовать ради PASS инженерного теста. Не реализовывать по одному изменению L/Rs без сохранения честной причины остановки.

## Реальный A3 и следующая реализация

A3 закончен:1/1 PASS2757.464s; native process2062.995s, outer2781.789s. BudgetExhausted, certificate=null;52candidates/55domains/105search probes,0rejections. В варианте[26,26,25,1] input2 Rs86M даёт amp−0.0118549032499361,timing−0.015s; Rs2.880071555M даёт amp+0.06956639592980918,timing−0.017s. Все5timing-ready точек остаются amplitude-outside. Наличие измеренного sign change не доказательство exact/полной достижимости; последняя unconsumed геометрия[27,27,26,1] приRs2.88M не считается сертифицированной.

Реализованы (адресная A4 SDK-проверка93/93 принята; новый physical N4 исход ещё ожидается): SameBranchLengthProposalFamily для обычного/разделённого банка, строгие inactive Rs/Ns/downstream/background и C-context guards; ограничение length proposalL/2..2L; конечный local normalization allowance=min(12,remaining candidates/4,remaining probes/8,remaining edits/4). Это перераспределение прежних global budgets, не расширение задания. Domain и обе пробы остаются свежими; при nonmonotone/неподходящих данных сохраняется mesh fallback. Новые tests охватывают само исключение чужих families и production controller N4, достигающий далёкой длины до плотного перечисления.

В этом же следующем варианте Rs refinement ускорен safeguarded log-secant внутри measured sign bracket (fraction[0.25,0.75]), с overflow-safe normalized residual magnitudes. Новый Rs всё равно реально измеряется. Это не ослабление amp tolerance и не интерполяционный сертификат; добавлены bounded nonlinear-response и extreme finite-data controls.

## Первая серверная проверка:91/93, новый Train не запущен

Root084cee615b81fa591ea2951fefaf12006bddaea3/Pulse7c6c94785af0c83104d348bb3b733ed1f149c8a8 собраны полностью. Все93 заявленных cases выполнены,91 прошёл; исходный FAIL сохраняется [отдельно](ValidationPlans/M40N1CoupledSdkA1-20261113/RESULT.ru.md). Отказавший старый N2 Branch test ожидал L12 в5 candidates; новый объявленный factor-two guard требует промежуточного измерения L8 и честно исчерпывает этот малый budget. Теперь fixture проверяет оба исхода:5→BudgetExhausted/L8 и6→Exact/L12, при неизменном Classic поведении и обязательном effective domain. Это изменение ожиданий адресного synthetic fixture, не увеличение scientific job budget.

Новый pure resistance-helper test произвольно требовал nonlinear1/R convergence1e-8 за12 calls; фактически получен1.3113062138914167e-7. Safeguard[.25,.75] гарантирует сжатие bracket, но не такое число шагов. Fixture теперь использует доказанный верхний bound64: на[4,16] производная по log(R) ограничена1/4, поэтому residual<=(log4/4)*.75^64<1e-8. Каждый кандидат по-прежнему заново измеряется toy response. Controller local allowance<=12, научные budgets иamp1e-5/sync.02 НЕ изменены. Pure helper convergence не обещает сходимость в12 local controller turns. Production Pulse code7c6c9478 не меняется. Новая полная native проверка требуется до Train.

A2 завершилась до запуска93 cases: два SCOPED_TRACE на одной строке диагностического fixture создавали одинаковое имя переменной GoogleTest. Исправление — разнести макросы по строкам; production algorithm неизменен. Whole kernel group закрыта, original compile failure и terminal cache сохраняются. Следующая A3 использует штатно допустимый существующий build cache только последовательно после closure; отдельный runtime и immutable commit capture до/после. Старые runtime защищены. Это не обход failed assertions и не изменение их математической цели.

Уточнение по фактическому production path: canonical A3 отверг существующий build с canonical_source_or_fresh_build до compiler/test/model execution. Раннее предположение о допустимости incremental cache было неверным для этого верхнего guard. Он не изменён; A4 использует чистый build/runtime. Старые failures сохраняются, математическая задача и production Pulse7c6c9478 прежние.

## Текущее подтверждение после A4

Fresh A4 root74e5d206d4b619fcf81f77f11b54ebec7b8f0f6e/Pulse7c6c94785af0c83104d348bb3b733ed1f149c8a8:93/93 cases PASS, все kernel groups закрыты; [полные исходники/результаты проверки](ValidationPlans/M40N1CoupledSdkA4-20261113/RESULT.ru.md). Старые failure outcomes сохранены. Same-budget cold Branch s07-n1-coupled-branch-train-m40-a1 запущен после gate; preflight completed и начались native raw trials. Scientific outcome/классификация нового варианта пока не установлены. Прежний измеренный bracket A3 относится к другому коду9656b420 и не перенесён на новый run как сертификат.

## Уточнение14.11 после фактического завершения

[Новый Branch Train](N1CoupledScientificReport-20261113.ru.md) завершён: одна jointly-ready input2, затем invalid_observation input1. [Реальный fixed-threshold diagnostic](BranchCoupledThresholdScientificReport-20261114.ru.md) дал TP1/FP5/FN0/TN2, target до последнего входа. Ранний текст «outcome ещё не установлен» выше относится к моменту запуска и больше не описывает текущее состояние.

Проверен recovery_ledger исходного native/train_stopped_summary.json (16103173B, SHA25694f28cc3abf9d31bdcf70a2cec653e055b60533e89cae0a84f126b3b2163e060; весь файл сохранён в [Train primary](ValidationPlans/M40N1CoupledPrimaryA1-20261113/RESULT.ru.md)). Пять ambiguous отказов относятся к разным полным векторам:

| search | epoch | L0,L1,L2,L3 | Rs0,Rs1,Rs2,Rs3 | disposition |
|---|---:|---|---|---|
|90|21|28,28,27,1|86M,86M,21.232304307596M,86M|cursor_advanced|
|95|22|29,28,27,1|86M,86M,21.232304307596M,86M|cursor_advanced|
|99|23|29,29,27,1|86M,86M,21.232304307596M,86M|cursor_advanced|
|103|24|30,29,27,1|86M,86M,21.232304307596M,86M|cursor_advanced|
|107|25|28,27,27,1|86M,21.232304307596M,21.232304307596M,86M|invalid_budget_stop|

Это не повтор одной точки и не дефект отсутствия продвижения cursor. Первые4 восстановления расходуют объявленный общий allowance4; пятое невалидное наблюдение останавливает поиск. Ни одна из этих точек не становится measured timing/amplitude candidate. Нельзя исправлять этот исход повышением allowance или объявлением merged peak valid.

Открыт вопрос порядка исследования геометрий и возможности отдельно измеримого раннего пика при общем кабеле. Пока причинная коррекция алгоритма из этих данных не доказана. [Сопоставимый текущему Branch-budget холодный Classic контроль](ValidationPlans/M40N1CoupledClassicCold4A1-20261114/STATUS.ru.md) выполняется на том же SDK, но прежний Classic recovery16 остаётся другим протоколом. После результата сравнить реальные assigned observations и причины остановки до новых изменений поиска.
