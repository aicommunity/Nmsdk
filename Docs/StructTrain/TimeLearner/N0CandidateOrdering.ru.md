# N0: порядок проверки длины и числа синапсов

Ветка codex/timelearner-n0-candidate-order от согласованного develop
1d4822af22e05b741e4a1c779cf99ba05cb0a1fa / PulseLib f23d1b8dee908ddfdc549619b754875fc627ce9b.
Предыдущий scoped live pipeline принят normal/ASan с полными Git primary;
полные этапы0–12 остаются открытыми.

## Проверяемая гипотеза

Текущий NextCandidate сначала перебирает все длины при текущем Ns, затем
следующее Ns при всех длинах. При maximumCandidatesPerInput=3 и широком
диапазоне L получаются (L1,Ns1),(L2,Ns1),(L3,Ns1). Даже если измерение L2
подтвердило timing, ближайшая нормализация (L2,Ns2) не проверяется. Результат
SearchUnresolved честен; проблема состоит в расходовании ограниченного
бюджета без использования уже измеренной информации.

Controlled kernel fixture использует production BoundedTrainingSession,
ProbeRecorder/валидаторы и per-input captured references. Два входа:
anchor L1/Ns1/Rs10 фиксирован, первый допускает L1..20/Ns1..2. Ответ таблицы
имеет допустимое timing при L2 и captured raw amplitude при Ns2. Остальные
длины не синхронизируются. Это oracle алгоритмического unit-test, не опыт
на физическом нейроне и не свидетельство классификации.

Сначала новый test должен воспроизвести SearchUnresolved текущего ядра на
обеих топологиях. XML/process/runtime source snapshots сохраняются. Только
после этого меняется порядок предложений; CapturedPerInput, tolerances,
Classic/Branch input order, fixed anchor и fresh final verification сохраняются.

## Направление исправления и ограничения

После завершения всех обязательных повторов кандидата, если он улучшил
измеренный rank, timing допустим, но amplitude вне допуска, приоритетно
предложить соседние Ns на этой геометрии. Это предложение, не доказательство
монотонности или сохранения timing: новый кандидат получает fresh anchor/input
пробы, полную revision и все прежние проверки. Дубли full parameter vectors
не расходуют бюджет повторно; заданные candidate repeats остаются отдельными
реальными измерениями. При отсутствии улучшения возобновляется ограниченный
основной перебор. Никаких выводов PhysicalInfeasible или Exact из stall/cap.

Проверки: controlled baseline/fix Classic/Branch, не ухудшить чистый поиск L,
Ns128/quantization, repeated observations, Branch shared banks, бюджет/stop,
invalid peaks и финальную проверку всех входов. Нужна последующая реальная
native N0-проверка edits/амплитуд/времени; unit oracle её не заменяет. N1 dynamic
mesh и полный profile/frequency/dimension coverage остаются отдельным остатком.

## Baseline M40

Неизменённое ядро f23d1b8d с root31934548524ab0da77311f4fc046db05cdf69b81
воспроизвело оба expected failures: SearchUnresolved, сохранён L2/Ns1,
L2/Ns2 не измерен. ASan native XML:2 cases/2 failures; supervisor0 означает
успех воспроизведения ожидаемого отказа, не прохождение tests. Runtime
before/after совпал. Первичные данные опубликованы ниже; приёмка исправления ещё не завершена.

Baseline опубликован: Reports/StructTrain/TimeLearner/s07-n0-candidate-order-baseline-asan-a1,
commit72d9df51a9684f1bdd485c7998ae065eb6defaa4. Проверены outer hashes и
21 member; архив10724 bytes. Исправленный root942e5df45 ожидает ASan приёмку.

## Обязательный независимый reader

Набор test_n0_candidate_regression_evidence проверяет фактический успешный
процесс с loaded-file provenance, точное множество31 JUnit cases без skips
и все4 объявленные warm/cold Classic/Branch N0 phases. Число фаз не выводится
из случайно имеющихся файлов. Каждый реально записанный JSON/CSV проверяется
production audit_probe, а references/candidates/final certificate сверяются
через audit_training_summary. Отрицательный сертификат не превращается в
классификационный verdict.

Четыре reader checks включают потерю финального trial, подмену residual/model
revision/Exact, изменение captured reference и candidate timing, обрезанный
CSV. Проверки используют копии фактических данных, не меняя численный source.
Normal reader PID2312312 и ASan reader PID154042 запущены на metadata root
a86f96ee5d015b304c63e7070b733477ed69891b и ждут успешного завершения соответствующей
численной попытки. Результатов4/4 пока нет. Report scope отдельно объявляет
четыре фазы обучения; editor-only waveform не выдаются за покрытые этим отчётом.
