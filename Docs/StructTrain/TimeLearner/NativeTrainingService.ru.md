# Общая native-служба обучения: рабочий подэтап

Ветка stage06/native-training-service соединяет native executor, model editor и
BoundedTrainingSession внутри обоих learner. BeginNativeTraining принимает
явный NativeTrainingPlan; далее штатный scheduler вызывает компоненты, а общий
service выполняет capture → search → fresh all-input verification. Caller не
должен вручную выполнять каждое Edit/Probe. Это ещё API, не конфигурационный
dispatch ControllerVersion=2 и не завершение этапов 6/7.

Зависимость уже принята: native structural edits объединены в PulseLib develop
075320527ca6a81ee56fa645ff2351f9af3f4f2f и root develop
69337b5b0742027cdc4e96a1804211233c08f981. Свежий recursive checkout этого root
проверен на обоих серверах. Текущий service-подэтап остаётся отдельной веткой;
его код проверяется отдельно от принятого structural edit подэтапа.

BeforeTick может применить одно явное изменение на разрешённой границе либо
поставить следующую пробу. AfterTick принимает завершённое наблюдение после
native recorder. Вложенного Calculate и собственных циклов физического времени
нет. Посторонние Queue/Take/Edit во время активного service отклоняются, а
адаптер service использует принадлежащий ему executor. Изменения модели
проверяются по effective readback и физическому fingerprint.

Каждый начальный reference получается новой штатной пачкой с CapturedPerInput
raw potential, фактическими временами и physical input ownership. References
одной задачи должны иметь общий начальный model revision/epoch. Бюджеты reference
проб и повторов отделены от bounded search. Model time и steady wall time имеют
отдельные явные ограничения. Timeout/external stop не создаёт сходимость.

Reset управления сохраняет физическую модель, захваченный goal, последнюю
привязку модели и immutable certificate. Старый certificate не заменяет outcome
новой попытки: Start очищает его и выполняет новый final gate. Warm restart
проверяет точное совпадение протокола и последнего model fingerprint, сохраняя
epoch. Подмена физики между попытками требует явной новой постановки, а не
автоматического переопределения цели. Recapture references — отдельный явный
новый старт на объявленной начальной структуре; проверку cold-start спецификации
должен выполнять production runner.

Для service-owned Reset не вызываются legacy ApplyLoadedAnchorProperties и
возврат к необученной структуре. Lifecycle-изменение во время незавершённой пробы
инвалидирует попытку. Default освобождает владение и очищает goal. Постоянный
SetInputPattern является retarget и очищает references/search/certificate;
transient evaluation stimulus не должен подменять этот training setter.

CalculateMode=0 автоматически снимает Need после терминального outcome;
CalculateMode=1 сохраняет внешнее управление. Need не доказывает Exact. Отдельно
доступны NativeTrainingState, TrainingStatus, Reason, references и certificate.
Отрицательный fresh certificate содержит реальные остатки, но Exact=false.

EncodeNativeProbeEvidence сохраняет полный внутренний ProbeSpec/Observation,
prepared context, requested trial даже при остановке до подготовки, absolute
и relative timestamps, stimulus profile, окна, baseline, все пики, wave assignment,
число samples и spikes. При выключенном измерении spikes count остаётся unknown.
Неизвестность не заменяется нулём. Nonfinite числа запрещены к JSON-кодированию,
а ошибка artifact sink делает попытку невалидной. Это internal evidence format,
не recognition CSV schema и не новый независимый verdict.

Native executor теперь самостоятельно сравнивает pattern hash с canonical hash
фактической однофакторной ISI-матрицы Dataset. Совпадение только двух заявленных
строк protocol/probe недостаточно. Неудачная подготовка сохраняет requested
specification с относительным временем; она не выдаётся за наблюдённую пробу.

Первая серверная проверка root 75e7fedb6c9ae6f040143393683f4bb4c8dee13b дала
41 pass и один failure из 42 cases на каждом сервере. Все четыре автоматические
Classic/Branch × N0/N1 поиска с настоящими edits и fresh negative final gate,
Exact/warm/Reset, остановки и бюджеты прошли. Failure выявил неверную первичную
диагностику: отказ при поддельном pattern hash ошибочно назывался изменением
base revision, хотя модель ещё не была подготовлена и revision был unknown.
Следующая правка сохраняет исходную причину первой и различает unavailable
и changed revision. Она также переносит общий bounds/protocol preflight до
первых reference-проб. Root 2fd45d4424360d7834ba094f875ddeda678c1625 прошёл
65 адресных cases на обоих серверах: 11 service, 11 bounded kernel, 17 final
verification, четыре native editor, 20 прежних lifecycle invalidation и два
шестивходовых controls. M40 ASan проверяется отдельно. Дополнение root
27068892e86095e67feb2a4bf904ca5171c090d1 сохраняет также полные reference
observations после Reset/warm restart; его отдельная проверка ещё выполняется.

Exact/warm control намеренно использует фиксированную структуру и sync tolerance
0.2 с: это проверка orchestration и lifecycle, не сходимость при default 0.02 с.
Четыре отрицательных поиска используют 0.02 с и ограниченную область L=2..3;
SearchUnresolved не доказывает физическую недостижимость за её пределами.

Остаются обязательными configured dispatch/построение без legacy rebuild,
динамические Rs domains по каждому L, полные trained-state import/export,
checkpoint/export bindings, полный физический и inhibition набор, C-trim,
conversion/PostTune/calibration, runner и научная матрица. Временный API явно
отклоняет запрошенные C-trim/PostTune/calibration и UseElementDefaults=true;
поддержка этих режимов остаётся целью, а не отменяется этим ограничением.

Перед scientific matrix требуется закрыть ещё две конкретные задачи. Окна
контрольного fixture [onset,onset+0.065] нельзя переносить в production как
универсальное правило: корректная кабельная задержка может превосходить это
окно или следующий ISI. Нужна явная проверенная политика измерения assigned
whole-burst wave либо revision-bound адаптация окна с ограниченным recovery;
прогноз задержки не должен подтверждать существование пика. Текущий service API
принимает объявленные caller окна и не заявляет такого автоматического решения.

Также full semantic identity сейчас вычисляется до/после каждого native tick.
Шестивходовой Classic control при 2000 Гц занимает примерно 150 секунд wall
на 1.29 секунды model time. До большой матрицы следует измерить этот overhead
и реализовать эквивалентный typed observer параметров/связей/кэшей, сохранив
строгую проверку полной ревизии на границах. Нельзя заменять её константным
hash, округлёнными строками или недоказанным счётчиком только собственных edits.
