# Полные frozen recognition пробы

Рабочий подэтап этапов 3/8. Полная цель этапов 0–12 сохраняется.

`NativeRecognitionTrialExecutor` используется обоими TimeLearner после явного
`ImportNativeRecognitionState`. Это отдельная проба распознавания, без требований
наличия пика и без изменения training target. `NativeProbe` остаётся измерителем
обучения и не получает фиктивного spike-режима.

## Выполнение

1. `QueueNativeRecognitionTrial` принимает run/trial/sample IDs, label target/foil,
   ISI-вектор, его canonical hash, длительность окна, reset policy и sample budget.
   Дублирующийся trial ID, неизвестная метка/политика, неправильный hash или число
   отвергаются. Нельзя заменить recognition state, пока проба активна либо результат
   не прочитан.
2. Перед детьми learner применяет transient pattern только к DatasetMatrix через
   штатные setter/Build/Init. InputPattern, Neuron.TrainingPattern и immutable
   recognition package не меняются. Dataset управляет однократной штатной пачкой.
3. `reset_per_trial` сбрасывает физический neuron; `preserve_neuron_dynamics`
   оставляет его динамику, сбрасывая только источник для новой пачки. ITI задаётся
   реальными промежуточными native ticks, без подмены model time. Отдельного
   checkpoint динамики и продолжения посреди пробы этот API не обещает.
4. Scheduler рассчитывает детей в штатном порядке. После детей записываются время,
   stimulus, LT output, все soma potentials и исходные timestamp histories обоих
   источников событий. Истории читаются каждый тик: конечный snapshot с AvgInterval
   не считается полной историей длительного окна.
5. Проба завершается только на границе полного окна. Проверяются покрытие, реальное
   число и времена стимулов, effective model до/после, lifecycle, граф, частота,
   неизменность источника. Source останавливается, временные Delay/Advance настройки
   восстанавливаются. Финальный model hash читается после очистки источника.

Контроллер не вызывает Calculate и не перестраивает физику. Повторная conversion
не выполняется. Отмена, Reset learner и обнаруженный пропуск кадров дают неполный
невалидный результат. Закрытое окно с ошибочными наблюдениями не становится valid.
Завершение окна, validity, spike response и scientific verdict — разные сведения.

## Первая поддержанная область и ограничения

Uniform-rate дерево; один штатный deterministic burst generator; один sample /
feature; все заданные ISI неотрицательны, межимпульсные интервалы не короче pulse
length. Полное окно лежит на временной сетке и включает окончание всей пачки.
Budget ограничивает число сохранённых кадров до запуска. Требуются actual
NPulseLTZoneCommon, предусмотренные топологией soma и storage-owned physics.
Multirate, внешние источники изменяемых protocol controls, overlapping pulses и
неподдерживаемые генераторы отвергаются, а не исправляются на каждом тике.

Порог наследуется из imported recognition package и остаётся frozen. API выбора
порога/калибровки ещё не реализован. Полная матрица LT-профилей, retarget,
PostTune/C-trim и independent scientific evaluation не объявляются закрытыми
адресными fixed-threshold controls. Положительный spike-path проверен отдельно
на двух заранее объявленных low-threshold storage-профилях (A5 ниже).

## Наблюдения и анализ

`NativeRecognitionTrialJson` schema 1 содержит полное наблюдение, включая абсолютные
и относительные к реальному stimulus onset времена, count/timestamps, первичные
кадры и причину завершения. Когда onset не наблюдался, он unknown/null. Нулевой
timestamp допустим и не фильтруется. Silence при полном валидном окне допустим.

Команда:

```text
python -m Scripts.StructTrain.TimeLearner analyze trial.json --format recognition-trial --model recognition_state.json
```

Scorer проверяет строгий набор полей/схему, finite числа, сохранённый model,
pattern hash, абсолютные/относительные времена и повторно собирает события из
первичных кадров. Несовпадение истории, count и агрегата отвергается. Пакетная
проверка получает ожидаемое множество проб из job spec и не зависит от порядка
строк: дубли, пропуски и подмена sample/label запрещены. Individual CLI проверяет
согласованность одной пробы, не доказывает полноту экспериментальной матрицы,
аутентичность выполнения или научный PASS. Итоговый verdict пока null.

## Текущая проверка

A1 root be9c0b3fb остановился на compile error const UEPtr conversion в новом
обходе. Исправление af35e3a использует штатный raw-handle conversion. A2 root
d4ce24c01: по 4/4 native pass на обоих workers, M40 ASan; две fresh-owner
проверки внутри выполняют по четыре полные пробы и cancel/gap controls. A2
prototype не содержит новых первичных histories в каждом кадре и не приравнивается
к окончательной схеме аудита.

A3 root d29361696014663681cba61938b39684a8ec8d97 / PulseLib 3a64cf6:
на обоих workers 4/4 native и 11/11 independent Python/CLI pass без skips/errors;
восемь полных проб, четыре неполных контроля, 1932 сохранённых кадра. Оба source
proofs проверены общим conversion auditor (28 primary training trials). Во всех
новых пробах spike count=0 при inherited threshold=1. Публикация и полная
адресная приёмка подэтапа не завершены.

A4 root 63e8be6ac / Core 81ee217 добавляет diagnostic catch для нестандартных
исключений и два дополнительных storage-профиля с initialThreshold=0.0001.
Оба workers остановили четыре owner cases до обучения: тест ошибочно сверял
порог в legacy setup (100), до configured native Build. Это ошибка размещения
новой проверки, а не доказательство дефекта cold storage construction.
Исходные XML/logs сохраняются. Серверный readback пакетов A3 подтверждает
реальный recognition threshold=1, а не legacy setup значение 100.

A5 root 127806a34d5caa07f4d9543c465fc6a497925e3e перемещает readback после
configured native Build. Два прежних и два новых fixed-threshold профиля
проверяют именно фактический дочерний LTZone. Порог положительного контроля
задан в storage до Train; live-подмена в frozen Test не применяется. На обоих
workers завершён: по 6/6 native и 12/12 independent Python/CLI, ноль skips/errors.
Четыре пакета дают 16 полных проб и 8 invalid cancel/gap controls, 3864 первичных
кадра. Четыре actual spikes повторно собраны из исходных LT histories; обе
low-threshold модели спайкуют, обе high-threshold модели молчат. Общий auditor
проверяет четыре source proofs с 56 primary training trials и paired reference
waveforms. M40 работает под ASan с detect_leaks=0. Process и native statuses=0.

Пакеты: Elder `60a1bd6fa44be04ce8fb59f2f2813dad84373b74`, M40
`4eb082dd4ae6a5dd9c7fa4d4516ccb3b17bbce70`; разделы
Reports/StructTrain/TimeLearner/s08-frozen-trials-{elder1,m40}.
На каждом локально проверены 414 stored / 412 raw hashes; перед публикацией
повторно сверены 112 / 300 runtime path/hash records соответственно.
Сохранены все A1–A5 и оба independent gates, включая ошибки постановки A1/A4.

Scope: Classic N0 / Branch N1, 2 kHz, два fixed-threshold storage profiles для
каждой топологии. Все jobs завершены. Это приёмка full-pattern native trial API
и его data audit. Калибровка, production train/evaluate job, scientific metrics,
остальная physics/frequency/mode matrix и полный план остаются открытыми.
Отдельные Reset learner / unexpected-exception recovery сценарии ещё требуют
адресных runtime controls; наличие обработки в коде не заменяет их проверку.
