Принято05.11: оба workers проверили205 retrieval records через production CLI и отвергли restored-path negative без receipt. Сверены все члены трёх первичных архивов,279 source hashes каждого принятого worker, exact Bin19 deletions+7 prefix-only docs и сохранность прежних тел. M40 data95b31194164bc280a162dc6c723a771a5f7ce8d7; Elder data067101b825b0f4ae59b3d05b7c07bbfa21c32efe. Bin develop merge34387285116ee96bb09f99cb2ee95881fd3b9e0a имеет дерево проверенного featuref03e31eb. [Независимая проверка](PsiToolRetirementVerification.json). Первая Elder A1 отказала до migration checks из-за ошибочного режима открытия global ledger; состояние сохранено, A2 читает ledger read-only. Ни глобальная политика, ни runtime работающих заданий не менялись. Постановка ниже сохранена как история; pending формулировки относятся к моменту до этой приёмки. Общий этап9 и этапы1–12 остаются частичными.

# Миграция исторических инструментов PSI

Candidate удаляет19 shell/Python файлов `Bin/Configs/SpikeSamples/StructTrain/SelectivityPresynapticInhib/scripts`. Исходная точка Bin525aafbafe72679b40332eeb7704a922c3c72eee; каждый repository/full commit/path/blob/SHA256/size/last-change/retrieval записан в script_migration.json. Общий manifest205 records, complete=false. Wrappers и копии на старых местах не оставляются. Приёмка обоими workers ещё не выполнена; этап9 открыт.

## Прочитанное поведение и ограничения

Группа включает copy/inject/merge/patch Test, legacy scorer wrapper, auto-threshold/NeuronClassName/pattern-scale/GUI-cold patchers, три runners и шесть setup tools, включая k-sweep, compress/expand и GUI warm continuation. Внутренние зависимости удаляются вместе. Literal source review корневых Scripts/Tests/App не нашёл вызовов PSI scripts или уникальных prepare_gui_psi_train/tune_timing_params; в Bin девять совпадений находятся внутри удаляемой группы. Это не доказательство отсутствия динамических внешних пользователей.

run_experiments и run_autothr_experiments подавляют ошибки Console через `|| true`, затем делают частичный XML sync и считают match по имеющимся CSV rows. Полнота окна/набора проб, Train certificate и semantic identity Test этим не подтверждаются. run_time_compress ограничивает число попыток20, распознаёт Done по log text, расширяет SyncTolerance при stall/no-Done, подбирает лучшую модель по результатам Test той же матрицы и восстанавливает лишь выбранный набор XML/CSV. Его PASS/legacy accuracy не являются independent evaluation или доказательством исходных tolerances.

tune_timing_params прямо помечает порядок как Done-seeking и предпочитает более широкий SyncTolerance. patch_pattern_scale одновременно масштабирует ISI и tolerances, применяет floor1.5ms, оставляет непарсящиеся токены. Эти эвристики не переносятся в новый controller: математическая цель CapturedPerInput и объявленные допуски фиксируются явно. Выбор нового допуска — другое условие эксперимента, а не исправление прежней несходимости.

merge_train_weights переносит20 выбранных parent tags, не весь граф, storage physics, индивидуальные дочерние параметры и связи. inject/patch_model используют текстовые anchors и счётчик Links; patch_neuron_class меняет первое имя без effective readback. prepare_gui выполняет несколько последовательных записей и задаёт LTZThreshold100, фиксированные Rs/L/reference zeros; GUI-autothr setup, наоборот, продолжает сохранённую структуру без cold reset. Эти протоколы различаются и не должны смешиваться как cold repetitions. Общее изменение физики и PSI задаётся storage-образами штатной структуры, не повторяющимися исправляющими записями learner.

## Сохранение истории и данных

Все прочие Bin blobs сохранены. Семь README/REPORT получают только исторический prefix; прежние тела сохраняются побайтно. Два golden Interface.xml в scripts сохраняются как данные, не исполняемые исторические инструменты. Config/Model/Parameters/Project.ini, matrices, CSV, thresholds, morphology и показатели исходных кампаний не переписываются.

Удаление запускателей не опровергает исходные PSI наблюдения и августовские визуальные4/8–6/8. Исторический k-sweep следует читать с фактическим протоколом, изменениями tolerances и использованием same-matrix выбора; новые order/ITI/independent проверки требуют отдельных прогонов. Кампания и серияD автоматически не возобновляются.

## Проверка перед приёмкой

На каждом worker: production `history verify-migration` всех205 records, отсутствие старых путей; отдельный negative Git tree с возвращённым одним PSI script обязан дать migration_old_path_still_present и не создать положительный receipt. Exact Bin diff:19 deletions +7 prefix-only documentation edits; все остальные blobs, включая XML шаблоны, неизменны. Exact root diff:Bin gitlink, migration manifest, этот документ; Scripts/Tests/App/CMake/Libraries/Rdk прежние. Проверки metadata-only в отдельных bounded groups без изменения работающих SDK/global resource policies.

Текущий path-filter inventory Bin (`StructTrain`/`TimeLearner`, suffix py/sh/ps1/bat/cmd) содержит160 paths до и141 после этой группы; это явно ограниченный inventory, не полнота семантической миграции. Активные общие analyzers/legacy matrix runner и остальные пункты этапа9 остаются на review.
