# Classic N0: target на каждой позиции, один фиксированный порог

Статус: подготовлен к выполнению, runtime ещё не проверен и job не запущен. Последняя попытка входа через jump дала timeout; это не результат нового эксперимента.

## Научный вопрос

[Исходный опыт](../../ClassicN0ThresholdScientificReport-20261114.ru.md) дал target hit после последнего input и4/7FP. Проверить, зависят ли фактические ответы этой же frozen модели от положения паттерна в последовательности при полном native reset-per-trial. Цель не улучшать процент ответов, а отделить свойство модели от эффекта предъявления/сброса/временной фазы.

## Неизменяемые условия

- Та же actual stopped Classic N0 модель revision35d849faa2aaea5d2620f0fd59d9934c77760b7fde0dd49d3284539f69f68263, L=[45,1,1,1],Ns1,Rs86M, stock NSPNeuronGen без LTMembrane,2000Гц.
- Тот же threshold0.012765548843211696, без повторного propose/calibration, без Train, conversion identity. Новый geometry fix Pulse58c здесь не применяется.
- Матрица Bin1c1464e248f8744e858bd66df0be99e39969fd65, все8 исходных pattern hashes/labels. XML и CSV перенесены literal Git bytes. Исторические responses из CSV не становятся современными метриками.
- Для каждой пробы прежние полные2с, reset_per_trial, onset target criterion и any-response foil criterion. ITI/continuous policy не меняются; совместимость непрерывного wrapper не расширяется.
- Тот же runtime377e0ebdee7bb1fa1cc11346438a1d2102b2124f08e3054b6347400c10a4f335 и byte-identical Console. При drift отдельная декларация и новый контроль baseline; прежний manifest не переписывать.

## Дизайн и выполнение

Production phasea_matrix.trial_design(rotations=8): восемь циклических сдвигов,8 паттернов в каждом,64 реальные пробы одним Console process. Каждый pattern встречается в каждой позиции один раз. Это детерминированный order control, не8 независимых обучений и не случайные seeds.

Максимум model ticks64*(4000+4)=256256; модельное время128с плюс штатные boundary ticks. Native wall cap7200с/8GiB, controller cap10800с/8GiB, output cap12GiB, minimum free16GiB, tasks128 у native. Это ресурсный предел отдельного64-trial Test, не увеличение бюджета обучения. При timeout сохранять частичное/непотреблённое как таковое, не считать64/64.

Исполнение только через публичный diagnostic-evaluate CLI, штатные run manifest/scorer/process-policy/owned groups/reservations. Новый worker-only test_fixed_threshold_order_matrix_native.py задаёт условия и проверяет область доказательств; он не заменяет алгоритмы, scheduler или scorer тестовой копией.

## Приёмка и анализ

1. До исполнения проверить полный source audit, signed source job, source package, runtime, case/normalization/frequency/threshold. Равенство job полей кроме run_id/trials/tick budget; sample IDs, duration и reset исходной первой матрицы прежние.
2.64 complete/valid observations и64 уникальных trial IDs. Фактические stimulus timestamps должны соответствовать объявленным ISI с явно указанной допустимой квантовкой native clock до1tick; это не ослабление Train SyncTolerance.
3. Первые8 waveform samples и model_before точно равны ранее принятому candidate run. Original baseline observations копируются literal в будущий compact primary; ранний отказ сравнения не переименовывать в инвариантность порядка.
4. Frozen model до/после и исходный baseline model должны совпасть по literal SHA; source package/manifest неизменны.
5. Для каждого rotation/position публиковать реальные TP/FP/FN/TN, spike count и времена событий относительно последнего actual input, включая отрицательные значения для ранних событий. Любой ответ foil учитывается. Не требовать исходныхTP8/FP32 ради PASS: counts являются результатом, а не ожиданием теста.
6. Показывать target в каждой позиции и остальные pattern responses. Отдельные soma/input overview и LT decision views с подписанными negative reset/positive-Y деталями. Детали временной шкалы должны увеличивать реальные ответы, не пустую границу окна. Полные galleries — M40 cache; Git — compact primary, models/metrics/selected originals.
7. Нет training certificate, independent Test, утверждения об8/8 или полной приёмке этапа11. Следующие ITI/reset/physical/legacy-V2 проверки остаются отдельными.

[Literal source bindings](source-bindings.json), [declaration](fixture/declaration.json). Исходные современные и августовские измерения сохраняются отдельно.
