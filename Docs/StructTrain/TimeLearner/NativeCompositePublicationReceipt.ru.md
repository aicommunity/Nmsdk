# Повторное использование проверки при записи execution

Причина изменения — [реальный timeout Classic N4](ValidationPlans/M40DataSdkBudget16TrainA1-20261113/RESULT.ru.md): state и summary записаны, SIGTERM застал повторный DecodeNativeCompositeTrainingArchive в execution wrapper.

PublishCheckedNativeCompositeArchive выполняет прежние проверки archive/protocol, package digest, recovery ledger и физической привязки; записывает и проверяет зеркальные primary bytes. Только после успешной записи index создаётся NativeCompositePublication с приватным конструктором. Объект владеет неизменяемыми JSON package/descriptor и измеренным числом ledger deliveries. JSON implicit sharing не требует копирования всех трасс.

Wrapper может использовать объект только при точном равенстве package и descriptor с сохранёнными значениями. Подмена даже с новым digest отклоняется. Это не флаг trusted, не глобальный cache и не новый wire schema. Без объекта wrapper выполняет прежний полный DATA replay. Старый PublishNativeCompositeArchive остаётся совместимым API. Оба Console-пути используют объект своей текущей публикации; lifecycle, физика, search, tolerances и бюджет не меняются.

Адресная проверка расширяет существующие4 Classic/Branch completed/stopped NativeRecoveryConsoleArtifact cases: signed execution равен независимому полному replay для base1/base2; изменённые package и descriptor отклоняются. Существующий тест foreign ledger обязан отказывать до появления файлов. Preflight/before-source semantics сохраняются. Локально численные проверки не выполняются; серверная сборка и runtime-проверка пока открыты. Факт устранения timeout большого N4 ещё не подтверждён.
