# Состояние рефакторинга на 31.10.2026

План 0–12 остаётся активным. Полностью принят этап 0; остальные этапы имеют
незакрытые требования. Это продолжение [снимка 30.10](CurrentStatus-2026-10-30.ru.md),
а не переоценка исторических результатов по новым критериям.

## Отправная точка и незавершённая ветка

Принятый root develop: `8446ce2fc6775bb157cc4423665cba1319af228f`.
Gitlinks: PulseLib `086b04fb43bb57506558bfb6beba6250f61a6ce2`,
Bin `cbb3bf453d82f58672541ed8a42f7b5da54a5508`,
Rdk `c903b9bba4a31e604f9740ae6f6ed52a4e7de74a`.

Рабочая ветка `codex/timelearner-threshold-calibration` содержит новые native
threshold candidate/proposal API, schema-2 наблюдения фактического LTZone.Potential,
независимые Python проверки, CLI select/confirm и candidate visual reports.
Она не объединена в develop: полная normal/ASan матрица и публикация её
первичных данных ещё не приняты. Наличие API не означает готовность всего
production calibration/PostTune controller.

## Проверенные новые факты

1. Разрешённая очистка тяжёлых производных отчётов завершена в origin и 14
   корневых Git-копиях с сохранением файлов, восьми stash и резервных bundles.
   Истории сабмодулей не переписывались. Проверены изменённые trees, свежий
   recursive checkout и старые → новые root SHA.
   [Отчёт](../../../Reports/StructTrain/TimeLearner/s10-root-history-cleanup-a1/README.md).
2. В обычном native candidate gate a2 прошли 12/12 cases. Independent reader
   подтвердил derivation и primary source CSV; последующие pure-data selection
   проверки сохранили NonSeparable для исходного двухпорогового набора.
   ASan a2 не принят: два 20-кГц source setups исчерпали 600-секундный wall budget.
   Для новых transport/calibration fixtures явно объявлены 1800 секунд;
   математические допуски и production default не менялись.
3. В новом potential gate на обоих workers прошли Classic/Branch N1 при 2000 Гц.
   Независимый reader `6d9bf22fc4f32ea404abd0a6dd6abe09c795841d` воспроизвёл
   bracket из настоящих LTZone frames и исходного learned-state CSV proof.
   Предложенные пороги: Classic 0.003336969230622544, Branch 0.006293579947234118.
   Общий timing scorer подтвердил отдельные свежие reset-per-trial пробы обоих
   кандидатов. CLI reader `2528cf27d89ab1b8c0646deb2e3f79f756435aa9` реально
   выполнил select/confirm этих двух случаев на Elder. Это новый dispersed
   двухпаттерновый контроль; не историческая восьмёрка и не общая разделимость.
4. Первый 20-кГц potential gate обнаружил ошибку fixture: предел 10000 тиков
   обрывал ожидание полного растянутого foil window, оставляя executor busy.
   В `2f773b934e6285655875b024fdc6e2f6aff3efd9` ожидание вычисляется из duration
   и frequency. На момент снимка исправленный Classic 20 кГц прошёл на Elder;
   Branch и оставшиеся фазы ещё проверяются. Старый M40 a1 остановлен явно после
   подтверждения этого дефекта; SIGTERM и owned PID записаны отдельно. Его exit 1
   не является ASan finding или полным результатом матрицы. Новый ASan a2
   запущен после завершения старого задания, в отдельном runtime.
5. Candidate renderer реально построил четыре Branch N1 2000-Гц предъявления
   с наложенными actual input samples; прошли 3/3 readback проверки. Сохранены
   общий Y-scale, overview и увеличенные окна не менее восьми пикселей на tick.
   Выбранные target overview/detail просмотрены; весь 178-файловый cache этим
   просмотром не объявляется визуально принятым.
   [Компактный отчёт](../../../Reports/StructTrain/TimeLearner/s08-threshold-candidate-report-pilot-a1/README.md):
   82 primary/metadata files в архиве 342668 bytes и три выбранных PNG.

Подробности API, ограничений и CLI: [NativeThresholdCalibration](NativeThresholdCalibration.ru.md).
Python результаты `native_execution_verified=false` не заменяют native gate.
Незавершённые gates не являются PASS; их артефакты ещё должны быть опубликованы
в Git перед приёмкой и child → root merge.

Последующее уточнение 31.10: все четыре potential cases на Elder теперь прошли
при 2000/20000 Гц. Reader `6b03832182e281d6d1c7534a84ba7b300035ec75` прошёл
8/8 проверок без skips/errors/failures, включая CLI, source/proposal/candidate
links и restoration records. Для всех четырёх случаев получено `confirmed`
по полным первичным reset-per-trial данным; fixture затем восстанавливает исходную
модель, а не устанавливает native calibrated state.
[Переносимый пакет](../../../Reports/StructTrain/TimeLearner/s08-threshold-potential-normal-a3/README.md)
сохраняет 308 primary/metadata files в lossless архиве 5730080 bytes, исходные
CSV и готовые CLI descriptors. Полные legacy-фазы 16-case gate и ASan a2
проверяются отдельно. Это дополнение не завершает этап 8.

Позднее завершён и сохранён [полный normal gate](../../../Reports/StructTrain/TimeLearner/s08-threshold-full-normal-a1/README.md):
16/16 native и 29/29 independent tests, без skips/errors/failures. Отдельные 8/8
proposal/link checks частично повторяют семь тестов первого reader; это не 37
уникальных проверок. В архиве сохранены legacy primary data и неуспешные
попытки с их настоящими причинами, без переименования в PASS.

После этого baseline добавлен новый validator raw observations и native
response assessment (root ad975bbeb / PulseLib 25cf6a5). Он уже собран и прошёл
два 2000-Гц potential-контроля на Elder; 20-кГц/legacy/ASan и независимый readback
нового Core ещё выполняются. Старый normal gate не является проверкой этого
последующего изменения. Native calibrated commit/export по-прежнему открыт.

Последующий полный normal gate этого изменения завершился: root
`ad975bbeb5df18555d94329d3ee95f321921c171`, PulseLib
`25cf6a5bfadc0ee72182cb924f1d0730cf6dc71b` — 16/16 native cases;
независимый reader root `1ef44e2e6c5ce40339f9aeaa5e4426810e36844b` —
35/35 Python tests без failures/errors/skips. Проверены 64 native response
assessments, включая primary и полные наборы. Их
[переносимый Git-пакет](../../../Reports/StructTrain/TimeLearner/s08-threshold-assessment-normal-a1/README.md)
опубликован commit `de019b2b14f4b7cf6efb4e6220e1838257da0e5f`:
897 файлов в lossless архиве 8251508 bytes, с размерами и SHA256 каждого файла.
ASan этого изменения
ожидает завершения предшествующего задания, без изменения его активного runtime.

Новый signed-threshold contract (`88b48711a51dbcdb079d2386bac9d699885cb533`,
PulseLib `dd353680407e903b7dcb0b1e55dda9eacc17fcef`) пока не принят.
Попытка Elder `s08-threshold-contract-normal-a1` завершилась с 1/6 PASS:
storage aliases проверены, но четыре candidate/potential cases встретили
`unknown_threshold_candidate_algorithm`, а isolated IaF control —
незарегистрированное имя `NConstGenerator`. Причины: `auto` сохранил
`QJsonValueRef` на временный объект вместо значения; тест использовал C++ имя
вместо storage-образа. Исправления: PulseLib
`479084f4c35d61f60ef9b37eb0da246bc8dec87a`, root
`0afbf97c4ba9df4591eebe9a41fb916e02d1903e`, образ `NCGenerator`.
Повторная попытка `s08-threshold-contract-normal-a2` выполняется отдельно;
неуспешная попытка сохраняется и не считается PASS. Изолированная ASan-сборка
первого снимка выполняется в собственных source/build/runtime на диске Data M40;
она не подменяет проверку исправленного снимка.

## Остаток полного плана

| Этап | Что ещё требуется для полной приёмки |
|---|---|
| 0 | Принят; для новых этапов сохраняется --no-ff child → root workflow. |
| 1 | Закончить исторический реестр с августа и review волн аудитов; связать semantic catalog с полной runtime/mode coverage. |
| 2 | Сквозной immutable runtime настоящего experiment runner, полный переносимый scientific run bundle; адресные runtime tests уже существуют. |
| 3 | Распространить единый строгий scorer и expected-trial contracts на все активные experiment/analysis пути; закрыть весь размерный и corrupted-data контроль. |
| 4 | Полная lifecycle/storage/growth/reuse/Copy/Load и heterogeneous/profile/frequency матрица, включая ограничения multirate. |
| 5 | Полная production model transfer матрица всех режимов, calibration provenance и independent frozen Test; имеющиеся native export/import fixtures не закрывают весь этап. |
| 6 | Завершить общий controller/adapters во всех заявленных режимах и compatibility A/B; configured native API уже реализован. |
| 7 | Полная N0/N1, ambiguous/invalid, quantization, bounds и shared Branch матрица; optional C-trim и final repeatability по плану. |
| 8 | Завершить native calibration transaction/commit/rollback и final calibrated export, все PostTune modes и реальную frozen independent оценку; текущие candidate/proposal APIs являются подэтапом. |
| 9 | Полный production CLI preflight/prepare/train/export/calibrate/evaluate, job specs и завершённая миграция с удалением старых tools; calibrate select/confirm пока является анализом измерений. |
| 10 | Сквозная scheduler/lease/PID/recovery и fail-closed публикация настоящих jobs на двух workers; текущие process/publisher/ConditionSpec проверки не закрывают всю интеграцию. |
| 11 | Исторический saved-state replay, cold retrain, legacy/V2 A/B, реальные permutations/ITI/reset policies и вся матрица моделей. |
| 12 | Актуализация всех затронутых root/submodule/config/ClDesc документов и сквозная проверка единственности актуальной спецификации после миграции. |

Серия D не возобновляется автоматически. Августовские визуально подтверждённые
4/8–6/8 остаются рабочими наблюдениями исходного протокола. Научные 8/8 не
являются условием завершения рефакторинга. Изменения порога не переносят
сертификат solo Exact на новую recognition модель.
