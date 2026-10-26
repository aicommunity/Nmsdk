# Native executor: проверенный внутренний контур

Подэтап разработан в stage07/native-probe-executor корня/PulseLib и
stage07/lifecycle-observation Rdk. Серверная приёмка описанного ниже внутреннего
API выполнена. Это не завершённый общий контроллер или весь этап 7.

## Путь исполнения

QueueNativeProbe ставит относительную ProbeSpec в очередь. Learner BeforeCalculate
проверяет готовность/частоты, фактический Dataset ISI, отсутствие concurrent
legacy PostTune/C-trim edits и поддерживаемый generator-режим. Затем сбрасывает
только Dataset/Neuron, считывает model-defined baseline и применяет временный
Branch solo overlay. Callback onPrepared вызывается до первого native stimulus.
После обычного расчёта children learner ACalculate собирает physical soma samples
и реальные OutputPulseTimes в общий ProbeRecorder. Вложенного Calculate нет.

Legacy Training/Experiment/inference-калибровка не исполняются, пока executor
владеет управлением. Между пробами владение сохраняется; оно не означает Done.
Явный learner Reset/Default освобождает управление. Косвенный Reset из
Build/Init должен отменять пробу и сохранять удержание управления до явного
решения caller. Обёртки сохраняют native порядок и не добавляют Build/Init.
Снятие IsNeedToTrain во время этого управления означает external_stop без
legacy обнуления паттерна/смены порога.

Scoped overlay использует штатные typed property bindings. Persistent UNet link
records не изменяются; перед проверкой base revision восстанавливаются исходные
связи. Checkpoint/export посреди пробы не поддерживается. Result содержит
prepared context, observation, текущий base revision, adapter reasons и
requiresFreshVerification; этот флаг требует отбросить ранее накопленную частичную
верификацию при неизвестном вмешательстве, даже если semantic hash восстановился.

## Проверенная зависимость: Reset без изменения semantic hash

Root 2298736 (полный SHA в manifest) на M40 воспроизводит два failures:
Classic/Branch Neuron.Reset на 0.04 с не меняет model hash, но старый executor
возвращает completed/valid. Два обычных native controls на том же снимке проходят.
Это дефект рабочего executor, не доказательство дефекта общей семантики Reset.

Первый smoke root 6c99881 также проходил 2/2, но использовал ResetToUntrained и
получал coincident L=1 вместо объявленных {2,1}. Этот контроль не доказывал
переключения разных точек Branch. В 2298736 fixture сохраняет явно заданную
начальную морфологию, проверяет наличие Dendrite1_2, выбирает другое подключение
и проверяет различие effective/base hash и восстановление исходного base.
Положительный baseline не подменяет последующие отрицательные controls.

В Rdk добавлен отдельный process-local ObserveLifecycle. Он инвалидируется
до native lifecycle hooks и при уничтожении объекта; математический hash
не меняется из-за этого диагностического токена. UEPtr — слабый указатель.
Executor должен проверять lifetime/текущий live graph перед чтением или
восстановлением узлов, а при недопустимом графе пропускать его дальнейший расчёт.
Штатные Dataset generator resets разрешены отдельно; Reset нейронного поддерева
посреди пробы делает наблюдение непригодным.

## Открытые проверки и ограничения

Проверены Reset/Build/UnInit/deletion, source/паттерн, callback errors, external
stop, повторные очереди native FinalVerification и размерности 1/2/4/6 в явно
заданных сочетаниях частот. Copy/retarget во время пробы, совпадающие attach
points, вся матрица торможения и physics ещё требуют отдельных controls.
Полный CTest, ASan и восемь bounded legacy A/B пройдены в указанном ниже объёме;
они не разрешают объявлять API готовой версией контроллера 2.

Native observation schema 2 содержит typed StimulusProfile: класс источника,
amplitude, pulse length, frequency Hz, frequency deviation и transit/pattern
режимы. Recorder требует конечный полный профиль, а FinalVerification связывает
его с references и каждой последующей пробой. Native request может задать
ожидаемый профиль; несовпадение отклоняется до предъявления. Внутри пробы профиль
сравнивается по настоящим численным значениям, включая изменения меньше точности
строкового форматирования. Schema 1 сохраняется для прежнего внутреннего контура
и контролируемых сигналов, без выдуманного source profile. Верификация не
смешивает схемы; recognition CSV остаётся отдельной schema 4.

Frequency/Delay генератора принадлежат Dataset playback. Production-сериализатор
условий должен включать typed source profile и фактическое расписание.
Внутренний Rdk string snapshot не является новым научным fingerprint.
Transient stimuli нельзя смешивать с retarget обучающей цели.

ControllerVersion=2, основной bounded search N0/N1, экспорт сертификата и полного
обученного состояния, conversion/PostTune/calibration и новый experiment runner
ещё не реализованы этим изменением. Сам native result не является сертификатом
сходимости или результатом распознавания.

## Промежуточные серверные результаты

Root ad9e54d прошёл 3/3 Rdk lifecycle checks и 4/4 native controls на двух
серверах, включая отклонение Reset при неизменном semantic hash. Root c143fcf
прошёл 16/16 native controls на двух серверах: вмешательства source/pattern,
pooled removal, external stop и реальные/no-op Build. Root 5b72f21 прошёл
28/28 native controls на обоих серверах: N=1/2/4/6, 2000/20000 в объявленных
случаях, реальные отдельные точки Branch, native FinalVerification для N=1
и Classic N=2. N=1 даёт Exact constraint certificate; исходная N=2 модель —
OutsideTolerance по времени при совпадающих raw targets. Это frozen исходные
модели, не завершённое обучение и не распознавание.

Новые schema 2/source-profile, callbacks/UnInit и ускоренный structural inspector
проверены отдельно от этих снимков. Старые schema 1 observations сохраняют свою
схему. Полные SHA, runtime provenance, первичные CSV/JSON и negative baselines
опубликованы в пакетах финальной приёмки ниже.

Рабочий контроль Branch N=2 расширен: недостающая reference снимается отдельной
native solo-пробой с проверкой фактических связей выбранной точки. Затем verifier
повторно предъявляет каждую точку в своём порядке, с собственной window и ID.
Подстановка одного наблюдения под два input ID запрещена. Primary CSV сохраняются
для дополнительной reference и каждой verification-пробы; JSON остатка содержит
target и measured raw potential. На M40 root
089866d374da64c807d0a5b682b02c05826a9720 прошёл оба случая 2000/20000 Гц.
Повторные raw amplitudes совпали со своими references (разные между входами);
timing residual первого входа -0.0705/-0.07005 с, второго — 0. Итог в обоих
случаях OutsideTolerance, без Exact. Elder-1 также прошёл оба случая.

В промежуточном a8 два теста OwnerUnInit выявили особенность общего lifecycle:
UContainer вызывает AUnInit напрямую и обходит UModule::BeforeUnInit. Добавление
только ABeforeUnInit в learner не останавливает его probe. Исправление отслеживает
ревизию в прямых Init/UnInit входах UContainer и отменяет probe в публичном UnInit
learner, сохраняя исходный обход hooks и порядок детей. Отдельный Rdk-тест
проверяет этот обход. Root d2b67279eb56a8a8bfa5a8752cb9d1a90db4908a (a9)
прошёл на обоих серверах 57 адресных тестов и 4/4 lifecycle tests, включая
OwnerUnInit обеих топологий. Полные CTest, ASan, legacy A/B и Git-публикация
этих данных выполнены на финальном снимке ниже.

На обоих серверах primary CSV четырёх общих случаев a7→a9 (Classic/Branch,
N=1/2 при 2000 Гц) побайтово совпали; base/effective semantic identities также
совпали. Анализ сохранён в s07-native-executor-optimization-a7-a9.json. Это
подтверждает отсутствие изменения этих waveform при ускорении inspector;
schema 1 старых наблюдений не превращается в schema 2 и проверяется отдельно.

ASan runtime root 089866d374da64c807d0a5b682b02c05826a9720 на M40 прошёл 51
адресный тест и 4 lifecycle checks (detect_leaks=0). Покрыты удаление синапса
обеих топологий, Reset/Build/UnInit, ошибки callbacks/source и Branch N=2 native
final verification. Это не полный ASan CTest и не утверждение об отсутствии
утечек. Elder-1 также прошёл оба новых Branch N=2 controls (2000/20000 Гц).
Полные CTest и legacy A/B пройдены, пакеты доступны через Git.

## Финальная приёмка подэтапа

Проверенный root: 089866d374da64c807d0a5b682b02c05826a9720, PulseLib
37bbc77bcfc418dfd6053aa267d71e18bbad63ff, Rdk
a6b94092d0016b6a941bd6fd403725ae5c395538, Bin
e78596e9639a841cd1989d73df7fe614419770ce. Последующие изменения до merge
затрагивают только документы, gitlinks на документальные commits и артефакты;
production/test code относительно этого снимка не меняется.

На обоих серверах прошли четыре maintained CTest suites. PulseLib: 247 cases,
238 passed, 9 skipped (восемь opt-in legacy controls и fresh-process helper,
вызываемый parent fixtures). Все 34 native execution cases выполнены; восемь
native final-verification controls выдали Exact для N=1 и OutsideTolerance для
N=2. Эти исходные frozen модели не выдаются за завершённый Train.

Отдельно прошли восемь baseline и восемь строгих legacy A/B на каждом сервере:
Classic/Branch × N0/N1 × 2000/20000, три модельные секунды. Сравниваются весь
JSON наблюдений/решений и binary64 soma waveform hash. Дополнительный анализ
подтвердил одинаковые graph/order/cache pointers, bindings, physics и значения
ptParameter. Только rdk_value прочих свойств исключены из этой metadata-проекции.
Baseline runtime привязан к a9f985a3b3a3a436e01205ddb50341952d57c83e; его binary,
ini и resolved libraries повторно проверены по прежнему manifest до исполнения.
Новую source closure к старому executable не приписывают.

Git-пакеты: [Elder-1](../../../Reports/StructTrain/TimeLearner/s07-native-executor-elder1/README.md),
[M40](../../../Reports/StructTrain/TimeLearner/s07-native-executor-m40/README.md).
Включены full CTest logs, XML, primary CSV/JSON, runtime manifests и SHA256.
Все 867 artifact hashes, gzip integrity и 863 raw payload hashes проверены
локально только как данные; численные проверки выполнялись на серверах.
Отрицательный a3 Reset baseline имеется на M40; его не приписывают Elder-1.
