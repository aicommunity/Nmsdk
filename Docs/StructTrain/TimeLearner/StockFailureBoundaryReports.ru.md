# Временные графики границы невалидного stock Train

Новая команда поддерживаемого корневого пакета:

```text
python -m Scripts.StructTrain.TimeLearner stock-threshold-study failure-report STUDY --output NEW_CACHE
```

STUDY — восстановленный каталог paired study с design/index, jobs, preflight,
source и четырьмя runs. Runtime manifest и code identity не передаются: модели
не запускаются. Сначала выполняется полный production audit исследования.
NEW_CACHE обязан быть новым каталогом вне STUDY. Полные PNG/SVG/PDF остаются
кэшем M40; в Git хранятся исходные данные, метаданные и выбранные оригиналы.

Для каждой из четырёх stock-условий Classic/Branch×0.0117/100 выбираются
последняя записанная невалидная проба и последняя предшествующая валидная
проба того же физического входа, если она существует. Порядок определяется
native sequence, ID должны быть уникальны. Не используются первая строка CSV,
первый доступный вход или предположение о наличии предшествующего успеха.
Если валидной пробы нет, это явно указано. Reference без search candidate
также явно отличается от измеренного кандидата поиска.

Отчёт сохраняет raw packet/CSV, actual terminal parameters, base/effective
revisions, recorded wave assignments, причины отказа, число стимулов и бюджет
invalid observations. Все записанные сомы показаны отдельно. Каждая пара
сравнивается с общими численными Y scales; доступны обзор и100-tick zooms,
без прореживания, с наложением фактических входных импульсов. Временные
пределы и исходные единицы не переинтерпретируются. Это training diagnostics,
а не Test всех8 паттернов; полный stopped-model eight-pattern отчёт отдельный.

## Исправление численного сравнения времени

В реальной Branch-пробе из proof
e5fa71d745119af0d818059f497dd226f4c7c25d окно начинается855.486s, длится1.8s,
записаны3601 samples. Прежний read_partial_probe сравнивал
`equal(end-begin, requested_end)`. Вычитание близких абсолютных величин
теряло точность и вызывало partial_requested_window_mismatch, хотя строгий
основной auditor использовал корректное абсолютное сравнение.

Теперь diagnostic reader также сравнивает `equal(end, begin+requested_end)`.
Используется прежний roundoff allowance native_evidence.equal. SyncTolerance,
амплитудные допуски и timestep не меняются. Проверка с изменением requested
window на один timestep должна по-прежнему отклоняться.

## Независимая проверка записанных волн

Для закрытой конечной CSV-пробы invalid status не превращается в valid.
Отдельная диагностика сверяет recorded wave arrays с реальными interior
plateaus: число, время начала/конца, raw potential и amplitude относительно
baseline. Детектор локальных максимумов механически выделен из строгого
основного auditor и используется обоими путями; математическая политика
определения пика сохранена. Неполные/нечисловые traces не используются для
whole-window counting. Изменённая recorded amplitude должна отклоняться.

В исходных Train100 JSON записаны3 волны при4 стимулах, с заметным потенциалом;
это не утверждение о полном молчании модели. Wave arrays подтверждены по CSV;
просмотрены8 выбранных overview originals. Слияние конкретных откликов,
идентифицируемость выбранной волны и изменение политики поиска требуют
отдельного разбора. Недостающий пик нельзя восстанавливать прогнозом или
объявлять Exact после ослабления OrderedWholeBurst.

## Проверки и текущая граница

Добавлены реальные data tests: все4 source conditions, same-input selection,
отсутствующий predecessor, duplicate ID, повреждённый timestamp, ложный valid,
реальное позднее окно, one-tick negative и изменённая recorded wave. Report
readers проверяют все сомы, primary copies, общие оси, hashes, размеры1920×960,
наложение входов и читаемость native zoom.
Первый старый launcher без plotting venv и следующий отказ времени сохраняются
в evidence. Обучение, модели, пороги и исходные исторические результаты не меняются.

На source root2b9f13a6c868e428e975252882067c9ee692d1fc прошли12/12 data/regression
checks на обоих workers без skips. На M40 CLI построил4-condition report:
20 probe/soma pairs и996 views;3/3 report readers прошли. Primary proof
e5fa71d745119af0d818059f497dd226f4c7c25d полностью сверён по1370 members.
Новые evidence2f9885d77b1e4a92c59b96875bc0b7cbea3f005d и
490998982c59367f39e7f3daa65a8028ee6069ea сохраняют7/84 primary members,
302 source hashes каждого worker и8 выбранных PNG; все независимо сверены.
Полный image cache находится на M40 в
`/media/user/Data/TimeLearnerRefactor/readbacks/s07-stock-failure-production-visual-a1/full-report-cache`.
Это повтор анализа одних исходных данных, не два независимых обучения.

## Замечание визуальной проверки и дальнейшее исправление масштаба

StockFailureBoundarySelectedOverviewReview.json фиксирует просмотр всех8 overview originals.
Общие оси и входы видны, Train100 не является молчанием: широкие terminal
волны отличаются от предшествующих четырёх. Classic сравнивает L3/Rs69.55M
с L54/Rs86M; Branch — активную точку14/Rs69.55M с15/Rs86M. Эти пары не
изолируют влияние одной длины или одного сопротивления.

При пороге0.0117 записаны12 положительных максимумов Classic и7 Branch.
У Branch вторичные максимумы около1.86e-5 заметно выше minimum1e-6, однако
общая шкала с отрицательным выбросом около−0.38 визуально скрывает их.
Существующий100-tick local view вокруг relative0.1945s имеет Y bounds
около−0.00517…0.000403: rebound занимает менее2 пикселей по высоте.
Горизонтальная читаемость сама по себе не обеспечивает вертикальную.

Добавляются отдельные measured-peak views: до10 реальных native samples
с каждой стороны максимума, явная local Y scale, исходные sample markers
и фактические входные отсчёты. Общие overview/100-tick plots сохраняются.
Пики заново определяются общим detector по CSV, без изменения физических
допусков, minimum amplitude или training validity. Дополнительная проверка
требует, чтобы реальный малый rebound занимал более половины высоты local
диапазона и соответствовал сохранённым samples.

На source root988d4bfb706f9a3e3520bb012a6fe93304baf4ef построен следующий
полный кэш: 20 probe/soma pairs, 1021 views, включая 25 новых локальных видов.
Четыре текущие report checks прошли без skips, в том числе проверка видимости
малого Branch-максимума и его реальных отсчётов. Все восемь прежних overview
PNG побайтно совпадают; старый кэш не изменён. Прежние 12 data checks каждого
worker повторно не запускались: побайтно сверены неизменные production selector,
auditor и diagnostic reader, а также AST класса тестов выбора проб. Эти guards
и ссылки на завершённые исходные проверки сохранены в reused-readers.json.

Новый proof bb0a5080aa5334647580264e4d78ca3726db14ea содержит 77 primary members,
302 source hashes и 12 выбранных PNG. Сверены все members, исходники и выбранные
оригиналы. Непосредственно просмотрены четыре новых detail PNG; прежние восемь
overview уже просмотрены и не изменились. StockFailurePeakDetailSelectedReview.json
принимает только эти выбранные виды, не весь кэш. Scientific verdict отсутствует.

Текущий полный кэш:
`/media/user/Data/TimeLearnerRefactor/readbacks/s07-stock-failure-production-visual-a2/full-report-cache`.
Выбранные оригиналы и сжатые данные находятся в Git:
[s07-stock-failure-boundary-m40-a2](../../../Reports/StructTrain/TimeLearner/s07-stock-failure-boundary-m40-a2/README.ru.md).

## Наблюдения для следующего алгоритмического контроля

| Условие | Предшествующий валидный кандидат того же входа | Терминальные параметры активного входа | Число волн: до → после |
|---|---|---|---|
| Classic, threshold 0.0117 | L=1, Rs=86 MΩ | L=1, Rs≈2.88007 MΩ | 4 → 12 |
| Branch, threshold 0.0117 | attachment=1, Rs=86 MΩ | attachment=2, Rs=86 MΩ; prefix=[2,2,2,1] | 4 → 7 |
| Classic, threshold 100 | L=3, Rs≈69.55126 MΩ | L=54, Rs=86 MΩ | 4 → 3 |
| Branch, threshold 100 | attachment=14, Rs≈69.55126 MΩ | attachment=15, Rs=86 MΩ; prefix=[15,15,15,1] | 4 → 3 |

В таблице валидность относится к измерению, не к сходимости. Все терминальные
окна закрыты; дополнительные положительные максимумы при низком пороге реально
есть в CSV и не являются floating roundoff. При высоком пороге видна широкая
ненулевая реакция с недостаточным числом отдельных максимумов.

maximum_invalid_observations=0 в этих jobs прямо предписывает остановку на
первой невалидной пробе. Повторный поиск и допустимое отклонение отдельного
неидентифицируемого кандидата остаются открытой задачей этапа 7. Точки проверки:
PulseLib Core/TimeLearner/BoundedTraining.cpp (Reject, NextDomainCandidate),
MeasuredLengthSearch.cpp (односторонний прогноз) и FinalVerification.cpp
(контекст измерения и независимый финальный gate).

Перед изменением порядка поиска требуется native-контроль с одинаковой
морфологией и отдельным изменением Rs: существующие соседние пробы изменяют
несколько параметров сразу. Прогноз длины не доказывает существование выбранной
волны. Нельзя считать ambiguous/missing сбоем интегратора без отдельного
подтверждения, объявлять PhysicalInfeasible по одному кандидату либо скрывать
малые пики повышением исходного minimum amplitude. Исходные этапы 1–12
остаются частичными; весь план этим подэтапом не закрывается.
