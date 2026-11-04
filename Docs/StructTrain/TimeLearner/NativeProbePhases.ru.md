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

Проверка начата на Elder и M40 ASan в
`readbacks/s03-native-probe-phases-{normal,asan}-a1`. До terminal receipts и
независимой проверки артефактов это исправление считается реализованным,
но не принятым по runtime. Исходные математика обучения, физические профили,
CapturedPerInput и допуски не менялись. Научный verdict отсутствует.
