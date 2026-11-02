# Wall-clock scheduling и native TimeLearner

Открытый подэтап lifecycle/режимов этапов1,4,6. Rdk UContainer::Calculate
при RDK_ENABLE_CALC_TIME_CHECKS и MaxCalculationDuration>=0 проверяет
прошедшее wall time после очередного ребёнка и может прекратить обход.
CalculationDurationThreshold отвечает за диагностику и этим ограничителем
не является. Возвращаемое значение Calculate не подтверждает полноту обхода.

Первая проверенная версия native V2 предполагает uniform single-rate tree
с расчётом всех необходимых детей на каждом тике. Политика совместимости:
любое неотрицательное MaxCalculationDuration на learner, его предках либо
необходимых физических/stimulus узлах должно явно отклоняться до пробы/Train.
Это capability policy независимо от compile flag: при отключённом флаге
такая настройка не должна выдаваться за реально действующий фактор.
Legacy/Rdk scheduler semantics не изменяются, отрицательные значения допустимы.
Запрещены самоприсваивания, принудительная запись -1 и вложенные Calculate.

Исходный snapshot: root f03f3a277fb69c082e670d7afec6f90ced313a4f,
PulseLib a18bf543007c52a3ac7a6fbb148a48cb2c351de3,
Rdk0a1c1d05a1b12de20feabf54a25712e210865791. В NativeProbe проверяются
ready/init/frequency, а явный запрет wall-limited required graph отсутствует.
ModelIdentity включает MaxCalculationDuration физического графа, но это
не заменяет проверку scheduler policy на learner/внешних предках.

Добавлены32 native fixture cases: Classic/Branch ×N0/N1 ×
owner/ancestor/neuron/generator ×0/1000000000ms. Заданные32 cases являются
контрактом раннего отказа, а не обещанием, что во всех исходных сборках
обязательно реально происходил wall-driven пропуск. Первая baseline проверка
выбирает ClassicN1OwnerLarge и BranchN1GeneratorLarge: большой лимит позволяет
измерить, принимается ли сейчас неподдержанный режим без wall-time flakiness.
После исправления обязательны status=Rejected, причина
unsupported_native_wall_limited_schedule, отсутствие observation/onSample,
сохранность индивидуальных параметров и самого заданного ограничения.
Для4 owner/Large cases восстановление отрицательного исходного лимита
подтверждается свежей настоящей пробой. Серверные результаты пока ожидаются.

Далее: единый read-only execution guard в preflight/native-training bindings/
probe/recognition и owned finalization, включая изменения политики во время
наблюдения. Generic Build/import/export и standalone physical edits этим
ограничением не запрещаются: это допустимые операции с данными Rdk; особенно
важно не блокировать восстановление физического checkpoint после внешнего
изменения scheduler policy. Отказ относится к выполнению проверенного
протокола, а не к возможности построить или сохранить граф. Ошибки передаются
специализированными статусами/диагностикой, не bool Build/Calculate/Reset.
Обязательны реальные проверки перед Arm и после изменения во время пробы;
C++ code и guards не принимаются до positive/negative/temporal evidence
на обоих workers. Это не закрытие всей lifecycle/storage matrix.

Начат исходный контроль по root162afc02abc321368304c8913a12a8ab2195682b.
Elder переиспользует source/build только после проверки отсутствия процессов
в cwd/exe/maps/fd; runtime новый и неизменяемый. На M40 созданы отдельные
Git clones всех gitlinks, отдельные build/runtime: исходное inherited ASan
задание продолжает работу. До дополнительной сборки доступны24GiB RAM и
около487GiB на Data; compile jobs ограничены2.

Первая M40 configure попытка a1 остановлена по проверенному PID/process group
до запуска тестов: не был перенесён RDK_LLM_BUILD_EMBEDDED=OFF из прежней
сборки. a2 сохраняет7 submodule clones, проверяет отсутствие пользователей
нового source/build, передаёт все прежние RDK_/NO_MOTION_CONTROL bool flags и
ASan compile/link settings. Контекст старого native source/build сравнивается
до и после; артефакты отменённой настройки сохраняются отдельно. Ни одна
baseline попытка ещё не принята как воспроизведение проблемы.

Предлагаемая реализация после воспроизведения: общий NativeCalculationPolicy
helper читает MaxCalculationDuration у owner/предков и required Neuron/
DatasetMatrix subtrees. BindNativeTraining проверяет execution policy до
Start и перед действиями, public preflight — до положительной квитанции,
probe/recognition — до arm и на live boundaries. Проверка не меняет свойства,
не вызывает Calculate/Reset/Build и не входит в общий model rollback.
В отдельной проверке нужно подтвердить отмену live наблюдения после изменения
политики; частичная observation не может стать valid complete result.

Baseline завершён на обоих workers:2 выбранных cases принимают большой
положительный лимит и выдают completed/по361 samples без нужной диагностики.
Elder proof `f6ad0174e9dee5943a4e66576894bf615ab75509` (43 members,27864B),
M40 proof `eb6c648128c1b3f8be2bad7ae17f6abb2c74f801` (66 members,33764B)
содержат также cancelled configure metadata. Это воспроизведение пробела
capability validation; фактические wall-driven skips не заявляются.

Pulse implementation `6d59d764fbd4181bf9d9697cf19291753a453100` добавляет
execution-only NativeCalculationPolicy и проверки в probe, recognition,
training adapter/service и owned finalization; Console preflight вызывает тот
же helper. Model revision reader не блокируется при невалидной политике,
чтобы сохранить partial observations. Общие builder/editor/import/rollback
не изменены. После onSample отдельно проверяются final-sample изменения;
явный callback cancel/reset сохраняет собственный исход.

Теперь объявлены62 native cases:32 pre-arm probe rejections,8 live changes
(включая4 final-sample),2 callback cancellation,16 Begin/reset/build controls
и4 recognition preparation rejections. Последние используют production
executor и реальные physical bindings; это не trained/frozen evaluation.
В Begin controls child metadata восстанавливается до структурного Build:
Build может законно заменить ребёнка из storage, старый pointer не checkpoint.
Восемь owner/ancestor controls проверяют Build/Init при сохранённом положительном
лимите. Four restored owner probes подтверждают отрицательный лимит; все
46 создаваемых проб имеют schema3 packet/CSV. Серверная positive приёмка,
регрессии, проверка полного Console preflight и temporal reports ещё открыты.

Дополнительная граница callback: observationSink вызывается уже после закрытия
пробы. Политика проверяется повторно после сохранения packet/sink, до принятия
reference либо сертификата. Две реальные service cases подтверждают сохранение
предыдущего valid complete observation и остановку текущего Train без Exact/
certificate при смене политики в sink. Всего64 cases/48 schema3 packet/CSV;
сервисы с pure adapters могут не предоставлять optional execution validator,
а BindNativeTraining предоставляет его всегда. Pulse итоговой реализации
`151a3883137bf112519543f64aa0b9bbf500c579`; серверная приёмка ещё ожидается.

Первая positive сборка a1 на обоих workers остановилась до тестов:
в новом fixture ошибочно вызван отсутствующий public CancelNativeProbe.
Core guard скомпилировался. Fixture исправлен через штатный learner.Reset
в середине/на final sample: Reset должен оставить Idle и удалить pending
result; контроль не фабрикует закрытую observation, а сохраняет отдельную
raw-sample reset diagnostic. Это66 declared cases,46 schema3 packet/CSV и
4 отдельных reset diagnostics. Это setup error теста, не модельный результат.


Повторная проверка a2 (root `efdf7a3afa5b1c0167fc78fff957c0cdc70d7782`)
завершилась на обоих workers: 62/66 passed, четыре одинаковых отказа
положительного контроля после восстановления отрицательного лимита.
Все четыре пробы завершены полностью; `IsolatedWindow` на полном окне
пачки закономерно вернул `peak_ambiguous:input0`. Это ошибка постановки
контроля, а не подтверждение повреждения модели либо дефект peak validity.
Исправление использует штатный `AssignedBurstWave` и проверяет выбранный
`pulse0`, сохраняя полное окно, первичные данные и все требования validity.
Production-алгоритм, физика и численные допуски не изменяются.
Полные failed-attempt данные сохраняются до нового серверного checkout.
66-case acceptance и актуальные temporal reports остаются открытыми.


Для отчётов объявлен самостоятельный статический contract
`specs/native-wall-schedule-v1.json`: точные66 JUnit IDs и46 packet/CSV.
`wall_schedule_reports` дополнительно проверяет32 pre-arm,16 Begin,
8 live-change,4 recognition-preparation,2 sink metadata и4 Reset diagnostics.
Сброшенный result не заменяется синтетической observation: отдельный renderer
строит raw соматические временные графики с реальным sampled input, без
утверждений о завершённости пробы, спайках или классификации. Масштаб zoom
следует общей политике100 native ticks на панель; отсчёты не прореживаются.
Reader tests используют реальные серверные corpus и их повреждённые копии.
Серверная проверка нового reader/renderer до приёмки ещё обязательна.
