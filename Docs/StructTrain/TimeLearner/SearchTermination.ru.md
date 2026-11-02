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


Исправленный baseline91a9524b5 на M40:7 tests, четыре ожидаемых failures
и три controls passed. Реализованная Pulse feature
`63fd7a9fecbc567fb8e5c690ae58fc73a896de65` различает sweep/probe/edit/epoch/
adapter limits и передаёт Reason через native service в существующие
summary/stopped-package поля. FinalVerification rejection не подменяется
старой search rejection. Exact на последнем sweep сохраняется.

В pure session свежий negative certificate остаётся измерительным свидетельством.
Native service при BudgetExhausted сохраняет модель, references, final/observed
packets в штатном diagnostic stopped state, без completed-Train сертификата.
Import должен сохранять outcome/reason/graph; ConvertNativeSoloToRecognition
не должен автоматически принимать такой stopped package. Отдельный diagnostic
Test path остаётся обязательным открытым пунктом плана, а не скрытым обходом.

Подготовлено46 cases:33 прежних controller tests (у девяти reviewed ожиданий
max-sweep сменён терминальный статус),9 termination checks и4 настоящих native
Classic/Branch×N0/N1 budget/export/import controls. Native controls фиксируют
законную исходную геометрию и Rs/Ns, sync tolerance0 только как контролируемое
условие несинхронности,8 полных observations на case. Это не научная оценка
при default0.02. Все32 packet/CSV и48 soma pairs подлежат строгому анализу
и полным временным отчётам. Приёмка ещё не выполнена, в develop изменений нет.
