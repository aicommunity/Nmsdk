Принято06.11: оба workers прошли production migration220 и restored-path negative без receipt. Все17 primary members и284 source hashes каждого worker сверены. Bin merge `3d5fc67c33f7be9ad3806db0b00b9d92588049bb` опубликован и имеет ровно проверенное tree4123c177. Data Elder `bcb532b4c044827646670766874ff800c568ff36`, M40 `45723a5242810d8da50c41eae6453239802e8e70`. [Сверка](AsymRmOverlayRetirementVerification.json). Ниже сохранена постановка до приёмки; весь этап9 остаётся частичным.

# Исторические AsymRm XML overlay/cold/warm инструменты

Подготовлено06.11.2026, серверная metadata-приёмка ожидается. Это отдельный
подэтап9, не изменение алгоритма обучения и не завершение миграции.

Исходный Bin commit `f12f09ae1f7fc0a9af1d99be86d3a4002a3cf4aa`, каталог
`Configs/SpikeSamples/StructTrain/SelectivityAsymRm/scripts`. Пять прочитанных
целиком файлов удалены без wrappers; source snapshot/blob/bytes/SHA256 и
команды извлечения добавлены в `script_migration.json`. Всего220 записей:
218 retired+2 moved; complete=false. [Source review](AsymRmOverlayRetirementReview.json).

| Исторический инструмент | Прочитанное поведение и решение |
|---|---|
| cold_patch_dspan.py | Cold-reset выбранных XML с четырёхэлементными L/Rs/references, neuron class и scalar DissociationTC/default overrides. Не переносить повторные записи общей физики в learner: задавать native storage profile и объявленное начальное состояние. |
| warm_start_l.py | Raise-only L для выбранных первых трёх входов через regex parent tag. Новое продолжение требует полного boundary-state import и инвалидирования измерений; корректность модели не определяется L>1. |
| patch_test_model.py + inject_analyzer.py | Whole Train Model copy в Test, фиксированные Dataset/LT/analyzer links, ручная Links Size. Исторические отчёты уже предупреждают о transient Dataset connectors/fire_all. Оба файла удаляются вместе: inject импортирует patch_model, других code consumers не найдено. Native frozen observations обходятся без такой правки Test XML. |
| merge_train_weights.py | Фиксированный список XML tags плюс правки Need/BuildMode; не передаёт произвольный storage/graph/links и индивидуальную физику. Не сохранять это как альтернативный transport: новые задания используют полный native export/import и semantic readback. |

Полный textual caller search выполнен в tracked root Scripts/Apps/Tests, Bin и
PulseLib Python/shell/CMake. Вне этой группы code consumers не найдены; поиск
не доказывает отсутствие произвольных внешних пользователей. Три исторических
Bin отчёта получают только добавленный prefix с retrieval и новой областью
применимости. Исходные тела, все модели/конфиги/данные и прочие blobs сохраняются.
Старые научные выводы не пересчитываются. СерияD не возобновляется.

После этой группы остаются24 Python-файла AsymRm; специализированные анализаторы,
reference/seed/guard helpers требуют отдельного разбора. Весь limited Bin inventory
уменьшается с131 до126, но это не полный глобальный inventory.

До merge children-first в develop нужны production history verify-migration220
на обоих workers, restored-path negative без положительного receipt, exact Bin
5 deletions+3 prefix-only docs и сохранность всех остальных blobs. Native/numerical
группы не требуются: старые скрипты не запускаются. Проверки metadata-only должны
соблюдать действующие worker limits; занятый Elder slot не освобождается принудительно.
[Полный model transport](NativeLearnedState.ru.md), [native construction](NativeModelBuilder.ru.md).
