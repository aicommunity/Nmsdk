# Native ModelSpec, cold construction и reuse

Подэтап `stage06/native-model-builder` прошёл адресную серверную проверку:
A3 на обоих серверах — 29/29 новых и 68/68 регрессионных; M40 ASan — 21/21,
detect_leaks=0. Дополнительные Ns>1/inhibition controls и независимый аудит
первичных данных завершены. Артефакты A1/A2/A3 сохранены в Git.
Configured ControllerVersion=2
и сериализация полного learner state этим документом не объявляются готовыми.

## Две явные операции

`ConstructNativeModel(NativeModelSpec)` — явное холодное создание: сначала
строятся отдельные Neuron/Dataset из immutable storage images, задаётся частота,
морфология и индивидуальные начальные Ns/Rs, проверяются граф и фактические связи.
Только после успешного preview заменяются прежние фабричные owned children.
Чужие listeners на старых Neuron/Dataset запрещают замену до удаления.
Отсутствующая optional Rs берётся из реального image, не parent fallback.

`AdoptNativeModel(NativeModelSpec)` — read-only приём существующего готового
графа. Проверяются классы, частота, topology/mapping, Ns, заданные Rs и target;
индивидуальные дочерние C/R и неоднородная физика не переписываются.
Adoption не означает, что модель обучена, и не восстанавливает сертификат.

Успешные операции передают управление native path и инвалидируют прежнюю цель:
новый capture/import references остаётся отдельной операцией. Изменения передаются
typed результатом Constructed/Adopted/Rejected/Failed, не public lifecycle bool.
После частично затронувшего owner отказа расчёт блокируется диагностикой.

NativeModelSpec содержит version, topology, storage classes, частоту, режим
вложенного нейрона 0/1/2, начальные attachments/Ns/optional Rs/ISI, allocation
и правила торможения. Allocation не смешивается с learner StructureBuildMode 0/1.
Mode 0 требует реального графа в объявленном образе; отсутствующие узлы не
достраиваются через learner-specific wake passes. New graph не рассчитывается
внутри builder. Все дочерние Calculate выполняет штатный scheduler.

## Параметры и lifecycle

Общая физика целиком принадлежит storage images. Parent uniform overrides и
UseElementDefaults отвергаются; prototype не изменяется. Используется штатный
TakeObject без дополнительного стирающего Default. UnInit/SetGlobalTimeStep,
структурные setters/Build и конечный Init выполняются только на создаваемом
графе до первой пробы. После каждого этапа проверяется effective readback.

В native-owned learner повторный ABuild валидирует текущий граф вместо legacy
BuildStructure/DelComponent(Neuron). Reset сохраняет модель; Build/Init/UnInit
во время активной пробы по-прежнему инвалидируют управление. No-op Build и
исходная инициализация native-owned модели не создают ложную ошибку обучения.
Индивидуальные learned Rs/C не восстанавливаются из устаревших XML anchors.

BeginNativeTraining на существующем legacy-построенном графе один раз снимает
actual declaration и переводит Ns/R metadata в effective readback. Это не
импорт старой цели. Дальнейшие несовпадения parent metadata и actual graph
отклоняются. Изменения L/R выполняются native editor на границе проб; setters
не применяют legacy clamps к новому графу. Retarget меняет только dataset target
и инвалидирует reference/search/certificate; physical model сохраняется.

В declaration-owned режиме typed inhibition rules определяют реальные банки и
Branch solo routing. При scaleInhibitionWithInput начальные отношения Rs
сохраняются для следующих edits; статический вариант задаётся явно.
Legacy inhibition properties не заменяют эту декларацию. Будущий configured
frontend должен адресно преобразовывать/проверять факторы, а не объявлять
неиспользованное legacy свойство действующим фактором.

Compatibility adoption описывает разрешённый Branch muted baseline явно.
Фактическое состояние каждого банка остаётся в semantic model hash; допускается
либо весь bank на объявленном source, либо весь bank штатно выключен. Foreign
source и частично подключённый bank не принимаются. Новое холодное создание
по умолчанию подключает все declared banks; эта политика не меняется задним числом.

## Первая серверная попытка

Root `3904cd40aa1fcb6f1540c950c7ba17e99f88e161`: на обоих серверах 24 новых
cases, 18 failed из-за двух неверных предположений fixture (Environment time
сохраняется; equal-value UProperty assignment не вызывает setter). Два
negative/adoption controls и все четыре cold service searches прошли.
Отдельные 68 regressions: 63 passed, пять Branch service cases отклонены новым
слишком строгим требованием fully-connected baseline. Это ошибка нового
валидатора; она не приписывается старым научным результатам. Исходные logs
сохраняются. Следующая попытка исправляет fixture и явно допускает проверенный
muted baseline, не ослабляя запрет foreign/partial bindings.

## Проверки и оставшаяся работа

Финальная нормальная серия A3 на root
`c1f90650bf7e5e01b848fbb5a278950ae927e641`: на каждом сервере 29/29 новых
и 68/68 регрессионных cases без failures/skips. Дополнительно проверены cold
Ns=3 с индивидуальными Rs, inhibition offsets 1/2, реальные Branch solo bindings,
growth и scaling тормозных Rs от объявленного начального отношения.

Независимый анализ на каждом сервере: 18/18 maintained Python checks без skips,
56 cold-service и 56 legacy-graph-service CSV/packets, по четыре отрицательных
сертификата каждого контура. Все 42 builder-probe packets согласованы с CSV;
наблюдения valid/complete. Это не scientific PASS и не полная mode/physics matrix.
Первая A1, последующая A2 и финальная A3 сохраняются отдельно, включая failures.

M40 ASan: 21/21 addressed cases, без ошибок AddressSanitizer, detect_leaks=0.
Под ASan проверены neuron modes при 2000 Гц, N=6, новые Ns/inhibition controls,
negative/adoption controls и четыре cold searches. 20000 Гц покрыты нормальной
A3; отсутствие всех утечек не заявляется.

Git-пакеты: [Elder-1](../../../Reports/StructTrain/TimeLearner/s06-native-builder-elder1/README.md),
[M40](../../../Reports/StructTrain/TimeLearner/s06-native-builder-m40/README.md).
Локально после Git-получения повторно проверены 3754 stored hashes и 3750 raw
gzip payloads, ошибок нет: [машинная сводка](NativeModelBuilder.validation.json).
PulseLib merge в develop: `5f1a6076edfe2e306e507013a82dc7574ec735d7`.
Включены runtime/source manifests, XML/logs всех попыток, primary CSV/model JSON,
результаты независимого анализа, stored/raw SHA256. Это evidence harness;
production runner/publisher исходного этапа 10 ещё не готов.

На root `51f8579e81909f00170508e99028825230bfd5b9`, PulseLib
`37e8cc47a50712daf98186dae933836b7218a974` завершена попытка A2:
на каждом сервере 25 новых cases и 68 regressions, без failures/errors/disabled.
Повторное чтение XML и source HEAD подтверждено отдельно от вывода задания.
Первичные A1/A2 пакеты опубликованы вместе с финальной A3, а не заменены ею.
См. [актуальную сводку](PlanCompletionAudit-2026-10-27.ru.md).

Пройдены actual storage/Environment проверки Classic/Branch, 2000/20000 Гц,
neuron 0/1/2, learner 0/1, N0/N1 и N=6. Новая модель получает первую пробу без
предварительного Calculate. Проверяются forced Build, Reset, UnInit/Init,
сохранность node identity/heterogeneous C/learned Rs, отказ до live replacement
при неверном spec/listener, read-only adoption и cold native service search.

Остаются configured ControllerVersion=2, portable ModelSpec codec и полный
trained-state import/export, геометрически зависимые Rs domains, вся physics/
inhibition матрица, C-trim/PostTune/calibration и научные контроли. В частности,
optional NativeModelDeclaration — process-local ownership, не controller checkpoint
и не обещание прозрачного Copy/XML всего learner до отдельной реализации codec.
