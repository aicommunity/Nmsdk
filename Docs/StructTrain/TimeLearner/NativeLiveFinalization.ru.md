# Живой переход Train → финализация

Реализация в ветке `codex/timelearner-live-finalization`; серверная приёмка
нового dispatcher ещё не выполнена. Это продолжение полного плана 0–12,
а не закрытие этапов 6–8 или обязательной матрицы.

`ConfigureNativeFinalization(NativeLiveFinalizationSpec)` задаёт неизменяемую
runtime-декларацию до старта Train: implementation ID, conversion и полный
PostTune design с фиксированным порогом либо реальной grid-калибровкой.
Само конфигурирование не строит модель и не выполняет Calculate. Декларация
не является checkpoint и пока не сериализуется свойством ControllerConfiguration.
После Load её необходимо явно задать; отсутствие декларации сохраняет прежние
guards optional modes и прежнее завершение Train.

Общая реализация `TimeLearner/NativeLiveFinalization.h` используется обоими
learner. Структурные действия разрешены только до штатного расчёта детей:

```text
native AfterChildren:
    training service consumes the completed observation
    if Finished and live finalization was declared:
        capture immutable boundary before closing the request
        if no completed certificate: stopped diagnostic, no recognition import
        else: queue finalization; retain active request

next native BeforeChildren:
    validate original controls, bindings, session and full source archive
    privately convert the captured Solo state
    import with the original boundary through the native owner path
    Build / Init; verify effective recognition package
    begin native owned PostTune

ordinary native ticks:
    owned PostTune advances before children
    scheduler calculates children once
    collect terminal PostTune report and execution separately from training outcome
```

Восстановление finished-состояния публичным Need=false→true не используется.
CalculateMode0 сохраняет Need до конца объявленной финализации, после чего
закрывает только локальный запрос. Подключённый provider никогда не записывается
dispatcher; его true требуется до старта. CalculateMode1 оставляет внешнее
управление запросом. Снятие внешнего запроса между capture и entry запрещает
импорт. Reset/Default/UnInit и внешняя перестройка прерывают queued/running scope;
внутренние lifecycle-вызовы импорта и PostTune отделены depth scopes.

План сверяется с действующими public mode/metric/policy, измерительным порогом,
действующими canonical floor/last и числом synthetic passes. Входные trials
объявлены явно, проверяются до обучения: размерность, target hash, уникальные
trial IDs, обе метки для каждой reset policy, полное окно и sample budget.
PostTune повторно проверяет фактическую конечную физику перед изменениями.
Неподдержанные target-only AutoCalibrateFixedLTZThreshold, C-trim и legacy
nonseparable fallback отклоняются явно. Target-reference и Branch legacy
parallel-peak calibration не подменяются target/foil grid; их включение в живую
последовательность остаётся отдельной обязательной работой.

`NativeLiveFinalizationReport()` содержит подписанные declaration, request,
boundary, capture/entry time и отчёты PostTune. `completed` означает терминальное
выполнение финализации; её собственный результат хранится отдельно. Оно не
означает Exact, calibrated, separable или успешную классификацию.
`failed/recovery_required` запрещают дальнейший расчёт детей через штатный
ForceSkipComponentCalculation. Булевы Build/Reset/Calculate не используются
для распространения ошибок. Dynamic checkpoint и mid-probe resume отсутствуют.

Новые native fixtures холодно строят модель из исходного физического профиля,
сохраняют реальные Train CSV/packets, ждут capture естественного Finished и
выполняют PostTune на обычных тиках. Проверяются fixed/calibrated policies,
local/connected request, stop без сертификата и control/reset/stop между capture
и entry. Последующий frozen replay той же target/foil матрицы проверяет
неизменность модели; это не независимый научный Test. До терминальных receipts
и проверки доступных в Git primary эти сценарии не считаются пройденными.

Остаются production job/CLI declaration, независимый evidence reader живого
перехода, all-pattern temporal reports, target-reference/parallel-peak фазы,
вся физическая/режимная матрица и independent frozen evaluation.
