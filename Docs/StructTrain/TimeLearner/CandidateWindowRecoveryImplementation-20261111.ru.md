# Восстановление поиска composite/candidate-window: контракт реализации

Статус: открытый подэтап7. Фундамент native-допуска отказа проверен29/29 на Elder и M40, все30groups закрыты и reservations released на каждом. [Переход search cursor реализован в ядре](CandidateWindowRecoveryCore-20261111.ru.md), но полный C1 ещё выполняется на серверах. Следующим отдельным изменением реализованы [cold8/runtime3 codecs и Python readers](CandidateWindowRecoveryWire-20261111.ru.md); их приёмка ещё не завершена. Service delivery, package/archive/history persistence и независимый replay остаются открыты. Основание — [реальные N4 графики](ClassicWindowTemporal-20261111.ru.md) и независимый [replay](../../../Reports/StructTrain/TimeLearner/ClassicWindowReplay-20261111/replay.json): L=54 missing в прогнозном окне, ambiguous в полном. Переход к глобальному максимуму или ослабление назначения не допускается.

## Фактический разрыв API

Исходный разрыв: ValidateCandidateWindowTrainingConfiguration допускал только RetrySameCandidate. Теперь ядро принимает отдельный AdvanceRejectedCandidateWindow и закрытый typed отказ; этот переход проверяется новым C1. Runtime2 и его прежний Python reader остаются retry-only; runtime3 и отдельный новый reader явно сохраняют AdvanceRejectedCandidateWindow. BoundedTrainingSession::Consume scalar имеет самостоятельный AdvanceUnassignedBurst; строковый RejectCandidateWindow → RejectTyped → Reject по-прежнему повторяет тот же composite-кандидат до исчерпания общего invalid budget. NativeTrainingServiceComposite.cpp пока передаёт только строку причины и явно запрещает новую policy при Start. Определять право продолжения по префиксу этой строки нельзя.

## Последовательность изменений

1. В CompositeTrainingMeasurement.h ввести закрытый тип rejected composite measurement. Создаёт только NativeCompositeTrainingAttempt; JSON/публичный bool не создают live authority. Он связывает PreparedCompositeMeasurement, group ID, action serial/epoch/revision, source origin/owner scope, candidate binding, actual geometry validity, hash полного diagnostic record и факт завершённой native-группы. В NativeCompositeTrainingAttempt.cpp::CloseGroup создавать его только после проверки графа/параметров/reset/source, полного n+2 инвентаря, повторяемости, завершённого окна, actual timestamps, finite samples, model/wall/byte/sample budgets и повторной проверки текущего owner. Для начального выпуска разрешить только Missing/Ambiguous назначения. Nonfinite/censored/incomplete/изменившийся граф/источник/неподдерживаемая физика/clock/budget ошибки не получают recoverable authority. Проверка wall budget нужна и для пути отказа, до выдачи authority.

2. В NativeCompositeTrainingAttempt.h добавить read-only getter этого типа, сбрасывать при StartMeasurement/Cancel/RevokeLive/новом edit. Старые Measurement()/RejectionReason() сохранить. Нет валидного scalar measurement — нет residual, target/reference или сертификата.

3. В NativeTrainingServiceComposite.cpp доставлять typed rejection только для Search и только при ещё актуальных generation/owner/request/epoch, после beforeConsume sink и бюджетных проверок. Generic string RejectCandidateWindow остаётся для остальных ошибок и никогда не разрешает переход к следующему кандидату. Reference capture и Final verification не используют recovery как способ пропустить вход.

4. В BoundedTraining.h/.cpp добавить отдельную явную policy для composite recovery; не переопределять незаметно scalar AdvanceUnassignedBurst. RetrySameCandidate остаётся default. Новый перегруженный typed consume/reject проверяет prepared identity и одноразовость group/serial. Общие counters probes/invalid/candidates не обнуляются. При допустимом отказе сбрасываются pending/compositeArmed, незавершённые anchor и N0 repeats; не добавляются timing/amplitude observations. Фаза возвращается к конечному CandidateCursor; новая геометрия проходит штатный domain assessment, legal-boundary edit, reset, fresh probe. Существующая очередность N1 interleaving сохраняется. Для RestoreBest отказ означает SearchUnresolved, а не бесконечный обход или Exact. Исчерпание общего бюджета — явный честный outcome; не PhysicalInfeasible.

Псевдокод:

    typed_failed_group = owner.close_and_validate_group()
    service.require_current_generation_revision_and_budgets()
    if search_policy permits typed_failed_group:
        consume_failure_once_and_charge_original_budgets()
        if restoring_best: stop_search_unresolved()
        else:
            discard_partial_anchor_and_repeats()
            keep_valid_history_and_finite_cursor()
            queue_next_legal_candidate_with_fresh_domain_assessment()
    else: preserve_existing_rejection_behavior()

5. Версионировать ConfiguredNativeTraining, CandidateWindowRuntimePlan, package/archive/summary и Python readers. Перед выбором числовых schema IDs проверить уже занятые версии. Старые runtime2/package6 неизменны; старый decoder должен отвергать новую policy. Экспортировать ordered recovery events с candidate/geometry proof binding, status before/after и counters. DATA replay воспроизводит переходы/бюджеты и rejects tampering, но не восстанавливает live authority. Проверить Encode/Decode/Copy/Load roundtrip и прерывание на границе этапа. Не объявлять поддержку mid-probe checkpoint.

6. Адресные C++ тесты на реальном owner/Environment: completed Missing/Ambiguous → новый кандидат; malformed/partial/nonfinite/foreign owner/stale revision/replayed group → запрет; capture/final не пропускаются; N0 partial repeats и C-context не протекают; anchor/restored-best; invalid/probe/edit budgets; отсутствие новых residual/certificate у rejected group. Python независимый replay проверяет те же ordered events и mutation controls. Ранее успешно проверенный geometry/Rs A/B не использовать как доказательство этой новой функции.

7. Серверная приёмка Elder+M40: сначала адресные production tests, затем тот же stock N4 protocol с исходными tolerances/CapturedPerInput/anchor/bounds, прежним window policy и единственным фактором recovery. Ошибку прогнозирования окон исправлять отдельным A/B. Публиковать full primary и читаемые временные full/omission графики; PASS классификации здесь не требуется. Сохранить исходный остановленный Train и его negative diagnostics.

## Границы

Общая Rdk lifecycle, native scheduler и true-return Build/Reset/Calculate не меняются. Никаких nested Calculate, динамических prototype patches, fallback C или новых общих амплитудных целей. Пока typed policy и её readers не реализованы, новый дорогой Train с ней не запускать. Контрольная SDK-сборка исходного N1 на Elder завершена (2/2 выбранные native roundtrip, не полный119),, source root5ba0a2e81759a28f378117757aa3a5b91f1c57ab / Pulsec10206d5e338792d42b58ab28e48e7364b07e481.
