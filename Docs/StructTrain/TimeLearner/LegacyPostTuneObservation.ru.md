# Граница наблюдений legacy PostTune inference

Рабочая ветка `codex/timelearner-posttune-observation` продолжает этапы 3/8.
Prerequisites native calibration/transport объединены в неё через --no-ff,
но весь этап 8 и эта новая проверка ещё не приняты в develop.

## Повторная сверка старого аудита

Текущий код уже содержит SampleMetricState, проверку finite/observed/finished,
запрет выбора mid после Timeout и сброс PostTuneResult в EnterPostTunePhase.
Branch больше не записывает общий soma accumulator поверх выбранной LTZ-метрики.
Эти прежние finding нельзя повторно объявлять открытыми без воспроизведения.
Исторический POST_TRAIN_TUNING описывает свой старый снимок.

Проверяется более узкий оставшийся путь: `MaybeStartInferenceMidProbes` при
проигрывании сохранённой Test Matrix. Он создаёт новый массив PostTuneMetrics,
но не сбрасывает PostTuneResult и SampleMetricState прежнего предъявления.
Если число samples совпало, UpdatePostTuneFreeRunPeak не пересоздаёт этот массив.
Поэтому у новой попытки могут сохраниться finished/observed от старой.
Это source-level finding; runtime causal evidence ниже появляется только после
завершения адресных серверных проверок.

## Постановка воспроизведения

Root `d8e2ad16d79d1309aef88887b5e9c388539542a4`, PulseLib
`ded4b558af46bb2caa07587d1dce81cba2da7c11`; его Core совпадает с a5671e96.
Используются настоящие storage/Environment, cold native модель, DatasetMatrix
и typed soma outputs обоих learner. Test subclass открывает существующие
protected методы; копий тела production-функций в тесте нет.

`LegacyPostTuneInferenceObservation` содержит по четыре случая на топологию:

1. Предыдущий публичный Success должен стать None при начале новой попытки.
2. Предыдущие завершённые sample states не являются наблюдениями новой попытки.
3. Fault injection: после наблюдения target Dataset останавливается до foil.
   Непосещённый foil не может участвовать как измеренный ноль в выборе mid.
4. Fault injection NaN в реальный typed soma output остаётся InvalidMetrics.

Fault injection использует вызов реального tracker и реальные компоненты,
но не представляет заданный вручную soma signal физическим экспериментом.
Для этих случаев не создаются поддельные CSV или waveform-графики. Сохраняются
полные JUnit failures, source/runtime, начальный graph readback и JSON диагностика.
Полные физические free-run traces потребуются отдельно для regression acceptance.

## Ограничения

Правка границы наблюдения не меняет физику, storage-образы, математическую
цель обучения или штатный scheduler. Она не должна выполнять Calculate из
контроллера, проверять bool Build/Reset или сбрасывать весь learner между пробами.
После исправления нужна отдельная normal/ASan проверка исходного отказа,
реальные finite free-run прогоны и сохранность training target/модели.

Legacy same-matrix/sample-0 политика остаётся исторической совместимостью;
production native evaluation использует строгие label/ID/hash. Новый V2
worker по-прежнему не включает legacy PostTune автоматически. Полный
transactional PostTune controller, C-trim и обязательная matrix остаются открытыми.

## Воспроизведено на normal и ASan

Оба baseline jobs завершены: восемь cases, шесть ожидаемых failures
(PreviousResult, PreviousSamples, MissingFoil × Classic/Branch), две NaN
проверки прошли. Native return code 1 сохранён; supervisor terminal 0 означает
лишь успешную проверку ожидаемого отказа, а не восемь прошедших тестов.
При MissingFoil оба learner ошибочно дали Result=Success, threshold=0.25
и AllSamplesValid=true. На Elder 1.350 s, на M40 ASan 7.330 s; leak detection
отключён. Это causal regression текущего legacy пути, не объяснение августа.

PulseLib 39810a760103d2e5d5a5b9e6ae6575290522b20c начинает новую inference
попытку с None/Complete=false, чистыми validity и margin diagnostics; для
объявленной сохранённой матрицы создаются новые sample states нужного размера.
Скалярные допуски, модели, входной порядок и waveform scheduler не менялись.
До серверной проверки это исправление в коде. Дополнительно поставлены четыре
реальных free-run waveform cases: Classic/Branch, 2000/20000 Гц. Они сохраняют
реальные soma/stimulus CSV, выбранную метрику, sample index и финальные состояния;
не требуют научного Success и проверяют сохранность цели и индивидуальных L/Ns/R.

## Физический fixture A1 и исправление постановки

Root cb24c5e / PulseLib 39810a7: восемь fault-injection regressions на Elder
прошли, но новый physical fixture ошибочно использовал NativeTrainingOwned
construction. Такой owner штатно обходит legacy ACalculate; Classic2000
достиг лимита 20000 ticks без завершения. Это ошибка fixture, не finding
алгоритма и не ASan memory error. Оба A1 process остановлены через pidfd
после проверки descendant ancestry, executable realpath и hash runtime;
fixture-cancellation.json и частичные native logs сохранены. Полный 49-case
A1 gate не принят.

Root e3fe53408b861b49c0e0ddc6c3de9acc548a9e54 использует штатный legacy Build
с отдельными class factories для physical cases и явно проверяет отсутствие
NativeTrainingOwned. A2 сначала исполняет 12 адресных tests, без расширения
на долгие regression suites до результата этого набора. Normal/ASan jobs
выполняются отдельно; до terminal+raw audit полная приёмка не заявляется.

Новый корневой анализатор/renderer `legacy-posttune-freerun` читает только
реальные physical JSON/CSV. Он проверяет частоту, каждый tick, фактические
импульсы, сумму сом, finite/finished sample states; не создаёт ProbeEvidence,
V2 calibration proof, training certificate или model hash отсутствующего
в legacy producer. Отсутствие spike markers означает «не записано».
Масштабированные PNG/SVG/PDF строятся общим plotting.py; full interval, все
сомы, реальные inputs и 100-tick zoom сохраняются. Физическое settling-окно
этим диагностическим producer отдельно не сертифицируется.
