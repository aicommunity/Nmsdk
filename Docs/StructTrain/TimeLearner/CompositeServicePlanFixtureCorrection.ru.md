# Явная декларация native-пробы в service fixture

08.11.2026. Root-only исправление от `540179d70ddf3764334eb6bb59b7fef691054eee`;
Pulse `f925e37247bb987980fce80da47831a1c31d04c9` не меняется.

Elder normal A2 прошёл все 143 предыдущие проверки и остановился на первом
случае `NativeCompositeService/ClassicCalculateMode0Exact`. Два assertions
сообщают `native_composite_plan_protocol_mismatch`:
ожидаемые CapturingReferences и Exact не наступили. Из 206 случаев выполнены
144: 143 passed, один failed, 62 не запускались. Архивные 23 случая ещё не
выполнялись. Evidence `153751c4b3a3b2c0a25f10540265b41233197f7c` сохраняет
исходную неуспешную попытку; исправление не переоценивает её как успешную.

Причина установлена по исходникам:

- `NativeProbeRequest` по умолчанию имеет пустой `protocolRevision` и
  `ClassicBurst` routing.
- Fixture `NativeCompositeFixture` заполняет specification и ISI в prototype,
  но не задаёт эти два поля request. Прямой actor заполняет их из logical
  request при `StartMeasurement`, поэтому предыдущие 46 core случаев могли
  корректно пройти.
- `ServicePlan` копировал этот prototype. Служба обоснованно проверяет
  согласованность декларации до создания actor; пустой revision не соответствует
  объявленному protocol. Для Branch дополнительно неверен routing.
- Рабочий `MakeConfiguredNativeTrainingPlan` уже явно задаёт оба поля.

Исправление повторяет штатное объявление в тестовом helper: после копирования
prototype задаются `p.probe.routing=p.protocol.routing` и
`p.probe.protocolRevision=p.protocol.revision`. Рабочая проверка согласованности,
пороги, поиск, физика, схемы и смыслы наблюдений не меняются. Идентификаторы
всех 206 случаев сохранены; hash translation unit в трёх inventory рассчитан
по точным staged Git blob bytes.

Приёмка требует реального серверного прохода service случаев и всего набора,
выгрузки фактических шести архивов и независимого чтения primary. На момент
подготовки исправления такого подтверждения нет. Нельзя считать сам факт
устранения ошибки декларации доказательством сходимости или правильности
распознавания.
