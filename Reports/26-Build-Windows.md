> **Historical report.** See [Docs/Overview/](../Docs/Overview/) for current documentation.

# Инструкция по сборке Nmsdk под Windows

## Требования

### Обязательные компоненты

1. **Visual Studio 2022**
   - Установите Visual Studio 2022 Community, Professional или Enterprise
   - Обязательные компоненты:
     - Рабочая нагрузка "Разработка классических приложений на C++"
     - Компонент "MSVC v143 - VS 2022 C++ x64/x86 build tools"
     - Компонент "Windows 10/11 SDK" (последняя версия)

2. **CMake** (версия 3.20 или выше)
   - Скачайте с [cmake.org](https://cmake.org/download/)
   - Добавьте CMake в PATH при установке
   - Или используйте установщик CMake, который автоматически добавляет его в PATH

3. **Git**
   - Необходим для работы с подмодулями проекта
   - Скачайте с [git-scm.com](https://git-scm.com/download/win)

### Опциональные компоненты

4. **vcpkg** (рекомендуется)
   - Менеджер пакетов для C++ зависимостей
   - Установка:
     ```cmd
     git clone https://github.com/Microsoft/vcpkg.git
     cd vcpkg
     .\bootstrap-vcpkg.bat
     ```
   - Установите переменную окружения `VCPKG_ROOT`, указывающую на директорию vcpkg
   - Интеграция с Visual Studio:
     ```cmd
     .\vcpkg integrate install
     ```

5. **Qt5** (если не используется vcpkg)
   - Qt5 должен быть установлен и доступен через CMake
   - Установите переменную окружения `CMAKE_PREFIX_PATH`, указывающую на директорию Qt5

## Подготовка проекта

### 1. Клонирование репозитория

```cmd
git clone <repository-url> nmsdk-git
cd nmsdk-git
```

### 2. Инициализация подмодулей

Проект использует Git подмодули для зависимостей. Инициализируйте их:

```cmd
git submodule update --init --recursive
```

Подмодули проекта:
- `Rdk/` - ядро системы
- `Bin/` - бинарные файлы и ресурсы
- `Libraries/Rdk-BasicLib/` - базовая библиотека
- `Libraries/Rdk-CvBasicLib/` - библиотека компьютерного зрения
- `Libraries/Rdk-HardwareLib/` - библиотека работы с железом
- `Libraries/Nmsdk-PulseLib/` - библиотека импульсных нейросетей
- `Libraries/Nmsdk-MotionControlLib/` - библиотека управления движением

### 3. Установка зависимостей через vcpkg

Если используется vcpkg, установите зависимости:

```cmd
cd %VCPKG_ROOT%
vcpkg install qt5-base curl opencv eigen3 zlib boost-program-options boost-thread
```

Или используйте манифест проекта (автоматически при сборке):

```cmd
vcpkg install --triplet x64-windows
```

## Сборка проекта

### Способ 0: Visual Studio 2022 через CMake Presets (Qt 5.15)

1. Убедитесь, что Qt 5.15.2 (msvc2019_64/2022) установлена и путь прописан в `CMAKE_PREFIX_PATH` (в пресете стоит `C:/Qt/5.15.2/msvc2019_64`).  
2. Откройте `CMakePresets.json` в Visual Studio → выберите Configure Preset:  
   - Debug: `win-vs2022-debug`  
   - Release: `win-vs2022-release`  
3. Build Preset в VS: `win-vs2022-debug` или `win-vs2022-release`.  
4. При необходимости задайте `VCPKG_ROOT` (по умолчанию `E:/vcpkg/scripts/buildsystems/vcpkg.cmake`).  
5. Запускайте сборку/установку из VS кнопками Configure/Build.

### Способ 1: Использование скрипта сборки (рекомендуется)

Самый простой способ - использовать готовый скрипт:

```cmd
build-windows.bat release
```

Для отладочной сборки:

```cmd
build-windows.bat debug
```

Скрипт автоматически:
- Проверяет наличие необходимых инструментов
- Инициализирует подмодули при необходимости
- Конфигурирует проект через CMake
- Выполняет сборку

### Способ 2: Ручная сборка через CMake

#### Шаг 1: Конфигурация проекта

Откройте командную строку разработчика Visual Studio 2022:
- Пуск → Visual Studio 2022 → Developer Command Prompt for VS 2022

Или используйте обычную командную строку и запустите:

```cmd
cd <путь-к-проекту>
mkdir out\build\win-vs2022-release
cd out\build\win-vs2022-release
```

Конфигурация с использованием пресета:

```cmd
cmake .. --preset win-vs2022-release
```

Или без пресета (с указанием генератора):

```cmd
cmake .. -G "Visual Studio 17 2022" -A x64 ^
  -DCMAKE_TOOLCHAIN_FILE=%VCPKG_ROOT%\Scripts\buildsystems\vcpkg.cmake ^
  -DCMAKE_BUILD_TYPE=Release
```

#### Шаг 2: Сборка проекта

```cmd
cmake --build . --config Release -j
```

Или откройте сгенерированный файл `Nmsdk.sln` в Visual Studio и соберите проект через IDE.

### Способ 3: Сборка через Visual Studio

1. Откройте Visual Studio 2022
2. Выберите "Open a local folder"
3. Укажите корневую директорию проекта
4. Visual Studio автоматически обнаружит `CMakePresets.json`
5. Выберите пресет `win-vs2022-release` или `win-vs2022-debug`
6. Нажмите "Build" или используйте меню Build → Build All

## Результаты сборки

После успешной сборки файлы будут находиться в:

- **Исполняемые файлы**: `Bin\Platform\Win\`
  - `NeuroModeler.exe` - основное приложение
  - `NeuroModelerConsole.exe` - консольное приложение

- **Библиотеки**: `Bin\Platform\Win\Lib.CMake\`
  - `rdk.static.qt.lib` - ядро системы
  - `Rdk-BasicLib.qt.lib` - базовая библиотека
  - `Rdk-CvBasicLib.qt.lib` - библиотека компьютерного зрения
  - `Rdk-HardwareLib.qt.lib` - библиотека работы с железом
  - `Nmsdk-PulseLib.qt.lib` - библиотека импульсных нейросетей
  - `Nmsdk-MotionControlLib.qt.lib` - библиотека управления движением

## Опции сборки

### Включение опциональных библиотек

Через CMake переменные:

```cmd
cmake .. -DRDK_USE_OPENCV=ON ^
         -DRDK_USE_PYTHON=ON ^
         -DRDK_USE_ODESOLVER=ON
```

Доступные опции:
- `RDK_USE_OPENCV` - включить поддержку OpenCV
- `RDK_USE_PYTHON` - включить поддержку Python
- `RDK_USE_ODESOLVER` - включить поддержку ODE Solver
- `RDK_USE_DARKNET` - включить поддержку Darknet
- `RDK_USE_TENSORFLOW` - включить поддержку TensorFlow

### Настройка путей к зависимостям

Если зависимости не найдены автоматически, укажите пути:

```cmd
cmake .. -DOPENCV4_PATH="C:\opencv" ^
         -DBOOST_PATH="C:\boost" ^
         -DANACONDA_PATH="C:\Anaconda3"
```

## Решение проблем

### Ошибка: CMake не найден

**Решение**: Установите CMake и добавьте его в PATH, или используйте полный путь к cmake.exe

### Ошибка: Visual Studio 2022 не найден

**Решение**: 
- Убедитесь, что Visual Studio 2022 установлен
- Установите компонент "MSVC v143 - VS 2022 C++ x64/x86 build tools"
- Используйте Developer Command Prompt for VS 2022

### Ошибка: Qt5 не найден

**Решение**:
- Установите Qt5 через vcpkg: `vcpkg install qt5-base`
- Или установите Qt5 вручную и укажите путь: `-DCMAKE_PREFIX_PATH="C:\Qt\5.15.2\msvc2019_64"`

### Ошибка: vcpkg не найден

**Решение**:
- Установите vcpkg (см. раздел "Требования")
- Установите переменную окружения `VCPKG_ROOT`
- Или не используйте vcpkg, установив зависимости вручную

### Ошибка: Подмодули не инициализированы

**Решение**:
```cmd
git submodule update --init --recursive
```

### Ошибка компиляции: C++20 не поддерживается

**Решение**:
- Убедитесь, что используется Visual Studio 2022 (поддерживает C++20)
- Проверьте, что установлен последний Windows SDK

### Ошибка: Не удалось найти библиотеки

**Решение**:
- Проверьте, что все подмодули инициализированы
- Убедитесь, что зависимости установлены через vcpkg или вручную
- Проверьте пути в переменных окружения

## Дополнительная информация

### Структура проекта

- `Rdk/` - ядро системы (подмодуль)
- `Libraries/` - библиотеки компонентов (подмодули)
- `App/` - приложения
- `Bin/` - бинарные файлы и ресурсы (подмодуль)
- `cmake/` - модули CMake
- `Reports/` - документация проекта

### Пресеты CMake

Проект использует CMake Presets для упрощения сборки:

- `win-vs2022-debug` - отладочная сборка с Visual Studio 2022
- `win-vs2022-release` - релизная сборка с Visual Studio 2022
- `win-msvc-debug` - отладочная сборка с Ninja (альтернатива)
- `win-msvc-release` - релизная сборка с Ninja (альтернатива)

### Стандарт C++

Проект использует C++20. Убедитесь, что компилятор поддерживает этот стандарт.

## Контакты и поддержка

При возникновении проблем:
1. Проверьте раздел "Решение проблем"
2. Изучите документацию в папке `Reports/`
3. Проверьте логи сборки для детальной информации об ошибках

