# Регрессия CLI analyze из-за локального импорта

На actual native304 source8021301e plain analyze падал с UnboundLocalError:
main содержит условный `from matched_resistance_analysis import analyze`;
Python делает analyze локальным именем во всей main. Поэтому обычный dispatcher
не мог вызвать верхнеуровневую analyze(args), даже если matched-ветка не выбрана.
Та же коллизия есть в принятом root8b231dae9. Этот дефект не является отказом
C++ обучения;18 subtest failures и два отдельных inventory errors не смешиваются.

Исправление: импорт matched-функции с явным именем analyze_matched_resistance.
Оба call sites обращаются к правильным функциям. Форматы, статусы, научные
допуски, data parser и математическая цель не меняются. Существующая suite
AnalysisCliTest из5 actual-native checks покрывает positive domain, unknown
schema, output collision, mandatory probe trace и historical schema adapter.
До реальных server checks runtime acceptance остаётся pending.

Отдельные ошибки границ inventory schema3/schema4 и ModelSpec2 в joint reader119
не исправляются ослаблением подсчёта; им нужен декларативный набор по actual
native spec. CLI hotfix не утверждает приёмку совместного C-search среза.


## Подтверждение и приёмка

Коллизия введена roota42322eaa1e821d31b50962d5137b838858c0fe3
при добавлении matched-resistance command. Это объясняет поздний plain analyze
failure; прежние зелёные проверки до этого commit не гарантировали последующие
CLI versions. Прямые библиотечные audits, C++ наблюдения и августовские визуальные
4/8–6/8 этим дефектом не отменяются.

Source7a98295005762c11a9937e5c8f63e6628564d6d6 проверен production suite5 на
обоих workers без errors/failures/skips. На Elder отдельные actual native2/2
ClassicReadonlyPreview/BranchReadonlyPreview создали первичные данные в прежнем
immutable normal SDK8021301e/Pulsecc97149c. На M40 те же два JSON получены через
Git и повторно проанализированы; новых native моделей там не запускали.
Это проверка Python dispatcher, не ASan/growth/вся физическая матрица.

Elder proof60442fb2a8ea1572a74d3d323d37a8b74e1cb08b:51 members/66740B;
M40 proof9ed1b059d957daadccb0dd3ec9983b96a6fd23a9:14 members/21112B.
Все member hashes и277 Python blobs каждого reader source независимо сверены.
Два native JSON побайтно совпадают между workers. Cgroups закрыты, leases
освобождены только после kernel readback. [Контрольные суммы](AnalysisDispatchVerification.json).

Совместный C-search source4c остаётся непринятым: его новые ModelSpec2 recognition
cases требуют отдельных fresh-process observations, а domain CLI corpus теперь
проверен на специальном native2 gate. CLI hotfix не подменяет эти восемь replay
проверок и не присваивает scientific classification PASS.
