# Branch-only full-domain Train: отдельный бюджет финализации, M40 A2

[Исходная ошибка и точные доказательства](../../ObservationDomainFinalizationTimeout-20261112.ru.md). A1 Branch закрыт timeout во время экспорта, без итогового package; A1 Classic не меняется и продолжает работу.

Новая попытка заново обучает только Branch. Source/tool f71bb4dd411922f28b3a5e419b6ffcc1184641a3, SDK8362/Pulse111/runtime61f3e2f0 и ранее принятый prepared plan3/config8 не меняются. Сохраняются CapturedPerInput/N4/N1/2000Hz/Sync0.02/amp1e-5, все search/probe/edit/invalid budgets. Native search1800s; process finalization900s отдельно, всего2700s. RAM/tasks/output/floor остаются прежними. Нового научного фактора или изменения цели не вводится.

Production validation loader выбирает один существующий Branch test по полному ID; его код не копируется и не меняется. Требуется valid complete package/physics audit и положительная проверка фактически применённых full-domain candidate frames. Exact не требуется для engineering PASS. No Test/calibration/template fallback. До полного результата, closure, source/fixture audit и проверки ledger попытка не принята.
