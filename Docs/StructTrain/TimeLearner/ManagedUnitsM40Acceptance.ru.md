# Managed-unit registry schema3: M40 acceptance

Принят evidence-подэтап: source34394c3017d3641377d8ec886eca3a1cfc502b92,
M4061/61 actual kernel/SQLite tests,0 failures/errors/skips. Двенадцать новых
managed-unit cases и все49 legacy reservation/budget/contained/recovery checks.
Proof5fe182a0a6e561faddd19e661701c3b9c3881a68;
[независимая проверка](ManagedUnitsM40Verification.json):290 archive members,
279 исходных Python blobs, прежний API sourceADC и21 свежая unit closure.
Нейронные модели не рассчитывались. Отдельная ветка implementation пока
не включена в develop: нужны Elder и последующая production worker integration.

Воспроизведённый ранее fault теперь проверен с отказом: parent cgroup закрыта,
отдельная managed child жива, schema3 lease остаётся held. После явного закрытия
child recovery успешно проходит; событие содержит closure всего зарегистрированного
графа, а SQLite подтверждает released. [Исходный baseline](WorkerUnitGraphBaseline.ru.md)
сохраняется как дефект прежнего поведения.

Новый режим явный: новая schema3 capacity/demands с slots/RAM/disk/tasks,
реальный controller binding и его kernel caps; registration-before-submission,
binding-before-start.ack, консервативный суммарный бюджет controller+managed units.
Pending/unknown/live участник удерживает резерв. Старый API отказывает при schema3.
Ошибки до submission abort-ят intent; ambiguous submission остаётся reserved.
Активный общий registry M40 остался schema1. Никакой автоматической миграции
текущих jobs или runtime не было. Parent-only recovery metadata worker применён
только после завершённой61-case suite и свежей проверки21 конкретной test unit.

Сохранена первая попытка с двумя errors в прежних multiprocessing tests.
Причина — отсутствовавшая main guard в одноразовом launcher, повторно выполнявшем
подготовку при spawn-import. Исходный код, все61 test IDs и лимиты совпадают с
повтором; initial failed verdict и stderr остаются в previous-a1 artifacts.
После явной проверки21 unit closure его служебный reserve освобождён; результат
не переписан в PASS. Это исправление запуска CI, не ослабление требований.

На Elder доставлен тот же source через Git и поставлен отдельный61-case worker.
Он ждёт kernel closure normal304 и освобождения занятого slot, перед тестами
резервирует собственные ресурсы. Ни checkout, ни runtime работающего normal304
не обновляются. Elder PASS пока не присвоен.

Остаются: Elder acceptance, дополнительные interrupted/unknown launch cases,
подключение schema3 context к native_process_policy/pipeline/calibration/PostTune,
полный scheduler/resource policy и production normal/ASan gates. Рекомендуемость
нового backend, завершение этапа10 или всего исходного плана не присваиваются.
