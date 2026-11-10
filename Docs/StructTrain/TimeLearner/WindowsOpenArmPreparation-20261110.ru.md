# Подготовка третьего worker: Windows .14, 10.11.2026

Цель — подготовить актуальную отдельную сборку для независимых native-проверок и последующего допуска экспериментальных заданий. Windows не заменяет обязательную приёмку на Elder и M40. Полный научный worker пока не принят.

## Зафиксированные условия

- Доступ по ключу user@10.245.1.14 подтверждён; hostname DESKTOP-RV8IOD6. Перед подготовкой процессов Nmsdk/компилятора и активных TimeLearner Scheduled Tasks не обнаружено.
- Свободная память перед подготовкой: 8,555,384 KiB; свободный диск C: 1,758,501,629,952 bytes. Это моментальное наблюдение, не резервирование. Backend повторно проверяет условия допуска.
- SDK: Root `8ec5ec265a5995df75e35cebdb78aab5e89dcfe3`, Pulse `165d49da7e65cd6ac59bca2812ce52884ddd50c2`, Rdk `de4134235c0dcb8b91fd9a43b267348ad1a163ca`, Bin `8cb6dba07b30432272984c8ce3136b48ad06f064`. Тот же C++ subject, что в текущих Linux119.
- Новая независимая source-копия: `C:/Projects/TimeLearnerWorker/source-branch-open-arm-order-win-a1`; пользовательский C:/Projects/Nmsdk не изменяется. Источники передаются Git pack, HEAD и точные gitlinks проверяются; существующие сборки не обновляются.
- Полный namespace: 4078 файлов / 8 Git repositories; [план и исходные file hashes](ValidationPlans/WindowsNative119OpenArm-20261110/preparation-plan.json), [спецификация сборки](ValidationPlans/WindowsNative119OpenArm-20261110/build-specification.json).
- Новый build/runtime/output; VS2026 x64, Release, Qt5, LLM/OpenCV/Python/ODEsolver Off, один compiler job. Targets: NeuroModelerConsole и Test_PulseLib_StorageComponents. Физика нейрона не изменяется.
- Штатный Windows Job backend: 4 GiB committed memory, максимум32 processes,7200 s wall; отдельный lock. Build admission не равен scientific admission. Сохраняются original execution/validity/whole-Job closure.

## Предварительные остановки подготовки

Новые модели не запускались. Первый локальный transport wrapper неверно раскрыл PowerShell-переменные; создание каталога не состоялось. После исправления Git pack был доставлен, но импорт штатного GitPreparation.psm1 остановлен process execution policy. Для следующего запуска выбран только process-local ExecutionPolicy Bypass; постоянные настройки машины не менялись. Успешный root checkout создал пустые gitlink directories: первоначальный запрет любого существующего пути остановил подготовку до child init. Следующий wrapper разрешает только существующий пустой обычный каталог; другие содержимое/reparse пути по-прежнему запрещены. Root не пересоздавался и не удалялся.

## Приёмка и оставшиеся действия

Доставка и полная сверка SDK выполняются. Runtime build ещё не принят. После сверки namespace — свежая bounded сборка; после terminal результата — проверка целостности и полного закрытия процессов. Сохранить исходные отрицательные результаты, если остаются descendants. Native запуск возможен лишь через действующий production gate и точный audited runtime.

При подготовке native заданий не считать наличие бинарника научным допуском. Требуются exact test inventory, actual loaded DLL identity, полные наблюдения, source/runtime preservation и Job closure. Console Train→Test, независимые научные условия, cross-platform численные сравнения и публикация полных compact primary остаются отдельными проверками.
