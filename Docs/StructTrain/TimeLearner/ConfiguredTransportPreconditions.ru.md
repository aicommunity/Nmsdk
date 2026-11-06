# Предусловия configured model transport — кандидат06.11.2026

Статус: изменения тестов подготовлены; новый25-case gate ещё не выполнен.
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

Новый изолированный normal SDK должен выполнить прежние23 IDs с двумя
исправленными диагностическими expectations плюс два новых positive controls.
Нельзя объявлять этот новый25-case verdict прохождением прежнего неизменённого
23-case gate: его два assertion failures остаются историческими фактами.

Обязательны original JUnit, фактические runtime/process captures, source hashes,
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
