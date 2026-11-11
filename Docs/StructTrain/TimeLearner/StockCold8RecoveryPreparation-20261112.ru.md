# Строгий N4 cold8 recovery — подготовка 12.11.2026

Новый public CLI:stock-candidate-window-study prepare-recovery SOURCE_PLAN --runtime-manifest RUNTIME --output OUTPUT. Источник — сохранённый план cold7, не learned model. Обе исходные jobs и conditions проверяются по production serializer, полные исходные effective identities проходят stock profile audit. Источник фиксируется frozen_digest до/после чтения.

Меняются только schema_version7→8, run_id и явно добавленный advance_rejected_candidate_window; подпись job пересчитывается. Physics/target/window policy, CapturedPerInput, N1, все search/time budgets и tolerances1e-5/0/0.02 сохраняются. Технические N2/N0/Sync0.2 inputs отвергаются. Повторное преобразование8→8 запрещено.

План2 отделён от прежнего плана1:run проверяет соответствие plan2/config8 и использует source7/summary8 auditor. Старый cold7 использует прежний reader. Перед Train обязательны native preflight, сравнение полного effective graph с исходным stock identity и новая регистрация managed child processes. Старые измеренные координаты служат только диагностической гипотезой окна; Train заново захватывает references. В новое обучение старые learned parameters/сертификаты/динамика не импортируются.

[Проверки выполнены на M40:5/5 PASS](ValidationPlans/M40StockCold8PreflightA2-20261112/RESULT.ru.md):четыре declaration regressions и свежий preflight обеих N4 моделей на новом runtime; полные исходные графы совпали. Следующий допуск — фактический cold Train после этих проверок; положительная классификация не предполагается. Строгие negative/unresolved сохраняются отдельно от invalid observations/configuration. Полная матрица и этапы1–12 остаются открытыми.
