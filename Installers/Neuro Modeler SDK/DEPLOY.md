# Развёртывание Neuro Modeler на Windows

## Требование: Visual C++ Redistributable

Для запуска Neuro Modeler на целевой машине Windows необходим **Microsoft Visual C++ 2015–2022 Redistributable (x64)**.

- Сборка с пресетом **localqt** (Qt 5.15.2 из `C:\Qt\5.15.2\msvc2019_64`) соответствует инструменту **VS2019**; на целевой машине должен быть установлен пакет, содержащий runtime 14.28.x.
- Рекомендуется установить официальный пакет «Visual C++ 2015–2022 Redistributable (x64)» с сайта Microsoft.
- Ссылка на загрузку: https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist

**Важно:** для сборки под развёртывание с локальным Qt 5.15.2 (msvc2019_64) используйте **только** пресеты **win-vs2019-release-localqt** / **win-vs2019-debug-localqt**. Пресеты «VS2022 + локальный Qt 5.x» удалены: Qt 5.15.2 msvc2019_64 собран под VS2019 (v142), а проект под VS2022 — под v143; смешение CRT в одном процессе ведёт к падению на чистой Windows (APPCRASH в MSVCP140.dll). Исправление невозможно без перехода на VS2019 для всей сборки.

Для пресетов win-vs2019-*-localqt зависимости vcpkg (curl, boost, glog и т.д.) собираются с **триплетом x64-windows-v142** (инструмент VS2019, v142), так что все DLL в `Bin\Platform\Win` используют один и тот же CRT (v142), как и Qt из C:\Qt.

---

## Вариант без установки Redistributable: копирование CRT DLL

Если на целевой машине нельзя установить VC++ Redistributable, можно поставлять CRT DLL рядом с приложением. Распространение этих DLL допускается лицензией Microsoft VC++ Redistributable для целей развёртывания (см. официальную документацию Microsoft).

### Какие файлы копировать

Для сборки под **VS2019** (пресеты win-vs2019-*-localqt) нужны:

- `vcruntime140.dll`
- `msvcp140.dll`
- при необходимости `vcruntime140_1.dll`

Версия должна соответствовать сборке: **VS2019 → VC142** (каталог Microsoft.VC142.CRT).

### Откуда брать DLL

1. **Из установленной Visual Studio 2019**  
   Каталог вида:  
   `%VCINSTALLDIR%Redist\MSVC\<version>\x64\Microsoft.VC142.CRT\`  
   (переменная `VCINSTALLDIR` задаётся при запуске из Developer Command Prompt для VS2019; типичный путь: `C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\`)

2. **После установки VC++ Redistributable на машину разработчика**  
   Файлы можно взять из каталога установки Redistributable или из кэша установщика.

Используйте только официальный источник (Visual Studio или установленный пакет Redistributable).

### Куда копировать

1. **Для локального запуска и для последующей сборки установщика:**  
   Скопируйте указанные CRT DLL в каталог **`Bin\Platform\Win`** (относительно корня репозитория).  
   Тогда они будут рядом с `NeuroModeler.exe` при локальном запуске.

2. **При сборке установщика:**  
   Скрипт **prepare_installer_qt.bat** копирует все `*.dll` из `Bin\Platform\Win` в `InstallSourcesQt\Bin\Platform\Win`.  
   **Перед вызовом prepare_installer_qt.bat** при необходимости скопируйте CRT DLL в `Bin\Platform\Win` — они автоматически попадут в InstallSourcesQt и в установщик. Дополнительных правок в prepare_installer_qt.bat не требуется.

### Пример (командная строка)

Пусть CRT лежат в `C:\VC142.CRT`. Выполните из корня репозитория:

```cmd
copy /Y "C:\VC142.CRT\vcruntime140.dll" "Bin\Platform\Win\"
copy /Y "C:\VC142.CRT\msvcp140.dll" "Bin\Platform\Win\"
copy /Y "C:\VC142.CRT\vcruntime140_1.dll" "Bin\Platform\Win\"
```

После этого запустите подготовку установщика (например, из каталога `Installers\Neuro Modeler SDK`):

```cmd
prepare_installer_qt.bat
```

---

## Не-Qt зависимости (vcpkg)

Помимо Qt (из `C:\Qt`) и CRT приложению нужны DLL от пакетов vcpkg: **curl**, **boost** (program_options, thread, filesystem, system, chrono, atomic), **glog**, **python3** и их транзитивные зависимости (libssl, libcrypto, zlib, gflags и т.д.). **OpenCV** поставляется через vcpkg только при включённой фиче `opencv` (в манифесте по умолчанию отключена, чтобы избежать падения сборки opencv4 под triplet x64-windows-v142); при необходимости включите фичу и скопируйте opencv_*.dll в `Bin\Platform\Win`.

### При сборке

При сборке NeuroModeler или NeuroModelerConsole скрипт CMake **DeployVcpkgDlls** копирует в **`Bin\Platform\Win`** все DLL из `vcpkg_installed/x64-windows/bin`, **кроме Qt** (DLL с именами `Qt*` не копируются — Qt кладётся отдельно из C:\Qt). Таким образом, после сборки в `Bin\Platform\Win` оказываются все нужные не-Qt зависимости.

### Ручное копирование не-Qt DLL

Если каталог `Bin\Platform\Win` был очищен или сборка выполнялась без vcpkg, не-Qt DLL можно подставить вручную скриптом:

- **Скрипт:** `scripts\copy_runtime_deps_to_bin.bat` (вызывает `scripts\copy_runtime_deps_to_bin.ps1`).
- **Запуск:** из корня репозитория:
  ```cmd
  scripts\copy_runtime_deps_to_bin.bat
  ```
- По умолчанию берёт DLL из `build\vcpkg_installed\x64-windows\bin` и копирует в `Bin\Platform\Win` только не-Qt и не-debug DLL. Пути можно задать переменными окружения: `VCPKG_BIN_DIR`, `BIN_PLATFORM_WIN`.
- **Когда использовать:** после клона репозитория или после очистки `Bin\Platform\Win`, если полная сборка не выполнялась и нужно только подготовить DLL для запуска или для **prepare_installer_qt.bat**.

CRT DLL при необходимости по-прежнему копируются вручную (см. раздел выше).
