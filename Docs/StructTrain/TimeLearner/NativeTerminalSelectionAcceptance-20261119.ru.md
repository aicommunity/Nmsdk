# Адресная приёмка native terminal selection —19 ноября2026

Проверенная комбинация: Root3c5bfe01609a6e6bd290aa9697938e885d5904b6,
Pulse1d8fc24cdb19b4b0e399483d198314b84548f9ea. M40 завершил44/44,
Elder независимо14/14. Worker validation, фактические JUnit IDs, отсутствие
ошибок assertions и закрытие supervisor/всех дочерних групп подтверждены.

| Проверка | M40 | Elder |
|---|---:|---:|
| Native terminal selection |14/14|14/14|
| Полный selected native snapshot |6/6|—|
| Kernel selected boundary |3/3|—|
| Предыдущие timing/probe-budget проверки |4/4|—|
| Physical DATA |7/7|—|
| Joint C и его rollback |6/6|—|
| Старые PostTune boundary guards |4/4|—|

Native suite:603.953с на M40,193.913с на Elder. Это реальное выполнение
компонентов, storage и scheduler на2000Гц, не копия тела функции в тесте.
Малые N=2 fixtures не заменяют научные N=4 опыты или полную режимную матрицу.
Часть snapshot transport fixtures явно использует sync0.2; это проверка
переноса, не сходимость при научном default0.02.

## Исправления и доказательства

При budget stop после edit фактический граф мог остаться неизмеренным.
Explicit terminalSelection сохраняет полный измеренный выбранный граф;
после отзыва прежнего control actor состояние Finalizing выполняет восстановление
на следующей штатной before-children границе. Резерв commit/rollback расходует
остаток исходного edit allowance. Search/probe budgets не пополняются.
История поиска сохраняет свою epoch, физическая epoch учитывает транзакции.
Ни nested Calculate, ни learner Reset для такого переноса не вызываются.

Четыре deadline cases охватывают Classic/Branch × N0/N1. Сверяются полный
semantic graph, индивидуальные параметры и повторный native отклик выбранного
входа со всеми recorded каналами; допуск сравнения samples1e−12. Отдельные
случаи проверяют C-state/отклик, explicit Reset и external stop без неожиданного
изменения графа, нехватку edit reservation, отказ attachment с сохранением
прежнего графа. BudgetExhausted сохраняется, certificate отсутствует.
Это не свежая all-input verification и не доказательство Exact.

Предыдущий snapshot gate A3 имел26/30. Независимое сравнение обнаружило,
что non-const JSON lookup добавляет baseline:null в пустое owned C-state.
Исправление использует value() без вставки поля. Все6 snapshot cases теперь
проходят; первоначальные отказы сохранены и не переписаны как успешные.

## Артефакты и остающиеся ограничения

[M40 primary](../../../Reports/StructTrain/TimeLearner/TerminalSelection-20261119/m40-primary.archive.json):
9729999 bytes,923 проверенных members; семь glog aliases сохранены как
ссылки на единственную копию их regular log bytes в manifest.
[Elder primary](../../../Reports/StructTrain/TimeLearner/TerminalSelection-20261119/elder-primary.archive.json):
3975451 bytes,361 проверенный member. Оба пакета находятся только во внешнем
M40 archive; control Git bundles, исходные traces, native readbacks, JUnit,
runtime/source provenance и kernel closure включены. В корневом Git — refs.

После этой комбинации добавлены retention исходного графа перед transaction
(Pulse592616447f4cdb17915bbd2e35fda49331ad14eb) и read-only historical export
context (Pulsec95390d9ab220c1d794787dd7462a36ff565778d). Они ещё не проверены
этими gate;14 расширенных assertions исходного graph/Dataset/C-state требуют
нового native прогона. Контекст экспорта не копирует controller/raw journal,
прежние проверки physical graph, images, C0 и measurement proof сохраняются.

Полный versioned factory/export/import/replay перехода, cold/runtime declaration
и интеграция с analysis pipeline ещё открыты. Обычные cold JSON не включают
terminalSelection, старые exporters продолжают отклонять этот scope.
Затем нужны same-budget cold A/B и actual frozen8 с читаемыми графиками.
Новый научный TP/FP/TN/FN этим gate не получен. Этапы1–12 остаются частичными.

## Следующий Console и научный контроль, 19 ноября

В cold configuration9 стоимость измерительной группы вычисляется по её базовой
composite-схеме: N+2 native волн, а не одна. `cold_budget` сохраняет исходные
search/probe limits и физику. Для explicit terminal policy он отдельно объявляет
два тика завершения после search model-time limit: обнаружение границы и применение
очереди восстановления до расчёта детей. Это не разрешение продолжить поиск.
В научном A/B оба задания должны иметь одинаковый внешний tick limit с этим
резервом. Coverage остаётся расчётом объявленных условий, без гарантии сходимости.

Первый Console control включает Classic и Branch, completed boundary и настоящее
changed-graph restoration, Window/N1. В декларации перечислены четыре case;
остальные двенадцать остаются отдельной обязательной проверкой. Исполняется настоящий
Console preflight/Train, затем export/frozen evaluation либо явно diagnostic
evaluation остановленного состояния. Каждый case имеет четыре полных Test-пробы.
Проверяются actual/historical model bindings, внешние CSV и закрытие процессов.
Инженерный N2 контроль не заменяет научное N4 обучение и не меняет его допуски.

После этого контроля приоритет — same-budget N4 Classic/Branch A/B и frozen8
с реальным подтверждением выбранного порога и Soma/input временными графиками.
Расширение инженерной матрицы выполняется вместе с научными экспериментами.
Production cold9 Train guard снимается только после подтверждения Console пути;
наличие тестового кода и отдельных успешных DATA-проверок недостаточно.

Native A8 завершён78/78; его полный primary опубликован отдельно. Первый DATA36
выявил два несоответствия Python/native: fixture scanner принимал source_graph.json
за пробу, а общий graph validator требовал подключения всех Branch banks даже
при явном allow_muted_input_baseline. Исправление сохраняет полный контроль L/Ns/Rs
и допускает только полностью отключённый банк в разрешённой Branch-модели.
Частичное отключение, дубли, чужой stimulus и неверный slot остаются ошибками.
Это повторяет штатный контракт NativeModelBuilder/CandidateWindowProposalReplay;
модель и научные допуски не меняются. Исправление требует повторного DATA gate.

Парный Console control завершён4/4 cases: два completed и два настоящих restored
Train,14 native операций,16 frozen наблюдений, обе test methods PASS. Полный
primary опубликован вместе с исходным отклонённым DATA36 и N4 A/B декларацией;
ошибки DATA36 не переписаны как успешные. После этого контроля production run_job
допускает explicit terminal Train только с contained process policy. Общая
рекомендация V2 и приёмка всей режимной матрицы остаются открытыми. Интеграционный
тест переведён на сам run_job Train и будет проверен этим же производственным
путём. Исправлен оставшийся доступ к C0 legacy schema1 в terminal journal;
отсутствие исторического поля по-прежнему не создаёт физический witness.
