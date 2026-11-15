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

После приёмки — один exploratory cold Branch N0 Train с тем же local limit12 и всеми остальными условиями принятого опыта. Изменяется только алгоритм выбора следующей длины. Это адресная проверка покрытия, не independent scientific validation. При новой invalid/nonconvergent остановке не увеличивать автоматически бюджеты; записать фактические длины, assignment validity, остатки и ограничения. Изображения Soma/inputs строить по первичным данным в читаемом масштабе; все payload только во внешнем архиве M40. Текущий статус: адресная приёмка A5 завершена142/142; сравнительное научное обучение выполняется. Ход прежних попыток ниже сохранён как история, а не действующий итог.

## Исполнение адресной приёмки

A1 завершён: все142 C++ cases исполнены,116 прошли,26 завершились исключением NewOnly из-за общих имён файлов тестовых fixture. Все26 сообщения проверены по фактическому JUnit; алгоритмический PASS из этого не выводится. Ошибка была в группировке сценариев в один leaf. Исходный отказ сохранён, процессы закрыты, heartbeat/final capture errors отсутствуют.

A2 оставляет тот же production Pulse a82a7cd и тот же C++ source/test inventory142;113 algorithm/codec checks запускаются одним leaf,29 native checks получают отдельный процесс и каталог каждый. Штатные guards не ослабляются. После подтверждённой остановки A1 используется его idle build directory с неизменными исходниками; новый deploy/runtime A2 отделён, прежний runtime защищён от записи. CMakeCache A1 до повторного configure сохранён во внешнем архиве с SHA256. Это повтор приёмки, не повтор научного Train. [Машиночитаемый статус](RejectedLengthCoverageAcceptance-20261115.json).

A2 подготовка была отклонена до build: `canonical_source_or_fresh_build`. Канонический путь SDK требует свежий build directory; его guard не меняется, исходный build/runtime A1 не изменены. Для повторного исполнения того же уже собранного binary используется штатный `native_gate` (контракт already-built tests),30 отдельных outputs и142 исходных случая. Это самостоятельная проверка исполнения, не новая fresh SDK build; raw A1/A2 отказы сохраняются. Новое обучение до полного PASS142 и закрытия всех cgroups не запускается.

Раздельный A3 исполнил113 algorithm/codec checks успешно и дошёл до wide-missing native case. Контроллер действительно предложил64, но ApplyNativeTrainingParameters отказал `invalid_edit_parameters`: новый тест разрешил64 только в search bounds, оставив native fixture максимум8. Исправлен единственный аргумент создания wide fixture на64; native bounds guard не меняется. Это ошибка нового теста, не доказательство неисправности алгоритма. Требуется новая сборка тестов и полный адресный повтор. Production Pulse a82a7cd не менялся; новый научный Train ещё не запущен.

Fresh SDK A3 использует исправленный root1a10165507c0aa2c4c63b010f1a199b6b35c6779/Pulse a82a7cd08a4334c5924839b7136ae9df5884da53. Каноническая подготовка A3 обнаружила отличие порядка selected IDs от развёрнутого runplan; A4 исправляет только порядок списка при том же наборе142 cases. Строгая проверка порядка сохранена. Все744 исходных файла закрытых неуспешных попыток сохранены во внешнем проверенном архиве7382028B, SHA256780e7ee6845766abb8f8e90a82c2f6baf058da9c470ecbcab50f08fbfdf73691; ссылка в машиночитаемой приёмке. Новое обучение ждёт полного адресного PASS.

Проверка production preflight: `Core/TimeLearner/ConfiguredNativeTraining.cpp:177` уже требует `search.bounds[i].maximumLength <= model.editPolicy.maximumCableLength`, а также проверяет Ns/Rs и исходное attachment. Ошибка нового wide fixture возникла в прямом unit/integration построении BoundedTrainingSession, минуя ConfiguredNativeTraining; отдельного открытого production-дефекта по этому признаку не заявляется. Производственный Train использует штатный admission и совпадающие max100 модели/поиска. Это read-only подтверждение по коду, не новый физический прогон.

## Таймаут длинного Classic-контроля и тестовое логирование

Fresh SDK A3 исполнил128 C++ cases без assertion failures, затем ClassicAmbiguousSearchQueuesFreshCandidate был остановлен gate timeout300с; итоговый XML отсутствует, оставшиеся14 не подтверждены. SIGTERM stack указывает на UContainer::LogPropertiesAfterCalc → UExceptionLogger → EStringDebug. ConsoleLikeInit явно включает DebugMode и все debug masks. Последняя законченная anchor-группа после ростаL54 потребовала около200с против примерно25с на исходной структуре; INFO-log при этом290B, то есть CPU тратится на форматирование отбрасываемых debug-свойств. Это свидетельство накладных расходов, не научной несходимости.

NativeCompositeFixture::Run временно снимает только RDK_SYS_DEBUG_PROPERTIES (бит4) с глобального logger mask на время BeforeTick/native Calculate/AfterTick; DebugMode, error/warning и остальные bits не меняются, actual onSample/observations сохраняются. RAII восстанавливает mask при исключении, отдельная проверка подтверждает восстановление. Production Rdk/PulseLib и научные budgets/допуски не меняются. Требуется повтор всех142 случаев, сравнение сохранённых исходных raw-reference CSV и последующий cold Train. Исходный timeout сохраняется как timeout, не PASS.

## Адресная приёмка A5 и научный запуск

A5 завершён:142/142 actual C++ cases PASS,30 leaf gates, heartbeat/final capture/record errors отсутствуют, supervisor и все дочерние cgroups закрыты. Это приёмка данного ограниченного изменения, не всей физической/режимной матрицы. Все8 raw reference CSV двух исходных Classic-групп из A3 и A5 совпали побайтово; [полные hash/размеры](RejectedLengthReferenceWaveforms-20261115.json). Исправление тестового debug mask не меняет эти наблюдения; общего ускорения физической модели этот контроль не доказывает.

На M40 запущен один cold Branch N0 Train `s11-n0-recovery-coverage-train-m40-a1`, control commit a8687c0315945fba9a4e8d0544601afe5e3f0dfb, runtime fingerprint7ab8c6f4f11d81f77d99d947d88021ab1dc249bbf189d78df12be6a087207132. Полная configuration фактического нового N0 job побайтово по структуре JSON равна configuration предыдущего завершённого local-budget12 пакета. Local12/global128probes/1280edits/4sweeps/4invalid/1800с/finalization300с и исходные допуски сохранены. Требуется результат измеренных пиков, исходы и свежая all-input проверка; сертификат из технического PASS не выводится.

Полные3850 файлов SDK A3 (128 PASS и незавершённый timeout) и A5 (142 PASS), control specifications и контроль8 CSV помещены в проверенный внешний архив30764561B, SHA25609b518f7d941fea9ed2e9551ca9a03680b3d20dd9c5198921130521876d7a63d. Для каждого tar member проверены размер и SHA256; в Git записана только ссылка в приёмке.

## Итог сравнительного обучения

[Научный отчёт](N0RecoveryCoverageScientificReport-20261115.ru.md): фактически исследованы L28,100,64,46,82; все пять input1 observations ambiguous. Первые13 scalar measurements полностью совпали с local12 контролем. Production CLI/DATA/physical1/1 и read-only temporal report1/1 приняты, процессы закрыты, сертификат отсутствует. Построены16 видов2880×2880,4 overview просмотрены; весь primary и галерея во внешнем архиве. Это адресное принятие normal/native поведения; ASan именно нового покрытия, вся физическая матрица и полные этапы1–12 не объявляются завершёнными.
