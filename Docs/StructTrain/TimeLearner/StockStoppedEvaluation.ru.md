# Диагностические восемь паттернов на незавершённых stock-моделях

Новый workflow `stock-stopped-evaluation` относится к этапам3/5/9/11.
Он подготовлен для серверной проверки; факт численного выполнения пока не заявлен.
Исходник — четыре реальные остановленные модели из threshold pair A3,
evidence `e5fa71d745119af0d818059f497dd226f4c7c25d`. Не используется исходный
шаблон вместо обучавшейся структуры. Source study повторно проходит production
reader, все четыре исходных пакета и их первичные пробы сохраняются.

Команды из корня checkout:

```
python -m Scripts.StructTrain.TimeLearner stock-stopped-evaluation prepare SOURCE_STUDY --bin-repository BIN_GIT --output NEW_DIRECTORY
python -m Scripts.StructTrain.TimeLearner stock-stopped-evaluation run SOURCE_STUDY --bin-repository BIN_GIT --output NEW_DIRECTORY
python -m Scripts.StructTrain.TimeLearner stock-stopped-evaluation analyze COMPLETED_DIRECTORY --output NEW_ANALYSIS.json
```

`prepare` не запускает физическую модель. `run` требует нового каталога и
проверяет точный исходный runtime перед/после32 native probes. Используется
штатный public diagnostic-evaluate с полным import stopped package, identity
conversion, reset-per-trial и frozen semantic hash. Native scheduler/Reset
не заменяются Python-моделью. Исходный порог0.0117 или100 не подбирается и не
снижается; результат при100 может быть молчанием и сохраняется таким.

Каждая модель получает восемь сохранённых августовских паттернов из точного
Bin commit `1c1464e248f8744e858bd66df0be99e39969fd65` через phasea_matrix.
Окно каждой пробы2 s,2000 Hz, реальное сохранение всех сом и threshold potential.
Это32 пробы /80 trial-soma pairs: по четыре сомы Classic и одной Branch.
Данный reset-per-trial протокол не объявляется воспроизведением исторического
scheduler/ITI. На этом шаге порядок единственный; robustness остаётся отдельно.

Проверяются исходная и конечная физика без LT, полные source packages,
модель до/после evaluation, runtime, все jobs/IDs/observations и отсутствие
сертификата. Любая ошибка/неполное окно запрещает полный diagnostic verdict.
Даже при хороших diagnostic counts поля training_completed=false и
scientific_verdict=null сохраняются. Это не подтверждение сходимости,
независимая Test выборка или причинное сравнение наличия LT.

Шесть адресных server readers в tests/test_stock_stopped_evaluation.py:
пять работают с actual source study и historical Git data; шестой требует
фактического32-trial результата. Skip не засчитывается как успешная проверка.
После выполнения следует сформировать production temporal reports: все
паттерны/сомы, реальные входные импульсы, полный обзор и читаемый zoom.
Компактный Git хранит primary/models/metrics и выбранные изображения;
полный воспроизводимый кэш — M40 Data. Этот документ не закрывает весь этап11.

## Первые попытки и обязательная повторная проверка

A1 отказался до чтения нового кода из-за DNS GitHub на Elder. Коммит передан
нативным Git pack через существующий SSH; проверены exact commit и connectivity.
SDK/source/build/runtime при передаче не изменялись. A2 выполнил4/4 source
readers, затем public CLI отказался до native probes: prepare не создавал jobs.
Добавлено штатное создание каталога и новый actual-filesystem prepare reader.
Первоначальные exception/CLI receipts сохраняются; исправление ещё требует
нового серверного запуска. Численные результаты32 проб пока отсутствуют.

A3 с root6342a56d68718d3231b11dc0f6af7c3bc045cd8d запущен в отдельном
каталоге Elder после Git connectivity verification. Все5 preflight readers
прошли без failures/errors/skips, включая actual-filesystem prepare.
Owner1111148 подтверждён живым по PID/start_ticks. Public CLI запущен из
чужого cwd; завершённых run manifests на момент проверки ещё нет. Source/runtime
A5 не обновлялись. Точная квитанция и следующие gates —
[StockStoppedEvaluation.progress.json](StockStoppedEvaluation.progress.json).
Это запись очереди/процесса, а не положительный численный результат.

## Завершённая диагностика A3 и опубликованные первичные данные

Все32 пробы завершены. Preflight5/5 и final readers6/6 прошли без errors,
failures и skips. Evidence `c8381cfc3ecbf446ae1f59175c794ef547dcc93d` опубликован
и remote ref проверен. Независимо сверены все2684 members /28236672 xz bytes,
247 точных Python source hashes по root6342a56d, frozen models до/после и
отсутствие LT во всех четырёх графах. Все7 дочерних commits точно присутствуют
в опубликованных refs своих origin. Передача primary из Elder выполнена
нативным Git pack через SSH; из-за DNS на Elder push сделан из локального Git
после проверки данных. Ни SDK, ни модели при синхронизации не обновлялись.

Здесь TP/FP означают наличие любого спайка за полное окно от onset до2 s.
Это диагностический критерий активности; корректное время ответа после
последнего импульса этими counts не устанавливается.

| Порог | Classic TP/FP/FN/TN | Branch TP/FP/FN/TN |
|---|---|---|
|0.0117|1/7/0/0|1/7/0/0|
|100|0/0/1/7|0/0/1/7|

Низкопороговые остановленные модели отвечают на все паттерны. Высокий порог100
унаследован от Train и не калиброван для распознавания: молчание не является
успехом классификации. Это не результаты завершённого обучения, не отмена
августовских4/8–6/8 и не причинное сравнение LT. Сохраняются исходные состояния,
порог,32 полных окна и отсутствие сертификата; повторного Train не было.

Добавлена production-команда построения полного временного отчёта:

```
python -m Scripts.StructTrain.TimeLearner stock-stopped-evaluation report COMPLETED_DIRECTORY --output NEW_M40_CACHE_DIRECTORY
```

Она использует штатный pipeline renderer, исходные32 trials и все80
trial-soma pairs; полный обзор и100-tick zoom с реальными входными импульсами,
без уменьшения частоты. Верхний index явно указывает отсутствие LT,
незавершённый Train и отсутствие калибровки. Три addressed report readers
проверяют сохранность всех samples/IDs/сом, все файлы/масштаб и отсутствие
ложного утверждения training/manual acceptance. Сам render и эти три readers
ещё не выполнены. До просмотра изображений visual_acceptance_complete=false.
Полные PNG/SVG/PDF остаются кэшем Data; compact Git получает метаданные и
выбранные непосредственно просмотренные рисунки.

M40 visual-a1 owner3424054 с исходниками renderer rootddfe1f39d поставлен
в ожидание точного H21 owner3416749/start_ticks281000389. После его закрытия
отчёт читает published proofc8381cfc и строит полный кэш без повторных моделей.
Декларация:80 пар и3 report readers. Отдельный publisher использует native
Git parser и remote fetch каждого child commit; в Git передаются только
metadata.tar.xz, manifest и checksums. Полные PNG/SVG/PDF не публикуются.
Численная диагностика завершена; queue и ожидаемые проверки графиков ещё
не являются visual acceptance или новым научным результатом.

Уточнение04.11 после завершения очереди: visual-a1 закрыт с ошибкой
`KeyError: diagnostic_only`, Git proof `7e02f1126f23f1ed326b8bd16d1474d5c6284839`
явно имеет `acceptance_status=not_accepted`. Первичный manifest дочернего
diagnostic renderer правильно отмечал остановленный Train, но возвращаемый
словарь не передавал эту роль в `live_pipeline_reports` / общий stock report.
Поэтому завершённый частичный кэш первой модели не является отчётом по80 парам.

Исправление `b8b366dd8b4f1987e3a60c9183633b5129be8b00` возвращает diagnostic
role, training_completed и source_training_outcome из того же manifest.
Читатель дополнительно проверяет реальный вложенный summary в pipeline
manifest, а не только корректность отдельного файла. Модели, исходные пробы,
метрики и собственно рисование не менялись.

Запущен отдельный `s11-stock-stopped-phasea-visual-a2`, owner3633270, исходники
получены через Git. Перед повторным render все2684 исходных файла сравниваются
побайтно с proofc8381cfc; данные a1 переиспользуются только после этой проверки.
Повторного Train/Test нет. Полная генерация,3 report readers и визуальная
приёмка выбранных изображений остаются открытыми до фактического завершения.

Служебная проверка a2 остановлена адресно по подтверждённому owner до render:
обход XZ members через неупорядоченный set вызывал повторную распаковку при
обратных seek. Первичные файлы не менялись; ASan jobs не останавливались.
`interruption.json` a2 фиксирует эту причину. Новый a3 owner3634999 читает TAR
последовательно (`r|xz`); все2684 файла уже сравнены с Git побайтно, receipt
`source-primary-reverified.json` сохранён. Генерация полного кэша продолжается
в `readbacks/s11-stock-stopped-phasea-visual-a3/full-report-cache`; никаких
утверждений о её завершении или визуальной приёмке до итоговых проверок нет.


## Приёмка временного отчёта04.11: обнаруженное обрезание заголовка

A3 завершил полный render32 trials /80 trial-soma pairs и3/3 production
report readers без failures/errors/skips. Однако непосредственный просмотр
выбранных PNG обнаружил обрезание длинного trial_id на первой строке
заголовка. Поэтому численная/структурная проверка A3 не является визуальной
приёмкой. Неопубликованный candidate8751cb12 с20 рисунками не принят;
его `manual_review_complete=false` не заменяется задним числом.

Исправление `43b2fbf7bae735d028f73690eeb5f2c245fbe4ef` переносит полный
заголовок и проверяет его реальные границы через rendering backend в полосе
страницы. Размер1920×960, область кривой, временные окна, amplitudes, реальные
входы и маркировка LT spike events не меняются. Шрифт остаётся9–11 pt;
если полный заголовок не помещается читаемо, renderer выдаёт ошибку вместо
обрезанного рисунка. Контроль использует реальный длинный trial_id.

A4 supervisor3648538/start_ticks284037842 на M40 заново сверил2684 primary
files с Git proofc8381cfc побайтно, затем прошёл6/6 plotting checks. Полная
генерация нового кэша ещё идёт;3 report readers запускаются после её окончания.
Повторных вычислений моделей нет. Первое фактически полученное изображение
передано через native Git и просмотрено целиком: title/axes/legend читаемы,
входные импульсы наложены на soma potential, waveform не закрыт легендой.

Preview proof `7f6a37c0259125015cba9caf5386b23e08f19bc5` содержит только
этот рисунок и его привязку к source/data/cache. Это приёмка оформления одного
изображения, не всех80 пар, не всех паттернов и не завершения обучения.
[Просмотренный preview](../../../Reports/StructTrain/TimeLearner/s11-stock-stopped-title-preview-a4/preview.png).
Полный кэш: `/media/user/Data/TimeLearnerRefactor/readbacks/s11-stock-stopped-phasea-visual-a4/full-report-cache`.
Остальные selected figures, полные cache hashes и публикация metadata остаются
открытыми до завершения A4. Августовские результаты не пересматриваются.


## Завершённый A4: полный render и selected20 visual QA

A4 owner3648538 и selector3652241 закрыты успешно. Source43b2fbf7b прошёл
6 plotting controls и3 production report readers. Все2684 primary files
сравнены с Git до render; моделей повторно не рассчитывали. Полный кэш
содержит14728 файлов:4450 trial-soma views и30 series PNG, соответствующие
SVG/PDF, manifests и portable primary copies. В Git размещены metadata archive
1,023,884B и20 выбранных PNG, без копии всего кэша.

Proof `d262170b3c5665ecce3fd55c9e9277fcf204b7f3` независимо проверен:
40 metadata members,414 exact source hashes, все20 PNG, cache inventories,
вложенные manifests и source archiveSHA. Producer manual flags оставлены
false; отдельно [зафиксирован реальный просмотр20](StockStoppedTemporalSelectedVisualQA.json).
Просмотрен весь selected набор, включая все8 Classic-low soma1 overviews,
target/foil остальных трёх состояний, четыре peak zoom и две local-Y детали.
Ни manual QA всех остальных изображений, ни завершение Train не заявляются.

[Читаемый отчёт с рисунками](../../../Reports/StructTrain/TimeLearner/s11-stock-stopped-phasea-visual-a4/REPORT.ru.md)
содержит TP/FP/FN/TN, условия, шкалы, доказательства и команду воспроизведения.
У LT spike event речь о штатном LTZone; **LTMembrane в этих моделях нет**.
Малый local-Y хвост порядка1e-11 и отсутствие импульса внутри отдельного zoom
не интерпретируются как большой ответ или потеря исходных входных данных.
Это завершённая визуальная доставка диагностического наблюдения, не научный
PASS классификации, не полный контроль порядка/ITI и не завершение этапа11.
