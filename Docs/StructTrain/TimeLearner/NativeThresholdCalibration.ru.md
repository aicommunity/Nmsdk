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

На момент создания документа серверная сборка этих изменений не выполнена.
Новые пакеты кандидатов ещё не поддержаны Python data auditor/scorer и общим
pipeline. Полный CalibrationResult, выбор/подтверждение порога, controller loop,
production wiring и все PostTune modes остаются обязательным продолжением.
Исходные default tolerances, CapturedPerInput и Rdk bool-контракт не меняются.
