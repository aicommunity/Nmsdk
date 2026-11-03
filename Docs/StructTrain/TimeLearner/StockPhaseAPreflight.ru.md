# Stock NSPNeuronGen: четырёхвходовой preflight без LT-мембраны

Контроль исправляет [подмену исходной научной модели integration-профилем](ScientificProfileDrift.ru.md).
Он использует уже существующий native CLI preflight: новая C++ физика,
изменение общего prototype или реконструкция из обученного fixture не нужны.

`stock-phasea-preflight SOURCE_BUNDLE --runtime-manifest RUNTIME.json --output NEW_DIRECTORY`
готовит обе декларации до первого native вызова и выполняет Classic/Branch.
В каждом job `profile_archives=[]`, `neuron_class=NSPNeuronGen`: используются
штатные зарегистрированные образы текущего runtime. Bundle прежней N1
калибровки даёт только проверяемый исходный синтаксис конфигурации; его
изменённая физика и обученное состояние не импортируются.

Факторы объявлены явно: N1, 2000 Гц, четыре исходных входа L1/Ns1/Rs86 MΩ,
target ISI [0.01,0.08,0.16,0.24], max cable length100. Общие body defaults,
каналы, синапсы и отсутствие LTMembrane должны прийти из storage. Native
preflight проверяет эффективную модель, интегратор и нулевое число Calculate,
references и training probes.

Дополнительный production audit проверяет реальных детей:

- четыре Soma и четыре Dendrite1 для Classic; одна Soma и один Dendrite1 для
  Branch с четырьмя начальными совпадающими точками подключения;
- LTZone класса NPulseLTZoneThreshold и полное отсутствие LTMembrane;
- body C1 nF, R/Rrest/FB10 MΩ обоих channel roles;
- NPSynapseBio R86 MΩ, secretion1 ms, dissociation5 ms, pulse1 ms, PSI Off;
- частоту2000 Гц у каждого узла, полный fingerprint и параметры input banks.

Фактический начальный порог также записывается, а не предполагается равным
историческому. Это profile/structure gate, не equivalence полного pulse response
и не доказательство обучения или classification.

В job сохранены отдельные будущие пределы V2 Train: собственные CapturedPerInput,
amp abs1e-5/rel0, sync0.02; полное окно1.8 s, AssignedBurstWave; nonreference
L1–100 и Rs1–86 MΩ, последний input фиксирован L1/Rs86 MΩ; candidates512/input,
probes2048, edits2048, sweeps4, model3600 s и wall7200 s. Эти новые search/probe
условия не выдаются за точный августовский протокол. Preflight **не выполняет
Train**, независимо от сохранённых будущих бюджетов; runtime может отличаться
от раннего N1 runtime и имеет собственную точную Git closure.

Три server reader checks требуют реальные результаты обеих топологий,
отвергают прежний LT fixture даже после подстановки знакомого имени и rehash,
а также изменённую C/кинетику после rehash. До серверной проверки это только
подготовленный gate. Следующий шаг — холодное обучение прошедших profile gate
моделей, затем полный экспорт, реальные пороги и temporal reports.

## Выполненная normal проверка

Proof `99e0291bd71d99857335f3c31e7719c8bce79812`:
две реальные native операции и3/3 readers, без failures/errors/skips. Проверены
все259 members /203 411 371 raw bytes →5 095 108 xz bytes, checksums и384
source hashes по Git producer472219ab9041e7a5be134c37ea306c21437fa8dd.
Использован существующий immutable J3 Console без сборки/обновления:
native root1c8206ed98dad49982f1a1e9a1764c118e2cfe34, Pulse84e456d6fb551021e0222ebaf51fa313df2623b4,
executable SHA256621f4cdfa3ec815181014ebedce409b46fd20c7ef5cb8d58d2cfb8e188763b76.

Подтверждены все заявленные body физические параметры и отсутствие LTMembrane.
Classic:8 membranes/16 channels/16 synapses; Branch:2/4/4 с четырьмя input banks.
Фактический начальный порог0.0117. Model revisions:
Classic `d74d60a450f51b48591f46f97485bb1dff5171d2cdf70b2e31033d5d4b1cc09f`,
Branch `216b1522f248df9830e4f6167e692ee627ee389f56bca3e076c92a871f82d81b`.
Calculate/training не выполнялись. Совпадение полного импульсного отклика с
исторической версией, ASan, cold Train и classification этим gate не доказаны.

## Первое cold обучение: валидный отрицательный результат

На тех же immutable runtime и неизменённых двух jobs выполнен cold normal a1,
producer15bae9cbee8a59e699d7efa0a788c6bb729cb1ab. Перед запуском новые4/4 readers
проверили и прямые Soma/LTZone/feedback связи; failures/errors/skips отсутствуют.
Начальные identity/parameters обеих моделей совпали с прежним preflight.
Новый graph или обученное состояние из fixture не импортировались.

Оба процесса завершились штатно, но обучение остановилось как
`invalid_observation / observation_not_valid_complete`, без certificate:
после4 valid reference probes и4 search probes. Последние окна complete,
end_reason=window_closed; проблема — ambiguous burst assignment, а не пропуск
окна. Classic:12 waves и peak_ambiguous:input0 при Rs0≈2.8800716 MΩ, L1/1/1/1.
Branch:7 waves и peak_ambiguous:input2 при L2/2/2/1 и Rs86 MΩ. Это не
PhysicalInfeasible и не доказательство несостоятельности исходной модели.
Classification/Test после незавершённого Train не запускались.

Опубликован proof322409d685f20ab6b0be03f7d69e69399f127239,77 members /
298368 compressed bytes. Его независимая локальная проверка ещё требуется;
`execution_valid` относится к выполнению и доказательствам, а не к сходимости.
Worker953150 завершён; каталог `s07-stock-phasea-cold-normal-a1` сохраняется.

Выявлено отдельное различие **training protocol**: в историческом Pulse
cbf76fbe077a7003dccf72b142d7136721fa1afb SetIsNeedToTrain/ApplyActiveLtzThreshold
выбирают TrainingLTZThreshold100. Нынешний V2 model берёт effective threshold
из storage/ModelSpec и не применяет этот legacy knob; в данном опыте это0.0117.
Эта граница уже отмечена в CalibrationPropertyContracts. Она не была учтена
при подготовке нового stock Train и требует исправления постановки.

Следующий шаг: явно задать training-output threshold через native construction
на законной границе до reference capture, с fingerprint фактической модели и
отдельным recognition/calibration состоянием. Не исправлять его на каждом тике,
не менять общий prototype, не переписывать архивы вручную и не переносить старый
certificate. Возможное влияние spike feedback на ambiguous peaks проверять
контролируемым сравнением; текущая корреляция ещё не доказывает причинность.
Также проверить bounded recovery после плохого кандидата: текущий declared
maximum_invalid_observations0 требует немедленной честной остановки.
