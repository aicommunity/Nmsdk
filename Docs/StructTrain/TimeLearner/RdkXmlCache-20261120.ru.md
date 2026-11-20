# Кэш XML при переносе обученной модели

Статус: дефект воспроизведён штатным Windows native81, исправление находится
в Rdk feature. A4 SDK принят; новый native86 выполняется, первые8 Rdk cases
прошли, включая прежний отказ LegacyDecimalPrefixes. Полного итога86 ещё нет.
Это адресная работа этапов4/5;
полностью принят только этап0 исходного плана.

Изолированный Windows A4 SDK завершён и принят: exit0,2622.06s,
вся kernel group и задача планировщика закрыты. Source Root de5287ca0ae54dc1de9334992bec27c527543d6e,
Rdk561986e9f336ee5914e2d119de90b005e06f3639, Pulse0cf335ae08347f2d042d7eb3f5d05ef70a55789c.
Запущен полный86-case cohort. Первые8 Rdk cases прошли; все81 прежних
case сохранены. [Принятый SDK](../../../Reports/StructTrain/TimeLearner/RdkXmlCache-20261120/windows-sdk-a4-accepted.json)
и [живой native Job, controls и частичные проверки](../../../Reports/StructTrain/TimeLearner/RdkXmlCache-20261120/windows-native86-running.json).
Частичный префикс stdout не заменяет финальный JUnit audit всего cohort.

## Наблюдение и исправление

Windows A3 SDK Root cbc1ac36f6be9b7abe4edb52f1c2c8f6dffbad60,
Pulse0cf335ae08347f2d042d7eb3f5d05ef70a55789c,
Rdkcb6fe50da94ca9cbc9d5e4c0811d42b37b44a14a завершён успешно.
Полный native81 завершён80 PASS/1 FAIL: все исходные78 cases и две новые
регрессии ширины/реального Copy прошли. Единственный отказ —
`RdkIntegralXml.LegacyDecimalPrefixesRemainReadable`: после первого чтения17
последующие записи−23,−1,0 читаются как17. Все процессы A3 закрыты;
отрицательный результат сохранён. Приёмка DATA8 целиком ещё не завершена,
независимые Python3, Console и Linux остаются отдельными gates.

`USerStorageXML::SetNodeText` не сбрасывал NodeTextCached. Также требовалась
одинаковая политика кэша при Create/Load/Destroy, смене и мутациях узла и
атрибутов. Исправление находится у владельца — Core/Serialize Rdk:

```text
before mutation or cursor change:
    invalidate cached text, name and attributes
    release cached node handles
perform the native XML operation
first read repopulates the cache for the current cursor
```

Совпадающие имена узлов не используются как identity. Частичная карта
атрибутов не определяет существование атрибута; это читает реальный XML.
LoadFieldsToNode сохраняет source-курсор и сбрасывает его кэш после возврата.
Кэш токенов пути сохраняется: он зависит от строки пути, а не содержимого XML.
Все три прямых ReadUnsigned приведены к тому же полному unsigned32-чтению,
что и общий оператор свойств. Десятичные префиксы и беззнаковый−1 совместимы.

Build/Reset/Calculate, scheduler, shared storage-образы и алгоритмы обучения
не меняются. Learner-specific повторных Build и исправляющих записей нет.
Продолжающиеся N4 Train используют прежние Root893/Pulsec508/Rdkde413;
их runtime и математическая цель этим изменением не меняются.

## Проверка

Новый изолированный A4 должен включать все прежние81 ID и пять новых:

| Suite | Проверка |
|---|---|
| RdkIntegralXml | NamedIndexedAndPositionalUnsignedReadsPreserveFullWidth |
| RdkXmlStorage | DirectMutationsAreVisibleAfterCachedReads |
| RdkXmlStorage | CreateLoadAndDestroyDiscardPreviousCursorValues |
| RdkXmlStorage | SameNamedNodesKeepIndependentCursorValues |
| RdkXmlStorage | LoadingFieldsPreservesSourceCursorAndCopiesActualValues |

Всего86, без platform exclusions. Это реальные USerStorageXML API,
Save/Load и production integration target, не извлечённое тело функции.
Исходный LegacyDecimalPrefixes не ослаблен. Дальше требуются фактическая
серверная компиляция/выполнение, прежние DATA8 assertions, независимый Python
readback и реальный N4 frozen Train→Test. Успех этих инженерных проверок
не является сертификатом обучения или новой научной классификацией.
