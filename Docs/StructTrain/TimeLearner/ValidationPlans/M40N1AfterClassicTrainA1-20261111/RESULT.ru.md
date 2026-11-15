# Classic stock N4/N1: фактическая остановка и границы вывода

SDK subject: root fcfd8bdff149c14cbe67149e996945d122bf954d / PulseLib 5f1a4ac6f9aff208ada7f8bcf62645c9d79a6615. Python actor fd55a9936ba6018ca86e583c0e844b10fb582d56. M40, новый приватный runtime.

Процесс native completed/0/valid (613.1407619719394 с), parent completed/0 (743.7951595806517 с). Owned closure подтверждена, lease released; operational diagnostics clear. Итог обучения invalid_observation: composite_train_assignment_missing;omission_group_closed, certificate=null. Test и калибровка не запускались.

Состояние L=[54,1,1,1], Rs=[86000000,86000000,86000000,86000000], Ns=1. Выполнены 4 edits, 14 search probes; всего 18 composite groups, 108 native probes, 388908 sample frames, 41684140 primary bytes. Повторные raw/composite CSV — копии одних наблюдений, не независимые эксперименты.

## Локализация дефекта измерения

Группы 1–13 приняты. Группы 14–18 повторяют отказ на input0 при неизменённом model revision. В последней группе selection.geometry содержит candidates=[], validity=missing, reason=no_unique_assigned_basin_peak_in_declared_window. Глобальный matched-omission отчёт отдельно ambiguous; подменять им причину используемого измерителя нельзя.

Прогноз окна взял исходную задержку L=1 (29 кадров) за линейный коэффициент на сегмент. При deltaL=53 shift=1537 и window=[1546,1626] кадров, то есть [0.773,0.813] с от начала full-before. Обнаруженные в полной записи вершины находятся на кадрах 1146,1466,2010 (0.573,0.733,1.005 с). Окно действительно пусто относительно этого списка вершин. Это не доказывает принадлежность любой из этих вершин input0 и не разрешает заменить закреплённый максимум глобальным.

Следующий обязательный разбор: полный временной график soma0 и фактических входов для последнего принятого кандидата input0 и первых/последних отказов; full-before/full-after и omission controls; наложение объявленных окон; масштаб обзора и локального фрагмента. После проверки принадлежности — отдельное исправление прогнозирования/восстановления окна и адресный A/B. Не менять CapturedPerInput, tolerances, условия настоящего слияния или статус Exact ради прохождения прогона.

## Проверка времени финализации

Применены отдельные native budget=1800 с, process timeout=2100 с и parent=3600 с. Адресный production-path тест проверил эти значения. Этот прогон завершился до лимита и потому не проверяет поведение на границе 1800 с и не доказывает причину прежнего Classic timeout.

[actual-result.json](actual-result.json) — фактический аудит результата и closure. [assignment-group-readback.json](assignment-group-readback.json) — read-only проекция всех 18 group JSON с сохранёнными полями selection/measurement/window_proposal и ссылками на raw. Полная компактная публикация новых первичных данных и графиков ещё требуется; один серверный путь не закрывает требование воспроизводимости.

Исходные этапы плана остаются частичными, эта ветка не принята в develop.
