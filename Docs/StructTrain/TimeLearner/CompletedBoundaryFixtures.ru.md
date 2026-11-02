# Положительные предпосылки тестов переноса

Восемь прежних default0.02 cold-Train fixtures остановились до downstream
assertions: maximum_sweeps_exhausted, completed certificate отсутствует.
То же воспроизведено неизменным runtime f683:112 CSV и112 packets совпали
с новой версией. Данные: f0af7f4a3629e6cf6e60fe2225c86952fd9800c7.
Эти tests не подтверждают transfer/recognition/calibration/PostTune.

Добавлен отдельный набор NativeCompletedTransportExplicitPointTwo, использующий
существующий ExactCertificateWithExplicitPointTwoTolerance fixture. Допуск0.2
явно указан в названиях suite/spec и в сохраняемой configuration/certificate.
Старые0.02 случаи, модель, протокол, алгоритм и production defaults не изменены.
Оба режима сохраняют исходный CapturedPerInput и амплитудный допуск1e-5.
Получение настоящего Exact certificate остаётся обязательной предпосылкой.

Восемь positive controls проверяют identity и historical Branch conversion,
fresh spiking recognition owner Classic/Branch, calibration grid Classic/Branch
и PostTune N0/N1. Используются прежние production import/export и scheduler
checks, включая независимый процесс, повторное преобразование, readback,
frozen model и transaction commit/rollback. Поддержка каждого конкретного пути
подтверждается только исполненными assertions, а не названием suite.

Это отдельный транспортный контроль с явно иной математической допустимостью.
Он не доказывает обучение при0.02, селективность или полноту этапов5/7/8.
Saved-state replay, cold train и изменённый протокол остаются разными опытами.
Положительная/отрицательная матрица при исходных физических профилях, частотах,
размерностях и допусках по-прежнему обязательна. Не заменять её этим набором.

Gate: Scripts/StructTrain/TimeLearner/specs/native-completed-transport-explicit-point-two-v1.json.
Перед запуском подставляются source_root и manifest неизменной server runtime.
Elder normal numerical root589c7e3086b8c32c163deb070c5294d846718bc2:
8/8 passed,704870ms. Evidencec17f7f61f11a05c7ea8992e77593528690c956c5:
467 проверенных members; все8 completed packages независимо проверены по
canonical SHA, exact=true и явным tolerances sync0.2/amp1e-5/relative0.
Контроль допускает Exact без изменения параметров, если исходная модель
проходит свою объявленную fresh verification. Он не доказывает обучение
нетривиальной морфологии или перенос каждого вида learned overlay.
M40 ASan той же постановки запланирован после завершения и публикации
предыдущих владельцев. ASan PASS этого набора ещё не заявляется.
