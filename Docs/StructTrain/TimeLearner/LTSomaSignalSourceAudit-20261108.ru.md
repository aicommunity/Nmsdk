# LT-мембрана, LTZone и измерение сомы: аудит пути сигналов

Статус: **read-only source audit, 08.11.2026**. Численные расчёты, imports
моделей, чтение серверов и новые графики не выполнялись. Причинное влияние LT
на результаты обучения этим документом **не подтверждено**. Машинная привязка
Git blobs/SHA/строк и оставшихся сравнений:
[LTSomaSignalSourceAudit-20261108.json](LTSomaSignalSourceAudit-20261108.json).

Источник PulseLib — `88ea9c7ab3583da601b1f01ec84bf6f122875a34` (далее Pulse88),
Rdk — `d6c9df759a3ee20ad42fa0a83841f19385fba60a` (RdkD6), root документации и
Python consumers — `c31cda612e223c97e873d6e6aa0dd0b2d5927fdc` (RootC31).
Это source binding, не повторная приёмка этих исходников или всех storage images.
Номера строк — LF-delimited Git blob lines, не позиции после преобразования CRLF.

## 1. Главный вывод и пределы

`LTMembrane` и `LTZone` — разные объекты. В штатных `NSPNeuronGen` и рассмотренных
Gen/Preinh/Fast/AsymRm/TauH0/Sim рецептах **отдельная LTMembrane отключена**, а
LTZone имеет реализацию `NPulseLTZoneThreshold`. Следовательно, по одному названию
Gen или кривой сомы нельзя приписывать этим образам RC-инерцию LT-мембраны либо
интегратор класса `NPulseLTZone`. У body/dendritic channels и synapses собственная
динамика остаётся. Реальный загруженный экземпляр всё равно определяется полным
native graph/storage/effective readback; recipe name не заменяет его.

Native Train измеряет `Soma*.SumPotential`, а не LTZone.Potential, не LTZone.Output
и не LTMembrane.SumPotential. Это соответствует сохранённой цели обучения по
синему сигналу сомы. LT decision potential — отдельный, действительно используемый
пороговым сравнением сигнал; flat zero на графике не доказывает, что LTZone его
игнорирует или что во всём физическом графе отсутствует сигнал.

В обычной сгенерированной топологии LT=On находится после сомы. Но сравнение
LT=Off/On меняет также адресата spike feedback. Поэтому Off/On не является
чистым сравнением одной LT time constant. Для explicit/recurrent graphs,
других классов синапсов, иной истории Reset или дополнительных связей общие
выводы о причинности не переносятся без проверки реального графа/трасс.

## 2. Различные сигналы и фактические consumers

| Сигнал | Определение по Pulse88 | Где реально читается |
|---|---|---|
| `NPulseChannel.Output` | динамическое состояние одного канала; C, G, R и Feedback участвуют в update | источник суммарного потенциала мембраны и downstream ChannelInputs |
| `NPulseMembrane.SumPotential` | сумма `Channels[i].Output(0,0)` после child calculations, без отдельного фильтра | Native Train baseline/samples; отдельные soma columns CSV; legacy MaxIterSomaAmp |
| `NPulseNeuron.SomaSumPotential` | суммирование soma channel outputs с делением по NumChannelsInGroup | отдельный агрегированный readout нейрона; не тождественен каждой Soma.SumPotential |
| `LTZone.NeuralPotential` | сумма Inputs с условным averaging по числу inputs/channel groups | внутренняя основа LTZone.Potential |
| `LTZone.Potential` | у Threshold — NeuralPotential; у NPulseLTZone — результат его PrePotential integration | фактический comparator; threshold traces, calibration и отдельная LT panel |
| `LTZone.OutputPotential` | у Threshold копирует Potential | вспомогательный matrix output; не spike output |
| `LTZone.Output` | PulseAmplitude при пороге, иначе удержание/выключение через ThresholdOff | neuron.Output и feedback; LT marker/history строится по событиям |
| `Membrane.Feedback` | FeedbackGain × сумма InputFeedbackSignal | входит в update каналов; это не потенциал LT-мембраны |

Источник суммы: `Core/NPulseMembraneCommon.cpp:185–204`; channel update:
`Core/NPulseChannel.cpp:215–290`; агрегат нейрона: `Core/NPulseNeuron.cpp:956–991`.
`NPulseNeuronCommon.cpp:370–374` копирует именно LTZone.Output в neuron.Output.

Classic `NativeProbeModelBindings` перечисляет Soma1..SomaN
(`NNeuronTimeLearner.cpp:4105–4116`); Branch — только Soma1 при N logical inputs
(`NNeuronTimeLearnerBranch.cpp:4853–4869`). `NativeProbe.cpp:354–358,415–424`
читает их SumPotential для baseline, recorder.Observe и onSample.potentials.
`NativeCompositeTrainingAttempt.cpp:292` сохраняет фактические physicalChannelPaths;
`NativeMatchedOmissionGroup.cpp:39–44` проверяет это отображение. Один soma channel
Branch нельзя размножить в дополнительные физические сомы по числу input IDs.

Legacy peak readers также берут Soma.SumPotential: Classic
`NNeuronTimeLearner.cpp:5266–5279`, Branch `NNeuronTimeLearnerBranch.cpp:6003`.
Однако legacy counters/history arrays и native assigned N+2 measurement — разные
контракты. Глобальный максимум окна Test не становится assigned Train maximum.

Нынешние plot consumers различают источники:

- `plotting.py:106–154` рисует `samples[].soma[channel]`; это не автоматическая
  запись LT-мембраны. `declared_window_basin_report.py:38` берёт actual CSV soma columns.
- `NativeSoloThresholdTrace.h:113–120,133–150` отдельно записывает
  `$.LTZone.Potential`, class, threshold, model binding, phase
  `native_after_children`, units=`model_units_SI_unverified`, soma и реальные события.
- `solo_threshold_reports.py:43–75` сохраняет отдельные Soma SumPotential и
  LTZone.Potential figures. То, что общий renderer технически получает singleton
  array `soma=[lt_potential]`, не меняет source label/manifest role этой панели.
- `NativeRecognitionTrial.cpp:209–228` отдельно сохраняет somaPotentials,
  LT Output/spike history и optional thresholdPotential=zone.Potential.
  Source path/class фиксируются (:162–163), а Python
  `recognition_trial_evidence.py:60–68` проверяет descriptor.
- `NativeCalibrationProposal.cpp:63–83` вычисляет full/inside/outside maxima по
  thresholdPotential с проверкой единого model/path/class. Legacy
  `ReadLTZonePotential` (:985–992) и `UpdateIterLTZPotential` (:996–1014) также
  читают zone.Potential; последнее пропускает неположительные значения. Это
  ограничение legacy calibration statistics, не определение самого сигнала.

## 3. Пороговый класс действительно обновляет и использует Potential

[`NPulseLTZone.h:25`](https://github.com/aicommunity/Nmsdk-PulseLib/blob/88ea9c7ab3583da601b1f01ec84bf6f122875a34/Core/NPulseLTZone.h#L25)
объявляет Threshold наследником NPulseLTZoneCommon. Он не заменяет ACalculate:
унаследованный `NPulseLTZoneCommon::ACalculate` (:224–261) выполняет
`Inputs → NeuralPotential → Potential`, затем вызывает виртуальный ACalculate2.
Threshold::ACalculate2 (:97–118) вызывает CheckPulseOn/Off;
CheckPulseOn (:164–168) сравнивает **Potential >= Threshold**, CheckPulseOff
(:172–174) — Potential < ThresholdOff. OutputPotential затем получает Potential.
`NLTZone::AReset` (:98–103 в NPulseLTZoneCommon.cpp) обнуляет Output и Potential;
Common::AReset (:204–221) очищает NeuralPotential/PrePotential и event history.

Таким образом, гипотеза «у NPulseLTZoneThreshold Potential не обновляется и не
используется, сравнение идёт по иному полю» **не следует из этого исходника**.
Для иной фактической C++ реализации/override или внешней связи нужен отдельный
source descriptor. `NativeThresholdSupport.h:12–18` допускает scalar threshold
только для точных C++ типов NPulseLTZoneThreshold/NPulseLTZone; имя storage image
само по себе не доказывает этот capability.

Flat zero надо диагностировать по raw bytes, source class/path, actual Inputs,
Activity/Init/Ready и calc phase; затем сверить expected aggregation с channels,
Potential и comparator. RdkD6 `UContainer::Calculate:2498–2522` возвращает true
также при Activity=false/InitFlag=false, не рассчитывая детей. Его bool не
является проверкой наличия сигнала. Нельзя объявлять zero результатом скрытого
отсутствия сигнала либо менять подпись comparator без такого evidence.

В двух рассмотренных production auxiliary producers ошибочного cast к sibling
`NPulseLTZone` нет: `NativeSoloThresholdTrace::Attach:24–25` получает
`NPulseLTZoneCommon` и требует nonnull, без fallback0; Prepare/Observe (:106–133)
проверяют source/lifecycle/nonexternal Potential. `NativeRecognitionTrial:155`
тоже получает Common, а :162–163 сохраняет его path/class. Реальный C++ fixture
RootC31 `Test_PulseLib_SoloThresholdTrace.cpp:36` также использует Common и
отказывает при отсутствии; его probe loop :67–78 сохраняет отдельные Cancel/
Changed сценарии. Это не проверка всех исторических/TEMP producers. В `NativeProbe` recordSpikes=false не выключает LT:
Prepare reset выполняется один раз (:331), AfterTick читает soma и вызывает
onSample (:419–424), без промежуточного Reset LT. Флаг относится к содержимому
spike observation; `ProbeObservation.h:38` прямо задаёт unknown spike response,
не zero. При выключенной записи отсутствие spike rows не доказывает no-spike.
Любой missing source/read должен стать unknown/error, а не нарисованным нулём.
Точная причина конкретной flat panel остаётся открытой до binding
plot→raw trace→producer source/runtime; источник нельзя угадывать по подписи.

`NPulseLTZone` — другая реализация: UseLTZIntegtation/TimeConstant/PrePotential
добавляют интеграцию перед тем же threshold comparator
(`NPulseLTZone.cpp:284–303`). Она не присутствует в stock Gen recipes. Отдельные
source-only вопросы для её регрессии: при integration=true и stabilizer=false
локальный input остаётся 0 (:288–295); setter UseSpikeStabilizer принудительно
записывает TimeConstant=0.00144 (:213–215). Это не измеренные эффекты и не
авторизация менять физику; тесты поддерживаемости этих режимов нужны отдельно.

## 4. Топология LT=Off/On и возможные обратные пути

[`NPulseNeuron.cpp:654–722`](https://github.com/aicommunity/Nmsdk-PulseLib/blob/88ea9c7ab3583da601b1f01ec84bf6f122875a34/Core/NPulseNeuron.cpp#L654):

```text
LT=Off: Dendrite channels → Soma channels → LTZone.Inputs
                                      LTZone.Output → Soma.InputFeedbackSignal
LT=On:  Dendrite channels → Soma channels → LTMembrane channels → LTZone.Inputs
                                               LTZone.Output → LTMembrane.InputFeedbackSignal
```

Диаграмма показывает связи, которые условно создаёт данный код, а не аттестует
полный граф уже сохранённого/клонированного экземпляра. При role replacement
существующие prototype links тоже требуют readback; отсутствующий в этой ветке
CreateLink сам по себе не является доказательством отсутствия старого link.
Обычный BuildStructure соединяет dendrite chains с soma (:732–765), но не добавляет
LTZone feedback в эти dendrites. Отдельный `BranchDendrite(name, feedback=true)`
умеет добавить обратную связь (:319–341); сохранённый explicit graph может иметь
и другие links. Hebbian/иные channel types требуют своей проверки.

**Ограниченный вывод по зависимости кода:** для LT=On в этой штатной feed-forward
топологии при неизменных body physics/stimulus/initial state LT-membrane RC не
входит в формулу Soma.SumPotential и не имеет показанного обратного пути к soma.
Она влияет на собственные outputs и вход LTZone. Это не наблюдённое сравнение и
не универсальное утверждение обо всех моделях. При LT=Off LTZone spikes могут
через Feedback изменить последующие soma channel outputs. Для предшествующего
первому spike участка этот feedback-путь отсутствует **только если** actual
история Output/Feedback действительно нулевая, а не унаследована от warm state.

Порядок тоже является частью модели: structured mode считает dendrites, soma,
LTMembrane, LTZone (`NPulseNeuron.cpp:998–1042`); mode0 сохраняет explicit порядок.
Rdk child loop выполняется до parent ACalculate (`UContainer.cpp:2557–2560,2611+`).
Membrane parent вычисляет Feedback после расчёта своих channels. Поэтому нельзя
предполагать мгновенный feedback на том же sample; его phase/delay надо записывать.
Добавление LT-компонента само по себе не доказывает изменение раннего soma peak.

## 5. Образы, C/R/threshold и границы uniform overrides

`CreateClassSamples` находится в `Core/NPulseLibrary.cpp:60`. Storage class name
может быть зарегистрированным образом того же C++ класса. Обычный NPNeuron имеет
LTMembraneClassName=NPLTZoneNeuronMembrane и LTZoneClassName=NPLTZone
(`NPulseNeuron.cpp:883–886`), а Gen намеренно заменяет их:

| Рецепт Pulse88 | Объявление | LT структура и владельцы |
|---|---|---|
| NSPNeuronGen | NPulseLibrary.cpp:1123–1132 | LTMembrane="", NPMembraneBio body, Threshold class, threshold0.0117 |
| GenSymInhC1e9 | :1134–1147 | без LT; body parent C и DissociationTC; не AsymRm |
| GenPreinh family | :1183–1205; membrane chain :401–427 | без LT; меняет body synapse image/inhibition coefficient, не LT RC |
| Fast grid | :1153–1178 | без LT; parent MembraneCapacity/SynapseDissociationTC + UseElementDefaults |
| PreinhFast | :1209–1223 | без LT; явный ApplyElementDefaults после parent fields |
| AsymRm C25e12/C25e11/C1e9 и preinh twins | :1226–1412 | без LT; body Exc/Inh Rm/Rsyn различны, parent C uniform по body |
| TauH0 family | :1415–1447 | без LT; C задаётся параметром recipe, Rm/Rsyn асимметричны |
| Sim family | :1449–1477 | без LT; C и несколько synaptic time constants масштабируются совместно; это не LT-only intervention |

Числа AsymRm также читаются из source, не из имени: Pack A задаёт body
Exc/Inh Rm=1e7/1e8 и Rsyn=8.6e7/8.6e8 с C=2.5e-11,2.5e-10 либо1e-9
(:1226–1332). Pack B — C=1e-11, Rm=1e7/1e8, Rsyn=5e7/5e8 (:1335–1372);
Pack C — C=2.5e-11, Rm=5e6/5e7, Rsyn=8.6e7/8.6e8 (:1375–1412).
Preinh body recipe выбирает отдельный synapse image: UsePresynapticInhibition=true
и InhibitionCoeff=k из массива (:227–245). Это synaptic conductance path,
не LT membrane capacitance. Комментарий TauH0 о целевой τ не заменяет actual
G/state-dependent TimeConstant; Sim заявляет совместное масштабирование, а
численная time-similarity этим source audit не проверялась.

C/R принадлежат `NPulseChannel` и synaptic Resistance принадлежит synapse;
NPulseMembrane имеет FeedbackGain и selectors child images. NPLTChannel образ
меняет C=1e-8 и RestingResistance=1e6 (:343–348), сохраняя остальные поля базы;
он не тождественен body Bio profile. Порог принадлежит LTZone. Storage image
registration устанавливает baseline, ModelSpec2.initialThreshold применяется и
readback-проверяется на legal construction boundary
(`NativeModelBuilder.cpp:494–507`); legacy learner Training/FixedLTZ paths отдельно
переключают effective threshold (`NNeuronTimeLearner.cpp:972–981,2769–2784`).
Construction threshold и сохранённый effective threshold не взаимозаменяемы.

`NPulseNeuron::ApplyElementDefaults` (:783–873) при UseElementDefaults=true
перезаписывает положительные parent C/R/TC values в **body membranes**, явно
пропуская объект с именем LTMembrane (:806–807). Positive parent C задаётся и Exc,
и Inh body channels; Rm — отдельно по роли; synapse defaults могут затереть
индивидуальные learned resistances. Значение 0 означает retain class value,
а не физическую нулевую ёмкость. Scoped helper
`NNeuronTimeLearnerScopedDefaults.h:40–119` ограничивает reapply одной rebuilt
membrane; header-комментарий «every membrane» не отменяет skip LT в общей функции.
Uniform live child writes не являются способом конфигурировать новые прототипы.

Современный `RegisterStorageProfile` (:104–237 в StorageProfiles.cpp) создаёт
отдельные body/LT channel/synapse/membrane/zone/neuron images. Он ставит
UseElementDefaults=false и обнуляет parent override fields (:221–224), чтобы
heterogeneous C/R images сохранились. Body и LT могут иметь разные C/R, но разные
UseAveragePotential для них явно запрещены (:181–183), поскольку neuron ABuild
распространяет global averaging. `RegisterFeedbackStorageProfile` (:240–286)
копирует существующие полные образы и меняет только явно заданный FeedbackGain;
это construction recipe, не overlay живого learned graph.

Native V2 запрещает ненулевые parent Override* (`NativeModelOwner.h:17–22`) и
UseElementDefaults=true (`NativeModelBuilder.cpp:449`, Learner:4446,
Branch:5225). Его C0 baseline содержит фактическое C каждого канала
(`NativeModelEditor.cpp:953–972`). Capacitance edit целится только в named
Dendrite membranes и использует **C_channel=C0_channel×scale**, сохраняя исходную
heterogeneity (:525–539); soma/LT вне targets обязаны оставаться на baseline
(:1094–1099). Это не uniform parent C и не LT-инерционный switch. New-growth
baseline берётся из проверенного storage image (:503–510).

Rdk lifecycle нужно учитывать при чтении recipes: UploadClass вызывает Build и
регистрирует factory (`ULibrary.cpp:283–304`), TakeObject использует Default +
prototype/factory Copy. Copy инвалидирует Ready (`UContainer.cpp:1081`), а Build
при Ready=true — no-op (:2251–2254). Возвращаемые bool Build/Calculate/Reset не
используются как scientific/error channel; проверяются state/readback/diagnostics.

Два определения требуют явного review без переименования прошлых результатов:

- `NSPNeuronGenD005C25e11` в fast table (:1156) фактически задаёт **5e-10**, как
  D005C5e10 (:1155), а не ожидаемое по имени 2.5e-10. Это mismatch определения/имени,
  не измеренный эффект образа.
- Fast grid ставит parent fields после первого Build и делает второй Build,
  не снимая Ready; Asym/Tau/PreinhFast вызывают ApplyElementDefaults явно. Это
  различие промежуточного prototype state. Оно не доказывает неправильные children
  у будущего экземпляра: factory Copy и последующий Build могут применить defaults.
  Нужен readback prototype→TakeObject→Build→grow→save/import по штатному lifecycle.

## 6. Единицы и сохранение известных наблюдений

Native clock декларируется в Hz, время записывается в секундах; update использует
`1/TimeStep`, а TC×TimeStep — число шагов. Для потенциалов действующий source
явно пишет `model_units_SI_unverified` (NativeSoloThresholdTrace.h:120).
Capacity/Resistance названы физическими величинами, но имена и масштабы 1e-9/
1e7 сами по себе не аттестуют F/Ohm/Volt. Порог сравнивается в единицах фактического
LTZone.Potential, который может быть агрегирован/усреднён иначе, чем одна Soma.

Формула channel Ti=C/(G+1/R), sum_u=1+G×R, update=(input-output×sum_u)/(Ti×f)
следует из кода. Q=C×R×f — условный zero-G diagnostic, не доказательство полной
numerical stability/effective storage или биологической размерности. Active G,
FBResistance, RestingResistance, feedback/history и averaging нельзя убрать из
вывода одним RC-названием или внешне похожими графиками.

Августовские визуально подтверждённые 4/8–6/8 сохраняются для исходного протокола,
без приписывания им permutations/увеличенного ITI. Этот аудит не воспроизводил их.
Существующие [high-threshold subset наблюдения](HighThresholdSubsetScientificReport-2026-11-08.ru.md)
с Threshold100, raw soma maxima и ранним Branch maximum до закреплённого input2
сохраняют свою прежнюю область. Flat auxiliary LT panel не отменяет положительный
Soma.SumPotential и не разрешает подставить full-window maximum в Train assignment.
Данные/рисунки/критерии этих отчётов здесь не менялись.

## 7. Необходимые дальнейшие сравнения, пока не выполнены

1. **Сначала измерительный identity gate.** На реальном экземпляре фиксировать
   class implementation, все linked/external sources, Activity/Init/Ready/order,
   full storage/effective graph, C/R/threshold/averaging. Одновременно записать
   soma Exc/Inh Output, SumPotential, LT Exc/Inh Output/SumPotential (если есть),
   zone Inputs/NeuralPotential/PrePotential/Potential/OutputPotential/Output,
   Feedback и actual source/events после детей. Проверить aggregation и comparator
   event crossings. Raw flat0 не интерпретировать до этого gate. Нынешний Train
   CSV содержит только stimulus+soma; не объявлять недостающие LT channels записанными.
2. **Чистый LT RC contrast внутри LT=On.** Два новых immutable storage profiles,
   различающихся только заявленной LT channel C (и его image/binding). Body physics,
   zone implementation/threshold, input schedule, Reset/initial state, frequency,
   topology/feedback links совпадают. Без live hot-swap. Проверить actual diff до
   выполнения. Отдельно сравнить pre-first-spike soma samples и downstream LT trace;
   возможное сходство/различие устанавливается данными, не этим source audit.
3. **LT topology Off/On отдельно.** Зафиксировать, что feedback destination тоже
   меняется, записать это в condition identity. Такой contrast отвечает на влияние
   полного узла/топологии, не одной инерции. Threshold100 engineering и исходный
   threshold — отдельные условия; no-spike подтверждается actual event history,
   не числом 100. Warm/order/ITI не смешивать с reset-per-trial comparison.
4. **Prototype/heterogeneity lifecycle gate.** Fast/Asym/Tau recipes: parent и
   effective children до/после штатных TakeObject/Build/Reset/growth/native export/
   import. Подтвердить skip LT и сохранение индивидуальных body C/R при ownership
   через images; negative parent override в V2 остаётся отказом. Definition/name
   mismatch не исправлять автоматически и не переписывать исторические модели.
5. **Отдельный NPulseLTZone flags gate.** Только после review его поддерживаемости
   проверить integration/stabilizer combinations, setter TimeConstant side effect
   и конкретный comparator source. Результат не переносить на Threshold-only Gen.

Все будущие C++/численные сравнения — только owned задания на разрешённых Linux
серверах с неизменяемыми inputs/limits/source, закрытием точных групп и Git-синхронизацией.
Все primary JSON/CSV/models опубликованных результатов сохраняются byte-preserved
в сжатом Git evidence; cache — staging/full-render convenience, не единственный
источник. Никакие jobs/adapter/instrumentation этим документом не реализованы и
не запущены; scientific causality и полная матрица остаются открытыми.


## Привязка конкретной Classic flat LT-панели

[Отдельный metadata trace](ClassicFlatLTMetadataTrace-20261108.ru.md) связывает
три Classic PNG исходного threshold100 отчёта с Git primary cd8d…, actual
compiled Root844/Pulse1f97 и renderer Root360ed…. Сохранённый graph/descriptor
содержит Threshold image, Activity=true, no LTMembrane и восемь LT Inputs links;
точный producer использует Common/direct Potential без fallback0. Per-sample
Ready/Init/actual calculation trace не опубликован; flat_cause остаётся null.
Это локальная metadata/структурная проверка, без новых численных запусков,
изменения графиков или переоценки positive Soma и исторических наблюдений.
