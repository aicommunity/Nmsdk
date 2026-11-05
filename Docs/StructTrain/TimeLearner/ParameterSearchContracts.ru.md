# Владельцы параметров поиска и времени предъявления

Проверены по исходникам ещё18 свойств: девять в Classic и девять в Branch.
[Реестр](parameter_search_contracts.json) дополняет, но не заменяет
[предыдущие10 управляющих контрактов](ParameterControlContracts.ru.md).
Исходный root — `fbc523a9d9fb226cf9a4834206fe17fdcd407185`, PulseLib —
`70f467d3b66ea4defdec2f58b84e76b692ab3602`. Для каждой записи приведены
commit, blob, строка декларации/регистрации и реализации. Это source review;
новых численных прогонов и полной runtime-приёмки18 свойств здесь нет.

Актуализация06.11: исходный JSON-реестр остаётся историческим source snapshot.
Текущие исправления и границы runtime-приёмки приведены ниже; их
[сверка с принятым PulseLib и первичными данными](ParameterContractStatusReconciliation.json)
не является новым численным прогоном.

## Действующие владельцы

| Свойство | Legacy: default и смысл | Configured V2 |
|---|---|---|
| StructureBuildMode |1; только ровно1 вызывает BuildStructure.0 использует готовый граф. Setter не проверяет диапазон и помечает Ready=false только при положительном значении. | Политикой сохранения выделенного кабеля владеет model.preserve_allocated_cable. При первоначальном explicit-native adoption без declaration значение0 участвует в создании политики. Не смешивать с режимами нейрона0/1/2. |
| MaxDendriteLength |100 сегментов. Setter может немедленно уменьшить геометрию и сбросить нейрон; это не пассивная граница поиска. Classic и Branch выполняют разные перестройки. | model.maximum_cable_length и согласованные search.bounds. При существующей declaration setter принимает только объявленную границу. |
| NormalizationMode |1: TipResistance;0: SynapseCount. N0 очищает derived Rs bounds; N1 может прочитать реальные tip Rs и изменить multiplicity. | model.normalization согласован с search.normalization; declaration запрещает переключение через legacy-свойство. |
| SyncTolerance |0.02 с, исходный временной допуск. | search.tolerances.sync. Изменение только legacy SyncTolerance не изменяет допуск плана V2. |
| PeakMeasureMargin |0.06 с, половина legacy-окна около предсказанного прихода. | Явные windows и peak_selection. Предсказание не подтверждает наличие пика. |
| DelayAgreeMarginMin |0.03 с, legacy agreement floor вместе с SyncTolerance. | Не является входом MakeConfiguredNativeTrainingPlan. |
| IterationGap |0.5 с, условный нижний предел. При AutoScaleIterationGap=true этот предел игнорируется. | Полный протокол определяется длительностью пробы, окнами, reset policy и фактическими timestamps, а не этим legacy-полем. |
| AutoScaleIterationGap |true: span+settle+slack. При false учитываются пользовательские floors. Dataset delay дополнительно ограничен снизу1.55 с для late-response окна. | Не объявляет V2 ITI. |
| Classic EstDelayPerSeg / Branch InitEstDelayPerSeg | Classic: публичная адаптивная оценка0.005 с/сегмент. Branch: seed0, означающий fallback0.005, и отдельная приватная адаптивная оценка. | Эти legacy-поля не управляют V2 proposal policy. В V2 уже принят отдельный measured-length proposer: минимум три согласованные измеренные длины, bounded bracket/secant candidate и обычный перебор при немонотонности. См. [область приёмки](MeasuredLengthProposal.ru.md); прогноз не подтверждает пик или Exact. |

Обычный Reset не означает Default и не возвращает эти параметры к defaults.
В частности, Classic сохраняет EstDelayPerSeg при ResizeSyncVectors. Branch
копирует seed в приватную оценку при ResizeSyncVectors; этот вызов нельзя
безусловно приписывать каждому Reset с неизменной размерностью. Сохраняемый
seed и текущая история оценки — разные сущности.

## Что требуется от постановки эксперимента

Перед Train определить класс и ControllerVersion, затем владельца изменяемого
значения. Для V2 менять соответствующее поле строгой декларации до cold build,
сохранять декларацию и effective readback. Для legacy сохранять также зависимые
переключатели: например, sweep IterationGap при AutoScaleIterationGap=true
не доказывает изменение фактического интервала. Для обоих путей проверять
реальные onset timestamps и законченные окна наблюдения.

Одного наличия UProperty или успешного setter недостаточно для подтверждения
фактора. Этот реестр пока не подключён как универсальный production preflight;
его интеграция и положительные контроли применения факторов остаются в этапе9.
Равенство результата N0/N1 само по себе не является ошибкой применения фактора.

## Статусы выявленных дефектов

`PARAM-FINITE-001` — **исправлен и адресно runtime-проверен**. Исходный
Pulse70f467d действительно принимал неконечные назначения. Исправление
`ecf35a6c322f58fc9c4ffdfb998bf882f990252a` добавило isfinite в четыре общих
setters, Classic EstDelayPerSeg и новый setter Branch InitEstDelayPerSeg.
Все десять тел методов в принятом PulseLib0ec9193 побайтно совпадают с tested
версиями. [TimingFiniteValidation](TimingFiniteValidation.ru.md) сохраняет
baseline failure и normal/ASan acceptance: на каждом worker4 property cases
и21 regression,120 NaN/±Inf назначений отклонены с сохранением предыдущего
значения. При сверке06.11 повторно проверены все71/112 archive members,
четыре actual property records и завершённые gtest receipts каждого корпуса.

Это обычный локальный UProperty::SetData на настоящих storage-объектах,
включая Return→Take, при2000/20000Hz. XML parser, SetDataDirect и connected
supplier не покрыты этим утверждением; не считать их автоматически проверенными.
Finite domains сохранены: общие margins/gap>=0, Classic estimate>0,
Branch finite seed<=0 остаётся штатным fallback. JSON V2 имеет своего validator.

`LIFECYCLE-BOOL-001`: legacy ABuild/AReset обоих learner всё ещё имеют ветви
return false при внутренних отказах. Уточнение после проверки Rdk0a1c1d05:
UContainer вызывает ABuild/AReset без чтения их bool; публичные Build/Reset
уже возвращают true. Это остаточная несогласованность hooks, а не доказанная
ошибка публичного bool или самостоятельная причина неуспешного обучения.
Любая очистка должна сохранить раннюю остановку, диагностическое состояние
и порядок scheduler; нельзя начинать распространять bool или продолжать
незавершённую инициализацию после механической замены return false.

`PARAM-NATIVE-FACTOR-001`: наличие совместимых legacy-полей при работе V2 создаёт
риск недействующего экспериментального фактора. Реестр точно указывает владельцев;
все активные генераторы jobs и preflight ещё требуется проверить по этому правилу.

Полные этапы1/4/6/7/9 остаются открытыми. Исходный source_inventory.json сохраняет
исторические pending flags;28 source-reviewed записей в двух дополнительных
реестрах не означают28 runtime-принятых параметров или завершение всего inventory.
