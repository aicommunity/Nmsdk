# Готовность к научным экспериментам — 06.11.2026

Сквозной процесс cold Train → boundary continuation → полный model export →
измеренная калибровка с confirmation → frozen evaluation уже выполняется на
реальных компонентах Classic/Branch. **Итоговая научная матрица ещё не готова.**
Проверенные N2 LT engineering cases не заменяют штатную четырёхвходовую модель,
исторические8 паттернов или независимую оценку. Текущий статус всех этапов и
разделение develop/кандидата находятся в [единой сводке](ImplementationStatus.ru.md).

## Обязательные условия ограниченной серии

| Условие | Есть | Осталось для допуска целевого научного задания |
|---|---|---|
|Неизменяемый runtime|Раздельные сборки, manifests, actual loaded files/process identities и Git source closure|Принять используемый общий SDK срез; зафиксировать точные code/profile/binary/data hashes именно задания|
|Эффективная физическая модель|Native storage construction, graph readback, полный state transport проверены адресно|Выбрать проверенный профиль, подтвердить дочернюю физику/частоту/связи; не считать parent defaults описанием всего дерева|
|Обучение|Native measured search и completed/stopped outcomes существуют|Получить валидный результат целевого cold Train либо честный unresolved/budget outcome; исправить/исследовать stock burst ambiguity без вымышленных пиков|
|Реальный перенос Train→Test|Экспорт, native import и frozen owner работают в проверенных путях|Сверить полный semantic model fingerprint; после неудачного Train/переноса не оценивать шаблонный Test как обученный|
|Порог|Fixed и measured calibration/confirmation проверены|Явно выбрать Same-Matrix или независимый протокол; любой выбранный порог проверить реальным spiking run|
|Полные наблюдения|Строгие trial/sample IDs, labels/pattern hashes, clocks, windows, spikes и arbitrary-N soma traces|Подтвердить expected set и полные окна каждой объявленной пробы выбранного протокола; отсутствие данных не означает молчания|
|Оценка|Есть versioned scorer и реальные frozen controls|Зафиксировать модель/порог до независимого Test; отделить TP/FP/FN/timing/morphology/robustness от выполнения и сходимости|
|Управление запуском|Public CLI/coordinator, owned cancellation, leases и Git publisher применяются в адресных gates|Preflight выбранных факторов и возможностей, ресурсный бюджет/диск, все primary/model/metric артефакты и проверенная публикация|
|Визуальный отчёт|Production renderer строит все recorded patterns/somas с actual input overlays|Включить в отчёт каждого нового научного задания overview, читаемые zoom/local-Y и visual QA; графики не заменяют scorer|

Существуют команды корневого `python -m Scripts.StructTrain.TimeLearner`:
inventory, preflight/prepare, train/export, calibrate/evaluate, analyze/report,
pipeline, publish и history. Наличие команды не означает поддержки любого
параметра или физического профиля. Для конкретного запуска использовать exact
проверенный source snapshot и capability preflight. Native dataset/clock,
whole graph/storage и параметрические ограничения проверяются до дорогого Train.
Reserved/no-op поля нельзя использовать как действующие факторы эксперимента.

Начальная научная серия должна явно ограничить поддерживаемую область:
Classic/Branch, объявленные N0/N1/profiles и единая частота дерева. C-trim и
PostTune можно оставить выключенными; базовый контур обязан честно завершаться
без них. Включённую неподдерживаемую опцию нельзя молча игнорировать. Новая общая
амплитудная цель, аксонные задержки и другая нелинейная физика не подменяют
рефакторинг исходной задачи CapturedPerInput с опорным входомN−1.

## Что проверено и что это не доказывает

Normal304 и адресные ASan8 SDK2e прошли. ASan133 A3 дал132 passed/1 output-directory
assertion failure; runner исправлен и адресно проверен на прежних бинарниках.
Полный свежий A5 прошёл133/133. Сверены4888 primary members,321 native,
323 Python и335 tool source hashes; fresh closure/released lease подтверждены.
[Точные версии и scope](IntegratedSharedAsan133Verification.json): root2e061/
Pulse12d, без последующих invalid-budget/recovery изменений. Это закрывает
заявленный ASan133 gate, не всю обязательную матрицу SDK. Старые ASan304 относятся
к другому SDK. Detect_leaks=0 не доказывает отсутствие утечек.

Coordinator schema1/schema2 прошёл16/16 cases /40 native phases, попарные CSV
совпали. ConditionSpec binding при этом декларативен; он не доказывает полную
effective-factor attestation. Два engineering N2 LT случая TP2/FP0/FN0/TN2
используют same-matrix calibration с одним повторяемым target и одним foil.
Это более узкий набор, чем прежняя восьмипаттерновая N2 LT серия5/8 с FP3;
её [измеренный результат](ScientificResults-2026-11-03.ru.md) сохраняется.
Суффиксы ModelSpec1/2 не являются версиями
контроллера или независимыми случайными репликами.
[Исходники, результаты и графики](https://github.com/aicommunity/Nmsdk/blob/ec15c06b1a52917b7a1a49abbddbd095e4b6bb7f/Docs/StructTrain/TimeLearner/SharedControllerNovember6Status.ru.md).

На stock NSPNeuronGen без дополнительной LT membrane валидного завершённого
обучения новой целевой серии пока нет. Missing/ambiguous peak, численная ошибка,
неполное окно и отсутствие spike — разные причины. Предсказанное время прихода
не может подтверждать отсутствующий измеренный пик. Не поднимать автоматически
minimum amplitude/tolerances ради положительного verdict и не объявлять локальный
stall доказательством физической невозможности.

## Последовательность научных проверок

1. [Saved-state replay августа](HistoricalAugustReplay.ru.md) уже воспроизвёл
   три исходных результата4/8,5/8,6/8 с первоначальным протоколом. Его receipt
   не является V2 certificate или независимой оценкой.
2. [Настоящий historical cold Train→Test](HistoricalAugustColdStart.ru.md)
   также уже воспроизвёл эти результаты с полным переносом нейрона. Осталось
   legacy/V2 A/B при согласованных исходных условиях. До интерпретации различий
   проверить effective graph/params и реальные волны; совпадение L само по себе
   не доказывает эквивалентность алгоритмов.
3. Frozen evaluation с target в каждой позиции, изменениями порядка и ITI.
   Reset-per-trial и continuous stream проверять отдельно, с полными окнами,
   неизменным learned-state hash и фиксированным порогом.
4. Расширять профили, торможение, C-trim и все PostTune modes после адресной
   приёмки соответствующих возможностей. Не смешивать новую физику с исправлением
   реализации. Влияние LT устанавливать контролируемым A/B, а не сравнением
   одновременно изменённых профилей.

Августовские визуально подтверждённые4/8–6/8 сохраняются как рабочие результаты
исходного протокола с плохой разделимостью. Перестановки и увеличенный ITI тогда
не проверялись; результаты изменённого протокола не отменяют исходное наблюдение.
Same-Matrix разрешён с явной маркировкой, но не выдаётся за независимый Test.
Silent threshold не делает молчаливые target успешной детекцией. СерияD не
возобновляется автоматически;8/8 не является условием завершения рефакторинга.

Сборки, численные проверки и render выполняются на Elder/M40 через jump host.
Синхронизация source/config/results — Git. В Git сохраняются сжатые primary,
модели, метрики и выбранные PNG; полные воспроизводимые отчёты — кэш M40 Data.
[Требования масштаба и visual QA](VisualTestReports.ru.md).

Первая ограниченная серия не требует окончания всей исторической миграции
скриптов и всех удобств очереди. Она требует доказанного сквозного процесса
именно своего задания. Общая рекомендация ControllerVersion2 и завершение
[исходного плана](RefactoringPlan.ru.md) требуют всей обязательной матрицы.
Предыдущая накопительная постановка29.10 с поздними дополнениями сохранена в
[Git](https://github.com/aicommunity/Nmsdk/blob/ec15c06b1a52917b7a1a49abbddbd095e4b6bb7f/Docs/StructTrain/TimeLearner/ExperimentReadiness.ru.md).


## Текущее применение допуска — 07.11.2026

[Fair-domain stock Train](FairDomainStockTrainVerification.json) допущен и
полностью исполнен:8 preflight/8 Train,16 run manifests; все Train остановлены
InvalidObservation. Его полная диагностическая оценка64 проб уже получена на
сервере, но весь worker с render ещё работает; закрытая первичная публикация
оценки и visual QA ожидаются. Это не повод повторять Train или менять текущий
runtime. [Статус задания](FairDomainStockEvaluationJobs.json).

Обе серии используют исходную физику без дополнительной LTMembrane.
[Сравнение](FairDomainStockScientificReport-2026-11-07.ru.md) подтверждает расширение
покрытия Advance и неизменность728 Retry CSV, но не улучшение классификации.
Готовность конкретного отрицательного результата и общая рекомендация V2
остаются разными решениями.
