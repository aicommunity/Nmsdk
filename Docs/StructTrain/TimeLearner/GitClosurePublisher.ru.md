# Публикация согласованного Git-дерева

Подэтап 10, ветка stage10/git-closure-publisher. Это инструмент публикации уже
подготовленных commits; полный runner/queue и проверка научной полноты этим
не реализованы. Publisher не создаёт commits, merge или rebase.

## Контракт

Команда:

```text
python3 -m Scripts.StructTrain.TimeLearner publish publication.json --root CHECKOUT --output NEW_RECEIPT.json
```

Spec schema 1:

```json
{
  "kind": "timelearner_git_publication",
  "schema_version": 1,
  "repositories": [
    {"path": "Libraries/Nmsdk-PulseLib", "commit": "FULL_40_LOWERCASE_SHA", "remote": "origin", "branch": "refs/heads/develop"},
    {"path": ".", "commit": "FULL_40_LOWERCASE_SHA", "remote": "origin", "branch": "refs/heads/develop"}
  ]
}
```

Это пример формы, не полный рабочий spec: необходимо перечислить все gitlinks
корня и вложенных сабмодулей, включая неизменённые, с точными commits. Исходный
checkout каждого repo должен совпадать с commit и указанной локальной веткой.
Dirty/untracked файлы запрещены. Receipt/spec держать вне публикуемого checkout.
Receipt резервируется через exclusive create до первого push; прежний результат
не заменяется.

Предварительная проверка обходит committed Git trees рекурсивно. Каждый gitlink
должен иметь единственную запись, совпадающую по SHA; лишний repo запрещён.
Неинициализированный каталог, который Git ошибочно относит к родительскому repo,
отвергается сравнением actual show-toplevel с ожидаемым каталогом.

Список gitlinks должен совпадать с committed .gitmodules. Fetch/push адреса
выбранного remote сверяются с адресом child в .gitmodules. Для одного host/path
допускаются SSH/HTTPS transport формы и суффикс .git; нестандартные порты
остаются частью identity. Относительные submodule URLs пока отвергаются явно,
а не разрешаются по догадке. Все адреса текущего корня абсолютные.

Алгоритм:

```text
reserve common-git-dir publication lock
validate complete local closure and committed remote mappings
for repo in depth-first children-before-parent order:
    revalidate complete local closure
    git push WITHOUT force, WITHOUT recursive implicit pushes
    read exact remote branch tip and compare to declared commit
recheck every published remote branch tip
only then return publication=published
```

Любая ошибка child push, проверки child ref, root push или финальной сверки
даёт publication=failed и process exit 2. Root push не запускается после
ошибки ребёнка. Уже опубликованные commits не удаляются и не откатываются:
это сохраняет историю и позволяет повторить тот же spec. Повторная публикация
неизменённого spec допустима. Если remote branch ушла вперёд, инструмент не
переписывает её историю ради старого tip.

Lock общий для worktrees. Оставшийся после crash lock не удаляется автоматически:
нужно проверить живой процесс и явно восстановить управление. Полный stale-lease
recovery scheduler остаётся отдельной задачей. Межрепозиторной Git-транзакции
нет: последующая внешняя смена remote ref возможна. Финальная сверка фиксирует
проверенное состояние, но не обещает вечную неизменность remote веток.

Receipt означает только доступность объявленных commits. Он сохраняет
scientific_verdict=null. Перед вызовом общий runner обязан проверить runtime,
Train, model transfer, calibration, все trial observations/metrics и обязательные
графические артефакты; publisher не превращает любой Git commit в научный PASS.

## Проверки

Проверяются настоящие временные Git working/bare repositories на workers,
а не monkeypatch subprocess. В baseline e665543d9 прошли 6/6 tests на обоих
workers: child-first order, идемпотентность, actual rejecting receive hooks у
ребёнка и корня, missing/wrong child, dirty tree и существующий lock.
Расширенный source e3a916fab добавляет committed URL checks, перенаправление
child remote и реальную CLI receipt/повторный запрет перезаписи. На обоих
workers прошли 8/8 адресных и 26/26 совместных publisher/runtime/ConditionSpec
tests без skips/failures/errors, все process statuses 0.
Reports: Elder 6b9ba782067637e53a09be84c36af1f8609488a4;
M40 852154adcfe0f1450f137c85a37eafcb54eba229. В каждом пакете локально
проверены все 10 stored / 8 raw hashes, включая декомпрессию. Подэтап
объединён в develop: 1ce9eb6a3390a6f553b81ffa72bde7e285f7f930; полный этап 10 не завершён.

Открыты: внешний production Git server fault matrix, relative URL resolution,
одновременная смена refs, crash/stale recovery, scheduler ownership и сквозная
связь публикации с проверенным RunManifest. Это не завершение этапа 10.
