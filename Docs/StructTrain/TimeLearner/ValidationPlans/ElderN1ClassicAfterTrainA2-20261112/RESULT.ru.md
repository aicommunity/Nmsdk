# Исправленный N1: технически принят, обучение остановлено на измерении

1/1 production CLI case PASS, failures/errors/skips0. Outer wall1153.034s; native execution completed/0. Полный stopped package/summary и физический граф проверены. Outer/native groups закрыты, lease released, operational diagnostics clear; source/fixtures before/after неизменны.16 raw подтверждений в `completed`.

Learning outcome `invalid_observation`, reason `composite_train_assignment_missing;omission_group_closed`, certificate=null.14 search probes,4 effective edits;18 logical groups/108 native probes/388908 sampled frames. Последняя физическая структура L=[54,1,1,1], Rs=86M для всех входов,Ns=1. Это диагностическое состояние, не завершённое обучение; calibration/Test не выполнялись.

Четыре реально измеренных кандидата input0:

|L|Rs, MΩ|Ошибка времени, ms|Амплитудный остаток, model units|
|---|---:|---:|---:|
|1|86|−480|0|
|1|2.880071555|−482.5|+0.3308828438|
|2|86|−470.5|−0.0034625577|
|3|86|−461.5|−0.0053686980|

Переход к L54 предложен поиском, но измерение в объявленном окне не дало допустимого максимума закреплённого импульса. Его residual нельзя достроить из прогноза или максимума всей пачки. Остановка не доказывает PhysicalInfeasible.

[Сопоставление с M40](comparison-to-M40.json): source input job и исходный граф совпадают; все108 CSV нового холодного запуска на Elder побайтно совпали с исходным M40 запуском. Нативные JSON/package bytes не объявляются одинаковыми. Совпавшие трассы позволяют использовать [ранее построенные временные графики](../../ClassicWindowTemporal-20261111.ru.md), сохраняя раздельное provenance двух запусков. Это детерминированное воспроизведение на другом worker, не независимые случайные обучения.

[Before завершился timeout без полного пакета](../ElderN1ClassicBeforeTrainA1-20261112/RESULT.ru.md). Поэтому данный after не закрывает полное физическое A/B и не доказывает улучшение классификации. [Читаемый алгоритмический разбор](../../N1ClassicScientificOutcome-20261112.ru.md).

[Полная новая stopped model и все первичные наблюдения](../../N1AfterPrimaryPublication-20261112.ru.md) сохранены отдельно в Git:463 members,10.3MB XZ. Совпавшие CSV не используются для подмены новых controller/runtime/model package файлов прежним corpus.
