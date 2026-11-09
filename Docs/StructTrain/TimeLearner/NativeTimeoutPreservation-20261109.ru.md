# Сохранение закрытого native timeout без подмены результата

Native119 A1 собрал targets и подтвердил 19 cases. Следующий Classic N6 routing остановлен внешним лимитом 2400 s; конечный JUnit и старый actual-tests record отсутствуют. Это не case FAIL по assertions и не успешный завершённый cohort. Его 100 оставшихся IDs включают начатую, но незавершённую проверку.

Исходный collector schema1 намеренно требовал завершённый JUnit для каждого записанного child. Он пригоден для уже опубликованного native48 9PASS/2FAIL, но не принимает A1. В одном лишь основном output A1 измерено 484 regular files/130782334 bytes; предел64 MiB также недостаточен. Исключать сырые данные N6 или сохранять только summary нельзя.

Schema2 `closed_native_collection` сохраняет прежний контракт schema1 и добавляет обязательную карту `incomplete_children`. Текущий явно поддерживаемый новый случай — закрытый `timeout` с отсутствующим XML, `validity=incomplete_test_observation`, `assertion_status=not_assessed`, `inventory=null`. Две исходные копии gate result должны совпадать и согласовываться с process result. При наличии исправленного actual-tests record он должен содержать ноль завершённых IDs и отдельно перечислять unobserved expected IDs. Runtime ownership, kernel closure, child maps, released original lease, exact namespace/link metadata и все frozen bytes проверяются независимо.

Schema2 outcome использует `not_completed_ids`, не смешивая неначатые и начатые незавершённые проверки с завершёнными. Никакой ID не добавляется в executed/passed по exit code, cleanup либо плану. XML, появившийся после freeze, изменение process outcome или добавленный record отвергаются. Математическая оценка и научный verdict остаются отдельными и здесь отсутствуют.

Для schema2 фиксированы пределы capture256 MiB/output512 MiB, минимальное свободное место512 MiB; каждый отдельный файл по-прежнему ограничен frozen-file API. В Git поступает сжатый primary bundle и контрольные JSON, исполняемые файлы не копируются в отчёт. Ограничитель не означает аттестованный внешний cgroup сборщика; его отсутствие по-прежнему указывается в receipt.

Девять новых адресных metadata tests используют production observation reader и реальные временные файлы; прежние14 namespace/role/size/gzip tests остаются обязательны. До серверной проверки и actual collection это source-only. Поддержка произвольного повреждённого/частичного XML, compile-failure до native leaves и всех остальных отрицательных сценариев данным расширением не заявляется.
