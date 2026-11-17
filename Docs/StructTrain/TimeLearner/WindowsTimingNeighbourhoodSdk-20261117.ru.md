# Windows: параллельная сборка N1 timing-neighbourhood

## Закрытый SDK a2: 218/218 C++ cases

Компиляция и линковка завершились с0 за2223.17с. Исходный build outcome
сохранён отрицательным (`descendants_remaining`, дочерний PID9480);
backend закрыл всю группу. Kernel Job отсутствует. Отдельный closed-build
audit прошёл:4635 исходников,8 repositories,17287 dependency files,62 runtime
files; original main/Job отсутствуют до и после.

Затем `windows-timing-neighbourhood-native218-a1` выполнил **218/218**
заявленных случаев, без failures/skips/missing. Process exit0, wall2.4704с,
cooperative capture завершён, проверены47 загруженных файлов, descendants
нет и native Job отсутствует. Прошли обе новые C/N1 регрессии, исходный
no-op C-context case и timing-neighbourhood / candidate-pair budget cases.
Controls native `b73a3892021615e0ef7a55825c77e1850d4f5d69`, audit
`81714503311989d99b78495308363a0d314b853e`.

Получены все71 primary files:218 JUnit IDs и bytes/SHA каждого файла
проверены локально как метаданные. Архив2127425 байт, SHA256
`889f2fd56f51b2e35de3c50168e4a78bbb2217c1483d600deb7c39ff4a222da9`.
Публикация этого пакета в M40 archive **пока не подтверждена**: VPN отключился,
вход сохранённым Automats2 отклонён с691. Не подменять локальную копию
проверенным внешним object reference.
[Компактный readback](../../../Reports/StructTrain/TimeLearner/WindowsTimingNeighbourhood-20261117/native218-readback.json).

Это адресная приёмка Windows cohort на Root93894dd / Pulse52cb953.
Linux219 ещё не выполнен, actual cold A/B и8-pattern Test нового алгоритма
не выполнены. Полный допуск Windows scientific worker не объявлен.
Новый byte-source parser находится в другой ветке и этим SDK не проверен.

## Историческое наблюдение нового SDK a2

На22:04UTC fresh SDK build a2 подтверждён через Windows kernel Job:
7 active processes, log7/534. Root `93894ddfac0b0cf25fb5e87c4e2de3813d17587a`,
Pulse `52cb953c3dd153b8b3e5459ea9b54825e05a89a8`; все4635 файлов/8 repos
сверены. Controls `3be359ac942f90a65ac0447bf30137fd45fe50fa`, namespace
blob `5a988c330f53c84f88c0c77a962fa5505da7f63b`, spec
blob `73dbd635278f31ddf3096a13a92dc61f67da102e`.
Используются новые source/build/runtime с суффиксом `timing-neighbourhood-win-a2`.
Исходные a1 и все отрицательные попытки сохранены. Политика и квоты сборки
не изменены. Заявлены218 cases; исходник и guard единственного Linux-only
исключения проверены при подготовке, его SHA включён в controls/cohort.json.

[Подготовка](../../../Reports/StructTrain/TimeLearner/WindowsTimingNeighbourhood-20261117/preparation-a2.json),
[dispatch](../../../Reports/StructTrain/TimeLearner/WindowsTimingNeighbourhood-20261117/dispatch-a2.json),
[фактический Job/log](../../../Reports/StructTrain/TimeLearner/WindowsTimingNeighbourhood-20261117/build-a2-observation.json).
Это выполняемая сборка, не C++ PASS или scientific-worker admission.

## Закрытые результаты и найденные дефекты

Сборка завершена: compiler/linker returncode 0, wall 2477.58с. Исходный
build outcome **не принят** (`descendants_remaining`); backend закрыл
оставшийся дочерний процесс. Отдельный production closed-build audit прошёл:
4635 исходников, 8 репозиториев, 17287 dependency files и 62 runtime files
проверены, старый Job отсутствует до и после. Это независимая проверка
артефактов, а не изменение исходного отрицательного outcome.

Native attempt a1 не запустил C++ из-за недостатка доступной памяти.
Причиной расхода около 25.7GB был наш старый PowerShell observer. Он остановлен
только после сверки PID, creation time и script hash; остальные процессы не
останавливались. Повторное наблюдение использует короткий bounded kernel API
observer. После освобождения памяти отдельный native a2 выполнил 216 случаев:
215 прошли, один упал. Все четыре новых случая timing-neighbourhood / нечётного
probe budget прошли. Gate целиком **не принят**: ожидалось 217, однако symlink
case закрыт `#ifndef Q_OS_WIN`; дополнительно упал C-context case.

Windows cohort следующего SDK должен явно исключать только
`NativeJobSourceTransport/SymlinkSourceCannotReplaceTheOwnedSnapshot`
с hash исходника и guard. В Linux он остаётся обязательным.
Нельзя исключать упавший C-context case. Исправление его no-op fixture и
два отдельных production regression cases описаны
[здесь](N1CapacitanceCandidateAdmission-20261117.ru.md). Новый код ещё не проверен.

[Компактные результаты и проверенная внешняя ссылка на raw JUnit/readbacks](../../../Reports/StructTrain/TimeLearner/WindowsTimingNeighbourhood-20261117/closed-build-and-native-observation.json).
Полный набор raw квитанций хранится на M40 в каталоге
`experiments/2026-11-17/windows-timing-neighbourhood/a1.json` внешнего архива.
Windows scientific worker не принят. Работающие Linux Train не менялись.

## Историческое наблюдение подготовки на 20:25 UTC

На20:25UTC новая сборка на user@10.245.1.14 (RYZEN7-5825U) действительно
выполняется: именованный Windows Job открыт через kernel API, active_processes7,
native stdout дошёл до76/534 шагов. Это подтверждение процесса, не приёмка
сборки, C++ тестов или научного worker. На Elder и M40 продолжаются прежние
два cold Branch; их исходники, runtime и бюджеты не менялись.

Сборка относится к exact Rootddb2dcadd33ddd683cf73662f306c2bc6383e325,
Pulseeb5c07b0bd56897e4b67d2e644d066ee6340fe11. Она включает два пока
непроверенных изменения: N1 исследование соседних длин после timing-ready
amplitude miss и отказ от нового candidate/domain/edit при одном оставшемся
probe. CapturedPerInput, исходные допуски и физика сохранены.

Проверены4635 физических исходных файлов и восемь репозиториев; HEAD/gitlinks,
чистота tracked tree, отсутствие alternates/reparse и byte hashes соответствуют
переданным Git object projections. Namespace Git blob
a84081e2b48ffd173d2b9a01fe3ecaf675528d21; build spec blob
29deccb051b9083ad35ee945dedeb7a09f0e530f; controls
00698d26cbda89b56f0aa5c78bdec13c049df4e6. Exact namespace совпадает с
подготовленным M40 SDK a2; никакой копии пользовательского рабочего дерева нет.

Использованы только новые каталоги под C:/Projects/TimeLearnerWorker:
source-timing-neighbourhood-win-a1, build-timing-neighbourhood-win-a1,
runtime-timing-neighbourhood-win-a1 и jobs/windows-timing-neighbourhood-sdk-build-a1.
Пользовательский C:/Projects/Nmsdk и прежние runtimes не изменялись.
Dispatch — TimeLearner-windows-timing-neighbourhood-sdk-build-a1,
Job Local\\TimeLearner-54e18cee-4633-4fa6-b25a-f3266deacedf.

Неизменённый production sdk-build.py использует Release/Qt5/MSVC18,
один compiler job,4GiB committed Job memory,32 процесса и7200с wall budget.
Зависимости берутся из прежнего проверяемого vcpkg_installed, их установка
отключена. VSCMD_SKIP_SENDTELEMETRY применяется только внутри owned batch.

Неудачи подготовки сохранены отдельно. Большой stdin transfer завис до
создания SDK; остановлен только его reader с проверкой точного script hash
и PID identity. Затем те же Git-объекты доставлены SFTP; передавались только
кодовые Git packs, не данные моделей или результаты экспериментов. Проверка
модуля сначала отказала из-за политики unsigned PowerShell scripts, до сборки.
Повторная проверка точного Git-модуля использовала process-local policy;
системные настройки не менялись. Предыдущий controls commit1410eadc сохранён.

Квитанции: [подготовка](../../../Reports/StructTrain/TimeLearner/WindowsTimingNeighbourhood-20261117/preparation.json),
[dispatch](../../../Reports/StructTrain/TimeLearner/WindowsTimingNeighbourhood-20261117/dispatch.json),
[kernel Job и native log](../../../Reports/StructTrain/TimeLearner/WindowsTimingNeighbourhood-20261117/build-observation.json).

На момент этой подготовки после закрытия требовались проверка build outcome и полного Job,
независимый closed-build audit, затем declared217 literal production TEST
cases через штатный Windows gate. Legacy TEST_F physical fixtures за пределами
этого cohort не считаются пройденными. Если build вернёт descendants_remaining,
сохранить отрицательный outcome; последующий audit не переписывает его.
Windows gate не заменяет обязательный Linux gate217 и настоящие cold/frozen8
опыты. Этапы1–12 полного плана остаются частичными.
