# Семантика исходных свойств: нормализация и повторные измерения

Code review PulseLib `025d809f7b86cc79e18ddd711c6adc40e2396bf8` охватывает
34 исходные записи. Это legacy controls, производные состояния и некоторые
зеркала native policy. Все runtime ограничения плана сохраняются.
Публичный bool не имеет setter, если отдельно не указано обратное.

## Общие свойства

| Свойство | Тип/default/единицы | Фактический setter/consumer и lifecycle | Условия применения и проверки |
|---|---|---|---|
| NormalizationMode | int, 1; N0=0 structural, N1=1 tip Rs | Setter отвергает иные значения, а при native declaration — любое отличие от объявленного mode. N0 очищает derived resistance bounds; N1 может принять реальные tips только при полном readback и принудительно задаёт Ns=1 | Native search.normalization должен совпасть с ModelSpec. N0 и N1 имеют одинаковую CapturedPerInput цель, но разные управляющие переменные. Не требовать разных L; проверять действующий bank/updates |
| SynapseResistanceStep | double, 1e9 Ом | Legacy setter в N0 применяет candidate value к extra Exc synapses k>=2 существующих tip membranes; в N1 сразу возвращает true без физического эффекта | N1-factor no-effect. Native editor управляет bank через explicit policy и readback, не этот legacy setter. Нужны bank count/Rs, heterogeneous physics и finite/positive validation; setter её не обеспечивает |
| SynapseResistanceBase | double, 8.6e7 Ом | Setter отвергает <=0, но не NaN/Inf. Legacy baseline и fallback для загружаемых/невалидных tips; изменение само по себе не заменяет все live Rs | Native initial individual Rs принадлежат ModelSpec/storage и learned state. Нельзя объявлять uniform live replacement без effective readback. Нужны cold/load ordering/anchor/per-input controls |
| ResistanceAdjustGain | double, 0.4, безразмерный | Setter принимает 0<g<=1, NaN не отклоняется. Legacy P-regulator; EffectiveResistanceGain динамически меняется при overshoot/undershoot | Не параметр native bounded candidate search. Gain change требует реального regulator-path positive control, а не различия результатов любой пары runs |
| AttenuationGamma | double, -1 (auto); показатель на сегмент | Setter не валидирует; <=0 инициирует оценку/fallback. Legacy используется в attenuation feedforward при length edit; auto-estimator может перезаписывать | Не измеренная амплитуда и не критерий сходимости. Native measured search не подтверждает timing по gamma. Проверять valid amplitude, Ns/Rs context, конечность и реальное применение |
| AutoEstimateAttenuationGamma | bool, true | Legacy переоценивает attenuation по амплитуде при подходящей длине/валидности; ResetToUntrained может очистить auto estimate | Fixed configured gamma не обязательно остаётся fixed при true. Нужны baseline/Rs context и фактический журнал обновлений; native explicit declaration не читает это как search mode |
| CorrectAttenuationGammaForTipR | bool, false | Legacy при auto-estimation компенсирует отношение фактического TipR к SynapseResistanceBase, прежде чем считать gamma | Имеет эффект только при выполнении ветви auto-estimate. Значение true без события не является проверкой эффекта. Проверять actual Rs/Ns/amp and estimator output |
| AcceptQuantizedAmpUnderTarget | bool, false | Только legacy N0: StructuralAmpQuantizationTracker хранит соседний bracket и допускает lower count при повторных наблюдениях. Default сохраняет прежнюю строгую ветвь | Старый tracker выбирает highest safe adjacent pair; это не новая measured-distance политика. Повтор знака не доказывает repeatability. Quantized/BestEffort не Exact; N1 фактор не действует. Новая N0 repeatability/selection остаётся задачей этапа 7 |
| ResetNeuronBeforeTrainBurst | bool, false | Legacy BeginTrainingIteration выполняет native Neuron->Reset при true; false сохраняет историческую reset-only-after-edit policy | Не Reset всего learner. Native probe executor уже имеет собственный declared rest/reset protocol; legacy flag не заменяет его. Проверять actual reset events и исходное состояние; отдельные cold/continuous comparisons |
| EnableRmaxLengthEscape | bool, false | Legacy разрешает использовать L как дополнительный escape при ограничении амплитудной коррекции Rmax; ветви зависят от topology/timing и отдельных hold/cooldown guards | Не доказательство физической недостижимости при false или stall. В native search возможные L задаются bounds/candidate policy. Нужны measured overshoot/undershoot/Rmax controls и финальный residual |
| MaxSynapseToMembraneResistanceRatio | double, 1000, Rs/Rm | Setter проверяет finite и >=1, при живых N1 membranes временно применяет candidate, пересчитывает bounds и откатывает scalar при отказе. Reciprocal ratio задаёт configured minimum до stability floor | Проверять effective child C/Rm/conductance/dt, per-input domains, повторный readback после роста. Native ModelSpec.editPolicy и mirror/validate требуют согласования. Scalar rollback не объявлять полным model transaction без проверки всех затронутых значений |
| ResyncAfterNormalization | int, 0 | Legacy Classic mode>0 после norm edit помечает non-reference timing не измеренным; >=2 очищает best-effort. Branch mode1 переоткрывает затронутый/ранние inputs, mode>=2 — все, включая после structural edit | Setter отсутствует, enum/finite preflight обязателен. Mode=1 при count=0 не проверяет реально выполненный resync. Native service всегда инвалидирует затронутые measured certificates своей политикой; это поле не переключает её |
| ResyncAfterNormalizationCount | int, 0, ptPubState | Число реальных legacy resync events; Reset/cold reset очищают | Диагностический counter, не независимый фактор и не число успешных перемеров. Для эффекта режима нужны event и complete fresh observations |

Остальные общие поля таблицы — ptPubParameter. Сохраняются штатным XML/Copy,
но history поисковых проб, текущая динамика и доказательства не восстанавливаются
одними параметрами. Обычный Reset не должен подменяться cold structure reset.

## Только Classic

| Свойство | Фактический контракт | Ограничения |
|---|---|---|
| RminLengthTolFactor | double, Default kRminLengthTolFactor (4); множитель legacy timing slack у Rs bounds; <1 возвращает historical constant | Не меняет исходный SyncTolerance для нового Exact. Завершение по slack — BestEffort. Native exact certificate использует объявленные tolerances; нужна маркировка любого legacy slack |
| DisableMidbandWalkToRmin | bool, false; отключает legacy midband walk Rs→Rmin | Действует только в соответствующей N1/midband ветви. Нельзя задавать Branch case отсутствующим Classic-only параметром |
| PreferConfiguredResistanceMinFloor | bool, false; разрешает дополнительный абсолютный Rs floor при derivation | Не отменяет integrator floor/локальную физику. Native edit policy строит optional configured floor из этого поля только когда declaration ещё не заменяет политику |
| ConfiguredResistanceMin | double, 1e6 Ом; используется при включённом PreferConfiguredResistanceMinFloor | Нет собственного setter finite/positive validation. Фактор условный; при false не следует ожидать эффекта. Проверять effective per-input minima |
| FreezeTipResistanceAfterFirstSync | bool, false; N1 diagnostic control, при первом AllDendritesSynced устанавливает latch | Не freeze всей модели или threshold; legacy AllDendritesSynced не заменяет all-input measured certificate. Нужны freeze-before/after-first-sync и repeated Reset |
| TipResistanceFrozenAfterSync | bool, false, ptPubState; latch предыдущего свойства; Reset/cold reset очищают | Диагностическое состояние, не ручной training factor и не доказательство нормализации |

## Только Branch

| Свойство | Фактический контракт | Ограничения |
|---|---|---|
| UsePerInputAttenuationGamma | bool, false; legacy estimator/readback выбирает отдельную gamma для каждого pulse вместо общего scalar | Эффект требует реального auto-estimation event. При изменении общего кабеля данные должны иметь revision; native reference/final verification управляются отдельно |
| AttenuationGammaByInput | vector<double>, ptPubState; Default заполняется текущим AttenuationGamma (-1), затем auto-estimates | Сохранённая оценка, не конфигурация heterogeneous physics. Размер и контекст проверять при Reset/Load; не активный фактор |

## Проверки, источники и оставшиеся изменения

Прочитаны SetNormalizationMode/SetSynapseResistanceStep/SetSynapseResistanceBase/
SetResistanceAdjustGain/SetMaxSynapseToMembraneResistanceRatio/SetAttenuationGamma
обоих классов; AdjustResistance/length decision, auto-gamma consumers,
ShouldFreezeTipResistanceAfterFirstSync, Begin/FinishTrainingIteration и reset paths.
Сопоставлены defaults и ptParameter/ptState flags в `.h` и конструкторах.

TimeLearnerResistance tests содержат per-input bounds, no common intersection,
Rmax и freeze controls; StructuralAmpQuantization tests проверяют старый tracker,
включая highest-safe bracket. Эти tests не доказывают новую repeatability policy.
NativeModelEdits/NativeTrainingService/FinalVerification проверяют measured
model-bound путь. Полная physics/normalization/public-property matrix остаётся
открытой, как и conditional/no-op factor preflight.

Для новых экспериментов нужно хранить не только значение переключателя, но и
capability выбранного controller version, факт применения, effective model/protocol
и события. Старые отчёты сохраняют свои критерии и не переоцениваются по названию
нового свойства задним числом.
