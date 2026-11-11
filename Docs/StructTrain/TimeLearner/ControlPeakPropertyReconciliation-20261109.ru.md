# Управление и peak policy: ограниченная source-сверка 09.11.2026

Проверены **14 регистраций: семь публичных свойств каждого learner**. Root
`d9d954cd083d716d9347767fee1c15f0da1ecb61`, PulseLib
`f7a0e3e63ec29d4647790a695606d1ca32164ef3`, Rdk
`d6c9df759a3ee20ad42fa0a83841f19385fba60a`. Это чтение immutable Git;
тесты, сборки, серверные команды и модели не запускались.
[Source JSON](ControlPeakPropertyReconciliation-20261109.source.json) содержит
точные header/registration/setter/default/Build/Reset references и fullSHA/blob/SHA256.
Каталог211 не пересоздавался; его исходные evidence statuses сохранены.

## Владельцы и семантика

Все семь — `ptPubParameter`: learner declarations/commands. Сохранённый параметр
не является checkpoint динамики. Эти поля не владеют C/Rm/синапсами/storage
physics; effective граф задают образы, ModelSpec и native edit policy.

| Свойство обоих классов | Default / обычный setter | V1 и V2, Build/Reset |
|---|---|---|
| ControllerVersion | 1; только1/2; changed value запрещён при NativeTrainingOwned; accepted значение ставит Ready=false | Отсутствие поля оставляет1. V1 без native ownership выбирает legacy; explicit native API возможен при1. V2 Build подготавливает declaration, autostart требует Idle+Need и готовый план. Reset версию не меняет. |
| CalculateMode | 0; только0/1; CountIteration=0/IsFirstBeat=true | Политика Need-clear, не Start/outcome. Native Finished в0 пытается снять Need с учётом pending finalization;1 может сохранить true. Direct запись connected-read игнорируется Rdk. Reset режим не переключает. |
| IsNeedToTrain | true; NativeRecognition отклоняет true | Локальный ordinary V2 false→true после ownership очищает intent и ResetControl/probe; следующий Idle tick может начать попытку. Falling setter и активный tick останавливают по false. Connected/direct rising setter не вызывают: Finished не становится Idle. Need не является сертификатом. |
| StructureBuildMode | 1; setter принимает любой int, только value>0 ставит Ready=false | Legacy BuildStructure вызывается лишь при1. Learner0/1 не равны neuron0/1/2. Configured cold construction при отсутствии declaration всё равно требуется. Native fallback mode0 задаёт preserveAllocatedCable, но явная declaration заменяет fallback собственной edit policy. Reset поле не меняет. |
| SyncTolerance | .02s; finite>=0,0 допустим | Legacy gates читают scalar. Typed V2 получает явный search.tolerances.sync; setter не меняет captured plan/Ready и не заменяет допуск timestep/1%. Reset scalar не возвращает к default. |
| PeakMeasureMargin | .06s; finite>=0 | Legacy half-width прогнозного окна. Typed native windows/selection/recipe принадлежат protocol; scalar setter их не переписывает. Прогноз не подтверждает отсутствующий/неоднозначный пик. |
| DelayAgreeMarginMin | .03s; finite>=0 | Legacy floor max(SyncTolerance,DelayAgreeMarginMin) для DelayUseOf; это не финальный residual tolerance. Typed protocol/search владеют отдельными допусками. |

Ordinary Rdk SetData вызывает setter до записи нового локального значения.
Connected чтение получает supplier без learner setter; connected запись
игнорируется. Локальный SetDataDirect обходит setter. ExternalDataSource —
отдельная ветка; фактический публичный путь её активации для данного Need
не установлен. AttachTo/SetPointer не доказывают такую активацию.
[Rdk SetData](https://github.com/aicommunity/Rdk/blob/d6c9df759a3ee20ad42fa0a83841f19385fba60a/Core/Engine/UProperty.h#L705).

## Lifecycle и rising gap

Rdk AfterBuild вызывает Reset. Native BeforeReset сбрасывает transient control,
сохраняя модель; Default/InvalidateTarget — отдельная операция. ResetControl
сохраняет закрытые references и сам по себе не доказывает новую попытку или новый
сертификат. Новый Start очищает прежний certificate. Public lifecycle bool не
является каналом convergence/error; legacy внутренние ABuild false returns
этой сверкой не объявляются исправленными.
[AfterBuild](https://github.com/aicommunity/Rdk/blob/d6c9df759a3ee20ad42fa0a83841f19385fba60a/Core/Engine/UModule.cpp#L147),
[autostart](https://github.com/aicommunity/Nmsdk-PulseLib/blob/f7a0e3e63ec29d4647790a695606d1ca32164ef3/Core/TimeLearner/NativeLearnerLifecycle.h#L60),
[ResetControl](https://github.com/aicommunity/Nmsdk-PulseLib/blob/f7a0e3e63ec29d4647790a695606d1ca32164ef3/Core/TimeLearner/NativeTrainingService.cpp#L379).

PROPERTY-CONTROL-RISING-001 остаётся **open/source-only**.
[Разбор b8e8f08e00a466108c62c6477dd9eb6958b871b1](https://github.com/aicommunity/Nmsdk/blob/b8e8f08e00a466108c62c6477dd9eb6958b871b1/Docs/StructTrain/TimeLearner/PropertyControlRisingRecheck-20261109.ru.md)
не является реализацией restart. Прежняя фраза «V2 rising edge» уточнена до
вызванного обычного локального setter; универсальной supplier semantics нет.

## Peak contract — отдельная декларация

Typed defaults: amplitude_absolute=1e-5, amplitude_relative=0, sync=.02,
minimum_amplitude=1e-6. Первые три принадлежат VerificationTolerances, последний
— protocol/configured declaration. Это не дополнительные одноимённые публичные
learner properties; legacy margin fields автоматически в них не переносятся.

Source cold6/protocol4 composite использует WindowOnly+IsolatedWindow с declared
input windows. Cold7/protocol5 использует initial reference windows и
candidate_window_policy для текущей candidate recipe. Поэтому общее описание
«назначение burst waves» не описывает все V2 методы. Это максимум закреплённого
импульса, не глобальный максимум пачки. Test/scorer response/spikes имеют
отдельный контракт. Наличие schema6/7 в source не означает runtime admission.
[Defaults](https://github.com/aicommunity/Nmsdk-PulseLib/blob/f7a0e3e63ec29d4647790a695606d1ca32164ef3/Core/TimeLearner/FinalVerification.h#L92),
[configured policy](https://github.com/aicommunity/Nmsdk-PulseLib/blob/f7a0e3e63ec29d4647790a695606d1ca32164ef3/Core/TimeLearner/ConfiguredNativeTraining.cpp#L194).

Результат этапов1/12 — актуальные прослеживаемые source-владельцы и ограничения.
Полная property/runtime matrix, restart controls и научный verdict не повышены.
