# Состояние полного плана: повторная сверка 27.10.2026

**Работа возобновлена пользователем 28.10.2026.** Оба прежних post-fix full CTest
сохранены как interrupted_by_user, не приняты. Audit-default defect воспроизведён
и исправлен: по 8/8 lifecycle и 18/18 UContainer passed на обоих workers,
дополнительно те же группы под ASan M40. Оба full A3 завершились: 4/4 suites,
PulseLib 387 pass + 10 skip, 0 failures/errors; по 9 Python tests и 208 primary
trials. Принят root develop `2ad95250fb91c32826399702081c636852a0d56a` с child
merge commits; свежий recursive checkout семи сабмодулей проверен на M40.
См. [PooledFullAcceptance](PooledFullAcceptance.ru.md). Это не весь этап 4/5.
В отдельной ветке `stage05/stopped-training-state` реализуется диагностический
перенос остановленного обучения, включая неполный capture и censored evidence.
Первый ASan A1: 2 pass / 14 failures; обнаружен stale capture plan после
InvalidateTarget, исправлен PulseLib `652c8f3`. Исправленные 16/16 cases прошли
на M40 ASan и Elder-1 normally. Последующая версия root 57b36592 / PulseLib 12c5ef5
прошла 20/20 native и 10/10 Python на каждом worker, по 66 primary trials.
Git-transfer: 16 пакетов M40→Elder-1 и 20 Elder-1→M40, byte-exact frozen CSV.
На последней версии Elder-1 прошли также 22 native regressions и 9 Python
проверок сертифицированного пути по 62 primary trials. Все пакеты опубликованы;
локально проверены 2317 stored и 2313 raw hashes. Этот более поздний snapshot
не входит в full source 7fb92a4; scoped проверки завершены, merge в develop ещё
не выполнен. Это не весь этап 5. См. [StoppedTrainingState](StoppedTrainingState.ru.md).
Историческая точка остановки: [ResumeAfterPause](ResumeAfterPause-2026-10-27.ru.md).

**План не завершён. Полностью принят этап 0. Частично выполнены этапы 1–7,
9, 10 и 12. Этапы 8 и 11 по новой спецификации не выполнены.**
Готовые API и адресные тесты не означают завершения соответствующего этапа.
ControllerVersion=2 пока нельзя рекомендовать для всей экспериментальной матрицы.

Эта сводка заменяет прежний текст с устаревшими промежуточными дополнениями.
Перепроверены Git, код, опубликованные manifests, непосредственно серверные
XML/логи A9, A15 и property-fixed-A2. Новые сборки для ответа о статусе не
запускались. Работающий A15 не прерывался. Старые отчёты относятся к своим SHA.

## Git: рабочие ветки и принятый develop

Исторический снимок перед коммитом сводки 27.10; актуальная приёмка 28.10 —
PooledFullAcceptance. На этом историческом снимке деревья чистые, gitlinks совпадают
с фактическими child HEAD.

| Репозиторий | Рабочий HEAD | Принятый develop |
|---|---|---|
| Root | `f3b45cb9300e4dd43f9d4c4d212e366b75195af1` | `68b77ac542cbd21479eab45c474b3603591add97` |
| PulseLib | `025d809f7b86cc79e18ddd711c6adc40e2396bf8` | `c1d5b177278f1eb347c1ebc725555837c36642bb` |
| Bin | `f5e1d0200127223981daa71da22cf5ee02fdbc60` | та же версия |
| Rdk | `1223bcc18cf1ba106e8f8a17f20cce8c000c104d` | `ef4f033704d54f11d06e4da2b3518c313f3a9992` |

Root/PulseLib: `stage05/native-trained-state`; Rdk:
`stage04/pooled-property-bindings`. Эти изменения ещё не приняты в develop.
Отдельный Rdk component-order fix уже принят. Следующие merge: после приёмки,
дочерние репозитории → root, merge commits без переписывания истории.

## Сверка с этапами утверждённого плана

| Этап | Статус | Сделано | Осталось |
|---|---|---|---|
| **0. Исходное объединение** | **Полностью** | Начальные merge commits, согласованные gitlinks, develop hints, проверка публикации и recursive checkout | Приёмка текущих feature-веток относится к следующим этапам |
| **1. Доказательства/параметры** | Частично | Исходные SHA, исторические опорные commits, inventory, дефекты, контракты | Полный ledger с августа и всех аудитов; semantic code catalog 211/211 исходных записей завершён и сверён с 217 текущими declarations (включая 6 новых); runtime/property matrix и исправление найденных gaps не закрыты. Нужен разбор 324 script candidates. Шесть новых configured properties описаны отдельно |
| **2. Сборки/runtime** | Частично | Изолированные runtime двух серверов, manifests, ресурсы, tracked Reports, Git evidence packages | Автоматический production run bundle, реально загруженные зависимости Train, окончательная приёмка общей тестовой инфраструктуры |
| **3. Наблюдения/scorer** | Частично | Строгие схемы, метки/ID, completeness, nonfinite, размерности >4, native burst assignment и отрицательные проверки | Один production-путь Train → calibration → frozen Test → оценка; замена конкурирующих старых анализаторов |
| **4. Lifecycle/storage** | Частично | Исправления Copy/XML/frequency/lifetime, immutable profiles, graph/link readback, builder/growth, сохранение индивидуальных Rs/C в проверенных случаях; принят component-order fix | Приёмка pooled-binding fix; полная Load/Copy/reuse и heterogeneous physics matrix; оставшиеся legacy overrides; profiles в рабочих конфигах |
| **5. Export/import, Train→Test** | Частично | Принят physical ModelArchive. В feature реализован certified completed-state пакет с references, финальными пробами и повторной проверкой сертификата; fresh-process/cross-host перенос и rollback адресно проверены | Устранить full-suite отказы, принять ветку; diagnostic/budget/external-stop состояния, recognition/conversion/calibration/PostTune transport и сквозной production Train→Test |
| **6. Общий контроллер** | Частично | NativeTrainingService, адаптеры, native scheduler, builder, configured V2 cold JSON/XML; default legacy V1 | Configured reconfiguration/retarget, все режимы и окончательная compatibility/integration matrix |
| **7. Алгоритмы** | Частично | CapturedPerInput, измеренные signed residuals, invalidation, bounded L/Ns/Rs, topology order, independent final verification | Динамические per-L Rs domains, окна/recovery, полный N0 spread/repeatability и quantized/best-effort контракт, optional heterogeneous C-trim, полная physics/inhibition matrix |
| **8. Conversion/PostTune/calibration** | **Не выполнен по новой спецификации** | Исторический код сохранён; это не приёмка новой архитектуры | Immutable идемпотентный Solo→Recognition, транзакционные все PostTune/rollback, Same-Matrix и independent frozen calibration, реальное подтверждение порога |
| **9. Пакет/migration scripts** | Частично | Корневые inventory/runtime/native evidence modules и tests | CLI сейчас предоставляет только inventory; остальные команды, lossless config adapter, полный migration manifest и удаление старых scripts из Bin/PulseLib/Docs |
| **10. Очереди/provenance/publisher** | Частично | Runtime identities и Git-публикация отдельных проверочных пакетов | Production ConditionSpec/serializer, runner, owned PID, leases/locks/crash recovery, fail-closed publisher полного run. Ручные test scripts их не заменяют |
| **11. Научные контрольные серии** | **Не выполнен** | Implementation tests, characterization, ограниченные compatibility A/B | Исторический replay, cold retrain, научное legacy/V2 сравнение, order/ITI sweep, полная physics/mode matrix и карта результатов |
| **12. Документация** | Частично | План, контракты, документы принятых подэтапов и адресные исправления | Сквозное обновление root/submodules/config/ClDesc, удаление ссылок на прежние scripts и единая итоговая спецификация |

## Подтверждённые адресные результаты

Результат относится к проверенному SHA и не переносится автоматически на последний HEAD.
Подробности: [NativeLearnedState](NativeLearnedState.ru.md),
[validation manifest](NativeLearnedState.validation.json),
[ComponentOrderBounds](ComponentOrderBounds.ru.md).

| Проверка | Результат | Ограничение вывода |
|---|---|---|
| A7, оба сервера, root `4cc548656857bd97d927c16fdd070c7608e091f0` | На каждом 16 learned-state pass + 1 helper skip; 43 regression pass + 1 helper skip | Classic/Branch × N0/N1, 2/20 кГц, configured sources, N=1/4/6; адресная transport matrix |
| Cross-host A6 | По пять пакетов в каждом направлении, frozen CSV побайтно совпали | Перенос модели, не научный verdict распознавания |
| A14, оба сервера, root `51c54abb95881ced0942e5cfd14928609da00ac6` | На каждом 5/5 native, 13/13 UContainer, 9/9 Python; независимо проверены 62 training trials и четыре rollback probes | Реальная ошибка attach и откат графа/отклика; Exact warm continuation без recapture |
| ASan A3, .17, тот же root | 4/4 pass; Python audit четырёх пакетов, 56 training trials, четырёх rollback probes | detect_leaks=0; не полная sanitizer matrix и не доказательство отсутствия утечек |
| Component-order bounds | Дефект воспроизведён; обычная и ASan проверки пройдены; Rdk develop merge `ef4f033704d54f11d06e4da2b3518c313f3a9992` принят | Закрыт отдельный дефект Rdk, а не весь этап 4 |

В опубликованных learned-state пакетах ранее проверены 7748 stored SHA и 7744
raw payloads. Эти числа не включают новые неопубликованные результаты ниже.
Exact-control использует явный SyncTolerance=0.2; dimensional fixtures также
имеют явно расширенные допуски. Это не подтверждение сходимости при default 0.02.

## Блокеры и незавершённые проверки: непосредственный серверный readback

**Полный maintained CTest .11 A9 не прошёл.** Root
`270c62ce55a80a9efea6e434bba8ca5664a821af`, каталог
`readbacks/s05-learned-a9`: три suites прошли, PulseLib suite не прошла.
Внутри PulseLib: **395 tests, 370 passed, 10 skipped, 15 failed**.
Отказы learned-state export/import сопровождаются null/external property binding
в Dataset/Generator. Адресные зелёные наборы не отменяют этот отказ.

Native reproducer выявил сохранение старых внешних прямых связей свойств при
Return→Take reuse и Copy. Исправление выполняется в Rdk с сохранением внутренних
связей и штатных Build/Reset/Default. Strict model identity не ослабляется.

**Новое исправление прошло адресные unit и integration проверки; полный gate открыт.** На .11
`readbacks/s04-property-fixed-a2`: **18/18 UContainer tests passed**,
failures/errors/skips=0. Root `f3b45cb9300e4dd43f9d4c4d212e366b75195af1`,
Rdk `1223bcc18cf1ba106e8f8a17f20cce8c000c104d`. Проверены external
scalar/matrix/vector bindings, Copy внутренних связей, constructor wiring и
обычный lifecycle. На .17 18/18 прошли под ASan (detect_leaks=0). На .11
последовательно прошли 25 builder и пять learned-state tests: 30/30; дополнительно
18/18 UContainer и 9/9 Python. Проверены 62 training trials и четыре rollback probes.
Оба evidence packages опубликованы через Git; локально проверены 3856 stored SHA
и 3852 raw payloads. См. [PooledPropertyBindings](PooledPropertyBindings.ru.md).

**Полный maintained CTest .17 A15 также не прошёл.** Root
`51c54abb95881ced0942e5cfd14928609da00ac6`, `readbacks/s05-learned-a15`:
три быстрые suites прошли, PulseLib: 395 tests, 370 pass, 10 skip, те же 15 failures.
На обоих workers independently проверены по 16 исходных trainings и 208 trial
CSV/JSON; это не отменяет transport failures. Исходные failed runs опубликованы
в тех же Git-пакетах. Runtime старых заданий не изменялся.

**Повторные post-fix full suites остановлены пользователем на обоих workers:**
`readbacks/s05-pooled-full-a1`, root `f3b45cb9300e4dd43f9d4c4d212e366b75195af1`.
CTest exit=8, PulseLib INTERRUPT; полного PASS нет. До приёмки
Rdk/PulseLib/root feature не закрываются. Новый test-only audit-default
reproducer в root 2063e41e ещё не запускался.

Последнее предложение относится к моменту паузы 27.10: 28.10 baseline выполнен,
дефект явного Default (не stock reuse) подтверждён и исправлен в PulseLib
4919bac2bd359118b13310862e54bcd24492967d. Адресные проверки опубликованы.
Full A2 не стартовал из-за shell preparation error; A3 на root
7fb92a4a57b9773ff56996cf2c7b8c75b2746cd8 сейчас выполняется на обоих workers,
используя проверенные immutable A2 binaries. Старые failed/interrupted runs
не перезаписывались. До terminal PASS никакого merge/полной приёмки нет.

## Очерёдность оставшейся работы

1. Закрыть pooled-binding дефект Rdk: integration regression, sanitizer, повторный
   maintained CTest; опубликовать положительные и отрицательные данные.
2. Принять certified-state подэтап child → root, затем добавить недостающие
   состояния переноса и закончить configured control/алгоритмические части 4–7.
3. Реализовать новую conversion/PostTune/calibration архитектуру этапа 8.
4. Довести CLI/runner/очереди/publisher; удалить прежние scripts с Git manifest.
5. Провести исторические и научные контрольные серии этапа 11.
6. Завершить evidence/property review и сквозную документационную приёмку,
   выполняя их также по ходу технических этапов.

Августовские визуальные 4/8–6/8 сохраняют статус рабочих наблюдений исходного
протокола; перестановки и увеличение ITI тогда не проверялись. Получение 8/8
не является условием завершения. Серия D автоматически не возобновляется.
