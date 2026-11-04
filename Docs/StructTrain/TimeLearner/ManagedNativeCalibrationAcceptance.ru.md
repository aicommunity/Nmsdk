# Managed native calibration: normal приёмка

На Elder source `b5a2c9f0a5f558393c4e73a37c06d7d1b98274d3` прошёл4/4 actual checks без failures/errors/skips. Каждый случай использовал новое Exact N1 состояние из [прошедшего managed Train](ManagedNativePipelineAcceptance.ru.md), а не исторический готовый нейрон. Повторного Train в этой операции не было.

Для Classic/Branch × ModelSpec1/2 выполнено:

1. Проверка полного Train/export/frozen primary. При исходном пороге1.0 наблюдения complete,valid,nonspiking.
2. Предложение четырёх порогов по измеренным native LTZone.Potential: между различными уровнями, внешние controls и исходный порог. Предложения не считаются проверкой спайкового критерия.
3. Настоящая нативная матрица для каждого из четырёх порогов и свежая confirmation выбранного порога. Измеряются все четыре объявленные пробы, не только target.
4. Отдельный managed native frozen Test калиброванного пакета: полное состояние до/после одинаково.
5. Отдельный silent-only grid с исходным порогом1.0: NonSeparable, source_restored=true, отсутствует calibrated_package и конечная модель полностью совпадает с исходным разобранным пакетом по всем полям и semantic hash.

| Случай | Выбранный порог, model units/SI unverified | Frozen TP/FP/FN/TN |
|---|---|---|
|Classic ModelSpec1|0.004780132099175549|2/0/0/2|
|Classic ModelSpec2|0.004780132099175549|2/0/0/2|
|Branch ModelSpec1|0.009589717471100379|2/0/0/2|
|Branch ModelSpec2|0.009589717471100379|2/0/0/2|

Сетка и frozen Test содержат две различные последовательности ISI: target `[.01,.03]`, foil `[.01,.24]`, порядок target,foil,foil,target; окно0.4s и reset-per-trial. Это **Historical Same-Matrix calibration** двухвходового engineering LT профиля. ModelSpec1/2 проверяют кодирование/перенос, а не независимые случайные повторения. Устойчивость к ITI, полный набор позиций target, continuous stream, независимый Test и научная классификация stock четырёхвходовой модели не установлены. Августовские наблюдения не пересматриваются. Из этого набора нельзя выделить причинный эффект LT-мембраны: парного вмешательства LT/no-LT нет.

## Процессы и сохранность модели

Реально запущены12 отдельных managed native units: grid,fresh-frozen,silent-control для каждого случая. В каждом lease/unit binding проверены точные IDs и kernel closure; источник Solo и исходный recognition package не менялись. Все schema3 leases released; operational global lease освобождён только после свежего подтверждения закрытия12 внешних групп и controller. Controller512MiB,native4GiB,aggregate4.5GiB. Расчётные методы выполнялись штатным native scheduler без вложенных Calculate из Python.

Runtime — неизменяемый root `f679d0410dd00a36995f9d32cc03812438819bb7`, Pulse `541bf89b9966f63ca5131fa57a31a9ae3f5820ea`; SDK не пересобирался. Физика, морфология, индивидуальные Rs/C, CapturedPerInput, опорный вход и допуски обучения не менялись. Калибровка меняла только разрешённое состояние порога через production transaction.

## Доказательства и оставшаяся работа

Proof `6d1e36ff2c990eace565745db52703fbea231ed9`, parent accepted8b231dae9. [Primary/outcomes/closures](../../../Reports/StructTrain/TimeLearner/s10-managed-native-calibration-normal-a1/README.ru.md). Сжатый первичный архив8 922 700B,SHA256 `db5b95d9b993572260492a813e9260a69b2b34036cd69706fbf303c23aee7a7b`. Локально независимо проверены все1462 member hashes и285 source Git blobs; [receipt](ManagedNativeCalibrationVerification.json). Первоначальный silent frozen результат при1.0 сохраняется в отдельном [отчёте](ManagedNativePipelineVisuals.ru.md), не заменяется новой оценкой.

Полные temporal reports всех кандидатов, confirmation, silent controls и frozen Test запущены на M40, source `b014bb245420e4bc812a923873344bfab17e3773`, readback `s10-managed-native-calibration-visual-a1`; пока результат plotting gate не принят. Полный кэш остаётся на Data, в Git должны попасть только выбранные рисунки и контрольные суммы.

Implementation branch пока не merged в develop. Эти данные закрывают normal-подэтап managed calibration, не весь этап8/10. Открыты M40 ASan/kernel62 и actual pipeline/calibration, актуальный joint SDK, положительные N0 и остальные profiles/modes, owned PostTune/live finalization, cancellation/recovery и общий production dispatcher. Все этапы1–12 остаются частичными.
