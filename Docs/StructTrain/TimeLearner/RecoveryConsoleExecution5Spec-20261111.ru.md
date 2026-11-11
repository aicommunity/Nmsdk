# Незакрытый Console boundary cold8/package7

Проверка исходников подтвердила дополнительные причины, почему native API
проверки ещё не дают допуска к новой Console научной серии.
TimeLearnerCompositeArtifacts.h принимает для publication только package5/6;
WrapConfiguredNativeExecution распознаёт configuration6/7, но не8.
Python native_pipeline_worker и live_training_worker также выделяют composite
только6/7 и ожидают execution3/4, а execution reader разрешает tuple3/5,4/6.
Новая configuration8 проходит общий declaration validator, но последующая
обработка не соответствует её реальному native package7/summary8.

Следующее изменение должно явно определить execution5 для configuration8,
package7, summary8, protocol5, archive2, recovery-ledger1 и runtime2/3.
Старые wire3/4 сохраняются. Запрещено переименовывать7 в6,8 в7 или5 в4.
Общие поля наследуются от composite execution; новые recovery_ledger_sha256
и recovery_delivery_count связываются с исходным ledger и actual model archive.
При preflight/before-owned-start failure оба поля null: журнал не создавался.
При пакете supplied entries проверяются DecodeCandidateWindowRecoveryLedger
против отдельно декодированного archive до публикации файлов. Их связность
не доказывает полноту истории и не восстанавливает controller authority.

В Python нужны отдельные dispatch пары execution5/package7 и5/configuration8,
строгие точные поля и bindings hash/count; существующий общий package reader
уже направляет7 в independent recovery audit. Обновляются artifact closure,
preflight, stopped/completed Train и start failure; live/base2 сохраняет свой
отдельный конечный статус, finalization и не допускается без адресной проверки.
Обязательно проверить payload/version/hash/count corruption, неполный primary
mirror, отказ до source, отсутствие ledger при preflight и прежние3/4 controls.

После unit producer/reader checks необходим настоящий Console preflight и
малый cold Train на обеих топологиях, затем export/import/frozen Test с полными
временными трассами. Только эти результаты могут закрыть Console boundary;
наличие нового JSON wrapper либо текущий native18/10 его не подтверждает.
