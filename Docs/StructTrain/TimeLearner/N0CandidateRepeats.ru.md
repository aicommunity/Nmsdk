# Повторные измерения кандидатов N0

Рабочий подэтап 7 от 30.10.2026, stage07/n0-repeatability. Это исправление
управляющей логики и первичной доказательности, а не новая амплитудная цель.
CapturedPerInput, опорный вход N−1, Ns bounds, физика storage и native scheduler
не меняются. Подэтап пока не принят и не объединён в develop.

## Подтверждённый пробел исходной реализации

BoundedTrainingSession оценивал каждый кандидат одной парой anchor/input.
Сохранялся один CandidateEvidence; значения другого Ns или другой revision
не являются повторными измерениями этого кандидата. Отдельного массива
амплитуд/разброса и полной/незавершённой группы повторов не было. Наличие
независимого final gate остаётся важным, но не заменяет эту историю N0.

## Новая политика

BoundedTrainingConfig.n0CandidateRepeats задаёт 1..128. Значение 1 сохраняет
старый протокол и старую schema-1 cold configuration. Для нового протокола
с повторениями cold configuration получает schema_version=2 и обязательный
search.n0_candidate_repeats (2..128). Неправильный тип, bool/fractional/outside
bounds, поле в schema 1 и применение к N1 отвергаются до дорогого Train.
Это действующий фактор с изменением числа проб; нельзя объявлять его no-op.

Не менять автоматически старые сохранённые конфигурации и исторические
результаты. После полной приёмки production experiment spec должен явно
выбирать повторения. Поддержка политики не означает общего признания V2
рекомендуемой для всей матрицы.

```text
choose legal L/Ns candidate and apply through native adapter if needed
for each required repeat:
    measure fresh anchor in native burst protocol
    measure active input on the same unchanged revision/epoch
    validate complete observation, identity, raw potential and timing
    retain individual primary trial IDs and signed residuals
aggregate only this candidate's same-revision measurements
rank using worst measured timing/amplitude residuals
advance only when all required repeats meet original tolerances
otherwise explore next legal candidate or restore best measured candidate
perform the existing independent all-input final verification
```

Ни совпадение знака ошибок, ни среднее между overshoot/undershoot не доказывают
сходимость. Группа хранит каждый actual raw potential, min/max, полные параметры,
input index, model revision/epoch, ID каждой input и anchor пробы. Worst residual
используется для решения; первичный CandidateEvidence каждой пробы остаётся
неизменённым и сверяемым с наблюдением. Не вводятся новые автоматические 1%
или timestep tolerances; исходные допуски сохраняются.

После невалидной пробы новая последовательность повторов начинается со свежего
anchor. Уже измеренные valid samples сохраняются как incomplete group с reason,
а не выбрасываются. Budget/external stop/invalid model также сохраняют partial
history; один удачный sample не становится complete group. Расход всех anchor/
input проб учитывается существующим maximumProbes и wall/model budget.

Min/max — диагностический разброс, не доверительный интервал. Детерминированные
повторы не считаются независимыми случайными обучениями. Итоговый Exact по-прежнему
относится к конкретной модели и исходным residual tolerances независимого final
gate; это не научный PASS разделимости или доказательство устойчивости к шуму.

## Схемы и анализ

Training summary с n0CandidateRepeats>1 имеет schema_version=2, явную политику и
candidate_repeat_groups. Schema-1 summary не может содержать скрытую repeat policy.
Анализатор сверяет все индивидуальные residuals обычным production audit,
затем каждую группу с теми же primary packets: размер, уникальность ID,
anchor IDs, raw potentials, min/max, context, complete/partial status и flags.
Все candidate trials должны быть покрыты группами ровно один раз. Потерянная
группа, повторно использованный ID, иной hash/revision или усреднённая подмена
raw не дают положительной проверки.

Native primary JSON/CSV по-прежнему обязательны; один summary не является
самостоятельным измерением. Новая схема не переименовывает старые отчёты.
Export/import всех completed/stopped вариантов и checkpoint history с новой
политикой требуют отдельной проверки; пока эта часть не считается закрытой.

## Реализация и адресная проверка

Core: BoundedTraining.h/.cpp, ConfiguredNativeTraining.cpp, ProbeEvidenceJson.cpp.
Root: native_evidence.py, test_n0_repeat_evidence.py, Test_PulseLib_BoundedTraining.cpp,
Test_PulseLib_NativeModelEditor.cpp. Контроли: второй sample отвергает первый
apparently exact candidate; поиск Ns2 вместо Ns1 в Classic/Branch; Ns128 может
пройти по реальным residuals; budget до второго повтора не выдаёт certificate;
схемы и N1 no-op rejection; configured native пары обеих топологий.

A1 root `a721fe4975a09f1d8473cef5f1054a286bc7b307` / Pulse
`76eab65b530b0c67a2f6db25affaa5def69721e8`: по 34/34 native tests на обоих
workers без skips/errors. Его ранний group format ещё не содержит partial reason;
это сохранённая промежуточная версия, не финальная схема.

A2 root `42d1b58803d6b2060bd8993b60f17c0d74577d5b` / Pulse
`8682435ce8518ef71e55a2fb8ed292f634c256d0`: Elder Release и M40 ASan
(detect_leaks=0) завершили по 35/35 native и 38/38 Python/infrastructure tests
без skips/failures/errors, process status 0. На каждом worker независимо
проверены восемь summaries и все 132 primary JSON/CSV trials; repeated profiles
дают 48 trials и десять полных candidate groups. Реальные fixtures сохраняют
SearchUnresolved и отрицательный fresh final certificate. Synthetic controls
проверяют второй sample и Ns128 отдельно от научных наблюдений.

- Elder report: `5fb83ecb2f5af3c7adf833ac57aca0b3a64f7edc`.
- M40 report: `9045b211253b7ad9b17e2a0049e34faf12d55883`.

В каждом отчёте локально проверены все 686 stored / 684 raw hashes;
файлы runtime повторно хешированы после завершения. Все задания terminal;
старые формулировки о продолжающемся A1/A2 больше не актуальны.

[Полные временные графики](NativeProbeVisualReports.ru.md) опубликованы для
всех 132 trials / 198 trial–soma пар каждого worker, включая references,
search anchors/inputs и final gate. Проверяется точное множество trial IDs,
primary hashes, общий Y-scale и неизвестность spikes при record_spikes=false.
Крупные overview/zoom PNG, SVG и PDF сохраняют исходные значения и фактический
input waveform. Просмотр четырёх контрольных панелей не закрывает визуальную
приёмку всей матрицы.

После адресной проверки объединённый Python-контур прошёл по 53/53 tests на
обоих workers без skips/errors. PulseLib develop merge
`b2b670a22f849e0d0d2b6789b8242308521b1c37`, Bin merge
`cbb3bf453d82f58672541ed8a42f7b5da54a5508`, root develop merge
`fbda0476dd6d3a1e29f27545217e80f86e103b03` опубликованы. Исходники Core и
native тестов совпадают с A2; production Python совпадает с combined gate.
Fresh recursive closure отмечается отдельно в [снимке состояния](CurrentStatus-2026-10-30.ru.md).
Полная матрица N0, final repeatability, storage,
новый completed/stopped export/import и warm continuation, conversion/calibration/
PostTune и научные эксперименты остаются требованиями полного плана.
