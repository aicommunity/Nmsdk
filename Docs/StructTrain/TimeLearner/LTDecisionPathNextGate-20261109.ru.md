# Следующая адресная проверка фактического LT decision path

Это предложение проверки, без реализации и runtime-приёмки. Renderer3 исправляет масштаб; он не доказывает выполнение LT. Нулевой LT Potential в actual burst по исходникам не утверждается. Активный baseline A4 не изменяется.

Уточнение к `LTSomaSignalSourceAudit-20261108` и `ClassicFlatLTMetadataTrace-20261108`: pinned `NativeProbe.cpp:242–247` уже требует Ready/Init и одинаковый TimeStep всех descendants при prepare, а `CheckLiveGraph:91–94` повторяет Ready/Init watched nodes на границах ticks. Policy запрещает ограничение `MaxCalculationDuration>=0`. Поэтому completed packet не оставляет полное отсутствие Init равновероятной непроверенной причиной. Сами флаги и фактическое посещение LT по фазам ещё не опубликованы.

Если новый overview оставит вопрос о нулевом LT при ненулевых soma channels, провести один изолированный gate с двумя cases:

- `NativeLTDecisionPath/ClassicPinnedHighBurstSameTick`;
- `NativeLTDecisionPath/ClassicPinnedHighSingleCollectorControl`.

Нужен точный исходный highClassic граф: Root `844b2789ea0c087c1a0f676d9584ce7b8a7a4d36`, Pulse `1f97e4facc5bf03887bc337450190cc7b24c3ebf`, Rdk `10e9d05aa658dd2203c89bc84ba9166595b50014`, Bin `fc67a3b0958e8becdfbe1cd3f0e4e054d966d54f`. Primary commit `cd8d32168c3580948d0684f6ccad9f64f8527d94`, members `runs/Classic-threshold-training100-retry32-{burst,single}/native`. Исходный model revision `913bd90b0a27697f237f08771db1b9431db64a86ac5d43a192f7610a80d71d04`. Не заменять его SoloThresholdTrace fixture другой модели.

Использовать production import/probe и штатное подробное логирование Rdk (`SetPropertiesForDetailedLog`, logger/debug masks). Не заменять LT-класс, не добавлять Calculate и не менять физику. DebugSysEventsMask исключён из semantic model identity, но отсутствие влияния логирования на primary должно подтверждаться парными fresh-import Off/On прогонами. Обычное чтение Inputs после tick обновляет lazy vector-property и не доказывает, какие входы ранее потребил LT.

Один упорядоченный bounded trace должен содержать frame/model-time markers и следующие readbacks:

1. Ready/Init/Activity/static/TimeStep для owner, neuron, Soma1–4, LTZone и generator, operation-failure sequence.
2. Реальный порядок посещений soma channels, soma parent и LTZone.
3. Непосредственно в LT-phase — восемь Inputs, размеры, GetDataSources/external-source признаки, UseAveragePotential, NumChannelsInGroup, затем NeuralPotential/Potential/OutputPotential после расчёта.
4. На существующей native-after-children границе — typed readbacks того же живого LT-экземпляра, generator, исходная diagnostics row и descriptor index.
5. Полные штатные CSV/packet/diagnostics/model/source snapshots. Отсутствующая запись означает unknown/отказ, а не нулевое значение. Не соединять фазы по округлённому wall timestamp.

Ненулевой Soma1 не требует ненулевого LT: LT агрегирует все восемь channel outputs с фактическим averaging. Проверяем aggregate действительно прочитанных в LT-phase входов. Если LT не посещён, проверяем scheduler/static/active-cache; если входы не равны источникам той же фазы — binding/dimensions. Нулевой полный aggregate допускает штатную компенсацию вкладов. Ненулевой aggregate при несогласованном Potential локализует LT execution/external override. Различие LT post-state и after-children указывает на промежуточную запись/Reset; различие typed after-children и diagnostics row — на collector/index mapping.

Gate выполняется только на сервере, с отдельными исходниками и runtime, после review конкретного fixture и native logging path. Это точечное продолжение прежнего source-аудита, а не повторный аудит всех его файлов и не основание приписывать графу дополнительную LT-мембрану.
