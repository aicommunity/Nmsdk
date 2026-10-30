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
for each declared finite threshold within model/protocol bounds and budget:
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
rejection NaN/Inf/nested/подменённого record и frozen graph hashes. Исходный
positive-only v1 также отклонял nonpositive; пересмотр этого ограничения см. ниже.
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

Для визуального анализа candidate-проб добавлен отдельный формат
`report evaluation.json --format threshold-candidate-evaluation --model candidate.json --output NEW_DIR`.
Он использует общий scorer калибровочных проб и штатные soma/input графики:
полные отсчёты, общий масштаб амплитуды, обзор и временные окна с разрешением
не менее восьми пикселей на native timestep. Первичные наблюдения сжимаются
без потерь. В manifest явно указано отсутствие утверждения о калибровке;
обычный recognition-evaluation по-прежнему не принимает candidate package.
Полные рисунки хранятся как worker cache, а не публикуются массово в Git.

## CLI анализа калибровки

`calibrate select SPEC --measurements SEARCH_SET --source-solo LEARNED_STATE --output NEW_RESULT`
выбирает кандидата по полному объявленному набору первичных проб.
`calibrate confirm SPEC --measurements SEARCH_SET --source-solo LEARNED_STATE --selection RESULT --confirmation FRESH_SET --output NEW_CONFIRMATION`
заново проверяет поиск и свежую подтверждающую матрицу. Эти команды анализируют
реальные измерения; сами они не запускают simulator и не подтверждают native import.
Отрицательный научный исход является корректным результатом анализа, а нарушение
схемы или неполные данные завершаются кодом 2. Существующие результаты не затираются.

Descriptor `timelearner_threshold_measurement_set`, schema 1, содержит массив
`measurements`: каждый элемент задаёт относительные пути `candidate`, `evaluation`
и объект `execution` (attempt_id, clock_id, stage, selection_sha256).
Все ссылки, включая compressed observations из evaluation spec, остаются внутри
переносимого каталога. Сохранённые scores не заменяют первичные наблюдения.
Для confirm descriptor содержит ровно одну свежую матрицу. Source learned state
по-прежнему проверяется вместе с исходными trial CSV, а не только по JSON digest.

## Scoped результаты 31.10

После duration-based исправления fixture полный normal gate на Elder прошёл
16/16 native cases: potential Classic/Branch N1 при 2/20 кГц, legacy candidate
Classic/Branch N0/N1 при 2/20 кГц и четыре owner/conversion regressions.
Полная ASan матрица пока выполняется; этот normal результат её не заменяет.

Независимые восемь proposal/CLI/link проверок reader
`6b03832182e281d6d1c7534a84ba7b300035ec75` прошли без skips/errors/failures.
Все четыре reset primary pair дали `confirmed` после отдельного native import
и нового предъявления. В частности, на 20 кГц предложены и подтверждены пороги
Classic 0.0031903129737191893 и Branch 0.00603317801091352 (model units).
Fixture затем восстанавливает исходный recognition state; native calibrated
commit/export этим ещё не реализован.

[Primary bundle](../../../Reports/StructTrain/TimeLearner/s08-threshold-potential-normal-a3/README.md)
содержит все 308 необходимых файлов (5.73 MB lossless archive), включая CSV
обучения и CLI descriptors. [Независимый Git roundtrip на M40](../../../Reports/StructTrain/TimeLearner/s08-threshold-primary-roundtrip-m40-a1/README.md)
проверил hashes всех членов архива и заново получил те же четыре selection и
четыре confirmation JSON из извлечённых данных. Simulator в этом roundtrip
не запускался. Это переносимость анализа, а не повтор native эксперимента.

Предложение порога использует nonspiking trace только для выбора кандидата.
Положительный исход определяется реальными spiking пробами выбранного порога,
учитывающими обратное влияние спайка на динамику; offline sweep одной трассы
не выдаётся за это подтверждение. Same-Matrix и independent frozen evaluation
остаются разными протоколами. Все данные этого контроля относятся к новой
двухпаттерновой fixture, а не к историческим августовским 4/8–6/8.

## Следующий рабочий подэтап: native решение по измеренным spikes

Root `ad975bbeb5df18555d94329d3ee95f321921c171`, PulseLib
`25cf6a5bfadc0ee72182cb924f1d0730cf6dc71b` добавляют общий validator закрытой
raw observation и `AssessNativeThresholdResponses`. Validator сверяет объявленную
request, точную native sample grid, полный интервал, finite значения и фактические
event arrays с покадровыми histories. Старое `valid=true` не скрывает вставленный
дополнительный отсчёт, потерянный frame или подменённый список spikes.

Общее определение response window вынесено отдельным механическим commit;
математическая цель не менялась. Native assessment вычисляет решения target/foil
по измеренным spikes, хранит все окна и отдельные reset policies. Он не вызывает
Calculate/Reset/Build, не меняет параметры и не присваивает calibrated=true.
Сохранение окончательного calibrated model и полный controller transaction
остаются следующими незакрытыми операциями.

Этот новый Core прошёл на Elder полную матрицу 16/16 native и 35/35 independent
Python tests; [первичные данные и метаданные](../../../Reports/StructTrain/TimeLearner/s08-threshold-assessment-normal-a1/README.md)
содержат все 64 native assessments. ASan остаётся отдельной незакрытой проверкой.
Прежние 16/29/8 результаты относятся
к Core 7f17735, а не автоматически к новому Core. Отдельный Python adapter
сопоставляет каждую native assessment с общим `score_threshold_candidate`,
включая primary и полные матрицы. Сам raw observation auditor версии 2 теперь
также проверяет native grid и различимость dt на текущем absolute clock.

CLI независимой проверки:

```text
python3 -m Scripts.StructTrain.TimeLearner analyze ASSESSMENT.json --format native-calibration-assessment --evaluation EVALUATION.json --model CANDIDATE.json --source-solo CASE_learned_state.json
```

Expected evaluation spec и source CSV обязательны. Согласованность расчётов
не выдаётся за подтверждение исполнения simulator, калибровку или training Exact.

## Пересмотр диапазона порога и проверка роли LT-зоны

CreateClassSamples (`NPulseLibrary.cpp`) регистрирует штатные IaF/Cable LT images
с Threshold=-0.055 и ThresholdOff=-0.07. Поэтому ограничение threshold>0 в новом
калибраторе не является общим физическим контрактом. Рабочий
`explicit-native-threshold-v2` принимает конечные signed значения, а
`nonspiking-native-ltz-bracket-v2` — конечные signed bounds. Старые v1 records
читаются с прежней областью допустимости. Структура JSON schema 1 сохраняется;
семантическая версия алгоритма явно записана в record. Baseline диапазон 1e-6..1
не расширяется автоматически при повторе старых экспериментов.

Наличие Threshold не означает, что он управляет spikes: frequency-encoding
NPSimple и continuous LT-зоны требуют другой постановки. Новый preflight helper
проверяет фактическую C++ реализацию (stock Threshold и leaky NPulseLTZone),
а не строковое имя образа. В частности, stock `NPulseLTZoneIzhikevich` является
образом NPulseLTZoneThreshold; отдельный одноимённый C++ класс — другая реализация.
Unknown overrides не получают выдуманный threshold operand; требуется адаптер.
Ordinary frozen schema-1 observation и чтение legacy v1 packages сохраняются.

Server gate `s08-threshold-contract-normal-a2` на Elder завершён: 6/6 native
и 6/6 independent Python checks, без failures/errors/skips. Проверенный root
`0afbf97c4ba9df4591eebe9a41fb916e02d1903e`, PulseLib
`479084f4c35d61f60ef9b37eb0da246bc8dec87a`. Изолированный IaF LT-zone control
подтверждает signed threshold и реальный spike через штатный scheduler;
он не подтверждает структурное обучение всей IaF модели и не содержит фиктивной
сомы. Дополнительно проверены 8 zero/negative roundtrips, 4 legacy-v1 roundtrips
и 2 signed-bound proposals на реальных frames Classic/Branch при 2000 Гц.
Первая normal попытка была неуспешной из-за dangling QJsonValueRef и ошибочного
storage-имени генератора; обе причины исправлены в указанном снимке.
ASan исправленного снимка поставлен после завершения отдельного задания
предыдущего снимка; активные source/build/runtime не обновляются.
[Переносимый пакет normal gate](../../../Reports/StructTrain/TimeLearner/s08-threshold-contract-normal-a2/README.md)
содержит модели, первичные данные, manifests и диагностику обеих попыток.
Полная повторная матрица 16 native / 35 independent checks исправленного снимка
выполняется отдельно и не подменяется ограниченным 6/6 gate.
# Повторное native чтение первичных данных калибровки

Добавлены `DecodeNativeRecognitionObservation` и strict-text
`ParseNativeRecognitionObservation`. Они принимают отдельно объявленную request,
проверяют все сохранённые поля обратным кодированием и повторно применяют общий
validator к реальным отсчётам и событиям. Duration не выводится из разности
абсолютных timestamps. Schema 1/2 сохраняются; дополнительные claims, boolean
вместо числа, повреждённые массивы, censored observations и дубли ключей текстового
JSON не допускаются в proof path.

В native fixtures добавлены roundtrip каждого реального наблюдения и сравнение
полного assessment после чтения, а также отрицательные контроли повреждения.
Новый code snapshot требует отдельного server gate; уже опубликованные gates
предыдущего снимка не являются его проверкой. Calibrated state commit/export
и полная транзакция остаются незавершёнными.
