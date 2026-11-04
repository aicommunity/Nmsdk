Принято04.11: оба workers прошли166-record production history CLI, exact scope и restored-path negative. [Независимая проверка](PhaseAToolRetirementVerification.json). Bin develop merge `500764df8ae41604e03bdecdfd5531c7bc16f49b` имеет точно то же дерево, что проверенный d7feac78. Ниже сохранена исходная постановка candidate; общий этап9 остаётся частичным.

# Удаление исторических инструментов Phase A

Candidate удаляет8 campaign-local scripts из Bin SelectivityPhaseA/scripts: copy_config.sh,inject_analyzer.py,ltz_sweep_offline.py,merge_train_weights.py,patch_ltzone_integration.py,patch_test_model.py,run_all_experiments.sh,setup_all_experiments.sh. Все прочитаны целиком; wrappers и исходники на старых местах не оставляются. Точный архив — Bin99f58da9296a794374cef679bbb878cb62af979a. Root script_migration.json содержит commit/path/blob/SHA256/size/last-change/retrieval каждого файла; manifest166 records,complete=false.

## Почему это исторические инструменты

- Runner использует фиксированный workspace и executable; Test скрывает ошибки через || true, точность считает как match/8 без проверки полноты. Setup меняет кампанию на месте через sed без effective readback/числа совпадений.
- Copy/merge/injection подменяют подмножество parent XML и строковые ссылки/размеры. Они не подтверждают полный перенос heterogeneous storage physics, синапсов, связей и model identity. Полный native export/import/frozen pipeline развивается в корневом пакете; эта миграция не утверждает его научную эквивалентность всей Phase A.
- Offline sweep использует один spiking CSV, фиксированный знаменатель8 и max только ранее fired foils; ошибки чисел/пропуски/complete windows не проверяются. В самом августовском REPORT уже объяснено обратное влияние spike/threshold на LTZ peak. Confirm-прогоны остаются основой результатов.
- patch_ltzone_integration использует имя NPulseLTZone, уже отмеченное в историческом REPORT как незарегистрированное; реальный зарегистрированный интегратор называется NPLTZone. Это LTZone-обработка сигнала, отдельная от LTMembrane как физического канала. Удаление patch не отвечает на вопрос о причинном влиянии LTMembrane, которое требует отдельного сравнения моделей.

## Сохранение августа и зависимостей

Все конфиги, модели, первичные CSV, таблицы и оригинальное тело REPORT сохраняются. Исходные визуально подтверждённые4/8,5/8,6/8 остаются наблюдениями исходного протокола; порядок/ITI тогда не проверялись. Новые критерии не применяются задним числом. Полный исторический cold/replay/robustness matrix и все оставшиеся modes не считаются завершёнными этой операцией.

Literal поиск по Bin99f обнаружил только исторический EXP01 README и setup→patch внутри удаляемой группы. Root production package не содержит literal вызовов этих путей. Remaining campaign copies имеют собственные helpers; indirect/dynamic external callers не исключены. Старые документы с упоминанием имени инструмента маркируются как историческая процедура. Root source inventories остаются immutable snapshots.

## Приёмка

Ожидаются проверки production history verify-migration на обоих workers: все166 retrieval records, source-byte/blob identity и отсутствие старых путей; негативный Git tree с возвращённым старым path должен отвергаться. Exact Bin diff должен содержать8 deletions и3 documentation changes. Все остальные Bin blobs, native root/Pulse/Rdk/Test/physics trees должны совпадать с baseline. Ни модель, ни старый скрипт ради этой проверки не запускаются. Этот документ пока candidate; результаты проверок будут записаны отдельно.


## Результат приёмки

Elder evidence `9010e85327bd885678c0caa51be8ac999963b130`, M40 evidence `f6b955760ef5c99dda7852c887a669bd18a4bfc1`. На каждом worker проверены все166 records; actual CLI отверг Git tree с возвращённым copy_config.sh и не создал положительный receipt. Negative root/Bin packs доставлены через Git и независимо прочитаны: diff возвращает только этот файл и соответствующий gitlink. Все166 архивных содержимых и279 Python source blobs пересчитаны локально как metadata, без запуска тестовых моделей.

Проверены40 published checksums на worker и все архивы: A1 по11 members, A2 по5, A3 по16. A1 прошёл positive/scope, но его negative-fixture builder не поддержал отсутствующий каталог scripts. A2 отказал до проверок из-за повторного harness job ID. A3 исправляет только постановку: ID выводится из output.name, builder создаёт новый каталог. Production verifier, критерии и model code не менялись. Все неудачные primary и group closure/lease release сохранены; A2 lease не создавалась.

Manifest166 состоит из164 retired и2 moved; complete=false. Из исторического lower-bound каталога189 Bin candidates этим удалением убраны8, остаётся181 из того снимка. Это арифметика exact source diff, а не новый исчерпывающий inventory или доказательство полноты зависимостей. Remaining active analyzers/campaign scripts, indirect root probes и научная матрица остаются открытыми.
