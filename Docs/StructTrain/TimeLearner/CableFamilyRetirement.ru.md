# Историческая группа cable_model и E1

Подготовлено удаление20 связанных исходников из текущего дерева:8 standalone Python/C cable tools и12 E1 utilities. Это часть миграции, не научная runtime-приёмка. Source snapshot `3c5e777393776d5340131b03a31b34f4cb668b27`. Точные20 путей, full commit, blob SHA1, SHA256 и размеры внесены в script_migration.json; wrappers и копии не остаются.

## Зависимости и границы

E1 timing/amp/fastspan используют CABLE_SIM; E1 four-dendrite/separability импортируют library/classic_full; E1 relaxation динамически загружает e1_2_repeatability.py. Поэтому весь набор убирается одной группой. E1 Console/probe utilities также используют исторические Bin repro_cold_lib/selectivity_metrics/tl_probe_kernels и ручные overlays. Новая версия этих старых алгоритмов не объявляется частью production CLI.

Проверены буквальные imports/callers в root Scripts/Docs и build scripts на snapshot выше, Bin99f58da9296a794374cef679bbb878cb62af979a, Pulse9ec4566d71bf56d4eeb5c8a920bbc683fcd85299. Вне удаляемой группы исполняемых зависимостей не найдено. Bin audit_l_oscillation.py содержит только строковую метку cable_model_vs_synced_peak, не import/вызов. Dynamic paths внешних пользователей этим поиском не исключаются.

Обнаруженные ограничения исторической постановки сохраняются явно:

- standalone cable.c/cable2.c воспроизводят собственные Euler/cascade updates; они не используют native scheduler/storage graph;
- library.py задаёт общий C=tau/Rm, глобальный DT=SUB/F, а subprocess.run не проверяет exit code. Такое приближение не подтверждает произвольную heterogeneous physics и частоту;
- E1 surrogate/proxy inhibition не является проверкой реальных native inhibitory routes;
- offline peak/margin не заменяет реальный spiking threshold run;
- E1 Console overlays и исторический scorer не заменяют полный versioned model export и strict trial validation.

Старый README сообщает совпадение одиночного пика W04 и частных длин. Это частное историческое наблюдение, не общая эквивалентность моделей; совпадение L не критерий сходимости. Августовские визуально подтверждённые4/8–6/8 сохраняются как результаты исходного протокола.

## Сохранность и проверка

Данные JSON/TSV, модели и исторические отчёты не удаляются и не пересчитываются. Старые команды в исторических документах относятся к своему Git snapshot. Для извлечения исходника использовать retrieval_command соответствующей manifest record; source snapshot не подменяет фактический код эксперимента.

Manifest теперь141 records:139 retired,2 moved; complete=false. Path-based остаток217 уменьшается до197 (9 root+188 Bin), это нижняя граница, не доказательство полноты миграции. Активные specialized analysis и E05 остаются отдельными pending items.

До merge требуются production history verify-migration на обоих workers для всех141 records, negative tree с восстановленным старым путём, отсутствие посторонних code/config/data изменений и полный Git retrieval. Исторические программы не исполняются. Наличие подготовленного manifest не считается этой приёмкой.
