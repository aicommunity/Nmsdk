# Recorded matrix provenance: 36/36

M40 job `s10-recorded-matrix-join36-m40-a1`, source `cc754d59682a0ce88239695c437ff9b248ef859f`, Tool `40e28802c29014ec8a5af0f8763aa607ad9a986a`. Все 36 объявленных test IDs прошли без failures/errors/skips. Wall time 17.839 s; whole group closed, lease released, operational diagnostics clear. Source/tool/fixtures before/after побайтно равны; 13 raw proofs сохранены в `completed/`.

Предыдущие 32 проверки повторены с четырьмя новыми проверками production `audit_matrix`: failed operation при успешном cleanup; подмена явно указанного runtime manifest; отсутствие собственных case process groups; незакрытое резервирование. Дополнительно код использует общий streaming frozen digest для больших первичных файлов без оставленных открытыми дескрипторов.

Область приёмки — адресная логика отказов и прежние regression checks. Она не доказывает положительный аудит полных 16 новых наблюдений или визуальную читаемость новой матрицы. Эти проверки ожидают завершения отдельного actual Console задания A2. Научный PASS и завершённое обучение не заявляются.
