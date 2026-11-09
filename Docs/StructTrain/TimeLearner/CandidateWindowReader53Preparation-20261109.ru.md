# Reader2: подготовка серверного gate 45 DATA + 8 actual-bound

Статус: только DOC/JSON source preparation. Серверные команды, создание source
projection, сборки, тесты, native jobs и графики не выполнялись. Dispatch
требует отдельного review Root этого точного descriptor/request/suite.

## Неизменные источники и входные данные

- Code `ef5ba0aad470e2bbcc05f3d078d45785415992c1`, frozen source
  `7352f62bfd77ea86606845866a06bab7400454a3`.
- Новая read-only validation source projection:
  `/media/user/Data/TimeLearnerRefactor/source-candidate-window-reader2-m40-a1`.
  Только все **640 Scripts files / 9 260 973 Git bytes**; SDK/submodules не
  материализуются. В пакете 449 Python files, fingerprint
  `46b93a6f59995d9c4c9cabd258d46481248d0d59d8ad3142ea23a046827cd45c`.
- ToolCEC `cec33f2fcceb8c8f815e3494173bf48dcd39ed6c` остаётся в существующем
  `/media/user/Data/TimeLearnerRefactor/source-channel-lt-overview-tool-m40-a2`.
  Его production `owned_python_job` выполняет `python-validation`, а child
  validation импортирует модули из новой source7352 по собственному cwd.
- Fixture остаётся в
  `/media/user/Data/TimeLearnerRefactor/fixtures-composite-native-a4-git-b4feb-a1`:
  **157 files / 74 969 578 B**, fingerprint
  `78f286701300c7d365e16d25bb64fca430a06b23e08b638396249a87b89056db`.
  Это прежние шесть actual A4 exports из Git
  `b4feb38aeed9940c4292b532b3de0e3ab853685e`. Никакой распаковки, копирования,
  исправления или перегенерации fixture не планируется.

Семь существующих actual tests уже отдельно приняты на CEC evidence
`1f1e8a5ef47abd4d7d644748ddc5a8624f3f0e75`. Это позволяет повторно использовать
неизменный production adapter и unchanged fixture; новые source/import/suite
bindings и новые 45+1 tests требуют свежих проверок. Tests не заменяют
выполняемый worker source snapshot и actual fixture before/after snapshot.

`.dependencies.json` содержит AST-only static local import closure production
adapter: 24 файла. Между ToolCEC и source7352 из этой closure отличается только
`contained_runner.py`: source7352 дополнительно пропускает
`TIMELEARNER_COMPOSITE_OUTPUT`. Source53 не вызывает native runner; фактический
owned job использует неизменный ToolCEC implementation. Это различие не
скрывается blanket утверждением о тождестве всех зависимостей.

## Suite и request

В одном maintained suite ровно 53 literal IDs, полученные из Git/AST:

| Класс | Число | Scope |
|---|---:|---|
| CandidateWindowDataTest | 39 | controlled arithmetic/graph/proposal/context/geometry/ledger DATA |
| CompositeArchiveAnalysisCliTest | 6 | CLI transport/malformed/strict originals/output guards |
| CompositeNativeArchiveTest | 7 | прежние actual archive1 regressions на шести A4 case |
| CompositeArchiveActualCliTest | 1 | production analyze для всех шести case, явная measured coverage |

Mock применяется только в отдельных CLI transport controls и не выдаётся за
положительный archive2 replay. Controlled waveform/graph fixtures — DATA-only.
Native execution, convergence, certificate или новый научный результат этим
suite не подтверждаются.

Request: `s10-candidate-window-reader53-m40-a1`, M40, memory **2 GiB**, tasks
**32**, wall **900 s**, minimum free **512 MiB**, output cap **128 MiB**.
Source/plan preparation cap **128 MiB**, free floor **768 MiB**.

Suite SHA256:
`7f646fae0412405860ebae9769475821debd8900320e30630669b57e9f6e14ab`.
Request SHA256:
`81d81bdc7ddb960e5ce59dc8d128214745a33843dd6449b812240a5ed959c2b9`.

Новый plan root:
`/media/user/Data/TimeLearnerRefactor/plan-candidate-window-reader53-m40-a1`.
Новый единственный job root:
`/media/user/Data/TimeLearnerRefactor/readbacks/s10-candidate-window-reader53-m40-a1`.
Suite/request должны быть материализованы как `suite.json`/`request.json`
побайтно из reviewed committed Git blobs. Новый launcher/API не нужен.

Будущая команда после review/preflight/authorization, ровно один раз:

```text
cd /media/user/Data/TimeLearnerRefactor/source-channel-lt-overview-tool-m40-a2 && exec /usr/bin/python3.12 -B -m Scripts.StructTrain.TimeLearner.owned_python_job run /media/user/Data/TimeLearnerRefactor/plan-candidate-window-reader53-m40-a1/request.json
```

Собственные production supervisor/process/validation logs остаются
авторитетными. Shell redirect, новый wrapper, generated program и внешняя
таблица fake CanonicalSpec не добавляются.

## Обязательный preflight до любых новых записей/dispatch

1. Проверить M40, точный Python 3.12 executable/runtime, canonical absolute paths
   и отсутствие трёх новых source/plan/job roots. Существующие A4/future33/
   metadata19 source/runtime/build paths не затрагивать.
2. Проверить HEAD/clean state ToolCEC и Git bytes всех materialized Scripts;
   сравнить с прежним accepted tool snapshot. Никаких global registry metadata
   changes, releases чужих leases или capacity adjustments.
3. Read-only проверить fixture157: все regular files без symlinks, каждый
   byte hash и aggregate fingerprint из исходного Git manifest. Не считать
   старый PASS заменой свежей snapshot; не читать waveform математику в prep.
4. Проверить свободную память не менее 2 GiB + 256 MiB; диск не менее execution
   floor + output cap, отдельно preparation floor 768 MiB. Capacity-null
   registry фиксировать как ограничение; kernel limits остаются обязательными.
5. Проверить отсутствие конфликтующих write leases для новой source/plan/job
   и наличие read ownership для ToolCEC/fixture. Native metadata19/future33
   jobs не останавливать и их sources не обновлять.
6. Только после review материализовать новую Scripts-only source из Git7352
   штатным existing private delivery helper. В donor ODB должны быть original
   root `.gitattributes`, `.gitignore`, `.gitmodules`; они не материализуются
   как extra checked-out project files. Source manifest содержит все object IDs.
7. Проверить source HEAD/status, все 640 materialized Scripts Git bytes,
   package449 fingerprint. Сохранить same-source import origin без выполнения
   тестов; validation loader/import admission дальше обязан подтвердить source7352,
   не соседний ToolCEC. Подготовить только новые reviewed plan files из Git blobs.
8. Перед единичным dispatch повторно сверить request/suite hashes, fixture
   fingerprint, root bounds, доступные ресурсы и отсутствие job root.

## Acceptance и предел доказательности

PASS требует точные 53 executed IDs, zero failures/errors/skips, exit zero,
binding actual worker PID/start ticks/cgroup, полную tree closure и освобождённый
собственный lease; source/fixture до и после должны быть тождественны.
Запущенный/успешный transport сам по себе не PASS. Negative attempt сохраняется
неизменным; никаких автоматических reruns.

CLI method пишет и повторно читает шесть отчётов **внутри TemporaryDirectory**.
Они затем удаляются штатным тестовым cleanup. Этот gate подтверждает
production CLI consistency/file writes, но **не сохраняет шесть report artifacts**
после test method. Unit logs/result, source/fixture snapshots и accounting
сохраняются production worker. В первичные 75 MB ничего не дописывается.

**Даже 53/53 не принимает whole archive2.** В frozen7352 известен отдельный P1:
`candidate_window_archive_evidence.py:294` проверяет runtime plan через
`validate_protocol→configuration_view`, ошибочно ожидая cold7 shape. Настоящий
runtime1/будущий runtime2 имеет отдельный codec/ownership. Дополнительно current
future33 service5 producer выдаёт `runtime-plan-scope.json` с
`runtime_plan2_exported:false`, а не genuine `runtime-plan.json`.

Эти два joins требуют отдельного source-reviewed owning runtime2 export,
dedicated strict Python runtime2 validator/protocol+budget binding и настоящего
service5 whole archive2 dispatcher+CLI positive с coherent rehashed tamper.
Manual33 archives остаются DATA, без выдуманного servicePlan/cold7/runtime2.
Копирование cold7 в runtime plan, восстановление из index claims, archive1→2
upgrade и ослабление file loader запрещены. До такой проверки source7352
не вливается в main и archive2/Train5 acceptance не объявляется.
