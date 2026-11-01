# Семантический review управляющих свойств TimeLearner

Проверены пять свойств каждого из двух learner: всего10 source reviews.
[Машинный реестр](parameter_control_contracts.json) содержит полные commits,
Git blob hashes и строки деклараций, setters, Default и Reset. Это часть
этапа1, не завершение всего реестра и не10 новых runtime-проверок.

Исходный согласованный root1d4822af22e05b741e4a1c779cf99ba05cb0a1fa,
PulseLib f23d1b8dee908ddfdc549619b754875fc627ce9b, Rdk
027f7f8353608f83b55f3857a2f6c39138df4c65. Файлы классов learner в текущем
N0 feature c25db29404b544311a3256336c0c43991a384e12 побайтно совпадают с этим
PulseLib снимком: N0 изменяет отдельный bounded kernel, не эти setters.
Это подтверждает применимость данного source review к обоим снимкам,
но не расширяет runtime-покрытие старых экспериментов.

## Проверенный смысл

|Свойство|Default|Фактический контракт и ограничения|
|---|---|---|
|ControllerVersion|1|Допустимы1/2. Setter отвергает смену версии при NativeTrainingOwned и ставит Ready=false при принятом вызове.2 выбирает configured native path; отсутствие поля в старом config сохраняет1. Explicit native ownership также защищает граф независимо от выбора версии.|
|ControllerConfiguration|Пустая строка|При version2 — строгая JSON декларация. Setter проверяет владение/активность, но синтаксический разбор происходит в Build. Изменённая декларация после initialized+native declaration отвергается; capturing/searching не допускают вызов setter. Текст не заменяет trained-model archive.|
|ConfiguredModelInitialized|false|Служебный marker с ptPubParameter и ptPubState, без setter. true при отсутствии native declaration вызывает typed отказ от повторного cold build. Само присваивание marker не валидирует модель и не инвалидирует Ready. Не использовать как фактор эксперимента или доказательство переноса.|
|CalculateMode|0|Допустимы0/1. Setter при вызове сбрасывает legacy CountIteration/IsFirstBeat, но сам не перестраивает физику.0 допускает автоматическое снятие локального запроса в terminal состоянии;1 оставляет управление извне. Это отдельная ось от Exact/recognition verdict.|
|IsNeedToTrain|true|Запрос управления, не сертификат. Native false вызывает ExternalStop; false→true локального запроса очищает прежний intent/control/probe transient state. Frozen recognition отвергает true. Generic Rdk binding может обходить локальный setter; native service дополнительно читает фактический запрос на тиках.|

JSON schema1 сохраняет N0 с одним измерением кандидата. Schema2 объявляет
обязательные2..128 N0 repeats; N1 с повторным N0-фактором отвергается. Неизвестные
поля/дубли/недопустимые значения не становятся действующими experiment factors.
Успех setter означает допустимость присваивания в данном контексте, а не
подтверждение применения физического фактора во всех режимах.

## Связь с lifecycle и сохранением

UProperty::SetData вызывает компонентный setter **до** записи нового значения.
Equality check может пропустить одинаковое присваивание вообще. Возврат false
из property setter имеет смысл: UProperty возбуждает EPropertySetterFail, значение
не записывается. Его нельзя смешивать с bool lifecycle Build/Calculate/Reset,
который не используется как доказательство успешного обучения.

Configured Build разбирает декларацию, проверяет topology/effective stimulus/
optional modes и использует native storage/model mechanisms. Повторный Build
обученного объекта не должен превращаться в cold construction по одному marker.
Текст конфигурации и marker не являются mid-probe checkpoint. Для переноса
нужен полный native model package с graph/readback, а не ручные boolean overlays.

Явный native Reset проходит ABeforeReset: сбрасывает временный control/request
intent, а не Default и не обученную структуру. Вложенный Reset под native
lifecycle scope различается с пользовательским сбросом. Hooks не восстанавливают
рассмотренные параметры в defaults; Default явно устанавливает version1,
пустую configuration, marker=false, CalculateMode0 и IsNeedToTrain=true.
Физические потенциалы/синаптическая динамика остаются ответственностью компонентов.

## Владение подключённым значением

В Rdk это разные механизмы:

- Обычный SetPointer/AttachTo задаёт IsConnectedFlag. Локальные SetData и
  SetDataDirect игнорируются; чтение возвращает значение подключённого поставщика.
- Защищённый ExternalDataSource имеет приоритет чтения и пересылает SetData/
  SetDataDirect поставщику. SetDataDirect означает обход локального setter,
  а не универсальную гарантию локальной записи.

В production дереве проверенного снимка присваивание ExternalDataSource
ненулевого значения не найдено. Есть отдельный derived inspection-test exposer;
он не доказывает достижимость такого binding у конкретного IsNeedToTrain.
Поэтому CTRL-OWN-001 в реестре — **source-contract risk с непроверенной production
достижимостью**, а не воспроизведённая ошибка текущих моделей.

При последующей проверке всех terminal/error writes необходимо сохранить
Rdk forwarding contract и ownership поставщика. Нельзя объявлять подтверждённым
сценарий через unsafe cast или менять общий Rdk setter ради learner-specific
обхода. Сначала требуется штатный воспроизводимый путь и native fixture.

## Доказательность и остаток

Существующие [configured controls](ConfiguredNativeController.ru.md) проверяют
часть Load/Copy/default/version/codec поведения; [live pipeline](NativeLiveFinalization.ru.md)
проверяет отдельные mode0/1, stop/cancel и сохранение модели. Это адресные
исторические проверки своих commits, а не полная runtime-приёмка всех10 записей.
Новых численных запусков для этого review не делалось.

source_inventory.json сохраняет свой первоначальный snapshot и pending flags.
Этот реестр не переписывает его историю и не помечает автоматически все
параметры проверенными. Остаются остальные публичные параметры, полный набор
owners/units/setters/defaults/effective readback, все режимы/профили и checks
для каждого действующего экспериментального фактора.
