# Проверка инженерного deadline fixture

08.11.2026. Две диагностические и четыре адресные deadline-проверки на M40/ASan
приняты отдельно. Полный248, production preparation и научная классификация
остаются открытыми задачами.

Первоначальный Rootcc23/Pulse88 выполнил13 случаев:12 passed,1 failed.
`BranchLastCompositeSinkCannotCrossRealGroupDeadline` не достигла нужного
callback. [Отрицательный результат](CompositeCancellationM40A1IndependentVerification.json)
сохранён; никакое ожидание теста не ослаблялось.

## Фактическая стоимость обычной группы

Root `f8f58334a8b203d017ada5e3d3300e6287286751` / Pulse88 добавил только
диагностическую запись фаз. Использованы прежние2000Гц,64 синапса и параметры
engineering fixture, включая sync tolerance0,2. Production default0,02 не
менялся. Для диагностики оставлен исходный ServicePlan group cap300s;
искусственной задержки в callbacks нет.

| Топология | Группы | Raw trials в группе | Frames в группе | Group record elapsed,s | Максимум fresh callback elapsed,s |
|---|---:|---:|---:|---|---:|
| Classic |6|4|1364|19,04–20,67|21,108|
| Branch |6|4|1364|13,71–15,674|16,109|

У обеих топологий реально достигнут последний consumed Final callback,
outcome Exact в этом engineering fixture. Результат не является проверкой
исходного научного допуска0,02 или классификации восьми паттернов.
[Независимая квитанция](CompositeDeadlineDiagnosticM40A1IndependentVerification.json)
сверила158 членов архива,3687 source files в8 Git repos, два JUnit cases,
ASan-loaded files, три закрытые группы и сохранность четырёх старых runtime.
Evidence `b4a1bc31bdb2c2a662051329cb8d3018881819c6` находится в
`origin/codex/timelearner-composite-deadline-m40-asan-a1-evidence`.

## Адресное исправление тестовых условий

Root `17db91ee0e8f308ea39cf7ebef641e1814080337` изменил только шесть числовых
полей в двух test template functions: group cap60s, настоящий sleep61s,
ожидание measured elapsed≥60s. Физика, алгоритм обучения, whole cap1800s и
обычный ServicePlan cap300s сохранены. Это явная инженерная настройка теста,
обоснованная измеренными phase times.

Прошли Classic/Branch × lastRaw/lastCompositeSink: каждый callback реально
задержался, затем получен BudgetExhausted/group_time_budget без service
certificate. Для lastRaw отсутствуют consumed references; lastCompositeSink
не может опубликовать Exact после истечения бюджета.
[Независимая квитанция4](CompositeSlowDeadlineM40A1IndependentVerification.json)
сверила219 членов архива,source3687,точные четыре JUnit IDs/durations,
ASan-loaded files,пять закрытых групп,327 ресурсов и пять старых runtime.
Evidence `43377c50075f015bed68d5717afdffac23201c6e` находится в
`origin/codex/timelearner-composite-slow-deadline-m40-asan-a1-evidence`.

Исходный обязательный union248 должен выполняться отдельно после проверки
maintained preparation helper. Два diagnostic IDs считаются отдельно;
compiled universe250 и source suite64 не подменяют executed248.
