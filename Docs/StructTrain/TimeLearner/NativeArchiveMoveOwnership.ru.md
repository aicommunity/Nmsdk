# Передача владения архивом: проверка кандидата

**Итог SDK355/M40:**15 audited completed PASS; C0 остановлен kernel OOM при
4GiB за1798.0285016261041s, returncode−9, без итогового JUnit; две warm проверки
не запущены. Полный18-case gate не принят. [Точные terminal/closure records](ValidationPlans/NativeArchiveMove18-20261110/terminal-readback.json)
сохраняют исходный отрицательный результат. Исправление move прошло свой
адресный тест, но недостаточно для всего memory-сценария.

До OOM source Train и export завершились:39 files/88467238 bytes, summary7
finished/exact,0 edits/4 probes,8184 sampled frames/301080 raw primary bytes.
Model revision0185754b40a2fc4dd306b8a60ed9c3869f22bf96672a25a251c45119833b4155
совпадает с прежним C0. Это engineering SyncTolerance0.2, не stock default0.02
и не классификация. Import/reexport/comparison ещё не приняты; между ними нет
достаточных phase markers, поэтому точное место OOM пока не установлено.

[Измерение размеров Source package](ValidationPlans/NativeArchiveMove18-20261110/source-size-diagnostic.json)
показывает33.49MB pretty JSON, measurement_archive10.83MB в compact UTF8 и
103876 JSON containers. Большие повторяемые поля — C0/storage-image witnesses;
raw measurements составляют около301KB. Это область дальнейшего профилирования,
а не доказанная единственная причина OOM. Полные primary ещё требуют Git capture.
Дальнейшие прежние записи «выполняется» ниже являются промежуточными снимками.

Промежуточная проверка SDK355 на M40: оба targets собраны; первые10 actual
JUnit cases completed/run без failure/error/skip. Новый ownership case прошёл
за7.165s, Load/XML8 и membrane stages также прошли. [Наблюдение10 случаев](ValidationPlans/NativeArchiveMove18-20261110/first10-readback.json).
Остальные cases ещё выполняются; полного18-case PASS и вывода об устранении
C0 OOM пока нет. Исходный raw XML и полные primary будут включены в итоговую
компактную публикацию, текущий readback её не заменяет.

Обновление: контрольный C0 на старом SDKff42 также завершился kernel OOM при
4GiB, wall1821.0976375229657s, returncode−9. JUnit отсутствует, assertions
not_assessed; loaded-runtime capture не успел завершиться. Группа закрыта,
lease released. [Точные10 исходных metadata files](ValidationPlans/NativePackage6C0Baseline-20261110/terminal-readback.json)
сохранены lossless/base64 с размерами и SHA256. Это подтверждает наличие
проблемы до XML/Load исправлений, но не устанавливает единственную причину
и не является приёмкой move-кандидата. Полные первичные данные обоих isolated
C0 прогонов ещё требуют компактной Git-публикации.

10.11.2026 подготовлена отдельная SDK-версия
`355c60df066bdc8da09bd6d7872b47f6e71c0494`, PulseLib
`165d49da7e65cd6ac59bca2812ce52884ddd50c2`, Rdk
`de4134235c0dcb8b91fd9a43b267348ad1a163ca`.

В декодированном архиве явно объявленный copy constructor подавлял implicit
move. В результате передача через `std::move` копировала первичные трассы.
Добавлены defaulted move constructor/assignment и copy assignment. Проверки
архива, формат данных и математическая постановка не меняются. Отдельная
копия записей в retained legacy proof сохраняется намеренно: её нельзя
уничтожать без проверки потребителей этого proof.

Новый integration case
`NativeArchiveOwnership/MoveRetainsDecodedPrimaryStorageAndCopyIsIndependent`
декодирует реальный сохранённый package6. Проверяет передачу backing storage
записей и вложенных samples, независимость явной копии и сохранность
document/protocol/reference groups/current attempt. Это проверка production
decoder и типа архива, а не копии их реализации в тесте.

## Объявленная серверная проверка

[Спецификации](ValidationPlans/NativeArchiveMove18-20261110/cohort.json)
зафиксированы в root `601ac11df7e0ccf2122175e0ba5094ee5b093dbc` до запуска.
Включены новый case и все17 случаев предыдущего repair17. Пять package cases
разделены на отдельные процессы/JUnit. Лимиты каждой leaf-группы остаются
4GiB/128 tasks; ASan `detect_leaks=0`, те же build flags и fixtures.

Штатная canonical preparation прошла на M40:4074 source files,29 SDK modules,
18 cases/10 leaf groups; completed/return0, group closed, diagnostics clear.
Она не выполняла C++ tests и не доказывает корректность исправления.

Запущена свежая сборка и последующий gate:
`/media/user/Data/TimeLearnerRefactor/readbacks/s05-native-archive-move18-m40-a1`.
[Наблюдение запуска](ValidationPlans/NativeArchiveMove18-20261110/launch-observation.json)
содержит supervisor identity и привязку к группе процессов. Это промежуточное
наблюдение, не итоговая приёмка. Исходники и runtime предыдущих заданий
не изменялись; контрольный C0 на SDKff42 продолжал работать параллельно.

## Что остаётся доказать

Нужны фактические JUnit18, закрытие групп, сравнение C0 peak memory и результата
при прежнем лимите, публикация полных компактных primary и проверка переноса
на Elder. Если C0 снова завершится OOM, изменение не объявляется достаточным:
следует исследовать другие копии decoder/replay, сохраняя проверки данных.

Даже PASS18 не закрывает полный package regression, Console Train→Test,
матрицу режимов/физики и этапы0–12. Научная классификация этим gate не
оценивается. До соответствующей приёмки ветки не объединяются в develop.
