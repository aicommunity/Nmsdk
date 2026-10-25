# Этап 4: подтверждённый подэтап и оставшиеся проверки

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
Исходные waveform двух отдельных fixtures различаются (диапазоны 0.1938155 и
0.00233225); равенство между независимыми fresh/reuse инициализациями этими
тестами не устанавливается. Это отдельный обязательный контроль следующего
подэтапа, а не основание объявлять все Reset/reuse контракты подтверждёнными.

Этап 4 целиком остаётся в работе: нужны расширенные Copy/XML/growth/rebuild,
heterogeneous profiles, коллизии образов, scalar/vector parameter assignment,
multirate характеристика и сопоставление readback с ModelSpec. Прежние слабые fixtures
не засчитываются как доказательство этих контрактов.
