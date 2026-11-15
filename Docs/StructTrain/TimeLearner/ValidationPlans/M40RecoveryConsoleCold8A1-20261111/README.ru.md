# Cold8 Console: отдельный Python source

Source3a64bbf09fb906844d9943ee3c4b0589300bcfda доставлен production Git projection в новый source-recovery-console-cold8-a1. Это Scripts-only источник, не новый SDK runtime. Plan: [подробная постановка](../../RecoveryConsoleCold8Preparation-20261111.ru.md).

Native32 использует неизменный root8362d58f/Pulse1110808. Во время его работы никакой runtime/source этого задания не меняется. Новый Python helper будет запускать Console только после точной приёмки native32 и фиксации executable/library hashes. Python code identity и native SDK identity фиксируются раздельно в условиях. Пока нет numerical launch request или runtime manifest.

Strict source guard на M40 проверил722Scripts files; Git status/bytes совпадают с source3a64bbf09. Python imports и unittest discovery обнаружили ровно2old cold7 и2new cold8 IDs; никакие test methods/setUpClass не выполнялись. [Точное наблюдение](source-metadata.json), package fingerprint010eb71ea9c3e360a68d51ae082bb3b7a1d507d6fb7e15324a3deba192dff9db. Это metadata preparation, не runtime-приёмка.

Actual Elder corpus доставлен на M40 отдельным Git commit53e013686493989f08ff6ad5cc736fb4b430ffc1,4files/fixture fingerprint588e016330cafa07549c3834d162ce92133693b9113b461bd48d67c09ce081dd совпадает с принятым independent6. [Доставка](corpus-git-delivery.json), [identity readback](corpus-identity.json). ORIGIN отражает исходный момент публикации до replay6; его historical flag не переписывается после последующей приёмки. Runtime/численный запуск всё ещё ожидают полного native32.

## Конкретный план запуска

Подготовлены два cold8 cases; tool/source3a64bbf09, package010eb71e...df9db, immutable native SDK8362d58f/Pulse1110808. Runtime fingerprint61f3e2f0937f8f0bc70e0d40d907c0ba30d86f2030c7b79b2671343cadb374a0 получен read-only snapshot; повторная verify_runtime после native32 обязательна. Console fixture выбирает ровно executable иINI (NeuroModelerConsole*); .a build libraries уже связаны в executable, runtime manifest отдельно проверяет resolved dynamic libraries.

Operation python-controller-validation выполняет suite в contained main PID, source==tool commit/path. Обычный python-validation создал бы дочерний interpreter и нарушил managed lease owner identity. Outer memory2GiB/tasks128, native child4GiB/tasks64; managed aggregate lease6GiB/tasks256, один native child за раз. Для всего job output6GiB, free floor2GiB,6h; временное восстановление архива включено. Это адресный технический запуск, не приёмка всей очереди/публикации исходного плана.

Ожидаемый control fingerprint вычислен production serializer на Linux из hashes объявленных bytes; фактические server files ещё будут проверены по Git bytes и fixture preflight. Windows preparation обнаружила расхождение lstat/fstat ctime у неизменного declaration.json; guard не ослаблялся. [Наблюдение](windows-file-identity-observation.json) остаётся открытым вопросом portability, не ошибкой модели. Никакие модели локально не рассчитывались.
