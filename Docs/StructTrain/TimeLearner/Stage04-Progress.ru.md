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

Этап 4 целиком остаётся в работе: нужны Copy/XML roundtrip, growth/rebuild,
heterogeneous profiles, коллизии образов, scalar/vector parameter assignment,
multirate характеристика и сопоставление readback с ModelSpec. Прежние слабые fixtures
не засчитываются как доказательство этих контрактов.
