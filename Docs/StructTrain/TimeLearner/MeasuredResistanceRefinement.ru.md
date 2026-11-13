# N1: уточнение сопротивления по измеренному bracket

Состояние: подэтап адресно принят (источники и пределы ниже). Это изменение
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

Первые изолированные normal/ASan сборки a1 были запущены из root
`e19a303f2d9252a5179ad0f457593e48c0c35fd1` / PulseLib
`bf50ae57512ff0a1591937f4f23cef172a8928dc`. После запуска локально добавлен
guard амплитуды источника (PulseLib `1dddf1b861546eb8e7802ab4ff6610ef2844520e`)
и соответствующий regression scenario. Рабочие серверные исходники a1 при этом
не обновлялись. Для окончательной приёмки необходима следующая адресная сборка
и тесты актуального commit после подтверждённого завершения a1; её результаты
не разрешается подменять результатами предыдущего commit.

Для исходного finite-mesh kernel дополнительно выполнен ASan physical baseline
`/media/user/Data/TimeLearnerRefactor/readbacks/s07-native-n1-mesh-asan-a1`.
Оба реальных Train дали SearchUnresolved, reader 2/2; proof commit
`1f14f6c031dae019733d52815737e1896532064f`. Его временные отчёты содержат
292 пары probe/soma, проверены тремя production report tests; ручная проверка
выбранных рисунков и публикация visual proof остаются отдельными действиями.

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
прохождением тестов. Ниже приведена последующая проверка исправленного commit.

### Адресная проверка актуального кода

Runtime source root `6ab3b0b3953b132c54a0c4db3662cec80f7f81b9`, PulseLib
`521df5450c3655e0f08b3a01a7aed7d18351c250`:

| Проверка | Elder normal | M40 ASan |
|---|---|---|
| Текущая сборка | a3: 40/40 C++ cases, Console и snapshot | a2: 32/32 C++ cases, Console и snapshot |
| Реальные cold N1 Train | Classic Exact; Branch Exact | Classic Exact; Branch Exact |
| Проверка одинаковых исходных условий и финального gate | 2/2 reader tests | 2/2 reader tests |

Текущий ASan набор включает весь изменённый helper/kernel и два native
read-only preview. Все десять native-domain regressions, включая 20000 Гц,
ранее прошли на ASan a1; эти depth=0 пути не меняет последующий guard.
Ненулевой refinement на реальной физике пока проверен только при 2000 Гц,
двух входах и указанных профилях. `detect_leaks=0`: отсутствие утечек не доказано.

Дополнительная сверка96 файлов четырёх depth=0 domain cases normal a3 и
ASan a1 обнаружила26 несовпадающих файлов. В12 Branch20000 пробах значения
stimulus/soma совпадают, но отличается абсолютное начало времени на0.0457 s.
В последней Classic20000 пробе ASan записано2687 отсчётов вместо3601:
`complete=false`, `end_reason=native_training_time_budget_exhausted`, итог
BudgetExhausted без certificate. Это сохранённая диагностическая проба,
не подтверждение full-window/final-gate при20000 Гц. GTest40/40 означает
прохождение конкретных domain assertions; этот fixture не требовал сходимости
или полного финального окна. Его ASan графики нельзя объявлять идентичными
normal либо подменять ими. Новые nonzero N1 Train при2000 Гц имеют отдельные
полные данные и свежие Exact certificates на обоих workers.

В обоих runtime исходная finite-mesh версия давала SearchUnresolved,
а measured refinement — Exact при тех же job declarations, исходных моделях,
CapturedPerInput и допусках. Получено Rs[0]=64369082.70599112, L[0]=2,
Ns[0]=1; опорный вход сохранён L=1, Ns=1, Rs=86000000.
Свежий финальный амплитудный остаток входа0 равен
`-9.574000452428066e-7` при допуске `1e-5`, временной — около `-0.019 s`
при допуске `0.02 s`. Собственные reference amplitudes входов различны:
0.004590480933837182 и 0.005492406840386876. Общая цель A* не вводилась.

Источники: normal proof commit
`bcbd30f1d87e352825e6c8400c5b929eff184ae5`, ASan proof commit
`44858d7fb92a330470f50741fb862f9f8db23840`; каталоги
`Reports/StructTrain/TimeLearner/s07-n1-refinement-build-{normal,asan}-a1`
и `s07-native-n1-refined-{normal,asan}-a1`. Сжатые архивы содержат первичные
JSON/CSV, модели, runtime и receipts с пофайловыми SHA256. Reader source:
`9699cd85c5bcf2c41c3662a4571960ab04eaca1a`.

Это сравнение двух вариантов контроллера V2, а не исторический replay августа
и не сравнение legacy V1/V2. Последующий [export/frozen контроль](PositiveN1Handoff.ru.md)
этих положительных моделей подтверждает перенос и реальные отрицательные
ответы при исходном пороге1; полноценная научная классификация, независимый
Test и полная матрица остаются отдельными проверками.
Временные отчёты строятся из всех реальных проб с наложенными входами;
полный кэш хранится на M40, выбранные рисунки и metadata публикуются в Git.
Визуальная приёмка данного подэтапа завершена: full caches содержат292 пары
probe/soma исходного поиска и142 нового, по3 production report checks;
536 первичных JSON/CSV сопоставлены между normal/ASan без различий значений.
Все24 выбранных PNG прямо просмотрены1920x960. Выбраны overview и первые
два zoom-окна с импульсами/пиками, полная ручная проверка cache не заявлена.
Компактный visual proof: `Reports/StructTrain/TimeLearner/s07-native-n1-visual-a1`,
первоначальные source commits966fe3d59/e0adf29b2 и отдельный selected QA.

PulseLib объединён в develop merge
`d1c3df4cd0749e5869b977fb5e69417400ce1112`. Его Core tree
`412b4997167f47f70419a9281acadcd9ad81647c` идентичен проверенному521df545.
Корневой develop merge `ff98c7fef96eb4f947eca756528834877d14492d` записывает
этот опубликованный gitlink. Это приёмка данного подэтапа, не полного stage7.
Дополнительный кэш
временных отчётов native-domain depth=0 regressions завершён отдельно:
четыре normal cases при2000/20000 Гц,48 проб/72 пары soma, полные native samples
и input overlays проверены production renderer;192 исходных файлов не изменены.
Все6 выбранных PNG прямо просмотрены. Compact proof:
`Reports/StructTrain/TimeLearner/s07-native-domain-visual-normal-a1`, source
`291793548f6acccb62b0a9111fadb957d902aec1`, proof
`8e6825653cccc475670fa78be22325d30172a76c`. Сравнение с неполным ASan a1
сохранено в metadata; общая отрисовка для них не заявляется. Это не расширяет
доказанный nonzero-refinement режим до20000 Гц.

## Следующий вариант после N1 A3 (13.11.2026)

A3 подтвердил valid opposite-sign amplitudes на[26,26,25,1], Rs86M и2.880071555M, при допустимом timing обеих точек; exact не достигнут. В следующей реализации bounded local turn допускает дополнительные свежие точки в прежних global budgets. Для подходящего measured bracket proposer использует safeguarded log(Rs) secant с fraction[0.25,0.75]; это очередность исследования, не свидетельство измеренной амплитуды. Старый midpoint остаётся частным случаем symmetric residuals. Domain, source amplitude, repeated-data consistency, timing и physical-scope guards сохранены; невалидные/немонотонные данные возвращают mesh fallback. Новые native tests и real same-budget Train ещё требуются; исторические PASS выше относятся к прежнему коду.
