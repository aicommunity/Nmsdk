# Полный повтор native119 после исправления reference fixture

Subject SDK: Root `f2f8e611d51f1b4f23ef0471ddfc7618e68a59ea`, Pulse165d49d, Rdkde413, Bin8cb. Изменён только тест принадлежности reference; production алгоритмы и условия измерения прежние. Отрицательные original runs SDK8ec на Elder и M40:64PASS/1fixtureFAIL/54not-run,38 leaf groups, все процессы закрыты. [Исходный отказ, candidate и syntax verification](Native119ForeignReference-20261110.ru.md).

В новом повторе сохраняются ровно те же119 уникальных IDs. Первый отдельный leaf foreign-reference-1 проверяет исправление; portable-proof6-16 содержит остальные16 исходных portable tests. Затем сохранены все прочие случаи. Группа native-package6-29 поставлена второй для получения actual corpus полного сохранения/переноса модели. Нет исключений или подстановки metadata fixtures. Всего43 leaf groups;310 artifact rules: прежние308 по смыслу сохранены (prefix portable17→portable16), плюс JUnit и actual portable proof первой группы.

Canonical preflight и namespace verification выполняются независимо на двух workers через штатный owned Python controller. Проверяемая физическая source namespace:4078 файлов,8 repositories. Полные source/controls переданы Git pack в новые standalone checkouts. Никакие source/build/runtime прежних работ не обновляются.

| Worker | Source | Новый output |
|---|---|---|
| Elder | `/home/user/timelearner-refactor/source-portable-reference-fixture-elder-a1` | `/home/user/timelearner-refactor/readbacks/s07-native119-foreign-reference-normal-a1` |
| M40 | `/media/user/Data/TimeLearnerRefactor/source-portable-reference-fixture-m40-a1` | `/media/user/Data/TimeLearnerRefactor/readbacks/s07-native119-foreign-reference-normal-a1` |

Build: Release/O3, LLM Off, parallel2, fresh build/runtime. Whole wall12h, leaf4GiB/128tasks, outer8GiB, reservation disk12GiB; free floor512MiB. Elder capacity registry v2 ограничивает slots/memory/disk; M40 registry v1 не обеспечивает количественное суммирование, сохраняются kernel limits и path locks. Эти режимы нельзя объявлять эквивалентными.

[Условия Elder](ValidationPlans/ElderNative119ForeignReference-20261110/canonical-plan.json), [условия M40](ValidationPlans/M40Native119ForeignReference-20261110/canonical-plan.json). Оба independent canonical plan prior_bindings=[]; старые unrelated38/86 bindings не наследуются. Во время предварительного наблюдения старые normal119 leases уже released; посторонняя held publisher lease M40 не удалялась и не объявлялась stale без проверки её владельца.

Runtime ещё не принят: preflight сейчас выполняется, новый full119 не запущен. После положительного canonical readback запускается новый owned native controller. После закрытия всего задания требуется полный compact primary export через Git, независимая сверка всех bytes/точного119set/artifact rules и проверка reader16 на actual package corpus. Далее — два новых Console cold7 сценария и научные прогоны в объявленных условиях.
