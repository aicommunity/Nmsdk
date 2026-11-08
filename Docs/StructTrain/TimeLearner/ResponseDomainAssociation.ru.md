# Контракт частичного сопоставления областей

Подготовлен production utility PulseLib `ResponseDomainAssociation.h/.cpp`.
Он использует общий `MeasuredResponse`, требует полный набор конкурирующих
пар channel×stimulus и сохраняет измеренные признаки при отказе сопоставления.
Модель, протокол, hash паттерна и фактические observation IDs связаны явно.

Это диагностический шаг этапа7. Hypothesis — единственный наибольший максимум
под объявленными областями; это не Valid origin и не разрешение обучать.
Shared вершины/плато, ties, clipping, nonfinite, gaps, неполнота и stale context
получают разные причины. NoCandidate не считается PhysicalInfeasible.

Включён counterexample предыдущей задержанной волны внутри формально
подходящей области следующего импульса: он доказывает, почему даже эксклюзивная
оконная гипотеза не является доказательством происхождения. API всегда
TrainingCertificateEligible=false; контроллер, schemas1–6 и сертификаты
не переключались. Signed offsets actual peak/onset сохраняются отдельно от
утверждения о принадлежности. Описание API — PulseLib
`Docs/TimeLearner/ResponseDomainAssociation.ru.md`.

Приёмка использует настоящий production CPP в target
`Test_PulseLib_ResponseDomains`. Fixtures охватывают меньшие/поздние/равные
максимумы, плато и onset внутри него, конкурентов, отсутствующие отклики,
guard samples и исходные индексы, N=1/2/4/6, разные physical channel IDs,
перестановку domains, absolute clocks, stale pattern/model/protocol и
неполные/повреждённые записи. Отдельная native applicability-проверка и
интеграция в обучение остаются необходимыми; unit PASS их не заменяет.

Статус: код и fixtures подготовлены. На локальной машине численные тесты
не выполнялись; требуется серверная сборка/проверка.
