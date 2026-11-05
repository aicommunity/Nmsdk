# Исторические инструменты FastResponse/FastSpan

Candidate удаляет 18 campaign-local tools: 6 из SelectivityFastResponse/scripts и 12 из SelectivityFastSpan/scripts. Bin исходная точка — `500764df8ae41604e03bdecdfd5531c7bc16f49b`; все commit/path/blob/SHA256/size/last-change/retrieval записаны в script_migration.json. Общий manifest содержит 184 records, complete=false. Wrappers и копии на прежних местах не сохраняются. Приёмка обоими workers ещё ожидается; этот документ не объявляет этап 9 завершённым.

## Результат чтения исходников

FastResponse: copy_config.sh, inject_analyzer.py, merge_train_weights.py, patch_test_model.py, run_grid.sh, setup_grid.sh. FastSpan: те же четыре copy/inject/merge/patch helpers, evaluate_selectivity_csv.py, patch_pattern_scale.py, patch_watch_pattern_legend.py, run_fastspan.sh, run_parallel.sh, setup_fastspan.sh, verify_element_params.py, verify_pattern_span.py.

Copy/inject/patch helpers в двух кампаниях побайтно одинаковы. FastSpan merge добавляет 14 parent tags, включая порог/калибровку и классы/defaults; это всё ещё частичный regex overlay, а не полный перенос структуры, неоднородной physics, синапсов, связей и storage identity. Его отсутствие ошибок не подтверждает Train → Test.

FastResponse runner подавляет ошибки Train/Test через `|| true`, использует фиксированный executable и выводит train_ok из первой строки Test. FastSpan корректнее обрабатывает exit status, но его selective gate предполагает target в строке 0 и acc>=4 при произвольной фактической длине CSV. Статические сверки L/D/C не заменяют model fingerprint, завершённость Train и полноту окон наблюдения. Legacy scorer wrapper также удаляется: новые active commands принадлежат корневому пакету, исторические схемы читаются его отдельными adapters.

Setup tools меняют текущие конфиги на месте; canonical scale tool одновременно переписывает 4-input/8-pattern matrix и эвристически меняет tolerances. Эти эвристики не переносятся автоматически в новый контроллер. Новые эксперименты должны явно задавать протокол, физический профиль и исходные допуски, затем проверять effective runtime model. Никакая новая кампания удалением не запускается.

verify_element_params проверяет текстовые counts и общую ожидаемую физику, а не реальные дочерние экземпляры/storage graph; для heterogeneous модели его предположение недостаточно. verify_pattern_span опирается на фиксированные четыре импульса, допускает skip без метаданных и не доказывает восемь полных проб или конечность всех чисел. GUI patch накладывает 0/1 markers с clipping на прежнюю ось дендрита; новый временной отчёт сохраняет все soma channels/реальные входные импульсы и читаемые zoom views отдельно. Сохранённые Interface.xml не изменяются этой миграцией.

## История и зависимости

Literal поиск по executable sources Bin не обнаружил внешних обращений вида SelectivityFastResponse/scripts или SelectivityFastSpan/scripts. Внутренние shell/Python dependencies удаляются целой группой. Отсутствие literal ссылок не является доказательством отсутствия динамических внешних пользователей. Ближайшие README/REPORT/JOURNAL явно помечаются как историческая процедура; FastResponse README больше не предлагает старые launchers как текущий способ запуска.

Все остальные Bin blobs сохраняются: конфиги, XML моделей/интерфейсов, CSV, matrix metadata, сводки, исходные измерения. REPORT и JOURNAL получают только исторический prefix, прежнее тело остаётся побайтно неизменным. Исторические результаты не пересчитываются новым критерием и не объявляются неработавшими. Как и августовские 4/8–6/8, они сохраняют свой протокол и уровень доказательности; order/ITI/independent evaluation требуют отдельных проверок.

## Проверки перед merge

Production `history verify-migration` на каждом worker должен проверить все 184 retrieval records и отсутствие старых путей. Отдельный негативный Git tree, возвращающий один старый script, должен быть отвергнут с migration_old_path_still_present и без положительного receipt. Exact Bin diff: 18 deletions и 4 documentation changes. Root diff: gitlink Bin, manifest и этот документ; Scripts/Tests/App/CMake/Libraries/Rdk остаются теми же Git objects.

Проверки metadata-only выполняются в отдельных bounded groups/registries, без запуска старых скриптов или моделей, без изменения рабочих SDK и глобальных resource limits. Только после проверки исходных bytes, полных результатов и Git closure разрешается merge Bin в develop, затем root. Из прежнего lower-bound набора 181 Bin tools после этой группы останется 163; это не новый исчерпывающий inventory. Общий этап 9, активные специализированные анализаторы и остальные пункты исходного плана остаются открытыми.
