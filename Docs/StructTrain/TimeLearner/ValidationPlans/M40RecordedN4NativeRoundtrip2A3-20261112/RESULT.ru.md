# Полные recorded N4 roundtrips:2/2 native PASS

SDK448b153f2fea3486ff40f3a626b8f1110b9e3ee2/Pulse7b524b8, Toold33af820e, runtime0d3a7ab04bd65dc01195930284fc2ed5679c9e9d68dc7e1888fbab5b5e5aa3f9. Оба actual C++ IDs completed/valid/passed, exact JUnit1+1, source и staged DATA bytes неизменны. Whole outer+2 children closed, supervisor reason=null/record_errors=[], original main exit0 до cleanup, один lease released. Tool/source snapshots before/after побайтно равны; оба native gates проверили runtime.

Каждый case импортировал полный stopped model, native Build/Init, экспортировал и повторно импортировал его в новом fixture. Сравнены semantic learned-state view/actual revision/ledger и каждый stimulus/Soma sample до/после. Оба показали4 stimulus edges и excursion>1e-6. Raw small proofs в completed; полный наборmodel/summary/response files привязан size/SHA в artifact-records.json, будет сохранён отдельным lossless corpus. Допуски не ослаблялись.

Classic остаётся invalid_observation и model35d849faa2aaea5d2620f0fd59d9934c77760b7fde0dd49d3284539f69f68263; Branch остаётся budget_exhausted и modelef c6bacd (полный SHA в phase-times). Certificate null; live search/controller checkpoint не восстановлены. Это model transfer/physical response приёмка, не cold retrain, calibration или классификация. Raw model JSON sizes175521654/192607805B на входе; исходные уникальные модели уже опубликованы в strict N4 primary.

Точные per-phase times в двух original phase-times.json. Они не разбивают весь wall test time: current RecoveryBoundaryResponse fixture использует full IdentifyModel per sample, в отличие от production observer; speedup старого/нового binary по этому прогону не заявляется. См. LargeModelRoundtripTimingReview-20261112.ru.md.

A1 directory admission отказ и metadata18A1 test mismatch сохранены; A2 не запускался. Source model/критерии/budgets A3 не менялись. Осталось: полный compact corpus, independent DATA readback и отдельный before/after performance; общий план не завершён.
