# Stock N4 cold7: подготовка холодного обучения — 11.11.2026

Исходные данные —8 полных валидных assigned burst проб свежей stock NSPNeuronGen, обе topology,2000Hz,без LT-мембраны. [Характеристика и исходные состояния](StockCold4Characterization-20261111.ru.md). Новый Train создаёт модель штатным native механизмом, сам захватывает per-input references и не импортирует обученное состояние.

## Декларация pilot

- Classic/Branch, N=4,N1; исходные ISI [.01,.08,.16,.24],L1,Ns1,Rs86MΩ,initial threshold100. C-trim/PostTune/auto-calibration Off. Learner StructureBuildMode1, neuron mode2, CalculateMode0.
- CapturedPerInput, anchor input3; anchor L1/Rs86MΩ фиксирован. Для входов0–2 L1–100,Rs1–86MΩ,Ns1.
- Amp absolute1e-5,relative0,minimum amplitude1e-6,SyncTolerance=.02. Физика и допуски не подбирались под PASS.
- Окна начальной регистрации: [.009,.05],[.089,.13],[.249,.29],[.489,.53]s; границы получены из actual onset и назначенного максимума: onset−2ticks,peak+51ticks.
- Candidate-window predictor29frames/segment — начальная гипотеза из полной задержки при L1; это не измеренная производная по L и не доказательство монотонности. Base left/right guards40frames, length/Ns/C guards0; Rs guards2/5/5/5frames на каждое изменённое сопротивление; maximum window160frames,hard frames1–3600. При отсутствии свежего корректно приписанного максимума сертификат Exact недопустим.
- Search:128 probes,1280 edits,128 candidates/input,4 sweeps,4 invalid observations,resistance depth8. Reference:8 probes,invalid budget0.
- Composite:3605samples/probe,6 native probes/group,21630 samples/group;512groups,3072 native probes,11074560 samples/attempt;20model seconds/group,300wall seconds/group,512MiB primary limit.
- Attempt:7200model seconds,1800wall seconds,14400000 ticks. Native memory4GiB; controller4GiB; demand вычисляется по фактическому kernel limit контроллера. Это явные бюджеты, не критерии сходимости или физической невозможности.

Подготовка создаёт оба job,ModelSpec,ConditionSpec с production serializer,expected initial identity и source packet/CSV hashes. Перед Train выполняется настоящий native preflight с проверкой эффективной stock-физики и точным сравнением начального model identity. Состояния выполнения, валидности данных и обучения сохраняются раздельно; классификация этим шагом не оценивается.

Команды: `stock-candidate-window-study prepare COLD_RESULT --runtime-manifest RUNTIME --output JOBS`; затем `preflight JOBS` или `train JOBS` с явными --case,--controller,--runtime-manifest,--output.

Первая подготовка отказала до native preflight/Train: код искал runtime.json в корне run вместо штатного process/runtime.json. [Исходный traceback](ValidationPlans/M40StockCold7Preflight2-20261111/original-unittest.log). Исправление6c5d2bd9c11bd691e415346c5478f63bce42d699; условия моделей и допуски не менялись. Второй preflight добавляет отказ при подмене ConditionSpec до создания output и проверку неизменности подготовленного дерева. [Неизменяемый request](ValidationPlans/M40StockCold7Preflight2A2-20261111/request.json). Его runtime-приёмка и настоящий Train пока открыты.

Source review до Train выявил вырожденную singleton proposal при нулевых base guards: seed берётся из измеренного peak/plateau, а не из всего reference window. Guards изменены на40frames/side; добавлена проверка production calculate_window на неизменённой и крайних конфигурациях. Это арифметическая проверка координат диагностического источника, не training measurement/admission proof. Новый Train получит собственные authoritative references и grid. Исходные допуски не менялись; новые значения guards включены в ConditionSpec.

Classic и Branch preregistered как отдельные cold Train попытки на immutable SDK22; каждая сначала повторяет native preflight и сравнивает полный initial model identity. [Classic request](ValidationPlans/M40StockCold7ClassicTrain-20261111/request.json), [Branch request](ValidationPlans/M40StockCold7BranchTrain-20261111/request.json). Результаты пока не приняты.

До запуска Train дополнен source review всех четырёх углов Lmin/Lmax×Rmin/Rmax. В варианте одинакового Rs guard5 для input0 комбинация Lmin с изменёнными Rs могла выйти ниже frame1. Guard input0 ограничен2frames по измеренному положению исходного пика; у остальных5. Проверены все углы и отрицательные controls (нулевой singleton interval и ранний выход за frame1). Requests A1 не запускались, что подтверждено отсутствием job directories; они сохранены как withdrawn. [Classic A2](ValidationPlans/M40StockCold7ClassicTrainA2-20261111/request.json), [Branch A2](ValidationPlans/M40StockCold7BranchTrainA2-20261111/request.json) используют отдельные попытки, те же исходные допуски и дополнительный final stock physics audit.
