# Сохранение целых параметров при переносе модели

>20.11: A3 SDK принят, полный native81 завершён80/81. Все исходные78 cases,
>ширина и Copy прошли; единственный отказ выявил устаревший текст XML-кэша.
>[Исправление владельца и следующий native86](RdkXmlCache-20261120.ru.md).
>Ниже сохранена постановка предыдущего A3 запуска.

Статус: исправления подготовлены; новая изолированная Windows A3 SDK-сборка
запущена и kernel Job подтверждён живым. Runtime-приёмка ещё не выполнена.
Научные N4 Train продолжают использовать прежние
Root893/Pulsec508 и Rdk de413; их runtime не изменяется.

## Подтверждённый дефект

В полном Windows native78 присутствовали все объявленные ID,59 PASS и19 FAIL.
В двух `NativeJointCapacitance/*Rollback` непосредственная причина —
`native_copy_mismatch` для `DebugSysEventsMask`. Общее чтение целых свойств
в `Rdk/Core/Serialize/UXMLStdSerialize.h` использовало `atoi`, возвращающий
32-битный int, до приведения к типу назначения. На Windows worker отдельно
воспроизведено преобразование корректного unsigned4294967295 в2147483647.

Другие17 отказов имеют отдельные причины:16 новых DATA fixtures не выключали
Default PostTune перед configured-owner Init; ещё один terminal-selection test
не успевал дойти до обязательного реального edit за10s wall. Они не являются
доказательством неисправности математической цели обучения.

## Исправление владельца

В общем XML reader используются `strtoll` для знаковых и `strtoull` для
беззнаковых типов. Формат XML, Rdk lifecycle и штатная цепочка CopyProperties
сохраняются. Не требуется исключать DebugSysEventsMask из строгого сравнения
storage-образов или исправлять значение из learner на каждом тике.

Числовые десятичные префиксы, ведущие пробелы и знак сохраняют прежнюю
совместимость. Строгую проверку полной строки и допустимости конфигурации
продолжает выполнять соответствующий parser/preflight; это не новая схема
валидации всех исторических Rdk параметров.

Rdk feature создана от develop10e9d05aa658dd2203c89bc84ba9166595b50014.
Принятый исходный de4134235c0dcb8b91fd9a43b267348ad1a163ca включён через
отдельный `--no-ff` merge756b75b0742a66b06061fd584b147d1a578d9704:
исправления предыдущей полной загрузки графа не теряются. Общий develop
ещё не обновляется до приёмки.
Исправление сериализации: Rdk cb6fe50da94ca9cbc9d5e4c0811d42b37b44a14a.
Compiled Root A3: cbc1ac36f6be9b7abe4edb52f1c2c8f6dffbad60.
[Namespace, dispatch и проверенный kernel handle](../../../Reports/StructTrain/TimeLearner/TerminalPhysicalData8-20261119/windows-sdk-a3-running.json).

## Проверки и ограничения

В существующий integration target добавлены три `RdkIntegralXml` cases:

1. Save/Load через реальные `USerStorageXML` operators для граничных значений
   всех поддерживаемых стандартных целых типов и внутренних64-битных значений.
2. Совместимые десятичные префиксы, знак и беззнаковый `-1`.
3. Copy реального `NPulseNeuron` и RegisterClassImage через storage/Environment:
   parent mask0xFFFFFFFF и дочерний mask0x80000001 должны сохраниться вместе
   с полным строгим descriptor.

Первый и третий сценарии проверяют production API, не копию тела функции.
Следующий SDK gate включает все прежние78 случаев и эти три регрессии:
81 declared tests, без platform exclusions. Обе failed-attachment топологии
уже присутствуют среди исходных78; повторный тест Branch не добавляется.

Инженерная terminal-selection fixture получает30s wall до required edit,
как ранее вариант C0. После настоящего edit по-прежнему ожидается реальный
wall deadline. Model-time budget20s, edit limits, finalization30s и допуски
обучения сохраняются. Это не расширение бюджетов научных Train.

Исправление DATA fixture из root ee7df956207bd4f541c7ede8aadc2578ccc4e7bf
включается в новую сборку. Следом обязательны три Python methods по16 реальным
native DATA fixtures, frozen Console, Linux-проверка и actual N4 source/DATA
response comparison до использования нового пути для научных выводов.
Исходный отрицательный Windows прогон и прежние Linux PASS сохраняют свои
версии и область доказательности.
