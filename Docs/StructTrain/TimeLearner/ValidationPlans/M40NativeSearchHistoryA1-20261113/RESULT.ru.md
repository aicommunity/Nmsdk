# M40: полный анализ исходной истории поиска принят

8 из8 тестов прошли, без ошибок и пропусков:7 unit controls и1 actual production CLI case. Исходный Root c899d8ff1b58a3cbe8a9f0453665f92d509eb3bc, actor7bd3684732e1d3f7a0aa038d659fd52bc95892bf, control Git a3489ccfdcb5642849a2541e004a59848d039d4c.

Job s07-native-search-history-m40-a1 завершён exit0 за405.54567408002913s; diagnostics clear, heartbeat errors отсутствуют, whole group closed, lease released. Source/actor/fixture snapshots до и после равны побайтно. Повторного Train и native rebuild не было.

Полный production audit_run_manifest исходного N4 Train принят; затем штатный CLI проверил исходные manifest/job/execution/summary bindings. [Оригинальный вывод CLI](completed-readback/worker/tmp/actual-training-search-report.json) сохранён без пересериализации. Подтверждены15 measured candidates,13 rejections,28 assessed domains,58 producer-reported search probes; terminal model3b8a160f.../L22 не совпадает с measured candidates, final_group_ids пуст. Producer counter58 не объявляется независимо пересчитанным числом предъявлений.

15 исходных записей находятся в producer Git72a0c74dd3b9dc8dacd05628f5b856d85eaaf144, перенесены Git pack и сверены с оригинальными blobs; [перечень bytes/SHA](completed-readback/integrity.json), [параметры получения](EVIDENCE_GIT.json).

Успех анализа означает согласованность сохранённых данных и корректность проекции в этой области. Native execution attestation этим DATA audit не создаётся, сертификат обучения отсутствует, научный verdict null. Полные этапы3/7/9 и обязательная physical matrix не закрыты.
