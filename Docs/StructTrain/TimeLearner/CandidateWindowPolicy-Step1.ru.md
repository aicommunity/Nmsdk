# STEP1: deterministic candidate-window arithmetic

Source-only pure production module: CandidateWindowPolicy.h/.cpp. Runtime/native/Train integration не выполнена и defaults/frozen paths не меняются. Локально compilation/numeric tests запрещены и не запускались.

Trust split: raw arithmetic helper принимает недоверенные числовые факты, возвращает только data/reasons; ни waveform/residual, ни valid=true, ни training proof в API нет. Typed overload требует opaque reference seed, не имеющий public raw constructor; STEP1 не создаёт seed minting factory. Actual candidate/map/source admission и matching owner family/reference proof остаются обязательными для следующего bridge.

Fast CMake target Test_PulseLib_CandidateWindowPolicy компилирует настоящий production .cpp и существующий TrainingCapacitance.cpp со scoped meaningful cases: geometry changes/whole-vector uncertainty, Off/no artificial C0, exact grid/source tags, dimensions/budgets, signed/exact-count overflow, no clamping, repeat independence и pure N4/N6 dimension controls. Эти N4/N6 не заменяют actual distinct-bank routing. Полный native этап требует Branch `[N..1]` positive controls отдельно от shared-bank negative.

Explicit supported frame origin/phase/reset declarations не являются attestation. Pure модуль не проверяет actual events, timestamps или physics; не добавляет dt к SyncTol. Candidate frame endpoints должны быть frozen до native group, actual frame existence/quantization/routing проверит следующий слой.

Isolated pure source preparation разрешена до завершения240; native/runtime admission и переход в defaults остаются за соответствующими evidence gates. Frozen206/214/229/240 pins не изменяются.
