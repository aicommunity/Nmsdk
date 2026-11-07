# Console replay многопикового одиночного отклика

Адресная normal-проверка новой диагностической политики принята на Elder.
Это закрывает Console replay одиночной пробы, а не назначение волн в Train
штатной пачкой и не классификацию.

## Неудачная первая попытка сохранена

A1: tool `89b3842d34290bdb5d3ebaf91f05304cd2e82681`, compiled Root
`62997ad1e7cb7869012d11da82b5a48b529ac1e7`, PulseLib
`24f9767ace1f498d5dc048a70fc303789adac757`.
Пять design tests прошли. Classic с прежней IsolatedWindow точно воспроизвёл
архивный отклик; следующий Console process завершился с кодом2 и
`invalid_native_configuration_selection`. До Branch выполнение не дошло.

Причина: диагностический SingleImpulseMaximum попадал в конфигурацию idle
владельца обучения. Native training configuration обоснованно запрещает эту
политику. Исправление `9f9de91f1b0e4c5e2841a57d5f0bb2b0d20595c5` сохраняет
IsolatedWindow в idle-конфигурации, а schema5 применяет только к фактическому
transient single-pulse запросу. Допуски и запрет диагностического сертификата
обучения не ослаблены.

Evidence A1 `924ae007b517f73722540e39f72cdd22e058cf10`:
231 members,1209856 compressed bytes. [Независимая сверка](SingleMaximumConsoleReplayA1Verification.json).
Отрицательная попытка не переименована в успешную.

## Сборка и успешный повтор

Собран Console Root `038a66413b7a41e75bf3826eda365db1c78c364b`, PulseLib
`217dc53c4b1cc010ad6938852a91ee6d2df09e3c`; Core соответствует6c520fb.
Сборка и CLI admission receipt: `07bd874f9561e7f027864317c644af0e6347a96f`,
27 members,67008 compressed bytes. Проверены498 Root и265 Pulse source hashes.
Четыре прежних runtime сохранены; сборка выполнялась последовательно.

Повтор A2 использовал тот же tool89b3842, те же исходные модели и параметры.
Все четыре задания Classic/Branch × IsolatedWindow/SingleImpulseMaximum
зафиксированы до запуска. Пять design tests и все четыре Console операции
прошли. Для каждой топологии прежняя политика сначала точно воспроизвела
архивную waveform. Затем между политиками точно совпали stimulus и soma
samples, relative clocks с объявленным roundoff-допуском; base/effective
model revisions совпали. Изменена только интерпретация наблюдения.

| Одиночная проба | Старая политика | Новый максимум | Амплитуда, native units |
|---|---|---|---|
| Classic, physical input0 | ambiguous,3 локальных пика | 0.027s, delay0.017s | 0.23209749260986 |
| Branch, physical input2 | ambiguous,2 локальных пика | 0.030s, delay0.020s | 0.011859327741041703 |

Частота2000Гц; threshold0.0117 сохранён. Это реальные многопиковые отклики
с обратным влиянием LTZone; новая политика не подавляет feedback и не
выбирает первый максимум после первого спада. Оба окна содержат3601 samples.
Применён первый source impulse к выбранному физическому входу: Branch input2
не означает предъявление третьего импульса исходной пачки.

Evidence A2 `e7b73e1fdc6c5d626604eb0e841adfb95d00ea70`:
459 members,2128700 compressed bytes, SHA256
`93dd6eeec908be54da0f05a510852c1949ac5f5e71ca5a7e35bfc40bcc221ce6`.
[Независимая сверка](SingleMaximumConsoleReplayA2Verification.json) проверила
все members,383 tool hashes,424 artifact bindings четырёх run manifests и
совпадение runtime с отдельным build receipt. Локально выполнялась только
проверка Git/archive/hash metadata; численные сравнения выполнены на Elder.

216 файлов извлечённого исходного кэша не продублированы. Их точные bindings
ссылаются на существующий primary archive commit
`fea18ada6b6446ac422fb728d119ec06bc257ae5` в bundle.external_source_cache.
Все новые run inputs, модели, primary observations и channel diagnostics
сохранены. Whole-group closure и released lease проверены после выполнения;
metadata/capacity очереди и immutable runtime не изменялись.

## Что остаётся открытым

- Визуальный отчёт новых наблюдений с читаемыми temporal plots.
- ASan физических компонентов нового schema5 пути: unit ASan34 не заменяет её.
- Максимум закреплённого импульса при наложении волн в штатной пачке Train.
- Остальная обязательная матрица, итоговые эксперименты классификации и merge
  законченного этапа в develop.

SingleImpulseMaximum остаётся diagnostic_only/training_eligible=false.
Ни сертификат Exact, ни положительный результат классификации этими пробами
не получены. Общий план и цель остаются незавершёнными.
