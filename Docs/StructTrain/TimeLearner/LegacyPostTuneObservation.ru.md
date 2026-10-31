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
