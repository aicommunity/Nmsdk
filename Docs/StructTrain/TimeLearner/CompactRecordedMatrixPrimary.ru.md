# Компактные первичные данные recorded N4 матрицы

Статус: guards и actual-data export/restore/rescore1/1 приняты; primary28.1MB опубликован в корневом Git. Bundle-only replay на Elder1/1 и полная галерея2/2 приняты;19 опубликованных overview просмотрены. [42 guards](ValidationPlans/M40RecordedMatrixCompact42A1-20261112/PLAN.ru.md) и [actual 16-trial roundtrip](ValidationPlans/M40RecordedMatrixCompact1A1-20261112/PLAN.ru.md) принимаются отдельно. [Полная галерея A2](ValidationPlans/M40RecordedMatrixPrimary2A2-20261112/PLAN.ru.md) повторно запущена с проверенным plotting interpreter после сохранённого A1 backend failure; исходный закрытый Console каталог не менялся.

Поддерживаемый модуль — `Scripts/StructTrain/TimeLearner/recorded_matrix_primary.py`. Перед отбором данных `create_primary` выполняет полный production audit исходной матрицы. Затем существующий `portable_primary` сохраняет исходные байты выбранных файлов в `primary.tar.xz`, с полным member inventory и SHA. Кодек, физика моделей и численные значения наблюдений не меняются.

В пакете находятся полные actual recognition models обеих топологий; внутри каждой модели остаётся полный stopped source с первичными измерениями обучения. Также сохраняются его original summary, все новые observation files, evaluation/execution specs, original signed run manifests, необходимые controller/child joins, source/tool before/after snapshots, raw runtime manifest и исходные XML/CSV Phase A. Повторные standalone copies stopped source, job echoes, build/runtime binaries и производные рисунки исключены. Полная исходная runtime directory остаётся кэшем M40.

`audit_primary` восстанавливает данные в новый отдельный каталог, проверяет каждую выбранную case запись по original run manifest, равенство original before/after hashes модели и исходную матрицу по labels/IDs/ISI. Затем production diagnostic scorer пересчитывает все метрики; результат должен полностью совпасть с original manifests, включая source evidence. Повторного выполнения модели эта процедура не доказывает. Saved closure joins не становятся native attestation; subset явно имеет `complete_runtime_directory=false`, `native_execution_attested=false`, `scientific_verdict=null`. Его нельзя передавать full-directory auditor как исходную рабочую папку.

Команды выполняются на разрешённом worker:

```text
python3 -B -m Scripts.StructTrain.TimeLearner.recorded_matrix_primary create DIRECTORY CONTROLLER RUNTIME_MANIFEST --output NEW_BUNDLE_DIRECTORY
python3 -B -m Scripts.StructTrain.TimeLearner.recorded_matrix_primary audit BUNDLE_DIRECTORY/bundle.json --output NEW_RESTORED_DIRECTORY
```

Оба пути вывода должны быть новыми и находиться вне входных деревьев. Пределы reader: archive128 MiB, expanded768 MiB, member256 MiB, максимум64 members. Для других размерностей/наборов данных этот формат нельзя молча расширять: пределы и проверки пересматриваются явно. Модели остаются остановленными, без certificates; молчание target остаётся FN. Пакет предназначен для повторного анализа научных данных, а не для продолжения посреди пробы или восстановления полного runtime.
