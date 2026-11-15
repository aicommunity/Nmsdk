# N1 recovery и амплитуда быстрого профиля — 15.11.2026

Отправная точка: root develop8395cf52960bf819ce6c5e52326b677921fa93a4, Pulse5052cfe1683ca38920b514aedfc3c37f4bd41aef. Работа в отдельных ветках codex/timelearner-n1-recovery-coverage корня и PulseLib. [Предыдущая пара](FastProfilePhysicsScientificReport-20261115.ru.md) завершена и архивирована; повторять закрытые задания нельзя.

## Отдельный exploratory cold Train

Наблюдение: fast-группа36 содержит четыре раздельных вершины и timing-ready input2 на полном L[121,121,121,1]/Rs86МОм. Амплитудный остаток−0.02347230991428706 вне допуска; наступил wall budget1800с. Конечное состояние L[122,122,121,1] относится уже к другому layout с незавершённым замером и не наследует этот остаток.

Новый опыт повторяет cold Train, а не продолжает unsupported checkpoint. Меняется только maximum_wall_seconds1800→3600 и идентификатор запуска; все128 probes/1280 edits/128 candidates/input/4 sweeps/4 recoveries, model budget7200с, геометрия до256, исходные targets CapturedPerInput, per-input Rs bounds и допуски сохраняются. Нормализация N1, 2000Гц, C2.5e-10/DissociationTC.002, C-trim/PostTune/calibration Off. В исходных controls сохранить original-before-budget.json и проверить полный JSON-diff до конфигурации с новым wall budget. Модель и амплитуды захватываются заново.

Это отдельное условие, не результат исходной пары с1800с. Тот же неизменяемый runtime cfcfd327b0b809ebeee1e5abf049c1661d17a860/Pulse5052; его файлы и исходники во время задания не меняются. Дополнительные300с — только запуск/экспорт, outer9000с включает DATA-анализ. Эксперимент не требует положительного исхода: сохранение честного stopped-state и полный пакет обязательны. Если обучение завершится, далее full-model transfer и frozen8 с реальным порогом; при остановке не выдавать diagnostic Test за завершённое обучение.

Новый run_label — только уникальный идентификатор попытки. Он не меняет ConditionSpec; wall budget меняет fingerprint через существующий production-сериализатор.

## Адресная правка алгоритма N1

[Подтверждённое ограничение](N1RejectedSearchCoverage-20261115.ru.md): после неоднозначной input1-пробы пять восстановлений сосредоточились на соседних L/layouts и shared-bank варианте. Нужно ограниченное покрытие совместных L/Rs proposals со свежим ResistanceDomainAssessment, сохранением downstream inputs и штатным apply/readback. N0-очередь не копировать вслепую.

Порядок работы: воспроизвести текущую production-последовательность; определить ограниченный порядок новых legal candidates; реализовать отдельно от valid-observation scheduling; kernel A/B с реальным контроллером на Elder/M40; isolated native SDK; cold same-condition N1-проверка и все выбранные full/omission/repeat графики. Не менять работающий runtime exploratory опыта. Не повышать допуски и не подтверждать синхронность прогнозом.

Всю приёмку фиксировать результатами и полными commit SHA. Child-first --no-ff merge, затем root; без переписывания истории. Предыдущий цикл дал реальные новые результаты и опубликованные артефакты (progress); исходный план по-прежнему активен, этапы1–12 частичны.

## Историческая постановка кандидата до приёмки

В Core/TimeLearner/BoundedTraining.{h,cpp} подготовлен отдельный opt-in путь для sealed rejected CandidateWindow при N1. Первый recovery предлагает тот же активный L, отделяет upstream bank Branch и первым проверяет нижнюю границу нового фактического Rs-domain. Следующие recovery используют ограниченное покрытие неиспытанных длин (наибольший пробел), сохраняя downstream/anchor. Если первый same-length domain недоступен, вне box либо не содержит новых полных кандидатов (например, уже испытанный singleton), разрешён один domain-only переход к дальней длине. Ни одна непринятая проба не становится scalar residual; свежие native domain, apply/readback и anchor/input обязательны. Допуски, бюджеты и обычное расписание по valid observations не меняются.

В production integration corpus добавлены пять cases NativeCandidateWindowRecovery: ClassicN1FixedRsExploresBeyondNearestMesh, BranchN1FixedRsExploresBeyondNearestMesh, ClassicN1RejectedWindowExploresFreshRs, BranchN1RejectedWindowExploresFreshRs, BranchN1FourInputsSeparateOnlyUpstreamBank. Первый снимок root сохраняет Pulse5052 для baseline; затем отдельный снимок закрепит candidate Pulse. Требуется выполнить одинаковый corpus на обеих версиях, сохранить исходные failures и положительную проверку candidate. Native fixture использует реальный storage/Environment/scheduler, а не копию функции или поддельный rejected token.

Этот абзац сохраняет состояние до приёмки; окончательные инженерные и научные результаты приведены ниже.

## Зафиксированные сравниваемые снимки

Baseline root47d67e8fa0d8ea9e2cf61e49ad7e7019dd91c50f/Pulse5052cfe1683ca38920b514aedfc3c37f4bd41aef; candidate root860ee87057196f0afb5b3a98cbd0bdacf378543a/Pulse42e35b63b6c25f59629f0436b9476a35d20cb2c4. Одинаковый исходник пяти новых native cases. На M40 отдельно запущены свежие source/build/runtime: s07-n1-recovery-baseline-sdk-m40-a1 и s07-n1-recovery-candidate-sdk-m40-a1. Canonical preparation обоих завершена успешно, окончательные SDK results ещё не приняты. Baseline control470669ef1dcc396c302c3e09ab0e8a43619b0be1; candidate controlb561ba8c6b88043f1566202687f1e244fb0cb5e5.

Общий SDK worker корректно останавливается на первом непрошедшем leaf. Поэтому отдельная проверка test_n1_recovery_baseline.N1RejectedRecoveryBaselineTest подготовлена для всех пяти изолированных контрпримеров на том же уже собранном и закрытом baseline runtime. Она требует полный JUnit ровно выбранного C++ case, native exit1 и статусы process_error/valid/failed и failure по ожидаемому length/Rs свойству, отвергая exception/fixture failure. Её Python PASS означает воспроизведение пяти ожидаемых native FAIL, а не успешность baseline SDK или обучения. Бинарник, source closure и исходный failed receipt не меняются; повторной свежей сборки не заявляется. До получения runtime receipt эта проверка остаётся неподтверждённой.

## Независимая kernel-проверка Elder

A1 s07-n1-recovery-kernel-elder-a1 закрыт с operation_passed=false: обе компиляции остановились до тестов, поскольку полный Test_PulseLib_BoundedTraining.cpp включает CandidateRecoveryEvidenceJson.h/QJsonObject. Это недостающая Qt Core зависимость standalone harness, не отрицательный результат алгоритма; assertions не исполнялись. Источник и ошибочные receipts сохраняются.

Для A2 controller_ab schema2 явно объявляет qt_core_package=Qt5Core/Qt6Core, получает compile/link flags и версию через системный pkg-config, фиксирует их и бинарник pkg-config в toolchain и повторно проверяет после обеих сторон. Исходные schema1 Qt-free проверки сохраняют прежнюю команду. Один и тот же набор106 исходных cases и те же baseline/candidate production SHA; native Rdk integration здесь не заявляется. Git доставлен на Elder через проверенные bundles, поскольку там не разрешается имя GitHub; исходные репозитории/сборки не переключаются.

## Уточнение приёмки 16.11

Все пять новых N1 native cases воспроизведены на baseline5052 как process_error/valid/failed, Python-проверка исходных контрпримеров1/1 принята, whole group closed. На candidate42e35 те же пять cases прошли completed/valid/passed; полная147-case SDK серия ещё выполняется. Это адресная проверка изменения proposal order и native domains, не доказательство научной сходимости.

Elder A2 остановился на link из-за отсутствующего в декларации CandidateRecoveryEvidenceJson.cpp; A3 добавил весь штатный translation unit и исполнил105 baseline assertions без failures, но правомерно отказал по неполному inventory: старый regex controller_ab считал макро-шаблон TrainingInvalidBudget/name тестом, пропуская четыре реальных expansion. В новом источнике используется тот же _literal_cases, что и production collector. Реальный неизменённый corpus содержит109 cases, а не106. Ни тесты, ни допуски не меняются; четыре budget cases включаются в исполнение вместо фиктивного name. A1/A2/A3 failures остаются исходными неуспешными gates; candidate сторона A3 до этого отказа не исполнялась.

Длинный fast A3 native завершён BudgetExhausted:20 scalar candidates,42 search probes,20 edits. Последний полный input2 замер на L[122,122,121,1], Rs2=10871143.923391603: timing−0.00050000000004502с, amplitude−0.0023612200739181466 (236.122 допуска). Конечный Rs2=9772503.178596893 относится уже к следующему неполному замеру и не наследует этот residual. Certificate=null. Полный CLI/DATA/physical1/1 принят; новый временной отчёт1/1 готов:24 PNG,6 overview просмотрены. [Научный отчёт и ограничения](FastProfileWallBudgetScientificReport-20261116.ru.md).

## Подтверждённые квитанции и текущий научный опыт

[Компактная приёмка](N1RecoveryValidationAcceptance-20261116.json): M40 SDK147/147, пять baseline-контрпримеров1/1 и Elder109/109 на обеих версиях A4 приняты с whole closure. Все первичные failures и positive receipts сохранены вне Git: M40 SHA2560451fd666029e619d70bb1450b23c8338bdef29f3268c15e9a25997b1ff75a4d (28448514байт/3507файлов), Elder SHA2563baab610075685040e07cf05dd5263d8ba0c55d6ccd2e01234848bf08237ffc2 (5178089байт/1230файлов). Каталог /media/user/Data/Nmsdk-StructTrainExpArchive/experiments/2026-11-16/n1-recovery-coverage.

Новый actual cold Stock Train s11-uniform-profile0-N1-recovery-train-m40-a1 запущен на неизменяемом runtime root860ee/Pulse42e35 после SDK147/147. Полный job структурно равен исходному Stock A1 после удаления только run_id и контрольного sha256. Физика, исходное состояние, допуски и все научные бюджеты, включая1800с, прежние; changed Core paths только BoundedTraining.cpp/.h. Controls3d1768eb42a600dfed71514645241ce9efa297b1. Опыт завершён: CLI/DATA/physical приняты, все процессы закрыты; итог budget_exhausted/native_composite_group_time_budget_exhausted, certificate=null. Первые22 scalar measurements точно совпали с исходным Stock A1, один measured candidate input2 одновременно выполнил timing/amplitude допуски. Новых полных scalar measurements после изменения recovery не получено. Конечный граф L[256,255,27,1], Rs[86,2.8800715552629367,21.232304307596028,86]МОм; последняя группа53 измеряла anchor input3 и не закончена. Этот граф не наследует residual прежних кандидатов. Научного улучшения сходимости пока нет; следующий вопрос — полезность и стоимость выбора recovery-кандидатов, не ослабление критериев. Полный primary1123файла/47478203байта, SHA25645aa3d1db8fdc2600ac438f304d5ad0ab199b136fea6cb71553f7413a0c3782c, хранится вне Git. Собственный сравнительный временной отчёт этого Stock A/B ещё не построен. Прежние закрытые задания не перезапускались. [Текущий статус и приоритеты](CurrentStatus-20261116.ru.md).
