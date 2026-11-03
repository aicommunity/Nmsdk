# Адресная приёмка C₀, native edits и переноса модели

Принят explicit API исходных ёмкостей и completed/stopped transfer. Это
подэтапы4/5/7, не выполнение полных этапов и не включение bounded C-trim V2.

Это запись приёмки именно explicit API. Последующие source/archive и parser
исправления приняты отдельно: [текущий статус](CurrentStatus-2026-11-02.ru.md).
Автоматическое владение C₀ проверяется в отдельной ветке:
[контракт и текущая приёмка](CapacitanceOwnership.ru.md). Подтверждённый ownership/transport scope normal43/readers26 и ASan43/readers26
описан ниже. Новые witness/service/schema3 и C-search остаются отдельной работой.

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


## Отдельная приёмка automatic C₀ owner/transport, завершение G3

Приняты только поведение Core30495d143795022ad444bf290d2ac30b7e140199 и заявленный
corpus43. Pulse develop merge027070e8e1181380427edc9384641d08ed9943be опубликован;
его Core побайтно совпадает с tested30495, дополнены документы.

| Проверка | Источник и результат | Проверенная публикация |
|---|---|---|
| Normal numerical |root496a80d7190cafcc1e96329ee3c8e2b17cb40114;43/43 PASS|ccfa43c1fea90567574aa3061eaa2a902c37710d;1062 members|
| Corrected normal readers |rootc63d1b7b9c08c7542398ca944bcc7cf22e5ea2b4;26/26 PASS|7ec395554f0f8d506c08b587ba130025d0af1719;11 members|
| ASan numerical/readers |тот же rootc63d1b7b;43/43 и26/26 PASS|82f205d733dc64513ff3dd22ede7df3f9ab7a445;1073 members|

Normal compiled C++/CMake/gitlinks между496a80 иc63d1 не менялись: исправлялся
реальный nonunit negative control в Python. Исходный failed-reader verdict не
переписан. ASan повторил native suite наc63d1; actual loaded-files подтверждает
libasan.so.8 (SHA2568d5845bdf056b5db4cfb9fff40ad5eeea8f6da05a8ca6f5935a7d1c138ed2558).
detect_leaks=0, отсутствие утечек не заявляется. Все archive members сверены локально.

Scope включает Classic/Branch N0/N1,2k/20k native edits, automatic ownership,
R bounds, joint C, rollback, active/dormant history, same/fresh-process completed
и stopped transfer и frozen responses в этих43 tests. Каждый вход остаётся целью
CapturedPerInput; общая амплитуда A* не вводилась, tolerances не изменялись.

Root acceptance сохраняет Rdkacc3de8d, актуальный к началу объединения. Отличие от
tested a62393f7 ограничено пятью Docs paths; Core/Deploy/прочие compiled sources
совпадают. Bin39d811e5 и остальные children не меняются. После child-first push
корень фиксирует точные gitlinks; fresh recursive checkout подтверждён отдельно ниже.

Это подэтапы4/5/7, не закрытие полных этапов. Profile/mode/dimension matrix,
multirate, новая public binding/witness API, tracked service/model schema3,
C-search On, весь PostTune/calibration pipeline и научные эксперименты не принимаются
этим corpus. Визуальные материалы ownership имеют отдельные source scopes и полный
cache на M40; selected figures не означают visual acceptance всех будущих моделей.
Version2 не объявляется рекомендуемой по всей матрице, научного verdict здесь нет.


### Опубликованная closure automatic owner

Root develop merge0a495cefe72778d9ffb74d1cc51990d0dda611e6 опубликован после
Pulse develop027070e8e1181380427edc9384641d08ed9943be. Fresh shallow recursive
checkout на M40 завершён из origin, все7 children совпадают с gitlinks и чистые.
Evidence17a4f61dee84743ede1e9d42ab4157336f4754c1:9 checksummed payload files,
включая closure, recursive status и Core trees. Pulse Core76eca8256da2588f7d5327e33ea0a5ee3259c8f2
совпадает с tested30495; Rdk Coreb204ef8da698476898394aa1d5b6a2679e5a91ed — с tested
а62393f7. Это подтверждение source closure; новая numerical сборка не заявляется.
Последующий merge этих receipts/docs не меняет принятых child pins или источников
App/Scripts/Tests. Полный план и ранее перечисленные ограничения остаются открытыми.
