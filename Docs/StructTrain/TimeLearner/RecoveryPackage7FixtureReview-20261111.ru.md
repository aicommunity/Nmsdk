# Проверка сценария package7 после Windows запуска

Исходный набор14 на .14 использует source3edb22a4/Pulse63d7a62 и продолжает
работу без изменения исходников или runtime. Первая завершённая проверка
`NativeRecoveryPackage7/ClassicN0StoppedRoundtripKeepsResponse` отказала с
`native_probe_requires_initialized_ready_learner` (98755ms). Это не PASS переноса.
Полный итог, оставшиеся cases и closure ещё ожидаются.

Уточнение после завершения: Windows F1 наблюдал все14 cases,3 PASS/11 FAIL;
whole process закрыт. M40 F1 наблюдал227 из240 cases,226 PASS и один тот же
отказ первого package7 case; следующие13 не запускались. Outer+130 child
groups закрыты, lease released, record_errors=[]; исходные records сохранены.

В исходном `RecoveryPackageRoundtrip` после `ImportNativeLearnedState` сразу
вызывался `QueueNativeProbe`. Импорт обоих learner явно устанавливает
`Ready=false`, поскольку заменён граф. Public QueueNativeProbe требует Ready
и Init. В тесте пропущена обычная native-инициализация после переноса. Это
проверяемое противоречие последовательности вызовов; оно не доказывает,
что сам экспортированный граф повреждён.

В следующем source изменяется только fixture:

```text
import through public native model import
require Adopted
capture adopted semantic revision
call native owner Build and Init
require Ready and Init; compare adopted revision
require service remains Finished and retains certificate/ledger
export/read back actual state and summary
queue and compare native raw response
```

Не меняются readiness guard, bool-контракт lifecycle, production import,
параметры и математические допуски. Не выставляются Ready/Init вручную, не
вызывается Default и не выполняется дополнительный learner Reset. Build
завершает штатную структурную настройку принятого графа; сохранность состояния
контролируется последующими прежними assertions и новым сравнением revision.
Результат этих правок пока **не проверен сборкой или выполнением**.

Последующая проверка M40 F3: sourcee75f1f7/Pulse63d7a62 собран успешно.
Первый case уже проходит readiness boundary, но `Build` переводит imported
controller из Finished в Idle. Поэтому первый вывод «достаточно поправить
fixture» был неполным. Ранее указанные assertions обнаружили production defect
в `ABeforeBuild` обоих learner: безусловный ResetControl для protocol4/5.
F3 завершён0/1, оставшиеся13 не запускались; outer+один child закрыты,
lease released. Эти результаты не объявляются PASS переноса.

Следующее исправление Pulse1110808 сохраняет только Finished boundary без
live composite/search и с сохранённой исходной конфигурацией. Active Build
по-прежнему прерывает управление, explicit Reset переводит в Idle. Никакой
Ready/Init флаг вручную не выставляется. [Контракт в PulseLib](../../../Libraries/Nmsdk-PulseLib/Docs/TimeLearner/ImportedCompositeBuildBoundary.ru.md).
14 roundtrip cases усилены проверками detached state и explicit Reset;
добавлены4 active-Build regressions protocol4/5 для обеих топологий.
Это новое production исправление ещё требует compiler/runtime приёмки.

Второй дефект fixture: `SavePortableObject("package7", ...)` использовал одни
имена для всего процесса. Linux leaf-per-case запуск изолирует каталоги,
а Windows выбранные14 выполняет одним процессом. Следующие cases могли
перезаписать предыдущие source/imported responses и модели. Новый префикс
включает test suite и case. Это изменение должно быть отражено в следующих
artifact rules и независимом corpus collector; старый работающий F1 не меняется.
Cache source сохраняется у породившего его case; повторно использующий его
warm case пишет свой полный imported package/summary/response и warm package.
Список файлов одного общего каталога F1 не является полным corpus всех14 cases.

Нужны серверные compile и адресный повтор14 cases, проверка полного набора
артефактов по case, затем положительный независимый package7/summary8/ledger
audit на фактических primary. До этого дорогой recovery Train и научная
приёмка нового переноса остаются открытыми.
