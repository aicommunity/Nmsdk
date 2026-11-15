# Native Train подтверждён

На 2026-11-12T14:36:42.981410+00:00 kernel cgroup inspection подтвердил running controller и отдельный running native Train. Записано30 CSV; это количество файлов наблюдений, не число поисковых решений. Native preflight execution сохранён вместе с исходными bindings: [receipt](startup/readback-integrity.json), [снимок наблюдения](startup/observation.json).

Задание s07-full-domain-budget16-train-m40-a2; исходный request находится в commitd3cd101cdd749f752d7a44827c71bb7ad0d205da. Итог обучения, финальная модель и классификация пока неизвестны. Бюджеты сохраняются; повторно задание не запускать, сначала проверять существующий handle.

Позднейшее уточнение12.11: повторный SSH и отдельная TCP-проверка jump host завершились timeout; Automats2 показывает Disconnected. Последнее kernel-подтверждение — native running; последующие пакеты CSV также наблюдались, но terminal outcome после потери связи не получен. Задание не перезапускалось. Истечение ожидаемого времени не заменяет проверку terminal result.

Терминальная проверка после восстановления связи: задание закрыто, native timeout2100s на формировании summary8. [Подтверждённый итог](RESULT.ru.md) заменяет прежние оперативные предположения; learning outcome остаётся неизвестен.
