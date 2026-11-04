# Shared recognition: восемь неуспешных проверок,04.11.2026

Candidate root `4f3db1160cda9bad59974af2bff01c023832248d`, PulseLib `f6a917d395b21610f6bf6cbb0ed945e6cdee31dd` успешно собран на Elder. Все8 NativeRecognitionOwner cases действительно выполнились и завершились assertions failures; complete valid JUnit содержит точное объявленное множество8. Full133 после этого не запускался. Ни candidate core, ни общий recognition helper не объединены в develop.

Проверки требуют завершённого Train и останавливаются до основной проверки Owner APIs. Утверждение «механическое выделение сломало Owner» пока не доказано: ранее принятый133 набор не содержит ни одного из этих8 IDs. Он не был их положительной baseline. Точные reasons/residuals и возможность добиться Exact в исходном fixture требуют отдельного сравнения. Допуски, CapturedPerInput и физика для получения зелёного результата не менялись.

Есть отдельный дефект producer: terminal candidate_cpp_executed=false выводится по наличию native-result второго этапа133. Он игнорирует реально выполненный focused-result первого этапа8. Исходный terminal сохранён как primary, а derived-status-correction.json явно исправляет факт исполнения. Это диагностическая ошибка, не дополнительный тестовый результат.

[Полный primary bundle](../../../Reports/StructTrain/TimeLearner/s06-shared-recognition-negative-normal-a3/bundle.json), evidence `d2a5de9ecbfaea49c85d650fa9b3f824ecd11f55`:395 members,1 286 960 compressed bytes,SHA256 `54fadabc2ff901ca3ced7bbe6b45173bf3b52b363b3670afa2d8c623d344b2a9`. [Независимая проверка](SharedRecognitionNegativeVerification.json) подтверждает каждый member,source hashes и реальный JUnit, сохранены CSV/models/events/build diagnostics. Kernel group закрыта, global lease released. Локально выполнялись только Git/hash/archive проверки.

## Следующий адресный контроль

Очередь s06-shared-recognition-ab-a1 ждёт завершения managed coordinator A4/live A5 и минимум3GiB свободного места, до создания bounded worker. Затем без сборки запускает те же8 на принятом lifecycle SDK1eab и candidate4f с теми же fixtures/environment; сравнивает failed IDs и все CSV побайтно. Совпадающий отрицательный результат остаётся отрицательным и не подтверждает Owner APIs. После A/B идёт отдельный full133 candidate. При расхождении traces сравнение прекращается с диагностикой; успех не подставляется.

Для окончательной приёмки helper нужны действующие положительные Owner-контроли, включая fresh/non-symmetric import, N0/N1, spiking/frozen identity и cancellation. A/B отрицательных источников и зелёный иной набор не заменяют эти проверки. Более широкий общий контроллер и исходные этапы1–12 остаются частичными; научная классификация здесь не оценивалась.
