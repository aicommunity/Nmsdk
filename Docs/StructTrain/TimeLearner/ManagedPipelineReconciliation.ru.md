# Pending: сверка завершённой native-фазы после сбоя coordinator

Добавлена отдельная команда `pipeline reconcile DIRECTORY`. Она берёт тот же exclusive Linux lock, повторяет аудит всего законченного prefix, требует ровно одну started-фазу, проверяет подготовленный job и полный production run manifest, immutable runtime/model bindings и фактическую kernel closure именно её записанной unit invocation. Физические компоненты не рассчитываются повторно; новых процессов модели нет.

После проверки записывается hash-linked reconciled_finished либо reconciled_halted с manifest SHA и свежим kernel readback. Native Train без completed certificate остаётся halted и не получает export/Test. Portable audit повторно проверяет manifest и соответствие closure binding сохранённому owned-unit; он не выдаёт произвольный сохранённый kernel record за свежее наблюдение.

Команда не освобождает lease и не меняет registry, не продолжает пробу посреди динамики, не дописывает отсутствующий manifest и не обрезает torn journal. Для resumed execution оператор/runner должен сначала урегулировать прежние operational leases и получить действующий reserve для следующей фазы. Сбой до полного phase manifest, worker reboot, active unit/cancel, torn-journal recovery и общий scheduler fault matrix остаются открытыми задачами исходного плана.

Подготовлены7 production-path checks на настоящем completed coordinator corpus, выполняемые только на исходном worker:утраченная последняя journal запись, stopped Train, missing manifest, изменённый native model, torn journal, повтор reconcile и public CLI. Используются новые временные копии законченных artifacts; исходные primary не меняются, готовая модель не подставляется вместо Train. Новых native запусков в этих metadata/recovery checks нет.

AST проверен локально; server runtime gate ещё не выполнен. Текущие coordinator8 и M40 rendering jobs закреплены на прежнем source2cc и этот новый commit не подхватывают. Это расширение pending coordinator, не принятие этапа10 и не scientific PASS.

При работе с восстановленной копией проверяется исходный coordinator PID/start_ticks: чужой ещё живой controller не допускает adoption той же попытки в другом каталоге. В исходном каталоге writers сериализует общий file lock. Проверка active-controller/duplicate-run сценария на реальных управляемых процессах остаётся отдельной обязательной частью fault matrix.
