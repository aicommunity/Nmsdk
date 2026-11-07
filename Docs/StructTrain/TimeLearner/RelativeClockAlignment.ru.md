# Сравнение относительного времени после большого model-time origin

Дефект в production replay comparator воспроизведён на actual Branch training100
состоянии. Исходная проба начиналась при model time855.486с, повторная —0с.
Число отсчётов, все input/soma значения и semantic model fingerprint совпали
точно. Но сравнение вычитало begin и применяло roundoff allowance только к
маленьким относительным разностям. Оно не учитывало масштаб исходных абсолютных
операндов. Это давало ложный single_pulse_control_waveform_changed.
[Первичная неудачная попытка](HighThresholdSinglePulseFailureVerification.json)
сохранена:2104 archive members/373 tool hashes сверены с Git;2 actual Branch
пробы завершены,2 Classic пробы не запускались. Runtime не изменился, группа
закрыта/lease released. Это не подтверждённый дефект физического model import.

## Исправление

В clock_alignment.relative_clocks_equal roundoff bound равен
32×binary64_epsilon×max(1,abs(tA),abs(beginA),abs(tB),abs(beginB)).
Сравнивается разность (tA−beginA)−(tB−beginB). Требуются конечные строго
возрастающие timestamps, одинаковое число samples и положительная одинаковая
частота stimulus profile. Если allowance достигает четверти native tick,
сравнение отклоняется как недостаточно разрешимое. Это guard точности часов,
не новый физический или синхронизационный допуск.

Helper используют exact burst replay, first-prefix comparison и paired feedback
comparison. Типы/поля результатов не изменены. Native scheduler, модель,
minimumAmplitude, SyncTolerance, амплитудные tolerances и target references не
изменяются. Общий native_evidence.equal не ослаблен. Это не глобальная приёмка
всех модулей, вычитающих абсолютное время: другие consumers требуют своего review.

## Проверка

[Пять actual-corpus regression controls](RelativeClockAlignmentVerification.json)
прошли на M40 без skips. Подтверждены исходный production failure, corrected
production comparator, прежние low replays, отказ полному/fractional tick shift,
пропуску/дублю, nonfinite и огромному неразрешимому origin. Сверены9 archive members,
437 tool hashes и20 input bindings по опубликованным high/low/original Train
архивам. Новые native пробы не выполнялись; worker group closed/lease released.

Фикс не завершает training100 study. Branch данные переанализированы, Classic
ещё надо выполнить на исходных состояниях. Не повторять уже полученные Branch
пробы только ради нового reader. Старый failed terminal остаётся failed;
исправленные читатели имеют собственный commit/evidence.
