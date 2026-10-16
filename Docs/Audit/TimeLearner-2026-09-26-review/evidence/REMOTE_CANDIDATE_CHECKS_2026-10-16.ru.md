# Release-проверки кандидатных изменений на `.11` и `.17` — 2026-10-16

Проверки выполнены после восстановления SSH-маршрута через `.12`, на серверных Linux Release-конфигурациях. Локальную Windows-сборку и обучение на рабочей станции не запускали. На момент последней проверки tmux-сессий, сборок и процессов `NeuroModelerConsole` на серверах не было.

## Сборка и тесты

На обоих серверах принудительно обновили временные метки изменённых исходников, чтобы исключить пропуск перекомпиляции из-за старых объектных файлов, затем собрали `Test_PulseLib_StorageComponents` из `build/linux-gcc-release-local`.

| Сервер | Кандидатный diff | Сборка | GoogleTest assertions | Итог CTest |
|---|---|---:|---:|---|
| `.11` | Classic и Branch: границы сопротивления, проверка численной устойчивости, общие изменения `NDatasetBase`/`NPulseSynapseCommon`; рабочая копия PulseLib основана на `2b30628` | exit 0; лог `/home/user/NmsdkRuntime/TimeLearnerCandidateChecks-20261016/classic/build-forced.log` | 49 из 49 прошли (10 наборов) | exit 8: после завершения всех assertions падение SIGSEGV при глобальном завершении приложения |
| `.17` | Branch: обработка невалидного пика/no-legal-recovery, перестановка сегментов и audit; общие изменения `NDatasetBase`/`NPulseSynapseCommon`; рабочая копия PulseLib основана на `2b30628` | exit 0; принудительная сборка повторно скомпилировала изменённые translation units | 34 из 34 прошли | exit 8: после всех assertions падение SIGSEGV при глобальном завершении приложения |

На обоих серверах stack trace teardown проходит через `UApplication::UnInit → UEngineControl::PauseChannel → URdkCoreManager::GetNumChannels → UGenericMutexSharedLocker`. Поэтому assertions кандидатных изменений прошли, но CTest как целый процесс завершился с ошибкой; эту причину следует учитывать отдельно от поведения алгоритма. Проверка пока не подтверждает корректность алгоритмов на обучающих прогонах.

Для `.11` полные логи находятся в `/home/user/NmsdkRuntime/TimeLearnerCandidateChecks-20261016/classic/build-forced.log` и `ctest-forced.log`; маркеры кодов возврата — `build-forced.exit` (`0`) и `ctest-forced.exit` (`8`). Для `.17`: `/media/user/Data/NmsdkRuntime/TimeLearnerCandidateChecks-20261016/branch/build-attempt05.log` и `ctest-rebuilt.log`; маркеры — `build-attempt05.exit` (`0`) и `ctest-rebuilt.exit` (`8`).

## Уточнение Branch invalid-peak проверки

Первое сообщение о провале `BranchInvalidPeakNoRecoveryTest.RefusesAfterRepeatedNoActionAboveRmin` было получено при сборке, которая не перекомпилировала `NNeuronTimeLearnerBranch.cpp`: timestamp объектного файла был новее исходника. Этот результат был ложным для текущего исходного candidate diff. После принудительной пересборки изменённый файл вошёл в библиотеку; временная инструментальная печать подтвердила срабатывание `no_legal_recovery`, затем была удалена. В тесте оставлены полезные assertions: после третьего no-action вызова timing error остаётся выше `0.02`, счётчик достигает `3`, и проверяются `FailureReason=3` и `Phase=5`. В итоговом forced run все 34 assertions прошли.

В `.11` forced build также действительно перекомпилировал `NDatasetBase.cpp`, `NNeuronTimeLearner.cpp`, `NNeuronTimeLearnerBranch.cpp`, `NPulseSynapseCommon.cpp` и тестовые translation units. Следовательно, результат 49/49 относится к обновлённым исходникам, а не к старым объектам.

## Ограничения вывода и следующие действия

- Это две разные незакоммиченные кандидатные копии, обе основанные на старом PulseLib `2b30628`; текущая локальная ветка PulseLib уже на `c8a0a891`. Не переносить результаты их тестов на более свежий исходник и не коммитить серверные рабочие деревья напрямую.
- `.11` и `.17` root checkout сильно отстают от origin и содержат незатреканные исторические данные. Не обновлять их поверх существующих деревьев и не чистить их. Перед новыми опытами нужно создать чистые изолированные checkout на актуальном `codex/historical_view`, перенеся в них только кандидатные изменения после отдельного review/rebase.
- Отдельно проверить общий teardown SIGSEGV в тестовом harness. Он возникает после успешных assertions и сам по себе не свидетельствует о дефекте проверяемой логики тренера.
- `NPulseChannelCable::GetAuditVmSummary()` в candidate `.17` найден только как объявление и определение; вызова из тренера нет, поэтому текущий audit min/max `Vm` не получает.
- Эти проверки не включали запуск обучения и не дают метрик сходимости или классификации.