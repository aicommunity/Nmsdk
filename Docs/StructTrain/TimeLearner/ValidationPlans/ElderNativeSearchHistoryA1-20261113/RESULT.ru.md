# Elder: проверки native-search-history

Приняты 7 из 7 unit controls, без ошибок и пропусков. Исходный набор и request зафиксированы до запуска в control Git e5c02c0d5b846e2adfd0b635c0cb6cc8df7a9ccc; проверяемый Root c899d8ff1b58a3cbe8a9f0453665f92d509eb3bc. Actor 929dbc176a0804910544539aaf79bdc4a02aa82a.

Внешнее задание s07-native-search-history-elder-a1 завершено exit0 за20.078855774831027s; operational diagnostics clear, heartbeat errors отсутствуют, вся группа процессов закрыта, lease released. Исходники actor/validation сохранены до и после проверки; их исходные JSON находятся в completed-readback. Проверки сравнения физических результатов и новый Train здесь не выполнялись.

Покрыты различие model revision и parameter vector, отсутствие истории, Branch/N0/N7 projection, сохранение дополнительных C/cost fields, запрет duplicates/schema/nonfinite, изменение summary после audit и запрет output в original run. Два unit controls используют mock boundary; реальный полный production CLI case проверяется отдельно на M40. Это не доказательство научной сходимости и не полная приёмка этапов3/7/9.

14 исходных записей сохранены byte-exact в producer Git ed8c9ddf4bb821f575794f0a88a9b918159a5da6 и перенесены Git pack; размеры/SHA перечислены в [integrity](completed-readback/integrity.json), параметры получения — [EVIDENCE_GIT](EVIDENCE_GIT.json).
