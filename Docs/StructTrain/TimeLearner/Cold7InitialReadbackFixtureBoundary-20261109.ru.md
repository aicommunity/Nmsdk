# Cold7 initial readback: исправление последовательности fixture

Исходный Root `956443560ebdb788a0642856381c9c6a7a554b76`, неизменённый PulseLib
`f7a0e3e63ec29d4647790a695606d1ca32164ef3`. Реальный native48 A1 собрался,
но первая common-codec leaf выполнила11 tests:9PASS/2FAIL; остальные37 не
выполнялись. Это не48PASS. Frozen A1 не изменяется и не перезапускается.

Оба failed IDs — NativeCandidateWindowCold7.ClassicInitialDeclarationUsesActualParametersRatherThanTemplate
и BranchInitialDeclarationUsesActualParametersRatherThanTemplate. В общем
helper `ActualCold7InitialReadback` первый ApplyNativeParameters вызывался на
Idle executor после уничтожения ещё не использованного actor. Production
`NativeModelEditor.cpp:883` корректно требует AtEditBoundary. По
`NativeProbe.h:86–89` это owned terminal executor с уже потреблённым raw result
и восстановленной routing/presentation; Idle этому условию не удовлетворяет.
Уничтожение actor не создаёт пробу и не является её потреблением.

Изменён только fixture-порядок. До edit один реальный reference-purpose N+2
characterization проходит существующий f.Run, scheduler и production native
runner. Проверяются measurement, Completed/owned edit boundary, реальные
1group/N+2raw probes/samples. Logical group не объявляется training-consumed;
allN references и certificate отсутствуют. Existing SaveCandidateWindowGroup
сохраняет фактические CSV/matched witness/boundary. Затем actor освобождается,
снова проверяется реальный edit boundary, и public editor применяет L3/Ns2.

Исходные assertions сохранены: captured declaration берёт действительные
L/Ns/explicitRs, тогда как исходный modelSpec остаётся L2/Ns1 с отсутствующим
explicitRs; windows/codec roundtrip/C0-off checks остаются. Characterization
peak не становится целью declaration и не используется для её заполнения.
Scope JSON теперь честно сообщает фактическую characterization, вместо0groups.

Новые primary paths: classic-native-window5/cold7-pre-edit-characterization
и branch-native-window5/cold7-pre-edit-characterization. Они различны и не
конфликтуют с прежними cold7-native-initial-declarations directories. Для
каждой topology сохраняются raw-0..3.csv, matched-witness.json,
window5-boundary.json и существующие after-model/boundary материалы.
Итого16 новых exact primary paths (8 на topology); следующий job manifest
должен явно потребовать их вместо предположения, что прежних185 rules достаточно.

Source-only исправление: production boundary guard, C++ библиотеки, физика,
математические допуски и test IDs не менялись. Локальные C++/модели/тесты и
серверные действия не выполнялись. Следующий серверный cohort должен реально
проверить обе topology и сохранённый declaration-vs-template смысл.
