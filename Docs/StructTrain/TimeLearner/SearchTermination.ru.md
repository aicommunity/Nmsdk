# Причины остановки ограниченного поиска

Открытый подэтап этапов6/7/5/12. Исходный PulseLib
`a18bf543007c52a3ac7a6fbb148a48cb2c351de3` объединяет исчерпание
maximumSweeps после OutsideTolerance и отсутствие измеренного допустимого
кандидата в SearchUnresolved. Это разные причины остановки.

Контракт исправления: Exact имеет приоритет при свежем успешном all-input
проходе, даже если использован последний разрешённый sweep. Если допуски
не выполнены и следующую итерацию запрещает maximumSweeps — BudgetExhausted
с конкретной причиной. Отсутствие measured legal candidate остаётся
SearchUnresolved. Неполные/повреждённые измерения не превращаются в эти исходы.
Не менять CapturedPerInput, ranking, выбор кандидатов, допуски и физику.

Первый commit содержит только6 новых controller tests (позднее уточнены до7), ещё без исправления.
Они используют production BoundedTrainingSession/ProbeRecorder и явно заданные
observations; это не доказательство native physics или классификации.
Четыре cases проверяют Classic/Branch × N0/N1 при maximumSweeps1/2;
три положительных контроля — Exact на последнем sweep, InvalidObservation
после missing-peak retries и SearchUnresolved при отсутствии регулируемых входов.
Сначала требуется реальный failing baseline на сервере, затем correction,
все старые affected decision tests, native controls, export/load и строгие
readers на обоих workers. Исторические результаты не переклассифицируются.

Quantized/BestEffort и прочие причины ограничений поиска остаются частью
полного плана. Данный подэтап не объявляет глобальную физическую недостижимость
и не закрывает весь этап7. Сборки — только серверные, в отдельных runtimes.


Первый ASan baseline root234f84b0d:6 tests, четыре ожидаемых budget failures
и один ошибочный fixture expectation. Missing peak не продвигает поиск
к следующему кандидату: штатно повторяет пробу до declared invalid-observation
budget, возвращая InvalidObservation. Исправлено только ожидание этого теста;
добавлен независимый N=1/no-adjustable-input control, который действительно
должен остаться SearchUnresolved при свежем OutsideTolerance.
Повторный baseline должен иметь7 tests /4 expected failures /3 controls.
