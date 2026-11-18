# Frozen DATA: отрицательная проверка Windows и границы исправления

## Проверенный снимок

Root `c736f6bbbd18821279813e2d87a57f4310d396dd`, Pulse
`5f8b281fc1d679ae7927f7ad7410d3ff675a522a`. Новый frozen DATA API и
Console/runner code впервые проверялись вместе. Исходный build имеет
returncode0/descendants_remaining; отрицательный исход сохранён. Отдельный
closed-build audit подтвердил4646 source files и62 runtime files.

Native gate247: **230 passed,9 failed,8 skipped**. Exact compiled JUnit IDs
совпали с заявленным Windows cohort. Итог gate не принят: наличие skips
не позволяет выдать PASS. Старый227/227 относится к Root03d/Pulsec54 и не
доказывает работоспособность нового формата.

[Полный отрицательный корпус](../../../Reports/StructTrain/TimeLearner/WindowsPhysicalModelData-20261118/frozen247-rejected-primary.archive.json):
392 файла,38293442 expanded bytes,5682300 compressed bytes, SHA256
`a6f1cddefe40512913550f0919c8b3c81501c89d9f1b90ad182b35cfbe087267`.
Сохранены build/audit/native jobs, оба A/B singleton jobs, все исходные
контрольные файлы,5 controls Git bundles, collector и свежая kernel closure.
Это архив первичных данных, а не подмена исходного failed gate.

## Три новых fixture failures

Файл `Tests/Integration/Libraries/Test_PulseLib_PhysicalModelData.cpp`:

1. `ClassicFrozenDataMatchesFullSourceTargetAndFoilWithoutProofAuthority`.
2. Соответствующий `BranchFrozenDataMatchesFullSourceTargetAndFoilWithoutProofAuthority`.
3. `FrozenDataRejectsSoloAndResignedThresholdMetadata`.

Первые два останавливались на отсутствии `before` observation исходного
full-source owner, ещё до сравнения DATA. Родительский model уже был Init.
По Rdk `UModule::Init` возвращается немедленно у инициализированного объекта;
повторный вызов родителя не инициализирует добавленные после него owners.
В старом успешном Roundtrip fixture target-owner инициализировался явно.
В production Console оба owner также проходят штатный Build/Init.

Исправление Root `28f748a17c9ff870790c263d563ad268c77219f1` вызывает Init
каждого нового owner и проверяет IsInit до пробы. Оно не меняет Rdk lifecycle,
физику модели, порог, допуски или алгоритм обучения. В третьем случае реальный
отказ корректен: `NmsdkTools::ModelArchiveError`, code
`calibration_model_mismatch`, путь `$.LTZone`. Fixture ошибочно ожидал
`std::invalid_argument`; теперь проверяет фактический typed error и его code.

Этот commit пока **не подтверждён runtime**. На .14 запущена отдельная сборка
a2 с тем же Pulse5f8, controls
`71be4205ae2042e7cb1cc26e6f720a67db411b25`. Source/build/runtime a1 сохранены.
[Exact Git projection и dispatch](../../../Reports/StructTrain/TimeLearner/WindowsPhysicalModelData-20261118/frozen-fixture-a2-preparation.json).
Нужны matching native fixtures, Python8 на их настоящих outputs и отдельный
Console DATA process. Сборка сама по себе не является их приёмкой.

## Шесть старых precondition failures

`NativeThresholdPotential`: Classic/Branch при2000/20000Hz;
`NativeCalibrationPersistence`: Classic/Branch при2000Hz. Все6 не получили
TrainingCertificate из исходного `CalibrationBoundaryFixture` и завершились
`maximum_sweeps_exhausted`. Исправление Init этих случаев не касается.

Отдельный fresh-process A/B одного `ClassicN1_2000` на прежнем Root03d/Pulsec54
и новом Rootc736/Pulse5f8 воспроизвёл **тождественные retained preconditions**,
включая revision
`b61c90eba0a989ebb3ed80a1cd36cf447fbee539cf85420d37e2d6656d6cbcc5`.
Поэтому для этого конкретного случая новая DATA реализация не объясняет отказ.
Остальные5 не объявляются независимо проверенными этим одним A/B.

Объявленная исходная fixture: интервалы0.01/0.08с, L=[2,1], Rs=[86,86]M,
первая эффективная C=1.41e-9, поиск input0 L2..3/Rs86..172M, одна sweep/K4,
SyncTolerance0.02с и amplitude absolute tolerance1e-5.

| Измеренный кандидат input0 | Timing residual, с | Amplitude residual |
|---|---:|---:|
|L2/Rs86M|−0.068|0|
|L2/Rs172M|−0.068|−0.0015190|
|L3/Rs86M|−0.0585|−0.000438915|
|L3/Rs172M|−0.0585|−0.00173336|

Ни одна измеренная точка не выполняет временной допуск. Отказ сертификата
правилен; это не обоснование глобальной PhysicalInfeasible. Для проверки
readout/persistence нужна явно достижимая и отдельно проверенная learning
fixture либо реальное опубликованное завершённое состояние. Запрещено
ослаблять допуски, приписывать сертификат или исключать эти6 из заявленного
полного gate ради положительного исхода. Исходный отрицательный контроль
сохраняется; изменённый input/search domain должен быть отдельной декларацией.

## Восемь пропусков и дальнейшая приёмка

`NativeCalibrationOwnership` Classic/Branch: ForeignResult, ConsumedResult,
SamePackageImport и NormalFlow. Отсутствовал требуемый опубликованный
success-grid transaction source; legacy environment
`TIMELEARNER_CALIBRATION_OWNERSHIP_SOURCE` не задан. Это дефект data prerequisite
постановки gate. Нужны реальные источники, объявленные hashes и полный
контролируемый путь доставки. Ambient environment или синтетический
TrainingCertificate не заменяют входные данные.

Новый full247 принимается только после разрешения всех9 failures и8 skips,
с сохранением исходных отрицательных результатов. Linux248, весь физический
план и Windows scientific-worker admission остаются отдельной областью.
На M40/Elder текущие научные задания выполняются на своих прежних runtime;
исправление fixtures и формат DATA не применяются к ним задним числом.

Дополнительная проверка внешнего опубликованного s08-calibration-grid-normal-a2
нашла реальные Classic/Branch success-grid transactions: по2 версии источника,
21.35/23.16MB на файл, recognition schema1. Полный архив2351604 bytes/SHA
`3ec3b4fd20ff680e53c49aa738661b62e6606e4c53f636d7bbf41b811e66f2b3`
существует и проверен. [Точные member paths и hashes](../../../Reports/StructTrain/TimeLearner/WindowsPhysicalModelData-20261118/calibration-grid-prerequisite-candidates.json).
Это кандидаты входных fixtures, не выполненные current8 tests: совместимость
старого schema1 с текущим Import ещё не проверена; две исторические версии
нельзя одновременно класть под glob, ожидающий один файл на topology.
