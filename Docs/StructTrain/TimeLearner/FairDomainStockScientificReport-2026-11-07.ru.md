# Fair-domain: парное штатное обучение, 07.11.2026

**Новый порядок расширил фактически проверенные геометрии, но ни один из восьми
Train не завершился с сертификатом.** Все исходы InvalidObservation. Это
измеренный отрицательный результат ограниченного поиска, не доказательство
PhysicalInfeasible. Классификация новых моделей этим Train-сравнением не оценена.

## Условия

Classic/Branch × порог0.0117/100 × RetrySameCandidate/AdvanceUnassignedBurst.
Четыре входа,2000Гц, штатный NSPNeuronGen без дополнительной LTMembrane,
N1, CapturedPerInput, reference3; C-trim/PostTune/калибровка выключены.
ISI[0.01,0.08,0.16,0.24], amplitude absolute1e-5, relative0, sync0.02.
У обеих recovery политик allowance32. Никакие допуски или budgets ради PASS
не увеличивались. Все jobs и cold graphs сопоставлены с baseline до первого
native вызова; повторная сверка после полного Train подтвердила восемь пар.

Baseline: root84d6/Pulse416; candidate: root36f598/Pulse8f057. Rdk Core и
Console driver идентичны; Pulse Core меняет только BoundedTraining.cpp/.h.
Tool root00ebc7. Полные SHA, runtime и первичные данные —
[verification](FairDomainStockTrainVerification.json).

## Измеренное покрытие Advance

Геометрия здесь — записанная группа полного вектора L/Ns и управляемого входа;
число не означает полный просмотр всего допустимого search box. Measured
records и typed invalid witnesses учитываются раздельно. Ни один missing/ambiguous
пик не превращался в valid только по предсказанному времени прихода.

| Топология | Порог | Geometry groups: baseline → candidate | Measured candidates: baseline → candidate | Итог обоих |
|---|---:|---:|---:|---|
|Branch|0.0117|5 → 58|3 → 25|InvalidObservation|
|Branch|100.0|31 → 60|235 → 27|InvalidObservation|
|Classic|0.0117|2 → 59|1 → 27|InvalidObservation|
|Classic|100.0|5 → 47|51 → 15|InvalidObservation|

Во всех Advance случаях записаны33 typed invalid observations: allowance32
и следующее наблюдение, остановившее попытку. Больше геометрий не означает
больше пригодных измерений: при высоком пороге их стало меньше. Это следствие
изменившегося распределения конечного бюджета между длинами и сопротивлениями,
а не подтверждённое улучшение обучения или распознавания.

В четырёх Retry-контролях совпали полные hashes model packages и summaries.
[728 native CSV](FairDomainStockRetryCsvComparison.json) имеют одинаковые
множества путей, размеры и SHA256. Это подтверждает сохранение default поведения
в этих четырёх условиях; не переносится на Advance, frozen Test или всю матрицу.

## Доказательства и следующий шаг

В Git опубликован primary a1ea63709dbd9a40a54a0e0a0b38fee2b02f9af8:
2730 members/21571700B xz,16 run manifests; каждый member и351 tool source hash
сверены. На сервере выполнены production primary/CSV audits обеих серий;
подтверждены full process-group closure и released lease. Исходный launcherA1,
отклонённый до worker из-за36h лимита, сохранён; native серия не повторялась
ради исправления publisher. Архив исключает только доказанные duplicate glog
aliases с отдельным журналом; оригинальные файлы не удалялись.

Следующая оценка использует каждую из восьми фактических stopped моделей и
потому остаётся diagnostic-only. План:64 полных предъявления восьми PhaseA
паттернов, inherited threshold без калибровки, reset-per-trial; затем временные
графики всех160 trial/soma pairs с входными импульсами. Это не independent
оценка, не исторический порядок/ITI и не завершённое обучение.
[Задание и исходное наблюдение очереди](FairDomainStockEvaluationJobs.json).

Нельзя заключить, что нужно лишь повысить budget, что исходная задача физически
невозможна или что fair traversal уже улучшил классификацию. Следующая
алгоритмическая проверка должна связать причины missing/ambiguous с фактическими
waveforms и параметрами, сохраняя исходный измерительный критерий и свежую
проверку всех входов. Старые августовские4/8–6/8 не отменяются этим экспериментом.
