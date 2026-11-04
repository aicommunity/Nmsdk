# Automatic configured Start не должен занимать явно поставленную пробу

H11 root14e95660ff0f1a12d6e67a0cf9a425fe7955d1ce /Pulse253fe870 завершил
все209 cases:207 passed, failures только ClassicN1ConfiguredPointTwo и
BranchN0ConfiguredRepeatedPointTwo. Evidence8ee2f9b03021b65bcd4796981fea1b0fb65ba45c
сохраняет исходные данные и обе probe_budget диагностики.

В обоих случаях probe=queued, training=finished/invalid_model,
reason=training_capacitance_read_during_probe, session ещё не начиналась.
Automatic ABeforeCalculate проигнорировал явного владельца probe runner и
попытался читать/захватывать C0 в незаконный момент. Прежнее снятие Need перед
frozen evaluation не исправляло pre-Train characterization: это разные точки.

Pulse54516bcc0aa7b0437c68f818598a19788e20eb55 ждёт отсутствия владельца probe
или подтверждённой AtEditBoundary. Это включает завершение, восстановление
временного routing и чтение результата. При сохраняющемся Need следующая
штатная итерация начинает automatic Train. Пробы Queued/Running и непрочитанные
результаты не вытесняются. Lifecycle bool остаются true, физика не меняется.

Новые4 NativeConfiguredProbeOwnership cases покрывают Classic/Branch N0/N1:
полная characterization probe при поднятом Need, Idle training на всех её
samples, отсутствие преждевременного C0 capture, затем ровно штатный tick
automatic Start с реальным C0 history и явная внешняя остановка без certificate.
JSON/CSV characterization сохраняются; handoff metadata не объявляет завершённый
Train или успешную классификацию.

Адресный gate6 добавляет два исходных H11 failures. Full regression213 и
independent readers запускаются после адресного PASS. Schema4/C-search не
включены в эту изолированную baseline ветку.

## H21: same-runtime ASan replay принят по native и исправленным readers

04.11.2026 завершены213/213 native cases из30 suites, без изменения исходных
inventory/order. GTest duration26,818.657s (около7h27m). Отдельно перед полным
набором прошёл исходный проблемный ClassicN1StoppedBeforeFirstTick.
Использованы прежние runtime/executable H14 и неизменный inner child timeout
120000ms. H14 failure не удалён и не объявлен исправленным изменением кода:
H21 добавляет успешный повтор при записанном resource preflight и memory
samples; причина прежнего timeout этим не доказана.

Исходные readers87 завершились с одной прежней диагностической expectation
ошибкой `test_missing_capture_witness_is_rejected`, без errors/skip.
Этот результат остаётся failed. Отдельные исправленные readers88 из
`ab95ba64323114f9b8a3fb05cdb46527c20d452a` прошли все88, без failures/errors/skip.
Оба протокола сохранены; новый PASS не подменяет прежний.

Проверенная closure: root `5c9b92350ee48d130d954bf10bf9521251f99e4e`, Pulse
`54516bcc0aa7b0437c68f818598a19788e20eb55`, Rdk
`acc3de8d1af2480d61ddb723c3288f7e81003049`, Bin
`39d811e5e0798eecf124f32356c9fc6edbe4538a`. Это отдельный снимок: его нельзя
обозначать как запуск текущей общей develop closure.

Proof `37cc03f72cdd461f0bde508fbc466ac976081f9c`, раздел
`Reports/StructTrain/TimeLearner/s07-configured-ownership-asan-h21`.
Сохранены все первичные JSON/CSV, модели, native process/runtime provenance,
исходные и исправленные reader archives, memory samples и899 source hashes.
Независимо проверены все2155 членов основного архива, вложенные reader archives
и source blobs каждого root/child. Фактически загруженный libasan подтверждён,
detect_leaks=0; отсутствие утечек не заявляется. Основной архив4,781,460B
содержит полные необходимые primaries, без производных изображений:
[ConfiguredProbeOwnershipH21Verification.json](ConfiguredProbeOwnershipH21Verification.json).

Это runtime-подтверждение выделенного probe ownership и охваченных регрессий.
Остальные профили/режимы плана, объединённая closure с более новыми изменениями,
научная классификация и завершение исходных этапов0–12 не следуют из этого gate.
