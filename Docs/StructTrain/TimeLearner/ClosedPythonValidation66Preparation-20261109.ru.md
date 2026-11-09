# Подготовка metadata66 для штатного closed Python collector

Статус: Git/JSON/AST only, без delivery/dispatch/tests. Source frozen 382180add59275c9c8bcc449a973cc0577015918.
66 literal tests = 28 новых metadata + 15 resource_reservations + 15 resource_budgets + 8 existing_reservations.
Unit fixtures синтетические metadata; реальный40/73 ещё не admitted.

Source637 Scripts/446 Python; FP f4be7a0f06f2e2fd32a67b4035f74c161464c16d365f1c48ae47092f0bd6d329.
ToolCEC отделён от validation source. Request512MiB/t32/240s/output128MiB, fixtures{}.
Owned TMPDIR задаёт существующий worker; writable TEST_DIR не связывается как immutable input.

Новые literal paths под /media/user/Data/TimeLearnerRefactor:
- source-closed-python-validation-m40-a1
- plan-closed-python-validation66-m40-a1
- readbacks/s10-closed-python-validation66-m40-a1

Все ПЯТЬ tracked Git controls входят в ODB и materialized patterns: root .gitattributes/.gitignore/.gitmodules,
LLM/.gitignore, Docs/Audit/TimeLearner-2026-09-26-review/plans/AGENT_PLAN_2026-10-20/tools/cable_model/.gitignore.
Полный точный перечень/bytes/blob/SHA указан в dependencies/source-manifest. Не сокращать его до трёх rootfiles.
Patterns — явные ordered arrays, их сохраняет sorted-key JSON serialization. Canonical LF bytes берутся из Git,
исходные Reports/input bytes не нормализуются. Source snapshot сравнивает ТОЛЬКО637 Scripts; пять controls отдельно.
SDK/submodules не materialized/verified, Git-only projections безalternates/lazyfetch, чужие caches не затрагиваются.

Source/plan пакуются отдельными roots/trees; source остаётся382, plan — следующий docs-only commit.
После reviewed delivery existingV2 нужны только READONLY metadata checks: source/tool snapshots,
проверка637/446/FP, пятиcontrols и6Docs противGit, explicitpatternarrays, AST66 и свежиеpath/capacity/free checks.
Request ссылается ПРЯМО на Git-tracked Docs/StructTrain/TimeLearner/ClosedPythonValidation66Preparation-20261109.suite.json.
Штатный owned_python_job.run получает Git-tracked nested request.json из того же Docs path и выполняет свой полный preflight.
Не создавать flat request/suite copies, excludes, preparation output или prep writer reservation.
Первый control snapshot8fdf5a57019b8415cd0d5c14f94b388a10d86796 сохранён вGit как undelivered/undispatched history;
избавление от flatten dependency не меняет Source382, suitebytes,66IDs или ограничения.
Root reviewed actualreadonlyreadback перед единственным ownedvalidation66 dispatch. Новый CPP/model запуск здесь отсутствует.

После positive66 + exactownedclosure/sourceequality нужен настоящий CLI сбор закрытого40, затем negative73.
Это отдельная приёмка integration; unit gate не доказывает completeprepare/реальныеnested11units или научнуювалидность.
Дополнительные opaqueSQLite/requests/closures/observer files сохраняются с явными ролями; kernel semantics уowningobserver.
