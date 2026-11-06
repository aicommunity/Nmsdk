# Общий бюджет невалидных проб — кандидат, 06.11.2026

Статус: исходный дефект **воспроизведён на M40**, fixed4/74 прошли;
native-приёмка дала21/23 на обоих SDK, с побайтно одинаковыми откликами.
Документ не является свидетельством runtime-исправления или закрытия этапа 7.
В develop этот C++ кандидат не объединён.

Baseline завершён на M40 в отдельном runtime; fixed-сборка поставлена после
его closure, освобождения lease и подтверждения ожидаемых baseline assertion
failures. Фактические PID/start_ticks проверены по /proc. Исходные launch/wait
наблюдения сохранены в [job record](AttemptInvalidObservationBudgetJobs.json);
они не являются постоянно обновляемым монитором и не доказывают fixed PASS.

После fixed normal gate дополнительно поставлены 23 оригинальные native
проверки реальных Classic/Branch: поиск N0/N1, отрицательный final pass,
остановка/timeout, сохранение censored evidence, completed/stopped model
transport, configured paths и N0 repeated partial state. Они используют новый
compiled SDK, без дополнительной сборки, и ждут closure fixed worker с
положительными исходными 4/74 JUnit. Это отдельная интеграционная приёмка,
не повтор 32 управляемых сценариев и не научная классификация.

В неизменяемых временных producers обнаружены унаследованные описательные
поля «build only/native gates disabled» и старое название waiting state.
Ошибки этих подписей перечислены в job record. Реальное выполнение определяется
gate specification, JUnit, process identity и kernel cgroup, а зависимость —
точным dependency.job_id. Работающие producers не редактировались; при
последующем разборе нельзя использовать эти подписи как доказательство
отсутствия тестов либо идентичности предшественника.

## Исходный риск и сохранённый baseline

Baseline с новыми регрессиями и прежним PulseLib:
root `7cc21bdd9e0904f8f5052466651e0682f2f1f1a3`
(ветка `codex/timelearner-invalid-budget-baseline`),
PulseLib `12d8c8a41c998ae1516496f716a0ae0f3d312b3e`.
Исправление PulseLib: `2c7e0144a902795cb6287ee677cff5aa08998847`.

В исходном BoundedTrainingSession счётчик `invalid` учитывает отклонения поиска.
BeginVerification передаёт полное `maximumInvalidObservations` новому
FinalVerificationSession, имеющему собственный `invalidCount`. При следующем
проходе создаётся ещё одна final session с полным бюджетом. Отклонения final не
списываются со счётчика поиска. Это подтверждено чтением production-кода;
возможность получить Exact после превышения общего бюджета теперь отдельно
воспроизведена тестами baseline, как описано ниже.

## Подтверждённый исходный результат

M40 выполнил четыре исходные production test functions: Classic/Branch × N0/N1.
Все четыре завершились assertion failure, исходный exit1 сохранён. В каждой
функции ровно восемь ожидаемых assertion failures: два превышающих бюджет
сценария × observation/preparation corruption × статус и наличие сертификата.
Итого32 assertions относятся исключительно к этим16 сочетаниям. Остальные16
сочетаний, проверяющие допустимый одиночный повтор и нулевой бюджет, не дали
assertion failures; отдельными зелёными JUnit cases они не объявляются.

В превышающих бюджет случаях фактический TrainingStatus=Exact (enum2), а не
InvalidObservation (enum6), и Certificate присутствует. Сверены исходные строки
двух assertions и каждый scenario/preparation trace. Это нарушение заявленного
бюджета выполнения, а не доказательство неверных физических residuals или
успешной научной классификации. Наблюдения производились production recorder
на управляемых численных waveforms; реальный нейрон этим baseline не проверен.

Proof `9c79384fcdec4eee1da2c00e5746fa33b2ae24fe` сохраняет исходные JUnit,
runtime/maps/process owner, compiler logs и архив34 members (66436 bytes).
Повторно сверены все members,481 root source files и265 PulseLib Core files
с точными Git blobs. Fresh kernel closure и released lease проверены перед
созданием evidence commit в отдельном Git store. Источники и runtime сборки
не изменены. [Receipt](AttemptInvalidObservationBudgetBaselineVerification.json),
[primary bundle](../../../Reports/StructTrain/TimeLearner/s07-attempt-invalid-budget-baseline-m40-a1/bundle.json).

## Серверная проверка исправленного SDK

На root `a2df1eac50bfb53e5ce6c9220eed8b7da7b5ba0b` / PulseLib
`2c7e0144a902795cb6287ee677cff5aa08998847` прошли4/4 новых regression functions
и74/74 смежных исходных tests, без skips/errors/failures. Использованы те же
новые регрессии, что в baseline:32 сочетания Classic/Branch, N0/N1,
observation/preparation failure и границ attempt budget. Это normal, не ASan.
Два оригинальных JUnit/process captures принадлежат разным actual native PID.

Proof `98e6fbc979ec3cd8ab75f0bff28b0cbbcde34fcc`:49 archive members,
70356 bytes xz, все746 root/Pulse source files сверены с точными Git blobs.
[Независимая сверка](AttemptInvalidObservationBudgetFixedVerification.json).

Дополнительный исходный native23 gate завершился21 passed /2 failed.
`NativeLearnedState/ClassicConfiguredN1` и `NativeLearnedState/BranchConfiguredN0`
остановились на `ASSERT_TRUE(service.Certificate())` после фактического
maximum_sweeps_exhausted. Их cold Train с SyncTolerance=0.02 не выполнил
предусловие completed-model transport. Это не сбой чтения JUnit или timeout;
полный исходный exit1 сохраняется. Эти два результата не превращаются в PASS
потому, что узкие budget regressions прошли.

Proof `8447d4f937623c56ed7292fd4c6c18aeb9fbbadb` сохраняет696 archive members,
788880 bytes xz, первичные пробы, summary до assertion и runtime captures.
Все members,335 tool source files и306 native source files повторно сверены.
На прежнем root7cc/Pulse12d выполнен **тот же неизменённый набор23 tests**,
с тем же normal build profile и отдельным runtime: также21 passed /2 failed,
с теми же assertions и maximum_sweeps_exhausted. Все252 CSV и7 training
precondition summaries побайтно совпали. Сверены compiler, значимые build flags,
resource root и все фактически загруженные shared files. Эти два отказа
воспроизводятся без нового budget-кода; в пределах этого контроля изменение
бюджета их не объясняет. Это не доказательство прохождения всей native матрицы.

Proof `a3710b95842d57813032b9bcd8ab3cc80075f92a`:696 members,
788492 bytes xz; все335 tool/306 native source hashes и все members проверены.
Каждый парный CSV/summary hash также совпадает с обоими опубликованными
primary archives, не только с текущими файлами сервера.
[A/B receipt](AttemptInvalidObservationBudgetNativeABVerification.json).
Список304 прежнего gate сам по себе не подтверждает любой иной набор случаев.
Следующее исправление fixtures должно сохранить исходный cold Train0.02 как
отрицательный контроль, а completed transport проверять отдельным явно
объявленным положительным случаем. Нельзя просто ослабить исходные tolerances
или назвать stopped Train завершённым ради прохождения assertion.

Приёмка конкретного budget fix, исправление неверных fixture assumptions и
полная приёмка исходного этапа7 — отдельные утверждения. Общий C++ кандидат
пока не объединяется в develop. Исторические и отрицательные измерения сохранены.

## Контракт и изменение

`maximumInvalidObservations` задаёт число разрешённых восстановлений после
невалидной пробы за **всю попытку** BoundedTrainingSession. Ноль останавливает
первую невалидную пробу, единица допускает один повтор и останавливает вторую.
Бюджет не восстанавливается после изменения кандидата, перехода в финальную
проверку или начала следующего прохода. Новая попытка имеет новый бюджет.

```text
begin final verification:
    final retry allowance = attempt allowance - consumed invalid probes
    accounted final invalid count = 0

after every final Arm / Consume, before accepting its result:
    delta = final invalid count - accounted final invalid count
    account delta against the attempt allowance
    stop InvalidObservation if allowance exceeded
    otherwise process the final status normally
```

FinalVerificationSession предоставляет фактический счётчик InvalidObservations.
Размер списка Rejected для этого не используется: список также может содержать
записи об инвалидировании ревизии модели. Счётчики инкрементируются с насыщением,
без переполнения. Ошибки подготовки Arm учитываются сразу, в том числе когда
дочерний контроллер разрешил повтор и остался Collecting.

Не меняются CapturedPerInput, tolerances, порядок входов, измеритель, N0/N1,
физика, scheduler и сигнатуры Build/Calculate/Reset. Исправление не вводит
восстановление отсутствующих пиков и не устраняет само по себе неоднозначность
stock burst assignment. Оно ограничивает число повторов честно объявленным
бюджетом, не превращая остановку в PhysicalInfeasible.

## Регрессии и оставшаяся приёмка

В штатный Test_PulseLib_StorageComponents добавлены четыре TrainingInvalidBudget
теста: ClassicN0, ClassicN1, BranchN0, BranchN1. Каждый выполняет восемь сочетаний:
четыре сценария для повреждённого final observation и для неверной final
preparation. Используются исходные production BoundedTrainingSession,
FinalVerificationSession и ProbeRecorder, с контролируемыми численными
waveforms; физический Rdk-нейрон этим тестом не моделируется.

Сценарии:

1. Одна невалидная поисковая проба, затем невалидная final: требуется остановка
   на второй, без сертификата Exact.
2. Невалидная final, затем валидный отрицательный final pass и новый проход:
   невалидная поисковая проба следующего прохода должна исчерпать общий бюджет.
3. Только одна невалидная final при allowance=1: валидный повтор должен оставаться
   возможным, с последующей обычной проверкой всех входов.
4. Allowance=0: первая невалидная final останавливает попытку.

Перед приёмкой необходимо:

- baseline собран и исходные ожидаемые падения сохранены; положительные
  контрольные сценарии и конкретные причины проверены по исходному JUnit;
- собрать fixed SDK в другом неизменяемом runtime и выполнить ту же матрицу;
- выполнить затронутые search/final/termination/N0-repeat регрессии и native
  stopped/completed transport, подтвердив корректные причины и сертификаты;
- выполнить необходимые normal/ASan проверки нового compiled-среза, сохранить
  JUnit, hashes, runtime/source closure и первичные данные через Git;
- после приёмки объединить PulseLib, затем корень в develop через --no-ff.

Локально разрешены только проверка diff/ссылок и фиксация исходников; численные
тесты и сборки выполняются на разрешённых серверах. Текущий ASan A5 использует
предыдущий неизменяемый SDK и не проверяет это новое изменение.
