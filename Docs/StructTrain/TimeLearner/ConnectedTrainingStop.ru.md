# Остановка native обучения через связанную IsNeedToTrain

Подэтап этапа 6. Полный план 0–12 не завершён.

Присваивание через `SetIsNeedToTrain(false)` уже вызывало ExternalStop. Однако
изменение реального output, подключённого к IsNeedToTrain через SetPointer,
не вызывает setter получателя. GetData возвращал false, но NativeTrainingService
продолжал capture/search. Это подтверждённый дефект управления, а не качество
обученного нейрона и не отказ return bool lifecycle.

## Исправление

Общий NativeTrainingAdapter получает read-only `trainingRequested`. BindNativeTraining
читает фактическую IsNeedToTrain.GetData обоих learner. Внутри уже существующего
try/catch сервиса запрос проверяется перед BeforeTick действиями и перед принятием
AfterTick наблюдения. Это учитывает изменения между тиками и из callback после
расчёта детей; копия управляющей логики в двух learner не вводится.

```text
if controller is active:
    if actual trainingRequested is false:
        cancel the pending probe
        stop the search
        clear the training certificate
        record the available observation
        finish as ExternalStop
        return
    continue the normal budget/action or observation path
```

В этом тике явный stop проверяется раньше budget/action. Завершённая ранее
сессия не переименовывается в ExternalStop. Внешний source не изменяется новой
логикой. Вызовов Calculate/Build/Reset learner не добавлено; отмена использует
существующее восстановление probe routing/source. Bool-контракт Rdk не меняется.
Pure controller adapters могут не иметь provider: тогда запрос считается активным.

## Воспроизведение и проверки

Root 93df1bbe3: первая fixture ошибочно меняла ControllerVersion после native
ownership; все 20 cases остановились на штатном guard. Это setup error, не
воспроизведение дефекта. Root 01bf64842332f1748d8cb4eae1ba9d0d4a945dbb на обоих
workers: 16 expected failures, 4 keep-true controls pass. ControllerVersion=2,
Normalization=N1, Classic/Branch, CalculateMode 0/1. Флаг меняет настоящий scalar output отдельного
компонента, соединённый штатным SetPointer, без вызова learner setter.

Stop points: первая незавершённая проба; один принятый reference; search после
фактического edit; sample callback. Проверяется остановка в данном native tick,
отсутствие сертификата, неизменность параметров после stop и сохранение реального
состояния diagnostic. Keep-true snapshot снимается до локальной teardown-отмены;
его последняя cancelled trial является cleanup, а не проверкой внешнего stop.

Fixed root 38492772838dcb48afc1a3c44c0388ccb387c11c / PulseLib
c99c47d89c24baf48879ace3d6ded635f8485272: на обоих workers прошли 57/57 native cases,
включая 20 новых и 37 service/cold/stopped regressions. Independent auditor
b236ee563d99e07250db584146a82e925ce231ce: 10/10 Python/CLI, без skips/errors;
28 новых и 66 прежних primary trials, 16 diagnostic моделей без сертификата.
Проверяются фаза capture, effective mode/topology, source/learner bool readback,
counts и пакет/первичные CSV. M40 — ASan с detect_leaks=0. Все numerical jobs
завершены; оба process/native statuses=0, skipped cases отсутствуют.

## Ограничения

Scoped runtime gate относится к read-only scalar SetPointer, V2 и указанным
двум CalculateMode. Другие alias/source-sharing механизмы, запуск с изначально
ложным внешним input, полный restart/retarget matrix остаются отдельными
проверками. Рост внешнего флага сам по себе не обещает автоматический restart
завершённой сессии; используются явные reset/start API. Это не завершение всего
этапа 6 и не scientific evaluation.

Readbacks на workers: s06-connected-stop-baseline-{normal,asan}-a1/a2,
s06-connected-stop-fixed-{normal,asan}-a1 и s06-connected-stop-audit-a1.
Сборки, первичные данные и проверки выполняются на workers. Пакеты опубликованы:
Elder `8280a184e6e1e15a749119dfe08c4a646d48261c`, M40
`406191506fa162a52780ffd12fb4ccc0b6d1006e`, разделы
Reports/StructTrain/TimeLearner/s06-connected-stop-{elder1,m40}.
На каждом локально проверены 1069 stored / 1067 raw hashes; до публикации
повторно сверены 84 / 225 runtime path/hash records соответственно.
Это scoped acceptance описанного дефекта. Весь этап 6 остаётся частичным.

No-ff acceptance merges: PulseLib `98308fc9b6c2d831578194d00fc76b173b62627b`,
затем root `1845df823b1e7f656b1d01a040cad3b0e2555275`. PulseLib merge
отличается от tested Core c99c47d только документацией. Дочерний commit
опубликован до корневого gitlink. Восходящий внешний фронт не запускает старые
задания или серию D автоматически.
