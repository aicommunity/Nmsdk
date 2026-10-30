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

### Промежуточная runtime-сверка A2

Elder native A2 завершён с exit 0: четыре 2-kHz cases, затем восемь expanded
cases; aggregate XML проверяет точное множество 12 test IDs, без ошибок и
пропусков. Первая независимая версия reader
`148eef9d7c4d36fd84f62669159844d12d1e94f8` завершена: 47/47 tests, ноль
skips/errors/failures, проверены 16 настоящих candidate packages. Raw результаты
пока находятся в `/home/user/timelearner-refactor/readbacks/s08-threshold-candidate-normal-a2`
и `s08-threshold-candidate-audit-normal-a1`; публикация compact primary artifacts,
временные графики и приёмка подэтапа ещё не завершены.

Следующий reader `ebb6407fd9b161f0723fc00c8941b8dd7589c3f1` добавляет явное
calibration-only scoring и три проверки полного набора/перестановки строк/
запрета frozen evaluation для candidate. Его normal gate пока выполняется
(PID 971369). ASan native A2 на M40 прошёл 4/4 при 2 kHz и выполняет expanded
часть (PID 2809841); новый ASan reader ожидает его завершения (PID 2822958).
Эти PID — указатели для повторной проверки, не доказательства текущего liveness.

Старый ожидающий ASan reader a1 отменён до tests в пользу нового reader.
Его EXIT trap записал `0` при SIGTERM; это не PASS. Отдельный attempt-status
сохраняет `interrupted_before_tests`, отсутствие validation.json и неизвестный
OS exit code. Новый launcher явно обрабатывает TERM/INT и всё равно требует
терминальный native status, точное множество JUnit cases и полноценный data gate.
Не считать завершённый shell процесс, файл с нулём и научную приёмку одним статусом.

## Выбор и подтверждение: реализация data contract

`calibration.py` принимает явную grid specification, balanced target/foil design
для каждого reset policy, source package/model hashes и отдельный attempt/clock
context. Все пробы проверяет общий scorer. Отсутствующий кандидат, цензурированная
проба, другой source или изменённый dataset запрещают выбор. Порядок строк и
массивов не подменяет presentation_index; порядок thresholds является явным
tie-break. Scientific conditions digest отделён от calibration attempt ID.

На полном проверенном prefix grid выбирается реально измеренный кандидат без
target violations и FP. Иначе результат — NonSeparable на объявленной полной
сетке либо BudgetExhausted на её ограниченном prefix. Состояние после выбора
остаётся PendingConfirmation. Подтверждение повторно проверяет selection,
тот же immutable candidate и полный новый trial set с другим run ID. В пределах
одних часов новые пробы должны быть позже поиска; между разными clock scopes
абсолютные model times не сравниваются и требуется другой attempt.

Native execution/provenance и статистическая независимость не доказываются
именами ID или JSON: соответствующие flags остаются false. Production runner
ещё должен выполнить rebuild/import/probes/commit/rollback и связать receipts.
Положительный путь confirmation пока не принят реальным integration gate.

## Измеренный LTZone bracket: рабочее расширение

Вместо предложения порога по soma sum добавлен opt-in raw observation schema 2:
`recordThresholdPotential` сохраняет реальную `LTZone.Potential` после штатного
расчёта детей, её model path/class и явные model units (SI не подтверждены).
Schema 1 не дополняется выдуманными значениями. Изменение не добавляет Calculate
и не записывает настройки на каждом тике. Включение внешнего source у Potential
отвергается; nonfinite измерение не сохраняется как действительное.

`ProposeNativeThreshold` проверяет заранее объявленный полный набор и допускает
только nonspiking characterization. Нижняя граница учитывает весь foil window
и запрещённые target-outside ответы; верхняя — минимум target peaks в нужном
окне. Порог предлагается внутри измеренного bracket и явных bounds. Допустимый
endpoint не теряется при integer/double quantization. NoGap/NoRepresentable
не являются PhysicalInfeasible и не означают успешную калибровку. Предложенный
порог обязательно проверяется реальными spiking пробами и свежим импортом.

Новые fixture cases явно отделяют primary reset-per-trial pair от continuous
robustness pair до предъявлений. Foil сохраняет first ISI и увеличивает остальные
в восемь раз; это новый контролируемый dataset, не историческая восьмёрка.
Все primary/robustness/cancel/gap observations сохраняются. Каждый записанный
Potential сравнивается с независимым чтением настоящего компонента на каждом
native тике. При measured proposal выполняются отдельные search и confirmation
imports из одного source; затем восстанавливается original recognition state.
Fixture сама не заявляет Calibrated по наличию gap или spike.

Schema-2/proposal собраны на обоих workers; полная матрица пока не принята. Поддержка V2 optional modes,
публикация compact primary data и обязательные читаемые soma/input графики,
а также полный общий PostTune/calibration controller остаются открытыми.


## Проверка 2026-10-31: окно пробы при 20 кГц

Elder, producer root `d5709b0d818f5000f16bf30548bbc9664a82122e`,
PulseLib `7f177359e7664da3243ece9404e07508cb2dfdc2`:
оба NativeThresholdPotential случая при 2000 Гц прошли; оба при 20000 Гц
завершились ошибкой ожидания результата. Legacy-фазы после этого не запускались.
Это не полная приёмка. ASan-задание M40 проверяется отдельно.

В fixture обнаружен фиксированный предел 10000 тиков: для растянутого foil
при 20000 Гц он короче объявленного окна. Незавершённая проба затем закономерно
запрещает import следующей модели (`native_recognition_import_requires_idle_boundary`).
Исправление fixture вычисляет предел по duration × frequency с запасом двух
тиков и проверяет maximumSamples. Production executor и физика не изменены.
До повторной серверной проверки исправление считается неподтверждённым.

Design schema 2 заранее сохраняет все requests, criterion и bounds.
Для уже полученных design schema 1 необходим явно ограниченный fixture adapter;
недостающие поля нельзя выдавать за сохранённые до запуска.
