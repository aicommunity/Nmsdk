# Семантика исходных свойств: цель, структура и время

Code review PulseLib `025d809f7b86cc79e18ddd711c6adc40e2396bf8`:
13 общих свойств × два learner, Classic EstDelayPerSeg и Branch
InitEstDelayPerSeg/RminNoImproveMinProgress — **29 исходных записей**.
Совокупный code catalog всех 211 записей представлен в PropertyReview.json;
runtime matrix остаётся отдельной приёмкой. Исторический inventory не переписывается.

## Общая семантика Rdk и владение

Все поля таблицы имеют `ptPubParameter`; TipSynapseResistance дополнительно
`ptPubState`. Они участвуют в штатных XML/Copy, но не заменяют full model import.
Scalar и vector `UProperty::SetData` вызывают setter **до** присваивания
`v=value`. Поэтому временный SetDataDirect/resize того же свойства внутри setter
не является гарантией окончательной нормализации публичного значения.
Нужно читать effective graph после штатного Build; нельзя менять общую семантику
Rdk ради ожидаемого поведения одного learner setter.

В legacy-векторных setters сохраняются loaded snapshots и часть физических
значений применяется сразу. Native-owned пути существенно строже: принятая
ModelSpec и физический readback проверяются общим владельцем, разрешённые изменения
проходят ApplyNativeParameters на границе проб. Во время frozen Test публичное
поле параметра не является разрешением менять модель.

В V2 математическая цель/окна/бюджеты/допуски принадлежат явной
ControllerConfiguration. Legacy SyncTolerance/PeakMeasureMargin/Delay не должны
молчаливо интерпретироваться runner как действующие V2 факторы. Отсутствие
setter-исключения само по себе не подтверждает применение фактора.

## Проверенные свойства обоих learner

| Свойство | Тип, единицы, Default | Setter, Build/Reset и фактическое применение | Ограничения и необходимые проверки |
|---|---|---|---|
| Delay | double, секунды, 0.5 | Legacy SetDelay игнорирует аргумент и записывает Dataset->Delay из EffectiveDatasetDelaySec; в момент setter собственное новое значение ещё не сохранено. Setup/последующие назначения повторно вычисляют effective delay | При AutoScale=true XML floor игнорируется. EffectiveDatasetDelay=max(settle+slack, разрешённый configured floor, 1.55). Не выдавать Delay за точный ITI. Нужны readback после setup и реальные timestamps; на native V2 пробу влияет её объявленный executor protocol |
| NumInputDendrite | int, число входов, 1 | Legacy отвергает <1, делает Ready=false, запоминает прежнюю размерность/применяет loaded anchors. Native ownership запрещает изменение числа входов обычным setter | Размерность pulse sequence, banks и target должна совпадать. Classic — отдельные dendrites; Branch — attach points общего кабеля. Tests N=1/2/4/6 покрывают части; обязательны невалидные/неполные векторы, Load ordering и граф |
| MaxDendriteLength | int, сегменты, 100 | Legacy >=1; Classic может укоротить пути и перестроить отдельные membranes/links; Branch ограничивает не-opорные attach positions, задаёт общий chain и relinks. При native declaration setter принимает только объявленный maximum | Не считать глобальную границу текущей фактической длиной. Нужны max-bound recovery, heterogeneous growth/shrink и сохранение anchor/order. Прямое изменение legacy поля может иметь структурный эффект ещё в setter |
| InputPattern | matrix<double>, ISI в секундах, Default Resize(N,1) | Legacy SyncInputPatternToDataset получает candidate argument, сбрасываются iteration counters. Native проверяет N×1, конечные >=0 ISI и конечную сумму; изменённая цель отменяет пробу, инвалидирует references и выдаёт training_target_changed_requires_new_plan, затем адресно присваивает Dataset | Это training target, не transient evaluation stimulus. Новый hash должен вычисляться из фактической матрицы. Native cold declaration/protocol retarget ещё не закончен. Нужны invalid shape/NaN/Inf, changed target during probe, unchanged target и frozen hash controls |
| DendriteLength | vector<int>, сегменты; Classic все 1; Branch все 1, последний 0 до построения | Legacy setter сохраняет old vector, снимает untrained snapshot и делает Ready=false; native ownership разрешает только прежний vector. Фактические native изменения — через editor с complete readback | Branch legacy 0-anchor нельзя автоматически объявить V2 soma synapse: native storage-owned model использует разрешённые attach>=1. Нужны canonicalization/adoption и roundtrip реального графа. Resize внутри setter не гарантирует размерность нового incoming vector |
| InitialSomaPotential | vector<double>, raw soma potential в единицах модели; начальные нули | Legacy сохраняет loaded snapshot и временно дополняет нулями; finalized single-synapse peak захватывается как индивидуальная цель. Cold reset/loaded snapshot могут восстанавливать её. Native служба владеет отдельными CapturedReferences и не использует изменение этого поля как новую цель | CapturedPerInput, опорный N−1; не общая A*. Raw rest-state не обязательно нулевой. Нужны конечность, dimension, сохранение references при Reset/import и invalidation при retarget. Public XML vector не заменяет proof packets |
| NumSynapse | vector<int>, число excitatory synapses; все 1 | Legacy setter делает Ready=false, размер старого vector подгоняется; построение применяет count к дистальной membrane. N1 EnforceParametricSynapseCount требует 1. Native editor читает и зеркалит весь фактический bank | В native setter нет отдельного запрета изменения, но ValidateNativeOwner требует совпадения с effective bank; это не разрешение обходить editor. Нужны count 1/128/ошибочные, совместные Branch attachments, growth и N0 quantization |
| TipSynapseResistance | vector<double>, Ом; все SynapseResistanceBase (8.6e7 в базовом Default) | Legacy setter сохраняет loaded request, вычисляет per-input clamp и применяет к реальным tip synapses при N1. Outer UProperty затем сохраняет исходный incoming vector; последующий native Build/derived-bounds readback принципиален. Native-owned setter допускает только прежний vector; editor/import зеркалят effective values напрямую | Не сравнивать serialized request с физическим Rs до readback. Нужны per-input bounds без требования общего пересечения, short/long vectors, invalid/nonfinite, XML order, N0 bank Rs и сохранение после Build/growth. Тип ptParameter|ptState не означает controller checkpoint |
| IterationGap | double, секунды, 0.5 | Setter отвергает только value<0. Legacy EffectiveIterationGap при AutoScale=true возвращает span+settle+slack, иначе max(configured positive либо 0.5, physical). Reset использует поле также для unmeasured sentinel | NaN/Inf не отсекаются текущим legacy setter. Отрицательное значение запрещено; 0 означает fallback, не нулевой интервал. Нужны effective onset spacing/complete windows; изменённый ITI — отдельный протокол от исторического |
| AutoScaleIterationGap | bool, true, setter отсутствует | Legacy управляет использованием floors IterationGap/Delay; settle зависит от текущей длины и оценки delay/segment. Само присваивание не гарантирует немедленный Dataset readback | Не обещает точный user ITI и не отменяет 1.55 floor. В V2 расписание проб определяется protocol/executor. Нужны true/false при изменении lengths, корректное окно late response и frozen evaluation timestamps |
| SyncTolerance | double, секунды, 0.02 | Legacy setter отвергает value<0; используется signed/absolute timing decisions и gate готовности. В V2 действует search.tolerances.sync явного JSON, а не автоматическое чтение этого legacy поля | 0 разрешён; NaN/Inf setter не отсекает. Не заменять допуск на dt/1%. Проверять signed residuals, overshoot, independent all-input sweep; old best-effort latches не являются Exact |
| PeakMeasureMargin | double, секунды, 0.06 | Legacy setter отвергает value<0; задаёт margin прогнозного peak search. Native V2 использует explicit input windows и назначение burst waves | 0 разрешён; NaN/Inf не отсекаются legacy setter. Прогноз не подтверждает отсутствующий пик. Нужны missing/ambiguous/clipped/incomplete peaks и finite checks, а не только факт выставления свойства |
| DelayAgreeMarginMin | double, секунды, 0.03 | Legacy setter отвергает value<0; участвует в измерительном согласовании DelayUseOf вместе с SyncTolerance. Не равен допускаемому финальному timing residual | 0 разрешён; NaN/Inf не отсекаются legacy setter. Нужны реальные peak-vs-prediction/roundoff controls; V2 windows/tolerances задаются отдельно и должны проверяться по effective protocol |

## Различия топологий и дополнительные свойства

| Свойство | Фактический контракт | Что ещё проверять |
|---|---|---|
| Classic EstDelayPerSeg | Публичный double, секунды/сегмент, Default 0.005 (kDelayPerSegDefault). Setter отклоняет <=0, но не NaN/Inf. Legacy EMA обновляет прогноз по наблюдению; влияет на settle и предложение длины/окна | Предсказание не доказательство синхронности. В V2 bounded measured search это поле не является автоматически применённым фактором. Проверки finite, немонотонности, пропавшего пика и signed timing |
| Branch InitEstDelayPerSeg | Публичный double, секунды/сегмент, Default 0, без setter. Начальный внутренний EstDelayPerSeg при resize/reset берётся из >0 значения, иначе kDelayPerSegDefault. Сам внутренний EstDelayPerSeg не является публичным аналогом Classic property | Требовать реальное применение начальной оценки после Reset, конечность и provenance; не менять частоту или физику через estimator. Seed/init не означает независимый случайный повтор |
| Branch RminNoImproveMinProgress | Публичный double без setter, Default 0, безразмерный коэффициент. При >0 очищает no-improve streak только у Rmin, после реального length edit, при одинаковом знаке ошибки и улучшении >= k*EstDelayPerSeg*abs(applied_delta) | No-improve/BestEffort не доказывают Exact/PhysicalInfeasible. Нужны same-sign/shrinking/overshoot/zero-delta controls. Native bounded controller не использует legacy latch как сертификат |

В обоих текущих `.h` kDelayPerSegDefault=0.005 секунды/сегмент. Это default
оценщика, а не измеренная характеристика любой физической модели и не иной
публичный параметр Branch с именем EstDelayPerSeg.

## Источники и существующие проверки

Прочитаны оба `.h/.cpp`: перечисленные Set* методы, ADefault/AReset,
EffectiveDatasetDelaySec/EffectiveIterationGapSec/SettleMarginSec, finalized
reference capture и consumers timing/margin. Проверена фактическая последовательность
scalar/vector SetData в Rdk UProperty.h, а не только комментарии learner.
NativeModelBuilder.cpp содержит ValidNativeTarget/AssignNativeTarget;
NativeModelOwner.h — Mirror/Validate; ConfiguredNativeTraining.cpp — явные окна,
timing tolerance, pattern hash и budget.

Имеющиеся production fixtures: NativeModelBuilder.*, NativeLearnedState.*,
NativeTrainingService.ExactAutoCompletionResetWarmRestartAndRetarget,
DeclaredPatternHashMustMatchTheActualNativeDataset; TimeLearnerResistanceTest
проверяет stale serialized minimum и per-input physical bounds; native probe и
assigned-wave tests проверяют измеренные окна. Прямой вызов отрицательного Set*
в старом тесте не доказывает полную XML/connected-property семантику.

Открытые code findings: incomplete finite validation legacy setters; setter-time
vs effective readback; несогласованный retarget конфигурации V2; возможность
молчаливого использования неактивного legacy поля как фактора V2. Пока нет
адресного runtime reproducer, эти пункты не объявляются воспроизведёнными сбоями.
