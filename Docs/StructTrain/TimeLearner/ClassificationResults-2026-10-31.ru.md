# Что подтверждено о классификации на 31.10.2026

Это сводка научного поведения, отдельно от PASS проверок реализации.
Временные графики и source/runtime receipts не заменяют измеренные TP/FP/FN/TN.

## Положительный двухпаттерновый контроль

В [production calibration bundle](../../../Reports/StructTrain/TimeLearner/s08-calibration-worker-normal-a1/README.md)
файлы `native-production/Classic-success/model.json` и
`native-production/Branch-success/model.json` содержат raw search и fresh
confirmation. В `calibration_proof.confirmation_assessment` у обеих моделей:
TP=1, FP=0, FN=0, TN=1; target даёт один спайк в разрешённом окне после последнего
импульса, сильно растянутый foil не даёт спайков во всём окне. Early/late target
spikes отсутствуют. N1, 2000 Гц, reset-per-trial, историческая same-matrix
калибровка. Это повторное предъявление после выбора порога, не независимая выборка.

Classic model revision
`00d2a426b0686efba5da9ea5d2378d8008e5fb9b19dc1fb347bf9d2c4584ddd1`,
threshold `0.003336969230622544`; Branch
`c07c70fb7841e84a8968e95772c734856150d5eff5244c953f1bcd313e8f9893`,
threshold `0.006293579947234118`.

Результат подтверждает возможность разделить именно эту пару. Один foil не
оценивает долю FP на широком наборе distractors. Source Train остаётся
`search_unresolved`; калибровка не создаёт сертификат сходимости обучения.
Нормальный и ASan контроль являются детерминированными повторениями реализации,
не независимыми статистическими обучениями.

## Измерительный PostTune и production Console

Более новый [production PostTune corpus](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-console-normal-a2/README.md)
содержит 18 настоящих Console jobs Classic/Branch N1, двух входов, 2000 Гц:
9 Calibrated, 7 SearchUnresolved, 2 BudgetExhausted. Здесь уже выполнены
измерительный поиск/проверка весов, реальный threshold grid и fresh confirmation.
Это другой протокол, чем фиксированный порог в ранних 20 evaluations ниже.
Off/KeepDone/Auto/Soma подтверждают ту же двухпаттерновую пару у обеих топологий;
Classic подтверждает также CanonRmin. Synthetic и другие отрицательные случаи
не объявляются физически неразделимыми из-за неудачи выбранной сетки.

[Графики native-контроллера](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-controller-visual-normal-a3/SELECTED_VISUAL_REVIEW.ru.md)
охватывают 24 диагностические транзакции и все 184 trial-soma pairs в полном
cache. На выбранных fresh confirmations виден target spike и нет foil spike
в объявленном окне. У части окон потенциал ещё не вернулся к rest-state:
длинные хвосты, поздние события и continuous stream этим не подтверждены.

Новые калибровки сохраняют исходный `search_unresolved` обучения. Вклад именно
структурного обучения в разделение этой пары не установлен; для этого нужны
сопоставимые baseline до/после обучения. Эти controls не являются независимыми
обучениями или восьмипаттерновой серией.

## Ранний контроль отдельных кандидатов PostTune

[Сорок Console-операций](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-worker-normal-a1/README.md)
root `c6410eecc67cdc27aa5d6c05ef40f81a174a4916` проверяют 20 export + 20 frozen
evaluations: Classic/Branch × N0/N1 × Off/KeepDone/CanonRmin/FlatLastR/
SearchSyntheticCandidate, два входа, 2000 Гц. Каждое evaluation содержит target
и явно изменённый foil, полные окна 0.4 s, reset-per-trial. Порог унаследован
фиксированным, нового подбора в этой проверке нет.

**Все 20 evaluations имеют TP=0, FP=0, FN=1, TN=1.** Это молчание на обоих
паттернах. Нулевой FP здесь не является успешной классификацией. Все исходные
training outcomes — `search_unresolved`. Четыре independent checks и 40 успешных
process executions подтверждают перенос, frozen identity, полные наблюдения и
корректность подсчёта, но не научный успех PostTune. SearchSyntheticCandidate
означает один запрошенный вектор Rs, а не выполненный поиск.

## Что ещё не доказано

После рефакторинга ещё не подтверждена работа полной восьмипаттерновой матрицы
с распознаванием target и малым FP на остальных семи, независимыми distractors,
перестановками предъявлений и изменением ITI. Это отдельные уровни проверки;
robustness не подменяет собственный сертификат сходимости обучения.

Августовские визуальные 4/8–6/8 остаются рабочими наблюдениями исходного
протокола с плохой разделимостью. Перестановки и увеличенный ITI тогда не
проверялись; новые критерии не отменяют исторический результат.
