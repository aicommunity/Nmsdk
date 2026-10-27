# Наблюдение фактической ревизии модели

Подэтап `stage06/model-revision-observer`. Реализация подготовлена; серверная
приёмка и измерение ускорения этой редакции ещё ожидаются.

`ModelRevisionObserver` — process-local read-only ускоритель существующего
`IdentifyModel`, не новая научная идентичность. Он не владеет компонентами,
не вызывает Build/Reset/Calculate, не сохраняется как checkpoint и используется
в одном штатном scheduler thread. Caller предоставляет живой root и ports.

При первом чтении и любом обнаруженном отличии выполняется полный IdentifyModel.
Повторное использование hash допустимо только после проверки:

- lifetime/ready/init/frequency/class каждого узла;
- именованного членства и порядка детей, карты и порядка свойств, адресов,
  runtime types и masks свойств;
- точных scalar/vector/matrix параметров всех поддержанных identity типов;
- actual input-slot sources, connected/external/inspectable, aliases;
- cached membranes/channels/LTZone/positive/negative generators;
- конечности physics readback, который полный inspector проверяет дополнительно,
  включая state TimeConstant;
- фактических объявленных boundary ports и lifetime их владельцев.

Перед чтением сохранённых typed property pointers проверяются lifetime и
принадлежность всех владельцев/свойств. UEPtr в Rdk является обычным указателем;
одной проверки ненулевого значения недостаточно. Смена свойств или native growth
заставляет повторно построить снимок из актуального дерева. NaN/Inf не могут
сохранить прежний valid hash; unsupported model остаётся ошибкой полного identity.

Dynamic state и presentation values исключены ровно по прежнему контракту
identity; значения подключённых параметров заменены их actual bindings.
Изменение сигналов на таком источнике не объявляется изменением физической
модели. Фактические stimulus physics/pattern проверяет native executor отдельно.

В native training adapter observer принадлежит callback конкретного плана.
Before/After probes проверяют реальные значения на каждом тике; optional
readFullModelRevision принудительно делает полный capture до/после reset,
routing/prepared callback и при закрытии/восстановлении пробы. Старый provider
без callback продолжает полный путь как раньше. Счётчик собственных edits и
форматированные строки не используются как замена observed parameters.

Проверки сравнивают observer с production IdentifyModel после мутаций всех
поддерживаемых семейств типов, masks, aliases, bindings, частоты, lifecycle,
native caches, growth/reuse и nonfinite values. Native A/B использует реальные
Classic/Branch на 2000/20000 Гц, сравнивает полные stimulus/soma arrays и actual
model hash. Tiny external C edit во время service пробы обязан остановить её
до следующего расчёта children. Benchmark отдельно измеряет стоимость чтения
на реальном 6-input graph; ускорение не доказывает научную сходимость.

Это не закрывает configured ControllerVersion=2, длительности проб, полные
trained-state transfer, динамические Rs domains или mode/physics матрицу.
