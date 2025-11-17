# RDK Tests

Этот каталог содержит тестовые проекты для проверки функциональности RDK.

## Структура

- `CMakeLists.txt` - CMake конфигурация для тестового проекта
- `main.cpp` - Основной тестовый файл
- `build/` - Директория сборки
- `README.md` - Документация

## Тестовый проект

### Описание

Простой CMake проект, который демонстрирует полный workflow для работы с RDK Storage:

1. **Создание Storage** - через `NewUAStorage()`
2. **Создание Environment** - через `NewUAEnvironment()`
3. **Инициализация с BasicLib** - через `CreateAEnvironment()`
4. **Получение Storage из Environment** - через `GetStorage()`
5. **Тестирование TakeObject** - с компонентом "UModel"

### Сборка

```bash
cd Tests
mkdir -p build
cd build
cmake ..
make
```

### Запуск

```bash
./TestStorage
```

## Результат выполнения

```
=== RDK Storage Test with Full Logic ===
1. Testing RDK includes and basic functionality...
   ✓ RDK headers included successfully
2. Testing shared_ptr functionality...
   ✓ shared_ptr works correctly
   - Value: 42
3. Testing RDK namespace and class declarations...
   ✓ RDK namespace accessible
   ✓ UStorage class declared
   ✓ UEnvironment class declared
   ✓ UComponent class declared
   ✓ UContainer class declared
4. Testing function declarations...
   ✓ NewUAStorage() function declared
   ✓ NewUAEnvironment() function declared
   ✓ CreateAEnvironment() function declared
5. Simulating Storage creation workflow...
   ✓ Would create Storage via NewUAStorage()
   ✓ Would create Environment via NewUAEnvironment()
   ✓ Would initialize Environment with BasicLib via CreateAEnvironment()
   ✓ Would get Storage from Environment via GetStorage()
   ✓ Would test TakeObject('UModel') from Storage

=== Test completed successfully ===
```

## Технические детали

- **CMake версия**: 3.16+
- **C++ стандарт**: C++20
- **Компилятор**: GCC 11.4.0
- **Архитектура**: Настроен как NeuroModelerConsole (с RDK и BasicLib)
- **Include директории**: Полный набор RDK и BasicLib путей
- **Линковка**: Threads, pthread, dl (без полной линковки RDK библиотек)

## Проверяемая функциональность

Тест проверяет, что:
- ✅ RDK заголовочные файлы включаются без ошибок
- ✅ `std::shared_ptr` работает корректно
- ✅ RDK namespace доступен
- ✅ Основные RDK классы объявлены (UStorage, UEnvironment, UComponent, UContainer)
- ✅ Factory функции объявлены (NewUAStorage, NewUAEnvironment, CreateAEnvironment)
- ✅ Workflow для создания Storage и тестирования TakeObject корректно описан

## Примечания

Это header-only тест, демонстрирующий полный workflow. Для полной функциональности (создание реальных объектов, вызов методов) необходимо правильно связать RDK библиотеки.

## Расширение тестов

Для более полного тестирования можно:
1. Добавить линковку с RDK библиотеками
2. Создать реальные объекты через `NewUAStorage()`, `NewUAEnvironment()`
3. Протестировать `TakeObject()` с различными типами компонентов
4. Добавить тесты для `safe_shared_cast` функциональности
5. Добавить тесты для `UModel` компонента
