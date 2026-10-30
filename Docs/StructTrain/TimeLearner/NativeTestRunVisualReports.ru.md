# Полное покрытие native test run графическими отчётами

Рабочий подэтап этапов 5/9/11. Приёмка всего исходного плана остаётся открытой.
Адаптер `native_test_reports.py` предназначен для артефактов native fixtures,
а не заменяет production runner экспериментов или матрицу физических моделей.

## Контракт покрытия

`specs/repeat-boundary-native-v1.json` объявляет точные 51 test ID, 26 фаз и
52 отдельные пробы текущего repeat-boundary A3. Это контракт конкретного набора
fixtures с Core `7b5939c5744877ba1a762393d78f7183853fd5c0`, не универсальное
ожидание от любого будущего запуска. Изменение состава fixtures требует
проверенного обновления контракта. Ожидаемое множество не выводится из наличных
файлов, иначе полностью пропавшая фаза могла бы остаться незамеченной.

Для каждой фазы проверяются исходный summary, число `reference_probes +
search_probes`, непрерывные номера recorder от 1 до этого числа, отдельные
packet/CSV и уникальность trial ID внутри выполнения. Warm continuation
содержит только заново предъявленные пробы; сохранённые references не выдаются
за новые наблюдения. XML producer использует `_xmlprobe_`, не `_service_`.

Дополнительно включены все frozen, paired import, rollback и fresh-process
пробы. Для fresh process исходный packet находится в `/probe` общего JSON:
сохраняются оригинальный wrapper, JSON pointer и hashes обоих первичных файлов.
Повтор используемого importer trial ID в другом процессе не означает одну
общую пробу: исполнения имеют разные группы. ID и measured values не меняются.

Проверка требует точного множества прошедших JUnit cases без skipped/error/
failure и полного учёта всех native probe packets, embedded `/probe` и CSV.
Случайный orphan CSV, пропуск последнего packet или целой фазы запрещает
создание положительной записи покрытия. Numeric/context validation использует
production probe loader, включая явную partial policy. Неполные данные
сохраняются диагностическими; полнота списка файлов не доказывает полноту окон.

## CLI и выходные данные

```text
python3 -m Scripts.StructTrain.TimeLearner report \
  Scripts/StructTrain/TimeLearner/specs/repeat-boundary-native-v1.json \
  --format native-test-run --artifacts /immutable/readback \
  --output /new/report
```

`readback` содержит `native.xml` и плоский `native/` с исходными файлами.
Выходной каталог должен отсутствовать. До рендера проверяется весь контракт.
Сохраняются исходные native artifacts, JUnit и переносимые probe-set specs.
Каждая фаза получает отдельный набор с общими Y limits для соответствующей
сомы. Импорт в другом процессе получает отдельную группу; модель и условия
показаны в первичных пакетах и manifests. Обзорный index ведёт к индивидуальным
полноразмерным PNG/SVG/PDF с временными zoom и подписанными detail Y views.

Inventory различает известные и потенциально рисуемые trial/soma пары.
Фактическое число `rendered_trial_soma_pairs` записывается только после рендера
и сверяется с inventory. Raw hashes, completeness и источник каждого packet
остаются доступными. `scientific_verdict=null` и
`visual_acceptance_complete=false`: одни автоматические checks не заменяют
визуальный просмотр. Единицы остаются model units / SI unverified.

## Проверки текущей реализации

Первый inventory gate `b6abe895883be8b374e0bd44c700202819e0579e` прошёл 6/6
адресных tests на обоих workers без skips/errors/failures. Реальные A3 artifacts
дают 78 групп и 338 проб на worker. Отдельные повреждённые копии проверяют
удалённую фазу, последний packet, orphan CSV, потерянный embedded fresh-process
packet, дублирование источника и skipped JUnit case. Это проверка каталога,
не доказательство наличия всех итоговых рисунков. Полный CLI render текущих
A3 данных и его визуальная приёмка ещё требуются.
