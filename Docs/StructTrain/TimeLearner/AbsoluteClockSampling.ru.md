# Sampling при ненулевом абсолютном времени

Full M40 `s07-domain-full-normal-a4` и Elder-1 `s07-domain-full-normal-a5`,
root 157a5301 / PulseLib e875ca5, завершились: по 430 parent cases, 22 failures.
Три Rdk groups прошли. Среди failures
configured N1, six-input Branch transport и все двадцать stopped-state controls.
Failed child XML сохранены. Этот full run не принимается и не заменяется
успешными адресными runs.

В первичном stopped CSV/JSON на absolute begin=131.677 s записаны 361 samples
с timestep 0.0005 s, но recorder добавил sample_gap и incomplete_observation.
`Observe` сравнивает `time-previous` с maximumSampleGap через roundoff allowance,
масштабированный уже вычтенным интервалом. Это теряет масштаб исходных timestamps:
ULP абсолютного времени может превышать разрешённый roundoff интервальной
проверки. Python primary auditor использует тот же ошибочный вид сравнения.
Сходный риск есть у final gate, сравнивающего end-begin с count*gap.

Ветка `stage07/absolute-clock-sampling` сначала добавляет baseline controls без
изменения production: обычная и пропущенная выборка при origins 131 и 1000000 s,
реальные Classic/Branch probes при 2000/20000 Hz. Native fixtures устанавливают
clock штатным UTimeControl до создания модели и восстанавливают прежнее время
после fixture; Reset/Calculate компонентов не меняются.

Дальнейшее исправление должно учитывать representational error абсолютных
timestamps, сохранять отказ для реально пропущенного frame и отклонять
неразрешимый timestamp scale. Оно не меняет SyncTolerance, amplitude tolerances,
физический timestep либо математическую цель. Увеличение физического допуска
и обнуление production clock перед каждой пробой не являются исправлением.

Baseline root f712e865 на обоих workers воспроизвёл 9 failures из 10 cases:
один recorder origin control и все восемь native probes. Dropped-frame control
проходит. M40 использует ASan detect_leaks=0. Рабочее исправление сохраняет
масштаб исходных absolute endpoints в sample-gap и final coverage comparisons.
При sampling period, неразличимом на фоне timestamp roundoff, specification
отклоняется; это не разрешение большого физического интервала. Production
Python auditor получает version 4 с той же границей и не пересертифицирует
старые invalid observations. Новые проверки включают реальные probes,
missing/duplicate frame и недостаточную разрешимость времени.

Failure bundles опубликованы: Elder-1
`868cdd8bb915eedc986d74be152f9fb3ffcf3851`, 2211 stored / 2209 raw hashes;
M40 `de015c16c07483efbb6b5f0dbff1fc650a48aa07`, 2207 / 2205. Все hashes проверены
локально. Полный независимый аудит всех измерений failed run не заявляется.
Сохранены child XML, полные primary traces, runtime manifests и live-process
mapped-file snapshots (26 Elder-1, 28 M40), без подмены их build-time ldd.

Рабочая комбинация: root `241db7256f0b6595b8e3d239d66d2bbd6d1a6762`, PulseLib
`d4c0cf0b4e93cb9df23a88ddf2479685748d90c8`. Идёт 52-case regression при явном
initial clock 131 s: recorder/final gate, реальные 2/20 kHz probes, 14 configured,
шесть completed-state и 20 stopped controls. Harness читает test-only
`TIMELEARNER_TEST_MODEL_TIME_US` один раз до tests; child roles наследуют это
условие. Production clock не обнуляется и per-probe timestep не меняется.

Причинная связь с августовскими экспериментами
не установлена; их визуальные 4/8–6/8 не отменяются. Этап 8 отложен до разбора
текущей full-suite регрессии.
