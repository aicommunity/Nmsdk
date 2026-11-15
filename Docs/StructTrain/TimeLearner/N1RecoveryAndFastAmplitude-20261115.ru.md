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

## Кандидат реализации: требуется приёмка

В Core/TimeLearner/BoundedTraining.{h,cpp} подготовлен отдельный opt-in путь для sealed rejected CandidateWindow при N1. Первый recovery предлагает тот же активный L, отделяет upstream bank Branch и первым проверяет нижнюю границу нового фактического Rs-domain. Следующие recovery используют ограниченное покрытие неиспытанных длин (наибольший пробел), сохраняя downstream/anchor. Если первый same-length domain оказался singleton/Unavailable/не имеет новых Rs, разрешён один domain-only переход к дальней длине. Ни одна непринятая проба не становится scalar residual; свежие native domain, apply/readback и anchor/input обязательны. Допуски, бюджеты и обычное расписание по valid observations не меняются.

В production integration corpus добавлены пять cases NativeCandidateWindowRecovery: ClassicN1FixedRsExploresBeyondNearestMesh, BranchN1FixedRsExploresBeyondNearestMesh, ClassicN1RejectedWindowExploresFreshRs, BranchN1RejectedWindowExploresFreshRs, BranchN1FourInputsSeparateOnlyUpstreamBank. Первый снимок root сохраняет Pulse5052 для baseline; затем отдельный снимок закрепит candidate Pulse. Требуется выполнить одинаковый corpus на обеих версиях, сохранить исходные failures и положительную проверку candidate. Native fixture использует реальный storage/Environment/scheduler, а не копию функции или поддельный rejected token.

На момент этой записи исправление не принято, научное улучшение не заявляется.
