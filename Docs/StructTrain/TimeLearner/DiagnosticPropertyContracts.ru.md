# Семантика исходных диагностик learner

Code review 19 общих свойств × два класса = **38 исходных записей** PulseLib
`025d809f7b86cc79e18ddd711c6adc40e2396bf8`. Вместе с предыдущими двумя обзорами
и остальными обзорами code catalog покрывает все 211 исходных записей.
Диагностика не является независимым экспериментальным фактором;
сохранение `ptPubState` не означает сохранение всей физической динамики.

У этих полей нет setter. Наблюдатели должны учитывать topology, controller version,
revision, завершённость окна и validity. Старые trace matrices не имеют всей этой
информации. Их нулевое/default значение не является измерением нулевого отклика.

## Выходные матрицы: ptOutput | ptPubState

| Свойство | Фактический размер/смысл и обновление | Ограничения |
|---|---|---|
| DendriteNeuronAmplitude | Default (N+1)×1. Legacy row0 — сумма sampled input-membrane potentials; rows i+1 — соответствующие membranes. Classic выбирает proximal segment1 с fallback к distal; Branch — membrane точки подключения | Это текущая выборка, не гарантированно finalized peak. При отсутствующей membrane legacy loop может пропустить запись. Native-owned ACalculate выходит раньше legacy обновления; эти rows нельзя считать новым V2 observation |
| SomaNeuronAmplitude | Default (N+1)×1. Classic legacy собирает отдельные soma rows и сумму. Branch row0 — текущая shared soma, rows i+1 — MaxIterSomaAmp предыдущего/текущего измерения отдельных pulses | Branch row0 не равен сумме rows i+1. Момент выборки и время накопления различны. Native-owned путь не обновляет legacy matrices; нужен ProbeObservation/CSV с timestamps/validity |
| Output | Default N×1; фактически копирует текущую Neuron->Output, также в native-owned/native-probe paths | Смысл и размер определяет дочерний neuron. Это не spike timestamps/count, не training outcome и не classifier verdict. Frozen evaluation требует полной observation schema |
| AmpDtTrace | UpdateNormTraces: 1×N, **InitialSomaPotential−MaxIterSomaAmp**, единицы raw potential | Несмотря на имя, не временная ошибка и не относительный residual. Legacy fallback недостающего элемента — 0. Native proof использует отдельные signed amplitude/timing residuals |
| TipSynapseResistanceTrace | 1×N, зеркало публичного TipSynapseResistance, Ом | Не самостоятельный physical readback. Нужны фактические синапсы и model identity после Build; public vector может отражать входную декларацию |
| ResistanceStatusTrace | 1×N, зеркало внутреннего ResistanceStatus, числовой флаг legacy регулятора | 0 не доказывает точную нормализацию: stall/best-effort и другие ветви также снимают флаг. Нельзя использовать как training certificate |
| NoImproveResistanceTrace | 1×N, legacy NoImproveResistanceCount | Счётчик отсутствия улучшения, не вероятность/число независимых повторов. Нулевой fallback и Reset отличать от измеренной повторяемости |
| EffectiveGainTrace | 1×N, legacy EffectiveResistanceGain, безразмерный gain | Настройка регулятора/текущее служебное состояние, не наблюдаемый закон физики. Не активный параметр V2 bounded search |
| DendriteLengthTrace | 1×N, зеркало DendriteLength как double, сегменты | Classic lengths и Branch attach positions имеют разные физические смыслы. Не полный morphology graph и не доказательство сохранности connections |
| LastAbsDtTrace | 1×N, legacy DendLastAbsDt, секунды | Абсолютное значение либо unmeasured sentinel; знак потерян. Best-effort ветви могут ограничивать значение допуском. Для Exact нужны свежие измерения и signed residuals |
| StimulusIterTrace | **1×1**, CountIteration как double | Это счётчик legacy iterations, а не N trial IDs. Не заменяет фактические stimulus timestamps и число complete trials |

UpdateNormTraces вызывается legacy train/finish logic, а не автоматически каждым
native-owned тиком. Все matrices в ней задаются для произвольного N; сам факт
наличия столбца не доказывает, что каждому входу получено валидное наблюдение.

## Производные bounds и статусы: ptPubState

| Свойство | Default и владелец/обновление | Правило интерпретации |
|---|---|---|
| ResistanceMin | 1e6 Ом до derived readback; при N1 итог — max per-input minima, при N0 очищается в 0 | Общая диагностическая сводка. Управлять конкретным Rs по локальному bound; не навязывать пересечение всем входам |
| ResistanceMax | 0 до derived readback; итог — min per-input maxima; N0 — 0 | Может оказаться ниже ResistanceMin при допустимых непересекающихся локальных интервалах. Это не автоматический PhysicalInfeasible |
| ResistanceMinRatio | 0; максимальный локальный minimum Rs/Rm | Безразмерная сводка; мембранная физика конкретного входа остаётся источником Rm |
| ResistanceMinByInput | пустой vector<double>; локальные минимумы, Ом | Пересчитываются по effective membranes/integrator и применённой политике. Размер нельзя додумывать по одному CSV: legacy может исключать фиксированный anchor, native editor выдаёт свой complete readback |
| ResistanceMaxByInput | пустой vector<double>; локальные максимумы, Ом | Не заменить одним scalar из отчёта. Нужны собственные bounds каждого входа после физического изменения |
| ResistanceMinRatioByInput | пустой vector<double>; локальные minimum Rs/Rm | Согласовывать с реальной мембраной, частотой, C и conductance model; сохранённый state может устареть после Load/growth |
| TrainingPhase | Default sync=0. Classic: sync0, normalize1, done2, postTune3, failed4. Branch: sync0, normalize1, done2, calibrate3, postTune4, failed5 | Один numeric code нельзя читать без класса. Native completion зеркалит Exact в done, любой иной terminal status — в failed. Поэтому failed не различает valid unresolved/budget/external stop/invalid. Использовать typed outcome; Reset может вернуть phase sync, сохранив learned model/certificate |
| TrainingFailureReason | Default 0. Classic: Rmax1, no-linear-stability2, no-monotone-floor3, invalid-integration4. Branch: Rmax1, segment-order2, invalid-peak-no-recovery3, no-linear-stability4, no-monotone-floor5, invalid-integration6 | Не единая кросс-классовая enum. NativeModelEditFailure/NativeTrainingService::Outcome/Reason — отдельные каналы, legacy поле не является полным зеркалом V2 ошибок. 0 не гарантирует valid или Exact |

Default state не является валидным derived result. XML/Copy могут сохранить
значения, но после изменения влияющей physics/topology они требуют пересчёта.
Public lifecycle bool не использовать для замены типизированного статуса.

## Источники, проверки и оставшиеся задачи

Прочитаны в обоих learner определения/регистрация полей, ADefault/AReset,
UpdateNormTraces, ACalculate и norm/length consumers; также
NativeModelOwner/NativeModelEditor и NativeTrainingService. Сопоставлены реальные
числовые phase/failure constants, а не старые комментарии `.h`.

Runtime evidence в ModelInspection/NativeModelEdits/NativeTrainingService и
NativeLearnedState проверяет physical bounds, model revision и certificates;
это сильнее чтения старой trace matrix, но не закрывает полную watcher/connected
property matrix. Требуются проверки stale/default/NaN diagnostics, >4 inputs,
обновления в frozen/native paths, schema-aware отображения terminal statuses.
Старые trace readers нужно мигрировать на versioned primary data и typed states.

Текущий native-owned ранний return оставляет ряд legacy diagnostic fields без
обновления. Это подтверждённое чтением кода ограничение нового интерфейса;
до адресной runtime проверки оно не объявляется воспроизведённой ошибкой
исторического анализа. Новый production scorer не должен опираться на эти поля.
