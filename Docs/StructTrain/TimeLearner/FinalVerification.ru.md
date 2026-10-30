# Финальная верификация: реализованная часть общего контроллера

Добавлены `Core/TimeLearner/FinalVerification.h/.cpp` в PulseLib. Контур выдаёт
input-specific requests, принимает подготовленный adapter context и свежую
ProbeObservation, затем завершает проход с Exact, OutsideTolerance,
InvalidObservation, BudgetExhausted либо ExternalStop. Подробный контракт:
[TimeLearnerFinalVerification](../../../Libraries/Nmsdk-PulseLib/Docs/Analysis/TimeLearnerFinalVerification.ru.md).

Он ещё не диспетчеризуется из двух legacy learner. В частности, старый
Branch AllSynapsesNormalized продолжает иметь local ActivePulseIndex gate;
TL-001 не объявляется закрытым внедрением отдельного модуля. Нет нового
публичного ControllerVersion=2 до подключения и полной обязательной проверки.

## Изменения алгоритмического контракта

- CapturedPerInput содержит неизменяемые raw references всех входов одной
  исходной модели. Reference не подменяется текущей амплитудой при stall и
  не заменяется baseline-deviation или общей A*.
- Финальный проход требует **каждый** вход, включая N−1. В Branch solo context
  обязан соответствовать запрошенному входу; пустой active input не даёт
  vacuous success. Порядок Classic — forward, Branch — reverse.
- Синхронность проверяется относительно свежего anchor observation **этого**
  финального прохода, а не cable prediction либо старого captured timing.
  Signed timing interval учитывает plateau обоих пиков. У самого reference
  timing residual равен нулю, но валидный пик и amp residual обязательны.
- Absolute amplitude tolerance default 1e-5, relative default 0;
  amplitude tolerance = abs + rel·abs(capturedRaw). SyncTolerance default 0.02.
  Нет скрытых 1%, одного timestep, Rmin slack и BestEffort→Exact.
- Изменение base model/epoch аннулирует все входы и прежний certificate.
  Transient Branch routing имеет отдельный effective probe revision, не
  подменяющий learned model key. Unknown runtime context и mid-probe change
  тоже аннулируют весь частичный проход.
- Проба проверяется на schema/context/IDs, finite optional values и согласие
  raw−baseline, actual delay и window. Одного valid=true недостаточно.
- External stop, незавершённый sweep и бюджет не выдают certificate. Bounded
  retry использует новый trial ID и сохраняет отклонённую пробу в истории.

## Сертификат и управление

CapturedReferences и TrainingCertificate создаются только проверенными
производителями; сессия не копируется как checkpoint. Сертификат — proof
solo timing/amplitude constraints, не selectivity/calibration verdict.
OutsideTolerance сохраняет валидные отрицательные остатки, Exact=false.
Matches проверяет model key/epoch, все references с provenance, полный typed
protocol, tolerances и LearnedSolo state kind. Для Recognition он отвергается,
даже если численный hash не изменился.

Адаптер обязан реально подготовить requested gate и native reset до первого
стимула. Контроллер не вызывает вложенный Calculate/Build/Reset и не меняет
физические параметры. Пока probe armed, повторный request не выдаётся.
RunId должен быть уникален для verification attempt; уникальность между
процессами обеспечит runner. Base/effective revision producers, различение
learned edit и transient probe routing пока остаются обязанностью адаптера.

## Проверки и доказательная область

Проверены production ProbeRecorder/FinalVerificationSession на управляемых
сигнальных fixtures для N=1/2/4/6: свежесть каждого входа, оба порядка routing,
signed error, текущий anchor, plateau uncertainty, исходные tolerances,
ненулевой baseline и измеренный raw=0/negative, replay, same-hash epoch change,
смена references/criteria, budget/external stop, recovery и повреждённые данные.
Это сигнальные unit fixtures, не научные обучения разных физических профилей.

Native N=1: каждый Classic/Branch case при 2000/20000 сначала независимо
capturing reference на реальных компонентах, затем создаёт/сбрасывает новый
экземпляр того же физического профиля и выполняет новую пробу. Arm выполняется
после подготовки реального графа, до первого стимула. Собираются отдельные
CSV/JSON для reference и verification, actual stimulus events, model identity
и ограниченный certificate JSON. Это не replay одного наблюдения под новым ID.

Initial L=1 в N=1 может удовлетворять математической задаче без изменения
шаблона. Поэтому положительный результат этого fixture — тривиальная свежая
проверка одного входа, а не завершённое multi-input обучение или 8/8 recognition.
LTZ threshold=1 задаётся immutable storage-профилем для subthreshold fixtures.

## Проверки и артефакты

Проверенный root 769869eadee9ba48031beaef843f5e2d83f819e3 использует PulseLib
db78ded793330d95e617624e969ee72b42d75ab5. На обоих серверах прошли 17 targeted
cases (13 сигнальных и четыре native N=1) и 4/4 maintained CTest suites.
Полный PulseLib suite: 200 cases, 191 passed, девять skipped (отдельные opt-in
long controls и archive helper, вызываемый parent fixtures в child process).
На M40 дополнительно прошли 15 checks под ASan: 13 сигнальных и два native
N=1 при 2000, с detect_leaks=0. Full ASan CTest и отсутствие утечек не заявляются.

Артефакты: `Reports/StructTrain/TimeLearner/s07-verification-elder1` и
`s07-verification-m40`. В них есть первичные CSV/JSON каждой физической пробы,
scope/tolerances/source IDs certificate, actual model identities, runtime
manifests до запуска, binary hashes и полные logs/XML. NumericChecks вынесен
механически из recorder; его machine-epsilon semantics не изменена.

## Оставшаяся работа

Рабочий [NativeProbeExecutor](NativeExecution.ru.md) уже подключает пробы к
обоим learner и проверяется в отдельном подэтапе. Native N=2 Classic/Branch
использует настоящие повторные пробы; это не означает переключения legacy
EndOfLearning на данный verifier. Для production поиска дополнительно требуется
глобальное сопоставление волн импульсам при меняющейся морфологии Classic:
объявленное окно и stimulus ID сами по себе не доказывают происхождение пика.
Случаи с задержанной ранней волной, пропущенным пиком и перекрытием должны
отклоняться либо разрешаться по измеренным данным, без model-delay fallback.

Не завершены: production wiring в NNeuronTimeLearner/Branch, общий train/search
action loop, настоящий base/effective ModelSpec producer, final native sweep
N>1 с правильным Branch mute и повреждением ранее committed input, normalizer
quantized/best-effort outcomes, complete versioned certificate/reference
serialization и Train→Test, conversion/PostTune/calibration и общая матрица.
JSON fixture не объявляется production exporter или controller checkpoint.
Исторические августовские наблюдения 4/8–6/8 сохраняются отдельно от этих
implementation checks.

## Принятая Git closure

PulseLib develop merge: bd79c6d62bd8a254b773e0b0fd9a393a5bb4c4e2,
опубликован до корневого merge. Production Core совпадает с проверенным
db78ded793330d95e617624e969ee72b42d75ab5; последующие child commits меняют
документы. Rdk остаётся f924023e78eb2f0775cca301272606b98de0f8f1,
Bin — 1c1c2e5064373b47d523fd6735aebe6785f2787d. Все 1034 опубликованных
artifact hashes и gzip payloads проверены локально как данные; численные
проверки выполнялись на указанных серверах.
