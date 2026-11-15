# Следующая парная проверка lifetime: состояние подготовки

Статус: исходники подготовлены и опубликованы; сборок и runtime-приёмки этой пары нет. Она не заменяет выполняющийся минимальный baseline A4 и не разрешает менять его исходники.

| Вариант | Root | PulseLib |
| --- | --- | --- |
| Corrected | `7ad96da0e66fe1ef51fc76acb2114174ab6a4e68` | `4b70b0bfb41510691971de86ce5c4993bb382b8b` |
| Deliberate unfixed control | `0530b4e012e18dde3b1053ee3d2bb8692f2e5d91` | `feb6b4bc02768727d1dbb74a397e95a3327ca7f1` |

Root независимо подтвердил, что конечные Root trees отличаются только PulseLib gitlink. В Pulse различаются четыре lifetime implementation-файла и сопровождающий документ; общий `ConfiguredNativeTraining.cpp` имеет одинаковый blob `5b776ac39e2d334e665cde4d82e50db6052d1e00`. Общие cold6/cold7 и execution3 owning-value исправления и codec-проверки одинаковы. Это снимает постороннее различие кодеков при будущей проверке owner-lifetime.

Unfixed получен обычными merge commits с явным сохранением прежних четырёх lifetime implementations из Pulse `800f92ae1f9e0133cefc0ccfe36abc3d8c99727f`. Fixed commits присутствуют в его ancestry; materialized code намеренно сохраняет дефект отрицательного контроля. Эти ветки не являются рекомендуемыми пользовательскими сборками. Общий test TU содержит 342 literal TEST declarations — это исходный перечень, не фактический compiled inventory.

Подробный review, фактический Pulse diff и Git-byte hashes опубликованы в обоих Root snapshots: `Docs/StructTrain/TimeLearner/ColdEnvelopeLifetimePairSourceReview-20261109.{ru.md,json}` и `ColdEnvelopeLifetimePairActualPulseDiff-20261109.patch`. Rebase, cherry-pick, squash и переписывание истории не применялись.

Ранее доставленные на сервер E11/BB1 копии не обновлялись: новые pins ещё требуют собственной materialization/source/canonical проверки. Для deliberate-unfixed разрешены только отдельно подготовленные forensic POS2/NEG1/NEG1 пробы с честным ожидаемым отрицательным outcome. Наличие одинаковых 20 lifetime controls в обоих test TU не разрешает объявить полный R20 на unfixed положительной приёмкой. Полный исправленный набор, научные измерения и merge в develop остаются отдельными незавершёнными действиями.
