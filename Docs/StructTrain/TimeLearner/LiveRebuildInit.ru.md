# Classic: молчащий новый нейрон после cold Reset

TL-015 воспроизведён до переноса общей управляющей математики. Причина —
незавершённый native lifecycle нового Neuron в Classic BuildStructure.
Сам контроллер и его математические критерии этим исправлением не заменены.

## Причина и изменение

Native UContainer сначала строит существующих детей, затем вызывает ABuild
родителя. Classic BuildStructure может удалить старый Neuron и создать новый
уже после этого обхода. При live Build корень нового поддерева оставался
Ready=true, IsInit=false. При этом children и связи выглядели корректными.
Проверки структуры или true от Build не обнаруживают такую остановку динамики.
Scheduler не рассчитывает неинициализированный корень, поэтому soma/reference
остаются нулевыми при реальных входных импульсах.

PulseLib ccb399c6bdcdace2814833155416ca82ab736ec2 добавляет в конец Classic
BuildStructure native Init для ещё не инициализированных Dataset/Neuron и
инвалидирование active cache. Такой путь уже присутствует в Branch. Параметры
и mathematical target не меняются; nested Calculate и learner-wide Reset нет.

```text
finish topology/parameter/link construction
invalidate active-child cache
if Dataset exists and is not initialized: native Dataset.Init
if Neuron exists and is not initialized: native Neuron.Init
return to the normal scheduler
```

Условия Rdk Build/Init/Reset сохранены. В частности, структурный Reset может
сделать Ready=false; следующий Build принадлежит scheduler. Проверяющий код не
добавляет отдельные «будящие» Build и не выводит сходимость из lifecycle bool.

## Воспроизведение и доказательства

Исходный PulseLib 4af8184275e182b943bb43df7447f8f7a065d73d. Root ab45be8bbfd0ce9592701f91551244cb61818b31
даёт четыре неуспешных Classic controls (N0/N1, model clocks 2000/20000) при
четырёх работающих Branch controls. Это числа тестовых случаев, не scientific
accuracy 4/8. На обоих серверах Classic имеет реальные восемь stimulus edges,
но soma waveform и references равны нулю; структура не меняется.

M40 diagnostic root a97b1594443d6e64918edf0abed7a863260a56f4 сохраняет полный
effective graph с Init=false именно у Neuron, Init=true у синапсов и корректными
Dataset binding pointers. Runtime manifest относится к этому diagnostic binary.
Hash более раннего M40 eight-case binary не был снят; его producer commit известен,
но точного binary provenance не заявляется. Elder-1 manifest соответствует
своему eight-case binary. Ограничение явно сохранено в baseline README.

Fixed root fd898a3c9813d3bf4ca9d7e5e8988d50366595aa с PulseLib ccb399c:
на обоих серверах проходят все восемь отдельных fresh-process controls и четыре
maintained CTest suites. Manifest снят до запуска. Трёхсекундные controls имеют
неплоский soma response, references и реальное изменение L/Ns; N1 также меняет
индивидуальное Rs. Need остаётся true: полного обучения не заявляется.

Восемь controls используют NSPNeuronGen, N=4, паттерн 0.01/0.08/0.16/0.24,
CalculateMode=1, MaxDendriteLength=8 и отключённый PostTune. Они опираются на
профиль/паттерн августовской базы, но не повторяют весь её протокол и бюджет.
Это не historical replay, не cold retrain до завершения и не independent Test.

Артефакты в Reports/StructTrain/TimeLearner:

- s04-live-init-baseline-elder1 и s04-live-init-baseline-m40;
- s04-live-init-fixed-elder1 и s04-live-init-fixed-m40.

Финальный test-only root 0c92362008415ce1f9a641c46dbc4ee120437983 проверен
отдельно; manifests сохранены в s04-live-init-final-* (см. validation.json).
Четыре коротких regression cases
и 4/4 CTest прошли на обоих серверах. Полный PulseLib suite: 152 cases, 143
passed, девять skipped (восемь opt-in long controls и один helper, исполняемый
в дочерних archive processes). На M40 четыре коротких случая прошли под
ASAN_OPTIONS=detect_leaks=0. Full ASan CTest или leak-freedom для этой правки не
заявляются. Исходники и все артефакты передавались через Git.

Ранние ошибки нового fixture (compiler includes/name collision, лишнее
требование Ready=true после Reset, общий process/pool вместо fresh child)
сохранены отдельно и не выдаются за дефекты learner. N=2 Asym/short-ISI
наблюдение с нулевыми references остаётся неклассифицированной диагностикой.

## Отдельный открытый вопрос TL-016 — эффективная частота

После двух пачек legacy control с clock=20000 обнаружен смешанный граф.
Например Classic N1 на M40: 15 узлов с 20000 и 64 с 2000 Гц; все узлы Init=true.
При clock=2000 все 79 узлов этого случая имеют 2000 Гц. Raw distributions по
каждому case сохранены в fixed validation.json и readbacks. Сходство outputs
N0/N1 за две пачки не доказывает эквивалентность этих алгоритмов.

SetGlobalTimeStep изменяет существующее дерево, но сам по себе не определяет
частоту образов, создаваемых позднее. Требуется закончить storage/profile и
growth contract нового контура; existing multirate остаётся compatibility.
Эти прогоны не доказывают uniform-rate поддержку 20000 и не разрешают новый
контроллер на смешанном дереве. Нельзя пересчитать исторические результаты
как uniform-rate только по частоте корневой модели.

Августовские визуально подтверждённые 4/8–6/8 не отменяются. Загрузка готового
графа и его обычный Init отличаются от обнаруженного live replacement. Для
исторического replay, cold retrain, порядка/ITI всё ещё нужны отдельные прогоны.

## Принятая Git closure

PulseLib develop merge: 55a5906cde40b1f93630bef00610bc47f7a0cf5c.
Bin develop merge (только документация): 1c1c2e5064373b47d523fd6735aebe6785f2787d.
Оба опубликованы до корневого merge; production Core совпадает с проверенным
ccb399c6bdcdace2814833155416ca82ab736ec2. Математическая extraction-ветка
ad955ba15409db32920f06867f4d5acdcd3caefd в эту closure не включена.
