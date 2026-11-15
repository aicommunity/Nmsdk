# Равномерный обход геометрий N1 — кандидат

Основание: [проверенное покрытие stock](SearchCoverageReview.ru.md) показывает,
что geometry-major обход всех Rs способен исчерпать invalid allowance на двух
длинах. Это не numerical bug/PhysicalInfeasible, но текущий порядок не даёт
широкого покрытия L до локального бюджетного stop.

Подготовлен отдельный вариант в BoundedTrainingSession::NextDomainCandidate.
Он действует только при native dynamic domains, N1 TipResistance и явно
включённом AdvanceUnassignedBurst. Default RetrySameCandidate, N0 и standalone
static domains сохраняют прежний порядок. Схемы конфигурации не меняются:
порядок алгоритма определяется точным code SHA; прежний stock replay использует
свои неизменяемые исходники/runtime, а не новый код с той же declaration.

```text
keep existing initial-candidate shortcut
for each C context independently:
    after issuing a domain candidate, yield to next geometry/Branch variant
    obtain a fresh effective domain for that geometry
    issue its next unvisited legal Rs within the actual current bounds
    retain the original scope + full-parameter deduplication
    after the last geometry:
        if this pass issued nothing: cursor exhausted
        else restart at first geometry for remaining Rs
```

Нельзя вычёркивать остальные Rs после первой invalid wave. Полный конечный mesh
остаётся достижимым, если хватает исходного candidate/probe/edit/invalid budget.
Fresh domain assessment обязателен при каждом возврате; старый интервал не
сохраняется как действующий. Модель/измерения по-прежнему revision-bound,
anchor измеряется заново, missing peak не превращается в valid observation.
У shared Branch сохраняются attach order, paired-bank legality и referenceN−1.

Два служебных флага — yield pending и issued-anything-in-pass — входят в
CandidateCursor, включая его suspended copies для C contexts. После BeginInput
они сбрасываются. Пустой pass означает лишь отсутствие оставшихся кандидатов
cursor, а не физическую недостижимость. Общие бюджеты/final certificate gate
и критерии CapturedPerInput не меняются.

Подготовлены4 production-controller/ProbeRecorder checks:

1. Default geometry-major против opt-in interleaving; обе последовательности
   действительно измеряют все9 пар3L×3Rs до честного отрицательного final result.
2. Allowance2: три actual invalid observations посещают три геометрии, последний
   получает InvalidBudgetStop; certificate отсутствует.
3. Повторный domain read меняет low/high: дальнейшая проба обязана использовать
   новый интервал. ExternalStop до restore-best отделяет эту проверку от
   отдельного контракта исторического best при изменённой физике.
4. Branch: допустимые полные векторы, совпадающие физические банки, fixed
   reference и несколько geometry variants.

Это ещё не серверная приёмка. Требуются normal gate, adjacent/default controls,
адресный ASan, native C-context/mode checks и отдельный stock A/B. Улучшение
классификации или сходимости не обещается. Новые ветки созданы от develop с
явными no-ff merges pending recovery prerequisites; это не promotion этих
prerequisites в develop. Активный renderer/старые runtimes не изменены.

Следующая отдельная проверка `CapacitanceContexts/
FairN1TraversalResumesEveryGeometryAndResistanceInEachSuspendedContext`
подготовлена для Classic и Branch. Она использует production session и
ProbeRecorder с контролируемым откликом, три C-контекста и полный mesh
3L×3Rs в каждом контексте. Проверяются сохранность dormant/anchor physics,
покрытие каждого mesh и продвижение до дальней длины перед оставшимися Rs
первой длины. Это проверка suspended cursor, не физический эксперимент.
Она добавлена после замораживания normal122 и в эту сборку не входит;
серверная проверка ожидается отдельно. Состояние normal122 записывается в
[job observation](FairDomainTraversalJobs.json), без предварительного PASS.

Первый normal122 успешно собран; в ходе исполнения три новых проверки прошли,
Branch-проверка обнаружила ошибочное ожидание теста: evidence после поиска
input1 штатно включает следующий input0. Проверка исправлена: reverse order
проверяется как1→0 без возврата, bank legality и fixed reference проверяются
для всех записей, geometry coverage — отдельно для input1. Алгоритм этим
исправлением не меняется. Исходный failed run сохраняется; полная приёмка
требует нового immutable source/runtime с исправленным тестом.

Для того же corrected C++ source36f5985 подготовлен отдельный
[ASan38 gate](FairDomainTraversalAsan38Jobs.json):19 recovery controls,
4 fair-domain checks и15 C-context checks. Он запускается только после
успеха normal137 и подтверждённых closure/released lease. `detect_leaks=0`;
отсутствие утечек и вся физическая ASan matrix этим не проверяются.

Парное научное сравнение должно использовать
[строгий matched-study analyzer](StockRecoveryCodeComparison.ru.md): одинаковые
jobs/cold graphs, полные primary audits обеих серий, разные code/runtime
identities. Новый analyzer отдельно проверяется на старой native серии;
такая self-comparison не считается повтором обучения или проверкой fair stock.

[Следующая stock-серия](FairDomainStockComparisonJobs.json) поставлена в очередь
после normal137 и ASan38. Она повторяет восемь условий предыдущего SDK84/Pulse416
на SDK36/Pulse8f. До первого native вызова сохраняются все declarations и
проверяется их совпадение с baseline, затем восемь cold preflight подтверждают
effective model. Новый Train ещё не начат. C-trim/PostTune/calibration выключены,
дополнительная LTMembrane отсутствует; цель и исходные допуски сохранены.

Git-сверка показала: между Pulse416 и Pulse8f в Core изменены только два
BoundedTraining файла; Console sources и корневой CMake между SDK84 и SDK36
совпадают. Runtime/source receipts и итоговая проверка физики всё равно
обязательны. Архивирование новой серии использует только regular payloads;
owner/hash-bound duplicate glog aliases перечисляются отдельно и не удаляются
из исходного server tree. Неизвестные ссылки не отбрасываются молча.

Исправленный [normal137](FairDomainTraversalNormal137Verification.json) принят
адресно:137/137, точный набор JUnit IDs,834 archive members и761 source hashes.
Worker group закрыт, lease released. Все783 исходных native CSV/JSON сопоставлены
с обоими опубликованными primary inventories:284 CSV и480 JSON побайтно равны;
19 startup JSON отличаются только93 значениями служебного Rdk StepDuration.
Первый publisher ошибочно ожидал469 JSON старого25-case subset вместо499
JSON полного native118 inventory; count correction сохранён в evidence.
Данные и tests не менялись и не перезапускались из-за этой ошибки публикации.

Это закрывает normal gate данного изменения, включая controlled C-context
проверку. Вся физическая C-trim matrix, ASan38, реальный stock A/B и полный
исходный план этим не закрываются. Новая научная серия по-прежнему ждёт ASan38.

Следующее состояние: [ASan38 принят адресно](FairDomainTraversalAsan38Verification.json),
38/38,64 primary members/761 source hashes, actual libasan mapping и executable
owner проверены. Whole group closed, lease released. Это не leak check и не
вся физическая ASan matrix. Первый stock launcherA1 был отклонён до worker:
129600s превысили штатный лимит86400s. Исправленный launcherA2 использует24h
внешний cap, сохраняя все бюджеты Train. СерияA2 прошла8 preflight и начала
Train; результаты пока промежуточные. Исходный отказ сохраняется в её receipt.
