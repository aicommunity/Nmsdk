# Настоящий Console cold8: подготовка, не приёмка

Добавлен RecoveryConsolePipelineTest с двумя server-only cases Classic/Branch. Общая механика вынесена отдельно из прежнего cold7 harness; default schema7, run_id suffix, test IDs и путь старого fixture сохранены. Runtime-проверка этого выделения и нового cold8 ещё требуется; наличие кода не считается выполнением.

Новый cold8 не переименовывает package6/схему7. Он полностью восстанавливает фактический Git corpus native10, проверяет completed N0 source7/summary8 и весь внешний primary mirror. Используются исходная configuration8 и зарегистрированные immutable storage images; saved learned state не передаётся в source_solo Train. Новый public Train должен сам получить Exact и обученную модель.

Последовательность для каждой топологии:

1. Проверить immutable runtime manifest, control/corpus bindings и source SHA; подготовить новые output/controller paths.
2. Выполнить настоящий Console preflight, затем cold Train. Ошибка/timeout/unresolved не допускают переход к обычному обученному Test.
3. Экспортировать фактический solo state через public CLI, импортировать recognition model, выполнить четыре полных target/foil пробы reset-per-trial и проверить неизменность модели.
4. Выполнить historical same-matrix measured-grid calibration, реальное подтверждение выбранного порога, frozen replay и rollback/replay silent candidate. Nonseparable сохраняется отдельным исходом.
5. Проверить execution5/package7/config8, ledger hash/count, полный primary mirror, manifest, actual PID/cgroup closure и освобождение reservations для каждой фазы.
6. Сохранить компактный portable primary corpus через Git и выполнить независимый анализ. Построить временные графики Soma SumPotential на все предъявления с фактическими входными импульсами: отдельные читаемые панели/увеличения и общий временной масштаб; полные рисунки кэшировать на M40, выбранные публиковать в Git.

Технический scope N=2/N0/SyncTolerance0.2 явно сохранён. Тест не подтверждает научный N4/default0.02 или независимую оценку после same-matrix калибровки. Test использует полное окно и общий максимум; критерий закреплённого импульса относится к Train. C-trim/PostTune выключены, новые физические гипотезы не вводятся.

Запуск разрешается только после получения точного результата native32 M40 и проверки созданного runtime; при работающем build исходники/runtime не изменяются. Для восстановления568983084bytes необходим output budget с запасом на новый Train и calibration data: прежний128MiB бюджет использовать нельзя. Конкретный budget/путь новой job фиксируются после измерения данных native32.
