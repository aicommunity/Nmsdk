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

`condition.py` — рабочий общий codec content references/ConditionSpec, matrix,
analysis и attempt identities. Это ещё не preflight/runner и не замена Bin queue.
`runtime.py` создаёт manifest schema 2: deploy/resource/compiler paths исключены
из content identity, полная provenance сохраняется. Историческая schema 1
не пересчитывается. Source 670f2ff79 прошёл 18 Python tests на каждом worker
и реальный relocation/startup A2 binary с суффиксом `.rs2`: production snapshot
сохранил fingerprint. Это проверка integrity/loader scope; подключения к runner
и очередям пока нет. Артефакты и ограничения:
[ConditionIdentities.ru.md](../../../Docs/StructTrain/TimeLearner/ConditionIdentities.ru.md).

`config_document.py` добавляет lossless edits существующих text leaves с полным
путём и обязательным expected-old. Numeric names `<00>` сохраняются. По семь
tests на workers и реальный native readback на M40 ASan прошли; BOM/declaration
дефект исправлен в Rdk. Это ещё не effective component preflight:
[ConfigDocument.ru.md](../../../Docs/StructTrain/TimeLearner/ConfigDocument.ru.md).

### Frozen owner observation audit

`python -m Scripts.StructTrain.TimeLearner analyze CASE_owner_recognition_state.json --format recognition-owner`
проверяет conversion/source proof, actual before/after owner/reference hashes,
полное paired waveform и negative controls. Требуются source trial JSON/CSV
и schema-2 owner observation; schema-1 prototype без hash readbacks не получает
достроенных значений. Это validation evidence, без scientific verdict и spikes.

`analyze trial.json --format recognition-trial --model recognition_state.json`
проверяет полную frozen-пробу по primary кадрам, включая реальные stimulus/LT
истории событий, counts/timestamps, onset, покрытие окна и model hashes.
Молчание может быть валидным отрицательным наблюдением. Отмена и пропуск кадров
остаются `valid_observation=false`; успешное чтение согласованного файла не
означает успешного распознавания. `evaluation_verdict` остаётся null.
Проверка одной пробы не доказывает полноту матрицы; для неё требуется ожидаемое
множество run/trial IDs и sample/label/pattern hash из job spec. Размещение
target первым в файле не требуется. Подробности и область серверной проверки —
Docs/StructTrain/TimeLearner/FrozenRecognitionTrials.ru.md в корне.

### Метрики и крупные графические отчёты

`analyze evaluation.json.gz --format recognition-evaluation --model model.json.gz`
оценивает объявленное полное множество trials по labels/IDs/hash паттерна.
Критерий окна ответа задаётся явно; early target и любой foil spike во всём
окне не скрываются. Reset policies выводятся отдельно. Глобальный scientific
verdict требует общего runner/provenance и здесь остаётся null.

`python3 -m Scripts.StructTrain.TimeLearner report evaluation.json.gz --model model.json.gz --output NEW_DIRECTORY`
создаёт переносимый diagnostic index.html, primary данные, analysis.json,
manifest и контрольные суммы. На каждую trial/soma пару — отдельные PNG
1920×960, SVG/PDF overview и zoom-панели максимум по 100 native ticks.
Рендерить на workers; требуется matplotlib. Существующий каталог не заменяется.
Открывать полный PNG или vector-ссылку для анализа деталей. Schema-1 units
помечены model units / SI unverified; финальная визуальная матрица не закрыта.
Подробности: Docs/StructTrain/TimeLearner/VisualReportRenderer.ru.md.

### Git closure publication

`python3 -m Scripts.StructTrain.TimeLearner publish publication.json --root CHECKOUT --output NEW_RECEIPT.json`
публикует подготовленные commits всех сабмодулей, затем корня, без force и
переписывания истории. Проверяет committed gitlinks/.gitmodules, чистые exact
checkouts, локальные branch tips и фактические remote tips. Любая ошибка
останавливает дальнейшую публикацию; receipt отделён от научного verdict.
Spec/receipt хранить вне публикуемого checkout. Полный контракт и ограничения:
Docs/StructTrain/TimeLearner/GitClosurePublisher.ru.md. Это ещё не сквозной
experiment runner, очереди или доказательство полноты артефактов эксперимента.

### Процесс задания

`python3 -m Scripts.StructTrain.TimeLearner.process_runner --runtime-manifest runtime.json --working-directory RUNTIME --output NEW_ATTEMPT --wall-seconds 60 -- ARGUMENTS`
запускает объявленный executable, проверяет runtime, сохраняет PID/start/boot
identity, mappings, логи и результат. Timeout/cancel сигнализирует принадлежащему
заданию процессу через pidfd. Cancel — файл NEW_ATTEMPT/cancel.request.
`inspect_attempt` возвращает unknown при исчезновении процесса без результата;
не перезапускать job автоматически из-за обрыва наблюдения. Пока ownership
охватывает только launched executable, не fork/daemon tree. Контракт и
оставшиеся ограничения: Docs/StructTrain/TimeLearner/OwnedProcessSupervisor.ru.md.
