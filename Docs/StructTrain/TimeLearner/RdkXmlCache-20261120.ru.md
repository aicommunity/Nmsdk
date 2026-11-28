# Кэш XML при переносе обученной модели

Статус: дефект воспроизведён штатным Windows native81, исправление находится
в Rdk feature. A4 SDK принят; native86 завершён86/86 PASS, включая прежний
отказ LegacyDecimalPrefixes. Независимые Python3 и два Console-процесса
также проверены; Linux и фактический N4 перенос остаются непроверенными.
Это адресная работа этапов4/5;
полностью принят только этап0 исходного плана.

Изолированный Windows A4 SDK завершён и принят: exit0,2622.06s,
вся kernel group и задача планировщика закрыты. Source Root de5287ca0ae54dc1de9334992bec27c527543d6e,
Rdk561986e9f336ee5914e2d119de90b005e06f3639, Pulse0cf335ae08347f2d042d7eb3f5d05ef70a55789c.
Полный86-case cohort завершён за3428.67с; все81 прежних case сохранены.
Все процессы закрыты, kernel Job отсутствует, JUnit inventory86/86 без
пропусков и отказов. [Принятый SDK](../../../Reports/StructTrain/TimeLearner/RdkXmlCache-20261120/windows-sdk-a4-accepted.json)
и [итог всех трёх интерфейсных gates](../../../Reports/StructTrain/TimeLearner/RdkXmlCache-20261120/windows-a4-accepted-gates.json).
Исходная квитанция running сохранена как наблюдение до завершения.

## Наблюдение и исправление

Windows A3 SDK Root cbc1ac36f6be9b7abe4edb52f1c2c8f6dffbad60,
Pulse0cf335ae08347f2d042d7eb3f5d05ef70a55789c,
Rdkcb6fe50da94ca9cbc9d5e4c0811d42b37b44a14a завершён успешно.
Полный native81 завершён80 PASS/1 FAIL: все исходные78 cases и две новые
регрессии ширины/реального Copy прошли. Единственный отказ —
`RdkIntegralXml.LegacyDecimalPrefixesRemainReadable`: после первого чтения17
последующие записи−23,−1,0 читаются как17. Все процессы A3 закрыты;
отрицательный результат сохранён. Последующая A4 прошла Python3 над16
настоящими DATA8 fixtures и два Console-процесса для N2 target/foil.
Это не научный N4 Test; Linux остаётся отдельным gate.

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
Исходные N4 Train используют прежние Root893/Pulsec508/Rdkde413;
их runtime и математическая цель этим изменением не меняются.

## Проверка

Изолированный A4 сохранил все прежние81 ID и добавил пять новых:

| Suite | Проверка |
|---|---|
| RdkIntegralXml | NamedIndexedAndPositionalUnsignedReadsPreserveFullWidth |
| RdkXmlStorage | DirectMutationsAreVisibleAfterCachedReads |
| RdkXmlStorage | CreateLoadAndDestroyDiscardPreviousCursorValues |
| RdkXmlStorage | SameNamedNodesKeepIndependentCursorValues |
| RdkXmlStorage | LoadingFieldsPreservesSourceCursorAndCopiesActualValues |

Всего86, без platform exclusions. Это реальные USerStorageXML API,
Save/Load и production integration target, не извлечённое тело функции.
Исходный LegacyDecimalPrefixes не ослаблен. Windows-компиляция и все эти
проверки завершены, прежние DATA8 assertions сохранены. Дальше требуются
Linux-приёмка и реальный N4 frozen Train→Test. Успех инженерных проверок
не является сертификатом обучения или новой научной классификацией.
