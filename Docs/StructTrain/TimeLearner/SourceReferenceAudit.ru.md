# Аудит ссылок на проблемную Elder рабочую копию

Продолжение [диагностики Bin alias](SourceWorktreeIdentity.ru.md). У ранее
использованной `source-n1-measured-refinement-normal-a1/Bin` Git проверял другой
checkout, а в запрошенном каталоге отсутствовали tracked files. Исправление
текущего checkout не подтверждает его прежнее содержимое задним числом.

Production tool `source_reference_audit.py` читает immutable Root Git tree в
`Reports/StructTrain/TimeLearner`, обычные metadata/code/log files и metadata
members primary.tar.xz. Для matching lines сохраняются номера и SHA256,
без публикации произвольного содержимого строк. Отдельно помечаются resource
root references, source bindings в коде, пути в логах и ссылки отчётного текста.
Скрипт не делает checkout и не выполняет исторический код. Каталог/commit
проверяются через native Git, включая соответствие requested repository/toplevel.

```text
python3 -m Scripts.StructTrain.TimeLearner.source_reference_audit \
  --root REPOSITORY --revision FULL_ROOT_SHA \
  --needle source-n1-measured-refinement-normal-a1 --output NEW_AUDIT.json
```

Ссылка на каталог не доказывает actual file reads; отсутствие буквальной ссылки
не доказывает отсутствие влияния. Вычисляемые/escaped имена, CSV и изображения,
вложенные archives, слишком большие/нечитаемые metadata не объявляются
проверенными. Лимит64MiB на blob/member отмечается явно как unknown; oversized
Git blobs дренируются без загрузки целиком. Сведения о source SHA и semantic
model identity должны проверяться отдельно. Scientific verdict не создаётся.

Первый снимок для анализа — опубликованный accepted Root422647a2d. Оба
серверных повтора завершены и побайтно равны: SHA256 полного audit JSON
`c3112045904de2b5abcdcd82aa2d04b41c61d7de09b0c27a40590986e6d7edf4`.
Проверены48882 Git blobs/96506 text entries/206 archives;266 metadata files
содержат ссылки в25 report folders. [M40 proof](../../../Reports/StructTrain/TimeLearner/s02-source-reference-m40-a1/README.md)
e0105c7a3345641c489c9a4bb5d379a208154b05 и
[Elder proof](../../../Reports/StructTrain/TimeLearner/s02-source-reference-elder-a1/README.md)
408e9a06ae4722f9f34bbb7a2245379e0813fb3f сохранены в compact Git. Все report
hashes и полный decompressed audit hash независимо проверены локально.

## Реестр дальнейшей проверки

[SourceReferenceReview.json](SourceReferenceReview.json) разделяет25 folders:

- Два содержат диагностические metadata repair/static review, а не model runs.
- `s07-measured-length-gate-normal-a2` — отдельный fresh native67 gate после
  repair, с проверенным текущим source context. Его нельзя смешивать с прежним
  normal attempt; actual resource reads этим текстовым scan не подтверждаются.
-22 folders требуют адресного dependency/source-claim review. Среди них timing
  controls, loaded/hot/XML readback, archive precision, N1 refinement/handoff/
  calibration, preflight и measured-length controls. Полный список и виды
  ссылок сохранены в JSON; нахождение ссылки не объявляет каждый run неверным.

Точное временное начало alias по историческим metadata не установлено.
Источник ошибки подтверждён поздней непосредственной проверкой; распространять
это наблюдение на каждый прошлый запуск без проверки нельзя. Старые первичные
данные и sealed bundles не переписаны. Source-claim review должен различать
полноту Git worktree, actual loaded code/resources, сохранённый effective model,
реальный протокол и достоверность измерений. Существующие independently matching
ASan traces/model identities остаются самостоятельными доказательствами своего
scope; они не превращают прежний HEAD/status в materialized Bin attestation.

Не прочитаны четыре >64MiB `transaction.json`: Classic-grid и Branch-grid в
обоих `s08-positive-n1-calibration-{normal,asan}-a1/primary.tar.xz`. Их пути и
Git blob IDs указаны явно. Они не считаются проверенными по отсутствию ссылки
в остальных материалах. Полный runtime impact audit остаётся открытым;
scientific verdicts, включая исторические августовские результаты, автоматически
не переклассифицированы. Остальные source names требуют отдельной проверки.
