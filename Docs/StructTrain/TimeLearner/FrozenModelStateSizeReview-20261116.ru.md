# Размер frozen-модели: история обучения внутри recognition state —16 ноября2026

В actual terminal21600 candidate размер model.json317,475,838байт. Source SHA2563ff82b8774b1c8bf50bd16b67011d200659f5802bdd9b23d9bbaaa73c3df9bc8; model revision2f22a5732cff349873805d1c6ba637f262ed27792739129b85cbf5a411fa0764. Это та же завершённая [диагностическая серия7/8](FastN1FullTrainingRecognitionScientificReport-20261116.ru.md), не новый Train/Test. [Измерения и source primary refs](FrozenModelStateSizeEvidence-20261116.json).

| Раздел | Байты compact UTF-8 JSON |
|---|---:|
|Весь threshold candidate|136740081|
|source_recognition|131966804|
|source_recognition.source_solo.measurement_archive|122410018|
|neuron конечного candidate|4763375|
|neuron исходного solo|4761138|

В measurement_archive401 primary blobs. Его доля около89.5% компактного candidate. Native XML самого конечного neuron содержит2,452,465символов; class definitions и typed identity также сохранены. Размеры compact вычислены Python JSONEncoder с ensure_ascii=False, separators=(',',':'), allow_nan=False; они не подменяют production semantic hashes. Native pretty JSON и compact representation имеют разный размер при том же содержимом.

## Область вывода

Подтверждено архитектурное дублирование: recognition/threshold carrier встраивает полный source_solo вместе с большим первичным архивом. Достоверность прежних результатов этим не опровергается. Требования разделения модели и controller/history в исходном этапе5 остаются незавершёнными. Потенциальный вклад такого объёма в стоимость повторных audit/import существенен, но точная доля wall time, CPU и RSS этим опытом **не измерена**. Размер файла нельзя превращать в численный speedup или объяснение всего времени работающего replay.

Не переоткрывать уже рассмотренные отдельные дефекты [повторного summary8 encoder](RecoverySummaryExportTimeout-20261112.ru.md) и [full-hash callback test harness](LargeModelRoundtripTimingReview-20261112.ru.md). Здесь измерен состав нового конкретного persisted candidate; эти три пути имеют разные причины и проверки. Перед исправлением сверять статус прежних приёмок по актуальному коду.

## Требование к последующему завершению этапа5

Модельный payload должен содержать полную физическую модель, storage closure, learned параметры, targets/references, threshold и его происхождение, solo/recognition/conversion state. История проб и первичные трассы должны оставаться полностью доступными как проверяемые отдельные primary, с явными cryptographic bindings. Controller checkpoint —отдельный формат. Исчезновение необходимого sidecar/blob, повреждение hash, изменение storage/graph/Rs/C или потеря negative/partial observations должны запрещать приёмку. Внешнее хранение не означает ослабление проверки источника.

Для конкретной реализации сначала измерить production call graph и число повторных проверок/materializations одного archive. Затем предусмотреть версионированный reference/envelope transport и legacy read adapter; проверить реальные Classic/Branch graph/response roundtrip, storage reuse/Load, candidate/calibration/PostTune, повреждённые sidecars и boundary continuation. Cache допустим только с доказанной immutable binding/invalidation; не заменять проверку текущего mutable graph счётчиком собственных edits. Будущий эффект измерять на одинаковом полном source corpus и protocol, сохраняя все прежние waveform и mutation-detection checks.

Текущие научные задания продолжают использовать прежние принятые формат и runtime. Изменений алгоритма, допусков, исходной математической цели или назначения пика в этом read-only исследовании нет. Новая миграция формата не является условием завершения уже запущенных научных проб.
