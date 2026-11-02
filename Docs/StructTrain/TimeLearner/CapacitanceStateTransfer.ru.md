# Сохранение C₀ при Train → Test

Реализация следующего среза; численная серверная приёмка ещё не проведена.
PulseLib: `922ba91f71075b296a1c808e561b69fdd71f6255`.

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

Остаётся выполнить normal/ASan и reader gates, построить временные отчёты,
проверить выбранные рисунки и merge closure. Также остаются автоматическое
владение baseline алгоритмом C-trim, обновление карты после последующих edits,
native XML/Copy retention и полная матрица режимов. Этот срез не включает
полноценный bounded C-trim search: V2 с SyncCapacitanceTrim On ещё не разрешён.
