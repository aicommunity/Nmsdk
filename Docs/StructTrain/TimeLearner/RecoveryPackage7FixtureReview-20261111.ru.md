# Проверка сценария package7 после Windows запуска

Исходный набор14 на .14 использует source3edb22a4/Pulse63d7a62 и продолжает
работу без изменения исходников или runtime. Первая завершённая проверка
`NativeRecoveryPackage7/ClassicN0StoppedRoundtripKeepsResponse` отказала с
`native_probe_requires_initialized_ready_learner` (98755ms). Это не PASS переноса.
Полный итог, оставшиеся cases и closure ещё ожидаются.

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
