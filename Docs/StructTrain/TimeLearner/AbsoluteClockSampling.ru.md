# Sampling при ненулевом абсолютном времени

Full M40 `s07-domain-full-normal-a4`, root 157a5301 / PulseLib e875ca5,
завершился: 430 parent cases, 22 failures. Три Rdk groups прошли. Среди failures
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

Normal baseline root f712e865 на Elder-1 воспроизвёл 9 failures из 10 cases:
один recorder origin control и все восемь native probes. Dropped-frame control
проходит. M40 ASan baseline ещё выполняется. Рабочее исправление сохраняет
масштаб исходных absolute endpoints в sample-gap и final coverage comparisons.
При sampling period, неразличимом на фоне timestamp roundoff, specification
отклоняется; это не разрешение большого физического интервала. Production
Python auditor получает version 4 с той же границей и не пересертифицирует
старые invalid observations. Новые проверки включают реальные probes,
missing/duplicate frame и недостаточную разрешимость времени.

Причинная связь с августовскими экспериментами
не установлена; их визуальные 4/8–6/8 не отменяются. Этап 8 отложен до разбора
текущей full-suite регрессии.
