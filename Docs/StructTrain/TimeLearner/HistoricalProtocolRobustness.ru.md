# Frozen-проверки порядка и ITI августовской модели

Постановка: сохранённая Phase A Classic-модель49/41/25/1, исходный threshold
0.0135 и native runtime Rootde02/Pulsecbf. Исходный контроль6/8 сохранён вместе
с отдельно подтверждёнными4/8 и5/8. Новая серия не переобучает модель, не подбирает
порог и не объявляет эти восемь паттернов независимыми данными.

Планируемая матрица:8 циклических перестановок всех8 паттернов ×Dataset Delay
1.5/3.0s. Target присутствует в каждой позиции. Все native процессы начинают
с исходного сохранённого графа; внутри каждой матрицы остаётся исторический
native reset policy. Reset-per-trial — отдельный будущий протокол, здесь он не
добавляется. Первым должен пройти исходный order/ITI контроль с побайтным CSV
6/8; остальные условия нельзя объявлять выполненными по этому контролю.

`historical_protocol_robustness` меняет реальные плоские блоки MatrixData
(32×1, восемь групп по4) и соответствующие MatrixClasses1×8, адресно в Model
и Parameters. Learner владеет Delay и устанавливает effective dataset gap,
поэтому обе декларации меняются согласованно. Preflight читает построенный
native граф и actual Dataset параметры; последующие timestamps должны
подтвердить фактические ISI и межпачечные интервалы. Отсутствующий либо не
влияющий фактор — ошибка постановки, не научный отрицательный результат.

Model mode1/Parameters mode0 сохраняются: старый runtime иначе может оставить
неверную размерность learner buffers. Короткий pre-stimulus native запуск
проверяет полную effective neuron identity и пять строк readout до первого
импульса. Его сохранённая Model не используется как вход полного Test.
Каждый40s Test использует отдельную исходную подготовленную копию, native
2000Hz recorder и полный post-run graph fingerprint. Исторический C++ не
патчится, bool lifecycle не интерпретируются как доказательство качества.

Reader различает sample ID и позиционный native trial ID, проверяет все32
actual impulses, labels/ISI, clock80000 samples/12 streams и все LT edges.
Сохраняются native in-window counts, полные интервалы до следующей пачки,
поздние и pre-stimulus spikes. Поздние события не исчезают из отчёта из-за
нулевого native CSV ответа. Historical accuracy не переименовывается в новый
сертификат; научный verdict не создаётся до полной приёмки наблюдений.

Полные временные графики должны показать все8 паттернов с actual input pulses,
полный диапазон и достаточно крупные детали; выбранные рисунки входят в Git,
полный воспроизводимый cache — на M40. Сжатые primary/configs/models/metrics
публикуются через Git после фактического завершения задания.

## Механическое выделение общей подготовки

В `historical_phasea_native.py` перенесены8 общих функций из двух старых
корневых replay/coldtest harness, плюс4 константы. Новая библиотека не импортирует
тестовые запускатели. Оба прежних CLI main и все8 function AST неизменны:
[source reconciliation](HistoricalPreparationExtraction.json). Это отдельный
механический шаг, не доказательство исполнения новых перестановок.

В первом снимке были выполнены только local AST/source review. Серверная проверка
общих helper, actual original-protocol pilot, corruption controls, расширение
до16 условий, temporal reports и scientific interpretation ещё не выполнены.
Этап11 остаётся частичным. Августовские исходные наблюдения не пересматриваются.


## Пилот и сохранённые отказы подготовки

[Зарегистрированный пилот](HistoricalProtocolJobs.json) сначала проверяет2×2:
исходный/сдвинутый на1 порядок ×ITI1.5/3.0, один frozen threshold0.0135.
Это4 полных матрицы и4 pre-stimulus checks, не вся16-условная серия. Все11
подготовительных tests на реальных архивных конфигах прошли; результат A3
на этом снимке ещё выполняется и не принят.

A1 остановился до native execution: при механическом переносе write был
пропущен модульный import json. AST восьми тел сохранился, но это не проверяло
их namespace dependencies. Импорт исправлен; существующая positive preparation
проверка теперь также выполняет production запись protocol.json. [ReceiptA1](HistoricalProtocolPilotA1Verification.json)
сверяет27 primary members/41052 compressed bytes,387 tool hashes и11 tests;
научного результата нет.

A2 выполнил один pre-stimulus native процесс и остановился перед40s Test:
новый full parameter export терял исходный Parameters threshold overlay0.0135
и восстанавливал parent Model default0.0115. Строгий graph guard это отказал.
Все604 узла/496 связей и все их параметры совпали с исходным neuron, поэтому
это не повреждение структуры: не было применено заявленное старое наложение
порога. Подготовка теперь берёт controls из исходного Parameters и переносит
их в обе новые декларации перед full export; не подбирает новый порог и не
ослабляет identity guard. [ReceiptA2](HistoricalProtocolPilotA2Verification.json)
сверяет69 primary members/56652 compressed bytes,387 tool hashes,26 actual
loaded-file records; полных Test0. Обе failed группы закрыты/leases released.

A3 использует новый immutable tool snapshot19f24aa и прежний runtime16428572,
прошёл11 preparation controls, подтверждён живым kernel cgroup. Старые попытки
и их terminal не переписываются. После pilot acceptance нужны расширение до
всех target positions, temporal reports/visual QA и интерпретация результатов.


### A3 raw baseline и продолжение A4

A3 завершил pre-stimulus иполную40s native матрицу. CSV побайтно совпал с
архивом: TP1/FP2/FN0/TN5,6/8. После этого reader ошибочно передал JSON array
trace-files в object-only load и остановился. A3 terminal остался failed,
но это не отсутствие выполненного native Test: executed2, full matrix1,
analysis-completed0. [Независимая сверка A3](HistoricalProtocolPilotA3Verification.json)
проверила95 primary members/4348184 compressed bytes,387 tool hashes и52
loaded-file bindings двух завершённых процессов; группа closed/lease released.

Reader исправлен с сохранением строгого array schema и source-role bindings.
Добавлены6 controls на настоящем complete A3 corpus; вместе с подготовкой17
проверок прошли на Elder. Они включают complete original6/8, отказ при пропавшем
sample, смене label, object вместоarray, ложном source иduplicate trace.

A4 повторно анализирует baseline без новых Calculate. Каждый используемый файл
сверен с member hashes опубликованного A3 bundle; старый case read-only. Полные
12 native streams/80000 frames и все окна приняты новым reader, originalCSV
неизменен, effective neuron hashca025286 сохраняется. Реальный межпачечный gap
при declaredDelay1.5 равен примерно1.511s: первое0.01 иnative tick не скрываются
за округлённой меткой ITI. A4 теперь выполняет только3 оставшиеся условия,
то есть6 новых native процессов, плюс2 переиспользованных. Это не повторное
обучение и не независимые повторы; окончательная приёмка2×2 ещё ожидается.


## Принятая первичная проверка пилота2×2

Evidence `72af32bdd057952d94ffe0241a3d6597f6a193f0`, toolRoot
`ea5c884e7a8e544e1fa9b4787886ab1058960625`. Все4 условия завершены;
6 новых native processes и2 baseline processes из A3, без повторного Calculate
исходного контроля. Группа закрыта/lease released;17 Python checks без skips.

|Порядок / позиция target|DeclaredDelay|Фактический gap|Native результат|FP sample IDs|
|---|---:|---:|---|---|
|Исходный /0|1.5s|≈1.511s|TP1/FP2/FN0/TN5,6/8|phasea-4,phasea-6|
|Исходный /0|3.0s|≈3.011s|TP1/FP2/FN0/TN5,6/8|phasea-4,phasea-6|
|Циклический сдвиг1 /7|1.5s|≈1.511s|TP1/FP2/FN0/TN5,6/8|phasea-4,phasea-6|
|Циклический сдвиг1 /7|3.0s|≈3.011s|TP1/FP2/FN0/TN5,6/8|phasea-4,phasea-6|

Во всех четырёх записях3 LT edges, late/pre-stimulus spikes0; границы32
trial intervals покрыты. Модель иthreshold0.0135 одинаковы на всех проверенных
boundaries: neuron hash `ca025286e43839d8442e134978603f1328017b2b1b5234138878206c0e3b82f3`.
Совпали не только counts, но иID двух ложных ответов. Waveform equivalence
между изменёнными протоколами не заявлена; здесь нет улучшения классификации,
переобучения, независимого Test или проверки всех перестановок.

[Независимая metadata сверка](HistoricalProtocolPilotVerification.json)
проверила263 primary members/13134272 compressed bytes, SHA256
`593efde1cfb4ccbd193bbf68e628cda8c7b1236a2250e93f8a9a14294de1c686`,387 tool
hashes,156 loaded-file bindings6 новых процессов и80 неизменённых bindings
переиспользованного baseline case, связанного с A3 Git archive. Локально
проверялись только Git/archive/hash/schema metadata; численный анализ выполнен
на Elder. Изначальный A3 failed terminal не переименован в passed.

Это ограниченное подтверждение устойчивости исторических6/8 к двум проверенным
порядкам и удвоенному Delay. Оно не отменяет исходные4/8–6/8 и не переносится
на другие models/modes. Обязательные temporal reports/visual QA пилота ещё не
построены; итоговый читаемый научный отчёт с графиками и расширение до16 условий
остаются следующими шагами. Исходные этапы1–12 всё ещё частичны.


## Временные отчёты пилота приняты отдельно

На M40 из опубликованных A3/A4 primary bundles восстановлены все четыре
case без новых native расчётов. ToolRoot `3466d963c7fe0a6800b740b35a02dc3b25ae5f41`;
evidence `5a8048ad2eb0349c5b09ab21f1267c64d550f90d`. Построены128 PNG:
8 паттернов ×4 вида ×4 условия,1920×1680, font≥12, без прореживания.
Реальные input traces наложены на четыре сомы и native SomaSumPotential;
выходной LT spike отделён от глобального максимума Test. Следующая пачка
исключена из предыдущего интервала. Full views сохраняют отрицательный
feedback, positive companions явно отмечают отсечение.

Три адресных tests на настоящих записях прошли; прежние observations не
изменились.88 compact archive members/46608B и389 tool-source hashes
сверены независимо; шесть выбранных PNG1744565B открыты по отдельности.
Это визуальная приёмка выбранных рисунков, не заявление о ручном просмотре
всех128. A4 layout overlap исправлен размещением подписи вне waveform area;
его evidence/negative review сохранены. Ошибки подготовки окружения A1–A3
сохранены отдельно от результатов моделей. M40 schema1 path ledger не
мигрировался: cgroup limit2GiB/tasks128 проверен отдельно, capacity-based
admission этого задания не заявлен.

[Читаемый научный отчёт с рисунками](HistoricalFrozenProtocolScientificReport-2026-11-07.ru.md)
и [независимая сверка](HistoricalProtocolTemporalVerification.json). Полный
кэш остаётся на M40 Data; primary данные и выбранные figures доступны в Git.
Пилотный temporal deliverable завершён; оставшиеся12 условий, вся матрица
режимов и общий этап11 остаются открытыми.


## Полная первичная матрица8×2 принята

Выполнены оставшиеся12 native условий с тем же frozen model/threshold.
Все16 условий дали6/8, TP1/FP2/FN0/TN5, те же FP sample IDs4 и6,
late/pre-stimulus events0. Target присутствовал во всех8 позициях на каждом
Delay.24 новых процесса завершены,8 прежних использованы без повторов;
группа закрыта/lease released.1002 primary members52316400B сохранены в Git.
[Полный отчёт по первичным результатам](HistoricalFrozenProtocolMatrixScientificReport-2026-11-07.ru.md)
и [независимая сверка](HistoricalProtocolCompletionVerification.json).
Фраза выше про оставшиеся12 условий относится к границе пилотного снимка:
их первичные данные теперь приняты;384 новых temporal views ещё ожидаются.
Это не новые cold trainings и не завершение всего этапа11.
