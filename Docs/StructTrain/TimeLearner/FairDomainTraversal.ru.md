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
