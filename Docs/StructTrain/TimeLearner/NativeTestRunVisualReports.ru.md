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
Выход обязан находиться вне immutable readback: запись внутрь исходных
артефактов запрещена до создания любого файла, в том числе во избежание
рекурсивного копирования output внутрь самого себя.
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

Объединённый readback `b2f357bcc75264a233524bfb30153b5d95816d6c` прошёл
92/92 tests на каждом worker без skips/errors/failures. Опубликованные commits:
Elder `a19ece3191c0c1fd3693bf09cad89a3f0b2b69b9`,
M40 `66e9d7ea225419ecbf470e8eb924cdbbec4f5f9a`.
Inventory различает 507 известных/рисуемых пар на worker и полноту наблюдения:
частичные trials не превращаются в complete. Полное построение A3 графиков
запущено отдельно на Data-диске M40 из Git-пакетов обоих producers, без новых
native расчётов. Результат рендера и последующего readback здесь пока не принят.

Последующее завершение исполнения: оба full render и зависимый readback
завершились с process status 0. Для каждого producer построены все 338 проб /
507 trial–soma пар; проверены 12925 nested stored hashes. Reader
`fb01871cf2158ece735ab45e148fc20fc33594cd` выполнил по 10/10 addressed tests
на каждом наборе, без skips/errors/failures: семь catalog/immutable-input controls
и три полных readback checks. Эти проверки сравнивают каждый packet/CSV с
оригиналом, проверяют все 507 наборов figures, PNG dimensions, zoom scale,
vector exports и hashes всех файлов. Изменений физики или нового обучения нет.

Git-публикация выполнена fail-closed после успешного readback:
Elder `03d02cd5abb6923274fb83cd17361cc591a3666f`,
M40 `bd79b0d31724f7230d658bcbc70bccdb5a0bdb25`.
Каждый внешний пакет содержит 12954 stored hashes и около 684 MB исходных
данных/рисунков. Вложенный portable report копируется без преобразования,
включая исходные native logs: изменение их формата нарушило бы вложенные hashes.
Шесть PDF каждого набора имеют Poppler previews с source hashes. Их локальная
визуальная проверка и итоговый develop merge пока не заявлены.

Последующая scoped visual проверка записана в
[NativeTestRunVisualReview-2026-10-30.json](NativeTestRunVisualReview-2026-10-30.json).
Шесть Elder previews открыты с original detail; все шесть M40 previews
побайтно совпадают с ними. Overview показывает actual pulses и полный ответ,
peak zoom — форму пика; в выбранном peak-only tile onset лежит в соседнем
фрагменте и overview. Partial tail остаётся явно неизвестным. Это не просмотр
всех figures и не human/global visual acceptance.

После вопроса об объёме пользователь выбрал компактный Git. Большие полные
ветки 03d02cd/bd79b0d сохраняются как уже опубликованные, но не объединяются
в source develop. Вместо них приняты компактные primary bundles с выбранными
PNG; полные reports — воспроизводимый M40 cache. См.
[CompactArtifactBundles](CompactArtifactBundles.ru.md) и
[аудит объёма](ArtifactStorageAudit-2026-10-30.ru.md). Научные данные не удалены.
