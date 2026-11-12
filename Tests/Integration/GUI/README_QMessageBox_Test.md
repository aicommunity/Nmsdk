# Тест QMessageBox::question для Windows

## RU

Этот тест проверяет работоспособность `QMessageBox::question()` в Windows и помогает выявить проблемы с падением на строке 477 в `UGEngineControlWidget.cpp`.

## Описание тестов

1. **Test 1**: Правильный способ с сохранением результата в переменную `QMessageBox::StandardButton`
2. **Test 2**: Прямое сравнение (старый проблемный способ, как было в оригинальном коде)
3. **Test 3**: С проверкой видимости виджета перед вызовом (исправленный способ)

## Быстрый запуск (Windows)

Самый простой способ - использовать PowerShell скрипт:

```powershell
cd Tests\Integration\GUI
.\run_qmessagebox_test.ps1
```

Или используйте batch скрипт:

```cmd
cd Tests\Integration\GUI
build_and_run_test.bat
```

## Компиляция через CMake

```bash
cd <build_directory>
cmake ..
cmake --build . --target Test_QMessageBox
```

Запуск:
```bash
./Test_QMessageBox  # Linux
Test_QMessageBox.exe  # Windows
```

## Компиляция standalone версии (Windows)

### С Qt5:
```bash
g++ -o Test_QMessageBox_Standalone.exe Test_QMessageBox_Standalone.cpp ^
    -I"C:/Qt/5.15.2/msvc2019_64/include" ^
    -L"C:/Qt/5.15.2/msvc2019_64/lib" ^
    -lQt5Core -lQt5Widgets -fPIC -mwindows
```

### С Qt6:
```bash
g++ -o Test_QMessageBox_Standalone.exe Test_QMessageBox_Standalone.cpp ^
    -I"C:/Qt/6.x.x/msvc2019_64/include" ^
    -L"C:/Qt/6.x.x/msvc2019_64/lib" ^
    -lQt6Core -lQt6Widgets -fPIC -mwindows
```

### С Visual Studio:
```cmd
cl /EHsc Test_QMessageBox_Standalone.cpp ^
    /I"C:\Qt\5.15.2\msvc2019_64\include" ^
    /link /LIBPATH:"C:\Qt\5.15.2\msvc2019_64\lib" Qt5Core.lib Qt5Widgets.lib /SUBSYSTEM:WINDOWS
```

## Что проверяет тест

- Работает ли `QMessageBox::question()` с сохранением результата в переменную
- Работает ли прямое сравнение (может вызывать падение в Windows)
- Помогает ли проверка видимости виджета перед показом диалога
- Выявляет ли тест исключения при вызове диалога

## Ожидаемое поведение

- **Test 1 и Test 3**: Должны работать без ошибок
- **Test 2**: Может вызвать падение или исключение в Windows, если проблема действительно в прямом сравнении

## Использование результатов

Если Test 2 падает, а Test 1 и Test 3 работают - это подтверждает, что проблема в прямом сравнении результата `QMessageBox::question()` без сохранения в переменную.

---

## EN

This test verifies `QMessageBox::question()` on Windows and helps identify crashes at line 477 in `UGEngineControlWidget.cpp`.

## Test description

1. **Test 1**: Correct approach — store result in `QMessageBox::StandardButton` variable
2. **Test 2**: Direct comparison (old problematic approach, as in original code)
3. **Test 3**: With widget visibility check before call (fixed approach)

## Quick run (Windows)

Easiest — use the PowerShell script:

```powershell
cd Tests\Integration\GUI
.\run_qmessagebox_test.ps1
```

Or the batch script:

```cmd
cd Tests\Integration\GUI
build_and_run_test.bat
```

## Build via CMake

```bash
cd <build_directory>
cmake ..
cmake --build . --target Test_QMessageBox
```

Run:
```bash
./Test_QMessageBox  # Linux
Test_QMessageBox.exe  # Windows
```

## Standalone build (Windows)

### With Qt5:
```bash
g++ -o Test_QMessageBox_Standalone.exe Test_QMessageBox_Standalone.cpp ^
    -I"C:/Qt/5.15.2/msvc2019_64/include" ^
    -L"C:/Qt/5.15.2/msvc2019_64/lib" ^
    -lQt5Core -lQt5Widgets -fPIC -mwindows
```

### With Qt6:
```bash
g++ -o Test_QMessageBox_Standalone.exe Test_QMessageBox_Standalone.cpp ^
    -I"C:/Qt/6.x.x/msvc2019_64/include" ^
    -L"C:/Qt/6.x.x/msvc2019_64/lib" ^
    -lQt6Core -lQt6Widgets -fPIC -mwindows
```

### With Visual Studio:
```cmd
cl /EHsc Test_QMessageBox_Standalone.cpp ^
    /I"C:\Qt\5.15.2\msvc2019_64\include" ^
    /link /LIBPATH:"C:\Qt\5.15.2\msvc2019_64\lib" Qt5Core.lib Qt5Widgets.lib /SUBSYSTEM:WINDOWS
```

## What the test checks

- Whether `QMessageBox::question()` works with result stored in a variable
- Whether direct comparison works (may crash on Windows)
- Whether widget visibility check before the dialog helps
- Whether the test catches exceptions when showing the dialog

## Expected behavior

- **Test 1 and Test 3**: Should work without errors
- **Test 2**: May crash or throw on Windows if the issue is direct comparison

## Using results

If Test 2 crashes but Test 1 and Test 3 work — that confirms the issue is direct comparison of `QMessageBox::question()` result without storing it in a variable.
