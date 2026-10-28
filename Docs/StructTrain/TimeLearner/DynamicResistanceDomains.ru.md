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
проверен до расходования бюджета на заведомо запрещённую точку. Runtime baseline
ещё не выполнен; scientific convergence этим тестом не требуется.

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
