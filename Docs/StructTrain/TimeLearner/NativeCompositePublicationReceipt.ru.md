# Повторное использование проверки при записи execution

Причина изменения — [реальный timeout Classic N4](ValidationPlans/M40DataSdkBudget16TrainA1-20261113/RESULT.ru.md): state и summary записаны, SIGTERM застал повторный DecodeNativeCompositeTrainingArchive в execution wrapper.

PublishCheckedNativeCompositeArchive выполняет прежние проверки archive/protocol, package digest, recovery ledger и физической привязки; записывает и проверяет зеркальные primary bytes. Только после успешной записи index создаётся NativeCompositePublication с приватным конструктором. Объект владеет неизменяемыми JSON package/descriptor и измеренным числом ledger deliveries. JSON implicit sharing не требует копирования всех трасс.

Wrapper может использовать объект только при точном равенстве package и descriptor с сохранёнными значениями. Подмена даже с новым digest отклоняется. Это не флаг trusted, не глобальный cache и не новый wire schema. Без объекта wrapper выполняет прежний полный DATA replay. Старый PublishNativeCompositeArchive остаётся совместимым API. Оба Console-пути используют объект своей текущей публикации; lifecycle, физика, search, tolerances и бюджет не меняются.

Адресная проверка расширяет существующие4 Classic/Branch completed/stopped NativeRecoveryConsoleArtifact cases: signed execution равен независимому полному replay для base1/base2; изменённые package и descriptor отклоняются. Существующий тест foreign ledger обязан отказывать до появления файлов. Preflight/before-source semantics сохраняются. Локально численные проверки не выполняются; серверная сборка и runtime-проверка пока открыты. Факт устранения timeout большого N4 ещё не подтверждён.


## Проверка M40

[Fresh Release/O3 build и7/7 actual cases приняты](ValidationPlans/M40PublicationReceiptSdkA1-20261113/RESULT.ru.md). Full namespace4166 подтверждён, оба native groups закрыты. Прежнее указание «серверная проверка открыта» выше — исторический снимок подготовки; Elder и большой N4 performance остаются открыты.

## Последующее подтверждение

[Elder7/7 принят](ValidationPlans/ElderPublicationReceiptSdkA1-20261113/RESULT.ru.md); [большой N4 native export и внешний DATA audit завершились в прежнем лимите](ValidationPlans/M40PublicationReceiptBudget16TrainA1-20261113/RESULT.ru.md). [Весь исходный Elder corpus независимо восстановлен на M40](ValidationPlans/M40Publication7SemanticReplayA3-20261114/RESULT.ru.md):498 archived members, production package/summary/wrapper replay, foreign ledger и corrupted CSV отказ. Ранее открытые пункты выше относятся к снимку подготовки. Replay не запускает новую модель; fixture wrapper counters не превращаются в native Console attestation.
