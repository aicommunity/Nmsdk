# Этап 4: подтверждённый подэтап и оставшиеся проверки

Последующие TL-017/018: [ProbeMeasurement](ProbeMeasurement.ru.md) фиксирует
зависимость class-image регистрации от pooled TimeStep visibility и ложную
коллизию при смене Environment mode. Исправления Rdk проверены на обоих серверах
полным CTest, дополнительными native controls и ограниченным ASan на M40.
Этим не закрываются оставшиеся OpenProject/CloneChannel и multirate проверки.

Последующая проверка TL-016 и исправление общего режима при присоединении
поддеревьев: [FrequencyContract](FrequencyContract.ru.md). Она отделяет
global-rate экземпляры от detached storage-образов и individual-rate моделей.
Весь этап 4 по этому локальному исправлению не считается завершённым.

Последующее дополнение: [LiveRebuildInit](LiveRebuildInit.ru.md) описывает TL-015
(исправление Init нового Classic Neuron) и новый открытый TL-016 — смешанные
частоты legacy-элементов после создания/growth. Восемь bounded native controls,
четыре коротких regression cases и четыре CTest suites прошли на обоих серверах;
на M40 четыре коротких случая также проверены под ASan. Это не закрывает весь
этап 4 и не подтверждает uniform-rate контур при model clock=20000.

Подэтап 4.1 завершён: коэффициенты NPulseSynapse пересчитываются в штатном Reset
после изменения частоты. На активированном и Init-компоненте старый код оставлял
2/4 при переходе 2000→20000 Гц; исправление даёт 20/40 и возвращает 2/4 при
обратном переходе. Сохранён raw failing test до исправления и passing test после.

Native fixture подтверждает порядок Build→Reset и before/calculate/after,
а fresh Take и Return/Take — эффективную C образа и соответствие внутренних
channel pointers именованным детям. Синтетические вручную созданные компоненты
активируются перед Init, как это делает штатный TakeObject.

Подэтап не меняет scheduler, bool lifecycle, параметры storage-образов и алгоритм
выбора амплитудной цели. Парная научная проверка влияния исправления ещё не
проводилась. Тест коэффициентов не доказывает объяснение всех старых FAIL.

Подэтап 4.2: добавлен native readback через Console --inspect-model. Реальные
Classic и Branch Test-проекты открыты и инициализированы без Calculate на Elder-1
и M40 (Qt5/Qt6). Получены соответственно 609/440 компонентов и 499/364 действующих
property bindings; diagnostics пуст. Старый обход output connectors не видел
прямые SetPointer-связи и давал 0 — он заменён чтением эффективных источников.

Четыре targeted tests и полный PulseLib CTest прошли на обоих серверах. Проверены
scalar/vector slot order, приоритет внешнего источника, отклонение источника вне
графа, C реального storage-образа и обнаружение NaN без исправляющего Build.
Читаются также cached membrane/channel/LTZone/generator pointers. Это ещё не
доказательство равенства Train/Test и не тест импульсного отклика.

Tested root: 5711943703ff8973e4b1460aa4c52e0c5170ef87; Rdk API/doc:
523053ba (полный SHA в runtime manifests); принятый Rdk merge:
4b8cc245b02241964859e1211cdb9c012b2c06f6.
Raw snapshots, журналы, manifest и SHA256SUMS опубликованы в
Reports/StructTrain/TimeLearner/s04-inspection-elder1 и s04-inspection-m40.
Evidence commits: d930feaefd1bfbbebe3fff0af4146c032a86b1bd и
f89323acce29bae1835e101b02e336aa5d2f03b0. Путь/данные сохранены в Git;
сжатые JSON можно повторно анализировать без доступа к серверу.

Подэтап 4.3: исправлен NPulseNeuron::UpdateComputationOrder при
StructureBuildMode=0. Раньше native Build перемещал Soma/LT в начало, оставляя
дендриты позади. XML Load + Init изменял порядок и отклик при том же наборе
связей и сохранённых C/Rs. Теперь режим 0 сохраняет явный порядок графа; 1/2
сохраняют существующий автоматический distal→soma→LT порядок.

На обоих серверах прошли 3/3 targeted tests и полный PulseLib CTest: native Copy,
native XML roundtrip и настоящий повторный Build через изменённый параметр.
Граф {1,2} с двумя soma и неравными C/Rs переносится в explicit full-graph режиме
(UseElementDefaults=false). По 400 отсчётов Copy/XML на каждом сервере дали
max |source-target| = 0; source waveform не плоский. CSV, native XML, readbacks,
журналы и checksums: Reports/StructTrain/TimeLearner/s04-roundtrip-elder1 и
s04-roundtrip-m40. Tested root ef91f639bc66928ca965afd0d71ae69fa9586fe0,
PulseLib 5423fc32076ccba0cbea242708021278d9b7b214,
Rdk docs f28843fa66f9bc6fb1667e2b96fcde1651f7e8f9.

До исправления корректно сериализованный baseline root
87c439cfaa1caccfa824d2dc5fce1566b53ef576 дал максимальное расхождение отклика
0.00010098689993054411. Raw XML/readbacks и failing test находятся в m40/before-fix.
Hash того baseline binary до пересборки не был снят; это ограничение явно
сохранено в baseline.json. Отдельный ранний провал с пустыми Parameters/State
был ошибкой fixture: маска SaveComponent не включала visibility group. Он не
является доказательством дефекта Rdk. Guide сериализации исправлен по native API.

Ограничения 4.3: это pairwise source→target проверка после native Reset, не
универсальный checkpoint и не проверка growth с UseElementDefaults=true.
На момент приёмки 4.3 исходные waveform двух отдельных fixtures различались (диапазоны 0.1938155 и
0.00233225); равенство между независимыми fresh/reuse инициализациями этими
тестами не устанавливается. Это отдельный обязательный контроль следующего
подэтапа; выявленные причины и исправление описаны ниже. Это не основание
объявлять все Reset/reuse контракты подтверждёнными.

Подэтап 4.4: до исправления NConstGenerator::AReset оставлял Output прежним,
только взводя update flag; NPulseSynapseCommon сбрасывал PreOutput, но оставлял
публичную проводимость Output. Потребители до первого native Calculate видели
старое состояние. Source-only/synapse-only native tests воспроизвели оба дефекта;
warm/fresh impulse test дал max difference 0.18559469050032673 после одинакового
Init/Reset. Baseline root 85be9bfd907e36ac05ecf80d7f76acee9c30f7e4 сохранён
в s04-reset-m40/before-fix вместе с runtime manifest и binary hash.

Исправление на уровне владельцев: constant source публикует Amplitude в Reset,
synapse обнуляет проводимость вместе с секрецией. Общий scheduler, computing
order, storage physics и bool lifecycle не изменены. Это не требование нулевого
rest-state: первый soma potential в тесте −1, constant generator output +1/−1.

После исправления на обоих серверах 9/9 targeted lifecycle/roundtrip cases и
полный PulseLib CTest прошли. Copy, XML и warm/fresh traces по 400 отсчётов при
2000 Гц совпадают (max pairwise error=0) и имеют одинаковый ненулевой диапазон
0.0023322486553478683. Сохранены исходные CSV, native XML/readback, checksums и
manifests в s04-reset-elder1 и s04-reset-m40. Tested root:
9e8086af724ff1b8eb851daeb3c6ec3f0e41cf7a; PulseLib code:
9d8bac51ca526ea5d3bd27d6646c9260c5f1e55a; accepted merge:
735fea58af4b1815dc332c7d38af5bf4f68d0855.

Это исправляет проверенную зависимость первого тика от прежнего состояния,
но не доказывает полную эквивалентность всех storage reuse/profile/frequency
комбинаций. Первый отклик старых конфигураций в новом binary может измениться;
исторические replay выполняются с их точными commits. Влияние на августовское
обучение и устойчивость к порядку/ITI остаётся предметом научного A/B этапа 11.

Подэтап 4.5: добавлен opt-in RegisterClassImage в Rdk. Он создаёт отдельную
native копию образа и проверяет параметры/структуру/слоты связей после Init;
возврат исходника в storage не меняет зарегистрированный образ. Совпадающее
имя допускается только при эквивалентном описании поддерживаемого prototype;
другая физика, nonfinite и внешние bindings отклоняются до регистрации.
Противоречие parent defaults с индивидуальными C не исправляется молча —
результат native Copy/Init обязан совпасть с заявленным исходным образом.
Описание служит process-local проверке; portable scientific fingerprint и
полный export профилей остаются отдельными задачами.

При проверке воспроизведён общий дефект UContainer::Copy: InitFlag получателя
оставался от прежнего графа. Реальный нейрон после pool/copy мог сохранять
cached LTZone вне именованного дерева. Исправление выполнено в общем владельце:
native UnInit перед заменой графа и invalidation Ready после CopyComponents.
UNet затем восстанавливает связи; BreakLinks/DisconnectAll могут штатно Build
получателя, поэтому Ready после производного Copy не обязан быть false.
InitFlag остаётся false, и новый граф проходит native Init перед исполнением.
Дополнительных Calculate и learner-specific «пробуждений» Build нет.

На обоих серверах прошли 15 targeted tests и четыре maintained CTest suites:
PulseLib_StorageComponents, UContainer_Components, Test_UComponent_Lifecycle,
Test_UComponent_Properties. Новый общий fixture использует зарегистрированную
storage factory: вариант без storage не исполнял реальный Build и был исправлен.
Legacy UStorage unit target по умолчанию отключён проектом и не засчитывается.
Artifacts: Reports/StructTrain/TimeLearner/s04-images-elder1 и s04-images-m40;
M40/before-fix содержит failing native baseline и runtime binary provenance.
Baseline root 6165ebc9c4ba67be01b3b108d7c2a806df6591d6; accepted source root
5c26aa5d9c976725c27444751b276b4730040cbb; tested Rdk
86ba939a5c81365845f5bda80bdad0e3a10511bf; Rdk merge
c80200bf1cd2bc8beec35546d3022da86afd35c9.

Постановка подэтапа 4.6 — применение registry к декларативной физике и росту
(результат описан ниже):

1. NPulseMembrane сейчас использует один SynapseClassName для Exc/Inh. Для
   разных исходных Rs нужны отдельные optional ExcSynapseClassName и
   InhSynapseClassName с пустым default/fallback к старому полю. Native Build
   должен выбирать соответствующий образ через существующий AddMissingComponent;
   старые конфиги сохраняют прежний выбор класса.
2. Зарегистрировать снизу вверх профили каналов и синапсов, мембран и нейрона;
   uniform C/Rm/kinetics/PSI должны приходить из образов. У новых профилей не
   должно быть повторного UseElementDefaults, стирающего learned Rs/C.
3. Проверить на реальном growth, что старые индивидуальные Rs/C сохраняются,
   новые сегменты и Exc/Inh синапсы получают именно выбранные классы/параметры,
   включая LTMembrane отдельно. Проверять частоту до финального Init.
4. Включить экспорт определений профилей и semantic model comparison в этап 5;
   process-local descriptor registry не подменяет ModelSpec/ConditionSpec.

Этап 4 целиком остаётся в работе: нужны расширенные Copy/XML/growth/rebuild,
heterogeneous profiles, интеграция проверки коллизий в запуск, scalar/vector assignment,
multirate характеристика и сопоставление readback с ModelSpec. Прежние слабые fixtures
не засчитываются как доказательство этих контрактов.

## Подэтап 4.6 — проверены физические storage-профили и рост

Реализована цепочка образов Channel/Synapse → Membrane → Neuron в
PulseLib/Core/TimeLearner/StorageProfiles. Физика задаётся рецептом до Train;
body и LT могут иметь разные C/R/кинетику. UseElementDefaults новых образов
выключен: рост использует образы, а не повторную parent-перезапись всех детей.
Поля ExcSynapseClassName/InhSynapseClassName мембраны имеют пустой default и
fallback к прежнему SynapseClassName. Их ClDesc добавлены в Bin для 13 образов.
Самоприсваивания Ns+1 → Ns в построении нейрона заменены обычным native Build.

При серверной проверке обнаружен общий дефект XML Load: обход VariableMap
применял StructureBuildMode после scalar длины и стирал её (ожидалось 3,
получалось 0). UNet::SetComponentProperties теперь использует порядок
регистрации свойств, как native Copy/Save. Regression проверяет зависимые setter
общего компонента и реальный mode-1 нейрон с последующим ростом после Load.

Полный прогон на M40 выявил аварию при shutdown после 121 успешных assertions.
Общая проверка Rdk отдельно воспроизвела повторный Free: Parent, Child, Child.
ClearObjectsStorage изменён на снимок корней владения и единственный native Free
на корень. ASan отдельно установил heap-use-after-free: ChannelDestroy удалял
Environment до storage; последующий Reset генератора читал освобождённую среду.
Теперь текущая модель освобождается при живой среде, затем уничтожается storage,
затем Environment и logger. Native bool-контракт и scheduler не менялись.

На обоих серверах root 12f450c91755d268180a08d6b04f264f20bff273 прошли 11
адресных проверок (10 profile cases и pooled shutdown probe), четыре maintained
CTest suites. На M40 полный ASan run прошёл 122 tests и shutdown; отдельно прошли
пробы Environment lifetime и очистки storage. ASAN_OPTIONS:
detect_leaks=0:halt_on_error=1 — отсутствие всех утечек не утверждается.

Артефакты опубликованы через Git: s04-profiles-elder1, s04-shutdown-elder1 и
s04-profiles-m40 в Reports/StructTrain/TimeLearner. Сохранены failing baselines,
runtime manifests, XML/readback, build/test logs и реальные waveform CSV.
На каждой частоте сравниваются ненулевые отклики: 200/2000 отсчётов при
2000/20000 Гц, max pairwise error=0. Все 196 хешируемых артефактов раздела
проверены после локального checkout, включая gzip-потоки.

Принятые child develop merge: Rdk b15f4384c4516c865afc59a83b487acd477744d0,
PulseLib 77cc52d06852cef0ddcd256a528283dd90631f49,
Bin 83ab62fcb40f62affd83f66ae68fcd557de55d53. Исходные tested SHA в manifests
сохранены; merge commits их не подменяют.

Рецепт не извлекает автоматически любую legacy-физику. Неописанные поля
наследуются от объявленного базового образа; default — конкретный Asym baseline.
Полная карта применяемых моделей, ModelSpec/export, произвольная смена профиля
живого графа и multirate остаются открыты. Проверки отклика не являются
результатами обучения или независимой оценки распознавания.

Дополнительно принят подэтап TL-019/020: пустая event history Single/Multi,
публикация реальной истории Multi и native dimension ownership PulseCount/Delays.
Проверены default count=1, реальные события в t=0, выключение/Reset и переходы
1→2→1 через scheduler. Полные сведения: [ProbeMeasurement](ProbeMeasurement.ru.md),
раздел серверной проверки повторных проб. Это не проверка всех Multi Copy/XML,
не поддержка его случайной ветви и не исправление RNG при Reset.


## Открытая проверка 31.10: bool при неинициализированном контейнере

При повторном чтении Rdk c903b9bb подтверждён исходный путь
UContainer::Calculate: активный container при InitFlag=false пропускает
вычисления и возвращает false. UModule::Calculate и прочие ранние выходы
возвращают true. Это несоответствие принятому пользовательскому контракту
lifecycle bool, а не доказательство корректной инициализации или обучения.

Исправление Rdk 6084bfa703ebbe0d85d2a588dfe8f79c74cd1144 меняет только
return false на true в этом раннем выходе. Документ Engine-Detailed уточняет
порядок hooks, детей и пропуск неинициализированного контейнера. Адресный gate: реальный
неинициализированный model/container со штатным дочерним компонентом; Calculate
должен вернуть true, сохранив Init/Ready и пропуск children, без скрытого
Build/Init. После штатного Init расчёт выполняется обычным scheduler.
Исправлять только возврат этого раннего выхода; не создавать propagation
ошибок через bool и не запускать children неинициализированного дерева.
Эта открытая проверка не закрывается прошедшими initialized-native fixtures.


### Уточнение native проверки 31.10

Root 492944f266b829aad1840669d779a62d10ae807e / Rdk 6084bfa7 проверены
на обоих workers, но эти запуски **не приняты**: terminal status=1.
В normal XML прошли 14 из 15 cases, включая десять прежних lifecycle,
Classic/Branch fixed-budget и два phase lifecycle controls. Новый bool control
записал uninitialized_return=true, сохранение пропуска children и по одному
вызову parent/child после Init, однако сам case упал на lifecycle.IsCurrent().
Причина — ошибка fixture: revision захвачен до Activity=false; штатный
SetActivity(false) вызывает Reset и меняет revision независимо от Calculate.
Это не основание менять setter или общий lifecycle.

Root 0fca58516941184549fb08ea23fa973e2ebdd30c разделяет наблюдения:
сначала штатный setter, затем snapshot revision и Calculate. Неактивный и
активный неинициализированный вызовы проверяются независимо. Исходный ASan
baseline a1 также использовал ошибочный fixture; его текст «only boolean»
не является доказательством единственной причины failure. Для корректного
отрицательного контроля создан root f34067c64f8f4ab99b1ff7bfb6c7cc7f7d2a3b8c:
тот же исправленный test с прежним Rdk c903b9bb, без изменений физики.

Повторные fixed jobs a2 не дошли до тестов: Elder остановлен по запасу места
(доступно чуть меньше 1.3 GB), M40 — по сокращённому SHA в fetch.
Они не считаются повторными numerical trials. Jobs a3 используют полный SHA;
для Elder предварительный порог 1.25 GB, после сборки по-прежнему требуется
более 1 GiB. До опубликованных raw evidence и проверки обоих workers этот
подэтап остаётся открытым. Полный этап 4 этим gate не закрывается.


### Адресный результат повторных проверок

Fixed a3 завершились с terminal status=0: Elder normal 15/15 cases (8.373 s),
M40 ASan 15/15 (45.143 s), без skips. Baseline ASan a2 на прежнем Rdk
c903b9bb завершил supervisor=0 как ожидаемый отрицательный контроль:
owned native process=1, один testcase и ровно один assertion failure
«Value of: uninitialized / Actual: false / Expected: true».
Остальные lifecycle assertions этого control прошли. Pre/post actual-test
runtime manifests равны, production runner сохранил loaded-file provenance.
Leak detection выключен; полнота mapped-file lifetime не заявлена.

Rdk объединён через --no-ff в develop: 027f7f8353608f83b55f3857a2f6c39138df4c65;
доступность commit в origin проверена. Корневой gitlink обновлён на этот merge.
Это приёмка только раннего bool-контракта; публикация raw proof выполняется
отдельно, полный lifecycle/storage этап и configured phase dispatch остаются открыты.
