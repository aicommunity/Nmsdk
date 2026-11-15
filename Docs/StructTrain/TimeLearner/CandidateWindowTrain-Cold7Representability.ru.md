# Cold7 capture: отказ молчаливой нормализации valid protocol

Source fix после Root `c94885592cacdf8594e0f63d040e4dfad8c893f1` / Pulse `b9fe5b9773e232150bcb846a8991f5bf27c2b70a`. Full validation прежнего capture не гарантировала, что cold7 сможет точно сохранить корректный low-level protocol. Добавлены полное равенство восстановленного protocol и input windows исходным значениям. Непредставимые именования/перестановки/origin/pattern получают явный refusal; новые поля и ограничения native low-level API не вводятся.

Шесть новых `CandidateWindowCold7.*` data cases: valid renamed input/stimuli, valid согласованная permutation, valid другой origin, valid иной pattern binding и positive run/checkpoint reset. Каждый отрицательный контроль отдельно требует успешной protocol validation. Это дополнение к прежним invalid-assignment tests, а не их переименование/ослабление. Derived planned scope442 =436+6, без runtime verdict.

Private B1 Commit не имеет самостоятельного stale guard: source contract требует fresh Prepare/check непосредственно перед noexcept publication в том же owning frame. Public Complete соблюдает это сейчас. Service composition удерживается до review; её callback/edit-between-stages controls остаются обязательными. No local numerical/build/snapshot/dispatch/cache operations.
