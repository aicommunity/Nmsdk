# Git publication: замыкание commits и объявленных артефактов

`Scripts/StructTrain/TimeLearner/publisher.py` сохраняет schema 1 для прежних
callers: только точная children-first Git closure. Для новых публикаций schema 2
добавляет обязательный непустой массив `artifacts` и явный `push_url` каждого
repository record. Остальные поля repository record прежние: `path`, полный
`commit`, `remote` (имя fetch remote), `branch` (`refs/heads/...`). Нужно перечислить
все рекурсивные gitlinks, а не только изменившийся PulseLib/Bin.

Каждый artifact set имеет точные поля:

```json
{
  "repository": ".",
  "manifest": "Reports/StructTrain/TimeLearner/RUN/SHA256SUMS.json",
  "manifest_sha256": "<64 lowercase hex characters>"
}
```

Manifest — UTF-8 JSON map `relative/file → sha256`, относительно его собственного
каталога. Запрещены повторяющиеся ключи, traversal, symlinks/gitlinks вместо
regular blobs, самоссылка manifest и неизвестные поля artifact set. Publisher
читает manifest и каждый указанный файл из точного commit, сверяет SHA256
потоком и отказывает до первого push при отсутствии хотя бы одного файла.
Ignored PNG в рабочем каталоге не заменяет отсутствующий committed blob.
Локальные `git replace` не меняют проверяемое содержимое исходного commit.

`push_url` должен указывать на тот же repository, что fetch remote и committed
`.gitmodules`; разрешается другой транспорт, например HTTPS для чтения и
`git@github.com:aicommunity/Nmsdk.git` для push. Remote configuration не меняется.
Пароли/token userinfo в URL не допускаются. Push выполняется без force, children
сначала; root и итоговая повторная проверка всех refs обязательны. Schema 2
receipt перечисляет `artifact_sets_verified`; scientific verdict остаётся null.

Для producer есть `stage_artifact_set(root, manifest_path, manifest_sha256)`.
Он сначала проверяет реальные файлы и inventory, затем добавляет **только**
перечисленные пути и сам manifest через literal NUL pathspecs с `--force --sparse`.
Это разрешает явно выбранные ignored изображения, не добавляя весь cache.
После add сверяются staged bytes; helper не создаёт commit и не публикует.
Если Git filters/line endings меняют байты, helper отказывает и оставляет index
для проверки. Автоматически продолжать commit/push после такого отказа нельзя.

Эти проверки не доказывают полноту самого объявленного inventory, валидность
primary schema, присутствие всех trials внутри архива или научный результат.
Это остаётся обязанностью production auditors/packager до подготовки публикации.
Первоначальные ad hoc публикации с sparse/HTTPS ошибками не становятся
испытаниями нового publisher задним числом. Его интеграция во все producers,
очереди, lock recovery и полная приёмка этапа 10 остаются открытыми.

Добавлены реальные Git fixtures для schema 2 и сохранены проверки schema 1.
Серверные результаты должны быть записаны отдельно после выполнения тестов;
наличие этого документа не означает, что они уже прошли.
