# Приёмка файлового входа NDataset, 03.11

Scope — строгий parser и отказ горячего reload без продолжения прежнего сигнала.
Полные этапы3/4/9 и весь исходный план остаются частичными.

Pulse develop merge `5a5256577a5f708742befb0b87aedeb575c324e2` опубликован;
его Core побайтно совпадает с проверенным6a60f5c. Удалённая достижимость merge
подтверждена до записи gitlink и публикации корневого develop.

Parser использует full-token locale-independent conversion, integer range и
finite double проверки, точное число полей и проверенную MaxSpikes metadata.
Транспортные BOM/whitespace/CRLF и оба штатных layout поздних slots сохраняются.
Missing file остаётся idle/retryable; повреждённое содержимое не превращается
в0 и не принимается как валидная метка/паттерн. Allocation bounds — пределы
int-indexed MDMatrix, не искусственное ограничение научной задачи.

При invalid reload прежние matrices остаются для диагностики, но генераторы
останавливаются штатным Reset. Native Ready/operation diagnostics сохраняют
ошибку, lifecycle bool остаётся true. При восстановлении файла native Build/
Reset заново готовит источник до расчёта детей без nested Calculate. Новый
граф и параметры не применяются на каждом тике; storage prototypes не меняются.

Проверенный root `b05a098893e7e0cb50c89bdcacf2718d974078d3`, Pulse
`6a60f5c63c23a8f0645480408a5f60b64ed85957`, Rdk
`a62393f7791cc4ad10d1c2c11f255b3db3334f89`, Bin
`14a88195a8a5538d3a2f5c0657981488e38829b7`. После этого исполняемые App/Scripts/
Tests/CMake не изменены; дальнейшие правки кандидата — документация и evidence.

| Проверка | Root evidence | Итог |
|---|---|---|
| Старый permissive parser, ASan22 | `e37135ab04f244a1e680452366fb872826cfab94` | 15 ошибочно принятых входов |
| Cold normal26 | `ea03ae8d2c752d87c46d899c90d4431c2622a021` | 26 PASS,7 readers |
| Cold ASan26 | `22a037fd0f7f345ada4c5aa1260d3389662ca5dc` | 26 PASS,7 readers |
| Integrated normal baseline53 | `e4f4a1fa7e349ced8f1f736e01717e84b0de614c` | 51 PASS,2 stale-output failures |
| Integrated ASan baseline53 | `84f2ff1e3520f5e369ddb690a02b20b7ae2b3625` | 51 PASS,те же2 failures |
| Integrated normal correction53 | `5c94d5490be958145989c5d019015c6acd0ccd51` | 53 PASS,17 readers |
| Integrated ASan correction53 | `33b95d5b173691ce0df067efe65b8954c098d079` | 53 PASS,17 readers,actual libasan |

Все outer/member SHA256 проверены. В каждом integrated correction пакете261
members; actual ASan mapping libasan.so.8.0.0 подтверждён. Normal/ASan отдельно
для baseline и correction имеют одинаковые85 CSV и52 cold input/observation
файла. До/после исправления83 соседних CSV не меняются; в двух hot CSV меняются
только3 invalid-phase samples1→0 на каждой частоте. Валидное исходное и recovery
расписание, soma arrays source-controls и размерности сохранены.

Первичные данные, журналы, manifests и точные comparison hashes находятся в
Reports/StructTrain/TimeLearner/s03-dataset-file-* и двух comparison разделах.
Неудачные include/spec attempts сохранены с корректным статусом. Их завершение
не считается проверкой алгоритма; негативный baseline не перезаписан fix-ом.

Не заявлены multirate-физика нового контроллера, обучение, Exact, 8/8, полная
матрица режимов/профилей, import arbitrary corrupt models или общий lifecycle
checkpoint. Августовские результаты не переоцениваются. C₀ ownership развивается
отдельно и не включается в этот merge. Приёмка — --no-ff Pulse develop, затем
root develop с точным опубликованным gitlink; Rdk/Bin остаются неизменными.
