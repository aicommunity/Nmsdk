# Инструкция по сборке и запуску теста QMessageBox

## RU

## Успешная сборка

Тест успешно собран с использованием:
- **VS2022 Developer Command Prompt**
- **vcpkg** (E:\vcpkg)
- **Qt5** через vcpkg

## Расположение исполняемого файла

```
Tests\Integration\GUI\build_test\Release\Test_QMessageBox.exe
```

## Как запустить тест

### Вариант 1: Через PowerShell (из корня репозитория)
```powershell
cd Tests\Integration\GUI
.\build_test\Release\Test_QMessageBox.exe
```

### Вариант 2: Двойной клик
Просто дважды кликните на `Test_QMessageBox.exe` в проводнике Windows.

## Что тестировать

В открывшемся окне есть 3 кнопки:

1. **Test 1: StandardButton reply = QMessageBox::question(...)**
   - Правильный способ с сохранением результата в переменную
   - Должен работать без ошибок

2. **Test 2: Direct comparison (problematic)**
   - Прямое сравнение (старый проблемный способ)
   - Может вызвать падение в Windows

3. **Test 3: With visibility check**
   - С проверкой видимости виджета перед вызовом
   - Исправленный способ

## Ожидаемые результаты

- **Test 1 и Test 3**: Должны работать без ошибок
- **Test 2**: Может вызвать падение или исключение в Windows

## Пересборка теста

Если нужно пересобрать тест:

```powershell
cd Tests\Integration\GUI
$vsPath = "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat"
$vcpkgRoot = "E:\vcpkg"
cmd /c "`"$vsPath`" x64 && cmake --build build_test --target Test_QMessageBox --config Release"
```

## Результаты тестирования

После тестирования всех трех кнопок, пожалуйста, сообщите:
1. Работает ли Test 1?
2. Работает ли Test 2 (или падает)?
3. Работает ли Test 3?
4. Есть ли какие-либо ошибки в консоли?

Это поможет подтвердить, что проблема действительно в прямом сравнении результата `QMessageBox::question()` без сохранения в переменную.

---

## EN

## Successful build

The test was built successfully using:
- **VS2022 Developer Command Prompt**
- **vcpkg** (E:\vcpkg)
- **Qt5** via vcpkg

## Executable location

```
Tests\Integration\GUI\build_test\Release\Test_QMessageBox.exe
```

## How to run the test

### Option 1: Via PowerShell (from repository root)
```powershell
cd Tests\Integration\GUI
.\build_test\Release\Test_QMessageBox.exe
```

### Option 2: Double-click
Double-click `Test_QMessageBox.exe` in Windows Explorer.

## What to test

The opened window has 3 buttons:

1. **Test 1: StandardButton reply = QMessageBox::question(...)**
   - Correct approach with result stored in a variable
   - Should work without errors

2. **Test 2: Direct comparison (problematic)**
   - Direct comparison (old problematic approach)
   - May crash on Windows

3. **Test 3: With visibility check**
   - With widget visibility check before the call
   - Fixed approach

## Expected results

- **Test 1 and Test 3**: Should work without errors
- **Test 2**: May crash or throw on Windows

## Rebuilding the test

To rebuild:

```powershell
cd Tests\Integration\GUI
$vsPath = "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat"
$vcpkgRoot = "E:\vcpkg"
cmd /c "`"$vsPath`" x64 && cmake --build build_test --target Test_QMessageBox --config Release"
```

## Test results

After testing all three buttons, please report:
1. Does Test 1 work?
2. Does Test 2 work (or crash)?
3. Does Test 3 work?
4. Any console errors?

This helps confirm the issue is direct comparison of `QMessageBox::question()` result without storing it in a variable.
