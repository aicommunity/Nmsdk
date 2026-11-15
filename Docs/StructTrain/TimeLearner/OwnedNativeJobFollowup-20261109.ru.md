# Убрать дублирование исходника supervisor при запуске native jobs

Статус: обязательная постановка этапов 9–10; реализация после завершения frozen corrected33. Текущие SDK, runtime, job, canonical и работающий supervisor не изменяются.

## Подтверждённый дефект

При подготовке corrected33 launcher содержал точные UTF-8/LF bytes supervisor SHA256 `bb602d60fbeebbbb6792afb853c2f64724641cc801cfff9d162c5b3286c3f3c9`, но отдельная assert-константа осталась от A4 (`013acaffaf21c77dab5001f5488928d192ecc7ad845abc3a344ae8999d622b9d`). Root обнаружил несогласованность до dispatch: launcher создал бы файл и завершился до Popen. Этот launcher не выполнялся. Узкое исправление заменило только константу; статическая проверка подтвердила равенство embedded bytes, отдельного source-файла и assert SHA256. Исправленный launcher SHA256 `a9a894bcaec89b9c28e305a12a818d0b396766624c34e27eb1bd6b6d2ab032ca` Root запустил один раз.

Предыдущие source-update подготовительные ошибки также сохранены отдельно: file resource отклонён directory-only reservation API до checkout; Git pack без root tree исправлен в donor-only стадии до SDK update. Они подтверждают необходимость адресной декларативной подготовки, но не являются отказами native тестов или физических моделей.

## Конкретный следующий код

1. Добавить поддерживаемый модуль `Scripts/StructTrain/TimeLearner/owned_native_job.py` и соответствующую команду существующего CLI. Переиспользовать форму декларативного request и контролируемого запуска из `owned_python_job`; не добавлять второй reservation registry или API управления процессами.
2. Перенести reviewed supervisor lifecycle в поддерживаемый Git-модуль. Запускать его как `python -B -m ...` с адресом request/canonical, без генерируемого Python-тела, `WORKER.write_text`, двух копий исходника и вручную дублируемых hash-констант. Request связывает exact source closure, actual module Gitblob/physical SHA256, raw canonical/job SHA256 и typed runtime limits. Content hash не называть цифровой подписью.
3. Сохранить ответственность `native_preparation` за schema2/repo-module и согласованность source inventory/cohort/argv, `native_acceptance_worker` за SDK configure/build/native gates, `contained_process` за kernel-owned units и `resource_reservations` за владение путями. Tool/preparer и SDK namespace остаются разными процессами; фактические imports фиксируются.
4. Перенести текущую матрицу lifetime-guards без ослабления: start intent записан до запуска; любая ошибка после start проходит общий finally; stdout разрыв не завершает supervisor; durable detached session с file-backed stdout/stderr и DEVNULL stdin. Физический worker/module сверяется до исполнения, а не по одному сериализованному self-hash.
5. Для nested leaves получить конечный набор `process/contained/request.json` из validated canonical runplan. При final closure проверять все известные intents, включая окно до `owned-unit.json`; adopt допустим только для доказанно завершившегося controller. Неразрешённые intent/JSON/binding/identity сохраняют held lease. Сначала сохранить исходный terminal/manager outcome, затем cleanup; закрытие не превращает failed/incomplete в completed.
6. Для publication сохранять точные request/token/owner PID+start/boot/uid/resources, runtime content identity и bindings/recovery; итоговое освобождение только после outer и всех известных дочерних групп. Имена executable не являются идентичностью процесса. Исторические pinned launchers остаются извлекаемыми из Git evidence, не копируются в активные Docs/Reports.

## Адресные проверки и приёмка

Проверки выполняются на серверах, локально допустимы только metadata/Git/AST/hash проверки. Production-путь должен подтверждать: обычное завершение; nonzero worker; отказ до start и после записанного intent; сбой записи STARTED; разрыв stdout; дочерний intent без binding; частичный JSON при живом outer с defer и final strict отказом; изменение bindings; cancellation/deadline; unknown closure с held lease. Использовать реальные owned units и текущие tested APIs, без убийства по имени или ручного release обходом registry.

Отдельные metadata-контроли проверяют, что request нельзя незаметно заменить после review, неправильный module/raw SHA/argv/cohort отвергается до запуска, и production-команда больше не содержит embedded source/самостоятельной assert-константы. Положительный адресный запуск обязан сохранить исходный outcome, actual IDs и полную closure; он не является новой научной матрицей.

Завершение: source/tests/docs и компактное Git evidence; merge commit в develop после приёмки. Удалить активные TEMP-based производители из pipeline; исторические bytes сохранить только в существующих архивных evidence/immutable commits. Frozen corrected33 используется как неизменённый baseline, повторять его целиком из-за orchestration refactor не требуется без нового поведенческого риска.
