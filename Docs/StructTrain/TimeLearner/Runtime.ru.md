# Изолированный runtime

Каждая CMake-сборка по умолчанию пишет runtime в `<binaryDir>/runtime`.
`-DNMSDK_DEPLOY_ROOT=/absolute/path` выбирает другой изолированный каталог.
`-DNMSDK_RESOURCE_ROOT=/checkout/Bin` задаёт корень RTlibs/ClDesc/Configs отдельно.
Для прежнего размещения можно явно выбрать `<checkout>/Bin/Platform/Linux`.

CMake создаёт runtime `NeuroModelerConsole.ini` с абсолютными resource paths.
Console принимает `--app-ini /absolute/path/NeuroModelerConsole.ini` либо переменную
`NMSDK_APP_INI`. Без них используется ini рядом с executable, а при его отсутствии
сохраняется старый поиск относительно CWD. Пустой или несуществующий явно указанный
ini не должен подменяться другим файлом.

Работающие старые эксперименты не обновляются. Для приёмки нужны независимые
configure/build roots на сервере и проверка runtime размещения и ресурсов.
Runtime manifest должен фиксировать executable, loaded libraries, build flags,
source commits, effective ini и resource root; само наличие нового пути этого
manifest не заменяет.
