# Кандидат устранения повторного декодирования при экспорте — 12.11.2026

Изменён владелец сериализации в PulseLib: NativeCompositeTrainingEvidence.h/.cpp,
NativeCompositeLearnedState.cpp. [Подробный контракт](../../../Libraries/Nmsdk-PulseLib/Docs/Analysis/TimeLearnerValidatedArchiveExport.ru.md).

Новый encoder возвращает и прежний document/primary, и уже полностью
проверенный decoded archive. Factory6/7 перемещает его в portable proof;
summary8 использует для ledger без повторного decode. Старый публичный encoder
сохраняет интерфейс и полную проверку. Внешний import и Console publisher
продолжают независимо проверять данные. Нет постоянного кэша, обхода проверки
или замены текущего source/runtime работающих N4 заданий.

В настоящем integration fixture добавлены четыре NativeValidatedArchiveExport
cases с обоими learner и completed/stopped границами. Старый fixture по
умолчанию работает как прежде; новый opt-in входит в ключ его локального
тестового кэша и не может вернуть непроверенный ранее созданный case.

Следующая приёмка: свежая изолированная SDK, все36 native cases и проверка
целостности их исходных артефактов. Данные текущего Branch retry с900s
финализации дают отдельный baseline. Равенство малого encoder/proof не
подтверждает скорость большого N4 экспорта; до отдельной проверки этот дефект
не закрывается. Полный исходный план0–12 остаётся активным.
