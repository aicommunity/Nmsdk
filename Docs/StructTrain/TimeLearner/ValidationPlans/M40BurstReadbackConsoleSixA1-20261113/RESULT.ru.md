# Первая реальная Console-проба: отказ до наблюдения

Задание s07-burst-readback-console-six-m40-a1 завершено с failed assertion: из запланированных шести probes только первый Classic replay был запущен и завершился exit2. Наблюдение не сформировано, изменение Rs не выполнялось. Источник Python Root7362d102f89643afc7452545b0c40a5393f0745e; Console из SDK Root1ae8826338906fedff5efd914b93a3814a2a50db / Pulsedfb9a98244f91b4f4029d8470465fd40116436ca. Исходные controls сохранены в controls; записи результата — в failed-readback. Внешняя группа и Console закрыты, reservations освобождены. Научного verdict нет.

Причина: candidate_window_summary_requires_owned_finished_boundary. Диагностический monitor ошибочно запрашивал finished training summary после штатного Reset импортированного контроллера в Idle. Дополнительная несовместимость — ожидание legacy observed_packets у composite package7.

Root49689590cbdc0bbe5abccfb91374ad716f0ff977 отделяет idle readback от finished summary и сверяет историю composite-архива. Защита экспорта завершённого обучения сохранена. Математическая цель, принадлежность пиков, lifecycle и модель не меняются. Адресные DATA проверки на Elder прошли 13/13; отдельная свежая сборка и реальные шесть probes ещё необходимы. Отказ A1 не превращается в успешный результат после исправления кода.
