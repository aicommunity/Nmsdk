# Связи свойств при повторном использовании объектов и Copy

Актуально 28.10: post-fix A3 на обоих workers завершён успешно — 4/4 suites,
PulseLib 387 pass + 10 skip, 0 failures/errors, 9 Python tests и 208 primary
trials. Rdk merge в develop: `1812624ff75c60f03ad57c10b379d3e3848590bc`.
Подробная область приёмки: [PooledFullAcceptance](PooledFullAcceptance.ru.md).
Ниже сохранены исходные failures и промежуточные snapshots.

## Подтверждённый дефект

Полный maintained CTest на Elder-1 A9 (root
`270c62ce55a80a9efea6e434bba8ca5664a821af`) и M40 A15 (root
`51c54abb95881ced0942e5cfd14928609da00ac6`) завершился одинаково:
три suites прошли; PulseLib — 395 tests, 370 pass, 10 skip, 15 failures
экспорта/импорта learned-state. Диагностика указывает на null/external bindings
Dataset/Generator. Все 16 исходных обучений каждого worker отдельно проверены
production Python auditor по 208 первичным trial JSON/CSV: измерения и
сертификаты согласованны. Успешный Train не отменяет отказ переноса.

`UStorage::TakeObject` при reuse вызывал Default, но сохранял прямые внешние
`Input.SetPointer` предыдущего владельца. Managed links и direct property links
не эквивалентны: прежний BreakLinks не очищал вторые. В Copy подключённое
свойство назначения могло игнорировать копируемое значение. Строгий model
identity обнаруживал оставшиеся указатели вместо создания ложного валидного
архива. Его проверка не ослабляется.

Test-only Rdk `6677338e46716d2ba5cf085e1564b8ead96cb949`
воспроизводит дефект штатным `Test_UContainer_Components`: два отказа
Return/Take и Copy, одна успешная проверка сохранения связей обычным lifecycle.
Matrix accessor первого fixture читал локальный cache; исходное доказательство
опирается также на фактические identities связей и неправильное scalar value.

## Исправление и границы применения

Rdk `1223bcc18cf1ba106e8f8a17f20cce8c000c104d` включает production fix
`c7560c6f9aaec13a24c7bb611375fc53e02d82a4` и уточнённые native fixtures. Изменения:

1. `UProperty.h`: DetachFrom очищает список источников, alias и cached flags;
   `ResetPointer(-1, nullptr)` означает полное отключение через существующий
   interface, без нового virtual slot.
2. `UContainer.cpp`: перед replacement Copy отключаются старые входящие связи
   самого объекта; затем работают штатные копирование значений, Build и дети.
3. `UNet.cpp`: full BreakLinks охватывает direct inputs; Copy сохраняет closed
   internal direct bindings исходного графа и восстанавливает их на объектах
   назначения. Внешние unmanaged pointers источника не копируются.
4. `UStorage.cpp`: перед Default повторно выдаваемого объекта собираются адреса
   свойств всего поддерева; внешние источники отключаются, внутренние сохраняются.
   Адрес потенциально уже устаревшего внешнего источника не разыменовывается.

```text
cold pooled reuse:
    collect properties of the old subtree
    for each inspectable input, from last source slot to first:
        preserve sources inside the subtree
        remove managed external links through their native connector
        detach external aliases or direct external source slots
    perform existing Default/factory reuse sequence

replacement Copy:
    capture closed internal direct wiring of source
    detach destination's previous incoming bindings
    perform native copy/build/children and managed link reconstruction
    rebind captured internal sources to destination properties
```

Обычные Build/Reset/Default не разрывают живые связи. Constructor/internal wiring
при reuse сохраняется. Исправление не добавляет learner-specific «будящих»
Build, вложенного Calculate или нового смысла lifecycle bool.

## Проверки и доступные данные

Root проверенной версии: `f3b45cb9300e4dd43f9d4c4d212e366b75195af1`.

| Проверка | Результат |
|---|---|
| Elder-1, property-fixed-A2 | 18/18 native UContainer pass, без skips/errors |
| M40, property-ASan-A1 | 18/18 native UContainer pass; detect_leaks=0 |
| Elder-1, pooled-bindings-A1 | 25 builder tests, затем 5 learned-state tests в одном процессе: 30/30 pass |
| Тот же integration run | 18/18 UContainer, 9/9 Python; независимая проверка 62 training trials и четырёх rollback probes |

В fixed-A1 сохранены два fixture failures: `MatrixInput(0,0)` читает локальный
cache. Fixed-A2 использует эффективное `MatrixInput.GetData()(0,0)`, добавляя
constructor wiring и mixed internal/external vector slots. Физика и численные
допуски для получения PASS не менялись.

Evidence опубликованы через Git и объединены в root feature:

- Elder-1: `28b59dc8814aec410a8d0d58c41e8faf122df394`,
  `Reports/StructTrain/TimeLearner/s04-property-bindings-elder1`.
- M40: `5747c1a2022a11adb4f85c69edceec4bb3f44c71`,
  `Reports/StructTrain/TimeLearner/s04-property-bindings-m40`.

Пакеты содержат также оба исходных full-suite failures, исходные данные,
ошибочные fixtures и независимый аудит; stored gzip и raw payload имеют
раздельные SHA256. Бинарники и credentials не публикуются.

Историческое состояние перед паузой: post-fix CTest `s05-pooled-full-a1` запущен на обоих
workers в изолированных runtime. До его завершения нельзя объявлять общую
интеграционную приёмку пройденной. Rdk feature пока не принята в develop.
Это не весь этап 4/5 и не научная проверка разделимости или августовских результатов.
