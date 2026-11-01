# Измеренное предложение длины — незавершённая приёмка

Feature изменяет порядок кандидатов V2, сохраняя CapturedPerInput, исходные
допуски, fixed anchor, topology order, native scheduler и все search budgets.
[Алгоритм в PulseLib](../../../Libraries/Nmsdk-PulseLib/Docs/MeasuredLengthProposal.ru.md).

Исходный контроллер перебирает ближайшие длины. Серверный контроль на Elder
root a558b66beb7e8b5ca33974875cf094dd826a5080 /PulseLib456a5ab воспроизвёл4/4
ожидаемых отказа: Classic/Branch ×N0/N1, четыре разрешённых кандидата, измеряемая
по заданному отклику точка L12 вне ближайшего перебора. Это настоящий production
BoundedTrainingSession/ProbeRecorder, но заданный response oracle не является
физическим нейроном. Supervisor завершил воспроизведение failed assertions;
сами исходные tests не являются PASS.

Proof commit 78c32cb3318b6a614ae5703a3c8c6fe66ee60e42:
[26 primary members/8840 B](../../../Reports/StructTrain/TimeLearner/s07-measured-length-baseline-normal-a1/README.md).

Новый MeasuredLengthSearch использует минимум три различные завершённые длины
при одинаковых Ns/Rs и остальных параметрах. Наблюдаемый monotone interval
предлагает целый bracket midpoint либо bounded secant estimate. Ни прогноз,
ни clipping по bounds не подтверждают существование/время пика или сходимость.
Немонотонность, конфликт повторов или неопределённый знак возвращают обычный
перебор; исходные trial/model revisions остаются в evidence. N0 ждёт все
обязательные повторы; N1 оценивает физический domain новой геометрии штатно.
Shared Branch перемещения остальных attachments не смешиваются в один trend.

В production root package добавлен воспроизводимый эксперимент:

```text
python3 -m Scripts.StructTrain.TimeLearner.length_proposal_experiment \
  --templates PREPARED_JOBS --baseline-runtime OLD.json \
  --current-runtime NEW.json --output NEW_DIRECTORY
```

Четыре byte-identical job declarations для обоих runtime: Classic/Branch,N0/N1,
2inputs/2000Hz, ISI [.01,.08], начальные L[2,1], Ns1 и исходные Rs. Диапазон
L0=2..16, anchorL1, Ns/Rs фиксированы, исходные CapturedPerInput/tolerances/
profiles сохранены. Полное окно0.5s с ordered whole-burst assignment;4 кандидата
N0 или5 N1 учитывают дополнительный native domain realization исходной точки.
Декларация не меняется между baseline/current. Исходы SearchUnresolved допустимы;
приёмка proposal path требует фактического измеренного нового скачка длины,
fresh all-input certificate, normal/ASan и temporal evidence. Это отдельный
контроль алгоритма, не independent recognition Test.

Normal/ASan сборки и14 новых helper/controller checks ещё в процессе проверки;
native regressions, cold A/B, отчёты и merge children-first пока не приняты.
Полные этапы6/7/11 открыты; legacy EstDelayPerSeg/gamma не объявляются действующими
V2 полями. Новые C-trim, общая A* или дополнительная физика не вводятся.
