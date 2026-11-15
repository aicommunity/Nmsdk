# Classic N0:64 frozen пробы с target во всех позициях —14.11.2026

**Во всех восьми проверенных порядках получены TP1/FP4/FN0/TN3.** По64 пробам:TP8/FP32/FN0/TN24,32 правильных ответа из64 и32 ложных реакции из56 foil. Каждый pattern сохранил класс ответа во всех позициях. Target каждый раз дал один спайк примерно0.503с от начала своей пробы —13мс после последнего actual input0.49с. Перестановка не устранила ложные срабатывания этой модели при этом пороге и reset policy.

## Что зафиксировано

Та же реальная stopped Classic N0 модель L=[45,1,1,1],Ns1,Rs86M, stock NSPNeuronGen **без LTMembrane**,2000Гц; тот же threshold0.012765548843211696.64 полных окна по2с,reset_per_trial, восемь cyclic rotations исходных8 pattern IDs/hashes. Новый Train и подбор порога не выполнялись. Это8 детерминированных предъявлений каждого pattern одной модели, не8 независимых обучений либо случайных seeds. ITI и continuous stream не менялись и отдельно здесь не проверены.

Source model revision35d849faa2aaea5d2620f0fd59d9934c77760b7fde0dd49d3284539f69f68263; C++ SDKroot74e5d206d4b619fcf81f77f11b54ebec7b8f0f6e/Pulse7c6c94785af0c83104d348bb3b733ed1f149c8a8, runtime377e0ebdee7bb1fa1cc11346438a1d2102b2124f08e3054b6347400c10a4f335. Новое исправление N0 geometry здесь не использовалось. Исходное обучение остановлено invalid_observation/ambiguous, certificate=null. Порог ранее выбран на той же матрице и теперь зафиксирован; это Historical Same-Matrix diagnostic, не независимая калибровка/оценка.

## Фактический итог

|Pattern|Метка|Результат в каждой позиции|Число таких ответов|
|---|---|---|---:|
|phasea-row-0|target|TP|8|
|phasea-row-1|foil|TN|8|
|phasea-row-2|foil|TN|8|
|phasea-row-3|foil|TN|8|
|phasea-row-4|foil|FP|8|
|phasea-row-5|foil|FP|8|
|phasea-row-6|foil|FP|8|
|phasea-row-7|foil|FP|8|

|Позиция target, начиная с1|Rotation|Target spike от начала пробы,мс|После последнего input,мс|TP/FP/FN/TN|
|---:|---:|---:|---:|---|
|1|0|503|13|1/4/0/3|
|2|7|503|13|1/4/0/3|
|3|6|503|13|1/4/0/3|
|4|5|503|13|1/4/0/3|
|5|4|503|13|1/4/0/3|
|6|3|503|13|1/4/0/3|
|7|2|503|13|1/4/0/3|
|8|1|503|13|1/4/0/3|

Времена в таблице округлены для чтения; полные значения сохранены в первичных данных. Ранние и поздние foil spikes учитываются, молчание target не выдаётся за успешную детекцию. Неизменность класса не является заявлением о побайтном равенстве всех64 waveforms: такое равенство проверено для первых8 относительно исходного опыта.

## Проверки и доступность данных

[Production1/1 и полные результаты](ValidationPlans/M40ClassicN0OrderMatrixA3-20261114/RESULT.ru.md): все64 observations complete/valid; first8 waveform samples/model_before точно равны исходному8-trial run. Native model.json/model-after.json побайтно равны исходной модели; source package/manifest неизменны. Outer completed3706.5094792968594с, whole group закрыта. Канонический scorer использует labels/IDs и полное множество trials; положение target в первой строке не является условием результата.

[Полный compact primary](ValidationPlans/M40ClassicN0OrderPrimaryA1-20261114/RESULT.ru.md):55,527,604B XZ,396 logical members вместо1.234GB expanded. В Git доступны все необходимые модели,64 observations, восемь baseline observations, конфиги и receipts. Независимый semantic restore этого нового архива ещё открыт. A1/A2 неверный режим запуска отклонён до native execution; failures сохранены и не считаются опытами модели.

## Все8 паттернов: проверенная исходная матрица

Ниже явно повторно использованы проверенные рисунки [исходного реального опыта](ClassicN0ThresholdScientificReport-20261114.ru.md). Первые8 новых waveform samples, inputs и model_before **точно совпали** с его candidate run, поэтому это визуализация воспроизведённого baseline, а не подмена нового порядка старым. Оранжевый — actual input, пунктир — actual LT events; единицы модели, SI не подтверждён. Для положительного диапазона Y отрицательный reset clipped; полный диапазон и LT decision figures доступны в исходном отчёте. [Новая собственная gallery принята1/1](ValidationPlans/M40ClassicN0OrderReportA2-20261114/RESULT.ru.md):15 trials×5 каналов×2 шкалы,267 PNG. Ниже добавлены8 новых target views и выбранные LT/native details; все13 новых публикуемых original PNG просмотрены.

### phasea-row-0:target,TP

![Воспроизведённый baseline Soma1 pattern0](ValidationPlans/M40StockN0ClassicThresholdPositiveReportA2-20261114/completed/worker/tmp/fixed-threshold-positive-response-gallery/trial-0000-soma-001/overview.png)

### phasea-row-1:foil,TN

![Воспроизведённый baseline Soma1 pattern1](ValidationPlans/M40StockN0ClassicThresholdPositiveReportA2-20261114/completed/worker/tmp/fixed-threshold-positive-response-gallery/trial-0001-soma-001/overview.png)

### phasea-row-2:foil,TN

![Воспроизведённый baseline Soma1 pattern2](ValidationPlans/M40StockN0ClassicThresholdPositiveReportA2-20261114/completed/worker/tmp/fixed-threshold-positive-response-gallery/trial-0002-soma-001/overview.png)

### phasea-row-3:foil,TN

![Воспроизведённый baseline Soma1 pattern3](ValidationPlans/M40StockN0ClassicThresholdPositiveReportA2-20261114/completed/worker/tmp/fixed-threshold-positive-response-gallery/trial-0003-soma-001/overview.png)

### phasea-row-4:foil,FP

![Воспроизведённый baseline Soma1 pattern4](ValidationPlans/M40StockN0ClassicThresholdPositiveReportA2-20261114/completed/worker/tmp/fixed-threshold-positive-response-gallery/trial-0004-soma-001/overview.png)

### phasea-row-5:foil,FP

![Воспроизведённый baseline Soma1 pattern5](ValidationPlans/M40StockN0ClassicThresholdPositiveReportA2-20261114/completed/worker/tmp/fixed-threshold-positive-response-gallery/trial-0005-soma-001/overview.png)

### phasea-row-6:foil,FP

![Воспроизведённый baseline Soma1 pattern6](ValidationPlans/M40StockN0ClassicThresholdPositiveReportA2-20261114/completed/worker/tmp/fixed-threshold-positive-response-gallery/trial-0006-soma-001/overview.png)

### phasea-row-7:foil,FP

![Воспроизведённый baseline Soma1 pattern7](ValidationPlans/M40StockN0ClassicThresholdPositiveReportA2-20261114/completed/worker/tmp/fixed-threshold-positive-response-gallery/trial-0007-soma-001/overview.png)

## Новые target responses во всех восьми позициях

Это actual64-trial run, а не baseline figures. У всех8 Soma1 views одна положительная Y-шкала, рассчитанная по всем64 observations; отрицательный reset выходит ниже оси и показан отдельно далее. Ось X — полное native абсолютное время собственной пробы. Класс ответа и события взяты из первичных записей.

### Target в позиции1

![Actual target position1](ValidationPlans/M40ClassicN0OrderReportA2-20261114/completed/worker/tmp/fixed-order-temporal-gallery/trial-0000-soma-001-positive/overview.png)

### Target в позиции2

![Actual target position2](ValidationPlans/M40ClassicN0OrderReportA2-20261114/completed/worker/tmp/fixed-order-temporal-gallery/trial-0057-soma-001-positive/overview.png)

### Target в позиции3

![Actual target position3](ValidationPlans/M40ClassicN0OrderReportA2-20261114/completed/worker/tmp/fixed-order-temporal-gallery/trial-0050-soma-001-positive/overview.png)

### Target в позиции4

![Actual target position4](ValidationPlans/M40ClassicN0OrderReportA2-20261114/completed/worker/tmp/fixed-order-temporal-gallery/trial-0043-soma-001-positive/overview.png)

### Target в позиции5

![Actual target position5](ValidationPlans/M40ClassicN0OrderReportA2-20261114/completed/worker/tmp/fixed-order-temporal-gallery/trial-0036-soma-001-positive/overview.png)

### Target в позиции6

![Actual target position6](ValidationPlans/M40ClassicN0OrderReportA2-20261114/completed/worker/tmp/fixed-order-temporal-gallery/trial-0029-soma-001-positive/overview.png)

### Target в позиции7

![Actual target position7](ValidationPlans/M40ClassicN0OrderReportA2-20261114/completed/worker/tmp/fixed-order-temporal-gallery/trial-0022-soma-001-positive/overview.png)

### Target в позиции8

![Actual target position8](ValidationPlans/M40ClassicN0OrderReportA2-20261114/completed/worker/tmp/fixed-order-temporal-gallery/trial-0015-soma-001-positive/overview.png)

## LT decision channel и native максимум сомы

LT threshold относится к LTZone.Potential; его нельзя читать как порог отдельной Soma1. Ниже первый и последний по времени target, каждый имеет реальное LT event после четвёртого input. Полный отрицательный reset сохранён отдельно.

![LT actual target trial0000](ValidationPlans/M40ClassicN0OrderReportA2-20261114/completed/worker/tmp/fixed-order-temporal-gallery/trial-0000-lt-decision-positive/overview.png)

![LT actual target trial0057](ValidationPlans/M40ClassicN0OrderReportA2-20261114/completed/worker/tmp/fixed-order-temporal-gallery/trial-0057-lt-decision-positive/overview.png)

![LT full range with reset](ValidationPlans/M40ClassicN0OrderReportA2-20261114/completed/worker/tmp/fixed-order-temporal-gallery/trial-0000-lt-decision-full/overview.png)

На увеличениях далее виден максимум полного Soma1-отклика, sample975,0.4875с от начала пробы. Он возникает до последнего input0.49с; это не противоречит позднему LT spike0.503с суммарного нейрона с четырьмя сомами. Принадлежность этого максимума закреплённому импульсу Train здесь не сертифицируется. Все21 native sample вокруг максимума показаны с маркерами без прореживания;71.04px/tick. Последняя ось X использует offset+114.51с: отметка0.006 означает114.516с абсолютного времени.

![Native Soma1 maximum trial0000](ValidationPlans/M40ClassicN0OrderReportA2-20261114/completed/worker/tmp/fixed-order-temporal-gallery/trial-0000-soma-001-positive/measured-peak-00975-detail.png)

![Native Soma1 maximum trial0057](ValidationPlans/M40ClassicN0OrderReportA2-20261114/completed/worker/tmp/fixed-order-temporal-gallery/trial-0057-soma-001-positive/measured-peak-00975-detail.png)

## Границы вывода

Получен валидный отрицательный результат для разделимости и положительный контроль повторяемости классов в восьми заданных cyclic orders при2с/reset_per_trial. Это не доказательство независимости от любого порядка/ITI/reset, не оценка других моделей и не завершённое обучение. Другой реальный порог может менять динамику через spike feedback; offline sweep этих spiking CSV не заменяет нового native прогона. Надёжная классификация без большинства ложных срабатываний пока не получена. Августовские визуально подтверждённые4/8–6/8 другого исходного протокола этим опытом не отменяются.
