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

Повторный normal прогон source5c202d61c6312521a7472a86491145164808da33
завершён: hot8/8, loaded32/32, regression21/21 без skipped, затем loaded
reader16/16 на текущих данных. Все8 warm CSV побайтово равны исходному
baseline; все32 loaded CSV равны принятому normal a4. Это подтверждает
локализацию исправления на публикации состояния после Reset. Точные данные,
runtime/process и equivalence records сохранены commit
932c90c396b61162ab56cd7f205924afbdd2e50a:352 члена primary archive,
415664 bytes. После получения через Git проверены все outer/member hashes.

Prerequisite подэтап loaded graph/MDMatrix принят в root develop
970fde1a0b13cf4d29b1c19659d423dd9899ebfe с Pulsee51c702/Rdk78e51a9b.
Pulse hot feature объединила этот develop через --no-ff:
04b234b693b0e4eaaadaf611550deb5d465d4a31 имеет точно тот же Git tree,
что проверенный6cfcca0c. Это изменение ancestry, не новая версия алгоритма.
ASan hot8/loaded32/reg21 выполняется на M40 отдельным runtime a1.
Там же строятся рисунки всех16 warm case/soma pairs из Git-restored normal
primary; визуальная приёмка ещё не выполнена. Root hot feature не принята
в develop, полные stages4/11 и цель0–12 остаются открытыми.
