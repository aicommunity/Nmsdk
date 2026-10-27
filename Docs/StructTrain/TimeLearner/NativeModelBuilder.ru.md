# Native ModelSpec, cold construction и reuse

Рабочий подэтап `stage06/native-model-builder`. Реализация подготовлена;
серверная проверка этой редакции ещё ожидается. Configured ControllerVersion=2
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

Подготовлены actual storage/Environment проверки Classic/Branch, 2000/20000 Гц,
neuron 0/1/2, learner 0/1, N0/N1 и N=6. Новая модель получает первую пробу без
предварительного Calculate. Проверяются forced Build, Reset, UnInit/Init,
сохранность node identity/heterogeneous C/learned Rs, отказ до live replacement
при неверном spec/listener, read-only adoption и cold native service search.

Остаются configured ControllerVersion=2, portable ModelSpec codec и полный
trained-state import/export, геометрически зависимые Rs domains, вся physics/
inhibition матрица, C-trim/PostTune/calibration и научные контроли. В частности,
optional NativeModelDeclaration — process-local ownership, не controller checkpoint
и не обещание прозрачного Copy/XML всего learner до отдельной реализации codec.
