# Наблюдение фактической ревизии модели

Подэтап `stage06/model-revision-observer`. На обоих серверах прошли 85/85
основных адресных C++ cases снимка `1f1e0352bce24bc538d888e20f4e20ebc4906339`.
Следующий test snapshot `87e444b67ef471d79cb8277630472ee1a090226c` добавляет
замену свойства и удаление declared source: 12/12 addressed cases и отдельно
20/20 regressions старого provider на каждом сервере. M40 ASan: 59/59 без
пропусков, `detect_leaks=0`. Включены восемь observer, семь full identity,
две native A/B на 2000 Гц, 13 service, 18 final verification и 11 bounded
search cases. Native 20000 Гц покрыты обычной A1, не этой ASan-подвыборкой;
отсутствие утечек не заявляется.

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

## Измеренное ускорение и данные

Одинаковый реальный граф из 169 nodes, шесть входов, 2000 Гц:
128 последовательных чтений стоят 3.8882/3.8631 с полным IdentifyModel
и 0.04655/0.03863 с observer на Elder-1/M40 соответственно. Отношение
стоимости чтения — 83.52/100.01. Здесь динамика не рассчитывалась: это
измерение read overhead, не ускорение всей симуляции в сто раз.

Реальные A/B-пробы двухвходовых Classic/Branch на 2000/20000 Гц ускорились
в 6.36–8.35 раза. Обе реализации provider используют одинаковые physics,
native reset/scheduler и assigned whole-burst protocol. Массивы stimulus и soma
совпали точно, relative timestamps — в пределах 1e-12 с; полные model hashes
совпали. Это адресное измерение, не обещание такого коэффициента для любой
длины, топологии или загрузки сервера. Стоимость больших production graphs
ещё должна измеряться в требуемой научной матрице.

Все 18 maintained Python data/corruption tests прошли на каждом сервере без
skips. Auditor 3 проверил новые 56 actual service CSV/packets и четыре
отрицательных certificate summaries, а также четыре isolated/assigned packets.
Отдельный анализ прочитал CSV всех четырёх A/B-пар и счётчики full/cache reads:
полные captures на границах действительно выполнялись. Runtime, compiler flags,
source closure, interpreter/module digest и первичные данные публикуются в
`Reports/StructTrain/TimeLearner/s06-model-observer-elder1` и
`s06-model-observer-m40`. Recognition verdict не вычислялся.

Пакеты опубликованы commits Elder-1
`9e8f5184fbdddee7962619dea85e2df182517d2b` и M40
`4325abdeb19f1ca8b5a0cd9869a92ff828349eaf`. После получения через Git
локально проверены 787 hashes сохранённых файлов и 783 распакованных payloads;
совпали пять cross-host semantic model identities (benchmark и четыре A/B).
PulseLib принят merge commit `38e977c674f999675d469198269c8937c83cce5e`;
корневой merge следует после него. Scientific/mode matrix остаётся открытой.
