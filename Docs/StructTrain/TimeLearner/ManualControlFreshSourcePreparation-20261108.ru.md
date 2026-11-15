# Новая SDK-копия manual control: фактическая подготовка M40

На08.11.2026 выполнена Git-only доставка **отдельной** SDK-копии
`/media/user/Data/TimeLearnerRefactor/source-manual-control-corrected-m40-a1`.
Root `e11bbd403a5f93790a7ad6c5a245c1964797d63d`, Pulse
`b2878e565febe20a4ba7c9c64536d6e66f672626`, Bin918/Rdkd6; остальные четыре
gitlinks перечислены в evidence. Действующие source/build/runtime A3 не менялись.

Статус — **source preparation, без CMake, native tests и моделей**.
[Независимая metadata/Git-проверка](../../../Reports/StructTrain/TimeLearner/s10-manual-control-corrected-source-preparation-m40-a1/independent-verification.json)
сверила восемь чистых HEAD/gitlinks,4020 материализованных файлов с точными
Git blobs до/после наблюдения и29 реально загруженных SDK Python modules.
Пути импорта принадлежат новой копии; package fingerprint
`d3dd9564a993abc98ee17d7edb793d71a6b09d0e188dcb2c3e8a77e9a5a8ab5f`.
Альтернативных object stores нет. Исходники доставлены Git packs; rsync/scp
для синхронизации не использовались.

Сначала production inventory был снят для четырёх TU:438 source cases.
Затем отдельно включены два pure declarations/proposal TU с54 cases.
Шестифайловый actual source inventory содержит492 IDs: **490 выбранных и два
diagnostic-only**, без duplicates;20 targeted control IDs входят в этот набор.
Все выбранные IDs сверены с точным future-plan commit
`fd787fd8e965ca4894ed212a5520c5a2c3e1fba3`; hashes шести TU совпадают с полной
материализацией. Это **не** compiled inventory и не490/20 PASS.

Полный Scripts tree новой копии, paired unfixed BB1 и ранее проверенного db2
одинаков: `2d49bcd6b0608f60ff57a53acb80310e56ebd9d0`. Code-scoped metadata13/30
переиспользуются по [точной dependency-проверке](https://github.com/aicommunity/Nmsdk/blob/fd787fd8e965ca4894ed212a5520c5a2c3e1fba3/Docs/StructTrain/TimeLearner/ManualControlLifetimeFutureAcceptance.ru.md).
Повтор43 unit checks в каждой одинаковой копии не выполнялся; он не заменил бы
полученную свежую materialization/import/inventory привязку.

Первый observer завершил чтение, но локальный SSH-клиент обрезал большой JSON
из-за ENOBUFS/SIGTERM. Частичный вывод, ошибка и последующее отсутствие процесса
с **точным argv observer** сохранены. Новое read-only наблюдение использовало
тот же source observer со сжатым lossless transport; C++/обучение не
перезапускались. Полные metadata сохранены gzip byte-preserved. Это ошибка
вывода инструмента, не отрицательный результат модели.

[Комплект evidence](../../../Reports/StructTrain/TimeLearner/s10-manual-control-corrected-source-preparation-m40-a1/summary.json)
занимает около2,03MB и содержит11 файлов: сжатые полные наблюдения/инвентарь,
delivery receipts, все hashes, verifier receipt, исходники metadata-tools как
сжатые данные и сохранённый transport failure. Голые executable wrappers в
Reports/Docs не добавлены. Большой несжатый metadata JSON хранить в Git не требуется.

Ограничения source checkout: Docs/Reports не материализованы, Bin содержит
ClDesc/Watch resources; прочие Bin paths явно перечислены как omitted.
Generic delivery-поле `child_gitlinks_not_materialized` относится к моменту
индивидуального checkout; итоговая восьмирепозиторная сверка подтверждает
последующую материализацию детей. Generic `omitted_paths` не заменяет фактические
sparse patterns. Эта копия не является восстановлением всех исторических данных.

Следующий native запуск требует независимого завершения текущего baseline248,
свежего resource preflight, настоящего compiler/cache/generated-flags профиля,
отдельного immutable runtime и нового production canonical job. В частности,
worker требует раздельные source/resources/build/runtime/output/framework paths:
нельзя подставить nested `SDK/Bin` как отдельный resources path. Никакие C++
Ready/Init/действительные waveform, модель, Train→Test, научный PASS или
завершение этапа этим source наблюдением не подтверждены.
