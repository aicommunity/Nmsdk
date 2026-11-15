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

## Исполнение адресной приёмки

A1 завершён: все142 C++ cases исполнены,116 прошли,26 завершились исключением NewOnly из-за общих имён файлов тестовых fixture. Все26 сообщения проверены по фактическому JUnit; алгоритмический PASS из этого не выводится. Ошибка была в группировке сценариев в один leaf. Исходный отказ сохранён, процессы закрыты, heartbeat/final capture errors отсутствуют.

A2 оставляет тот же production Pulse a82a7cd и тот же C++ source/test inventory142;113 algorithm/codec checks запускаются одним leaf,29 native checks получают отдельный процесс и каталог каждый. Штатные guards не ослабляются. После подтверждённой остановки A1 используется его idle build directory с неизменными исходниками; новый deploy/runtime A2 отделён, прежний runtime защищён от записи. CMakeCache A1 до повторного configure сохранён во внешнем архиве с SHA256. Это повтор приёмки, не повтор научного Train. [Машиночитаемый статус](RejectedLengthCoverageAcceptance-20261115.json).

A2 подготовка была отклонена до build: `canonical_source_or_fresh_build`. Канонический путь SDK требует свежий build directory; его guard не меняется, исходный build/runtime A1 не изменены. Для повторного исполнения того же уже собранного binary используется штатный `native_gate` (контракт already-built tests),30 отдельных outputs и142 исходных случая. Это самостоятельная проверка исполнения, не новая fresh SDK build; raw A1/A2 отказы сохраняются. Новое обучение до полного PASS142 и закрытия всех cgroups не запускается.

Раздельный A3 исполнил113 algorithm/codec checks успешно и дошёл до wide-missing native case. Контроллер действительно предложил64, но ApplyNativeTrainingParameters отказал `invalid_edit_parameters`: новый тест разрешил64 только в search bounds, оставив native fixture максимум8. Исправлен единственный аргумент создания wide fixture на64; native bounds guard не меняется. Это ошибка нового теста, не доказательство неисправности алгоритма. Требуется новая сборка тестов и полный адресный повтор. Production Pulse a82a7cd не менялся; новый научный Train ещё не запущен.

Fresh SDK A3 использует исправленный root1a10165507c0aa2c4c63b010f1a199b6b35c6779/Pulse a82a7cd08a4334c5924839b7136ae9df5884da53. Каноническая подготовка A3 обнаружила отличие порядка selected IDs от развёрнутого runplan; A4 исправляет только порядок списка при том же наборе142 cases. Строгая проверка порядка сохранена. Все744 исходных файла закрытых неуспешных попыток сохранены во внешнем проверенном архиве7382028B, SHA256780e7ee6845766abb8f8e90a82c2f6baf058da9c470ecbcab50f08fbfdf73691; ссылка в машиночитаемой приёмке. Новое обучение ждёт полного адресного PASS.
