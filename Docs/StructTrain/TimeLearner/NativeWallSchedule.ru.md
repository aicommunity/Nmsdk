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

Далее: единый read-only guard в native builder/preflight/edit/probe и
recognition, включая изменения политики во время наблюдения. Ошибки передаются
специализированными статусами/диагностикой, не bool Build/Calculate/Reset.
Обязательны реальные проверки перед Arm и после изменения во время пробы;
C++ code и guards не принимаются до positive/negative/temporal evidence
на обоих workers. Это не закрытие всей lifecycle/storage matrix.
