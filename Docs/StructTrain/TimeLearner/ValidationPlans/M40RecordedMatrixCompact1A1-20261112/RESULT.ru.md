# Compact actual-data roundtrip: 1/1 принят

Job `s11-recorded-matrix-compact1-m40-a1`; source `3f5086df45aa2f03e222d4379d39cb231a4bda88`, Tool40e28802. Production export проверил полную исходную matrix, отобрал исходные байты, затем пакет восстановлен и обе модели/все16 observations пересчитаны единственным production scorer. Полные metrics совпали с original run manifests. Test прошёл за1431.935 s; whole group closed, lease released, diagnostics clear, source/tool/fixtures before/after равны. 15 raw proofs в `completed/`, включая actual bundle manifest и численный readback.

Пакет: 42 members, expanded406979001B, archive28053768B (28.1MB), SHA `d8ea0c4911f0114737d955a81261abba23a1f4e49858a08c8e4e2991a6755468`. Полные модели и исходная обучающая evidence сохранены; ~3GB working directory и производные рисунки целиком не копируются в Git.

Scientific scope остаётся отрицательным: обе остановленные модели при threshold100 имеют TP0/FP0/FN1/TN7; certificates отсутствуют, training outcomes invalid_observation/budget_exhausted сохраняются. Это DATA export/reanalysis acceptance, не успешное обучение или новый model execution. Git publication, отдельный replay без original M40 directory и визуальная галерея принимаются далее самостоятельно.
