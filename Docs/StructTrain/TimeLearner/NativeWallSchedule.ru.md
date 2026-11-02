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
