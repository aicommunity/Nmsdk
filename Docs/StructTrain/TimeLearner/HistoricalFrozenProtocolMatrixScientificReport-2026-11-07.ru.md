# Историческая модель: полная frozen-матрица порядка и интервала 8×2

**Во всех16 условиях сохранены6/8: TP1, FP2, FN0, TN5.** Target присутствовал
в каждой из восьми позиций при каждом из двух интервалов. Два ложных ответа
во всех условиях относятся к тем же sample IDs: `phasea-4` и `phasea-6`.
Поздних и pre-stimulus спайков не обнаружено; effective model fingerprint
сохранился. Это подтверждает устойчивость данного сохранённого исторического
результата к проверенным изменениям протокола, без улучшения разделимости.

Первичные данные и полный графический комплект всех16 условий приняты.
Построены512 temporal views для128 предъявлений: четыре вида каждого
паттерна, с фактическим входом, четырьмя сомами и native SomaSumPotential.
Пилотные128 изображений использованы по проверенным hashes;384 созданы
дополнительно без новых native расчётов.

## Модель и протокол

Одна сохранённая Phase A Classic-модель49/41/25/1, один неизменный порог0.0135.
Root `de02a3809395dd0bbd11e2ba792bfc04a51c89f3`, PulseLib
`cbf76fbe077a7003dccf72b142d7136721fa1afb`, Bin
`1c1464e248f8744e858bd66df0be99e39969fd65`.
Все native запуски выполнены на Elder при2000Hz, по40s модельного времени.
Runtime executable SHA256:
`1642857243c8235466a62c64a4a9b5e9a36b75e48e44c66e5326f3e8d6735357`.

Проверены восемь циклических сдвигов одной исторической матрицы и Dataset Delay
1.5/3.0s. Измеренный last→first gap составляет приблизительно1.511/3.011s;
фактические timestamps сохранены. Это восемь определённых порядков, не все8!
перестановок. Состав distractors и target не менялся. Новый процесс начинал
каждую матрицу с исходного сохранённого графа; внутри неё оставалась
историческая native reset policy, без добавленного Reset перед каждой пробой.

Обучение, retarget, подбор порога и изменение физического профиля отсутствуют.
Модель всех условий имеет одинаковый effective fingerprint до/после Test:
`ca025286e43839d8442e134978603f1328017b2b1b5234138878206c0e3b82f3`.
Контрольный исходный CSV побайтно совпал с историческим replay. Исходные
августовские4/8–6/8 сохраняют свой смысл; здесь отдельно проверена модель6/8.

## Результаты

|Сдвиг|Порядок sample indices|Позиция target, с нуля|Delay1.5s|Delay3.0s|
|---:|---|---:|---|---|
|0|0,1,2,3,4,5,6,7|0|6/8; TP1/FP2|6/8; TP1/FP2|
|1|1,2,3,4,5,6,7,0|7|6/8; TP1/FP2|6/8; TP1/FP2|
|2|2,3,4,5,6,7,0,1|6|6/8; TP1/FP2|6/8; TP1/FP2|
|3|3,4,5,6,7,0,1,2|5|6/8; TP1/FP2|6/8; TP1/FP2|
|4|4,5,6,7,0,1,2,3|4|6/8; TP1/FP2|6/8; TP1/FP2|
|5|5,6,7,0,1,2,3,4|3|6/8; TP1/FP2|6/8; TP1/FP2|
|6|6,7,0,1,2,3,4,5|2|6/8; TP1/FP2|6/8; TP1/FP2|
|7|7,0,1,2,3,4,5,6|1|6/8; TP1/FP2|6/8; TP1/FP2|

В каждой ячейке FN0/TN5. Идентичность counts не заменяет сравнение waveforms;
побитная эквивалентность кривых разных порядков/интервалов здесь не заявляется.
Это16 детерминированных условий одной модели, не16 независимых обучений и
не новая независимая Test-выборка. Прежний исторический критерий отделён от
проверки полноты длинных межпачечных окон: все окна покрыты, late events0.

## Доказательства и ограничения приёмки

Новые12 условий дали24 native процесса: preflight до первого импульса и
полный Test для каждого. Четыре условия пилота и их восемь процессов повторно
не исполнялись.323 файла используемых case сверены с первичными архивами
A3/A4 до и после read-only анализа. Вся группа закрыта, lease released;
ошибок heartbeat нет, metadata resource ledger не изменена.

Новый evidence commit: `657e48449626ac1caf6362ffe1d53685434f2f83`.
В Git сохранены1002 primary archive members,52316400 compressed bytes,
SHA256 `22f18e5fbf5315f7ab9ca1a3ec286e3523ece981132ca6fc489420499cce1bff`.
Архив содержит исходные модели/configs,12 наборов native traces/observations,
process/runtime/loaded-file evidence, design, контрольные hashes и ссылки на
четыре использованных прежних условия. Первичные данные не заменены одним
абсолютным серверным путём. Производные полные рисунки остаются кэшем M40.

[Независимая metadata сверка](HistoricalProtocolCompletionVerification.json)
проверила весь архив,387 tool-source hashes,24 завершённых native процесса,
624 loaded-file bindings,323 bindings прежних case, покрытие всех target
positions на каждом Delay и неизменность fingerprint. Локально проверялись
Git/hash/archive/schema metadata, без расчёта реакций или trace arithmetic.

Новые условия запускались последовательно с disk guards:64MiB на case,
128MiB на итоговый архив и обязательным свободным резервом системы1.5GiB.
После завершения на Elder подтверждено около1.77GB доступного места. Удалять
первичные записи до проверки их Git/M40 копий не требуется для приёмки.

Полный графический отчёт покрывает все128 предъявлений, с actual inputs,
четырьмя сомами и отдельно native SomaSumPotential, full/response и явно
отмеченным positive-scale companion. Пилотные128 изображений не
генерировались повторно; для остальных условий построены384 новых изображения.
Рисунки показывают общий максимум Test и реальные LT spikes раздельно;
принадлежность пиков импульсам Train ими не сертифицируется.

Остаются другие исторические состояния4/8 и5/8, новые cold retrain,
reset-per-trial, другие интервалы/порядки/состав distractors, физические
профили и полноценное сравнение legacy/V2. Полный этап11 и исходный план
рефакторинга этой матрицей не завершаются.


## Временные графики и воспроизведение полного отчёта

Полный кэш M40:
`/media/user/Data/TimeLearnerRefactor/ReportsCache/historical-protocol-matrix-temporal-a1/figures/index.html`.
Оглавление содержит128 раскрываемых предъявлений и512 ссылок на исходные
1920×1680 PNG. Шрифт≥12, прореживания нет. Для каждой пробы доступны full,
response zoom, positive_full и positive_response. Полные виды сохраняют
отрицательный feedback, а выход за positive scale явно отмечен.
Оранжевый — actual input, красный — actual LT output spike, чёрный —
глобальный максимум соответствующего канала Test, не training assignment.

Target в позиции5 при увеличенном интервале:

![Target в позиции5](../../../Reports/StructTrain/TimeLearner/s11-historical-protocol-matrix-temporal-m40-a1/selected/rotation3-gap3-phasea-0-positive_response.png)

Foil phasea-4 предъявлен первым; реальный выходной spike остаётся ложным
ответом, несмотря на позицию0:

![Foil в первой позиции](../../../Reports/StructTrain/TimeLearner/s11-historical-protocol-matrix-temporal-m40-a1/selected/rotation4-gap1.5-phasea-4-positive_response.png)

Target в позиции1 после другого паттерна:

![Target в позиции1](../../../Reports/StructTrain/TimeLearner/s11-historical-protocol-matrix-temporal-m40-a1/selected/rotation7-gap3-phasea-0-positive_response.png)

Правильно отвергнутый foil phasea-1 в позиции2:

![Отвергнутый foil в позиции2](../../../Reports/StructTrain/TimeLearner/s11-historical-protocol-matrix-temporal-m40-a1/selected/rotation7-gap3-phasea-1-positive_response.png)

Увеличенные виды не заменяют полных: все512 доступны в оглавлении. Пример
[полного отрицательного feedback](../../../Reports/StructTrain/TimeLearner/s11-historical-protocol-temporal-m40-a5/selected/original-order-gap1.5-phasea-4-full.png)
и исходные target/FP controls сохранены в [пилотном отчёте](HistoricalFrozenProtocolScientificReport-2026-11-07.ru.md).
По сходству выбранных рисунков не устанавливается побитное равенство реакций.

Temporal evidence `2d7127959c104de8e24a6064ad3da0efeb7b1cab`:
65 compact members83084B, SHA256
`36e6b09e779b14911171a2a8ea2fc98d0aacb5604286552e8de8469c3a2ff74e`.
[Независимая сверка](HistoricalProtocolMatrixTemporalVerification.json)
проверила391 tool hashes,512 manifest entries, bytes всех четырёх выбранных
PNG и byte reconstruction16 observations против hashes исходного primary
архива. Четыре новых выбранных рисунка открыты по отдельности; шесть
пилотных проверены раньше. Ручной просмотр каждого из512 не заявляется.
Физические observations не изменены, source/cache прежних результатов
не изменились, worker group закрыта/lease released.

Git содержит сжатые первичные данные, models/configs/metrics, manifests и
выбранные рисунки. Полные512 PNG остаются воспроизводимым кэшем M40.
Для воспроизведения на analysis worker восстановить новый1002-member
bundle штатным portable_primary; четыре прежних набора взять из принятых
A3/A4 primary или неизменного проверенного пилотного кэша. Новые case IDs
`rotation2`…`rotation7` ×`gap1.5/gap3` обработать historical_protocol_temporal.
Затем historical_report_index с явным списком16 папок создаёт оглавление:
первые четыре папки сохраняют имена original-order/rotated-order из пилота.
Полное соответствие condition→plot folder находится в `case-map.json`
temporal evidence. Новых Train/Test для построения отчёта не требуется.


## Удаление подтверждённых raw-дубликатов на Elder

После проверки Git archive и восстановления/анализа всех1002 members на M40
удалены только12 закрытых case cache directories нового запуска на Elder.
972 файла699653698 logical bytes перед удалением совпали по sizes/SHA256 с
первичным Git archive. Сжатый архив52316400B, старые A3/A4 controls, исходники
и runtime сохранены. Полный кэш и отчёт M40 не затронуты. Свободное место
Elder увеличилось с1717362688 до2420523008B.

Receipt `dc404bd88e484571049630137edff5e3d02d0e39` содержит точные targets,
план и результат; [независимая сверка](HistoricalRawCacheCleanupVerification.json)
сопоставляет972 записи с опубликованным archive manifest. Уникальные исходные
результаты не удалены. Повторный анализ этих12 case следует выполнять из
Git archive либо проверенного M40 restoration, а не из удалённого raw-кэша.
