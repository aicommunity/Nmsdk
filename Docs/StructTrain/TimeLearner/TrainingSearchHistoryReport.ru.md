# Измеренные кандидаты и конечный снимок native Train

Новый root CLI analyze --format native-search-history принимает signed run-manifest.json операции train, выполняет полный production audit_run_manifest, затем читает native summary8 из hash-bound исходных bytes. Поддерживаются Classic/Branch, N0/N1 и произвольная допустимая размерность; это отчёт по уже выполненным пробам, не запуск обучения и не новый scorer сходимости. Иные summary versions явно отвергаются и продолжают иметь свои прежние readers.

Отдельно выводятся complete candidate records с исходными signed timing bounds/amplitude residuals, parameter-change cost и прочими полями (включая C witnesses); recorded rejections; assessed per-input Rs domains; producer-reported counters; actual terminal graph revision/parameters; final verification group IDs. Число measured candidates не выдаётся за число всех search probes: последние включают anchor и другие действия. Domain assessment не является предъявлением/измерением точки.

Сопоставление terminal model с candidate history требует одновременно одинакового model revision и полного parameter vector. Совпадение L/Rs/Ns без revision не доказывает совпадение всей физики. Даже точное совпадение с candidate не заменяет fresh final pass/certificate; этот анализ не даёт training или scientific verdict. Если history не сохранена, соответствующая coverage — null/unknown, а не false/«не измерено».

В реальном completed budget16 Classic состоянии3b8a160f... actual L22, но15 valid records относятся к L1 (два Rs), L2..14. Все timing residuals вне sync0.02; terminal model не совпадает ни с одним measured candidate и final_group_ids пуст. [Принятый исходный Train](ValidationPlans/M40PublicationReceiptBudget16TrainA1-20261113/RESULT.ru.md). Это конкретная причина не интерпретировать final morphology как результат сходимости; глобальная невозможность обучения не следует.

Перед проекцией summary/job/execution сверяются с original manifest SHA/size, каждый файл читается bounded frozen read; manifest повторно сверяется после анализа. CLI запрещает запись результата внутри original run directory. Основной native DATA audit не удаляется и не заменяется сравнением нескольких полей или producer bool. Source snapshots работающих заданий не обновляются.

Проверки:7 unit controls (revision vs parameters, empty retained history, Branch/N0/N7 projection, extra C/cost preservation, duplicates/schema/nonfinite, changed-after-audit refusal, CLI output overlap) и1 actual production CLI case полного исходного N4 run. Последний проверяет конкретные15/13/28 records и отсутствие measured/final coverage terminal L22. C++ тело в Python не копируется. Локально выполнен только AST parse. [Elder:7/7 unit controls приняты](ValidationPlans/ElderNativeSearchHistoryA1-20261113/RESULT.ru.md); [M40:8/8, включая полный исходный N4 run, приняты](ValidationPlans/M40NativeSearchHistoryA1-20261113/RESULT.ru.md). Новый формат не закрывает весь этап3/7/9 или full physical matrix.

## Измеренная траектория input0 последнего принятого Train

Таблица получена из [исходного production CLI output](ValidationPlans/M40NativeSearchHistoryA1-20261113/completed-readback/worker/tmp/actual-training-search-report.json), проверенного на M40. Амплитудные остатки приведены в native units; перевод в SI отдельно не подтверждён. Во всех строках within_timing=false. Таблица не включает отклонённые пробы и не описывает все58 search probes.

|L|Rs, МОм|Временной остаток, s|Амплитудный остаток|
|---:|---:|---:|---:|
|1|86.0000000|-0.4800|0.000000e+0|
|1|2.88007156|-0.4825|3.308828e-1|
|2|86.0000000|-0.4705|-3.462558e-3|
|3|86.0000000|-0.4615|-5.368698e-3|
|4|86.0000000|-0.4520|-6.605703e-3|
|5|86.0000000|-0.4425|-7.488893e-3|
|6|86.0000000|-0.4330|-8.159176e-3|
|7|86.0000000|-0.4235|-8.689981e-3|
|8|86.0000000|-0.4140|-9.123674e-3|
|9|86.0000000|-0.4045|-9.486512e-3|
|10|86.0000000|-0.3950|-9.794164e-3|
|11|86.0000000|-0.3850|-1.005370e-2|
|12|86.0000000|-0.3745|-1.026773e-2|
|13|86.0000000|-0.3630|-1.043673e-2|
|14|86.0000000|-0.3495|-1.055690e-2|

При Rs86МОм увеличение L уменьшает модуль временной ошибки и одновременно увеличивает модуль амплитудной. Единственная сохранённая complete точка с другим Rs относится к L1; по ней нельзя заключать, что нормализация при L14 или L22 невозможна. Все13 retained rejections имеют reason rejected_candidate_window:ambiguous. Принадлежность каждого отказа конкретной геометрии требует связи с исходной пробой; один список rejections такой связи не доказывает.28 оценённых Rs-интервалов не означают28 измеренных Rs-кандидатов.

## Следующее решение об алгоритме

Сначала выполнить ограниченную диагностику Rs при неизменной геометрии фактического L22, отдельную от Train и классификации. Использовать штатный импорт полной stopped модели; исходные storage/дочерняя физика/пачка/частота/порог сохраняются. Существующие prepare_stopped_job/expected_import_parameters задают семантику Rs intervention, но не считаются проверенным готовым запускателем нового composite/candidate-window package: перед запуском обязательна проверка совместимости схемы/configuration/window и native import readback. При отсутствии такой поддержки нужен отдельный production adapter с адресными проверками; экспорт в неполный legacy overlay запрещён. Для changed и matched-control нужны одинаковые абсолютные model clocks, actual input events, reset policy и byte-equal warm baseline; прежний matched_resistance_analysis задаёт этот принцип, но его старую жёсткую матрицу Classic+Branch нельзя выдавать за новый single-Classic protocol.

Перед запуском зафиксировать конечный список Rs из свежей per-input native domain assessment, включая unchanged86МОм и ограниченные изменённые точки; старый интервал другого model revision не использовать как live bound. Изменение должно затрагивать только заявленный excitation bank и разрешённые зависимости; полный semantic graph diff обязателен. Выбирать максимум закреплённого импульса; ambiguous остаётся отрицательным измерительным исходом, полный waveform сохраняется для визуального анализа. Не заменять его максимумом пачки и не захватывать новую цель CapturedPerInput на изменённой геометрии.

Если при fixed L корректная Rs-нормализация восстанавливает измеримость/амплитуду, отдельно проверить изменение порядка поиска L/Rs: механическое выделение кода, затем алгоритмический commit с A/B. Если нет, исследовать оставшиеся причины по waveform и конкретным rejected trials. Одна диагностическая длина не доказывает PhysicalInfeasible. Длинный Train, увеличение budgets и изменение tolerances не являются следующим автоматическим действием. Этот ограниченный протокол пока не выполнен.

Необходимый [raw-burst adapter](NativeBurstReadback.ru.md) прошёл последующую адресную проверку: после исправления monitor и schema dispatch приняты свежая Console сборка/2 roundtrip,13 Elder DATA/declaration controls,5 actual-file reader checks и6 реальных Console процессов Classic/Branch N=2. [N4 серия на фактическом L22 запущена](ValidationPlans/M40L22BurstResistanceStudyA1-20261113/STATUS.ru.md); её результат ещё не принят. Малые контроли не подменяют причинную диагностику большой модели.

Production-модуль native_burst_resistance_study выполняет импорт фактической stopped-модели, исходный replay, matched no-op и конечный заранее объявленный список Rs. Каждый changed probe проходит native domain assessment, full graph audit и сверку clocks/actual inputs/warm baseline. Нулевое изменение потенциала допускается как отрицательный результат, а failed import/probe прекращает серию. Графики должны охватить все Soma channels с фактическими входами, обзором и деталями не более901 исходного отсчёта, без прореживания. Общие максимумы явно помечены как диагностические, не как измерения закреплённого импульса. Запуск ещё не является полученным и проверенным результатом N4.

## Неполная терминальная группа L22

В исходном пакете найдены62 measurement records. Терминальной revision3b8a160f... соответствуют61 (input3, complete/valid) и62 (input0, incomplete). У62 сохранены два полных CSV full-before/omit-0 по3601 samples и censored omit-1 на415 samples, закончившийся по native_training_time_budget_exhausted. Это не три полные пробы и не завершённая omission group. Исходные bytes уже входят в опубликованный Train primary; новые предъявления перед их разбором не требуются.

composite_training_temporal получает явный --allow-incomplete-groups для диагностического показа таких данных: полный production package audit сохраняется, статусы взяты из связанных native packets, неполученная часть окна затенена, отсутствующие пробы не создаются. Без флага incomplete group по-прежнему отвергается. Schema3 отчёта не даёт assignment/certificate/scientific verdict. Серверная проверка на фактической группе62 и визуальная приёмка ещё ожидаются.
