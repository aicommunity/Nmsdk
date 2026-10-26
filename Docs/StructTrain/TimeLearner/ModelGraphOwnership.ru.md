# Единый владелец native model API: рабочий перенос

Ветка stage06/model-owner создана от develop
aee8c2a0b64b2dcec5dbbe1d9f291ef9a8440157 отдельно от измерительных изменений
stage07/burst-assignment. Она готовит общий producer идентичности модели для
контроллера PulseLib. Server source/runtime работающих CTest не изменяется.

## Изменение размещения

ModelBoundary, ModelInspection, ModelIdentity и ModelArchive перенесены из
App/NeuroModelerConsole в Libraries/Nmsdk-PulseLib/Core/TimeLearner. Console и
интеграционные fixtures включают публичные TimeLearner/*.h и используют одну
реализацию из Nmsdk-PulseLib.core. Прежние App-файлы удалены; их .cpp больше не
собираются отдельно в Console и тестовом executable. Namespace NmsdkTools и
имена функций сохранены. Публичные функции имеют штатный RDK_LIB_TYPE export.

Для всех семи файлов статически проверено равенство содержимого после удаления
include-строк и export-аннотации RDK_LIB_TYPE, с нормализацией CRLF→LF.
[Машинная запись](ModelOwnerRelocation.json) содержит старые commit/path/blob и
хеш нормализованного текста. Это проверка исходников, не замена сборки или
численной проверки. Форматы identity/archive, canonical binary64 encoding,
native Load/Init/Reset и математический fingerprint этим commit не меняются.

## Приёмка и ограничения

Нужны серверные сборки Console и интеграционного executable, native identity и
archive/port/fresh-process regressions, сравнение реальных probe fingerprints и
waveforms с предшествующим runtime, а также проверка отсутствия второго владельца
символов. До этих результатов перенос не принят в develop.

Перенос не добавляет controller dispatch, полный LearnedSoloState/
RecognitionState/certificate export или mid-probe checkpoint. Незавершённая
transaction импорта storage-образов остаётся отдельным требованием этапа 5.
Ветки объединяются merge-коммитами после независимой приёмки; rebase/cherry-pick
для переноса изменений между ветками не используются.
