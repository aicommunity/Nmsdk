# Унаследованные параметры Rdk у TimeLearner

Источник: PulseLib `a18bf543007c52a3ac7a6fbb148a48cb2c351de3`, Rdk
`0a1c1d05a1b12de20feabf54a25712e210865791`. Это адресный source review,
не новая runtime-приёмка свойств. [Машиночитаемые ссылки](InheritedPropertySource.json)
содержат Git blob/SHA256, строки деклараций, constructor/Default mentions и
hash/строки всех выбранных consumer overloads. Производитель — production
`Scripts.StructTrain.TimeLearner.inherited_properties`; он читает только Git.

Обе цепочки: learner → UNet → UItem → UConnector → UContainer → UComponent →
UModule. Девять перечисленных UProperty объявлены в UContainer; промежуточные
заголовки не добавляют UProperty members. Это девять общих контрактов,
действующих на оба learner, а не18 новых собственных learner properties.
Runtime aliases из ClDesc, подключаемые свойства и образцы storage этим
статическим счётчиком не инвентаризируются. Каталог217 остаётся отдельным.

|Свойство|Владелец/единицы и применение|Constructor и public Default|Последствия для эксперимента|
|---|---|---|---|
|Name|UContainer, NameT; SetName, owner lookup, пути связей/диагностики.|Default не назначает фиксированное имя. Setter отклоняет пустое имя, проверяет имя и обновляет owner lookup.|Это идентичность графа/адресация, не научный фактор. Переименование требует проверки связей и semantic model identity.|
|Id|UContainer, UId; SetId, owner component lookup.|Constructor присваивает0; SetId для ForbiddenId делает no-op. Default не генерирует экспериментальный ID.|Нельзя использовать0 как доказательство успешного создания/Build. Проверяется фактический граф, а не bool setter/Build.|
|Activity|UContainer, bool; SetActivity/Calculate/Reset.|Constructor false; public Default не включает Activity явным присваиванием.|false прекращает Calculate до before/children/after hooks. Setter передаёт значение непосредственным детям и вызывает Reset при выключении; это не нейтральное mute и не внешний IsNeedToTrain stop.|
|TimeStep|UContainer, UTime=unsigned int; фактически частота вызовов/Гц. dt=1/TimeStep.|public Default вызывает SetTimeStep(2000). Значение constructor нельзя считать уже выполненным Default.|Setter обновляет OwnerTimeStep/cache, не пересчитывает самостоятельно все физические коэффициенты. SetGlobalTimeStep рекурсивен. Частота задаётся штатно до окончательного Build; effective child physics проверяется отдельно.|
|MaxCalculationDuration|UContainer, signed long long, wall milliseconds; отрицательное значение отключает ограничение.|Constructor и Default: -1.|При RDK_ENABLE_CALC_TIME_CHECKS может остановить оставшийся child обход; CheckDurationAndSkipComponentCalculation имеет собственный путь пропуска. Это меняет вычислительный протокол, не только лог. В проверяемом V2 контуре нужен отдельный запрет/проверка такого ограничения; внешние wall timeouts принадлежат runner.|
|CalculationDurationThreshold|UContainer, signed long long, wall milliseconds.|Constructor и Default: -1.|Диагностический порог предупреждения в Calculate, при соответствующем compile flag. Не является SyncTolerance, model-time budget или условием Exact.|
|Coord|UContainer, MVector<double,3>; координата сети, SetCoord.|Фиксированное экспериментальное значение не назначается UContainer::Default.|Не физическая длина кабеля L и не attach positions. Не использовать как способ структурной настройки нейрона.|
|StepDuration|UContainer, unsigned long long, измеренное wall time в ms; ptPubSysState.|SetActivity обнуляет; Calculate измеряет. GetStepDuration/GetFullStepDuration различаются включением времени детей.|Runtime диагностика, не dt и не научный фактор. Состояние не переносится как evidence сходимости. Наличие состояния в XML зависит от выбранного штатного save mode.|
|DebugSysEventsMask|UContainer, unsigned mask; фильтр событий совместно с Logger.|Default:0xFFFFFFFF; setter применяется штатно.|Логирование может менять wall duration; при включённом MaxCalculationDuration это косвенно меняет пропуски расчёта. Не смешивать такие прогоны как одинаковый вычислительный протокол.|

Точные флаги `ptSysParameter`, `ptPubParameter`, `ptPubSysState` и `pgSystem`
сохранены в JSON. UContainer::Copy копирует ptParameter и отдельно ptState при
copystate, но включает UnInit, Build и CopyComponents. Это не рекурсивный
checkpoint всей динамики; ранее принятые ограничения ModelArchive сохраняются.
Public Default сначала обходит детей, затем выставляет системные defaults и
вызывает ADefault/AfterDefault. После Default нельзя полагаться на прежние
20000Hz или обученную структуру без штатного readback.

## Порядок scheduler и ограничения multirate

В UContainer::Calculate Activity=false даёт ранний выход; неинициализированный
объект также не рассчитывает детей. После проверки Ready и штатного Build
вызывается BeforeCalculate, затем дети, затем ACalculate, затем AfterCalculate.
При равной TimeStep ACalculate один раз; при меньшей дочерней частоте используется
CalcCounter; при большей текущий цикл включает endpoint `>=0`. Поэтому нельзя
объявлять отношение частот точным числом полных проходов дерева: дети и hooks
не повторяются вместе с каждым ACalculate. Новый V2 контур сохраняет uniform
tree; multirate остаётся отдельным compatibility/verification scope.

Build/Reset/Calculate bool не используются как доказательство готовности или
сходимости. Проверяются lifecycle observations, IsReady/IsInit, effective graph,
допуски, специализированные execution/validity/training состояния. Поведение
setter bool не переносится на контракт этих lifecycle методов.

## Что ещё проверить

Нужны реальные inherited-property readbacks на обоих классах, connected
assignments, Activity/Reset/continuation, сохранение в XML/Copy/reuse, различие
глобальной частоты и локальной TimeStep, compile-time duration checks и
MaxCalculationDuration в storage-профилях. Существующие frequency/reset/XML
proofs являются адресными связанными источниками, но не заменяют эту матрицу.
Не вводить per-tick исправляющие присваивания или learner-specific Build chains.
Единообразная физика по-прежнему задаётся immutable storage images.
