# Единый владелец native model API: проверенный перенос

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

Серверные сборки Console и интеграционного executable, native identity и
archive/port/fresh-process regressions, сравнение реальных probe fingerprints и
waveforms с предшествующим runtime и проверка единственного владельца символов
выполнены на обоих серверах. Объём адресной приёмки указан ниже; полный CTest и
ASan для механического переноса отдельно не заявляются.

Перенос не добавляет controller dispatch, полный LearnedSoloState/
RecognitionState/certificate export или mid-probe checkpoint. Незавершённая
transaction импорта storage-образов остаётся отдельным требованием этапа 5.
Ветки объединяются merge-коммитами после независимой приёмки; rebase/cherry-pick
для переноса изменений между ветками не используются.

## Адресная проверка на обоих серверах

Root 2694796a522a55d3b0b6c7b57d2c96eaf6ad0613 / PulseLib
2fc96a00fa3c9eb14317933bd7cafbdf5ebf1211 прошли изолированную серверную сборку
Console и интеграционного executable на Elder-1/Qt5 и M40/Qt6.
19 адресных cases дали 18 pass и один штатный skip fresh-process helper;
четыре parent NativeArchive controls затем явно выполнили fresh children при
2000/20000 и прошли отдельно. Численные тесты локально не запускались.

nm подтвердил по одному определению всех шести public API в PulseLib.core.
Primary CSV двух Classic/Branch native controls при 2000 и semantic model/
effective hashes совпали с прежним runtime до переноса. Результаты сохранены
в s06-model-owner-a1-linkage-and-waveform.json. Пакеты:
[Elder-1](../../../Reports/StructTrain/TimeLearner/s06-model-owner-elder1/README.md),
[M40](../../../Reports/StructTrain/TimeLearner/s06-model-owner-m40/README.md).
Они включают build logs, pre-test runtime manifests, первичные traces и данные
fresh child processes. Все 68 artifact hashes и 64 raw payload hashes проверены
локально только как данные. Измерения выполнены на серверах; source/results
переданы через Git. Последующие документальные commits не меняют исходники
относительно проверенного снимка.

PulseLib develop merge: 6480310a4ea83a444871164f0ffd787a99a66385, опубликован
до согласования корневого gitlink. Rdk остаётся
8846c1423ab13a24e3ebfdce786ce85b6a9fc0d6, Bin —
e78596e9639a841cd1989d73df7fe614419770ce. Source/test code относительно
2694796a522a55d3b0b6c7b57d2c96eaf6ad0613 не меняется.
