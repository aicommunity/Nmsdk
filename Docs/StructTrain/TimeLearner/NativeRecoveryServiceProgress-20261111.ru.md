# Проверка доставки recovery в native service — 11.11.2026

Source root `4417545808e422fcc202b235f566b0cbdc0855cc`, Pulse `dbc8a408e08095c274fae64a44c5bdbeddd4f7c4`. Эта комбинация пока не получила runtime приёмку.

M40: canonical D1 отклонён до сборки (`native_preparation_leaf_union_or_order`): общий selected_ids был ошибочно отсортирован отдельно от runplan. Исходный отказ, exception, terminal, closure и lease release сохранены в [D1](ValidationPlans/M40CandidateWindowRecoveryServiceD1-20261111/). D2 меняет только порядок декларации, оставляя те же222 cases и source. Canonical D2 принят, native job запущен: supervisor492118, start_ticks347615707, boot0340843f-8a05-4b7e-bd66-afeefecdbe55. [Точные условия и receipt](ValidationPlans/M40CandidateWindowRecoveryServiceD2-20261111/). Сборка изолирована от прежних runtimes.

Состав:98 decision,29 rejection/factory,19 core/wire,76 delivery/callback и затронутых прежних composite service/source guards;125 отдельных leaf groups. Новые service cases сохраняют archive2/primary и deliveries/runtime; direct core cases сохраняют versioned event JSON. Новые cases ещё не являются принятыми проверками.

Elder продолжает прежний C2 root5643/Pulse0fb: последняя проверка живого supervisor2684254/start396745925 показала45 закрытых leaf results без ошибок; terminal ещё отсутствовал. Не смешивать это с текущим source service222.

Windows .14 исключена из расписания для апгрейда по просьбе пользователя, пока он не сообщит о готовности. На ней ничего нового не запускалось.

Отдельная независимая Python проверка использует десять реальных C++ cold8/runtime3/legacy documents C2 M40 (46774bytes), Git fixture manifest и declared fixture fingerprint. Шесть cases проверяют оба topology, неизменность данных, принятие только соответствующим reader и отказ downgrade. [Условия](ValidationPlans/M40NativeRecoveryWireInterop6A1-20261111/). Принято6/6: execution completed, assertions passed, failures/errors/skips пусты; whole group closed, lease released и owner missing. Полные сырые записи сохранены в completed и проверены readback-integrity. Это проверка форматов DATA, не runtime service delivery или классификация.

Остаются: версия model/summary с полным recovery ledger, boundary import, Console, independent native event joins, ambiguous service/C-context/partial-repeat recovery, проверки затронутой матрицы и stockN4 A/B. Старые package6/summary7 намеренно отказывают при наличии новой policy/history вместо молчаливой потери событий. Эти отказы не закрывают поддержку versioned export/import. До её приёмки дорогой Train с новой policy не запускать.
