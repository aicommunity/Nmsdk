# Прерывание пробы при импорте остановленного состояния

Исходное ограничение: source-baseline перед изменением Rs уже сохраняла
частичную CSV/JSON при отмене, timeout или исчерпании числа шагов, но затем
внешний Require прерывал формирование execution.json. Такой результат был
непроверенным выполнением; его нельзя было выдавать за успешное вмешательство.

Изменение в `f679d0410dd00a36995f9d32cc03812438819bb7` сохраняет частичный
native result как итог именно выполненной фазы. При незавершённой baseline:

1. Не применять Rs и не создавать основную пробу.
2. Сохранить исходный эффективный граф и неизменную controller history.
3. Записать initial/final state и полную artifact closure, включая реальный
   cancel.request при отмене.
4. Выдать execution schema3 с `terminal_phase=source_baseline` и
   `resistance_intervention_applied=false`.

При завершённой baseline изменение выполняется через штатный consumed probe
boundary; основная проба имеет `terminal_phase=main_probe`. Даже совпадающее
с прежним значение Rs отмечается как выполненное вмешательство, если native
editor принял эту операцию. Реальное изменение физики проверяется по графу.

Schema3 применяется к imported jobs; cold jobs продолжают выдавать schema2.
Старые execution schema1/2 читаются с прежним составом analysis, чтобы не
переподписывать исторические production manifests. Новый reader связывает
phase, applied flag, полный граф, фактический terminal packet, его trial ID,
причину прерывания, лимит шагов и measured wall budget. Наличие одного файла
отмены не подтверждает состоявшееся прерывание.

Адресная матрица: Classic/Branch × completed, baseline timeout, baseline
cancel, baseline tick budget, main cancel, main tick budget. Семь readers
проверяют реальные packets и отказы на повторно подписанные повреждения
phase/applied/boundary/request/budget/completion. Для completed отдельно
сравниваются девять исходных физических primary файлов; для старых запусков
повторно читаются оригинальные manifests без изменений.

## Runtime-приёмка 04.11.2026

Набор `readbacks/s03-native-probe-phases-{normal,asan}-a1` прошёл на обоих
worker: по12 реальных jobs и7 readers, без errors/failures/skip. Каждый
worker выполнил18 native-проб: завершённые baseline/main и частичные
baseline/main при явно указанной причине прерывания. Прерванные baseline
сохраняют исходный граф, history и реальные отсчёты; основная проба и
изменение Rs отсутствуют. В completed cases девять физических primary
файлов на топологию побайтно совпали с предыдущими uninterrupted Rs controls.
Записанные конечные окна stock-моделей по-прежнему имеют три идентифицируемых
максимума; PASS этого контракта не подтверждает обучение или классификацию.

Ещё по два cold jobs выполнены тем же новым executable. Восемь CSV/JSON/
initial/final files на каждом worker побайтно равны ранним cold controls;
сравнение повторено непосредственно с их Git-артефактами. Четыре прежних
production manifest прочитаны на каждом worker без переподписывания.

Proof commits: `a069c078b184c714e46c381e028565000e0e6774` (Elder) и
`a294f0a2b2a67c8f9676c09537c45d6d5cf6a35b` (M40 ASan). Для каждого
проверены все14 outer members, отдельный cold archive, source blobs и все
7362 исходных файла:330 retained и7032 reused из неизменяемого Git reference.
Compact native часть занимает697396B на Elder и627288B на M40; точные
контрольные суммы и состав записаны в
[NativeProbePhasesVerification.json](NativeProbePhasesVerification.json).
Для всех12 imported runs M40 подтверждён фактически загруженный libasan;
detect_leaks=0. Ни отсутствие утечек, ни полный план этим не принимаются.

Исходные математика обучения, физические профили, CapturedPerInput и допуски
не менялись. Общие import failure/rollback, остальные модели/размерности и
научная матрица остаются отдельными обязательствами плана.
