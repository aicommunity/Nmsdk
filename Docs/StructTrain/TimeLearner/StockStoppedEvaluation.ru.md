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
