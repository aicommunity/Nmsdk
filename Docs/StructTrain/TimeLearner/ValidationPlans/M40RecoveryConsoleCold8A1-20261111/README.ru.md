# Cold8 Console: отдельный Python source

Source3a64bbf09fb906844d9943ee3c4b0589300bcfda доставлен production Git projection в новый source-recovery-console-cold8-a1. Это Scripts-only источник, не новый SDK runtime. Plan: [подробная постановка](../../RecoveryConsoleCold8Preparation-20261111.ru.md).

Native32 использует неизменный root8362d58f/Pulse1110808. Во время его работы никакой runtime/source этого задания не меняется. Новый Python helper будет запускать Console только после точной приёмки native32 и фиксации executable/library hashes. Python code identity и native SDK identity фиксируются раздельно в условиях. Пока нет numerical launch request или runtime manifest.

Strict source guard на M40 проверил722Scripts files; Git status/bytes совпадают с source3a64bbf09. Python imports и unittest discovery обнаружили ровно2old cold7 и2new cold8 IDs; никакие test methods/setUpClass не выполнялись. [Точное наблюдение](source-metadata.json), package fingerprint010eb71ea9c3e360a68d51ae082bb3b7a1d507d6fb7e15324a3deba192dff9db. Это metadata preparation, не runtime-приёмка.

Actual Elder corpus доставлен на M40 отдельным Git commit53e013686493989f08ff6ad5cc736fb4b430ffc1,4files/fixture fingerprint588e016330cafa07549c3834d162ce92133693b9113b461bd48d67c09ce081dd совпадает с принятым independent6. [Доставка](corpus-git-delivery.json), [identity readback](corpus-identity.json). ORIGIN отражает исходный момент публикации до replay6; его historical flag не переписывается после последующей приёмки. Runtime/численный запуск всё ещё ожидают полного native32.
