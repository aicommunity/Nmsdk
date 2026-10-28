# Эффективные области N1: следующий алгоритмический подэтап

Ветка `stage07/native-dynamic-bounds` создана от develop. Зависимости native state
включены отдельными `--no-ff` merges рабочих веток; это не их приёмка в develop.
Живые full jobs продолжают использовать неизменённые root 7fb92a4 / PulseLib
4919bac / Rdk 1223bcc. Новые адресные jobs используют отдельные idle checkouts.

## Подтверждённое чтением кода

`BoundedTrainingSession::BeginInput` один раз строит Rs mesh по declared
`InputSearchBounds`. `NativeModelEditor::ApplyNativeInputParameters` строит
preview, проверяет его интегратор и вычисляет `minimumResistance` /
`maximumResistance` только для принятого edit. `NativeTrainingService` передаёт
контроллеру effective parameters и model revision, но не эти интервалы. Поэтому
следующий кандидат не использует границы изменённой геометрии. Новый native
fixture задаёт внешний диапазон 0.5 MOhm–1 GOhm и бюджет три кандидата при
фиксированной геометрии; ожидается, что внутренний физический диапазон будет
проверен до расходования бюджета на заведомо запрещённую точку.

Runtime baseline root `fda22b8d99e7a65bb8f97ac4d2ce288219ced9c0`, PulseLib
`87e6c2247f0cd962609bc40a04fd92dafa024a0b` (tree равен 12c5ef5): на каждом
worker два tests / два ожидаемых failures, строго по одному assertion на test.
Native preflight отклоняет mesh Rs как `channel_step_not_certified_strictly_stable`;
запрещённый Rs не применяется. Остальные assertions, включая фактический edit
и не менее двух измеренных кандидатов, прошли. Это дефект бюджета поиска, а не
подтверждённая неустойчивость применённой модели. Scientific convergence не требуется.
Production Python-аудит проверил по 20 actual trial JSON/CSV и final certificates.
Артефакты: [Elder-1](../../../Reports/StructTrain/TimeLearner/s07-domain-baseline-elder1/README.md),
commit `a37d00b9071a338fd01259750e28f82b15a9ab85`;
[M40 ASan](../../../Reports/StructTrain/TimeLearner/s07-domain-baseline-m40/README.md),
commit `35693008140819edeef8b77d3fb2f729372ffd77`.
Локально проверено по 57 stored и 55 raw hashes. Controller ещё не исправлен;
expected-failure tests не принимаются в develop.

Рабочая реализация PulseLib `4be5bc8` добавляет read-only
`AssessNativeResistanceDomain` обоих learner и native preview API: учтены
declared scaled/fixed inhibition, отдельный диапазон активного входа и shared-bank
ограничения. Live graph проверяется после уничтожения preview; отсутствие области
не называется PhysicalInfeasible. TrainingParameters выделены отдельно, `fada6b6`.
После compile correction `39179da` прямые четыре preview/storage-profile tests
прошли нормально на Elder-1 и под M40 ASan, detect_leaks=0. Elder-1 также прошёл
восемь editor regressions N0/N1 при 2/20 кГц, всего 12 cases. Более длинный
M40 ASan regression run продолжается в неизменяемом runtime; отдельный четырёх-
case ASan job использует тот же binary с собственным output. Эти данные ещё
готовятся к публикации. Compile failure A1 сохраняется отдельно.

Текущая production реализация `e875ca5` подключает Native N1 к явным controller
domain actions. Standalone kernel сохраняет declared-only API по умолчанию;
native N1 требует физический provider до reference capture. Mesh пересчитывается
после effective edit; scope/candidate dedup учитывает preview identity и весь
вектор параметров. Сохраняется исходная математическая цель CapturedPerInput,
исходные допуски и независимый final sweep.

Для Branch рассматриваются ordinary/shared и separated upstream geometry;
locked downstream/anchor bank не меняется. При невозможности разделения остаётся
singleton geometry с существующим общим Rs. Best candidate сохраняет полный
вектор параметров. Если одинаковые L/Ns/Rs имеют разные stimulus bindings,
реализация preview требует явного edit и новой пробы, а не подмены scope.
Domain evidence выводится отдельно в training summary. Новые controller tests
усилены требованием реально измерить эффективную нижнюю границу; их runtime
проверка завершилась на обоих workers: исходные два cases проходят, новая
матрица — 14 arithmetic/controller + шесть native cases, 20/20 на каждом.
Четыре native searches при 2/20 кГц и два shared/separated Branch controls
дали по 68 primary trials и 15 domain assessments; production Python-аудит
подтвердил наблюдения и имеющиеся final certificates. Controller evidence
опубликована: Elder-1 `1969585a72d3d09d6e6583f443d980e717575046`, M40
`b902086fad6b6723e3c2f393c108cfbd3a13054b`, по 232 stored / 230 raw hashes.

ASan controller M40 A3: 18/18 cases (14 arithmetic, четыре native при 2 кГц),
44 actual primary trials и 11 domain assessments. Пакет
`45d7fb05e98b880a2c34b2ef6d9ecc21e1746c48`, 114 stored / 112 raw hashes.
Learning/export regressions нового controller на обоих workers: 22/22 native,
9/9 Python, пять actual packages и 62 primary trials; commits
`0a8d90b86e2f6a417c6f095dd213eeea951adcd5` и
`ab494d522a9a134a35990c14d639fc72e086d39c`, по 508 stored / 506 raw hashes.
Все эти compressed/raw hashes проверены локально.

Full maintained groups текущего source ещё выполняются, исправление пока
не принято в develop. Production auditor проверяет исходные пробы и residuals;
он пока не пересчитывает физическое происхождение domain coefficients из
графа. Это отдельное незакрытое требование к decision provenance.

## Не переносить условную границу как универсальную

Нынешний `ResistanceIntervals` считает изменяемым ExcSynapse1, остальные
проводимости — фиксированными в данном preview. Это корректная проверка
конкретного кандидата. Однако при `scaleInhibitionWithInput` сопротивления
связанных InhSynapse тоже зависят от Rs данного входа: их нельзя держать в fixed
части при построении диапазона других Rs. Совпадающие Branch banks требуют
явного учёта владельцев. Нельзя собирать общее пересечение диапазонов разных
входов или менять опорный вход N−1 ради допустимости активного.

## Расчёт по фактической модели

Для поддерживаемого explicit NPulseChannel и статических NPulseSynapse после
native preview строить проводимость каждого затронутого канала как
`g_k(R_i) = a_ki/R_i + b_ki`. В `a` входят все excitation/inhibition synapses,
управляемые Rs активного входа, с реальными коэффициентами масштабирования,
Weight, secretion/PSI bound и averaging. В `b` — остальные фактические источники.
Для каждого из Resistance/RestingResistance/FBResistance канала использовать
его собственные C, r и frequency. Нынешняя no-crossing policy задаёт:

```text
available_k = (sqrt(C_k*r_k*f_k) - 1)/r_k - b_ki
if available_k <= 0 and a_ki > 0:
    no finite interval under this declared no-crossing policy
else:
    lower_i = max(lower_i, a_ki/available_k)
lower_i = max(lower_i, Rm_tip/ratio, configured_floor, declared_lower_i)
upper_i = min(Rm_tip*ratio, declared_upper_i)
```

Это производная используемой модели, не универсальное правило `tau>=2dt`.
Отдельная проверка strict stability (`gain<2`) сохраняется и не смешивается с
no-crossing policy (`gain<=1`). Отсутствие области по этой policy или заданному
search box не доказывает PhysicalInfeasible. Если изменяемая зависимость не
описана или параметры connected/dynamic, нужен явный unsupported diagnostic.
Численные границы должны округляться в безопасную сторону через направленное
округление, без нового физического допуска в процентах/timestep.

## Предполагаемые изменения production API

1. Native editor: выделить read-only candidate-domain preview, который не
   рассчитывает модель, не меняет live graph/prototype и возвращает полные
   по-входовые основания ограничений даже при запрещённом текущем Rs.
2. Native model declaration: передавать зависимости inhibition от Rs, а не
   угадывать их по совпадению чисел. Частный fixed-inhibition профиль сохранить.
3. Bounded controller: отдельное действие domain assessment перед Rs mesh для
   каждого L; declared bounds остаются неизменяемыми условиями эксперимента.
   Эффективные диапазоны и model/geometry revision являются derived evidence.
4. Native service/adapter: выполнять assessment на допустимой границе, проверять
   неизменность actual model revision и возвращать результат контроллеру.
5. Перестраивать mesh после изменения влияющей физики/геометрии; запретить
   повторное использование области с другой revision. Не засчитывать domain
   preview как физическую пробу; сохранять bounded candidate/edit/probe budgets.

Проверки: baseline на обоих learner; разные L и heterogeneous child C/Rm;
2000/20000 Гц; fixed/scaled inhibition и coincident Branch banks; непересекающиеся
области разных входов; отсутствие конечной области; безопасное сохранение live
graph при отказе; unchanged anchor; реальные measured residuals и fresh final
gate. Тесты выполняются только на заданных серверах, исходники/артефакты через Git.

## Ограничения подключения контроллера

- Branch geometry для изменения Rs может требовать разнести ещё не посещённые
  совпадающие upstream attachments. Совпадение с фиксированным downstream/anchor
  bank даёт locked Rs; anchor не меняется. Preview описывает весь предлагаемый граф.
- После каждого effective edit область запрашивается заново. Дедупликация mesh
  учитывает geometry/physics scope и весь вектор параметров, особенно при
  shrink/growth heterogeneous модели. Возможный scope — identity preview на
  фиксированном reference Rs с учётом всех связанных inhibitory Rs.
- Declared bounds и tolerances неизменны; derived intervals являются отдельным
  evidence. Отсутствующий native N1 provider не заменяется статическими bounds.
- Assessment является отдельным controller action через адаптер, без Calculate
  и без зачёта физической пробы. Preview и отброшенные geometry имеют конечный
  бюджет; число candidate/probe/edit действий остаётся ограниченным.
- Baseline, все фактически измеренные точки и fresh final gate различимы.
  Clipping, отсутствие interval и исчерпание mesh не создают Exact.
