# Cold cap16: полная характеристика и проверка порогов

Статус: получена исходная подпороговая характеристика обеих фактически
сохранённых моделей. Обе модели завершили фактическую проверку выбранных порогов:
Classic и Branch — TP1/FP2/FN0/TN5. Общий owner completed, группы закрыты. Это Same-Matrix diagnostic stopped-моделей.
Обе исходные Train-сессии завершились BudgetExhausted без сертификата.

## Полученные наблюдения

Закрытый `s11-fair-input-cold-matrix-m40-a1` сохранил по8 native наблюдений
Classic и Branch. Для каждой модели:32008 ticks при2000Hz,8 окон по2с,
4001 отсчёт в каждом окне, native reset-per-trial. Входы и все Soma/LT
отсчёты записаны. Фактические input times проверяются по первичным событиям.
Обе native execution записи завершены; оба процесса exit0 с loaded-files
capture и закрытыми группами. Общий controller остановился по wall budget;
этот отрицательный итог сохраняется.

Classic имеет завершённый run manifest и метрики при Threshold100:
TP0/FP0/FN1/TN7. Все8 паттернов вызвали молчание. Accuracy7/8 здесь не означает
работающую детекцию. Branch также сохранил8 complete/valid native наблюдений
без спайков, но его run manifest не успел оформиться. Полный portable аудит
его исходного run не объявляется завершённым по одним флагам observations.

Модель Classic: `da62fde7b7ce7db67acd6f8abe4eedab4a33f07d7b3c561c84d55762cb253dee`.
Модель Branch: `90d9dacecd08b165a3cf394558abdaf9446bf9ec1206409bb8e80b34009f63e0`.
Это фактические terminal graph, а не выбранные Python скаляры из истории.

## Гипотезы порога

Для Test берётся максимум фактически записанного LT decision potential по
полному окну паттерна. Soma и LT potential не подменяют друг друга: у Classic
здесь используются именно LT potential. Эти данные не меняют правило Train,
которое относится к максимуму закреплённого импульса.

Пусть A_target — максимум целевого паттерна. Из максимумов отвлекающих
выбирается наибольший строго меньший A_target: A_lower. Кандидат:

```text
Threshold_candidate = A_lower + (A_target - A_lower) / 2
```

| Модель | A_lower | A_target | Кандидат |
|---|---:|---:|---:|
| Classic |0.018950574616243304|0.019859704144444407|0.019405139380343855|
| Branch |0.07158936690583229|0.076077677337829|0.07383352212183064|

Для обеих моделей подпороговый proxy — TP1/FP2/FN0/TN5. Это гипотеза по
максимумам, **не результат классификации**. Два отвлекающих максимума выше
целевого; идеальная разделимость по этим данным не утверждается. Реальный
спайк может изменить динамику и последующие пики, поэтому требуется прогон
с выбранным Threshold. Native model units не объявляются проверенными SI.

## Запущенный опыт

Job `s11-fair-input-threshold-m40-a1`, controls
`9b47fd86155f56bb695faffa0ce3e2b0eb324bfd`.
Request: `/media/user/Data/TimeLearnerRefactor/requests/fair-input-threshold-a1/request.json`.
В Git controls сохранены правило,16 исходных observation hashes, максимумы,
кандидаты и исходная отрицательная closure общего controller.

Используется production recorded_diagnostic_matrix, actor Root
`ea0b039f3bd4f7784ff76e32d90fb99a50032ac2`; native Root
`445c834fe00b81f07857f5622809349e01bd1841`, Pulse
`c54d9c0a65ac6eadeccfe1793672b7a9472ea559`.
Runtime fingerprint:
`c9e6acf35f2b59fe9ee6f4b0033d11d285a242672e557e6c8452cf6490b673b3`.
Это тот же полный source importer и native runtime, что у исходной
характеристики. Новый DATA API не используется.

Предъявляются все8 исходных PhaseA паттернов для каждой модели,2с,
reset-per-trial, whole-window criterion от onset. Единственный новый фактор —
явно заданный диагностический Threshold. Модель frozen внутри каждого Test;
её новая threshold revision должна совпадать до/после каждой пробы.
Полный source, summary и provenance проверяются штатным runner повторно.

Лимиты: owner16GiB + native leaf16GiB; leaf3600с, whole14400с;
16GiB output ceiling и16GiB minimum free. Удлинён общий бюджет для полного
чтения и анализа больших исходных историй; предыдущий исход не переписывается.
Проверка никогда не превращает BudgetExhausted в Exact или завершённый Train.

## Следующая приёмка

Нужны actual16 observations, неизменность физической модели, strict scorer,
разделение TP/FP/FN/TN и реальные временные позиции спайков. Незавершённый
prefix не получает оценку полного набора. Затем — читаемые временные графики
каждого паттерна с наложенными фактическими входными импульсами, все Soma
отдельно, общий масштаб внутри сравниваемой модели и увеличенные фрагменты.
Полные primary и отчёты публикуются во внешнем M40 archive; Git содержит
компактные ссылки. Independent Test и robustness остаются отдельными опытами.

После фактического TP≥1/TN≥2 соответствующие примеры включаются в актуальные
DOCX Classic/Branch как варианты общего семейства. До этого DOCXv2 остаётся
последней проверенной редакцией.

## Classic: реальное подтверждение выбранного порога

Все8 declared observations завершены, valid/complete, по4001 samples/2с.
Production manifest completed/valid, whole-window counts **TP1/FP2/FN0/TN5**.
Это результат реальных спайков с установленным порогом, а не offline sweep.

| PhaseA row | Метка | Спайки | Время относительно начала окна, с |
|---|---|---:|---|
|0|target|1|0.493|
|1|foil|0|—|
|2|foil|0|—|
|3|foil|0|—|
|4|foil|1|0.492|
|5|foil|0|—|
|6|foil|1|0.492|
|7|foil|0|—|

Revision до/после каждой пробы:
`27112e8ad8ef2d0ec298978bae0640cfc82ba7ae33c35ce710331100868e3943`.
Цель отвечает через3мс после последнего входа, ложные ответы rows4/6 через2мс.
Accuracy6/8; foil response rate2/7. Начальные Train/timing/amplitude residuals
не становятся успешными от подбора порога. Это Same-Matrix diagnostic stopped
model, не независимое подтверждение обобщения и не all-input certificate.
[Наблюдения и manifest readback](../../../Reports/StructTrain/TimeLearner/FairInputCold-20261118/threshold-confirmation-progress.json).

Branch также завершён: TP1/FP2/FN0/TN5, те же false-positive rows4/6.
Revision74786bc43e78e8f5c98993f8a1d826b08133f02356a2c7e4488f1d27ef9a6f8a.
Оба run manifests completed/valid; общий controller operation_passed=True,
reason=None, все groups closed и lease released. Full primary collection и
temporal report выполняются отдельно; повторение Train/Test не требуется.
[Закрытые16 наблюдений и штатные metrics](../../../Reports/StructTrain/TimeLearner/FairInputCold-20261118/threshold-confirmation-closed.json).
