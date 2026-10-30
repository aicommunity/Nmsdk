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
шестивходовых controls. M40 ASan: 8/8, detect_leaks=0. Дополнение root
27068892e86095e67feb2a4bf904ca5171c090d1 сохраняет также полные reference
observations после Reset/warm restart; 31/31 прошли на каждом сервере. Root
90d11d1990221753e6b494dbf40d83964b7d0fa3 добавляет полный state summary с
конфигурацией, кандидатами, readback и численными остатками сертификата;
39/39 прошли на каждом сервере. Summary не является checkpoint/import-форматом.

Корневой модуль Scripts/StructTrain/TimeLearner/native_evidence.py проверен
на root 99cacf35326548a9f2d4f3ed2cad143497dc7a2b: 12 тестов на каждом сервере
используют реальные C++ пакеты, включая повреждение данных и перестановку
references/residuals. Проверены 56 CSV/observations и четыре свежих отрицательных
сертификата на каждом сервере: candidate↔anchor epochs/revisions, действительные
максимумы и timestamps, Raw CapturedPerInput, signed residuals и допуски.
Модуль не производит recognition/evaluation verdict. CLI отдельной пробы:

```text
python -m Scripts.StructTrain.TimeLearner.native_evidence trial.json --trace trial.csv
```

Source анализа, interpreter и hash модуля сохранены отдельно от C++ runtime.
Все попытки, включая исходный failure, опубликованы через Git:
[Elder-1](../../../Reports/StructTrain/TimeLearner/s06-native-service-elder1/README.md),
[M40](../../../Reports/StructTrain/TimeLearner/s06-native-service-m40/README.md).
ASan A2 предшествует A3 retention и A4 диагностическому encoder; их normal
проверки представлены собственными snapshots. Полный CTest или завершённая
V2 physics matrix этим набором не заявляются.
Локально проверены 1233 compressed artifact hashes и raw gzip payloads двух
Git-пакетов. Результаты численного анализа и тестов получены только на серверах.

Следующая проверка выявила дополнительный разрыв критериев в Python-аудиторе:
global whole-burst assignment не заменяет требование одного локального максимума
в isolated window старого формата. На root
036b3a072023801f0562ba306dfc8743776991f1 воспроизведён expected failure при
расширении окна до двух реальных волн. C++ такой пакет valid не выдаёт; ошибка
касалась проверки изменённых входных данных, а не ранее сохранённых сертификатов.
Auditor v2, root 7c65d7c6ffa3991c2fa77e775a5fe9aec07dedd1: 13/13 тестов на
каждом сервере, те же 56 первичных traces и четыре negative certificates остаются
согласованными. Все попытки добавлены в те же Git-пакеты. Для выбора одной
assigned wave в широком окне требуется новый явный policy/формат; старое окно
нельзя просто расширять, меняя смысл validity без версии.

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
окно или следующий ISI. Следующий подэтап
[AssignedWaveSelection](AssignedWaveSelection.ru.md) реализует явный выбор
назначенной measured wave в широком окне с сохранением isolated default.
Прогноз задержки не подтверждает существование пика. Service API по-прежнему
принимает объявленные caller окна: автоматическая длительность и ограниченный
recovery ещё не реализованы.

Первоначальный full semantic identity до/после каждого tick был узким местом:
шестивходовой Classic control при 2000 Гц занимал примерно 150 секунд wall на
1.29 секунды model time. [ModelRevisionObserver](ModelRevisionObserver.ru.md)
добавляет проверку actual typed parameters/bindings/caches на каждом тике и
полный capture на границах. Native двухвходовые A/B-пробы 2000/20000 Гц
ускорились в 6.36–8.35 раза при одинаковых stimulus/soma arrays и model hash.
Это не замена полной ревизии счётчиком собственных edits. Стоимость больших
production graphs остаётся измерить в научной матрице.
