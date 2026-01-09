# Инструкция по сборке и запуску теста QMessageBox

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
