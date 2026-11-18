# Статус TimeLearner — 18 ноября 2026

Полная цель0–12 возобновлена. Принят этап0, этапы1–12 остаются частичными;
научные8/8 не являются условием завершения. VPN восстановлен: фактический
доступ к Elder, M40 и Windows .14 через .12 подтверждён.

## Закрытый cold cap16 на M40

`s10-finite-fair-input-cold-m40-a4`: обе native группы и исходный controller
закрыты, lease освобождён. Native processes exit0, loaded-files capture завершён;
manifests execution=completed/validity=valid. Обе модели BudgetExhausted,
сертификата нет. Это не завершённое успешное обучение.

| Топология | Измеренные кандидаты | Группы / native пробы | Причина |
|---|---:|---:|---|
| Classic |21|47 /281|Group wall deadline; terminal graph мог остаться без законченного измерения|
| Branch |51|108 /645|Общий wall deadline; all-input gate не завершён|

Classic native process7298.40с, Branch22024.05с. Wall time не равно model time.
Сохранены фактические состояния и полная история; лучший scalar из истории
не подменяет terminal model. Классификация этих моделей ещё не оценена.
DATA-reader не объявляет native proof replay или общую сходимость по exit0.
[Readback](../../../Reports/StructTrain/TimeLearner/FairInputCold-20261118/closed-readback.json).

Lossless collection завершена за107.54с и опубликована:3040 regular files
и2 log aliases,3049956373 expanded bytes,2 дерева/3 закрытых units, controls
`19a270cb64fb59aff7c743f1ce734f8f770a39dc`. Primary48281492 bytes, SHA
`64c3db050e205f4e78e89c9be4a12c8e016c1da05f53e88afd4c4a158f7613a8`,
catalog `experiments/2026-11-18/fair-input-cold/primary-a1.json`.
[Проверенные ссылки на полный корпус и provenance](../../../Reports/StructTrain/TimeLearner/FairInputCold-20261118/primary-publication.archive.json).
Далее требуются actual frozen8 Test и читаемые Soma/input временные графики.

## Elder продолжает прежний single-sweep

`s10-single-complete-sweep-branch-elder-a3` подтверждён running. Получены698
полных raw JSON packets; выполнялась117-я composite группа, epoch54.
Это промежуточный prefix. Последнее подтверждение running —04:08UTC,
свободно2.869GB. Runtime и budgets не менялись.

## Windows: реальные физические проверки

На Root93894dd/Pulse52cb953 завершён `windows-timing-neighbourhood-native-burst8-a1`:
**8/8 PASS**, без skips/missing, wall73.48с. Реальные Classic/Branch bursts,
2000/20000Hz и N4/N6 на2000Hz, штатный scheduler. Exit0, потомки закрыты,
47 actual loaded modules, kernel Job отсутствует.
[Readback](../../../Reports/StructTrain/TimeLearner/WindowsTimingNeighbourhood-20261118/native-burst8-readback.json).
Full primary опубликован и byte-exact проверен на M40:67 файлов,18 actual CSV,
777433 bytes, SHA `fb9f40baf154f0b88eacf8a9ed7d135e0ee9af349981f8c1c4bd6f1a3aa0656f`,
catalog `experiments/2026-11-18/windows-native-burst/a1.json`. Графики ещё впереди.
Это не классификация или полный допуск Windows scientific worker.

Предыдущий Windows218 primary теперь опубликован и перепроверен на M40:
71 файл/218 JUnit cases,2127425 bytes, SHA
`889f2fd56f51b2e35de3c50168e4a78bbb2217c1483d600deb7c39ff4a222da9`,
catalog `experiments/2026-11-17/windows-timing-neighbourhood/a2-native218.json`.
Отрицательный исходный build outcome сохранён; subsequent audit/gate имеют
свои результаты. [Readback с CAS ref](../../../Reports/StructTrain/TimeLearner/WindowsTimingNeighbourhood-20261117/native218-readback.json).

## Перенос крупных моделей

Малый byte-parser kernel остановился до компиляции: в controls указан Qt5Core,
которого нет на M40; установлен Qt6Core6.4.2. Ни один из4 C++ cases в этой
попытке не запускался. Исправленный wrapper с явно объявленным Qt6 и сверкой
actual toolchain прошёл следующий отдельный gate, описанный ниже.

Новый isolated SDK Root `a9006c710806f03ae8d0d97d010291657bb7e836`, Pulse
`c54d9c0a65ac6eadeccfe1793672b7a9472ea559`, controls
`4862918b7f8c13296b9b37ae34b9d857d5027e4d`: canonical preparation прошла,
её process/lease закрыты. Сборка228-case gate остановилась на новом fixture:
const UEPtr не поддерживает неявный upcast к UContainer;0/228 cases выполнено.
[Failure и scope исправления](../../../Reports/StructTrain/TimeLearner/PhysicalModelDataSdk-20261118/build-a1-failure.json).
Root be5f6cf3d58b46405465b060d12fd362b025f986 добавляет явный upcast через
Get(), без изменения проверок или production алгоритма. С ним попытка a2 на Root
`944f7dd34bbe538346e20a183fb56d2cb5153bd0` / прежнем Pulse c54,
controls `908b24852d9c57d081238d40f68a27b7c7f97d5f`. Её canonical preparation
прошла; Console и StorageComponents собраны. Выполнены228 случаев:226 PASS,
2 новых roundtrip cases отказали до пробы с native model-repair guard.
[Закрытый readback](../../../Reports/StructTrain/TimeLearner/PhysicalModelDataSdk-20261118/native-a2-readback.json).
Новый fixture не задавал target-owner ControllerConfiguration, обязательную
для штатного Version2 Build. Root f1b8ae9aea9c2ebdc95ca6d1b9e4e243fddcbc19
передаёт сохранённую декларацию до Init и отдельно проверяет обе причины
ошибок owner. Исправление ещё не проверено; полный gate не принят.
Новая попытка a3 выполнена в отдельном source/build/runtime на Root
`445c834fe00b81f07857f5622809349e01bd1841` / прежнем Pulse c54. Её canonical
preparation прошла за135.03с. Console и тесты собраны,228 случаев выполнены,
226 прошли. Model-repair guard больше не срабатывает: обе полные source/target
трассы совпали,601 отсчёт. Единственные отказы — valid=true для исходного
и восстановленного наблюдения с одинаковым `peak_ambiguous:input0`.
[Readback a3](../../../Reports/StructTrain/TimeLearner/PhysicalModelDataSdk-20261118/native-a3-readback.json).
Root3dce4532db40a5b14623a403e08437d8e1ca7bbc исправляет именно неверное
требование fixture: сверяются полные observations и одинаковая диагностика.
Неоднозначность не превращается в успешное измерение; физика/окна/порог не
изменены. Правка пока не проверена; весь228 gate и новый формат не приняты.
Используются2 compiler jobs/8GiB, штатный CMake Qt6. Старый prepared219
superseded без запуска;228 содержит все его случаи и9 новых. Native228 PASS
и измеренное снижение RSS ещё не получены.

После gate необходимы полные saved-state imports и actual8-response Test.
[Model DATA](PhysicalModelData-20261118.ru.md) и
[terminal best-state](TerminalBestStateBoundary-20261118.ru.md) остаются
открытыми пунктами5/7. Feature changes пока не объединены в develop.

До actual Branch Test обнаружен ещё один transport blocker: сохранённый
summary167249672 bytes больше прежнего compressed-summary ceiling128MiB.
В recorded_diagnostic_matrix подготовлен case option
`maximum_summary_raw_bytes`: прежний default128MiB, явный потолок не более1GiB,
полные raw bytes/SHA и compressed frame обязательны; свыше128MiB требуется
отдельно объявленная owner memory не менее16GiB. Для этого корпуса достаточно
256MiB. Legacy uncompressed64MiB путь сохранён. Это лимит чтения данных,
а не изменение научного условия или сокращение истории. Новая declaration
регрессия, exact-boundary чтение и closure joins прошли в25/25 Python cases;
там же actual production parser4 прошёл на объявленном Qt6Core6.4.2.
[Readback](../../../Reports/StructTrain/TimeLearner/LargeSummaryTransport-20261118/closed-readback.json).
Это DATA/codec проверка; далее нужен
реальный импорт167MB summary и обеих полных моделей.

## Следующий фактический Test

Обе terminal-модели cold cap16 и summaries уже потоково сжаты без изменения
исходных bytes, привязаны к SHA и сохранены в CAS M40. Все шесть входов,
включая исходную PhaseA matrix, занимают48814736 bytes. Controls
`9b39e59367719c11d80c5809cd876afe0e851e62`, каталог подготовки
`TimeLearnerRefactor/requests/fair-input-cold-matrix-a1`.

Запущен declared diagnostic —16 native pattern trials: все8 паттернов для
каждой фактически сохранённой модели, полные2с/reset-per-trial, исходный
порог100. Job `s11-fair-input-cold-matrix-m40-a1`, controls
`918481bdeb23c0b0779a13d3bda08b1591860a70`. Используется существующий
полный source importer и Console SDK a3, fingerprint
`c9e6acf35f2b59fe9ee6f4b0033d11d285a242672e557e6c8452cf6490b673b3`.
Новый physical-model DATA путь не используется. Полный SDK gate остаётся
отклонённым; разрешён только этот диагностический прогон существующего пути,
с сохранением обоих известных отказов fixture. Это не приёмка нового формата,
не новый Train и не разрешение на develop merge.

Закреплены checked-file-source-v1 и явные лимиты source/summary:1GiB/256MiB,
owner16GiB + native16GiB. [Controls и CAS](../../../Reports/StructTrain/TimeLearner/FairInputCold-20261118/matrix-preparation.json).
Подбор порога — отдельный Same-Matrix experiment
с реальным повторным прогоном кандидата. Оценка не подменяет BudgetExhausted
на завершённый Train и не переносит scalar best в сохранённую модель.

По readback04:41UTC Classic уже выполняется в отдельном native Console
cgroup; окончательные8 наблюдений ещё не получены. Python controller прошёл
первоначальную проверку полного источника, peak memory около4.06GB, OOM нет.

## Параллельная проверка на Windows .14

Новый Root `03d05059f45bcc149c98aa51ec6937ace3b0ac73` / Pulse c54 доставлен
через Git object projections:8 репозиториев,4644 файла,23.46MB pack. Все
файлы и gitlinks сверены. Controls `a3be8be9c9ca5bfb2f98bb5596fa1821f75ba6c3`.
В отдельном `C:/Projects/TimeLearnerWorker/source-physical-model-data-win-a1`
запущен `windows-physical-model-data-sdk-build-a1`; kernel Job подтверждён
active04:42UTC, compiler MSVC19.51.36260.0. Подготовлен227-case Windows
inventory; Linux-only symlink case явно исключён по исходному `#ifndef`.
Пока это сборка,0/227 новых tests выполнено. После закрытия нужны build audit
и actual native gate. Новый формат, полный Linux228 и scientific admission
Windows остаются непринятыми.
[Квитанция подготовки и dispatch](../../../Reports/StructTrain/TimeLearner/WindowsPhysicalModelData-20261118/preparation.json).

M40 Linux SDK a4 подготовлен только как immutable source/controls, без запуска;
он не отнимает slot у фактического Test. Elder продолжает прежний Train.
