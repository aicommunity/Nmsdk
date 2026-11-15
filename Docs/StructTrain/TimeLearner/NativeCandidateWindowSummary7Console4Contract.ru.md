# Frozen CPP contract: summary7 / execution4 / transport source6

Source boundary before implementation: Root `121fcbbac7046871c02e0750ee42e87595f22c68`
(code `ac46230a1dd58f214d5a768b8a68ba67c5e09537`), Pulse
`0286336fbc5c05ce5b0d40cc1a886d2f2ebc0f63`. Native package6/proof и runtime2
подготовлены, не compiled/runtime accepted. Этот contract не утверждает, что
новый CPP/Console или Python путь уже реализован или научно принят.

## Summary7

Отдельный `EncodeNativeCandidateWindowTrainingState` допускает protocol5/common2
на stopped/completed Finished boundary с настоящей source family. Public
`EncodeNativeTrainingState` выбирает его ТОЛЬКО для protocol5; old protocol4
encoder/summary6 meaning и scalar1–5 не расширяются через `>=`.

Summary7 имеет **точно keyset summary6**, приведённый в соседнем JSON contract.
`schema_version=7`, `kind=native_training_state_summary`, `runtime_plan` — actual
runtime2, `certificate` — actual service cert3 либо null. `references`, selected
group/proof IDs, candidates/anchors/counters берутся из реальных service records,
а не scalar3 packets. Proposal/recipe/instance IDs не дублируются новым overlay:
они связаны через group semantic proofs в archive2 и cert3.

REFERENCE_FIELDS прежние: input_id/run_id/trial_id/effective_model_revision/
raw_potential/measurement_group_id/semantic_proof_id. CANDIDATE_FIELDS прежние,
optional `capacitance` — actual candidate witness.controller_parameters.
Current/anchor groups должны быть consumed и иметь измерение/proof; initial
references — только атомарно закрытый allN, staging prefix не подставляется.
Original refs могут быть historical attempt; selected finals — current/latest
observed actual final run. Current relative timing уже вычислен от ACTUAL origin
каждой full-before группы, не абсолютного model clock.

`search_history_retained=false` после import: candidates/rejections/domains пусты,
accepted_parameters/applied_edits/search_probes — null. Archive/counters/original
refs остаются полными. `certificate_matches_actual_model` сравнивает actual
service cert/refs/current revision+epoch/tolerances, не mathExact stopped DATA.
`contains_evaluation_verdict=false`; summary — дополнительная consistency record,
не primary evidence или source execution attestation.

## Console execution4 и primary writer

Existing training/preflight commands и training-job1/2 keysets сохраняются.
Nested configuration7 направляет в execution4, configuration6 — прежний3,
scalar/recovery configurations1–5 — прежний base1/2. Old bool helper сохраняется
для old callers; новый configured dispatcher различает exact versions.

Execution4 имеет **тот же keyset, что execution3 соответствующего base1/base2**.
Extra fields: base_schema_version, measurement_method, measurement_archive,
model_semantic_hash, source_origin, composite_counters. Их форма в JSON contract.
`base_schema_version` читается в OWNING QJsonValue ДО вставки новых полей.
`sha256` — прежний canonical document hash; это не криптографическая подпись.

Preflight base1: package/archive/source null, attempt/archive counters известные0,
execution callback counters0, model_semantic_hash — actual initial model identity.
Failed before owned Start base1: package/archive/source null; attempt/archive
counters неизвестны/null, execution counters actual observed callbacks; отдельный
`training-start-failure.json` schema1 имеет прежний keyset/meaning. Нельзя создавать
fake empty archive/family. Completed/stopped: package6/archive2, source/counters
из actual export, model_semantic_hash — actual package model_revision.
Live base2 сохраняет прежние finalization/recognition fields и null semantics;
source Solo и final Recognition identities не смешиваются.

`PublishNativeCompositeArchive` явно связывает package5→archive1/protocol4 и
package6→archive2/protocol5 ДО файловых записей. Для нового пути обязательны
embedded primary и strict decoder; все external mirrors побайтно те же.
Existing names сохраняются: train_learned_state.json / train_stopped_state.json,
train_learned_summary.json / train_stopped_summary.json,
composite-measurements/index.json, group-{i+1:06d}.json и raw primary_ref.relative_path
ВСЕХ retained records, включая historical refs и interrupted raw. Paths не
выводятся из количества выполненных сейчас probes. Outer artifacts перечисляют
все реально записанные файлы с exact bytes/SHA; `measurement_archive` — descriptor
на actual index, не подмена embedded package archive.

Completed classification требует original execution.package_sha256 + artifact
exactbyte/source-case binding. Coherent DATA rewrite из package6 limitation test
не получает producer success от самого math/metadata hash. Python counterpart
сохраняет эту existing pipeline boundary, package-only audit не execution claim.

## Transport / Recognition

Новых CLI commands, циклов и recognition envelope versions не требуется.
Existing export-job1, evaluate-job1, recognition-state1/conversion-spec1–2 и
trial/observation1–2 сохраняют keysets. Nested source_solo6 проходит strict
Prepare6 и complete actual graph readback; package5/old source branches неизменны.
NativeRecognitionState уже вызывает общий PrepareNativeLearnedState.
Новый CPP chunk добавит scoped actual source6 conversion/import/frozen trial
controls и необходимые owner-correctness правки, а не обход import.

Metadata сохраняет training как source_solo history. После conversion
`recognition_verification={status:unverified,model_identity:<current>,certificate:null}`;
source Train Exact не превращается в OriginalExact текущей Recognition.
Actual Rs conversion применяется один раз от immutable source Solo; native
ImportRecognition повторяет его для проверки, не масштабирует импортируемый
граф ещё раз. Diagnostic stopped6 остаётся diagnostic recognition.
Test использует existing whole-presentation criterion (onset, offset0, end null)
и настоящие output spikes/полную записанную реакцию, не assigned Train windows.

## Filescope

Pulse: NativeCompositeLearnedState.h/.cpp (новый summary7 encoder),
ProbeEvidenceJson.cpp (explicit summary dispatch); NativeRecognitionState.*
только если actual source6 owner tests выявят необходимую integration правку.
Root CPP: TimeLearnerCompositeArtifacts.h, TimeLearnerTrainingJob.cpp,
TimeLearnerTransportJob.cpp при необходимости explicit source6 transport validation;
existing Test_PulseLib_CompositeTraining.cpp и native recognition/Console test
components. Python package6/cert3/summary7/execution4/CLI adapters владеет другой
agent; здесь они не редактируются. Старые tests/bytes не переименовываются.

Новая native6 factory/29 tests + prior17 proof/common Cold7 fix и новый CPP chunk
остаются unrun до объединённого remote build/actual checks. Никакого локального
compiler/numerical/CLI/native запуска или изменения active server snapshots.
