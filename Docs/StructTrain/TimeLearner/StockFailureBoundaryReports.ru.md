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
это не утверждение о полном молчании модели. Подтверждение wave arrays по CSV
и визуальная приёмка нового отчёта пока pending. Слияние конкретных откликов,
идентифицируемость выбранной волны и изменение политики поиска требуют
отдельного разбора. Недостающий пик нельзя восстанавливать прогнозом или
объявлять Exact после ослабления OrderedWholeBurst.

## Проверки и текущая граница

Добавлены реальные data tests: все4 source conditions, same-input selection,
отсутствующий predecessor, duplicate ID, повреждённый timestamp, ложный valid,
реальное позднее окно, one-tick negative и изменённая recorded wave. Report
readers проверяют все сомы, primary copies, общие оси, hashes, размеры1920×960,
наложение входов и читаемость native zoom. До выполнения на сервере это WIP.
Первый старый launcher без plotting venv и следующий отказ времени сохраняются
в evidence. Обучение, модели, пороги и исходные исторические результаты не меняются.
