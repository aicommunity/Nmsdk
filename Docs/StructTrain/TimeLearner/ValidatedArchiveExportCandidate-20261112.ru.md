# Кандидат устранения повторного декодирования при экспорте — 12.11.2026

На M40 принята свежая SDK и36/36 actual native checks, включая четыре новых
проверки Classic/Branch×completed/stopped. Source/runtime/protected bytes
сохранены, outer+36 children closed и lease released.
[Приёмка и исходные JUnit](ValidationPlans/M40ValidatedExport36A2-20261112/RESULT.ru.md).
Сравнение API выполнено в одном новом binary, не как A/B двух бинарников.
Большой N4 export/performance и Elder остаются отдельными gates.

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

На M40 свежая изолированная SDK и все36 native cases приняты, целостность
исходных JUnit/closure/source proofs проверена. Полный native36 corpus ещё
нуждается в отдельной compact publication и independent replay.
Данные завершённого Branch retry с900s финализации дают отдельный baseline.
Следуют Elder и большой recorded N4 import/export. Равенство малого encoder/proof не
подтверждает скорость большого N4 экспорта; до отдельной проверки этот дефект
не закрывается. Полный исходный план0–12 остаётся активным.
