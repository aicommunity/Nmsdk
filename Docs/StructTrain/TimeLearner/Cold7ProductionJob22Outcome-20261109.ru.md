# Production validation cold7 — 09.11.2026

На M40 проверены **22/22** cases: 9 адресных проверок входа `native_pipeline_worker.validate_job` и 13 регрессий composite configuration. Source `79d707d4b05e257d52f2b2e1d7f8cff14f6c6228`, controls `d321bd1492a9c92c0f6ccefc026c14e8f32649ce`; Tool `cec33f2fcceb8c8f815e3494173bf48dcd39ed6c`.

Исправлен ранний путь в `project_training_configuration`: явно выбранная schema7 проходила через legacy recovery validator до более поздней cold7 dispatch и отклонялась. Теперь private projection сохраняет исходную декларацию и использует специальный контракт cold7. Это не изменение wire schema, математической цели или разрешение legacy-конфигурациям молча выбирать новый режим.

Контроллер завершён с кодом 0 за 14.868 s, diagnostics clear; source и Tool до/после совпадают. Root сверил все 22 имени с unittest log, отсутствие skipped/failures/errors и освобождение собственного lease `b6e2ecc1-434e-42ce-a205-ffb611b313b1` после закрытия группы. [Сжатые исходные наблюдения и журнал](../../../Reports/StructTrain/TimeLearner/s10-cold7-production-job22-root-observation/index.json) сохранены отдельно от вывода.

Проверки вызывают production validation на контролируемых конфигурациях. Они **не запускают C++ preflight, Train или Test** и не дают научного допуска. Изменение предназначено для future package6 ветки; её C++ ancestry не должно автоматически попадать в maintained develop до отдельной приёмки.
