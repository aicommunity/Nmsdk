# Pending: единый managed pipeline coordinator

Добавлен candidate public CLI `pipeline run|continue|audit`. Он использует существующие production native workers и их строгие auditors, schema2 process policy/registered lease и frozen runtime. Физические компоненты рассчитывает native scheduler; Python не вызывает вложенный Calculate.

## Постановка

JSON kind=timelearner_managed_pipeline_job, schema_version=1, attempt_id и phases. Каждый phase содержит operation,job,wall_seconds. Допустимы Train→export→[posttune]→[calibrate]→evaluate. Train job — полный подписанный cold schema1 native job. У остальных jobs удалён sha256, а source_solo/source_recognition ровно null; coordinator подставляет полный фактический выход предыдущего этапа и подписывает новый job. Готовую историческую модель в эту позицию передать нельзя.

Для выполнения обязательны runtime manifest и process policy schema2 с действующим registered resource lease, покрывающим выходные phases. Координатор не создаёт lease сам и не освобождает чужой reserve. Runtime копируется в неизменяемую постановку; отдельные workers повторно проверяют реальные executable/loaded libraries. Scientific ConditionSpec не подменяется hash всей операционной постановки; соответствующая интеграция остаётся открытой.

Пример интерфейса:

```
python3 -m Scripts.StructTrain.TimeLearner pipeline run NEW_DIRECTORY --specification JOB.json --runtime-manifest RUNTIME.json --process-policy POLICY.json --stop-after train
python3 -m Scripts.StructTrain.TimeLearner pipeline continue SAME_DIRECTORY --specification JOB.json --runtime-manifest RUNTIME.json --process-policy POLICY.json
python3 -m Scripts.StructTrain.TimeLearner pipeline audit SAME_DIRECTORY
```

## Журнал и перенос состояния

journal.jsonl сохраняет created/started/finished/halted, порядковый номер, предыдущий hash и hash события. Записи, файлы постановки и каталоги fsync; одновременные writers исключены Linux flock. Неизвестное поле/порядок, оборванная запись либо изменённый manifest запрещают положительный аудит. До следующего этапа заново проверяется completed prefix и exact binding каждого job к фактическому predecessor model.

После каждого процесса проверяются production artifact audit, фактическое закрытие cgroup и привязка к одному runtime. Незавершённый Train сохраняется как halted; export/Test не запускаются. Статус completed процесса не подменяет completed_boundary. Неудачная/NonSeparable калибровка может вернуть исходное состояние; Test использует именно фактический возвращённый пакет. Классификационные counts рассчитывает общий scorer по полным declared trials.

--stop-after — остановка coordinator на завершённой границе, не Reset/ExternalStop физического learner. Continue проверяет прежние файлы, сохранённые manifests и свежую kernel closure; завершённые этапы не исполняются повторно. Для нового lease допустим новый policy при продолжении той же неизменной постановки. После полностью законченного pipeline continue выполняет только аудит. Это не controller checkpoint посреди пробы.

## Открытые пункты и приёмка

AST проверен локально, фактического runtime PASS пока нет. Восемь адресных integration tests используют реальные public CLI команды:4 cold Exact engineering N1 pipelines с остановкой после Train, продолжением, measured grid/fresh confirmation/frozen Test;4 реально stopped old declarations с запретом export/Test. Ожидаются20 отдельных native units, kernel closure, lease/unit IDs и отсутствие повторного Train. Исторические declarations дают только параметры, не модель или готовый verdict.

Это ещё не законченный scheduler. Открыты fault/cancel/reconciliation matrix, обработка torn journal с сохранением повреждённого оригинала, полная static semantic preflight всех последующих факторов до дорогого Train, ConditionSpec/JobSpec binding, queue dispatch, публикация и full-report cache wiring. Существует намеренный отказ cold-manager для schema2 live-finalization Train: у него уже есть конечный recognition-model, который нельзя молча потерять повторным export из solo; требуется отдельный маршрут этого состояния и реальные проверки. Старые public native commands/live controller не изменяют свою поддержку из-за этого нового маршрута.

Остальные profiles/modes, N0 positive outcomes, continuous stream, ASan и полная научная матрица не подтверждаются этими восемью тестами. Pipeline/job hash — операционная identity, не fingerprint научного условия. До серверной приёмки candidate не рекомендуется и не объединяется в develop; весь этап10 остаётся частичным.
