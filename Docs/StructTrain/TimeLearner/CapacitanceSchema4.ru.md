# Подготовка полного сохранения C-search policy: schema4

Статус: код и fixtures подготовлены; native/reader проверки не выполнены.
Новые branch commits не приняты в develop. Основной контракт в Pulse
Docs/Analysis/TimeLearnerCapacitanceSchema4.ru.md; исходные этапы0–12 не сужены.

Cold config, training summary и completed/stopped model4 сохраняют закрытый
объект абсолютной C/C0 policy. Один C++ serializer используется configuration
и diagnostic producer. Параметры: enum round_robin_absolute_C0_v1, min/max scale,
subdivision depth, max contexts, max membranes, max cursor elements. Import
сверяет policy с training metadata neuron archive и actual C0 owner bounds.
Форматы1–3 при отсутствии policy продолжают иметь прежние поля.

Independent readers поддерживают4, проверяют policy/summary/archive agreement,
реальную физику witness history, всю матрицу первичных проб и original CSV.
Native auditor revision7/learned auditor5 объявляют новую поддержку явно.
Кэш/исторические критерии не переименованы. N0 prepare сохраняет schema4 при
декларировании повторов, вместо повреждающего понижения до2.

Подготовлены16 native cases:4 strict codec,4 completed transfer,4 stopped
transfer и4 реальных C-search activation controls Classic/Branch N0/N1.
Последние используют explicit sync tolerance0 и fixed L/Ns/Rs, обязаны реально
изменить и измерить C, но не объявляют scientific success. Transport controls
используют явно широкий0.2 допуск и сами не доказывают необходимость C-trim.
Together with11 pure controls targeted gate имеет27; будущий regression251.
Это декларации, а не число завершённых проверок. Readers11 требуют все actual
codec/package/fresh-process/activation artifacts; синтетические подмены не
используются как положительные данные. Полные первичные CSV сохраняются для
последующего обязательного отчёта soma+input pulses в читаемом масштабе.

H11 выявил отдельный дефект передачи управления explicit probe → automatic
configured Start. Он исправляется и принимается изолированно в H12 на schema3;
нельзя приписывать успех или отказ H12 новой schema4. Code fix54516bcc включён
в C-search ветку merge-коммитом как необходимая зависимость будущих native tests.

Остаются normal/ASan, полнота визуальных отчётов, fresh Git closure, measured C
comparison scope/refinement, все production modes/physics и исходные эксперименты.
Schema4 не обещает mid-probe динамический или точный search-cursor checkpoint.


## Первый native запуск J1: обнаружен дефект test-target inventory

На root90798f2c4e648483eaa7718189956d211bde7ff2 обе сборки завершились;
четыре actual codec tests прошли, boundary/activation ещё выполняются.
GTest сообщает16 native tests вместо заявленных27: файл
Test_PulseLib_CapacitanceContexts.cpp ранее проверялся отдельным production
kernel builder, но не был добавлен в CMake target Test_PulseLib_StorageComponents.
Исправление включает этот original test source в штатный target. Проверка
инвентаря не ослабляется; текущий J1 не может получить положительную приёмку
27-case gate даже при успехе всех16 actual native cases. Его результат и причина
будут сохранены; повторная проверка требует завершения owners и нового runtime.


J1 завершён: фактически16 native cases,12 passed/4 failed. Все codec и
completed/stopped transfer прошли. Четыре activation controls отвергнуты до
создания search: observation_not_valid_complete. Первичные packets показывают
complete=true, peak_ambiguous:input0, candidate_count=2 и два valid assigned
burst waves: при расширении окна на всю пачку fixture оставил isolated_window.
Исправление явно выбирает AssignedBurstWave одновременно в protocol и probe;
исходный sync0, физика, пачка, пределы и требования реального C-edit неизменны.
Strict invalid-observation gate не ослабляется. Failure evidence08864d3261e8fe7c2d962f347a5bf3cc299c49f8
сохраняет исходную ошибку постановки. Повтор должен включать CMake inventory fix,
все27 случаев и independent readers; успех повторного запуска ещё не заявлен.
