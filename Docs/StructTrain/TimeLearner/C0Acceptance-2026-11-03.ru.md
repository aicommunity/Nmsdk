# Адресная приёмка C₀, native edits и переноса модели

Принят explicit API исходных ёмкостей и completed/stopped transfer. Это
подэтапы4/5/7, не выполнение полных этапов и не включение bounded C-trim V2.

Это запись приёмки именно explicit API. Последующие source/archive и parser
исправления приняты отдельно: [текущий статус](CurrentStatus-2026-11-02.ru.md).
Автоматическое владение C₀ проверяется в отдельной ветке:
[контракт и текущая приёмка](CapacitanceOwnership.ru.md). Его normal8/readers19
не заменяют ещё выполняющиеся ASan, transport и визуальную проверку.

## Проверенная реализация

- PulseLib tested commit `69d463aa50144a1c8ddb4a674bb900c2a07e769f`,
  Core tree `39f2d24f1775f7b800948e4506cafb0da95f6ecf`.
- PulseLib develop merge `5cbb877bbabaab88f4bf7bb04e4c846598744884` сохраняет
  этот Core без изменений; добавлены только уточнения приёмки в документах.
- Rdk tested commit `48d6548e46f3310537a2d8b59fb5be553307a54f` и develop merge
  `a62393f7791cc4ad10d1c2c11f255b3db3334f89` имеют одинаковый Core tree
  `b204ef8da698476898394aa1d5b6a2679e5a91ed`.
- Root runtime/scorer/tests — `6db2d5156fe51e03e1ebdeb1c256c5010dadb9b7`.
  Между ним и принимаемой C₀-веткой нет изменений App/Scripts/Tests;
  CMake test switch ранее принят отдельно в root develop d12c50a6.
- Bin и другие gitlinks не меняются. Remote develop обоих изменённых children
  проверены до публикации корня. История сохраняется через merge commits.

## Изменение поведения

Bound baseline schema2 хранит исходный граф, неизменяемые storage definitions,
индивидуальные C₀, статическую физику каналов и происхождение новых каналов.
Рост получает C₀ из проверенного образа; текущие обученные C не заменяют
исходный baseline. Совместные L/Ns/Rs/C edits проходят native preview,
полную проверку и commit/rollback. Ошибки Build/Reset/Calculate проверяются
через состояние и operation diagnostics, а не их интерфейсный bool=true.

Completed/stopped schema2 включает полный физический архив и capacitance_state.
Import проверяет приватную модель до замены живых детей. Оба learner удерживают
импортированную карту для повторного export. Schema1 остаётся читаемой;
отсутствие C₀ означает unknown provenance, а не доказательство отсутствия trim.

## Доказательства

| Проверка | Фактический результат | Root evidence commit |
|---|---|---|
| Normal transfer |9 unit,14 native PASS; исходный reader failure сохранён|`57383f8d93ebf660bd2f80d08ac315a67abe2896`|
| Исправленный independent reader|24/24 на прежних primary, включая growth-only dependency mutation|`b7b2d5d0a15e281da503d0b5af076d03e072f21f`|
| Combined ASan|9 unit,35 native,24 readers PASS; actual libasan mappings|`780b21afcd6e9d477bc7eb8181217c5a655fa0df`|

ASan35:8 bound C₀ Classic/Branch × N0/N1 ×2000/20000Hz,6 joint/rollback,
3 operation diagnostics и14 completed/stopped/frozen/fresh-process transfer.
Все766 members ASan bundle и5 367 892 compressed bytes проверены по SHA256;
normal/reader bundles также проверены. Primary лежат в Reports/StructTrain/
TimeLearner/s05-capacitance-state-normal-b3, s05-capacitance-state-readers-b5 и
s07-capacitance-combined-asan-c2. Ранее принятые selected C₀ waveforms сохраняются.

## Границы и незавершённая работа

Positive completed fixtures явно задают SyncTolerance=0.2. Они проверяют
перенос, не сходимость при default0.02 и не классификацию. Внутри fixture
roundtrip/rollback/frozen responses проверены. Между normal14 и ASan35 совпали
non-time columns118/122 общих CSV;4 waveform различаются при разной model-time
предыстории старого dataset. Полная cross-inventory эквивалентность не доказана;
clock-origin defect и следующий source fix находятся в отдельной ветке.

Не приняты automatic C₀ ownership последующими edits, C-trim search, native
XML/Copy persistence correction map, mid-probe checkpoint, вся physics/mode
матрица и научные эксперименты. SyncCapacitanceTrim On для V2 остаётся запрещён.
Дополнительные archive telemetry и dataset clock изменения в этот merge не входят.
Исходный план0–12 остаётся активен; полностью принят только этап0.
