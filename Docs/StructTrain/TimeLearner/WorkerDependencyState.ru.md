# Pending: состояние ресурсной зависимости worker

inspect_worker_dependency(directory, registry, job_id, reservation_optional=False) — read-only проверка одной точной bound worker invocation. Фактический kernel/cgroup readback обязателен; сохранённые closure/recovery JSON сами по себе готовность не доказывают. Код не стартует следующий job, не вызывает adopt/stop и не освобождает lease.

Состояния:

| Условие | Результат |
|---|---|
| Жив worker или его descendant | pending, независимо от наличия receipt |
| Группа закрыта, lease того же initial PID/start_ticks/boot/uid удерживается | pending; требуется явное recover/release |
| Группа закрыта, её lease в registry released | ready с reservation_state=released |
| Группа закрыта, записей нет, reservation_optional=True | ready с reservation_state=not_created; released не приписывается |
| Нет обязательного lease, чужой owner, неоднозначный job_id, ошибочный id при существующем lease worker | refused |
| Неизвестная/изменённая invocation, epoch mismatch, повреждённые данные | ошибка, не ready |

Отсутствие reservation.json не является доказательством. Проверяется постоянный registry с сохраняемой историей; истечение TTL не освобождает ресурс. job_id — уникальное имя попытки в данном registry. API относится к initial main worker; резервирование другими descendant/controller owners требует отдельного explicit контракта. Не доказывается отсутствие ресурсов в неизвестных внешних registries.

ready означает только resource readiness. Даже worker с exit7 может иметь корректно закрытую группу и никогда не создавать lease. Его Train, observations, scientific validity и необходимость запуска зависимой фазы проверяет отдельный production auditor/runner. У всех результатов successful_execution_attested=False и scientific_verdict=None.

Причина изменения — реальные ранее сохранённые guards, требовавшие recovery-event у предшественника, который остановился до reserve. Общая функция различает такой случай без эвристики по имени terminal field. Существующие immutable задания не переподключаются к новому коду.

Подготовлены9 actual Linux unit/SQLite checks, без mocks/нейронных расчётов: живой worker; optional/required missing lease; held-expired и explicit recovery; чужой unit/owner; неправильный job_id; неоднозначные два lease; живой descendant; nonzero exit без ложного business success. Нужны оба server gates и внедрение в production dispatch. AST проверен локально; runtime PASS пока не получен. Это не полное завершение scheduler/fault/cancel/reboot/ConditionSpec/publisher этапа10.
