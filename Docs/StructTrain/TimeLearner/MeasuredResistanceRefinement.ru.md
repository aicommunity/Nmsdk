# N1: уточнение сопротивления по измеренному bracket

Состояние: реализация в feature, серверная приёмка не завершена. Это изменение
proposal policy V2, а не амплитудной цели, допусков, физики или Rdk lifecycle.

## Основание

На Elder выполнены два cold native N1 контроля Classic/Branch при 2000 Гц,
ISI `[0.01,0.03]`, начальных L=1/Ns=1/Rs=86 МОм, области первого
L=1..3/Rs=43..86 МОм и фиксированном последнем входе. Подготовитель
`572f236df212a263e0b47a9a2c292e4c937f32de`, действующий native kernel PulseLib
`38edfcad7983478a7e2ca736c32ae2703861c1fd`. Данные находятся в
`/home/user/timelearner-refactor/readbacks/s07-native-n1-mesh-normal-a1`;
Git proof `12f39119a3eacc843441db2cbae58b0a5ad560e4` опубликован и включён
в эту feature-ветку: `Reports/StructTrain/TimeLearner/s07-native-n1-mesh-normal-a1`,
406 файлов /52 837 153 исходных байт, archive 896 572 байта, actual-data reader 2/2.

Сетка subdivision depth=4 измерила 52 кандидата Classic и 36 Branch,
включая восстановление лучшего кандидата. Оба исхода — SearchUnresolved.
На L2 были измерены согласованные ошибки разных знаков; лучший итоговый
остаток по амплитуде `4.7358625548610256e-5` при допуске `1e-5`, временная
ошибка `-0.0095` с при допуске `0.02` с. Это ограничение конечной сетки,
а не доказательство физической невозможности и не ошибка honest verdict.

## Реализация

`MeasuredResistanceSearch` предлагает точку между соседними измеренными Rs.
`BoundedTrainingSession` хранит измерения только текущего активного входа и
привязывает их к normalized preview revision эффективного графа, получаемой
штатным ResistanceDomain action. Дополнительно сравнивается полный вектор
параметров: отличаться может только Rs активного входа. Эффективная амплитуда
источника в domain assessment должна совпадать с неизменяемым stimulus profile
протокола, по которому проверены сохранённые наблюдения. Изменение физики,
остальной геометрии, Ns или других входов не наследует прежний bracket.

```text
on valid completed candidate:
    retain actual residual, timing validity and full parameters
    attach the explicitly assessed normalized physical scope

on fresh native resistance-domain assessment:
    intersect actual physical domain with declared individual bounds
    select only measurements of this scope and full geometry
    require at least three distinct measured resistances
    reject inconsistent repeats, timing-invalid or nonmonotone samples
    find neighboring opposite-sign residuals outside the original tolerance
    propose their geometric midpoint inside the effective bounds
    prioritize that candidate, keeping the finite mesh as fallback

apply and measure candidate through the unchanged native adapter/probe path
accept Exact only through the unchanged fresh all-input final gate
```

Проверяется монотонность имеющихся измерений, а не постулируется глобальная
монотонность мембранной модели. Новая точка всегда измеряется; обнаруженная
немонотонность возвращает поиск к ограниченной сетке. Повторы не усредняются
для создания подходящего знака ошибки. Endpoint clipping не создаёт новую
точку; midpoint, округлившийся к endpoint, отбрасывается.

Уточнение применяется только в native N1 с явными physical-domain actions и
ненулевым `resistanceSubdivisionDepth`. Depth=0 сохраняет прежний поиск
endpoint-кандидатов; N0 и standalone arithmetic callers без domain ownership
не меняются. `maximumCandidatesPerInput`, probe/edit/time budgets сохраняются.
Исчерпание поиска остаётся SearchUnresolved/BudgetExhausted, не Infeasible.

## Обязательная приёмка

1. Серверные production C++ tests: реальные тела helper и общего контроллера,
   bracket/finite bounds, nonmonotone/timing invalid/repeat inconsistency,
   смена normalized scope, midpoint между seed points и fresh final damage.
   Arithmetic controls отдельно маркируются; они не доказывают физическую
   применимость к реальному нейрону.
2. Новые изолированные Console runtime normal/ASan; baseline не перезаписывать.
3. Те же cold N1 job declarations с исходными CapturedPerInput/tolerances,
   фактический effective-domain readback, all-input final residuals и полные
   временные кривые сомы с входными импульсами.
4. Addressed N0/depth0 regression controls и реальные native storage/editor
   проверки. Научная классификация проверяется отдельно от сходимости.
5. Компактные Git proofs, полные source SHA и merge children-first только
   после успешной адресной приёмки. До неё feature не является develop.

## Состояние проверки

Исходный dimension/N0 proposal подэтап принят в корневой develop merge
`2b5af8c191b6ea20dff0f8b676e702db8c53c82f`, с прежним PulseLib develop38edfcad.
Эта N1 feature объединена с ним через отдельный merge, без переписывания истории.

Новые изолированные normal/ASan сборки a1 запущены из root
`e19a303f2d9252a5179ad0f457593e48c0c35fd1` / PulseLib
`bf50ae57512ff0a1591937f4f23cef172a8928dc`. После запуска локально добавлен
guard амплитуды источника (PulseLib `1dddf1b861546eb8e7802ab4ff6610ef2844520e`)
и соответствующий regression scenario. Рабочие серверные исходники a1 при этом
не обновлялись. Для окончательной приёмки необходима следующая адресная сборка
и тесты актуального commit после подтверждённого завершения a1; её результаты
не разрешается подменять результатами предыдущего commit.

Для исходного finite-mesh kernel дополнительно запущен ASan physical baseline
`/media/user/Data/TimeLearnerRefactor/readbacks/s07-native-n1-mesh-asan-a1`.
Результат и временные отчёты этого N1 сравнения ещё не приняты.

Normal a1 завершён: 40/40 выбранных C++ cases, включая 7 новых helper/kernel
cases, Console и runtime snapshot; wall1083.99 s. Это снимок e19a303f/bf50ae57,
а не проверка последней правки. После подтверждённого terminal состояния
исходники и build cache переиспользованы для a2 с новым отдельным runtime.
Старые бинарники a1 оставлены; первоначальный finite-mesh runtime38edfcad
и его исходники не изменялись.

Normal a2 (roota8709e79/Pulsec89a067e) остановился на компиляции за10.37 s:
в source guard была неверно использована optional `VerificationProtocol::stimulusProfile`.
Исправление PulseLib `521df5450c3655e0f08b3a01a7aed7d18351c250` проверяет наличие
профиля и использует `->amplitude`; при отсутствии профиля refinement не
предлагается. Неудачная попытка сохранена в отдельных receipts и не считается
прохождением тестов. Требуется normal a3 и актуальная ASan сборка после a1.
