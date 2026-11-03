# Явный начальный порог native-модели

Подэтап следует обнаруженным [различиям профиля](ScientificProfileDrift.ru.md)
и [первому stock Train](StockPhaseAPreflight.ru.md). Исторический legacy Train
использует TrainingLTZThreshold100, тогда как native V2 не применяет этот legacy
knob и сохраняет actual threshold из модели. Сравнение0.0117/100 должно быть
явным, без скрытого изменения default или общего storage prototype.

## Контракт

| Native ModelSpec | Построение |
|---|---|
| schema1 | Прежний wire format и порог из storage, без дополнительных полей |
| schema2 | Обязательный finite scalar `initial_threshold`, применяемый только при cold construction |

Ноль и отрицательное значение разрешены явно, как в native scalar threshold
calibration; boolean/NaN/Inf/unknown fields/schema downgrade отвергаются.
Остальная физика берётся из прежних storage-образов. Для stock-проверки нет
LTMembrane и не меняются C/R/кинетика. Встроенные frequency-encoding LTZone и
неизвестные scalar overrides не получают вымышленной поддержки: используются
те же typed capability guards, что у native threshold candidates.

Последовательность: построить private neuron/структуру/банки → применить
initial threshold к его LTZone → штатный Init → повторно найти **фактический**
LTZone и проверить значение → проверить граф/интегратор → attach и fingerprint.
Ни одного Calculate в этом пути нет. Build/Reset/Calculate возвращаемые bool
не используются как новый канал ошибок; диагностика остаётся typed native.

Inspector, Reset, growth и import не применяют initial threshold повторно.
Поздний recognition/calibration threshold принадлежит текущему графу и своему
происхождению. Старый certificate Exact не переносится на изменённую модель.
Автоматического скрытого перехода к порогу0.0117 после Need=false не добавляется.

## Скрипты и проверка

`stock-phasea-preflight ... --initial-threshold 100` создаёт ModelSpec2.
Отсутствие опции сохраняет ModelSpec1 и штатное значение образа. Production
pipeline и completed/stopped readers проверяют wire version; preflight/Train
дополнительно сравнивают actual initial LTZone.Threshold с декларацией.

Добавлены10 native tests с реальными storage/Environment и обоими learner:
Classic/Branch ×2000/20000 Гц, два legacy controls, strict codec/signed values,
unsupported LTZone до attach, read-only inspection после другой scalar value
и Return→Take после освобождения модели с порогом100.
Проверяются actual child, отсутствие LTMembrane, прототип, clock и повторные
Build/Init/Reset, а не только bool результата. Три Python reader tests требуют
actual ModelSpec2 preflight, отвергают malformed versions и rehashed readback
mismatch. AST/source checks локальны; численные/integration checks — серверные.

До их завершения реализация не принята. Для научного сравнения заранее выбрать
обе threshold values0.0117/100 и выполнить оба варианта на одной новой сборке;
сравнение только старого runtime с новым не выделяет причинный эффект порога.
Все прочие bounds, CapturedPerInput, amp1e-5/rel0 и sync0.02 сохраняются.
После валидного cold Train — полный export/import и реальные calibration/Test
с temporal reports. Отрицательный результат не превращается в неразделимость
всех моделей, а invalid candidate не становится доказательством infeasibility.

## Парный production workflow

### Серверная проверка реализации: промежуточное состояние

Попытка A1 на Elder не дошла до native tests: GCC обнаружил отсутствие
`template` у зависимого вызова `GetComponentL` в новом тестовом fixture.
Исправление — root `7ffec7acbf7f1f9884c713aaf22e6d852f6d4ce5`.
Production Pulse Core при этой ошибке уже компилировался; это не подтверждает
корректность нового construction path. Ни один из14 тестов не считать пройденным.

Артефакты отказа сохранены в commits
`268fe310c43385599d124e6823fbdc28fc19b961` (A1,60 members) и
`394d90462c928d9a7acd7feac7e59a4129f6a154` (A2,5 members).
Локально независимо проверены outer/member SHA256, размеры и явное
`acceptance_status=not_accepted`. A2 правильно отказался запускать readback
после незавершённой сборки. В его подготовленном обходном пути также выявлено
неверное имя импорта native gate; A3 использует реальный `run_native_gate`.

A3 запущен на Elder в отдельных source/build/runtime/framework каталогах
`initial-threshold-normal-a3` с исходниками root7ffec7acb / Pulse541bf89b.
Исходные каталоги A1 не изменяются. До фактического результата A3 отсутствует
приёмка14 native tests, двух preflight100 и трёх reader tests; cold pair ещё
не выполнялся. Эти состояния не означают завершения этапов4/7/11.

### A3:13 реальных pass, один неверно заданный negative fixture

A3 завершил полную сборку и все14 cases;13 прошли. Единственный failure —
`NativeInitialThreshold/UnsupportedZoneIsRejectedBeforeAttachment`: fixture
передал C++ имя `NPulseSimpleLTZone` в поле имени storage-образа. В реальном
CreateClassSamples этот образ зарегистрирован как `NPSimpleLTZone`.
RegisterStorageProfile корректно выдал `missing_profile_template` до вызова
проверяемого construction API. Поэтому отказ не проверял требуемую диагностику
неподдерживаемой scalar threshold semantics.

Исходный A3 proof `0edde4558c2ad8035688afb2133752aa8f31c481` остаётся
`not_accepted`; независимо сверены132 members,424 exact root/child Git source
hashes и фактический XML14/13/1. Supported stock100, legacy image,2000/20000Hz,
repeated Build/Init/Reset, codec и pool controls прошли в этом scoped запуске.
Это не общий14-case pass. Source hashes дочерних файлов проверены по точному
gitlink Pulse541bf89b, а не попыткой читать submodule contents из root tree.

Первая cold pair закономерно отказалась до Train: proof
`e8d882f7740aa36cf7215de6999c3ed533038ef1`,5 members/289 source hashes сверены.
Исправление fixture в root `ed12d19c7a43d7e35fa15e209159aa219b0fd61d`
использует `NPSimpleLTZone` и сначала требует реальный `CheckClass`. Ожидаемые14
test names и production Pulse Core не изменены. Stock scientific model по-прежнему
имеет NPulseLTZoneThreshold и не содержит отдельной LTMembrane.

Новая A4 выполняется в отдельных source/build/runtime/framework каталогах на
Elder. Pair A2 ждёт конкретного A4 owner; при отказе не начнёт обучение.
Исходные A3 source/runtime не изменяются. До фактических A4 и pair результатов
приёмка14/2/3 и четыре cold обучения остаются pending.

`model.schema_version=2` — версия вложенного NativeModelSpec с initial threshold;
она отлична от версии внешней cold configuration (cooperative policy и C-search
имеют собственные внешние версии). Их нельзя объединять по одному числу2.

`stock-threshold-study prepare/run/analyze` использует прошедший native
preflight100 как источник stock-конфигурации. `run` требует тот же runtime
manifest и code identity (Pulse Core/Rdk Core trees и hash Console driver).
Алгоритмическая идентичность дополнительно привязана к фактическому executable
SHA; путь binary и attempt ID в ConditionSpec не включаются.

Все четыре job specs, ожидаемые полные initial identities и ConditionSpec
создаются до первого нового native вызова. Два значения порога для одной
топологии имеют полностью одинаковые прочие факторы. Все четыре preflight
должны совпасть с ожидаемыми графами прежде, чем начинается хотя бы один Train.
Ожидаемая модель получена из actual stock witness заменой только declared
LTZone.Threshold; это проверяемая гипотеза конструкции, а не подмена actual
readback. Каждый Train создаёт fresh native model и сравнивается со своим
preflight. Никакого warm import или шаблонного Test нет.

После Train reader дополнительно проверяет фактический архив конечного нейрона:
LTMembrane отсутствует, число сом и LTZone/feedback connections сохранены,
все новые мембраны имеют исходные классы и C/R/Rrest/FB/Type, кинетика синапсов
и PSI не изменены, порог равен исходному. Индивидуальные обученные Rs и рост
дендритов разрешены; это не сравнение конечной модели с неизменённым шаблоном.
Четыре адресных reader tests используют реальные cold пакеты двух топологий
и отклоняют rehashed добавление LT, изменение C и перенаправление feedback.
Серверная проверка A2 завершена:4/4 без errors/failures/skips, evidence commit
`613bb241d06cce32f4881b351365f6c59090be2d`. Использованы actual initial/final
graphs из исходного cold proof `322409d685f20ab6b0be03f7d69e69399f127239`;
численные прогоны не повторялись. Независимо проверены7 archive members,
outer/member hashes,289 точных Git source hashes и фактический reader result.
Это подтверждает scoped reader, а не сходимость cold Train. A1 остановился
до reader из-за отсутствующего Git object исходного proof; в A2 добавлен его
явный fetch. Отказ A1 сохранён в `0f3df5456328ca7fbb37a1d89117acc8d524f93b`.

Серия `s07-stock-threshold-pair-normal-a1` поставлена на Elder в ожидание
конкретного owner A3. При его отказе серия завершится без Train. При принятом
A3 она использует неизменённый native runtime root7ffec7acb и отдельный
Python code snapshot74369ef34; SDK не обновляется. Декларации четырёх условий
формируются production workflow до первого native вызова. Это ещё не результат
четырёх обучений и не проверка классификации.

Четыре cold runs — по одному на условие. Генератор и остальные декларации не
получают случайности от нового attempt ID. CapturedPerInput, bounds, Ns1,
амплитудные/временные допуски, full-window assignment и budgets остаются ровно
из source preflight. Данные передаются production native_pipeline_worker.
Валидные invalid_observation/search_unresolved/budget_exhausted сохраняются
отдельно от ошибок выполнения; положительная сходимость не требуется для
приёмки достоверности эксперимента.

`analyze` повторно проверяет каждый portable manifest, actual graph/runtime,
параметры источника, все условия и producer outcomes. Три server reader checks
требуют реальные четыре runs и проверяют missing condition и независимость
fingerprint от attempt/path. Classification/calibration этим workflow не
оцениваются. Они следуют отдельным этапом только для фактически полученных
состояний, с честной маркировкой stopped diagnostic при отсутствии certificate.

## Итог A5 и четырёх холодных stock-контролей

Предыдущие записи о pending A3/A4/A1 относятся к хронологии попыток.
A4 снова дал13/14: отрицательный fixture ошибочно требовал отсутствия детей
после отказа, хотя TakeObject уже создаёт их. Исправление теста проверяет
сохранение существующего графа, target, порядка и clock при typed rejection;
production-физика и диагностический контракт не ослаблены.

A5 завершён: `d7471b10d2ea744fb75034f72c871793a38c9893`,14/14 native,
два zero-tick stock preflight100,3/3 readers. Независимо проверены350 members,
426 точных Git source hashes и неизменность прежнего runtime до/после.
Это повторная сборка в закрытом source/build A4 с новым runtime A5, а не новый
чистый checkout. Native root `5c4adf7ed3b2dcd977c763846d7f4010b67869d3`,
Pulse `541bf89b9966f63ca5131fa57a31a9ae3f5820ea`. Qt6/ASan-проверка этого
изменения ещё не выполнена; общий этап lifecycle не закрывается.

Cold pair A3 завершён: `e5fa71d745119af0d818059f497dd226f4c7c25d`,
четыре preflight и четыре cold Train,3/3 readers. Проверены1370 members,
289 точных source hashes. Все четыре execution завершены и пакеты валидны,
но обучение остановилось с invalid_observation. Train certificate отсутствует,
classification не оценивалась; шаблонный Test не запускался.

| Условие | Последняя проба (числовой suffix) | Фактические L | Волны | Причина |
|---|---:|---|---:|---|
| Classic0.0117 |8|1/1/1/1|12|ambiguous input0|
| Classic100 |108|54/1/1/1|3|missing input0|
| Branch0.0117 |8|2/2/2/1|7|ambiguous input2|
| Branch100 |476|15/15/15/1|3|missing input2|

Каждая последняя проба имеет3601 samples, complete=true, window_closed.
Полнота наблюдения не означает существование однозначно назначаемого пика.
Декларация maximum_invalid_observations=0 останавливает поиск при первом
таком результате; это не доказательство PhysicalInfeasible. Увеличение порога
изменило траекторию поиска, но не обеспечило завершённого обучения.

[Точный readback и hashes источников](StockThresholdStoppedReadback.json)
выбирает последнюю пробу по числовому суффиксу, а не лексикографически:
trial99 не является последней при наличии trial108 или trial476.

Следующий алгоритмический разбор: проверить assignment на реальных waveform,
историю лучших измеренных кандидатов, переходы Reject/rollback и ограниченное
восстановление после неудачного кандидата. Не подменять отсутствующий пик ETA,
не ослаблять допуски и не менять штатную пачку одиночным импульсом. Отдельная
диагностическая оценка остановленного состояния допустима только с явной
маркировкой незавершённого Train, исходным порогом и frozen model hash.
Эти контроли без LT не изолируют причинный эффект LT относительно прежнего
двухвходового профиля: различаются и другие параметры/размерность.

## Qt6/ASan SDK: независимая проверка в процессе

На M40 запущен отдельный SDK с root
`ddfe1f39d40373daab1d4e2894a9c822c90a288f`, Pulse541bf89b,
папками source/build/runtime/framework-initial-threshold-asan-a2.
Owner3428746 подтверждён живым; CMake build выполняется с одним потоком.
Конфигурация RelWithDebInfo: -O1 -g1 -fsanitize=address,
-fno-omit-frame-pointer; private GTest58d77fa8070e8cec2dc1ed015d66b454c8d78850,
системный GTest отключён. Исходники и runtime работающего H21 не изменяются.
Git object donors зафиксированы и сохраняются до dissociation.

Декларация приёмки:14 native tests, фактический libasan mapping,
два zero-tick stock preflight100 и3 readers. Начальные модели должны целиком
совпасть с опубликованными normal A5 readbacks. Не запускается новый cold Train.
Эти проверки не доказывают все режимы ModelSpec2: калиброванный roundtrip с
конечным порогом, отличающимся от construction value, остаётся отдельным gate.
До terminal/primary проверки ASan pass и develop merge не заявляются.

Первоначальный a1 был только ожидающим процессом3426523: ни исходники, ни
build/runtime не создавались, расчётов не было. После измерения свободных RAM
и12 CPU этот owned waiter остановлен с сохранением superseded.json, чтобы
не откладывать независимую однопоточную сборку до конца многочасового H21.
A2 использует новые каталоги; прежние сведения не удаляются.

## Дополнительный native contract: сохранение последующего значения порога

Добавлены четыре адресных теста Classic/Branch ×2000/20000Hz в существующий
Test_PulseLib_InitialThreshold.cpp. Декларация native-initial-threshold-v2.json
содержит18 cases; прежняя v1 с14 cases сохранена. Текущий ASan a2 с rootddfe
выполняет прежние14 и не считается проверкой новых четырёх.

Fixture строит реальный stock NSPNeuronGen без LT с ModelSpec2.initial_threshold100,
затем между измерениями явно меняет единственный LTZone threshold на0.005.
Это idle instance edit; state_kind=model_spec, training.status=not_trained,
calibration.status=fixed. Сертификат или результат подбора порога не создаются.
Полный ModelArchive с image closure и DatasetSnapshot импортируется в новый
owner, который до замены действительно имел construction threshold100.
Применяются common CommitNativeLearnerChildren и public AdoptNativeModel:
обновляются штатные child aliases, а не сохраняются старые указатели.

Проверяются весь semantic graph, фактический0.005 после Build/Init/Reset,
неизменность clock при переносе и prototype0.0117. Реальный root scheduler
рассчитывает оба дерева; первые60ms штатной пачки (до второго импульса) должны
дать одинаковые фактические input, soma и LTZone output traces. Ненулевой
input/response и finite samples обязательны; это проверка физического переноса,
не обучение на одиночном импульсе и не модель динамического checkpoint.
Исходный archive записывается до paired run, чтобы сохранить контекст отказа.

Все18 cases выполнены на Elder (Qt5/GCC11 Release) и M40
(Qt6/GCC13 AddressSanitizer, detect_leaks=0). Продукционный код Pulse541
не изменён. Физический roundtrip не заменяет отдельный
calibrated-recognition-state roundtrip ModelSpec2.

## Подтверждённый физический roundtrip18, 2026-11-04

Normal A2: root63d861e823aea132625b22f3702ac11c3d1e7320,
evidence60f5905c7b04ac41f16d405d2fe715f1e3eed174. Фактический GTest XML:
18 tests, 0 failures/errors/disabled, 43.570s.
ASan A1: тот же root и Pulse541bf89b9966f63ca5131fa57a31a9ae3f5820ea,
evidencecd3a477ee03f5f75b2d71af83772ec6dce5dda1e. Фактический XML:
18 tests, 0 failures/errors/disabled, 300.608s. Реальный libasan mapping
проверен по loaded-files; отсутствие утечек не заявляется.

В каждом пакете независимо проверены все97 members и430 hashes исходников.
Исходники обоих запусков совпали с точными Git blobs. В четырёх новых
readbacks подтверждены полная semantic identity графа, untrained metadata,
ModelSpec2.initial_threshold100, effective threshold0.005 и отсутствие
LTMembrane. Все paired input/soma/spike samples конечны и попарно равны:
121 samples при2000Hz,1201 при20000Hz. Есть ненулевой стимул и изменение
потенциала сомы; проверка не сводится к сравнению двух молчащих нулевых трасс.

Использованы закрытые SDK/build с заменой только тестового CPP и новым
runtime каждого запуска. До/после сохранены и сверены байты/realpaths прежних
runtime. Первоначальная compile failure Normal A1 остаётся в readbacks;
она не подменена успешным A2. Полные97-member primary archives занимают
295424 и370876 bytes в Git; изображения не добавлялись. Доступность всех7
точных child commits проверена по удалённым refs и записана в ASan-пакете.

Оба отчёта опубликованы и объединены в рабочую feature-ветку через --no-ff.
Эти адресные gates закрыты; полный этап4/5 и calibrated-recognition-state
roundtrip ModelSpec2 не завершены. Научного результата обучения эти fixtures
не создают. Проверка H21 и полный80-pair визуальный отчёт остаются отдельными
заданиями.

## Следующая проверка: ModelSpec2 и полный калиброванный recognition package

Добавлены NativeCalibratedModelSpec2.ClassicN1_2000/BranchN1_2000 и gate
native-calibrated-model-spec2-v1.json (два новых и два исходных schema1 cases).
Вариант использует существующий реальный LearnedBoundary и production
configured controller; математическая цель, допуски и физика не меняются.
ModelSpec2.initial_threshold1 передаётся до холодного configured Build.
После реального обучения выполняются измеренные search и отдельное fresh
confirmation, формируется полный NativeCalibratedState и проверяются
строгий импорт, сохранение после Build/Init/Reset и frozen responses.

Новая schema2 ветка дополнительно импортирует пакет в отдельный свежий
learner, сохраняет весь пакет и исходный recognition graph, проверяет
фактический выбранный порог (отличающийся от construction1), отсутствие
training certificate/references у распознающего owner и выполняет реальные
frozen probes через корневой scheduler. Первичные transfer и response
readbacks сохраняются; схема1 проходит прежний неизменённый сценарий.

Область: двухвходовый инженерный профиль с LTMembrane, существующая primary-pair
same-matrix calibration, N1,2000Hz. Это проверка API переноса, не stock science,
не независимая оценка и не полная матрица всех вариантов. Новые cases пока
не собраны/не выполнены; gate остаётся открытым до серверной проверки.

### Первый запуск полного calibration gate: отказ до калибровки

Rootf32de33257dd67e84962926f1225b1a6f6b29fcd/Pulse541, Elder Normal A1:
4 tests,4 failures,0 errors,46.412s. Все четыре (оба прежних schema1 и оба
новых schema2) завершают Train причиной maximum_sweeps_exhausted и не имеют
training certificate. Калибровка и distinct-owner transfer не выполнялись.
Reader-worker корректно отказался от анализа как успешного calibration.
Это не доказательство дефекта schema2, import или калибровки.

Выявлена ошибочная предпосылка выбора контрольного fixture: старый
LearnedBoundary использует ISI[.01,.08],L0=2,Rs0=86MΩ и область первого
L=2..3/Rs=86..172MΩ, depth0,4 candidates,1 sweep. Подтверждённый положительный
production N1-контроль MeasuredResistanceRefinement имеет другие условия:
ISI[.01,.03],L0=1,Rs0=86MΩ,L=1..3/Rs=43..86MΩ,depth4,80 candidates.
Успех последнего нельзя переносить на первый. Изменение tolerances либо
автоматическое увеличение бюджета старого fixture не выполняется.

Следующий шаг — выбрать согласованный реально достижимый source для проверки
полного переноса и объявить его условия до Train; исходный отрицательный
контроль сохранить. В fixture добавлен terminal training summary перед
фатальной проверкой certificate, чтобы такой отказ сохранял состояние поиска.
Это только observability change, пока не собранный на сервере; активные SDK
не меняются. ASan A1 на момент первого normal readback ещё выполнялся.

ASan A1 затем завершился:4/4 failures по той же precondition,324.753s,
без ошибок интеграции/сообщений о memory error в проверенных test failures.
Это не общий ASan pass: тесты остаются failed. Normal proof
470a9251af14e50f47e89815edafe5b6d7471513 и ASan proof
29da1f5bc1dfdd401d8bceb97cc7650f537dd5b5 опубликованы. Независимо сверены
154/153 members,431 точных hashes исходников, реальные XML failure messages,
libasan mapping ASan и прежние runtime до/после. Калиброванных пакетов и
transfer readbacks в архивах нет. Оба reader-worker закрылись prerequisite
refusal; четыре reader-теста не запускались и успешными не считаются.

Следующая проверка должна использовать повторение точного опубликованного
положительного N1 production job с изменением только model.schema_version2 /
initial_threshold1 и соответствующий schema1 контроль. Реальные source
declarations и storage definitions берутся из Git primary, не из короткого
LearnedBoundary. Полная CLI-цепочка train→export→measured calibration→fresh
evaluation должна оставлять действительный source-case и полный calibration
proof. Исходные допуски и CapturedPerInput сохраняются; новая постановка
декларируется отдельно и не заменяет нынешние отрицательные результаты.

## Production replay вместо короткого calibration fixture

Команда model-spec-transport prepare восстанавливает точные206 primary members
из baseline proofbcbd30f1d87e352825e6c8400c5b929eff184ae5. Проверяются SHA256
архива/manifest и каждого member, исходные native manifests и действительные
Exact source certificates. Schema1 job полностью совпадает с опубликованным;
в schema2 меняются только вложенные model.schema_version/initial_threshold1
и производный digest. Physics/storage archives, ISI.01/.03, CapturedPerInput,
допуски, bounds, бюджеты и режимы остаются прежними. Четыре jobs записываются
до первого Train; оба варианта должны восстановить тот же effective cold graph.

Команда model-spec-transport run использует production CLI train/export/
evaluate/calibrate. После настоящего Exact выполняется identity export,
полные nonspiking proposal probes для заранее объявленных target[.01,.03]
и dispersed foil[.01,.24] (2kHz,reset-per-trial,0.4s). Пики лишь предлагают
конечную сетку порогов. Каждый кандидат и свежий confirmation измеряются
штатным native calibration transaction; NonSeparable сохраняется как
отрицательный исход и не создаёт calibrated package.

При calibrated результате новый процесс Console импортирует полный пакет
и выполняет четыре frozen probes с target на обеих позициях. До/после
сверяется весь пакет и выбранный threshold, отличный от construction1.
Нельзя подменить отсутствие source certificate шаблонной моделью. Все
подготовленные данные должны остаться побайтно неизменными.

Область — сохранённый двухвходовый инженерный LT профиль и primary-pair
historical_same_matrix calibration, не stock science и не independent Test.
Три подготовительных теста проверяют реальные pinned primaries, неизменность
job и геометрию trial design; три итоговых — genuine Train, calibration
provenance и complete frozen import. Пока серверное выполнение не завершено,
полный transport gate остаётся открытым.
