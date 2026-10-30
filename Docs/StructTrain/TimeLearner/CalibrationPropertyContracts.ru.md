# Семантика исходных свойств: порог, PostTune и калибровка

Code review **44 исходных записей** (22 × оба класса), PulseLib
`025d809f7b86cc79e18ddd711c6adc40e2396bf8`. Это описание текущего legacy-кода,
а не объявление реализации нового этапа 8. Native V2 пока явно отклоняет
включённые PostTune и AutoCalibrate; completed-state codec сохраняет только
фактический fixed threshold, не calibrated/PostTune controller checkpoint.

## Порог и training-only калибровка

| Свойство | Default, тип/единицы | Фактическое применение/setter | Ограничения и проверки |
|---|---|---|---|
| LTZThreshold | double, 100; единицы потенциала LTZone | Setter ищет текущую Neuron.LTZone, пишет Threshold; если отличие от Fixed>1e-6, снимает UseFixed. При отсутствии child возвращает true без физического применения. Build/Reset ApplyActiveLtzThreshold выбирает training/fixed по Need | Значение parent не заменяет effective child readback. Не переносить threshold через неполный XML overlay; hash конечной модели обязан включать реальный порог |
| TrainingLTZThreshold | double, 100 | Setter только принимает значение. Legacy используется для подавления ранних spikes при Train и при некоторых calibration/probe phases; переключается через ApplyActiveLtzThreshold/SetIsNeedToTrain | Это изменённая физика LTZ dynamics, не просто offline decision level. Native model определяется storage/ModelSpec; legacy knob не подтверждает effective V2 threshold |
| FixedLTZThreshold | double, 0.0115 | Setter не применяет автоматически; затем используется при recognition/Need=false/UseFixed и может изменяться калибровкой | Изменение после подбора требует реального прогона с выбранным порогом. Не объявлять frozen Test при изменяемом Fixed |
| UseFixedLTZThreshold | bool, false | Setter true пишет текущий Fixed в LTZone и LTZThreshold; false само по себе не применяет Training threshold. Дополнительно меняется SetLTZThreshold/калибровкой | Проверять threshold readback после Load/Reset и команды Need; имя флага не описывает полностью effective state |
| AutoCalibrateFixedLTZThreshold | bool, false | Setter stub. Legacy после синхронизации вычисляет threshold по LastSyncedMin/MaxLTZ; при max<=min+1e-9 пропускает обновление | Эта target-only процедура не доказывает разделимость target/foils и не заменяет independent calibration. V2 включение запрещено до реализации нового протокола |
| CalibrateLTZThresholdMode | int; Classic 0 gap_fraction, Branch 1 peak_fraction | Setter не валидирует enum. Mode==1: max*f; любой другой код попадает в min+f*(max−min) | Нужны preflight enum checks. Default топологий различается, поэтому нельзя считать одинаковый отсутствующий XML field одинаковым протоколом |
| CalibrateLTZThresholdFraction | double; Classic 0.85, Branch 0.99; безразмерный | Setter stub, используется формулами выше | Нужны finite/range checks и сохранение фактически использованных min/max/data identity. Setter сам их не даёт |
| CalibrateLTZThresholdMin | double, 0.0115; LTZ potential units | Setter stub; lower clamp вычисленного threshold | Проверять finite и согласованность min<=max; clamp не исправляет повреждённые исходные измерения |
| CalibrateLTZThresholdMax | double; Classic 0.05, Branch 1.0 | Setter stub; upper clamp | Те же проверки; разные defaults должны входить в ConditionSpec и provenance |
| CalibratedFixedLTZThreshold | double, 0, ptPubState | Результат авто-калибровки или PostTune finalization; записывается вместе с Fixed | Нулевой default не означает проведённую неуспешную калибровку. Это scalar diagnostic, не CalibrationResult с доказательствами |

Все поля выше, кроме CalibratedFixedLTZThreshold, — ptPubParameter. Сохраняются
XML/Copy. Все числовые threshold/calibration setters сейчас не дают полного
finite/range validation. Native training ошибки идут через typed states, не bool.

## PostTune controls и результаты

| Свойство | Тип/default | Фактическая логика | Ограничения и обязательные controls |
|---|---|---|---|
| EnablePostTrainTuning | bool, **true** | Legacy EndOfLearning переводит в PostTune; native configured/BeginNativeTraining включение отвергают | Поэтому default legacy configuration не является готовым V2 config. Явное Off — базовый обязательный протокол, не ошибка постановки |
| PostTrainTipResistanceMode | int, 1 CanonRmin | 0 Off, 1 CanonRmin, 2 FlatLastR, 3 KeepDone, 4 SearchSynthetic. ApplyPostTrainTipMode выбирает snapshot/canonical/flat/trial tips; неизвестный mode может попасть в canonical fallback | Setter отсутствует; preflight должен отвергать неизвестный enum. Нужны все commit/rollback/interruption controls и post-transform model identity |
| EnablePostTrainMidThreshold | bool, true | Разрешает mid computation и inference free-run probes совместно с EnablePostTrainTuning; участвует также в Dataset hold/release | Это отдельная изменяющая порог стадия, не passive analysis. Frozen Test должен отключить автоматическое доподбирание |
| PostTrainMidMetric | int, 0 Auto | 1 LTZ, 2 Soma. Auto Classic читает LTZ peak; Auto Branch использует shared-soma-related peak path. Branch ReadPostTuneProbeMetric берёт также max с per-input MaxIterSomaAmp; live metric берёт shared soma | Нельзя сравнивать Auto разных классов как одну величину. Нужно определить единственную измерительную процедуру и проверить тип наблюдений, а не полагаться на имя soma_amp_sum |
| TipResistanceCanonFloor | double, 2e7 Ом | Canonical vector floor/ранние tips; итоговые Rs ещё ограничиваются фактическими bounds через setters | Номинальный floor не равен фактическому после clipping. Нужны индивидуальные значения всех синапсов, включая anchor |
| TipResistanceCanonLast | double, 8.6e7 Ом | Last tip в canonical и scalar для FlatLastR | Изменение влияет только при выбранном mode. Нужны actual Rs, conversion order и clipping provenance |
| PostTrainSilentThreshold | double, 1.0; LTZ units | Порог silent probes и fallback при nonseparable/invalid/setup failures | Молчание всех patterns не является хорошим detection result. Отсутствие spikes должно оцениваться как target miss, даже если семь foils молчат |
| UseCandidateMidOnNonSeparableTest | bool, false | Legacy inference helper при включении может подставить finite candidate_mid в (0,1), сохранив nonseparable/result status; Train этим helper не меняется | Это **Test-time tuning**, не frozen independent evaluation. Допустим только явно маркированный historical protocol. NonSeparable не превращается в PASS |
| PostTrainSyntheticFoilCount | int, 8 | Ограничивает набор synthetic/recognition probe patterns, создаваемых BuildSyntheticPatterns/BuildRecognitionProbePatterns | Различать фактический набор и requested cap; сохранить IDs/hash каждого pattern. Такой набор не равен любой исторической восьмёрке |
| PostTrainTipSearchIters | int, 12 | SearchSynthetic budget; consumer использует max(1,configured) | Ноль/отрицательное значение не выключает search в legacy. Нужны явные positive budget и честный budget-exhausted outcome |
| PostTrainTuneComplete | bool, false, ptPubState | Флаг окончания legacy PostTune; сбрасывается start/reset paths | Complete означает завершение процедуры, не valid/Exact/calibrated/PASS. Не восстанавливает поисковую транзакцию после Load |
| PostTuneResult | int, kResultNone=0, ptPubState | NNeuronPostTrainTune.h: success1, nonseparable2, setup_failure3, timeout4, invalid_metrics5, best_effort6, reverted_keep_done7 | Читать вместе с фактическим порогом/graph и protocol. Success legacy metric landscape не заменяет independent recognition evaluation. Ненулевой result не всегда failure и не всегда pass |

Остальные PostTune поля — ptPubParameter без setter, в том числе numeric controls.
Сохранение этих полей не сериализует PostTuneSampleState/снапшоты/очередь проб
и не обеспечивает идемпотентного Solo→Recognition conversion.

## Прочитанные источники и границы приёмки

В обоих `.cpp` проверены defaults/registration/setters, ApplyActiveLtzThreshold,
UpdateIterLTZPotential, CalibrateFixedLTZThresholdFromTraining, EndOfLearning,
ReadPostTuneProbeMetric/ReadPostTuneLiveMetric, ApplyPostTrainTipMode,
SetupPostTuneFreeRunProbes, Enter/FinalizePostTune, MaybeStartInferenceMidProbes
и budget consumers. В NNeuronPostTrainTune.h проверены enums, validity helpers,
LandscapeOk и ApplyCandidateMidOnNonSeparableTest. NativeConfiguredOwner и
BeginNativeTraining подтверждают запрет пока неподдерживаемых optional modes.

Legacy tests/helper controls проверяют отдельные landscape/nonseparable/finite
случаи. Они не являются приёмкой transactional native import, полной storage
physics при Branch rebuild, сохранения conversion state или выбранного порога
на реальном повторном spiking run. Этап 8 остаётся невыполненным.

Требования рефакторинга: immutable Solo→Recognition; явные Same-Matrix и frozen
independent protocols; один common probe runner; полный commit/rollback модели;
fresh final verification после изменения physics; CalibrationResult с данными,
методом и подтверждающим actual threshold run. Legacy inference finalization
также удаляет SelectivityLog/results.csv и сбрасывает analyzer после своих проб;
новый pipeline обязан хранить версии наблюдений/попыток и не терять первичные
данные при калибровке. Offline sweep одного spiking CSV
не заменяет такой run из-за обратного влияния spike на LTZ dynamics.
