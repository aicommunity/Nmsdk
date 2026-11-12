# Полный primary Classic budget16 timeout

Сохранён весь закрытый job s07-full-domain-budget16-train-m40-a2:1368 members,638046035 expanded bytes; XZ32487228 bytes, SHA51b68ff76920d7903051bbc0f57ce96c41bcb2c3002fc94028079f953c55cd73. В Git добавляется только сжатый корпус и компактные manifests, без неупакованных CSV и полной галереи.

Reports/StructTrain/TimeLearner/ClassicBudget16TimeoutPrimary-M40-20261112 содержит398 native packets,397 с исходными valid/complete flags и последнюю отменённую пробу. Все796 CSV сохранены с исходными именами, SHA-различных398; дубли экспортных имён не считаются дополнительными наблюдениями. Исходный measurement index270193422 bytes также сохранён в архиве: он содержит67 records, включая неполную группу, но не является финальным learned-state или summary.

Production closed-primary collector проверил весь namespace, bytes/hashes и закрытие всех declared owned units до и после упаковки. Источники не переписаны; файловые identity/timestamp integers в collection-proof.json сохранены исходными байтами. Исторические glog aliases требуют штатного dereferenced-glog-aliases-v1 restore adapter.

Producer Git563879998936e1cb6fb980f8deafdc0d6c2f73ff; transfer pack32579394 bytes/SHA84b5d74136019f0aba1a0f901b19239b9e77fe6a7fbcc1f0c6fc43e4bb186f11. Передача через Git; все6 файлов проверены по ARTIFACTS. [Production DATA audit исходного индекса](ValidationPlans/M40Budget16RetainedArchiveAuditA1-20261112/RESULT.ru.md) пересчитал67 records/398 primary files; независимое восстановление именно нового полного архива отдельно ещё не заявляется.

[Научный статус](ValidationPlans/M40FullDomainBudget16TrainA2-20261112/RESULT.ru.md): execution timeout, training outcome unknown, нет финальной модели или классификации. Корпус нужен для адресного исправления summary/export, без повторного дорогого Train для каждой итерации.
