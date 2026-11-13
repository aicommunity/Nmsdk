# N1: следующие адресные вопросы после текущего A3

Текущий same-budget A3 ещё не завершён; ниже выводы из production кода, не его научный исход. Runtime A3 и подготовленный набор не меняются.

1. MeasuredResistanceSearch.cpp требует >=3 различных измеренных Rs в одном физическом scope перед bracket refinement. Один дополнительный local turn даёт новое измерение, но сам по себе не гарантирует трёх точек до возврата в общий обход. После A3 проверить число уникальных Rs на каждой timing-ready геометрии и реальные residuals. Если refinement так и не достигается, оформить конечный local normalization turn с явным allowance, используя прежние global budgets; измерять каждый кандидат, не выводить сходимость из bracket.

2. BoundedTraining.cpp::PrioritizeMeasuredLength заменяет только active length в историческом full vector, после чего требует полного совпадения с текущим vector. В Branch рост одновременно перемещает ещё не посещённые upstream attach positions. Поэтому реально соседние точки одного детерминированного семейства могут не попасть в length proposer. MeasuredLengthSearch.cpp уже умеет предлагать bounded extrapolated candidate по измеренному тренду; вопрос в допуске точек к нему.

Предлагаемая проверка/реализация: выделить штатный builder полного семейства из background, input, length, topology variant и C-context; предыдущая и текущая точки допустимы для proposal только если обе точно воспроизводятся этим builder, inactive Rs/Ns/profile/C совпадают, anchor/committed downstream неизменны. Варианты общего банка не смешивать. Прогноз служит только порядку легальных кандидатов, никогда сертификатом: новый domain, edit, fresh anchor и assigned-burst probe обязательны. Ограничить дальность предложения и сохранить конечный широкий обход; конкретное allowance/step policy фиксировать до следующего A/B.

Проверки: реальный production session с N4 upstream propagation, separate variants, неподходящее C/Rs/physics, немонотонный measured trend, invalid/missing probe, finite global budget, неспособность локального успеха заменить all-input final verification. Затем native same-budget Branch comparison; положительный эффект не требовать ради PASS инженерного теста. Не реализовывать по одному изменению L/Rs без сохранения честной причины остановки.

## Реальный A3 и следующая реализация

A3 закончен:1/1 PASS2757.464s; native process2062.995s, outer2781.789s. BudgetExhausted, certificate=null;52candidates/55domains/105search probes,0rejections. В варианте[26,26,25,1] input2 Rs86M даёт amp−0.0118549032499361,timing−0.015s; Rs2.880071555M даёт amp+0.06956639592980918,timing−0.017s. Все5timing-ready точек остаются amplitude-outside. Наличие измеренного sign change не доказательство exact/полной достижимости; последняя unconsumed геометрия[27,27,26,1] приRs2.88M не считается сертифицированной.

Реализованы (ещё без серверного PASS): SameBranchLengthProposalFamily для обычного/разделённого банка, строгие inactive Rs/Ns/downstream/background и C-context guards; ограничение length proposalL/2..2L; конечный local normalization allowance=min(12,remaining candidates/4,remaining probes/8,remaining edits/4). Это перераспределение прежних global budgets, не расширение задания. Domain и обе пробы остаются свежими; при nonmonotone/неподходящих данных сохраняется mesh fallback. Новые tests охватывают само исключение чужих families и production controller N4, достигающий далёкой длины до плотного перечисления.

В этом же следующем варианте Rs refinement ускорен safeguarded log-secant внутри measured sign bracket (fraction[0.25,0.75]), с overflow-safe normalized residual magnitudes. Новый Rs всё равно реально измеряется. Это не ослабление amp tolerance и не интерполяционный сертификат; добавлены bounded nonlinear-response и extreme finite-data controls.
