# Целостность современных pipeline archives

Найден отдельный дефект упаковки: verify_packaged_run_closure принимал только
run-manifest schema1 и операции Train/export/evaluate. Текущие native preflight/
Train имеют schema2, diagnostic-evaluate — schema3, contained операции — schema4.
Их полные первичные данные нельзя отклонять как неизвестный старому упаковщику
формат. Это дефект inclusion gate, а не новое доказательство качества моделей.

Подготовлен общий фикс в artifact_bundle.py:

- Прежний byte-map API использует один verifier hash/size inventory.
- Native schemas1..4 связаны с допустимыми операциями: schema3 только diagnostic,
  остальные кроме4 не выдают diagnostic за обычный Test. PostTune/calibration
  сохраняют прежнюю schema1; неизвестные/bool версии отклоняются.
- Cold Train/preflight и cold probe не получают imported source. Export/evaluate/
  diagnostic и source-based probe обязаны сохранить фактический source package.
- Manifest bytes связаны с реально посчитанным inventory; полное множество его
  artifacts сохраняется. CSV повреждение, потерянный input/source, незаявленный
  файл и неизвестная операция не допускают положительного inclusion proof.
- verify_pipeline_archive потоково читает существующий архив без extraction:
  сверяет outer SHA/size, все regular members, пути, отсутствие дублей, byte/hash
  каждого файла и все вложенные run inventories. Общий лимит8GiB и manifest16MiB;
  все CSV одновременно в память не загружаются.

Эта проверка не заменяет audit_run_manifest, свежий kernel closure/released lease,
source provenance, validity измерений и TrainingCertificate. Полный архив честного
отрицательного процесса также может быть целостным; научный verdict всегда None.

Семь серверных проверок подготовлены на шести настоящих producer snapshots
schema1/2/3/4 из трёх уже опубликованных Git archives. Точные refs/blobs и member
prefixes: Scripts/StructTrain/TimeLearner/specs/packaged-pipeline-archive-fixtures-v1.json.
Исторические источники не запускаются, новые модели не рассчитываются, исходные
архивы повторно в Reports не публикуются. Тестируются оба API, streaming,
source filtering, повреждения, unknown schema/operation, links/duplicates/
traversal и extraction budget. Серверная проверка этого фикса ещё ожидается.
