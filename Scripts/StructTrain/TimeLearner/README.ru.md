# Поддерживаемый пакет TimeLearner

Запуск из корневого репозитория: `python -m Scripts.StructTrain.TimeLearner`.
Import не запускает эксперименты. Сейчас реализованы `inventory` и native
подмножество `analyze`; остальные команды runner/migration ещё не готовы.

```text
python -m Scripts.StructTrain.TimeLearner analyze record.json --format domain
python -m Scripts.StructTrain.TimeLearner analyze trial.json --format probe --trace trial.csv
python -m Scripts.StructTrain.TimeLearner analyze case_learned_state.json --format learned-solo
python -m Scripts.StructTrain.TimeLearner analyze case_stopped_state.json --format stopped-solo
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

Это ещё не единый recognition scorer, не анализ исторического spiking CSV и
не полный production runner. Старые запускатели будут удалены после замены
их действующих функций и записи commit/blob в migration manifest.
