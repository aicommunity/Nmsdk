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

На обоих workers завершены39 production helper/controller checks без skips,
включая14 новых:6 helper и8 контроллерных сценариев. Сборки используют root
1cdbdaa2b072715d623cc00de62e0ca13c1ca918 и PulseLib
a728d97110b706bd7869039557de957ea299c6ea. Native regression28 на каждом worker
ещё выполняется; его результат не выводится из helper PASS.

На Elder завершены8 реальных cold A/B и4 actual-template generator checks.
Byte-identical jobs дают одинаковые initial graphs, CapturedPerInput references
и допуски между baseline/current. Старый порядок измеряет L2/3/4/5 (N1 ещё6),
новый L2/3/4/9 (N1 затем5). Все8 исходов SearchUnresolved с отрицательными свежими
all-input certificates: фиксированные Ns/Rs не восстанавливают амплитуду.
Измеренный скачок не объявляется сходимостью или классификацией.
[Normal primary](../../../Reports/StructTrain/TimeLearner/s07-measured-length-native-normal-a1/README.md),
commit7c8820398466341e6713c5c32ffc3cee585c8988:460 проверенных members/629680 B.
Python experiment root41261d366b4d7537dcb24e7e7e22bafad5c6c8ed; Console/Pulse
code одинаков с binary root1cdbdaa2b. Первый generator attempt остановился до
моделей на progress-array/strict-object mismatch; receipts сохранены в primary.

ASan cold A/B, native regressions, повтор прежних положительных N1-контролей,
полные temporal reports/визуальная проверка и merge children-first пока
не приняты. Full figure cache размещается только на M40 Data; в Git остаются
сжатые primary, metadata и выбранные просмотренные рисунки.
Полные этапы6/7/11 открыты; legacy EstDelayPerSeg/gamma не объявляются действующими
V2 полями. Новые C-trim, общая A* или дополнительная физика не вводятся.
