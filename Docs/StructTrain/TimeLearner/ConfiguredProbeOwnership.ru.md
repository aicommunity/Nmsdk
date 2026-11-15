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
independent readers87 запускаются после адресного PASS. Пока результаты этих
новых проверок отсутствуют, исправление остаётся code-only. Нужны также ASan,
согласованная closure и отдельная приёмка полной матрицы исходного плана.
Schema4/C-search не включены в эту изолированную baseline ветку.
