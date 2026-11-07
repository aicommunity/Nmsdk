# Fair-domain: парное штатное обучение, 07.11.2026

**Новый порядок расширил фактически проверенные геометрии, но ни один из восьми
Train не завершился с сертификатом.** Все исходы InvalidObservation. Это
измеренный отрицательный результат ограниченного поиска, не доказательство
PhysicalInfeasible. Отдельная завершённая диагностическая оценка64 проб
не обнаружила улучшения классификации при двух проверенных порогах.

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

## Диагностическая классификация и временные графики

Оценка использовала каждую из восьми фактических stopped моделей:64 полных
предъявления восьми PhaseA паттернов, inherited threshold без калибровки,
reset-per-trial, окно2с и одна позиция target. Во всех случаях наблюдения
полны и valid, learned-state hash при frozen evaluation неизменен.

| Порог | Случаев (Classic/Branch × Retry/Advance) | TP | FP | FN | TN |
|---|---:|---:|---:|---:|---:|
|0.0117|4, каждый|1|7|0|0|
|100|4, каждый|0|0|1|7|

Это diagnostic-only после незавершённого обучения, не independent Test и не
исторический порядок/ITI. Низкий порог даёт срабатывания на все отвлекающие
паттерны, высокий пропускает target. Два порога не доказывают NonSeparable
на всей сетке. [Приёмка первичных данных](FairDomainStockEvaluationVerification.json):
commit77748412dcdfe2a838b10dcfaba69bdac3001abe,5043 members/47970556B xz,
SHA256920397b42bd8ec191924c63579d02f9d94b1f92b7dfe6a8a194acc06d09cf59f.
Все members повторно проверены; process group закрыта, lease released.
Исходные наблюдения очереди сохранены в [журнале](FairDomainStockEvaluationJobs.json).

Полный воспроизводимый отчёт на M40:
`/media/user/Data/TimeLearnerRefactor/ReportsCache/stock-fair-frozen-normal-a1/index.html`.
Он содержит160 trial/soma pairs и9190 временных views;30302 файла/2077769934B.
Для каждой пары есть полный2с обзор и40 непрерывных50мс увеличений с общей
шкалой Y; дополнительные local-Y details показывают слабую динамику.
Данные не прорежены; PNG1920×960, минимум14.208px на native tick в увеличениях.
Потенциал сомы и реальные входные импульсы показаны на общей временной оси.
Полный cache хранится на M40, Git — сжатые primary, checksums и выбранные PNG.

[Ручная QA четырёх рисунков](FairDomainStockSelectedVisualQA.json) подтвердила
читаемость подписей и возможность рассмотреть слабую динамику. Это не ручная
проверка всех160 пар. Единицы потенциала остаются `model_units_SI_unverified`;
их нельзя автоматически называть вольтами или милливольтами.

Выбранные рисунки (относительные ссылки ведут к Git-артефактам):

- [Classic: target, полный обзор](../../../Reports/StructTrain/TimeLearner/s07-stock-fair-selected-visual-m40-a1/Classic-threshold-low-advance32-target-soma1-overview.png).
- [Classic: foil, полный обзор](../../../Reports/StructTrain/TimeLearner/s07-stock-fair-selected-visual-m40-a1/Classic-threshold-low-advance32-foil-soma1-overview.png).
- [Classic: слабая динамика и входной импульс,0.45–0.50с](../../../Reports/StructTrain/TimeLearner/s07-stock-fair-selected-visual-m40-a1/Classic-threshold-low-advance32-target-soma1-zoom-010-detail.png).
- [Branch: динамика при молчащем выходе,0.15–0.20с](../../../Reports/StructTrain/TimeLearner/s07-stock-fair-selected-visual-m40-a1/Branch-threshold-training100-advance32-target-soma1-zoom-004-detail.png).

В обзорах Classic отрицательные экскурсии совпадают с LT events; одна эта
картинка не устанавливает причинную роль торможения. В Branch detail в выбранном
интервале нет входного импульса, но потенциал меняется: молчание выхода не
означает отсутствия физической динамики. Следующий шаг — связать причины
InvalidObservation с измеренными пиками штатной пачки.

Нельзя заключить, что нужно лишь повысить budget, что исходная задача физически
невозможна или что fair traversal уже улучшил классификацию. Следующая
алгоритмическая проверка должна связать причины missing/ambiguous с фактическими
waveforms и параметрами, сохраняя исходный измерительный критерий и свежую
проверку всех входов. Старые августовские4/8–6/8 не отменяются этим экспериментом.


[Последующий аудит264 невалидных проб](FairDomainStockPeakAudit-2026-11-07.ru.md)
подтвердил wave arrays по CSV и разделил excess/missing maxima. Он не
повторял Train, не менял критерий и не устанавливает физическую невозможность.
