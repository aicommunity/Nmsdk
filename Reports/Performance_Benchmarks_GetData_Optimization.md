# Бенчмарки производительности оптимизации GetData()

## Обзор

Этот документ описывает бенчмарки для измерения эффекта оптимизаций производительности `GetData()` после перехода с прямого доступа к `.v`.

## Выполненные оптимизации

### 1. Улучшение fast-path в GetData()
- Добавлены branch prediction hints (`[[likely]]`/`[[unlikely]]`)
- Оптимизирован порядок проверок для максимальной эффективности

### 2. Кэширование значений в критических местах
- Оптимизированы файлы: `NNeuronLife.cpp`, `NPulseHebbSynapse.cpp`, `NPulseLTZone.cpp`, `NPulseSynChannel.cpp`
- Кэширование значений свойств в начале методов для избежания повторных вызовов `GetData()`

## Тесты производительности

### Расположение тестов
`Rdk/Tests/Unit/Engine/UProperty/Test_UProperty_Performance.cpp`

### Доступные тесты

1. **GetDataUnconnected** - Измеряет производительность `GetData()` для неподключенных свойств
2. **SetDataUnconnected** - Измеряет производительность `SetData()` для неподключенных свойств
3. **GetDataConnected** - Измеряет производительность `GetData()` для подключенных свойств
4. **FindProperty** - Измеряет производительность поиска свойства
5. **UnconnectedVsConnected** - Сравнение производительности подключенных и неподключенных свойств
6. **MultipleGetDataCalls** - Сравнение производительности множественных вызовов `GetData()` с кэшированием и без
7. **GetDataInLoop** - Измеряет эффект кэширования `GetData()` в циклах
8. **GetDataDifferentTypes** - Измеряет производительность для разных типов (int, double, bool)

## Запуск тестов

### Через CMake и CTest

```bash
# Сборка тестов
cd build
cmake --build . --target Test_UProperty_Performance

# Запуск всех тестов производительности
ctest -R PerformanceTest -V

# Запуск конкретного теста
./Test_UProperty_Performance --gtest_filter=PerformanceTest.GetDataUnconnected
```

### Через Visual Studio

1. Откройте проект в Visual Studio
2. Соберите проект `Test_UProperty_Performance`
3. Запустите тесты через Test Explorer или напрямую исполняемый файл

### Прямой запуск

```bash
# Windows (из папки build)
.\Rdk\Tests\Unit\Engine\UProperty\Debug\Test_UProperty_Performance.exe

# Linux/Mac
./Rdk/Tests/Unit/Engine/UProperty/Test_UProperty_Performance
```

## Интерпретация результатов

### Ожидаемые значения

#### GetDataUnconnected
- **Целевое значение**: < 1000 ns на вызов
- **Ожидаемое улучшение**: 20-50% благодаря branch prediction hints

#### MultipleGetDataCalls
- **Без кэширования**: Множественные вызовы `GetData()` в одной строке
- **С кэшированием**: Один вызов `GetData()` с последующим использованием кэшированного значения
- **Ожидаемое улучшение**: 60-80% для оптимизированных паттернов

#### GetDataInLoop
- **Без кэширования**: `GetData()` вызывается в каждой итерации цикла
- **С кэшированием**: `GetData()` вызывается один раз перед циклом
- **Ожидаемое улучшение**: 60-80% для циклов с множественными итерациями

### Пример вывода

```
[==========] Running 8 tests from 1 test suite.
[----------] Global test environment set-up.
[----------] 8 tests from PerformanceTest
[ RUN      ] PerformanceTest.GetDataUnconnected
Average GetData time (unconnected): 45.2 ns
[       OK ] PerformanceTest.GetDataUnconnected (1234 ms)
[ RUN      ] PerformanceTest.MultipleGetDataCalls
Multiple GetData() without caching: 135.6 ns
Multiple GetData() with caching: 45.2 ns
Improvement from caching: 66.7%
[       OK ] PerformanceTest.MultipleGetDataCalls (2345 ms)
[ RUN      ] PerformanceTest.GetDataInLoop
GetData() in loop (per access): 45.2 ns
GetData() cached before loop (per access): 0.5 ns
Improvement from caching: 98.9%
[       OK ] PerformanceTest.GetDataInLoop (3456 ms)
...
[==========] 8 tests from 1 test suite ran. (12345 ms total)
[  PASSED  ] 8 tests.
```

## Метрики для отслеживания

### Ключевые показатели

1. **Среднее время GetData() для unconnected свойств**
   - Базовое значение (до оптимизации): ~50-100 ns
   - Целевое значение (после оптимизации): ~30-50 ns
   - Улучшение: 20-50%

2. **Производительность множественных вызовов**
   - Без кэширования: 3x время одного вызова
   - С кэшированием: ~1x время одного вызова
   - Улучшение: 60-80%

3. **Производительность в циклах**
   - Без кэширования: N вызовов GetData()
   - С кэшированием: 1 вызов GetData() + N использований кэша
   - Улучшение: 60-80% для больших циклов

## Рекомендации по использованию

### Когда использовать кэширование

1. **Множественные вызовы в одной строке/выражении**
   ```cpp
   // Плохо
   result = prop1.GetData() + prop2.GetData() + prop3.GetData();
   
   // Хорошо
   const double p1 = prop1.GetData();
   const double p2 = prop2.GetData();
   const double p3 = prop3.GetData();
   result = p1 + p2 + p3;
   ```

2. **Вызовы в циклах**
   ```cpp
   // Плохо
   for (int i = 0; i < n; ++i) {
       sum += property.GetData();
   }
   
   // Хорошо
   const double prop = property.GetData();
   for (int i = 0; i < n; ++i) {
       sum += prop;
   }
   ```

3. **Повторные вызовы одного свойства**
   ```cpp
   // Плохо
   if (prop.GetData() > threshold && prop.GetData() < max) {
       // ...
   }
   
   // Хорошо
   const double val = prop.GetData();
   if (val > threshold && val < max) {
       // ...
   }
   ```

### Когда кэширование не нужно

1. **Одиночные вызовы** - накладные расходы минимальны
2. **Редко вызываемые методы** - оптимизация не критична
3. **Значения могут изменяться** - кэширование может привести к использованию устаревших данных

## Следующие шаги

1. Запустить тесты производительности
2. Зафиксировать базовые значения
3. Сравнить с ожидаемыми улучшениями
4. При необходимости провести дополнительные оптимизации

## Примечания

- Результаты могут варьироваться в зависимости от компилятора, оптимизаций компилятора и платформы
- Рекомендуется запускать тесты на Release-сборке с включенными оптимизациями компилятора
- Для более точных измерений рекомендуется использовать профилировщик (например, Intel VTune, perf)

