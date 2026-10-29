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
fresh-destination recognition controls. SSH transport вернул ненулевой статус;
сохранённые process-exit/exit-status необходимо отдельно прочитать до приёмки.
На M40 SSH оборвался; состояние сборки/процесса неизвестно. Это не основание
повторно запускать задание. Повторное подключение остановилось на jump timeout.

Readbacks: Elder `/home/user/timelearner-refactor/readbacks/`, M40
`/media/user/Data/TimeLearnerRefactor/readbacks/`; имена
`s03-spike-history-{baseline,fixed}-{normal,asan}-a1`.
Runtime каждой попытки отдельный и не обновляется работающим заданием.

После восстановления связи: проверить исходные process statuses/XML и отсутствие
skips, завершение M40 и ASan-диагностику; сохранить baseline и fixed runtime
manifests, XML/logs и primary owner observations через Git с hashes. Только
затем решать scoped acceptance и merge. Полная матрица LT-моделей и runner
спайковых target/foil проб этим изменением не объявляются завершёнными.
