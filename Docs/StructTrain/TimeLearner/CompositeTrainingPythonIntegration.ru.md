# Python integration холодного composite Train: подготовка контракта

Рабочая область — root Python adapters/tests; Pulse/C++ service/codecs и
Console принадлежат отдельному этапу. Исходная точка root99534a29d8e4892ece1b4e13b4827a9ecc0103c6,
reader fix f71c16b46d3c8150eb860be2aeb6949e57247642 объединён merge commit.
Это code preparation, не подтверждённое выполнение новых моделей.

## Зафиксированная декларация

Cold schema6 явно содержит base_schema_version1–4 и composite_measurement.
Это отдельная плоская оболочка, а не вложение candidate-recovery schema5.
Проекция base сохраняет исходные значения и используется только при проверке;
нативному процессу, manifest и hashing передаётся исходный полный cold6.
Legacy cold1–5 не получает нового поведения при отсутствующем selector;
поле composite_measurement в этих версиях запрещено.

Method — declared-window-basin-necessity-v1. Точные поля policy и budgets
проверяются в composite_configuration.py; неизвестные поля не игнорируются.
Нужны как минимум два входа, N объявленных windows, неизменённая native частота
и шаг1/f, record_spikes=false, peak_selection=isolated_window. Context time
comparison tolerance строго меньше половины шага; поисковые допуски при этом
не заменяются timestep или процентом амплитуды. Attempt limits и group limits
имеют разные области действия. Малый положительный attempt budget может
завершить поиск честным budget_exhausted; его нельзя называть сходимостью.

Protocol4 связывается с исходными model/source/protocol IDs, pattern hash,
порядком stimulus/input IDs, объявленными окнами и теми же policies.
wave_assignment=window_only. Смена окна после наблюдения не допускается.
Нельзя подставлять schema3 peak packet вместо полного native N+2 group.
Declaration preflight не создаёт measurement, training certificate или PASS.

Новые JSON counts/schema IDs следуют native codec: конечное целочисленное
числовое значение, не bool, не больше2^53−1, с проверкой требуемой положительности.
1 и1.0 после JSON decoding имеют одинаковый математический смысл; byte SHA
документа и semantic identity остаются разными понятиями. Старые wire schemas
сохраняют прежние правила своих readers.

## Роли параметров

В новом Train comparison_radius_ticks, influence_absolute и influence_relative
из context_policy сохраняются для дополнительного прежнего v1 diagnostic/
witness codec и проверки допустимого диапазона. Они diagnostic_only: не являются
новыми Train geometry factors и не требуют sensitivity positive control как
изменение измерителя обучения. Geometry repeatability, declared windows, source,
common-context integrity и соответствующие budgets имеют отдельные роли.
Preflight возвращает эту классификацию; метод не использует v1 influenceExclusive
как решение нового Train. Legacy schemas1–3 сохраняют прежнюю v1 семантику.

Для cold6 condition binding имеет собственную schema2 (это не schema2 managed
pipeline). Только после полной проверки исходного cold6 из operative condition
исключаются ровно эти три diagnostic-only поля. Их значения и semantic digest
сохранены отдельно в supplementary_diagnostics; полный pipeline/job SHA также
сохраняется. Invalid radius/NaN не получают scientific identity через strip.
Geometry/source/model, context baseline/time/repeatability/native probe budgets
остаются в condition. Для cold1–5 прежний binding schema1 не меняется; перенос
идентичного binary в другой каталог по-прежнему не меняет condition fingerprint.

## Следующая интеграция и проверка

Пока не реализованы и не приняты learned package5/certificate2/full group
writer/readers, cold6 не имеет статуса рекомендованного научного контура.
Нужны versioned dispatch learned/stopped, полный перенос N+2 primary через
load_case/snapshot/native artifact closure и source/storage/model bindings.
Diagnostic schema1 record не становится TrainingCertificate2 из-за успешного
чтения или geometry recomputation. Portable import не восстанавливает livelease.

Semantic proof ID сохраняет declared run/trial/group/attempt identity против
replay; переименование filesystem paths при сохранении bytes/packet IDs не
должно менять его. Model semantic hash относится к фактическому полному graph,
SourceOrigin отдельно хранит initial target-family lineage. Ни один из них не
подменяется document SHA или выводится из одного scalar результата.

Frozen Test сохраняет свою whole-response/global maximum и actual spikes
семантику; Train assigned-window criterion туда не переносится. Перед отдельным
Test должны быть зафиксированы полный model hash и реальный проверенный порог.
Partial/stopped результаты diagnostic-only, без научного PASS.

Проверки данного нового Python-кода ещё не выполнены. Все новые unit/native/
pipeline проверки выполняются на серверах из Git-pushed source; локально только
AST/static review. Общий runtime должен собираться из объединённого C++service+
Python closure: старый compiled runtime не подтверждает поддержку cold6.
