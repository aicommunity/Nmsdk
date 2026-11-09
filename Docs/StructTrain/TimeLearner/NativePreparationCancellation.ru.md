# Native preparation callback cancellation

Source fix: Pulse `5712dd4350ed348383ce315e9738209c3bb324b4`, isolated from the following service/codec changes. Runtime acceptance is pending; no local build or numerical tests ran.

`NativeProbeExecutor::BeforeChildren` now respects explicit cancellation/reset performed by `onPrepared`, matching the existing post-`onSample` rule. It checks native state, the still-current recorder and request identity before continuing preparation. Previously, callback cancellation could be overwritten by a second failure after physical restoration; one native request could leave a second unharvested result. The patch changes no peak math, tolerances, schemas or Calculate/Build/Reset return semantics.

Four production integration cases use actual learner/storage/scheduler:

- NativePreparationCancellation.ClassicCallbackKeepsSingleCancelledResult
- NativePreparationCancellation.BranchCallbackKeepsSingleCancelledResult
- NativePreparationCancellation.ClassicSubsetRestoresFullPresentation
- NativePreparationCancellation.BranchSubsetRestoresFullPresentation

They require exactly one Cancelled result, no sampled frames, no second result, restored base model identity and (Recorder6) restored full presentation matrix. Existing raw probe tests remain required.

Inventory correction for subsequent gates: the historical static count “71 BoundedTraining” omitted macro expansions and counted a macro-body placeholder. Actual suite count is **74 BoundedTraining +23 FinalVerification =97**. The typed feature adds46 (143 together). This correction does not rewrite frozen Pulse269/Root27ba or the preserved mechanical A1 inventory failure; workers must compare the runtime `--gtest_list_tests` inventory and complete JUnit names.
