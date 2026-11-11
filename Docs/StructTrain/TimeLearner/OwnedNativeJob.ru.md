# Штатный контроллер приёмочного native job

Модуль `Scripts.StructTrain.TimeLearner.owned_native_job` заменяет создававшиеся во временном каталоге supervisor/launcher с двойными копиями Python и независимыми hash-константами. Исполняется только модуль из закреплённого Git Tool root; сохранённый source snapshot является JSON-данными, а не запускаемой копией. Существующие `native_acceptance_worker`, `contained_process` и `Reservations` сохраняют владение вычислениями и ресурсами.

## Поддержанный первый контур

Команды `launch REQUEST`, `status CONTROLLER`, `recover CONTROLLER`. Никакая команда не возобновляет и не перезапускает job. Публичный request не позволяет задавать произвольную команду, модуль или дополнительные ограничения. Допускается только production native acceptance worker и его schema1 job / schema2 preparation.

Request — закрытый schema1 объект `timelearner_owned_native_job`: `kind`, `schema_version`, `job_id`, `worker_host`, `execution_root`, `tool_commit`, `job:{path,sha256}`, `preparation:{path,sha256}`. Все source/control bindings проверяются до создания controller. Worker native helper должен совпадать с проверенной Tool-версией байтами Git. Preflight не утверждает, что SDK-модули загружены в Tool-процесс: SDK namespace проверяется самим worker.

Первый выпуск использует существующий неменеджируемый schema1/2 registry. Schema3 с managed-unit graph явно отвергается, поскольку текущий SDK worker не регистрирует в нём дочерние leaf units. Этот отказ не меняет и не ослабляет schema3 recovery. Нового registry/overlapping controller lease нет. Единственная рабочая lease принадлежит native worker.

## Неизменяемые входы и fresh context

До подготовки canonical необходимо объявить будущий `BASE/readbacks/JOB-controller/inputs/job.json` в argv. Job.preparation объявляет соседний `inputs/preparation.json`. Внешние входы фиксируются в Git и копируются туда байт-в-байт после atomic fresh mkdir controller. JSON не переписывается, новый hash-цикл не создаётся. Идентичность inode/size/mtime/ctime и SHA копий проверяется до исполнения, в цикле и на завершении. Старые frozen A2/A3 задания с другим argv не поддержаны этим новым входом и продолжают воспроизводиться своим закреплённым старым кодом.

Все path/resource/capability/profile/source/prior-group проверки идут до launch-side effects. Atomic fresh context исключает повторное использование job identity. Launch failure сохраняется; повторный launch в этот каталог запрещён. Supervisor запускается detached с файловым журналом и DEVNULL stdin; потеря наблюдающего stdout не прерывает работу.

## Владение и завершение

Supervisor использует только конечные `contained/request.json` пути из canonical runplan. Даже intent без `owned-unit.json` учитывается; после доказанного закрытия его настоящего controller применяется существующий `adopt`, затем `stop` и kernel inspection. PID без start ticks, неизвестная идентичность, подмена binding, исчезновение ранее виденного request, повреждённый final JSON или ошибка сохранения доказательств оставляют lease held. Никакого поиска/завершения процессов по имени нет.

Все действия после start охвачены finally. Исходное состояние manager и terminal worker сохраняется до cleanup, поэтому успешный stop не становится доказательством успешного вычисления. Отдельно проверяются outer и все дочерние units. Lease освобождает только штатный `recover_closed_worker` после доказанного закрытия полного конечного графа. Recovery после смерти supervisor проверяет его точные PID/start/boot/uid и связь с contained request, исходные raw controls, durable child intents/bindings; неизвестная идентичность не считается умершей.

Возврат0 для public supervisor дополнительно требует настоящий terminal native worker: built=true, job/cohort checks=true, ровно объявленное число actual completed/passed cases, пустые failures/capture errors. Это приёмка инженерного контура, scientific verdict всегда null.

## Проверка перед активацией

Данный commit — исходный код до серверной приёмки. Локально выполнен только AST/Git обзор. Обязательны прежние19 metadata/profile тестов с реальным bounded TinyCMake fixture,2 новых path checks,10 closed-request/immutability metadata controls и9 real-kernel controls. Kernel controls используют только закрытый private fixture модуль, отдельные сохраняемые SQLite ledgers и явный consumed `TIMELEARNER_OWNED_NATIVE_TEST_OUTPUT`; C++/модель не запускаются. Проверяются actual zero/nonzero, whole deadline, cancel, nested child, unbound intent, partial final JSON/held lease, injected receipt failure и BrokenPipe. Fault injection явно помечена и не выдаётся за сбой ОС. Public request не может выбрать fixture.

Новый orchestration source проходит отдельный review и серверные гейты. Уже запущенный corrected37 A3 и его SDK/controls не изменяются.

Consumed kernel fixture: `TIMELEARNER_OWNED_NATIVE_TEST_OUTPUT` указывает на read-only каталог с неизменяемым `kernel-output.json` (kind=timelearner_owned_native_kernel_output/schema_version1/job_id/path). Запись допускается только в `BASE/readbacks/JOB/worker/kernel-cases`: проверяется точное соответствие job_id и реальному унаследованному TMPDIR того же outer job. Marker до/после неизменен; все case ledgers/closures/logs остаются в его WRITE subtree. Внешний read-only fixture root не используется для выходов.
