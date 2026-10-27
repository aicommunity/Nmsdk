# Сводный статус полного плана: повторная проверка 27.10.2026

Последующее дополнение: A1–A6 и межсерверный learned-state replay уже
опубликованы через Git. Пять пакетов в каждом направлении дали побайтное
совпадение frozen CSV, модели и сертификата; локально проверены 4052 stored SHA
и 4048 raw payloads. См. [NativeLearnedState](NativeLearnedState.ru.md) и
[машинную проверку](NativeLearnedState.validation.json). Это уточняет pending
публикации/cross-host ниже, но не меняет классификацию полных этапов.

Этот снимок отвечает на вопрос о завершении всего утверждённого плана, а не
отдельных API-подэтапов. Основание: чтение текущего кода, Git, предыдущих отчётов
и повторное чтение серверных A6 XML. Новых сборок и экспериментов в ходе этой
проверки не запускалось. Старые промежуточные статусы относятся к своим SHA.

**Полностью принят этап 0. Частично выполнены этапы 1–7, 9, 10 и 12.
Этапы 8 и 11 по новой спецификации не выполнены. Весь план не завершён;
версию 2 пока нельзя объявлять рекомендуемой для всей экспериментальной матрицы.**

## Проверенный Git-снимок

| Репозиторий | Текущая рабочая версия | Принятый develop |
|---|---|---|
| Root | `dad2cad9de1421617c8a37b30d02c849ef5c23b6` | `68b77ac542cbd21479eab45c474b3603591add97` |
| PulseLib | `025d809f7b86cc79e18ddd711c6adc40e2396bf8` | `c1d5b177278f1eb347c1ebc725555837c36642bb` |
| Bin | `f5e1d0200127223981daa71da22cf5ee02fdbc60` | та же версия |
| Rdk | `8846c1423ab13a24e3ebfdce786ce85b6a9fc0d6` | та же версия |

Root и PulseLib: `stage05/native-trained-state`. Деревья чистые на начало аудита,
root gitlinks совпадают с фактическими child HEAD. Эта ветка ещё не объединена
в develop. Поэтому «реализовано в ветке», «проверено» и «принято» ниже разделены.

## Статус этапов

| Этап | Статус | Завершённые части | Незавершённые требования |
|---|---|---|---|
| 0. Исходное объединение | Выполнен | Начальные merge commits, согласованные gitlinks, develop hints, child-first публикация и recursive checkout | Для новых изменений продолжать ту же процедуру; текущую stage05 ещё предстоит принять |
| 1. Доказательства и параметры | Частично | Исходные SHA, исторические опорные commits, inventory, контракты, журнал найденных дефектов | Полный ledger экспериментов с августа и всех волн аудита; semantic review 211 исходных записей параметров и разбор 324 script candidates |
| 2. Сборки и runtime | Частично | Изолированные deploy roots на двух серверах, manifests, ресурсы, tracked Reports, Git-передача проверенных пакетов | Полный автоматический production run bundle и загруженные зависимости настоящего Train; повторная проверка общей тестовой инфраструктуры после последнего исправления пути ini |
| 3. Наблюдения и scorer | Частично | Строгие схемы, ID/метки, completeness, nonfinite, размерности >4, native burst assignment, отрицательные проверки | Один production-путь Train → calibration → frozen Test → итоговая оценка; замена всех конкурирующих старых анализаторов |
| 4. Lifecycle/storage | Частично | Исправления Copy/XML/frequency/lifetime, immutable profiles, graph/link readback, builder, рост и сохранение индивидуальных Rs/C в проверенных случаях | Полная matrix профилей, режимов, Load/Copy/reuse и heterogeneous physics; устранение оставшихся legacy overrides; распространение profiles на реальные конфиги |
| 5. Model export и Train→Test | Частично | Принят physical ModelArchive с image closure, ports, fresh/cross-host roundtrip. В рабочей ветке реализован certified learned-state package с повторным вычислением сертификата | Приёмка новой ветки: расширенная matrix, ASan, независимый аудит, Git-публикация, cross-host learned-state replay и merge. Также diagnostic/budget/external-stop states, recognition/conversion/calibration/PostTune transport |
| 6. Общий контроллер | Частично | NativeTrainingService, adapters, native Before/After scheduler, builder, configured V2 cold JSON/XML; default legacy V1 сохранён | Configured reconfiguration/retarget, полный перенос всех режимов и integration matrix; окончательная compatibility приёмка |
| 7. Алгоритмы | Частично | CapturedPerInput, измеренные signed residuals, invalidation, bounded L/Ns/Rs, topology order, integration checks, независимый final sweep | Динамические per-L Rs domains, длительности окон/recovery, полный N0 spread/repeatability и quantized/best-effort контракт, optional heterogeneous C-trim, полная физическая/inhibition matrix |
| 8. Conversion/PostTune/calibration | Не выполнен по новой спецификации | Исторический код сохранён; его наличие не означает приёмки | Immutable идемпотентное Solo→Recognition преобразование, transactional все PostTune, rollback, Same-Matrix и independent frozen calibration, реальное подтверждение порога |
| 9. Новый пакет и миграция | Частично | Root inventory/runtime/native evidence modules и tests | Главный CLI содержит только inventory; нужны остальные команды, lossless config adapter, полный migration manifest и удаление старых scripts из Bin/PulseLib/Docs |
| 10. Очереди/provenance/publisher | Частично | Runtime identities и проверенная Git-публикация отдельных evidence packages | Production ConditionSpec/serializer, runner, owned PID/leases/locks/crash recovery, fail-closed publisher полного run; ручной test harness их не заменяет |
| 11. Научные контрольные эксперименты | Не выполнен | Implementation tests, characterization и ограниченные compatibility A/B | Исторический replay, cold retrain, научное legacy/V2 сравнение, настоящий order/ITI sweep, полная physics/mode matrix и опубликованная карта результатов |
| 12. Документация | Частично | Поддерживаемая спецификация и документы принятых подэтапов, исправления профильных материалов | Сквозная актуализация всех root/submodule/config/ClDesc материалов, удаление ссылок на старые scripts, единая итоговая спецификация после завершения реализации |

## Последняя рабочая ветка: что действительно проверено

На обоих серверах source остаётся на root
`7186788be098a58091a14025d664647e5d9eb2cd`, PulseLib
`025d809f7b86cc79e18ddd711c6adc40e2396bf8`.
Повторно прочитаны `/home/user/timelearner-refactor/readbacks/s05-learned-a6/`
`results.xml` и `regression.xml`:

| Сервер | Новый learned-state набор | Регрессии | Failures/errors |
|---|---|---|---|
| Elder-1 / .11 | 5 pass + 1 служебный skip | 43 pass + 1 служебный skip | 0/0 |
| M40 / .17 | 5 pass + 1 служебный skip | 43 pass + 1 служебный skip | 0/0 |

Это Classic/Branch × N0/N1 и отдельный Exact-control с явным SyncTolerance=0.2.
Проверены перенос references и сертификата, heterogeneous child C, импорт в
свежий процесс, совпадение frozen traces, сохранение после Reset и отказ ряда
повреждённых пакетов. Это не результат научного распознавания и не подтверждение
сходимости при default 0.02.

Следующий root `dad2cad9…` расширяет tests до 20 кГц, configured sources,
N=1/4/6. Каталога A7 на обоих серверах нет: эти новые проверки ещё не запускались.
Чужие процессы не исследовались; принадлежащих этому build/test checkout активных
процессов при проверке не обнаружено.

Новые A6 артефакты пока не опубликованы завершённым Git evidence package.
ASan, cross-host именно learned-state transfer и полная maintained CTest проверка
последнего shared harness ещё не завершены. Предыдущие physical archive
cross-host проверки не заменяют новую приёмку.

## Обнаруженное уточнение доказательности runtime

В текущей ветке исправлен test harness: executable и соседний runtime ini
разрешаются по фактическому пути процесса, независимо от CWD. Ранее часть
ad-hoc запусков из source могла пользоваться defaults вместо заявленного ini.
Это ограничивает прежнее утверждение об изоляции ini именно для таких запусков;
их физические проверки нельзя автоматически считать недействительными, но
соответствие заявленному runtime ini требует нового подтверждения. A6 использует
исправленный путь. Полный maintained набор после изменения общего harness нужен.

## Последовательность оставшейся работы

1. Завершить приёмку текущего certified learned-state подэтапа и принять child → root.
2. Закрыть недостающие состояния переноса, configured управление и алгоритмические
   ограничения этапов 4–7; проверять реальные компоненты и первичные данные.
3. Реализовать и проверить conversion, PostTune и калибровку этапа 8.
4. Довести root CLI/runner/очереди/publisher, удалить прежние scripts с Git manifest.
5. Провести исторические и научные контрольные серии этапа 11.
6. Закончить evidence/property review и сквозную документационную приёмку.

Документацию и ledger обновлять по ходу каждого пункта. Августовские визуально
подтверждённые 4/8–6/8 сохраняют статус наблюдений исходного протокола; устойчивость
к перестановкам и увеличенному ITI тогда не проверялась. Получение 8/8 не является
условием завершения рефакторинга. Серия D автоматически не возобновляется.
