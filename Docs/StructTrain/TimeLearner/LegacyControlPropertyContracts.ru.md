# Семантическая проверка исходных свойств: управление и выбор классов

Проверены оба `.h/.cpp` learner и общие NativeModelOwner/ConfiguredNativeOwner/
NativeTrainingService в PulseLib `025d809f7b86cc79e18ddd711c6adc40e2396bf8`.
Это **code review 16 из 211 исходных записей**, восемь свойств каждого класса.
Исторический source_inventory.json не переписывается: его pending относится к
моменту создания. Совокупный code review всех 211 исходных записей фиксирует
PropertyReview.json; runtime matrix остаётся отдельной незавершённой приёмкой.
Шесть новых configured
properties описаны отдельно в ConfiguredPropertyContracts.ru.md.

Все перечисленные свойства — `ptPubParameter`, сохраняются штатным XML и
parameter Copy; это не checkpoint физической динамики. Setter вызывается до
сохранения нового значения UProperty. Default устанавливает исходные параметры;
Reset не является Default и сам по себе не должен возвращать необученную модель.
Проверка исходника не объявляется runtime-подтверждением всех вариантов.

| Свойство обоих классов | Смысл/default/владелец | Setter и фактический lifecycle | Режимы, ограничения и необходимые проверки |
|---|---|---|---|
| StructureBuildMode | int; 1; способ структурной настройки learner | Setter при value>0 делает Ready=false, но не валидирует enum. Legacy ABuild вызывает BuildStructure только при ==1. Native-owned ABuild валидирует принятую декларацию; V2 cold Build проходит отдельный ConstructNativeModel | Разрешённые learner modes 0/1 нельзя смешивать с neuron 0/1/2. V2 значение 0 не является обещанием пропустить необходимую cold конструкцию. Нужны fresh/adopt/growth/Build controls обоих modes и отказ 2/отрицательных значений на preflight; native import сохраняет поле |
| PulseGeneratorClassName | string; NPulseGeneratorTransit; класс дочернего генератора Dataset | Setter делает Ready=false без проверки существования класса. Legacy BuildStructure использует selector. Native declaration зеркалит его и ValidateNativeOwner требует совпадения с ModelSpec | Имеет эффект через создание соответствующих storage instances, не через per-tick patch. Не менять образ существующих экземпляров. Проверки: недоступный/неподходящий класс, storage collision, effective Generator1 profile и frequency; после native ownership несовпадение должно диагностироваться |
| NeuronClassName | string; NSPNeuronGen; storage-образ нейрона | Setter отклоняет другое имя при уже принятом NativeModelDeclaration; допустимое значение делает Ready=false. Legacy выбирает образ при BuildStructure; native Mirror/Validate связывают его с declaration | Класс и образ определяют также child physics и рост. Нужны effective graph/profile readback, fresh/reuse/Load/Copy/growth. Замена profile — явная reconfiguration, не обход setter через SetDataDirect |
| SynapseClassName | string; NPSynapseBio; reserved learner property | Setter только Ready=false. По всем обращениям в обоих `.cpp` нет использования этого learner selector для выбора создаваемых синапсов; фактический класс задаётся структурной настройкой мембраны | Сохранять загрузку ради совместимости; запрещать как действующий фактор новых экспериментов. Изменение этого поля не заменяет membrane/storage profile. Нужен preflight negative control; существующий parser ещё не обеспечивает это правило |
| CalculateMode | int; 0; политика автоматического снятия Need | Setter принимает только 0/1, сбрасывает CountIteration/IsFirstBeat. Native AfterTick снимает Need при завершении только в mode0; в mode1 завершённая служба может сохранять Need=true | Need не доказывает Searching/Exact. Outcome/certificate независимы. Legacy mode1 снятие Need может вызвать ZeroingTrainingPattern, кроме активного PostTune. Нужны обоих topology × mode completion/external-stop/warm controls; текущие адресные ExactAutoCompletion проверки не закрывают всю матрицу |
| IsNeedToTrain | bool; true; внешняя команда управления | V2 rising edge после native ownership сбрасывает controller/probe control, затем штатный BeforeCalculate запускает idle службу. Falling edge вызывает ExternalStop. V1 с явным native ownership также останавливает службу; legacy дополнительно сбрасывает счётчики/phase и переключает threshold, а mode1 может очистить TrainingPattern | Это не certificate и не качество распознавания. В native imported frozen model выставляется false; ResetControl сохраняет references, retarget требует отдельной invalidation. Проверены named native external-stop/censored и Exact warm cases; полный режимный/lifecycle набор остаётся обязательным |
| SpikesFrequency | double; 1.5; compatibility no-op | Setter игнорирует value; кроме регистрации/default/setter функциональных чтений нет. Не является частотой вычислений Rdk или длительностью итерации | Не приписывать единицы Hz действующему фактору. Загрузку сохранять, использование как научного фактора отклонять. Для физической частоты использовать timestep дерева и effective generator profile; для времени предъявления — объявленный протокол |
| AdditionalInputPattern | matrix<double>; Default Resize(N,1), не отдельная скалярная цель; reserved | Setter игнорирует value; кроме регистрации/resize/default/setter чтений для выполнения дополнительного обучения нет | Пустые/недиспетчеризуемые legacy методы не создают incremental learning. Сохранение матрицы не означает её предъявление. Нужен preflight negative control; новый retarget должен инвалидировать references/history/certificate/calibration явным путём |

## Источники и адресные проверки

- Оба `NNeuronTimeLearner*.cpp`: SetStructureBuildMode, SetPulseGeneratorClassName,
  SetNeuronClassName, SetSynapseClassName, SetCalculateMode, SetIsNeedToTrain,
  SetSpikesFrequency, SetAdditionalInputPattern, ADefault, ABuild, AReset,
  ABeforeCalculate/ACalculate; для no-op проверены все обращения имён в файлах.
- `TimeLearner/NativeModelOwner.h`: MirrorNativeModel/ValidateNativeOwner;
  `ConfiguredNativeOwner.h`: cold construction и marker guard;
  `NativeTrainingService.cpp`: ResetControl, InvalidateTarget, ExternalStop.
- `Test_PulseLib_NativeModelEditor.cpp`: NativeModelBuilder.*,
  NativeTrainingService.ExactAutoCompletionResetWarmRestartAndRetarget,
  ClassicExternalStopPreservesCensoredEvidence,
  BranchExternalStopPreservesCensoredEvidence; configured cold/Copy/XML controls
  и NativeLearnedState.* проверяют соответствующие части, а не все восемь полей.

Новые дефекты/риски не исправляются путём переописания contracts: acceptance
gaps, reserved-factor preflight и неполная enum validation остаются работой плана.
Legacy ABuild всё ещё содержит false-return ветви, поэтому полный заданный
пользователем контракт lifecycle bool ещё нельзя считать выполненным для всех
унаследованных путей. Их устранение требует адресных production fixtures и
typed diagnostics, а не проверки bool в experiment runner.
