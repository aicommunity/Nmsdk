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
