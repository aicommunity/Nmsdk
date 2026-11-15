# STEP3-B1: закрытая allN release граница

Source implementation после отдельного core376/6579 и mapping32e1. В Pulse `NativeCompositeTrainingAttempt` выделены private allocating/checking Prepare и noexcept Commit; actor/adoption хранят shared immutable complete RefSet. Public Complete API и source/family/live/clock guards остаются, никаких новых public eligibility flags или portable addresses.

Десять `NativeCandidateWindowReferenceRelease.*` actual C++ fixtures сохраняют все primary и проверяют allN/prefix flags, неправильную семью/duplicate evidence, actual edit/Reset/Default. `CandidateWindowReferenceReleaseGateInventory.json` закрепляет новые literal IDs, текущие Git-byte hashes и необходимые ancestors. Derived planned scope418 — previous408 +10, не число выполненных tests. Все frozen inventories остаются на прежних pins.

Новая граница пока готовит service5 transaction: его собственные allocations должны завершиться ДО actor commit, последующая публикация обоих владельцев — только noexcept и без callbacks. Service dispatch/warm ledger/cold7 initial declaration/package6 остаются следующими отдельными commits; CLI/defaults не включены. Подробности и ограничения — `PulseLib/Docs/TimeLearner/CandidateWindowReferenceRelease.ru.md` и `CandidateWindowTrain-ServiceSessionMapping.ru.md`.

Artifacts: `classic-native-window5/release-*`, `branch-native-window5/release-*` — реальные N+2 raw, а `classic-window-reference-release5/*`, `branch-window-reference-release5/*` — actor archive2 и `reference-release.json` со scope `actor_allN_release_before_service5`. Default после потери graph не получает придуманный after-model; оригинальные уже полученные raw/source сохраняются.

Локально выполнены только Git/text/AST inventory checks. Численные tests, C++ compilation/syntax-only, dispatch/caches не запускались. Это не runtime acceptance, не full248 closure и не completed portable package6.
