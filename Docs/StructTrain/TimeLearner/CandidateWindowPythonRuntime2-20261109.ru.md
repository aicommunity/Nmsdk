# Python runtime2: отдельный plan и полный synthetic archive2 join

Статус: source-only follow-up от frozen Root
`7352f62bfd77ea86606845866a06bab7400454a3`. Локально разрешены и выполнены
только AST/Git/text checks. Серверные 20 tests и настоящий service5 export/
whole archive2 dispatcher+CLI gate ещё не приняты. Frozen53 не менялся.

## Исправление P1 и точный контракт

В frozen7352 `candidate_window_archive_evidence.py:294` подавал `runtime_plan`
в `validate_protocol`, затем в `configuration_view`, которая ожидает cold7.
Это ошибка границы форматов: настоящий current runtime plan является отдельным
codec, может отражать warm attempt/уже изменённый граф и не должен становиться
копией исходной конфигурации.

Новый `candidate_window_runtime_plan.py::audit_candidate_window_runtime_plan`
принимает три независимых DATA документа: runtime2, original cold7, protocol5.
Cold7 используется только для проверки исходного immutable protocol; текущие
runtime fields проверяются собственным строгим контрактом. Archive2 вызывает
этот validator вместо ошибочного cold7 view.

Source parity: Pulse
`073869082041e3f66a3f6bfb3c69b84b4d1276f6`,
`CandidateWindowRuntimePlan.cpp::Encode/DecodeCandidateWindowRuntimePlan`.
Точные runtime2 top keys:

```text
schema_version protocol_binding run_id initial_model_revision initial_model_epoch
search maximum_reference_probes maximum_invalid_reference_probes
maximum_model_seconds maximum_wall_seconds record_capacitance_history composite_measurement
```

Версия ровно 2; `protocol_binding` — canonical binary64 hash полного encoded
protocol5, включая contract2/reference windows/candidate-window policy.
`search` сохраняет точные runtime1 имена: normalization N0/N1, probe/edit/
candidate/sweep/invalid limits, subdivision depth, n0 repeats, bounds, tolerances,
nullable capacitance_search, retry_same_candidate. Из cold7 они не подставляются.
Bool/строки/дробные counters, nonfinite numbers и неизвестные поля отвергаются.

`composite_measurement` содержит common-policy2 и candidate_window_policy.
Method/context/geometry/window policy должны точно совпасть с protocol5;
run/current attempt, current record limits и archive cap связываются как прежде.
Native-probe budget не меньше N+2, sample budget не меньше context total,
reference budget не меньше N, group model/wall limits положительны и не выше
текущих attempt time limits. Bounds имеют int32 positive L, Ns<=128 и finite
positive Rs. Current runtime budget/search/tolerances/normalization могут
отличаться от initial cold, а retained history остаётся под своими старыми caps.

`initial_model_revision`/epoch проверяются как непустая/count declaration
текущего attempt, а не как утверждение равенства original source.initial_model.
При отсутствии новых current-attempt groups эти поля не выдают свидетельство
исполнения или снимок текущей физической модели. Ревизии реально записанных
групп продолжают проверяться по полным candidate graph/raw/native contexts.

Off не требует выдуманного C0/C property. Nullable C-search проверяется как
declaration; `record_capacitance_history=false` сохраняется, не вводится новое
искусственное capSearch→history restriction, которого нет в low-level owner.
Owned C0 в измерениях проверяется отдельно общим source/candidate/raw witness
путём. Политика cursor/region повторяет именно shared owner ограничения
`BoundedTraining.cpp::ValidateCapacitanceSearchPolicy` и seed-domain enumeration
`MeasuredCapacitanceSearch.cpp::CapacitanceSeedScales`: context count равен
**1 + число уникальных ограниченных seeds**, включая deduplicated unit/current
seed; затем floor cursor reserve и L/Ns inventory, Branch region maxL-nextMinL.
Отдельный контроль constant unit domain различает 2 контекста от ошибочного 1.

Private common-policy1 view используется исключительно для shared numeric/
context declaration validation. Observation/archive/schema/certificate не
понижаются до старых форматов. Runtime1 и старый audit_runtime_plan не изменены.
Callbacks, адреса, native executor и live lease из runtime2 не восстанавливаются.

## 20 подготовленных проверок

10 runtime declaration methods проверяют форму/полный protocol hash, warm
модель/epoch/search/tolerances/caps, независимую normalization, отказ cold7/
runtime1/scope marker, числа/unknown fields, bounds/time/raw/ref relations,
capSearch flagfalse и cursor/region constraints.

10 whole-archive methods вызывают настоящий public archive2 dispatcher и CLI
**без mock**. Полностью контролируемая artificial DATA fixture включает original
cold7, настоящий runtime2 shape, полный semantic graph/readback/storage/source
DATA, 2 refs + search + 2 finals, 20 primary CSV, native portable contexts,
actual timestamp projection и независимый geometry replay. XML/графы, часы и
waveforms искусственные; это не actual native Rdk run и не upgrade старого
archive1 native export. Семантическая идентификация параметров проверяется,
но native import/execution и prequeue/live ownership из таких данных не следуют.

Negative controls включают self-consistent rehashed foreign reference proof,
Rs readback claim против неизменного semantic bank, candidate frame shift,
raw/full-repeat tamper, historical prefix cap за повышенным warm cap,
missing/corrupt external CSV и отсутствие original runtime-plan.json.
Положительный warm-empty контроль сохраняет immutable allN references и
старые record budgets; новые start model/epoch/session не приравниваются к P0.

Все reports сохраняют native_execution_verified/live_authority_restored/
training_certificate_verified=false, scientific verdict отсутствует. Полный
synthetic join закрывает пробел unit coverage, но не заменяет настоящий
source-reviewed service5 producer. Нужны genuine original cold7 + owning
runtime2 + archive2 + external primary из будущего service gate, затем реальный
dispatcher/CLI positive и coherent rehashed tamper на этих exports. Manual33
DATA по-прежнему не получает выдуманного servicePlan, runtime2 или cold7.
