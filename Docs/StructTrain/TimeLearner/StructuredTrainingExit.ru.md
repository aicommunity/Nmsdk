# Аудит структурированного остановленного Train

Реальный Console на root507c8a6c4 вернул exit2, model_tick_budget_exhausted,
1 tick и полноценный diagnostic stopped package. Для training job schema1
native_pipeline_worker не вызывал audit_execution: _structured_live_exit
принимал только job schema2. Такой run manifest оставался unverified_execution
с analysis:null, хотя собственные первичные данные были доступны и согласованы.
Это воспроизведение пути анализа, не ошибка динамики/классификации.

Новый producer записывает pipeline run manifest schema2. При native Train
schema1 либо schema2 и exit2 выполняется строгий audit_execution: подписи,
job/model/packet bindings, actual owned loaded runtime и отсутствие completed
claim при ненулевом exit обязательны. Execution остаётся process_error,
completed_boundary:false и evaluation_verdict:null. valid означает согласованность
данных, а не завершённое обучение. Другие exit codes, timeout, loader errors и
отказы preflight не превращаются в структурированный Train.

Reader сохраняет исторический контракт run manifest schema1: старые schema1
Train с analysis:null не переинтерпретируются как новые valid runs. Native job,
model package, ControllerVersion и научные критерии не меняются. Неизвестные
manifest версии отклоняются. Schema2 является новой явной версией политики
аудита, а не переименованием старых исторических результатов.

Команда preflight-regression SPEC.json --output NEW_DIR исполняет maintained
root module. SPEC schema1 kind timelearner_public_preflight_regression содержит
поля template_corpus, source_root, executable, app_ini, cmake_cache,
loader_environment (QT_QPA_PLATFORM/ASAN_OPTIONS), maximum_wall_seconds.
Относительные input paths разрешаются относительно SPEC, не cwd. Сначала
проверяются все declarations и ожидаемый набор14+6+2; runtime environment
устанавливается ДО snapshot и восстанавливается после операции. Historical
шаблоны используются только как inputs. Все процессы, graphs, initial states,
stop packages и runtime receipts создаются заново production-путём.

Покрытие:14 positive preflights,4 native configuration rejections,2 descriptor
rejections,2 actual one-tick schema1 Train controls; scope default negative
wall limits. Не заявляется публичное применение положительного wall override,
полное физическое обучение или научный результат. Серверная приёмка pending.
Ранние ad-hoc setup failures сохраняются отдельно, новые campaign Python
launchers не создаются: CLI получает декларативный SPEC.


## Серверная приёмка

Driver `5325bbd0938c453d988b0ac71b3263c24683c401`, immutable C++ runtime root
`507c8a6c4da2b795d4dca3caf7b43806c8bf6835` (Pulse151a388, Rdkeda206b6).
На обоих workers14 positive preflights,6 expected rejections и2 schema1
one-tick Train controls. По28/28 reader/preparation/compatibility tests,
0 failures/errors/skips. Основные primary:
normal `9eeb7ba1cea3eedd1cefdbdf7c213e469d230107` (1162 members,344648 B),
ASan `b4fa92323ec4e9642a929fc913e9746cd0dcfd5c` (883 members,267376 B).
Содержат также завершённые integrated74 иMath6, прежние setup failures и
actual loaded-file snapshots; ASan библиотека присутствует в обоих C++
процессах M40. Source context before/after совпал до следующего checkout.

Дополнительно self-contained compatibility inputs:
normal `295012f7dd36d0e0a861ecacdee5e7a4ca1ea9e5` (35 members,56236 B),
M40 `89aaefc1d10831624a90ab6262e257385f20ae01` (35 members,60320 B).
Сохранены exact18 template job files, corpus metadata и реальный legacy Train
с manifest schema1. Его interpretation остаётся unverified; новое runtime/
physics assurance ему не приписывается. Все bundle/archive/member hashes
проверены локально. Для повторного анализа не требуется старый абсолютный
путь на сервере: unpack primary и compatibility archives, передать локальные
пути в TIMELEARNER_NATIVE_PREFLIGHT_DIR / TIMELEARNER_STRUCTURED_EXIT_DIR /
TIMELEARNER_LEGACY_SCHEMA1_TRAIN_DIR и запустить три test modules.

Это приёмка Python пути анализа и maintained regression CLI, а не всех
stages9/10. Новые numerical experiments, queue leases/recovery, все modes,
полная source-impact review и scientific matrix остаются открытыми.
Visual acceptance integrated74 не выводится из этих records; полные soma
reports продолжаются в соответствующем native подэтапе. Preflight не
измеряет response; one-tick controls не являются полным Test-паттерном.
