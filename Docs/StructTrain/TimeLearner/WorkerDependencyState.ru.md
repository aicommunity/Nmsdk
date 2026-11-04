# Состояние ресурсной зависимости worker

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

Подготовлены9 actual Linux unit/SQLite checks, без mocks/нейронных расчётов: живой worker; optional/required missing lease; held-expired и explicit recovery; чужой unit/owner; неправильный job_id; штатный отказ второго lease с тем же job_id и сохранность первого; живой descendant; nonzero exit без ложного business success. Два server gates прошли9/9:по10 реальных kernel units и9 SQLite registries, без failures/errors/skips. [M40 primary](../../../Reports/StructTrain/TimeLearner/s10-worker-dependency-m40-normal-a2/README.ru.md), [Elder primary](../../../Reports/StructTrain/TimeLearner/s06-corrected-baseline-and-dependency-readbacks-a1/README.ru.md). M40 independently verified18 files/333 members/558 source blobs/18 SQLite primary-readback pairs с учётом failed attempt. [Receipt](WorkerDependencyM40Verification.json). На Elder выполнено также реальное ожидание предшественника через schema2 operational registry; полный schema2/3 fault matrix и production dispatch integration остаются открытыми. Это не полное завершение scheduler/fault/cancel/reboot/ConditionSpec/publisher этапа10.

Первый M40 gate source6b1f9bb4:8/9, один неверный test setup пытался создать duplicate job_id, уже запрещённый production SQLite API. Test исправлен на проверку фактического reservation_job_already_recorded/сохранность исходного lease. Защитная ambiguous ветка API не выдаётся за runtime-tested valid-registry сценарий; отказавший прогон сохраняется отдельно.

## Выявленная гонка очереди

После закрытия bounded worker внешний supervisor ещё выполняет recovery/release. Старый guard немедленно требовал recovery-event.json и ошибочно отказывал в этом промежутке. Пять сохранённых dependent jobs остановились до reserve/model. Новый observer читает фактический registry:closed+held остаётся pending, closed+released становится ready; optional not_created — отдельное состояние, подтверждённое registry и точной invocation. Текущий coordinator retry использует этот путь; существующие исходные failed attempts не изменены. Это исправляет конкретную resource-readiness постановку, не сертифицирует весь scheduler.
