# Публичные свойства feature и develop: сверка 07.11.2026

Production `property_drift` повторно прочитал неизменяемые Git objects PulseLib:
принятый develop `0ec9193e6620ae2439329eece5ecd6d6f167c70a` и текущую feature
`8702d264bc7b4f4c464e200f4a1092e55c6b44ff`.
[Полный source receipt](PropertyFeatureSourceDrift-20261107.json).

Все 217 собственных UProperty деклараций двух learner присутствуют в обоих
снимках. Для каждой совпали исследованные registration, declaration, setter и
Default source slices: новых, удалённых или изменённых записей нет. Это только
Git/source metadata; компоненты локально не создавались и numerical tests не
выполнялись. Унаследованные Rdk свойства учитываются отдельно.

При этом реальные consumers существенно изменились. Поэтому нулевой drift
каталога не разрешает переносить runtime-приёмку develop на всю feature.
Проверенный diff обоих learner включает следующие области:

| Изменение consumer/API | Доказательства и ограничение |
|---|---|
| Делегирование BeforeCalculate/BeforeDefault/BeforeReset общему NativeLearnerLifecycle; recognition hooks общему NativeRecognitionControl | Общие SDK gates перечислены в ImplementationStatus. Не менять public lifecycle bool на протокол ошибок; compatibility и multirate матрица остаётся открытой |
| InstallNativePreparedModel и fresh-owner admission | Normal26/Console12 на M40, normal163/readers19 на Elder; повторная установка отклоняется. Собственный [ASan26/readers19 API8702](FeedbackStorageASan-2026-11-07.ru.md) выполнен отдельно; старый single-pulse ASan37 не используется вместо него |
| Native training capacitance binding/readback/edit и invalidation | C0 и opt-in bounded C-search имеют отдельные receipts и ограничения; отсутствие новой UProperty не означает отсутствия нового управляющего фактора |
| Feedback/storage recipes, graph import и single-pulse characterization | Отдельные physical-profile/native controls. Изменение general physics остаётся во storage, характеристика одним импульсом не заменяет штатный burst Train |
| Analyzer и measurement/verification helpers | Требуют своих schema/finite/assignment проверок. Число пиков всей пачки не является общей целью Train; новый контракт ещё не реализован во всех production путях |

Эта сверка исключает повторное объявление неизменённых setters новыми дефектами,
но не закрывает effective-factor matrix, connected/direct/XML assignment,
исторические adapters, общий semantic audit и этап1 целиком. Конкретные runtime
доказательства относятся к сохранённым compiled commits, а не автоматически
к более позднему documentation HEAD.
