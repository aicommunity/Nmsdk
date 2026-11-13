# Отдельный холодный контроль N0 после coupled N1

Постановка14.11.2026. [Classic N1](ClassicCoupledCold4ScientificReport-20261114.ru.md) не имеет jointly-ready кандидатов и остановлен на ambiguous input0; [Branch N1](N1CoupledScientificReport-20261113.ru.md) имеет одну локальную jointly-ready input2, затем ambiguous input1. Требуется проверить, меняется ли эта траектория при штатной N0-нормализации. Успех N0 не предрешён; отрицательный результат сохраняется.

## Единственный объявленный фактор

Меняется механизм нормализации: N1 управляет TipRs при Ns=1; N0 управляет целым Ns в пределах1..128 у неопорных входов при фиксированном исходном индивидуальном Rs. Опорный входN−1 сохраняет Ns=1, исходный Rs и длину. Изменение допустимого актуатора и его границ является частью фактора N0/N1; это не изолированное сравнение одной числовой переменной при одинаковом поисковом пространстве.

Физический начальный граф и исходные input L/Ns/Rs сохраняются. Stock storage без LTMembrane,2000Гц, пачка target, reference capture windows, full observation candidate domain, CapturedPerInput и исходные ampabs1e-5/relative0/min1e-6/sync.02 сохраняются. Общие budgets wall1800s/probes128/edits1280/candidates128/input/sweeps4/invalid4 не увеличиваются;300s process finalization отдельно, только при Train. C-trim/PostTune/threshold calibration выключены. Каждая проба проходит штатные native механизмы; старое learned state не импортируется, Train заново захватывает references.

## Production-путь

Команда stock-candidate-window-study prepare-N0 принимает только исходный schema3 N1 full-observation план с согласованными job/condition/runtime/initial fingerprints. Создаёт новый schema4 план с algorithm id stock-observation-domain-cold8-N4-N0-control-v1 и именами Classic-stock-cold8-N0 / Branch-stock-cold8-N0. Исходные файлы не меняются. Новый job и ConditionSpec пересчитываются штатным сериализатором; N1 fingerprints не переносятся на N0 как идентичность условия. Поддержка старых plan1–3 сохраняется.

Штатный stock-candidate-window-study preflight/train использует production run_job, immutable runtime, owned processes, cold identity comparison и полный DATA/physical audit. Новый Python-only оператор не требует смены C++ SDK: всё нейронное исполнение использует уже проверенный Pulse7c6c94785af0c83104d348bb3b733ed1f149c8a8/root74e5d206d4b619fcf81f77f11b54ebec7b8f0f6e runtime105ccc46bf2d23aa093ee6ec5fb088d9f33faa8e572f8191869f8cc279377a8a. Эффективная поддержка N0 всё равно требует native preflight.

## Проверки и порядок

1. На M40 и Elder:11 declaration regressions (4 recovery,4 full-observation,3 N0), без skip. Проверяется неизменность физики, references и budgets; Ns128 только неопорным, индивидуальный фиксированный Rs, отказ stale digest/повторного N0/сдвига окон/подвижного anchor/ослабления допуска. Это проверки деклараций, не научная проверка модели.
2. На M40: оба настоящих N0 preflight через public CLI и исходный runtime, exact cold identity и job bindings, closure. До их приёмки Train не запускать.
3. Два отдельных холодных Train, по одному на топологию, последовательно на immutable M40 runtime. Два завершённых N1 controls уже есть на том же SDK. Не требовать различий результата ради PASS: проверяется применение режима и честность измерений.
4. Сохранить весь primary в сжатом Git bundle, прочитать typed recovery и measured histories отдельно, проверить frozen конечное состояние при отдельно объявленном Test. Если Train остановлен, diagnostic Test не выдавать за законченное обучение.
5. Отчёт: исходы/остатки/Ns/quantization/saturation/budget и assigned waveforms с actual inputs, читаемый масштаб и selected originals. Совпавшие детерминированные состояния не считать независимыми seeds.

Train и успех этапа11 пока не подтверждены. Даже совпадение N0/N1 исходов не доказывает эквивалентность алгоритмов, глобальную недостижимость или отсутствие влияния физики. Исходные августовские наблюдения относятся к своему протоколу и сохраняются.

## Проверено и запущено14.11

[Declaration11/11 M40](ValidationPlans/M40StockN0DeclarationUnitA2-20261114/RESULT.ru.md) и [11/11 Elder](ValidationPlans/ElderStockN0DeclarationUnitA3-20261114/RESULT.ru.md) приняты; исходные ранние отказы launcher сохранены. [Настоящие оба preflight1/1 M40](ValidationPlans/M40StockN0PreflightA1-20261114/RESULT.ru.md) приняты на прежнем native SDK. После этих gates запущен отдельный холодный Classic N0 s11-stock-n0-classic-train-m40-a1. Branch N0 ожидает закрытия Classic; параллельные изменения runtime исключены. Scientific outcome ещё неизвестен; он не выводится из успешных предварительных проверок.
