# Семантика исходных свойств: cold reset, experiments и logging

Code review последних **15 записей** исходного inventory, PulseLib
`025d809f7b86cc79e18ddd711c6adc40e2396bf8`. Вместе с другими профильными
обзорами покрыты 211/211 исходных записей; шесть новых configured properties
проверены отдельно. Это завершение code catalog, а не всей runtime/property
матрицы, не всего этапа 1 и не всего плана.

| Свойство | Тип/default/flags | Фактическая логика | Ограничения и необходимые проверки |
|---|---|---|---|
| ResetToUntrainedState, оба | bool, false, ptPubState; setter принимает value без действия | Legacy AReset считывает one-shot, очищает flag и отдельно вызывает ResetToUntrained; snapshot принимается только при cold-looking lengths, иначе создаётся исходная структура. Native-owned AReset выходит раньше этой legacy ветви | В native режиме это поле не выполняет cold reconstruction. Обычный Reset сохраняет модель/цель; новый cold reset должен быть отдельной явной операцией. Проверять loaded trained graph, snapshot validity и действительную declared initial state, а не L>1 как обязательный признак trained |
| UseLoadedTipResistanceOnUntrainedReset, оба | bool, false, ptPubParameter; setter отсутствует | Legacy cold reset при N1 принимает loaded TipRs только при полной размерности и всех finite positive entries, затем clamp; loaded vector имеет приоритет перед scalar base/snapshot | Это явно warm/configured resistance seed, а не гарантированный factory cold start. Native initial physics задаётся declaration/import; legacy flag не подменяет её. Нужны finite/dimension/Load-order controls и provenance исходного состояния |
| ExperimentNum, оба | int, 0, ptPubParameter | Setter устанавливает CalculateMode=1, сбрасывает первый file-step. Experiment() в этих двух классах возвращает true без dispatch | Поле имеет управляющий side effect, но **не выбирает реализованный incremental algorithm**. Загрузку сохранить, использование как научного режима запретить. Не приписывать функциональность NNeuronLearner |
| ExperimentMode, оба | bool, false, ptPubParameter | Setter true ставит ExperimentNum=1 и epoch counter; false закрывает file streams и разрешает изменение L. Legacy ACalculate вызывает пустой Experiment(), затем всё ещё Training(), если Need=true. Native-owned early return эту ветвь обходит | Комментарий «instead of Training» не описывает фактический dispatch. Это не работающий альтернативный Train/recognition protocol. Требуются preflight capability и mode side-effect tests |
| EnableDebug, оба | bool, false, ptPubParameter; setter только принимает value | Включает подробные legacy decisions/dynamics и дополняет условие записи compact training audit. Default сбрасывает false | Не scientific factor. Logging overhead может повлиять на wall-time budget; model time и wall time хранить отдельно. Logs не заменяют complete primary observations |
| EnableTrainingAudit, оба | bool; **нет явного присваивания в ADefault**; ptPubParameter, без setter | Fresh UProperty value-initialization даёт false; audit пишется при Debug OR Audit и доступном Environment/data directory. При reused object Default сам этот flag не сбрасывает | Нельзя документировать общий Default=false для reuse только по fresh constructor. Это code finding незакрытого default/reuse контракта; нужен production Return→Take reproducer и fix у владельца. Новый runner должен явно задавать и сохранять logging configuration |
| Branch DynamicsLogHead | int, -1, ptPubParameter | При <0 — прежняя запись всех active burst ticks; при >=0 первые head records полные, после них включается thinning | Это число log records, не model steps/проб. DynamicsLogCounter увеличивается только при Debug && Environment && IterationActive, Default задаёт 0; обычный Reset не подтверждён как сброс counter |
| Branch DynamicsLogEvery | int, 1, ptPubParameter | После head consumer использует max(1,value); оставляет каждую every-th запись | <=0 не выключает log. Прореженный журнал не является полной waveform trace и не доказывает отсутствие early/late events |
| Branch DynamicsLogComponentState | bool, true, ptPubParameter | После head регулирует подробный component-state payload. Head records остаются полными; при head<0 действует historical full mode | Отсутствие детализации не означает отсутствия соответствующих channels/synapses. Сохранить выбранный sampling policy, не выдавать thinning за complete observation |

Число строк с пометкой «оба» учитывается отдельно для каждого класса.
LearningAdditionalPattern_1_4 и IncrementalLearning явно игнорируют arguments и
возвращают true; Experiment также пуст. Успешный lifecycle/interface return
не является доказательством существования алгоритма.

## Прочитанные источники и проверки

Оба `.h/.cpp`: registration/defaults, SetExperimentMode/SetExperimentNum/
SetResetToUntrainedState/SetEnableDebug, ResetToUntrained/AReset,
ApplyLoadedAnchorProperties, ACalculate и пустые experiment methods;
AppendTrainingIterationAudit/AppendTrainingDoneAudit/AppendTrainingDynamicsSample,
Branch thinning и DynamicsLogCounter. Rdk UProperty constructor подтверждает
fresh value-initialization; это не доказательство поведения reused Default.

Существующие cold-reset/resistance fixtures и native Reset/warm/import cases
проверяют отдельные состояния. Необходимы дополнительные Return/Take audit-flag,
side-effect/capability и log-sampling controls. Исторические логи сохраняются;
исторические executable scripts после миграции должны быть удалены из trees,
с repository/commit/path/blob в migration manifest.
