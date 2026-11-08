# STEP2 candidate-window: review границы и нового wire contract

Статус: source types/schema preparation, без runtime acceptance и без подключения service/CLI/defaults. Нормативный подробный контракт находится в PulseLib `Docs/TimeLearner/CandidateWindowTraining-Step2Contract.ru.md`; типы — `Core/TimeLearner/CandidateWindowTrainingBoundary.h`.

Pulse source pin этого review: `5e4faf0d94c2ea74dcc0f8e38a3e3f085eb124b1` (parent `e7a38933051706f8f2fa76fe322c3fe7401ee52a`). Никаких существующих production .cpp или serializers этот Pulse commit не меняет.

Основание: source-reviewed design `CandidateSpecificWindowPolicy-Design.ru.md`, чистая арифметика Rootdf06/Pulsee7 и отдельный normal40+ASan40 evidence72da089b46d64aaa9bd8a4abdc6acfddf0c8bebb. Pure40 не подтверждает native seed, actual graph/Branch bank membership или Train admission. Frozen206/214/229/240 и их результаты не переосмысляются.

Эта первая точка review определяет отдельные Protocol5/contract2/spec2/candidate-binding2/record2/archive2. Protocol4/contract1 остаётся fixed-window. Новый contract2 использует `reference_input_windows` и полную `candidate_window_policy`; старый alias `input_windows` запрещён. Новые record2 добавляют обязательный `window_proposal`, null только для Reference, и имеют явную spec2. Не использовать `schema>=4` или fallback в старый decoder.

Закрытые типы разделяют:

1. Staged actual reference seed и полный `CandidateWindowReferenceSet`, выпускаемый только после complete `CapturedReferences` для всех N inputs. Search/final не получают partial seeds.
2. `NativeCandidateWindowSnapshot` из actual graph/P/C0/ordinal/bank readback; public DATA/успешная арифметика не создаёт этот объект.
3. `PreparedCandidateWindowProposal`, замороженный до первой N+2 queue и связанный с live owner/family/current attempt/request/revision/epoch.
4. Отдельный `ReplayedCandidateWindowProposal`: независимый strict portable replay настоящих reference primary и actual candidate binding обязателен перед любой новой scalar/Train admission. Native attempt не имеет доступа к его private constructor.

В этом commit нет factory/minting/decoder/selector implementation. Типы не включены в текущие `VerificationProtocol`, `CapturedReferences`, `NativeCompositeTrainingAttempt`, service или codecs, поэтому новые branches остаются отклоняемыми. Следующая реализация начинает с общего live/portable proposal validator, actual fullBefore reference plateau indices/P0/C0/source grid, actual physical bank map и spec2 projection через реальные retained frame timestamps. Scalar arrival остаётся относительно actual origin события текущей группы; predict delay не подтверждает пик.

Нужно подтвердить адресными native fixtures рост L, выводящий вершину из initial window; CtrimOff без C0; actual C0/readback изменения; warm из portable initial references; запрет partial seeds; stale family/attempt/revision/epoch/Reset/Default/Need=false; tampered recipe/proposal/primary; недостающие реальные frames. N4/N6 Branch positive-routing отдельно использует distinct attachments `[N,N−1,...,1]` с сохранёнными actual bank/IsConnected/source ordinal witnesses. Старый shared-bank negative/plumbing fixture не заменяет эту проверку. Не обещать Exact для неразрешённой физической сходимости и не расширять train tolerances ради теста.

Root helper correction6dacdb3d4fb3245649aba3a5d69ba8f83f611c8e уже включён отдельным merge commit47e86014391d887b63b7436249b7b64e1df6ff42. Шесть future composite inventories сверены с точными Git-index bytes merged CompositeTraining TU SHA256 `db1aca276bed90b08712f3af81ea61508cc14de7719118ec10a42c5b61c35245`. Это source metadata, а не новый runtime результат.

Локально выполняются только Git/diff/text checks; C++ compile/syntax-only и numerical tests не запускались. Никакие server source/build/runtime caches не изменялись.
