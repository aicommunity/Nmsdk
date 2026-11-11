# Native canonical25 A1: ошибка подготовки fixture

На M40 выполнены **13 старых owner-тестов: PASS**. Все **12 новых canonical-тестов не запускались**: setUpClass завершился ошибкой до первого метода. Это не 25 выполненных тестов и не научный результат.

Причина: fixture использовала `git archive HEAD Scripts` в намеренно частичном Git checkout. Git попытался загрузить отсутствующий посторонний blob `ac8f25bb4fbc1440bccb5fc9fae6952d910f561c` (.cursor/rules/timelearner-experiment-prose.mdc); origin в изолированной копии не настроен. Production canonical/owner этим результатом не проверены.

Source `01a763dab6a2344eef9ed79e2312dfd3ec2f0de9`, plan `873c6d763e70e7170e73d028675bd226a6eb3cc4`, прежний ToolCEC. Root прочитал исходный результат, полный журнал и фактическое состояние того же unit: группа закрыта, собственный lease `a56f646c-f246-4434-a456-1da8f21909a5` released, Source/Tool неизменны. [Полные наблюдения и hashes](../../../Reports/StructTrain/TimeLearner/s10-native-canonical25-a1-root-observation/index.json).

Исправление ограничено fixture: получить весь production Scripts через точные Git tree/blob IDs без archive и lazy fetch, сохранив байты и режимы файлов. Новый source/план A2 проверяется отдельно; A1 не перезапускается, посторонние Root/Reports blobs не загружаются. До A2 и реального SDK namespace/canonical integration native48 не допущен.
