# История спайков на границе Reset

29.10.2026. Подэтап этапов 3/4, необходимый для frozen recognition observations.

`NPulseLTZoneCommon::ADefault` создавал историю размером 1×1 со значением 0.
`AReset` очищал внутренний список событий, но выполнял `ToZero` над выходным
массивом, сохраняя его размер. До следующего Calculate наблюдатель видел
фиктивные события в t=0, в том числе несколько событий после прошлой пробы.
Нулевое время нельзя фильтровать: настоящий первый спайк также может иметь t=0.

Исправление у владельца: Default и Reset публикуют массив 1×0. Динамика,
порог, scheduler и bool-контракт lifecycle не изменены. Ручной дополнительный
Reset встроенного генератора NPulseSimpleLTZone не добавлен: это штатный
зарегистрированный static child.

## Проверки и состояние приёмки

Baseline root `9ecb3967fa30d813785a08a6ce509d622fc767ea`:
на обоих workers два native теста воспроизвели два ожидаемых отказа.
Первый проверяет пустую историю после native Init/Reset объекта из storage.
Второй использует настоящий NPulseLTZoneThreshold в model scheduler:
реальный спайк в t=0 сохраняется, длительный импульс не создаёт второй onset,
но Reset ошибочно оставляет timestamp. Baseline журналы находятся на workers;
их Git-публикация ещё не выполнена.

Fixed root `d13620e1e5734373d840fc4f2efe5db049d30c62`, PulseLib
`1de63d0` расширяет второй тест двумя раздельными rising edges с проверкой
обоих timestamps, затем проверяет пустую историю после Reset и молчаливого тика.
На Elder-1 получен native XML/log итог 12/12 pass: 10 lifecycle tests и два
fresh-destination recognition controls. После восстановления VPN подтверждён
M40 ASan: те же 12/12 pass, ноль skips/errors. Оба native процесса вернули 0;
внешняя оболочка вернула 1. Задания завершены, повторно не запускались.

Readbacks: Elder `/home/user/timelearner-refactor/readbacks/`, M40
`/media/user/Data/TimeLearnerRefactor/readbacks/`; имена
`s03-spike-history-{baseline,fixed}-{normal,asan}-a1`.
Runtime каждой попытки отдельный и не обновляется работающим заданием.

## Причина внешнего exit status и публикация

Одинаковая диагностическая команда с успешным телом при parent SHLVL=0
возвращает 1 через `bash -lc` и 0 через `bash --noprofile --norc -c` на обоих
workers. `.bash_logout` вызывает `clear_console` при SHLVL=1; под `set -e`
ошибка очистки консоли изменяет итог login shell. Это ошибка оболочки запуска,
не ошибка native тестов. Исходный process status=1 не переписан. Первая
диагностика A1 запускала вложенную оболочку с другим SHLVL и получила два нуля;
её ошибочное ожидание сохранено. A2 явно задаёт SHLVL и воспроизводит причину.
Следующие задания должны использовать non-login shell, собственное окружение
и раздельные process/native statuses.

Пакеты опубликованы: Elder `8e1569e7bcb41a531babe68d569d0661b37f9d4c`,
M40 `04a705c9d05967d3cf5ffd4d6eb96077f75d2f49`, разделы
Reports/StructTrain/TimeLearner/s03-spike-history-{elder1,m40}.
Локально проверены по 98 stored / 96 raw hashes; до публикации на workers
повторно проверены 56 / 150 runtime path/hash records соответственно.
Включены baseline и fixed XML/logs, manifests, primary fresh-owner observations
и обе короткие shell diagnostics. Native ASan ошибок в проверенном журнале нет.

Это scoped acceptance дефекта истории событий. Полная матрица LT-моделей и
runner спайковых target/foil проб этим изменением не объявляются завершёнными.
