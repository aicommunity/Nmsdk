# Branch N1: целевой ответ сопровождается пятью ложными срабатываниями

На фактическом остановленном состоянии нового coupled-search обучения получен целевой спайк и ответы на **5 из 7 отвлекающих паттернов**. При одном заранее выбранном пороге результат — **TP1 / FP5 / FN0 / TN2**, то есть 3/8 по объявленному критерию полного окна. Целевой спайк возникает в 0.262 с, на 228 мс раньше последнего входного импульса. Это отрицательный результат проверки разделимости данного состояния: надёжное распознавание завершённой последовательности не подтверждено.

## Условия и границы сравнения

Branch N4, N1, 2000 Гц, исходный stock storage-профиль **без LTMembrane**. Обучение использовало CapturedPerInput и опорный вход N−1. Терминальный вектор путей: L=[28,27,27,1], Rs=[86M,21.232304307596M,21.232304307596M,86M], Ns=1. Применён штатный диагностический перенос фактического terminal state в recognition-граф; сведения о преобразовании и effective readback сохранены в manifests. Шаблонная модель вместо обучаемой не подставлялась. [Предшествующий Train и локальный успех input2](N1CoupledScientificReport-20261113.ru.md).

Train завершился **invalid_observation/ambiguous**, общего TrainingCertificate нет. Терминальный вектор отличается от локально успешного кандидата group48, поэтому его локальная готовность сюда не переносится. Здесь нет нового обучения, warm continuation, независимого Test или сертификата калибровки.

Каждый из восьми паттернов предъявлен отдельно с reset-per-trial, полным окном 2 с и 4001 исходным отсчётом. Модель заморожена внутри каждого условия; между условиями изменён только заявленный порог. Все 16 наблюдений завершены и валидны. Порог входит в model identity, поэтому разные hashes двух условий ожидаемы. Повтор исходного порога100 побайтово воспроизвёл samples/model_before предыдущего frozen8 baseline.

| Условие | TP | FP | FN | TN | Ответившие отвлекающие | Точность |
|---|---:|---:|---:|---:|---:|---:|
| Исходный порог100 |0|0|1|7|0/7|7/8, целевой пропущен|
| Фиксированный 0.03578062022182049 |1|5|0|2|5/7|3/8|

Правило выбора одного кандидата зафиксировано до реального spiking-прогона: середина между target LT maximum 0.03724473698714392 и наибольшим строго меньшим foil LT maximum 0.03431650345649706. Margin относительно максимума всех foils равен −0.012079873648321415. Поэтому это **Same-Matrix diagnostic**, а не независимая оценка. После получения спайков порог не подстраивался. Совпадение proxy FP5 и реального FP5 не заменяет фактических событий.

## Когда возникают реальные спайки

Критерий post_anchor_target_whole_window_foil_v1 считает ответ от onset по полному окну; TP сохранён по этому заранее объявленному критерию. Ранний target отдельно отмечен и не выдаётся за распознавание всей пачки. Времена в таблице и на рисунках абсолютные native timestamps, в секундах.

| sample_id | Метка | Спайки LT | Последний входной импульс | Результат |
|---|---|---|---:|---|
|phasea-row-0|target|0.262|0.49|TP, до завершения входа|
|phasea-row-1|foil|нет|2.4905|TN|
|phasea-row-2|foil|4.4965|4.491|FP|
|phasea-row-3|foil|нет|6.4915|TN|
|phasea-row-4|foil|8.256|8.492|FP, до завершения входа|
|phasea-row-5|foil|10.497; 10.74|10.4925|FP, два события|
|phasea-row-6|foil|12.2745; 12.3115|12.493|FP, два ранних события|
|phasea-row-7|foil|14.675; 14.712|14.4935|FP, два события|

Из девяти событий только одно относится к target; это отличается от доли ответивших паттернов. Тестирование учитывает полный отклик. Максимум всей пачки при этом не подменяет максимум закреплённого импульса при обучении.

## Временные графики всех восьми паттернов

Синий — записанный SumPotential сомы, оранжевый — фактические входные импульсы, фиолетовые вертикали — реальные события LT. Overview сохраняет отрицательную фазу после срабатывания и одинаковую Y-шкалу для всех паттернов. Порог показан только на графиках LT decision potential: он не является порогом отдельной сомы.

Оригиналы 1920×960, без прореживания. Zoom охватывает 0.05 с: native шаг0.0005 с занимает 14.208 пикселя по фактической ширине оси. Для молчащих строк1/3 выбран detail с явно локальной Y-шкалой; их амплитуды нельзя сравнивать по высоте картинки с общей шкалой. Внутри native тика событие LT может предшествовать сохранённому after-children потенциалу; отсутствие видимого пересечения в одном отсчёте не отменяет запись события.

### phasea-row-0: целевой паттерн

![Потенциал сомы и реальные входы, phasea-row-0](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0000-soma-001/overview.png)

[Увеличение сомы](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0000-soma-001/zoom-006.png), [LT: полное окно](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0000-lt-decision/overview.png), [LT: увеличение](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0000-lt-decision/zoom-006.png).

### phasea-row-1: отвлекающий паттерн

![Потенциал сомы и реальные входы, phasea-row-1](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0001-soma-001/overview.png)

[Увеличение сомы](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0001-soma-001/zoom-011-detail.png), [LT: полное окно](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0001-lt-decision/overview.png), [LT: увеличение](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0001-lt-decision/zoom-011-detail.png).

### phasea-row-2: отвлекающий паттерн

![Потенциал сомы и реальные входы, phasea-row-2](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0002-soma-001/overview.png)

[Увеличение сомы](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0002-soma-001/zoom-010.png), [LT: полное окно](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0002-lt-decision/overview.png), [LT: увеличение](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0002-lt-decision/zoom-010.png).

### phasea-row-3: отвлекающий паттерн

![Потенциал сомы и реальные входы, phasea-row-3](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0003-soma-001/overview.png)

[Увеличение сомы](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0003-soma-001/zoom-011-detail.png), [LT: полное окно](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0003-lt-decision/overview.png), [LT: увеличение](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0003-lt-decision/zoom-011-detail.png).

### phasea-row-4: отвлекающий паттерн

![Потенциал сомы и реальные входы, phasea-row-4](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0004-soma-001/overview.png)

[Увеличение сомы](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0004-soma-001/zoom-006.png), [LT: полное окно](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0004-lt-decision/overview.png), [LT: увеличение](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0004-lt-decision/zoom-006.png).

### phasea-row-5: отвлекающий паттерн

![Потенциал сомы и реальные входы, phasea-row-5](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0005-soma-001/overview.png)

[Увеличение сомы](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0005-soma-001/zoom-010.png), [LT: полное окно](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0005-lt-decision/overview.png), [LT: увеличение](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0005-lt-decision/zoom-010.png).

### phasea-row-6: отвлекающий паттерн

![Потенциал сомы и реальные входы, phasea-row-6](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0006-soma-001/overview.png)

[Увеличение сомы](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0006-soma-001/zoom-006.png), [LT: полное окно](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0006-lt-decision/overview.png), [LT: увеличение](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0006-lt-decision/zoom-006.png).

### phasea-row-7: отвлекающий паттерн

![Потенциал сомы и реальные входы, phasea-row-7](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0007-soma-001/overview.png)

[Увеличение сомы](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0007-soma-001/zoom-014.png), [LT: полное окно](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0007-lt-decision/overview.png), [LT: увеличение](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/trial-0007-lt-decision/zoom-014.png).

## Проверки и воспроизводимость

Реальные baseline/candidate native runs completed/closed за190.03793791122735 и249.22456999728456 с соответственно. Production-проверка опыта1/1 PASS2379.098 с; внешний процесс закрыт вместе с дочерними за2410.941907689 с. Построение и проверка отчёта1/1 PASS457.799 с, внешний процесс487.485312591 с; ошибок heartbeat нет. Это wall time, не model time; поле model_time в receipts равно null.

Просмотрены **все32 выбранных оригинальных PNG**: 8 обзорных Soma, 8 обзорных LT и по8 увеличений. Подписи читаются, actual input overlays и события сохранены. Полная gallery1087 PNG плюс SVG/PDF воспроизводится и остаётся кэшем M40; её полный ручной просмотр не заявляется. Исходный manifest с visual_acceptance_complete=false сохранён без переписывания: эта приёмка относится только к перечисленным32 выбранным файлам. [Selection и SHA256 оригиналов](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/threshold-figures/selected-originals.json).

[Фактические metrics и receipts](ValidationPlans/M40N1CoupledThresholdA1-20261113/RESULT.ru.md), [проверка отчёта](ValidationPlans/M40N1CoupledThresholdReportA1-20261114/RESULT.ru.md), [полный compact primary](ValidationPlans/M40N1CoupledThresholdPrimaryA1-20261114/RESULT.ru.md). Архив69,875,324B содержит826 regular files и2 проверенных aliases (828 логических записей), включая модели, все16 наблюдений и закрытые execution/controller receipts. SHA256 ae966e7fdd8c507d240d1a73e54d9fff741828dc2d753af465fcf41c69e5600b; независимый restore этого нового архива ещё не выполнен. PNG занимают4,753,640B; полная gallery в Git не добавлена.

Source SDK root74e5d206d4b619fcf81f77f11b54ebec7b8f0f6e, Pulse7c6c94785af0c83104d348bb3b733ed1f149c8a8. Runtime105ccc46bf2d23aa093ee6ec5fb088d9f33faa8e572f8191869f8cc279377a8a. Исходный stopped-state SHA2568ab8e4d9bfbc935ff2e5b888e14f611397036869beb2a6188bc2790eb2a40b98 остался неизменным. Полные manifests и raw receipts сохранены побайтово.

## Что следует из результата

У этого остановленного состояния снижение порога устраняет молчание target, но сопровождается множеством ложных ответов. Этот опыт не обосновывает общую невозможность обучения Branch, не отменяет августовские визуальные4/8–6/8 и не сравнивает контроллеры на согласованной полной матрице.

Следующая работа относится к незавершённому обучению: исследовать неоднозначность раннего закреплённого пика и получить свежую all-input verification либо честный ограниченный исход поиска. Повторный подбор порога по тем же восьми результатам не заменяет эту задачу. После выбора модели и порога необходим отдельно объявленный frozen независимый протокол.
