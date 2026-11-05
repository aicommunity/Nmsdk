Принято06.11: оба workers прошли production migration215 и restored-path negative без receipt; exact Bin10 deletions+7 prefix-only docs, все прочие blobs неизменны. Проверены все17 primary members и281 source hashes каждого worker. M40 data `d8d9178e33d471ce8888e5cf2e1ac9995a94b978`, Elder data `b85b102140d8217c7926ebe9d15449cc9227f6a9`. Bin merge `f12f09ae1f7fc0a9af1d99be86d3a4002a3cf4aa` опубликован; его tree равен проверенному639bc3ef. [Независимая сверка](AsymRmDriverRetirementVerification.json). Постановка ниже сохранена как история; слова «пока не выполнена» относятся к состоянию до приёмки. Общий этап9 остаётся частичным.

# Миграция оставшихся shell-драйверов AsymRm

Подготовлен отдельный подэтап9: удаление десяти исторических shell-файлов
`Bin/Configs/SpikeSamples/StructTrain/SelectivityAsymRm/scripts` без wrappers.
Это продолжение прежней миграции17 wave entrypoints, а не её повторная приёмка.
Исходная точка Bin — `34387285116ee96bb09f99cb2ee95881fd3b9e0a`.
Все215 записей общего `script_migration.json` содержат repository, полный
archive commit, старый путь, blob SHA1, content SHA256, размер, last-change
commit и точную команду извлечения. Manifest остаётся `complete=false`.

## Поведение и решение

| Файлы | Прочитанное поведение и причина удаления |
|---|---|
| copy_config.sh, clone_asymrm_exp.sh | Копирование шаблонов через rsync, regex Project.ini, изменение TSV; Train→Test передаёт выбранные parent tags и вставляет analyzer. Это не полный native model export/import. |
| setup_asymrm.sh, reset_asymrm_cold.sh | Создание18 старых cases либо изменение существующих Train/Test на месте: L/Rs/references, классы, C/кинетика/Rm, timestep. Cold reset дополнительно перемещает/копирует выбранные StatisticLog snapshots. Не переносить эти процедуры в learner или обход storage. |
| run_asymrm.sh | Общий adaptive length/amplitude driver с повторными warm запусками, L-reference guards и повторным XML physics patch. По умолчанию проверяет Done/calibration перед Test, но ALLOW_PARTIAL_TRAIN=1 снимает отказ. Частичный overlay не подтверждает semantic identity Train/Test, а агрегация имеющихся CSV не подтверждает полное наблюдение. |
| run_parallel.sh | Прямой запуск из изменяемых каталогов, общий default executable, PID-array concurrency. Exit codes учитываются, но immutable runtime/provenance и полная изоляция descendants отсутствуют. |
| pilot_status.sh | Legacy Done/calibration/L-reference summary для перехода к scale; это не сертификат обучения или независимой классификации. |
| export_preinh_audit.sh | Собирает glob preinh_audit_*.json и выводит CORRUPT только при определённом сочетании полей. Пустой список получает OK; missing last_abs_dt/dendrite имеют permissive defaults. Такой итог не переносится в production validity gate. Старые отчётные значения сохраняются. |
| inventory_statisticlog.sh, prune_statisticlog.sh | Исторические protected timestamps и список каталогов/размеров. Prune удаляет manifest-relative каталоги без canonical containment/content-duplicate proof. Удаление этих двух скриптов не запускает их и не удаляет никакие логи. |

Остающиеся29 Python-файлов этого каталога, включая специализированные
физические анализаторы, сохраняются до отдельного semantic review/переноса.
Нет обещания автоматической эквивалентности старого shell workflow новому CLI.
Общие новые функции выполняет корневой пакет: declared native construction,
полный экспорт модели, измеренная калибровка, frozen evaluation и строгий scorer.

## Сохранность и приёмка

Семь связанных Markdown-документов получают только исторический prefix;
исходные тела должны сохраняться побайтно. Все прочие Bin blobs, включая
конфиги, модели, CSV, JSON, TSV и остальные отчёты, неизменны.
Ни старые эксперименты, ни серияD не возобновляются.

Перед merge в develop необходимы на обоих workers: production
`history verify-migration` всех215 записей, negative Git tree с восстановленным
одним старым путём и отказом без положительного receipt, exact Bin diff
10 deletions+7 prefix-only docs, exact root diff Bin gitlink+manifest+этот
документ, неизменность Scripts/Tests/App/CMake/Libraries/Rdk.
Проверки metadata-only, в отдельных bounded groups, без изменения работающих
исходников/runtime и global resource policy. Приёмка пока не выполнена.

Ограниченный Bin inventory по путям StructTrain/TimeLearner и suffix
py/sh/ps1/bat/cmd уменьшается с141 до131. Это не доказательство полноты
всех Git trees и не закрытие этапа9; этапы1–12 остаются частичными.
