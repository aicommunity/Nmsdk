# Общие codec fixes для парного lifetime source-контроля

Статус: source-only подготовка, без сборок, unit/numerical execution, серверных checkout, cache updates или runtime admission. Публичные `main`/`develop`, исходные E11/BB1/Pulse800/b287 и их опубликованные evidence не меняются. Этот документ не разрешает запуск полного R20 на unfixed и не обещает там PASS.

## Парные источники до общего DOC-only слоя

| Вариант | Root code | PulseLib |
| --- | --- | --- |
| corrected | `de8d97fa155eed23da0190f2d56d0a6ed3758e01` | `4b70b0bfb41510691971de86ce5c4993bb382b8b` |
| deliberate unfixed | `3a250198556c549b7265792577b4bf1c9a57f8ca` | `feb6b4bc02768727d1dbb74a397e95a3327ca7f1` |

Ветки в обоих репозиториях: `codex/timelearner-cold-envelope-paired-corrected` и `codex/timelearner-cold-envelope-unfixed`. Общий DOC-only review публикуется на corrected ветке, затем обычным `merge --no-ff` переносится в unfixed с сохранением его Pulse gitlink. Code pins таблицы предшествуют этому общему документационному слою; они уже отличаются только Pulse gitlink в Root. Final branch heads надо фиксировать из Git, не подменять ими исходные code pins в historical evidence.

Unfixed Pulse получен обычным `merge --no-ff` с родителями `800f92ae1f9e0133cefc0ccfe36abc3d8c99727f` и corrected `4b70b0bfb41510691971de86ce5c4993bb382b8b`. Перед merge commit явно оставлены четыре lifetime code paths из800 и отсутствие lifetime doc из800. Это намеренная merge resolution отрицательного контрольного варианта. Она не является утверждением, что fixed commits отсутствуют в ancestry: они присутствуют, а именно эти materialized файлы преднамеренно сохранены в старом виде. Общие codec изменения берутся из того же merge, без копирования отдельных patches, rebase или cherry-pick.

Unfixed Root — обычный `merge --no-ff` с родителями `bb1d24ea950ff068c25f7db7186517b55eef3dbd` и corrected Root `de8d97fa155eed23da0190f2d56d0a6ed3758e01`. После merge сохранён gitlink на unfixed Pulse. Все Root файлы, включая App, Scripts, CMake, документы и весь maintained test TU, совпадают с corrected. Это не metadata-only descendant BB1: помимо общих codecs он получает те же 16 дополнительных lifetime controls и их helpers/docs, что corrected. Изначальные четыре forensic cases сохранены без изменения ID. Из наличия всех20 tests в обоих source TU не следует допустимость полного R20 запуска на deliberate-unfixed варианте.

## Точное materialized различие

`git diff --name-status` Root corrected→unfixed содержит только `M Libraries/Nmsdk-PulseLib`. Раскрытый Pulse diff содержит четыре code paths:

- `Core/TimeLearner/NativeCompositeTrainingAttempt.cpp`;
- `Core/TimeLearner/NativeTrainingService.cpp`;
- `Core/TimeLearner/NativeTrainingService.h`;
- `Core/TimeLearner/NativeTrainingServiceComposite.cpp`.

Пятый Pulse path — `Docs/TimeLearner/ManualControlLifetime.ru.md`, отсутствующий в unfixed и original800. Полный diff corrected4b→unfixedfeb6 побайтово равен исходному diff b287→800, включая все контексты и blob IDs. Каждый из четырёх unfixed code blobs побайтово равен800. Таким образом, deliberate defect не заменён новой реализацией и не смешан с другим физическим/алгоритмическим изменением. При первоначальном сравнении E11↔BB1 пятым **code** path был Root test TU; теперь этот TU общий и больше не является различием парной среды.

Actual patch сохранён в `ColdEnvelopeLifetimePairActualPulseDiff-20261109.patch`. `ColdEnvelopeLifetimePairSourceReview-20261109.json` содержит Git-byte SHA256 каждого code file, исходного800, общего ConfiguredNativeTraining encoder, общего Console header и всего общего test TU. SHA вычислены по `git show`, а не CRLF workingtree. Общий test TU:342 literal TEST; это source inventory, не захваченный compiled binary inventory.

## Source review и границы

Corrected guard наблюдает private nonserialized owner-control lifetime; service takeover/reset/interrupt его инвалидирует, включая публичный interrupt без stored composite. Unfixed оставляет прежнюю проверку чужого активного service и прежние lease factories: после чужого `Begin→Finished` старый manual actor не получает новой token-проверки. Это и есть сохранённый negative-control дефект. Общие Need/lifecycle/model/readback/deadline guards, callbacks, budgets и portable DATA validation не удалялись и не подменялись.

Обе стороны получают одинаковый cold6/cold7 owning-value encoder и одинаковый execution3 wrapper fix. Объектный и serialized-byte codec tests одинаковы, decoder остаётся строгим. Нет coercion, смены assignment/math/CapturedPerInput/referenceN−1/tolerances, изменений физики/моделей/defaults или выдачи новых сертификатов. Ранее добавленные historical implementation/inventory docs интерпретируются по указанным в них source pins; само их присутствие на unfixed ветке не утверждает наличие исправления в его четырёх production blobs.

Для будущего парного runtime остаются отдельные prerequisites: независимая проверка baseline отрицательного evidence, actual Git/source/materialization/same-SDK/canonical capture, проверка closed kernel/resource/lease границ и отдельная санкция root на выбранный cohort. Подготовка этой пары не заменяет baseline A4, full248, additional candidate-window gates или forensic разделение unfixed POS2/NEG1/NEG1. Никаких runtime результатов здесь нет.
