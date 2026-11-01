# N0: измеряемый порядок кандидатов — принятый подэтап

Исправление ограниченного поиска N0 принято адресно. Это **не закрытие полного
этапа7** и не подтверждение классификации. CapturedPerInput, исходные допуски,
fixed anchor, порядок входов Classic/Branch и fresh all-input gate сохранены.

Функциональный Core: PulseLib c25db29404b544311a3256336c0c43991a384e12,
численный root942e5df4559467a9a19c56755f945ce6501e7780. Последующие PulseLib
commits меняют документацию; merge develop38edfcad7983478a7e2ca736c32ae2703861c1fd
имеет тот же Core tree64cdc352af865dc0e860ea05fb2c6d9799ccc36e.
Root feature фиксирует этот опубликованный child; root merge следует отдельно.

## Дефект и изменение

Раньше NextCandidate расходовал бюджет на все длины при текущем Ns, а затем
переходил к следующему Ns. При лимите3 получались L1/Ns1,L2/Ns1,L3/Ns1 даже
после реально измеренного подходящего timing при L2. Ближайший L2/Ns2,
исправляющий амплитуду в controlled fixture, не проверялся. SearchUnresolved
был честным исходом; дефект — неиспользование измеренной информации при выборе.

Теперь после **полной требуемой группы повторов**, при улучшении измеренного
rank и withinTiming=true/withinAmplitude=false предлагаются Ns+1 и Ns−1
на полной измеренной геометрии. Предложение не доказывает монотонности,
сохранения timing или сходимости: каждый новый кандидат получает fresh anchor
и input probes с актуальной revision. Без улучшения продолжается базовый перебор.

```text
consume complete valid measurement/repeat group
if measured rank improves:
    remember best
    if N0 and timing ready and amplitude outside original tolerance:
        queue legal neighboring Ns on this full geometry
next candidate:
    issue unseen legal priority vector, otherwise normal enumeration
    perform real required repetitions at that same candidate
on local budget exhaustion:
    restore and freshly remeasure best
finish only through independent fresh final verification of every input
```

PrepareCandidate сохраняет Branch shared-bank legality и явное перемещение
только ещё не посещённых upstream attachments. Последний anchor не изменяется.
Выданные полные векторы не расходуют бюджет повторно; обязательные повторные
измерения и свежее восстановление best не удаляются. N1 и его domain mesh этим
подэтапом не изменены. Numerical stability по-прежнему проверяет native adapter.

## Проверки и доказательства

|Контроль|Опубликованный результат|
|---|---|
|Unchanged baseline|[2 expected failures](../../../Reports/StructTrain/TimeLearner/s07-n0-candidate-order-baseline-asan-a1/README.md), root31934548524ab0da77311f4fc046db05cdf69b81/Pulsef23d1b8d;21 members/10724bytes. Supervisor0 означает успешное воспроизведение двух failing tests, не PASS самих tests.|
|Normal regression|[31/31 native +4/4 reader](../../../Reports/StructTrain/TimeLearner/s07-n0-candidate-order-normal-a2/README.md), proofc9c65de9b12989b0ddcb51da5924f1854a56f88e;205 members/346080compressed bytes.56 реальных probes.|
|ASan regression|[31/31 native +4/4 reader](../../../Reports/StructTrain/TimeLearner/s07-n0-candidate-order-asan-a2/README.md), prooffb1f578b94395fbb786e7e6658b9e0f704f341ac;201 members/348832bytes. Gtest2764.079s; reader0.159291s.|
|Configured N0 repeats, normal|[3 native +3 actual-data checks](../../../Reports/StructTrain/TimeLearner/s07-n0-candidate-order-repeated-normal-a1/README.md), proofa0ff3273501466677d34423d3c2a5d52d36766d3;125 members/104708bytes,48probes/10groups,108 unchanged native files.|
|Configured N0 repeats, ASan|[3 native +3 actual-data checks](../../../Reports/StructTrain/TimeLearner/s07-n0-candidate-order-repeated-asan-a1/README.md), proof6e596751df9be629b6480d249756f72dd9874a5a;125 members/108188bytes,48probes/10groups,108 unchanged native files.|
|Base temporal normal|[56trials/84soma pairs](../../../Reports/StructTrain/TimeLearner/s07-n0-candidate-order-visual-normal-a1/README.md),077334d7fb76bc6d05983a892570f5178ce9b21d;3 N0 checks +3 shared-reader legacy regressions;8 PNG прямо просмотрены в QAfd90e862d4f817cc2269ad9c46ba9c8c52aeb5a8.|
|Base temporal ASan|[56/84 и3 checks](../../../Reports/StructTrain/TimeLearner/s07-n0-candidate-order-visual-asan-a2/README.md),32cca42c0275ce92bee3a93f37970448f0bf9526;142 metadata members/96408bytes.8 independently rendered PNG побайтно совпали с reviewed normal.|
|Repeat temporal normal|[48trials/72soma pairs и3 checks](../../../Reports/StructTrain/TimeLearner/s07-n0-candidate-order-repeated-visual-normal-a1/README.md),78a12250c220c1e480559ab450ee07f0220298a0;119 metadata members/81904bytes +4 PNG/618333bytes. QA252ca56bf3a492130d9193efd8edb3c57875a38f — прямой просмотр всех4.|
|Repeat temporal ASan|[48/72 и3 checks](../../../Reports/StructTrain/TimeLearner/s07-n0-candidate-order-repeated-visual-asan-a1/README.md),4d024c5f822cc6265bbfc0ac017f90890f0addfb;112 metadata members/81664bytes.4 PNG побайтно совпали с reviewed normal.|

Все outer/member hashes локально проверены после получения через Git. ASan
leak detection выключен; leak freedom не заявляется. Source/runtime/binary
численных jobs не менялись в ходе исполнения. Дополнительные repeat suites
повторно использовали тот же executable без rebuild после terminal основного job.

Пять новых controlled-kernel cases проверяют обе топологии, сохранение length-only
бюджета, возврат к длинам после плохого соседа, dedup и полные repeated samples.
Это actual production BoundedTrainingSession/ProbeRecorder, но response oracle
не является физическим нейроном. Реальные native regressions проверяют
edit/growth/readback Classic/Branch при2000/20000Hz и training при2000Hz;
configured schema2 отдельно подтверждает два физических измерения кандидата.
Native fixtures сохраняют SearchUnresolved и fresh negative certificates;
их нельзя выдавать за успешную физическую сходимость или recognition Test.

Термин warm в fixture означает уже построенный объявленный граф, не продолжение
ранее обученной модели/checkpoint. Saved-state replay августа здесь не выполнялся.

## Ошибки вспомогательной проверки не скрыты

Первые [normal](../../../Reports/StructTrain/TimeLearner/s07-n0-candidate-order-timeout-normal-a1/README.md)
и [ASan](../../../Reports/StructTrain/TimeLearner/s07-n0-candidate-order-timeout-asan-a1/README.md)
попытки остановлены production wall budget300s во время editor20000Hz. Повторы
стартовали только после actual terminal timeout, на том же binary, с3600s.
Это не full JUnit PASS и не доказательство дефекта алгоритма.

Первый independent reader включал обязательный service_model.json в glob trial
файлов. Исправление71878cb5435f75a413e979be5fba3071fdbd847d требует exact набор
нумерованных probes **и** отдельный valid model, пересчитывает его canonical hash
и сверяет actual revision. Первые reader/publisher failures сохранены в proof.
Ни численное обучение, ни исходные данные ради исправления reader не менялись.

## Граница приёмки

Git содержит сжатые первичные данные/модели/метаданные и12 выбранных normal PNG;
ASan использует только exact reviewed-image references. Full derived caches
остаются M40 Data. Manual QA относится к final input0/first soma selected views;
остальные trials/channels проверены автоматически. Нет утверждений о full-cache
ручной приёмке, SI units или ответах после записанного окна. valid/complete на
графике описывают данные, а не сходимость обучения/успешное распознавание.

Открыты полная normalization/physics/frequency/dimension/mode matrix, native
поведение informed proposals на более широких физических случаях, N1 search,
quantized/best-effort semantics, C-trim, исторические и independent scientific
controls. CapturedPerInput не заменён общей амплитудойA*. Научного PASS и полного
закрытия этапа7/плана0–12 этот подэтап не создаёт.
