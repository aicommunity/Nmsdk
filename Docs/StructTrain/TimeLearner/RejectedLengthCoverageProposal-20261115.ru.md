# Branch N0: широкое предложение длины после отвергнутой пробы — 15.11.2026

Исходная версия: root develop e8b5b75176f55ee006798047d630dbef23d462af, PulseLib develop64f452ec7538d3fba1eff0334e00803e4fab82d3. [Опыт local-budget12](N0LocalBudget12ScientificReport-20261115.ru.md) действительно дошёл до input1, но исчерпал invalid budget на пяти различных L28..32. Это недостаточное покрытие области поиска; само по себе оно не доказывает существование решения при дальней длине.

Изменение ограничено typed AdvanceRejectedCandidateWindow, Branch N0 и исходным Ns/Rs текущего входа. Legacy, RetrySameCandidate, Classic и N1 сохраняют порядок. После отвергнутой пробы предлагается ещё не предъявленная длина, максимизирующая расстояние до предъявленных длин того же семейства. Проверяются ближайшие края области и середины промежутков; число операций зависит от сохранённой истории, а не ширины целочисленного диапазона. Равенства разрешаются в пользу меньшей длины. При допустимых28..100 и первой отвергнутой28 предложения покрытия:100,64,46,82. Это примеры порядка, не предсказанные времена прихода.

```text
on typed rejected search observation:
    preserve rejection and consume the original invalid allowance
    if searching, not restoring best, Branch N0 and original Ns/Rs:
        bound legal L by downstream bank and upstream length bounds
        find largest uncovered interval in the issued geometry family
        queue a legal unissued endpoint/midpoint at highest priority
    continue native edit -> effective readback -> fresh anchor -> input
```

Каждый изменённый граф полностью инвалидирует старые измерения. Missing/ambiguous не создают scalar residual, bracket или measured timing trend. Все budgets, CapturedPerInput, N−1 anchor, amp_abs1e−5, rel0, minamp1e−6 и sync0.02 неизменны. Смена Ns, C-контекста, downstream или Rs не даёт права использовать чужой измеренный остаток. Никакого сертификата до свежей проверки всех входов.

Проверки: четыре unit-сценария покрытия/дублей/границ/int overflow; два native storage/scheduler-сценария missing и ambiguous с предложением за пределами короткой nearest mesh, штатным применением графа и новой anchor-пробой. Существующие invalid/probe/edit budget, replay, default-policy и N1/Classic recovery guards должны пройти. Сборка только на серверах в отдельном неизменяемом runtime.

После приёмки — один exploratory cold Branch N0 Train с тем же local limit12 и всеми остальными условиями принятого опыта. Изменяется только алгоритм выбора следующей длины. Это адресная проверка покрытия, не independent scientific validation. При новой invalid/nonconvergent остановке не увеличивать автоматически бюджеты; записать фактические длины, assignment validity, остатки и ограничения. Изображения Soma/inputs строить по первичным данным в читаемом масштабе; все payload только во внешнем архиве M40. Статус: код подготовлен, серверная приёмка ещё не выполнена; новый научный результат не получен.
