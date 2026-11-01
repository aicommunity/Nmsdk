# Адресная проверка Reset прогретого learner

Следующий проверяемый контракт этапа4: явный Reset learner сбрасывает его
динамические показания до модельного rest-state до следующего Calculate,
сохраняя индивидуальные физические параметры. Rest определяется фактическим
начальным состоянием мембран, а не предположением о нулевых каналах.

Fixture `Test_PulseLib_HotReadoutReset.cpp` использует реальные storage,
Environment и штатный scheduler. Матрица: Classic/Branch, N=2/4,
2000/20000Гц, ControllerVersion1, готовый native граф0. После начального
Reset снимаются показания сом; затем выполняется50ms настоящей пачки с
записью каждого входного импульса, физического и публичного soma readout.
Повторный Reset проверяется до первого последующего тика. В обоих состояниях
сохраняются индивидуальные C=1.23nF и Rs=91MOhm, L и вектор TipRs.

Это отдельный baseline текущих PulseLib92241d3/Rdk1699d365. Пока нет
серверной проверки, наличие устаревшего публичного канала считается гипотезой.
Build/Reset/Calculate bool не используются как доказательство поведения.
Тест не проверяет hot XML checkpoint, Branch per-input peak history,
остальные физические профили или ControllerVersion2. Он не завершает этап4.

Сборку и исполнение выполнять на Elder в отдельном runtime; работающий
ASan runtime M40 и его source tree не изменять. Failing/compile-error
попытки сохранять с точной Git closure, без объявления подтверждённого
runtime-дефекта при ошибке компиляции fixture.

Первый baseline16638b7ad завершился на Elder: компиляция успешна,8/8
native cases дают отказ из-за stale SomaNeuronAmplitude после Reset.
Физические сомы при этом возвращаются к измеренному начальному rest.
Новый PulseLib6cfcca0c7970a6f9a9381c9592cfbc8ffcbdea94 публикует
физические показания в AAfterReset, после штатного сброса детей.
Branch per-input peak history и private peak/time vectors очищаются отдельно.
Тест дополнительно проверяет dendrite readout относительно начального
native Reset, отсутствие diagnostic и Branch history до/после первого тика.
Эти дополнительные assertions не входили в первый baseline и должны
проверяться новым прогоном. Прежние исходники/данные baseline сохраняются.

Production reader hot_readout_reports.py проверяет8 native условий и16
case/soma pairs, строгую схему observation, все finite samples50ms, часы,
фактическое число/интервалы входных импульсов, совпадение live physical/cache,
соответствие последнего CSV отсчёта warm snapshot, физический rest и остаток
cache после Reset. Отрицательный baseline остаётся stale_readout с process
error; process success не подставляется. Scientific verdict/certificate=null.
Для рисунков переиспользуется общий full-sample renderer с явными подписями
Physical soma/Learner readout и before Reset, без мнимого второго предъявления.

На Elder sourcee29669f45e4e9f3af390bf1aa8de5450237275a7 прошёл16/16
corruption/data tests на baseline и16/16 на fixed корпусе. Совместимость
прежнего loaded reader проверена16/16 на normal a4. Fixed C++8/8 завершился;
loaded32/regression21 ещё выполняются и не выдаются за завершённую приёмку.
Reader receipts опубликованы14f6c65b47d81684f907bd7158d4b4436ec43421,
Reports/StructTrain/TimeLearner/s04-hot-reader-normal-a1 (47700 bytes), затем
локально проверены все outer hashes. ASan, графики и final acceptance остаются
открытыми; исходные stages4/11 и полный план этим не закрыты.
