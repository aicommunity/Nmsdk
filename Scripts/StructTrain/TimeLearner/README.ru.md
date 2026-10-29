# Поддерживаемый пакет TimeLearner

Запуск из корневого репозитория: `python -m Scripts.StructTrain.TimeLearner`.
Import не запускает эксперименты. Сейчас реализованы `inventory` и native
подмножество `analyze`; остальные команды runner/migration ещё не готовы.

```text
python -m Scripts.StructTrain.TimeLearner analyze record.json --format domain
python -m Scripts.StructTrain.TimeLearner analyze trial.json --format probe --trace trial.csv
python -m Scripts.StructTrain.TimeLearner analyze case_learned_state.json --format learned-solo
python -m Scripts.StructTrain.TimeLearner analyze case_stopped_state.json --format stopped-solo
python -m Scripts.StructTrain.TimeLearner analyze case_recognition_state.json --format recognition
```

`--output new.json` создаёт новый файл и отказывает при существующем пути.
Без этого параметра результат выводится в stdout. Ошибки дают structured
diagnostic в stderr и exit code 2. Code 0 означает завершённый анализ записи,
но не Exact, пригодность domain либо успешное распознавание: эти признаки
содержатся отдельно внутри `analysis`; `evaluation_verdict` остаётся null.
Ошибки содержимого имеют validity=invalid. Ошибка файловой операции, включая
существующий output, имеет execution=process_error / validity=unknown:
сбой записи не доказывает повреждение исходных данных.

Для исторической domain schema 1 требуется `--allow-legacy`; результат всегда
с `physics_verified=false`. Нельзя подставлять этот адаптер в другой формат.
Original primary CSV обязателен для отдельной probe; learned/stopped loaders
требуют связанные исходные пакеты по их versioned naming contract.
Recognition analysis требует исходный solo package с первичными пробами,
conversion record и declared frozen transport spec/observation/CSV schema 1.
Проверяет математику преобразования и неизменность остальных model properties;
unknown/incomplete transport не принимается. Spikes остаются unknown, а не 0;
это проверка переноса/состояния, не recognition selectivity verdict.

Это ещё не единый recognition scorer, не анализ исторического spiking CSV и
не полный production runner. Старые запускатели будут удалены после замены
их действующих функций и записи commit/blob в migration manifest.

`analyze <case_reconstruction.json> --format posttune-reconstruction` проверяет
фактический graph/heterogeneous C и полные parallel traces до/после native
реконструкции/rollback. Проверяются объявленная one-pass Dataset policy и
stimulus timestamps. Это evidence audit; native execution и научный PASS
команда не утверждает. Требуется полный комплект spec/observation/CSV файлов.

`analyze <case_transient.json> --format posttune-transient` проверяет закрытую
схему полного transient presentation, actual onsets/relative arrival windows,
сохранность training goal и raw presented ISI в каждом frame. Неполные окна,
NaN, неизвестные схемы и скрытая временная подмена запрещают valid result.
Native execution, training certificate и scientific PASS команда не утверждает.
