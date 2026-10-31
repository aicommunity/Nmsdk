# Семантика исходных свойств: порог, PostTune и калибровка

Code review **44 исходных записей** (22 × оба класса), PulseLib
`025d809f7b86cc79e18ddd711c6adc40e2396bf8`. Это описание текущего legacy-кода,
а не объявление выполнения этапа 8. Указанные ниже запреты относятся к
configured learner properties. Отдельные typed PostTune/calibration API, native
model import и production jobs реализованы позднее; актуальная граница описана
в дополнении 31.10 в конце документа. Cold declaration не является checkpoint.

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

## Дополнение 31.10: API и независимые владельцы фаз

Typed NativePostTuneTransaction и NativeThresholdCalibrationTransaction,
versioned recognition/calibrated packages и production schema-2 fixed jobs
проверены отдельно: [текущий контроллер](NativePostTuneController.ru.md),
[normal jobs](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-fixed-console-normal-a1/README.md),
[ASan jobs](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-fixed-console-asan-a1/README.md).
Это не подключённый dispatch перечисленных public properties. Оба optional
mode guards в PrepareConfiguredNativeOwner и BeginNativeTraining остаются.

Повторная проверка действующих consumer paths выявляет следующие обязательные
различия для phase plan; объединять эти поля в один флаг запрещено:

| Декларация | Фактический legacy consumer | Требование к новому phase plan |
|---|---|---|
| AutoCalibrateFixedLTZThreshold | CalibrateFixedLTZThresholdFromTraining использует LastSyncedMin/MaxLTZ и mode/fraction/clamps | Это target-reference threshold proposal. Не подменять его процедурой target/foil grid. Сохранять происхождение proposal и проверять выбранный порог настоящим прогоном |
| Branch EndOfLearning при EnablePostTrainTuning=false | После optional target-reference процедуры всегда переходит в kPhaseCalibrateLtz; FinishTrainingIteration вызывает FinalizeAfterParallelCalibration и CalibrateFixedLTZThresholdFromParallelPeak | Эта parallel-peak калибровка не проверяет AutoCalibrate внутри своего consumer. AutoCalibrate=false и PostTune=false не гарантируют сохранение fixed threshold. Переход есть также при N0; только Rs scaling отдельно ограничен N1 |
| EnablePostTrainMidThreshold | FinalizePostTuneMid использует PostTuneMetrics и valid sample states; может работать при AutoCalibrate=false | Это самостоятельная target/foil процедура PostTune. AutoCalibrate=false само по себе не означает отсутствие этого выбора порога |
| PostTrainSilentThreshold | Применяется при PostTune/inference probes и некоторых отрицательных исходах | Порог изменяет LTZone dynamics. Явно отделить threshold измерения весов от порога конечной recognition-модели. Нельзя молча игнорировать несовпадение с inherited threshold |
| PostTrainTipResistanceMode | NNeuronPostTrainTune.h: 0 Off, 1 CanonRmin, 2 FlatLastR, 3 KeepDone, 4 SearchSynthetic | Enum не совпадает по порядку с NativePostTuneControllerMode. Использовать явное сопоставление, не static_cast |
| PostTrainMidMetric | 0 Auto, 1 LTZ, 2 Soma; Auto зависит от topology | Сохранить topology-dependent metric и измеряемый физический канал. Не сравнивать несовместимые единицы без записи источника |
| PostTrainSyntheticFoilCount | Ограничивает BuildRecognitionProbePatterns / BuildSyntheticPatterns, а не число кандидатов Rs | Проверять действительный предъявленный набор и pattern hashes. Не связывать это поле с maximum_candidates поиска весов |
| PostTrainTipSearchIters | Бюджет проходов SearchSynthetic | Отдельный budget от числа weight candidates, recorded samples, threshold candidates, model/wall time |

Для Branch подтверждены цепочки EndOfLearning → kPhaseCalibrateLtz →
FinalizeAfterParallelCalibration → CalibrateFixedLTZThresholdFromParallelPeak
и отдельный IsParametricNormalization guard только в ScaleTipResistancesForParallelActivation.
Следовательно, первоначальный конфиг с AutoCalibrate=false не является
доказательством отсутствия runtime threshold selection. В историческом реестре
указывать effective graph/threshold и фактическую фазу; при отсутствии конечного
состояния сохранять unknown. Не отменять августовское наблюдение и не приписывать
ему новый frozen-threshold протокол по одним исходным флагам.

Native KeepFixedThreshold сейчас измеряет weights при наследуемом пороге и
сохраняет этот же порог; это проверенная математическая задача данного API.
Она соответствует public-config фазе только после явной проверки согласованности
независимых mid/auto/silent controls. Не менять её скрыто ради подключения
legacy defaults. Для отличающегося probe threshold требуется явно записанное
состояние физики измерения, полный native import и проверка конечного порога;
сертификат измерения нельзя переносить на другую threshold-физику.

При recognition import VisitNativeRecognitionControls зеркалирует IsNeedToTrain,
EnablePostTrainTuning, AutoCalibrate и threshold-поля, а InstallNativeRecognitionState
очищает training service и NativeConfiguredPlan. Поэтому original phase declaration,
завершённый Solo package и training outcome сохраняются до первого import в
отдельном orchestration state. Последующая фаза не восстанавливает исходные
flags из уже изменённых owner mirrors. Явный Reset/Default не запускает rollback
или import из lifecycle hook; подготовленный InterruptOwnerLifecycle переводит
контроллер в RecoveryRequired без доступа к owner. Normal приёмка detach API получена: 16 native, 12 прежних regressions и
8 reader checks. ASan также завершён: 16 native, 12 regressions, 8 reader,
без skips; leak detection off. Сам configured phase dispatch ещё не подключён.
