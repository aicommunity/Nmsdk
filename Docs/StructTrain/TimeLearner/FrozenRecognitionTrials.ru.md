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
порога/калибровки ещё не реализован. Положительный spike-path нового executor,
полная матрица LT-профилей, retarget, PostTune/C-trim и independent scientific
evaluation не объявляются закрытыми адресным контролем молчаливой модели.

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
задан в storage до Train; live-подмена в frozen Test не применяется. Проход
запущен на обоих workers; его результат пока не подтверждён. Следующий
independent gate требует четыре пакета, спайки у двух low-threshold моделей,
согласованные первичные histories и ноль skips; полноту пакетов нельзя
достраивать из предыдущего silent-only прохода.
