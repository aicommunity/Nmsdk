# Сохранение C₀ при Train → Test

Explicit C₀ native transfer принят адресно; полный controller/physics scope
остаётся открытым. [Приёмка и согласованный develop](C0Acceptance-2026-11-03.ru.md).
Проверенный Pulse Core: `69d463aa50144a1c8ddb4a674bb900c2a07e769f`.

Описанный ниже explicit transfer — принятый снимок. Последующие source-clock
и strict dataset-parser исправления приняты отдельно; актуальная последовательность
находится в [текущем статусе](CurrentStatus-2026-11-02.ru.md). Автоматический
export после ordinary edits и dormant-image transport проверяются отдельно в
[owner-кандидате](CapacitanceOwnership.ru.md). Его normal8/readers19 уже прошли,
но ASan и расширенный перенос ещё pending. Из этого не следует поддержка
bounded C-trim search либо полного XML/Copy controller checkpoint.

## Контракт принятого explicit transfer

История реализации: исходный Pulse `922ba91f71075b296a1c808e561b69fdd71f6255`.
Первый изолированный build root `833b9bb9e1062778d405928a191bb32500828f2b`
остановился до тестов из-за отсутствующего include QJsonDocument в обоих
learner. Исправление PulseLib `69d463aa50144a1c8ddb4a674bb900c2a07e769f`.
Неудачная сборка опубликована в `6f05f66ea89d93762dee1860a9952f4e5cc95400`,
её фактический cache/flags дополнительно сохранены до изменения build cache:
`bd35b706609d1c1acfb8df230e2f231cb4cfdebe`. B1 не является runtime PASS.

Completed/stopped package schema 2 добавляет `capacitance_state` к полному
native archive. Содержимое: исходные индивидуальные C₀, их capture/image
свидетельства, ModelSpec/storage closure, полная карта абсолютных поправок,
граница изменения и hash конечного физического графа. Первый экспорт явно
принимает NativeCapacitanceCorrection. Перед экспортом проверяются все C,
классы, статическая физика, storage и единая частота. Проверка сертификата
обучения остаётся отдельной и не ослабляется.

PrepareNativeLearnedState проверяет это состояние на приватно восстановленных
нейроне и dataset до commit живых детей. Import обоих learner сохраняет C₀
для последующего обычного re-export; baseline не захватывается заново.
Пакеты schema 1 не меняют прежний формат и не получают вымышленных C₀.
Source-solo с schema 2 может проходить существующий recognition import;
его сертификат относится к solo, а не автоматически к преобразованному графу.

`capacitance_evidence.py` независимо сверяет C₀, классы/физику, image closure,
масштабы и итоговую модель. Readers learned/stopped версии 3 читают обе схемы;
для schema 1 provenance C₀ остаётся unknown. Reader не утверждает, что исполнил
native XML import: это доказывают отдельные реальные компонентные fixtures.

Spec `native-capacitance-state-transfer-v1.json` объявляет 14 cases: шесть
completed/frozen/fresh-process C₀ fixtures, два partial stopped C₀ fixtures,
четыре прежних completed transport и два прежних partial stopped controls.
Положительные completed controls используют явно заданный sync=0.2; default
0.02 и amp=1e-5 сохранены. Это проверки переноса, не новая научная сходимость.
Mutation reader tests используют настоящие C++ packages и primary CSV.
Проверяется также независимый reader для обоих новых owned recognition
результатов с сохранённым source-solo C₀. Старые reader fixtures с фиксированным
набором 20 stopped scenarios не ослабляются под новый меньший набор.

## История проверок до адресной приёмки

Normal B3 (root `58d941c2664703e794179d0e5dfeaa95e54949ad`) завершил
9/9 lifecycle и 14/14 native проверок. Reader gate завершился с ошибкой:
Python учитывал только классы существующих узлов, тогда как native
`ModelArchive::Classes` также включает непустые строковые параметры
`*ClassName`, управляющие последующим ростом. Исправление сохраняет строгую
проверку точного множества зависимостей и добавляет отрицательный контроль
удаления growth-only зависимости на реальных пакетах. До повторной проверки
reader это не полная приёмка B3.

ASan C1 не дошёл до тестов: Qt6 не разрешает неявное сравнение QJsonObject
с QJsonValue в четырёх EXPECT_EQ. Исправление теста `673f632b9` явно использует
`toObject()`; точность сравнения не меняется. Evidence неудачной сборки:
`17e5baadb0aece02aa278ef6323845d107ed163a`. Повтор использует новый runtime.

Normal B3 подтвердил9/14, отдельный reader B5 —24/24 на прежних primary.
ASan C2 завершён:9/9 unit,35/35 native (8 bound C0 +6 joint +3 diagnostics
+14 transfer),24/24 readers. Evidence `780b21afcd6e9d477bc7eb8181217c5a655fa0df`:
766 members/5 367 892 compressed bytes и actual libasan mappings проверены.
PulseLib `69d463aa50144a1c8ddb4a674bb900c2a07e769f`, numerical root
`6db2d5156fe51e03e1ebdeb1c256c5010dadb9b7`. Это scoped memory/lifecycle/transfer
проверка; она не охватывает последующие archive/dataset clock changes.

Между normal14 и ASan35 общие122 CSV:118 имеют полностью одинаковые non-time
columns,4 — разные signals при разной предыстории shared model time.
[Сравнение с SHA каждого исходного CSV](../../../Reports/StructTrain/TimeLearner/s07-capacitance-normal-asan-comparison-a1/comparison.json).
Полная cross-run waveform equivalence не подтверждена. Независимый
[clock-origin эксперимент](RecognitionClockOrigin-2026-11-02.ru.md) показывает
реальную зависимость старого источника от clock origin; не приписывать эти4
различия ASan или C0 без отдельного вмешательства. Кандидат исправления source
требовал собственной normal/ASan приёмки; этот следующий source срез уже принят
отдельно, см. текущий статус. На момент приведённого сравнения временные отчёты,
проверка рисунков и merge closure ещё ожидались; explicit API впоследствии
принят согласно C0Acceptance. По-прежнему остаются автоматическое
владение baseline алгоритмом C-trim, обновление карты после последующих edits,
native XML/Copy retention и полная матрица режимов. Этот срез не включает
полноценный bounded C-trim search: V2 с SyncCapacitanceTrim On ещё не разрешён.
