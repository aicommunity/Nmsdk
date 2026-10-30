# Первый production renderer native recognition отчётов

Подэтап stage09/visual-test-reports объединён в develop:
398dabf684181cddccaa37cb221227a38ad64295. Это реализация части VisualTestReports.ru.md,
а не завершение этапов 9/11 или всей обязательной визуальной матрицы.

## Реализованный путь

`python3 -m Scripts.StructTrain.TimeLearner report evaluation.json.gz
--model model.json.gz --output NEW_DIRECTORY` принимает schema-1 evaluation
spec и полный recognition package. Новый каталог не заменяет существующий.
До рендера применяется production scorer: ожидаемые IDs, labels, модель,
timestamps и полнота анализируются тем же кодом, что в analyze.

Для каждой ожидаемой trial/soma пары строятся отдельные PNG 1920×960, SVG
и PDF: overview всего заявленного окна и последовательные zoom-панели максимум
по 100 native ticks. При данной ширине осей один tick на zoom занимает минимум
14 пикселей. Полная выборка сохраняется, decimation/interpolation отсутствуют.
Разрыв более 1.5 dt разделяет линии; censored хвост обозначается серой областью.

Синяя линия — фактический SomaN.SumPotential; оранжевая ступенчатая линия —
фактические samples общего generator input на собственной Y-шкале. Фиолетовые
вертикальные маркеры — зарегистрированные LT spike events. Порог не рисуется
на soma axis без доказанного соответствия сигналов. Общий вход не превращается
в N независимых каналов. Никакой вывод о сходимости не извлекается из рисунка.

Schema 1 recorder не содержит физического unit descriptor. Адаптер сверяет
пути $.Soma1..N с реальным сериализованным графом; Branch имеет одну сому.
Значения подписываются model units / SI unverified. Автоматическое переименование
в mV не производится. Требование проверки единиц для каждого физического
класса остаётся открытым.

Пределы Y общие для всех trials одного канала модели и включают отрицательные
значения и extrema. В manifest сохранены точные пределы и временные окна.
Переносимый index.html содержит ссылки на полный PNG/SVG/PDF и primary данные;
внешние CDN/server не нужны. В primary сохраняются все наблюдения, model и spec,
причём spec адресует соседние файлы. analysis.json воспроизводится из них.
Контрольные суммы всех файлов находятся в SHA256SUMS.json.

## Проверки и найденные ошибки

Первый scale gate d9ecf261a выявил пустой последний zoom при округлении
абсолютного времени 192 s; исправление 12d48355e не изменяет первичные timestamps.
Исходный провал двух tests (одна ошибка, process status 1) сохранён в report
78983e9354de71496b51bdb3d5be2da275790867; все четыре stored hashes проверены.
При просмотре PNG A2 обнаружено наложение второй строки legend на рамку;
исправление a7e37f6e9 резервирует дополнительное место над axes.

На source 12d48355e оба workers построили четыре контрольных профиля:
Classic N0 / Branch N1, high/low storage threshold, 16 trials и все 24
trial/soma пары. Source native observations — 127806a34, новых моделей не
обучали. Шесть scale/primary-roundtrip/coverage/hash/raster/vector checks source
41e24b3f7 прошли на каждом worker без skips/errors. Отдельный реальный report CLI
на Branch spiking profile завершился с status 0 на обоих workers.

A2 отчёты: Elder 2c46f04f6cd31ca1b46b0bfa004307c27214ccd3 (338 hashes),
M40 be7b8d5d784a482cccec14ae2db4e3510a194ee2 (343 hashes). Все локальные hashes
проверены; A2 имеет описанное наложение legend и не является финальной
визуальной приёмкой. A3 перестроил все четыре профиля через настоящий CLI
с исправленным layout; на обоих workers 6/6 checks без ошибок/пропусков,
process status 0. Reports: Elder 8188472cd3d36f00c698b1b531815e84b43f1731
(342 hashes), M40 8abf68a20c4abc03718b662ee4ed1e01b2dff6ee (345 hashes).
Все hashes проверены локально. Просмотрены Elder Branch spiking target overview
и M40 Classic Soma2 foil zoom-001/002: legend отделена от рамки, импульсы,
фронты, хвост и отрицательный свободный диапазон не обрезаны. Молчаливый
zoom-001 сохраняется рядом с zoom-002 с ответом. Это адресная PNG проверка;
общая visual acceptance, полный vector/PDF просмотр и матрица ещё не закрыты.

M40 использует отдельный /media/user/Data/TimeLearnerRefactor/plot-venv-a1,
не системный Python. Matplotlib 3.9.4; фактический pip freeze и bootstrap/install
logs сохранены в A2. Elder использует доступный серверный matplotlib; версия
записана в каждом manifest. Полный воспроизводимый dependency lock/runtime
для общей инфраструктуры ещё требуется.

## Открытые требования

Рабочее продолжение от 30.10.2026: ветка stage09/visual-series-and-detail,
implementation 1b9a41c3299b2f4b3fb653478a101f4419dce1ba, auditor
fd80b9ec43d8ac1d13c1163abf8a0d8414a5f127. Добавлены panorama для каждой
записанной сомы с исходным абсолютным временем и дополнительные local-detail
Y views, когда размах выбранного фрагмента меньше четверти общего диапазона.
Общий сопоставимый график всегда остаётся рядом; нормировки нет. Для границ
detail учитываются соседние bracketing samples. Пока проверки выполняются,
это не принятая замена перечисленных ниже требований.

Series timeline сохраняет фактические onset-to-onset и last-to-first stimulus
интервалы, порядок и policy boundary. Неизмеренные промежутки видны серым:
их нельзя интерпретировать как отсутствие ответа в ITI. Точный timestamp
физического Reset schema 1 не содержит, поэтому он остаётся null; зелёная
граница обозначает только заявленную reset-per-trial policy. Нельзя называть
полученную панораму доказательством continuous coverage при разрывах наблюдения.

На Elder первый прогон implementation 1b9a41c32 прошёл три scale/timeline
теста и построил Classic spiking report с восемью trial/soma парами, status 0.
На обоих workers запущена проверка четырёх профилей через настоящий report CLI
с auditor fd80b9ec4: на каждом worker прошли 16 адресных checks, ноль
skips/failures/errors, process status 0. Каждый пакет содержит четыре профиля,
16 trials и все 24 trial/soma пары. Новых native моделей не обучали.
Reports: Elder 7cb89e8e4b8554501ef19ed8e367d6af95835069;
M40 1e1ce1d85f7a297a31c04e57c4fad67750ef81ed. Все 398 hashes каждого пакета
проверены локально. Просмотрены Elder Classic spiking Soma2 series overview
и Soma1 trial-0 zoom-003-detail: легенды не перекрывают график, отдельный
Y-scale подписан, форму слабого хвоста можно сравнить с исходным shared view.
Это адресная PNG проверка, не полная visual/physics matrix или vector/PDF QA.
Подэтап подготовлен к merge; полный stage 9/11 остаётся незавершённым.

- Native continuous coverage/ITI/reset matrix и точные reset event descriptors.
  Actual-clock panorama и дополнительные detail Y views уже реализованы
  в описанном подэтапе; grey gap policy отдельно проверена synthetic control.
- Полные descriptors канала/единиц/routing из producer и проверка всех классов.
- Diagnostic coverage отсутствующего trial/канала, NaN и неподдержанной схемы
  с явной картой отсутствующих данных; текущий strict loader может отвергнуть
  такие данные до построения отчёта, что не равно готовому partial report.
- Реальные N>4, 20 kHz, все N0/N1/topology/physics режимы, отрицательный baseline,
  late FP, длинный tail, order/ITI и continuous/reset matrix.
- Просмотр финальных PNG и vector/PDF при целевом масштабе и фиксация визуальной
  приёмки. Существование файлов и шесть автоматических checks её не заменяют.
- Общий runner/report completeness/publisher gate и исторические adapters.

Поэтому manifest имеет status=diagnostic, visual_acceptance_complete=false
и evaluation_verdict=null. Исполнение renderer не доказывает новый научный
результат и не пересматривает августовские 4/8–6/8.
