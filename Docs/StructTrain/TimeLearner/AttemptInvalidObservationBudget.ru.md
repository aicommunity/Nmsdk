# Общий бюджет невалидных проб — кандидат, 06.11.2026

Статус: исправление подготовлено; серверные baseline/fixed проверки **ещё не
выполнены**. Документ не является свидетельством runtime-исправления или закрытия
этапа 7. В develop этот кандидат не объединён.

## Исходный риск и сохранённый baseline

Baseline с новыми регрессиями и прежним PulseLib:
root `02e4d46fa79c138fa6a09568d1c10ee1bf677efb`,
PulseLib `12d8c8a41c998ae1516496f716a0ae0f3d312b3e`.
Исправление PulseLib: `2c7e0144a902795cb6287ee677cff5aa08998847`.

В исходном BoundedTrainingSession счётчик `invalid` учитывает отклонения поиска.
BeginVerification передаёт полное `maximumInvalidObservations` новому
FinalVerificationSession, имеющему собственный `invalidCount`. При следующем
проходе создаётся ещё одна final session с полным бюджетом. Отклонения final не
списываются со счётчика поиска. Это подтверждено чтением production-кода;
возможность получить Exact после превышения общего бюджета должна быть отдельно
воспроизведена тестами baseline, а не объявлена измеренным фактом.

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

- собрать baseline на сервере и сохранить исходные ожидаемые падения вместе с
  положительными контролями; отдельно проверить валидность fixture и причины;
- собрать fixed SDK в другом неизменяемом runtime и выполнить ту же матрицу;
- выполнить затронутые search/final/termination/N0-repeat регрессии и native
  stopped/completed transport, подтвердив корректные причины и сертификаты;
- выполнить необходимые normal/ASan проверки нового compiled-среза, сохранить
  JUnit, hashes, runtime/source closure и первичные данные через Git;
- после приёмки объединить PulseLib, затем корень в develop через --no-ff.

Локально разрешены только проверка diff/ссылок и фиксация исходников; численные
тесты и сборки выполняются на разрешённых серверах. Текущий ASan A5 использует
предыдущий неизменяемый SDK и не проверяет это новое изменение.
