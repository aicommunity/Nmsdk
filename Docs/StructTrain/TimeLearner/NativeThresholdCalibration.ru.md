# Native-калибровка порога: рабочий контур

Ветка `codex/timelearner-threshold-calibration`. Это незавершённая реализация
этапа 8, не разрешение optional modes для ControllerVersion=2.

## Физический кандидат

`CreateNativeThresholdCandidate` начинает с immutable recognition package,
повторно проверяет его conversion и native import. Разрешено единственное
изменение: фактический Threshold cached LTZone. Storage-образы не меняются;
морфология, индивидуальные Rs/C, связи, dataset и исходный solo proof сохранены.
Вложенный candidate как source запрещён: каждый порог выводится из одного
исходного recognition state, без повторного scaling.

Кандидат имеет отдельный kind `timelearner_recognition_threshold_candidate`.
Его `candidate_record` содержит source package/model hashes, LTZone path,
прежний и новый порог и `calibrated=false`. Новый graph hash не получает
исходный solo certificate как собственное доказательство. Архив хранит
фиксированный фактический порог с protocol `threshold-candidate-not-calibrated`.
Импорт заново выводит ожидаемый граф из source и сравнивает metadata/identity,
затем использует штатный native archive import. Re-sign повреждённого record
не делает его допустимым. Build/Init/Reset и scheduler остаются штатными.

Кандидат устанавливается отдельным native import на границе полной пробы.
Внутри recognition trial он frozen: прямая live-подмена порога запрещена.
Создание/импорт не исполняют Calculate и не продвигают model time.

## Обязательный следующий алгоритм

```text
freeze source recognition state and calibration data/design
for each declared finite positive threshold within bounds/budget:
    derive candidate from the same immutable source
    native import, initialization and declared reset policy
    execute every expected full target/foil trial through native scheduler
    reject missing, invalid, censored or mismatched observations
    score actual spikes using the declared label/ID based criterion
select using measured FN, FP, timing residuals and declared tie-breaking
reconstruct selected candidate independently from source
run the full confirming matrix at that actual threshold
publish CalibrationResult bound to candidate, data/design and observations
freeze resulting model/threshold before independent evaluation
```

Нельзя выбирать порог offline sweep одного spiking waveform: LTZone spike
изменяет динамику. Отсутствие разделимого кандидата даёт NonSeparable,
а исчерпание бюджета/неполная матрица — отдельный unresolved/invalid результат.
Silent threshold с target miss не превращается в successful detection.

Historical Same-Matrix и Frozen Independent — разные маркированные протоколы.
Их данные и final confirmation не смешиваются. PostTune mode candidates должны
использовать ту же границу export/import/probe, а commit/rollback — сохранять
полный граф и owner/controller provenance. Это ещё не реализовано данным API.

## Проверки и текущий статус

Добавлены восемь native cases: Classic/Branch × N0/N1 × 2000/20000 Гц.
Каждый получает настоящее completed solo state, делает identity conversion,
строит low/high threshold candidates, выполняет native owner import и штатные
Build/Init/Reset, полные target/foil пробы и cancel/gap controls. Проверяются
неизменность source, отсутствие Calculate при создании, повторяемость package,
rejection NaN/Inf/nonpositive/nested/подменённого record и frozen graph hashes.
Для low threshold при 2000 Гц требуется реальный spike в контрольных пробах.

Первоначальная версия root `72b967641ac8aeb89b0b7821adc455597917bbaf` /
PulseLib `b07bda1ec1273d6971df8480cc824928096edbb2` собрана на обоих workers.
Elder A1 завершён: четыре regression cases прошли, восемь новых cases выявили
`threshold_candidate_missing_ltzone`. Ошибка нового API: семантический путь
`$.LTZone` передавался напрямую в поиск относительного имени компонента.
M40 A1 намеренно остановлен SIGTERM после подтверждения той же ошибки; его
signal stack не объявляется ASan finding или полной приёмкой матрицы.

Исправление PulseLib `fbc1b4630f486a94ea3c5172bcc7dd2aaa3baeff` удаляет
семантический префикс только при поиске, сохраняя полный путь в provenance.
Root `ff987acea813c1e1055d6ff4767d7ac5c0dde23e` запущен на обоих workers:
сначала четыре 2-kHz cases, затем четыре 20-kHz и четыре regressions, с разными
XML и runtime manifests. На 2-kHz части оба workers прошли 4/4; полной приёмки
и merge пока нет. Старые binary/runtime директории не перезаписываются.

Python `threshold_candidate_evidence` независимо выводит единственное изменение
в semantic graph, сравнивает storage images, metadata и весь native XML через
штатный lossless Rdk dialect adapter. С optional primary source case отдельно
проверяются conversion и исходный solo proof. Само совпадение hash не подменяет
эти проверки. Новый CLI требует источник первичных данных:

```text
python -m Scripts.StructTrain.TimeLearner analyze candidate.json --format threshold-candidate --source-solo source_learned_state.json
python -m Scripts.StructTrain.TimeLearner analyze trial.json --format recognition-trial --model candidate.json
```

`score_threshold_candidate` использует общий label/ID/window scorer с явным
признаком calibration probe. `score_recognition_evaluation` отклоняет такой
неподтверждённый candidate. Подбор/подтверждение из успешного подсчёта spikes не
выводятся. Адресный ранний аудит двух Classic 2-kHz source/candidate pairs прошёл
по настоящим source CSV и полным frozen observations; общий regression/data gate
ожидает терминальных native результатов и всех 16 пакетов.

Полный CalibrationResult, выбор/подтверждение порога, controller loop,
production wiring и все PostTune modes остаются обязательным продолжением.
Исходные default tolerances, CapturedPerInput и Rdk bool-контракт не меняются.
