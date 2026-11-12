# Actual N4 diagnostic16 A2 завершён

M40 job `s11-recorded-n4-diagnostic16-m40-a2`, Tool `251dddc6293bfb4bf620b46d25adf2c633cae8fc`, SDK `448b153f2fea3486ff40f3a626b8f1110b9e3ee2`. Original worker exit0; outer и оба child groups закрыты; единственная lease освобождена; source/tool before/after побайтно равны; diagnostics обоих Console clear. 16 raw proofs в `completed/` сохраняют controller/request/closure/source/runtime results и оба run manifests.

Обе реальные остановленные N4 модели прошли восемь исходных Phase A паттернов при reset-per-trial, 2000 Hz, полном окне 2 s, inherited threshold100. Для каждой получены TP0/FP0/FN1/TN7: спайков нет ни на target, ни на foil. Это полное молчание при высоком пороге, не 7/8 успешной классификации. Frozen model verification пройден в обоих run manifests. Threshold selection, cold retraining и новые certificates не выполнялись. Source training outcomes сохраняются: Classic invalid_observation/ambiguous, Branch budget_exhausted.

Это техническое завершение actual Console матрицы. Независимый production-аудит всех 16 первичных наблюдений и полная галерея 40 pattern×soma запускаются отдельно: [план](../M40RecordedMatrixPrimary2A1-20261112/PLAN.ru.md). До их приёмки и публикации необходимых первичных данных итоговый научный отчёт не объявляется готовым. Предыдущий A1 failure остаётся самостоятельным результатом 0/16.
