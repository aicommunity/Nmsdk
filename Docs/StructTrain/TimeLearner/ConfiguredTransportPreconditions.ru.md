# Предусловия configured model transport — кандидат06.11.2026

Статус: новый normal25-case gate прошёл на M40; четыре изолированных matched
cold controls также прошли. Общая приёмка pending C++ SDK ещё не завершена.
Это не исправление физики, не новая процедура обучения и не научный PASS.
PulseLib остаётся `2c7e0144a902795cb6287ee677cff5aa08998847`.

## Подтверждённая ошибка постановки

NativeLearnedState/ClassicConfiguredN1 и NativeLearnedState/BranchConfiguredN0
вызывали LearnedBoundary с SyncTolerance=0.02 и ожиданием completed certificate.
В исходном SDK12d и budget-fixed SDK2c7 оба cold Train исчерпали максимум sweeps.
Отказ происходил до проверки transport на ASSERT_TRUE(service.Certificate()).
Поэтому эти случаи не подтверждали перенос завершённой модели.

Оба исходных23-case запуска сохранены без изменения verdict:21 passed/2 failed.
Парное сравнение проверило одинаковые compiler/build conditions, resource root,
loaded shared files,252 побайтно одинаковых CSV и7 одинаковых precondition
summaries. [Исходный A/B](AttemptInvalidObservationBudgetNativeABVerification.json)
отделяет ошибку fixture expectation от budget change. Дефект полноты исходных
проверок не устраняется существованием другого выбранного304-case gate.

## Изменение и сохраняемые условия

В Tests/Integration/Libraries/Test_PulseLib_NativeModelEditor.cpp два исходных
случая сохраняют свои IDs, normalization, model/storage physics, частоту,
паттерн, Ns/Rs/L bounds, budgets и SyncTolerance=0.02. Изменяется только
объявленное downstream expectation: DiagnosticSweepBudget вместо Completed.
Fixture должен проверить отсутствие обучающего сертификата, фактический
budget_exhausted/maximum_sweeps_exhausted и полный stopped-state roundtrip.
Recognition conversion stopped state должен отклоняться.

Отдельно добавляются NativeCompletedTransportExplicitPointTwo:
ClassicConfiguredN1 и BranchConfiguredN0. Они явно используют fixture tolerance
0.2, должны получить реальный Exact и пройти исходные completed export/import
проверки. Это дополнительные engineering controls с другим объявленным допуском,
а не переоценка исходных отрицательных результатов. Default0.02 не меняется.
Имена артефактов LearnedBoundary уже различают strict и explicit-tolerance
profiles; новые положительные случаи не должны перезаписать исходные cold traces.

## Приёмка

Новый изолированный normal SDK выполнил прежние23 IDs с двумя
исправленными диагностическими expectations плюс два новых positive controls.
Нельзя объявлять этот новый25-case verdict прохождением прежнего неизменённого
23-case gate: его два assertion failures остаются историческими фактами.

На root `d41fdb6efbef2c672229df55266be8acabc57ac7`, PulseLib2c7, получено25/25
без skips/errors/failures. Proof `f45818ef3670da162c65a355c21080fd36b9ab75`:
804 members,1135504 bytes xz; все members и746 source files сверены с Git.
[Primary receipt](ConfiguredTransportPreconditionVerification.json).

Сравнение общих23 и25-case процессов не объявляется полностью идентичным:
из252 прежних CSV совпали170,82 отличаются, потерянных нет. В просмотренных
примерах различается абсолютное время после дополнительных lifecycle фаз.
Полный список различий сохранён в cold-evidence-comparison.json; одного
переноса кривых к onset недостаточно для matched control.

Поэтому выполнен отдельный контроль: ClassicConfiguredN1 и BranchConfiguredN0
по одному в свежем процессе на старом и новом test SDK, всего четыре native PID.
Старые случаи сохранили исходные assertions/exit1, исправленные прошли полный
diagnostic stopped-state transport. До downstream assertion все28 cold CSV и
две precondition summaries побайтно совпали, включая абсолютные timestamps.
У каждого нового случая появились по три дополнительных CSV downstream фаз.
Никакое численное или временное выравнивание при сравнении не применялось.

Proof `c69274b623f16433b3f8468753857fdbc97dc0f5`:220 members,
166808 bytes xz; все members и335 tool source files сверены.
[Matched receipt](ConfiguredTransportColdMatchedVerification.json).
Свежие closure/released leases и фактические loaded-runtime identities
проверены для обоих заданий. Это normal controls; ASan не засчитывается.

Сохранены original JUnit, фактические runtime/process captures, source hashes,
complete/stopped packages и исходные пробы. Проверить сохранение исходных cold
условий и отсутствие изменений обучающей физики/алгоритма. Изменение числа
downstream replay/probe artifacts ожидаемо: прежде два теста прерывались до
переноса; оно не оправдывает потерю исходного training evidence.

Если stopped configured transport либо positive completed control выявит
реальную ошибку import/lifecycle, исправлять её на уровне владельца, а не
ослаблять assertions или подставлять шаблонную модель. Возвраты
Build/Calculate/Reset остаются интерфейсными true; numerical outcomes передаются
штатными typed states. Сборки и пробы — только на разрешённых серверах.

Этапы4/5/7 и весь исходный план остаются частичными. Новая политика продвижения
после unassigned burst имеет отдельную ветку и не входит в этот SDK.
