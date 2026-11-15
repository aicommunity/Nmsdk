# Строгий N4 cold8 preflight — M40 A2, 12.11.2026

**5/5 PASS**, failures/errors/skips отсутствуют:четыре declaration regressions и один integration test, выполнивший два реальных native preflight (Classic и Branch). [Unittest](completed/worker/validation/unittest.log), [результат](completed/worker/validation/result.json).

Python source/actor:4d9defb6dda231570a3e270af10adc73e48c0066; package fingerprint a8881bfba7fbaa62b3d09998839c02452035c7e5767a120c23229f8d95f2e33a. Native SDK8362d58f4d6576a0c8b0cc7633270976dff1df7b/Pulse1110808f4ad1f67538dadc6fe1d3f097e00c0630, ранее принятый32/32 на обоих Linux workers.

Public CLI prepare-recovery проверил исходный9JSON cold7 план/условия и сформировал cold8. Public preflight построил свежие штатные stock N4 модели, проверил effective дочернюю физику и **полное равенство исходному cold graph** каждой топологии. Сохранены N1/CapturedPerInput, исходный target,2000Hz, ген-профиль без LTMembrane, исходные индивидуальные Rs/attachments, допуски amplitude1e-5/relative0/sync0.02 и все search/time budgets. [Classic](completed/worker/native-stock-cold8/Classic-stock-cold8-N1/index.json), [Branch](completed/worker/native-stock-cold8/Branch-stock-cold8-N1/index.json).

[Controller result](completed/controller-result.json), [closure/released lease](completed/closure-and-reservation.json):whole outer group closed, lease released. Native preflight groups также закрыты. Source/tool/fixtures до и после побайтно совпадают; heartbeat_errors пуст. [Контрольные суммы сырых readbacks](completed/readback-integrity.json). NS timestamps сохранены исходными байтами, без преобразования через JavaScript Number.

A1 не дошёл до тестов:actor/source commits различались; исходный отказ сохранён отдельно. В A2 actor и source совпадают. Параметры модели этим исправлением не менялись.

**Train не запускался**, training_started=false для обеих топологий; converged certificate, recovery delivery и classification не заявляются. Принят допуск к ограниченному строгому cold Train на этой комбинации. Следующий обязательный шаг — фактические Classic/Branch N4 Train с этой конфигурацией8, раздельной оценкой execution/validity/training, экспортом конечного или честно stopped состояния; Test обученной модели разрешён только после подтверждённого переноса. Это не приёмка полной научной/режимной матрицы и не завершение этапов1–12.
