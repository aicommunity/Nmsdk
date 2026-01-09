# Production тест QMessageBox

## Описание

Этот тест создан для проверки падения на строке 483 в `UGEngineControlWidget.cpp`. В отличие от обычного теста, он использует **точно те же бинарники Qt и плагины**, что и штатное приложение из `Bin/Platform/Win`.

## Ключевые отличия от обычного теста

1. **Место сборки**: `Bin/Platform/Win` (как штатное приложение)
2. **Qt DLL**: Используются напрямую из `Bin/Platform/Win` при запуске
3. **Плагины**: Используются из `Bin/Platform/Win/plugins`
4. **Окружение**: Идентичное штатному приложению

## Сборка теста

### Через CMake из корня проекта:

```cmd
cd <project_root>
cmake -S . -B build_prod_test -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=ON
cmake --build build_prod_test --target Test_QMessageBox_Production --config Release
```

### Результат сборки:

Исполняемый файл будет создан в: `Bin/Platform/Win/Test_QMessageBox_Production.exe`

## Запуск теста

### Вариант 1: Через скрипт (рекомендуется)

```cmd
cd Tests\Integration\GUI
run_production_test.bat
```

### Вариант 2: Вручную с настройкой окружения

```cmd
cd Bin\Platform\Win
set PATH=%CD%;%PATH%
set QT_PLUGIN_PATH=%CD%\plugins
set QT_QPA_PLATFORM_PLUGIN_PATH=%CD%\plugins\platforms
Test_QMessageBox_Production.exe
```

## Что тестирует

Тест содержит 3 кнопки:

1. **Test 1: Exact code from line 483 (FIXED)**
   - Точное воспроизведение исправленного кода из строки 483 `UGEngineControlWidget.cpp`
   - Использует `QMessageBox::StandardButton reply = QMessageBox::question(...)`
   - Должен работать без ошибок

2. **Test 2: Direct comparison (OLD WAY - may crash)**
   - Прямое сравнение (старый проблемный способ)
   - Может вызвать падение в Windows

3. **Test 3: Multiple calls (stress test)**
   - Множественные последовательные вызовы для проверки стабильности

## Ожидаемые результаты

- **Test 1**: Должен работать без ошибок (исправленный код)
- **Test 2**: Может вызвать падение или исключение (если проблема не исправлена)
- **Test 3**: Должен работать стабильно при множественных вызовах

## Использование Qt

Тест использует:
- **Qt версия**: 5.15.2 (та же, что и штатное приложение)
- **Qt DLL**: Из `Bin/Platform/Win` (те же файлы, что использует NeuroModeler.exe)
- **Qt плагины**: Из `Bin/Platform/Win/plugins` (те же плагины)

## Проверка версий Qt

Для проверки версии Qt, используемой тестом:

```powershell
[System.Diagnostics.FileVersionInfo]::GetVersionInfo("Bin\Platform\Win\Qt5Core.dll").FileVersion
```

Должно быть: `5.15.2.0`

## Устранение проблем

### Ошибка: Qt plugins not found

Убедитесь, что плагины присутствуют в `Bin/Platform/Win/plugins/platforms/qwindows.dll`

### Ошибка: Qt DLL not found

Убедитесь, что Qt DLL присутствуют в `Bin/Platform/Win`:
- Qt5Core.dll
- Qt5Gui.dll
- Qt5Widgets.dll

### Тест не запускается

Проверьте, что тест собран:
```cmd
dir Bin\Platform\Win\Test_QMessageBox_Production.exe
```

Если файл отсутствует, пересоберите тест (см. раздел "Сборка теста")
