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
их Git proof ещё должен быть опубликован.

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
параметров: отличаться может только Rs активного входа. Изменение физики,
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
