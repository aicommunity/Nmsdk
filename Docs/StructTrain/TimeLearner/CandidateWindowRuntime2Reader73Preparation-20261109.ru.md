# Runtime2 reader: подготовка серверного gate 73

Статус: DOC/JSON preparation, без серверных записей, тестов, native jobs,
сборок и графиков. Dispatch требует review точных request/suite/descriptor
и последующего source/resource preflight. Frozen53/source7352 не изменяются;
его evidence collection принадлежит отдельному агенту.

## Frozen source и suite

Source `1292babb67ee653d04316f7f6927a3d23d5d682c`, code
`a85094b240f93cf4d6f24f917f7b950936a3dcfc`. Новая source projection — только
**643 Scripts files / 9 300 579 Git bytes**, из них 452 Python files,
package fingerprint
`cb44469b00318b7d2c103af0626f77259ba172294b5289b133faa85b90b02d8c`.

Ровно 73 literal AST IDs, без изменения прежних 53 идентификаторов:

| Cohort | Methods | Scope |
|---|---:|---|
| CandidateWindowDataTest | 39 | прежний controlled DATA слой |
| CompositeArchiveAnalysisCliTest | 6 | прежний CLI transport |
| CompositeNativeArchiveTest | 7 | прежние actual A4 archive1 regressions |
| CompositeArchiveActualCliTest | 1 | analyze всех шести actual A4 case |
| CandidateWindowRuntime2DeclarationTest | 10 | отдельный runtime2 codec/binding/warm budgets |
| CandidateWindowWholeArchive2SyntheticTest | 10 | unmocked whole synthetic DATA dispatcher/CLI и tamper |

Точные IDs находятся в `.suite.json`. Mock остаётся только в ранее выделенных
transport controls. Новый whole archive2 слой не использует mock; artificial
graph/XML/clock/waveform fixtures явно DATA-only, не actual native exports и
не archive1→2 upgrade.

Tool остаётся прежним ToolCEC
`cec33f2fcceb8c8f815e3494173bf48dcd39ed6c`, 632 Scripts / Python441, path
`/media/user/Data/TimeLearnerRefactor/source-channel-lt-overview-tool-m40-a2`.
Production `owned_python_job python-validation` работает оттуда; child cwd и
validation imports должны принадлежать новой source1292. `.dependencies.json`
фиксирует 24-file AST import closure; CEC→1292 отличается только forwarding
`TIMELEARNER_COMPOSITE_OUTPUT` в contained_runner, который этот native-free
suite не вызывает как native runner. SDK/submodules/Qt/NumPy не требуются.

## Неизменная fixture и новые пути

Используется прежняя существующая read-only fixture
`/media/user/Data/TimeLearnerRefactor/fixtures-composite-native-a4-git-b4feb-a1`:
157 original files, 74 969 578 B, fingerprint
`78f286701300c7d365e16d25bb64fca430a06b23e08b638396249a87b89056db`, Git
`b4feb38aeed9940c4292b532b3de0e3ab853685e`. Перед/после требуются все SHA;
копировать, распаковывать, менять или создавать седьмой case нельзя.

Все новые paths отделены от frozen53/actual33/metadata19:

```text
/media/user/Data/TimeLearnerRefactor/source-candidate-window-runtime2-reader-m40-a1
/media/user/Data/TimeLearnerRefactor/plan-candidate-window-runtime2-reader73-m40-a1
/media/user/Data/TimeLearnerRefactor/readbacks/s10-candidate-window-runtime2-reader73-m40-a1
```

Suite SHA256
`55fe10aaf2ae4ebc8049d5f2fa2da73167fe8c0087a82df841cbbe2fee85ec1b`.
Request SHA256
`b4cff4487b058aa9703179cf0f1f3a6f1d6a57dd00373ee7e8598c851ed5e76a`.

Memory 2 GiB, tasks32, wall900s, output128MiB, execution free floor512MiB.
Source/plan preparation cap128MiB/free floor768MiB. Kernel limits обязательны;
capacity-null registry отмечается явно, её metadata/общую capacity не менять.

## Preflight и будущий dispatch

Сначала только read-only discovery: M40/Python3.12 identity, ToolCEC HEAD/clean/
Git bytes, fixture157 hashes, canonical roots/три новых paths absent, память
не менее 2GiB+256MiB, диск выше floor+cap, отсутствие конфликтующих write leases.
Существующие native33/metadata19/53 jobs, sources, runtime/build не изменять;
чужие leases не освобождать.

После review source доставляется прежним Git-only private delivery helperv2
только в новый source root, all643 Scripts. Original `.gitattributes`,
`.gitignore`, `.gitmodules` входят в donor ODB, но не материализуются extra
project files. Семь plan docs и flat suite/request берутся только из reviewed
committed Git blobs. Никаких SSH/SCP scientific data или нового launcher.

Перед разрешением единичного запуска сохранить actual source643/Python452 FP,
ToolCEC632, fixture157, plan hashes, resource/own prep lease receipt и отсутствие
job root. Повторить быстрый resource/path check непосредственно до dispatch.
Только затем отдельное authorization Root допускает:

```text
cd /media/user/Data/TimeLearnerRefactor/source-channel-lt-overview-tool-m40-a2 && exec /usr/bin/python3.12 -B -m Scripts.StructTrain.TimeLearner.owned_python_job run /media/user/Data/TimeLearnerRefactor/plan-candidate-window-runtime2-reader73-m40-a1/request.json
```

PASS требует фактические 73 unique log/AST/suite/result IDs, ноль ошибок,
failures/skips, exit0, точный STARTED kernel binding/PID/ticks/cgroup, full tree
closure, освобождённый собственный lease, исходники/fixture before==after.
Transport success не является test PASS. Negative сохраняется без rerun.

## Что 73 не принимает

Этот source исправляет P1 cold7/runtime2 confusion и содержит положительный
whole **synthetic** join. Настоящие service5 original cold7 + owning runtime2 +
archive2 + external primary ещё должны быть получены и независимо проверены
публичным dispatcher/CLI и rehashed tamper. Manual33 DATA не приобретает
выдуманного servicePlan или runtime2. Исторические модель/epoch/P0/C0 family
не переснимаются с trained graph. Whole actual archive2/Train5/cert3 и научная
сходимость не следуют даже из 73/73.

Прежний actual CLI method создаёт/читает шесть reports внутри TemporaryDirectory,
после метода они удаляются. Gate подтверждает consistency/file writes, но не
оставляет retained шесть analysis artifacts. Metadata logs/results/source/
fixture/kernel receipts сохраняются. Primary75MB в evidence не дублируются.
