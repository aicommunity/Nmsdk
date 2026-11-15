# CERT2-ANCHOR-PLATEAU-001

Статус: source-подтверждённое расхождение residual codec; исправление подготовлено,
runtime/физический plateau reproducer не запускался. Это отдельный дефект old5
reader, не скрытая часть новой package6 семантики.

До исправления Python source Root `16e63b9a6b9e4f2a720808da5d15e52ebabe903d`,
`Scripts/StructTrain/TimeLearner/composite_certificate_evidence.py`, функция `audit_composite_certificate`,
вычислял arrival−anchor.plateau_end и plateau_end−anchor.arrival для всех inputs,
включая anchor N−1. При plateau это даёт ±width для самого anchor.

Native Pulse `0286336fbc5c05ce5b0d40cc1a886d2f2ebc0f63`,
`Core/TimeLearner/FinalVerification.cpp`, `FinalVerificationSession::Finish`
вычисляет interval только при i+1!=accepted.size(); anchor self residual
остаётся нулевым. Поля InputVerificationResidual инициализируют timing в0.

Две Python формулы теперь используют0 только для N−1. Для остальных inputs
signed interval, исходные допуски, plateau endpoints и exact aggregation не
изменены. Ни C++/physics, ни old5 wire/version не меняются.

Четыре server-only unit controls вызывают production certificate2 residual
auditor на явно минимальных residual DATA: широкий anchor, неизменённый
negative signed interval другого input, rehashed ложная anchor error и прежний
single-sample anchor. Они не подделывают native execution и не заменяют raw CSV
integration; принятый на call boundary archive audit в этой unit-модели задан
как предпосылка. В combined reader suite требуется также actual package5-classic
полный первичный корпус и прежние schema5 regressions. Новый actual-corpus case
добавлен к package6 corpus suite; missing corpus остаётся error.

Локально выполнены только source/AST/Git metadata проверки. Численные Python
тесты, native тесты и model runs не выполнялись; новая физическая plateau
конфигурация этим patch не вводилась.
