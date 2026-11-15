# Совместные проверки инфраструктуры и временные графики,05.11.2026

На Elder и M40 прошли по74 проверки Python-пакета `d9363446203bdc41c762c81d47deffc835057148`. Ни одного failure/error/skip; C++ runtime и нейронная модель в этом наборе не выполнялись.

| Набор | Количество на каждом сервере | Что подтверждено |
|---|---:|---|
| condition |12| Идентичность descriptor; привязка production ConditionSpec ещё открыта |
| historical_selectivity |9| Исходные августовские CSV4/8,5/8,6/8; неизвестная полнота не достраивается |
| resource_reservations |15| Реальные Linux процессы и файловые ресурсы |
| resource_budgets |15| Ограничения и проверки ресурсов |
| publisher |17| Реальные закрытые Git-remotes, включая отказ дочернего push |
| NativeProcessPolicyTest |6| Валидация typed policy; фактический native containment этим набором не проверен |

Оба ограниченных задания закрыты, leases освобождены. Три исторических CSV извлечены побайтово из Bin `1c1464e248f8744e858bd66df0be99e39969fd65`: EXP00 baseline и EXP01 thr00130/00135. В текущем Bin thr00135 отсутствует; исходный файл доступен в истории и сохранён в архивах проверки. Старые скрипты не возвращались в рабочее дерево. Это анализ исходного наблюдения, а не новое обучение августа.

[Независимая проверка архивов, Git-blobs и границ](IntegratedMetadataAndTemporalReportsVerification.json) сверила по317 Python blobs,15 members и18 опубликованных checksums на сервер. Elder evidence `f9b4edcbe1de6d93f5a2e0ef52a4e9219c12396f`; M40 `7e0ef058f2736d7c42282be183bc7c4813e5d4c3`. Архивы:24300/24588 bytes. Объединённый исходный код остаётся candidate; приёмка данных не продвигает его алгоритмы в develop.

## Что можно посмотреть

[Галерея42 исходных графиков с проверенной читаемостью](../../../Reports/StructTrain/TimeLearner/s11-managed-coordinator-visual-a6/REVIEWED.html) содержит24 overview — каждый frozen trial×soma,12 примеров увеличенных участков и6 первых/последних training packets. [Протокол ручного просмотра всех42](../../../Reports/StructTrain/TimeLearner/s11-managed-coordinator-visual-a6/manual-review.json) привязан к SHA каждого оригинала. Все изображения1920×960, оси и легенды читаются, графики не редактировались. Orange — фактический общий вход генератора; blue — измеренный `NPulseMembrane.SumPotential` сомы; purple — реальные LT spike events. У Classic показаны обе сомы, у Branch общая сома. SI единицы потенциала пока не подтверждены; это model units.

Полный кэш на M40: `/media/user/Data/TimeLearnerRefactor/ReportsCache/managed-coordinator-normal-a6/reports`. Он содержит16 phase reports:8 Train,4 calibration,4 frozen;368 training trial–soma,120 calibration и24 frozen pairs;5752 views в PNG/SVG/PDF. Исходные samples без downsampling, в zoom не менее8 pixels/native tick. Все2238 первичных файлов после render неизменны. По4/4 data/report checks подтверждены покрытие, полнота, соответствие входных импульсов, потерянных samples нет. Ручной просмотр5752 views не заявляется. В Git сохранены только42 PNG (5784905 bytes),661 сжатый metadata member (972428 bytes) и рецепт восстановления; исходные primaries уже опубликованы в `2776bd89fb53a4c32324a445d771e75d010a30d0`. Полные cache-изображения в Git не дублируются. Evidence `4c77e75950d5feb90ac334075098df88999f4013`, renderer package `8c9ee9f6b319a06224d6ebdcdd537b88e993fc4a`.

## Как читать результат

Четыре положительных инженерных случая Classic/Branch×ModelSpec1/2 имеют TP2/FP0/FN0/TN2 каждый. Это два входа, один target и один foil, Historical Same-Matrix calibration, порядок target/foil/foil/target, reset-per-trial. ModelSpec1/2 здесь одна физика в разных версиях сериализации, не независимые повторы. Четыре остановленных Train не имеют Test. Не заявляются stock4-input/8-pattern классификация, independent evaluation, все позиции target или устойчивость к ITI. Ранние foil zoom показывают первый импульс; поздний второй виден на overview и в полной zoom-последовательности кэша. Сравнение первого/последнего training packet не означает одинаковый active input.

Кривая сомы и LT spike marker не являются записью потенциала отдельной LT-мембраны. Влияние её инерции требует отдельного matched Off/On эксперимента с одинаковой физикой и измерением соответствующего канала; по этим рисункам причинного вывода нет.

A4/A5 render завершились до построения из-за выбора Python без matplotlib; A6 явно запускает существующее plot-venv. Ошибки сохранены в metadata, модели повторно не рассчитывались. Битовая воспроизводимость SVG/PDF с изменёнными timestamps/fonts не обещается.

Открыты совместные C++/ASan/Owner и managed-runtime gates, перенос package в production, ConditionSpec wiring, вся физическая/режимная/научная матрица. Полностью принят только этап0; этапы1–12 остаются частичными.


## Уточнение source dataflow LT/Soma — 08.11.2026

[Read-only аудит Pulse88/RdkD6](LTSomaSignalSourceAudit-20261108.ru.md)
разделяет Soma.SumPotential, отдельную LTMembrane и LTZone.Potential/Output.
У NPulseLTZoneThreshold inherited Potential действительно обновляется и служит
comparator input. Flat auxiliary panel сама по себе не доказывает отсутствие
физического сигнала; missing source/read должен быть unknown/error, не zero.
LT=Off/On в штатном BuildStructure меняет также feedback destination, поэтому
это сравнение полного узла/топологии. Чистую RC-инерцию следует проверять
отдельно внутри LT=On при неизменном body profile. Прежние samples, spike markers,
engineering результаты и августовские визуальные наблюдения не переоцениваются;
новые runtime comparisons этим source audit не выполнялись.
