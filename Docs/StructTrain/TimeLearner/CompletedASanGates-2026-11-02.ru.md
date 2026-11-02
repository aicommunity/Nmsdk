# Завершённые ASan gates после восстановления связи

Это приёмка перечисленных проверок, а не полных этапов исходного плана.
Все четыре ранее запущенных владельца процессов отсутствовали при проверке;
задания завершились самостоятельно, повторных запусков не было. Источники,
build/runtime работающих заданий не менялись. Во всех четырёх stderr пуст.

| Контур | Результат | Численный источник |
|---|---|---|
| integrated163, попытка ASan-a2 | 163/163 | root07167d55125ced4eeff72703a718203e8c90bfc7 / Pulsefca7141178a854c5a2f579e4a195b3a3165340f9 |
| native trace recording | 18/18 | rootd467ef31af128bceabfeb5fd5bae237309b3a984 / Pulse225642bd9b3a5651fce2808bd0bef79944d4f1b8 |
| public preflight | 14 positive, 6 negative, 2 one-tick Train | тот же d467/Pulse225 |
| public diagnostic regression | 2 complete, 2 interrupted, 2 ordinary rejections | тот же d467/Pulse225; drivera8eaf77e4262c8807c6a7b86af4f8c6a14d3b778 |

Readers a8eaf77:12 preflight +7 diagnostic pipeline +5 trace recording =24/24;
отдельно8/8 integrated inventory/debt checks. Пропусков и ошибок нет.
Использованы реальные артефакты этих серверных запусков. Повреждение,
неполнота и подмена сертификата проверяются на копиях артефактов.

Основное доказательство: commit44548f908365f5030445e4ced11a71147d044331,
`Reports/StructTrain/TimeLearner/s03-s05-s07-completed-asan-a1`.
После Git fetch проверены outer hashes и каждый из2172 members;
primary.tar.gz занимает11207017 bytes. Внутри сохранены specifications,
runtime/source closures, owned receipts, JUnit, JSON/CSV, stdout/stderr,
результаты readers, inventory и сравнения. Сборки уже доступны в отдельных
proofs b9ce935628f758fbee8c7a546b0f169b3122ad93 и
41db2c7641c41a934dec401bf11df09ef8f1665b; бинарники повторно не добавлены.

Сохранены фактические mappings libasan.so.8.0.0 из1 integrated,1 recording,
8 diagnostic/source и20 preflight/Train процессов. SHA256 библиотеки:
8d5845bdf056b5db4cfb9fff40ad5eeea8f6da05a8ca6f5935a7d1c138ed2558.
Это проверка реальной загрузки ASan, а не вывод только из build flags.

## Временные данные и компактное хранение

Для integrated163 все407 CSV побайтно равны опубликованным normal данным,
все413 native probe packets семантически равны. Для нового recording18:
88 CSV равны побайтно,94 packets равны семантически, включая6 aliases.
Aliases не становятся независимыми измерениями. Прочие JSON не объявляются
одинаковыми: различаются55 integrated и11 recording control/model файлов;
имена различий сохранены в comparison.json. Отсутствующих файлов нет.

Таким образом, уже построенные normal temporal caches и просмотренные
selected originals применимы к тем же ASan сигналам. Отдельный ASan render
и повторный просмотр изображений не заявляются. Ссылки на visual QA:
Integrated163TemporalVisualQA.json и NativeTraceCoverageVisualQA.json.
Полные изображения остаются кэшем M40 Data.

Для public diagnostic сравнение отдельно подтверждено commit
286f7e1b4499db2bc4e9ad49e5980dbd219866bf:
`Reports/StructTrain/TimeLearner/s05-diagnostic-temporal-equivalence-asan-a1`.
Все10 inline waveform trial JSON равны normal семантически:4+4 complete,
1+1 interrupted. Четыре исходных Train CSV равны побайтно. Строгий selector
требует именно это множество; пустая первоначальная выборка CSV в native
не считалась успешным сравнением, поскольку waveform находится внутри JSON.
Это связывает данные с normal temporal proof4661b39647b204e3ca04ee613bb08bb6d7cadc88
и9 просмотренными original PNG из DiagnosticRecognitionVisualQA.json.

## Ограничения и следующий шаг

Integrated163 сохраняет6 untraced packets и5 declared observability gaps.
Они не исчезают из-за PASS или сравнения с normal. Новая запись18 не меняет
старые артефакты задним числом. Неполные окна остаются неполными.

Public diagnostic использует остановленный external_stop Train, null
certificate. Завершение окна Test не означает завершения обучения.
Это проверка безопасного диагностического пути, не успешная классификация.
Никакого нового научного результата или рекомендации ControllerVersion2 нет.

Закрыто ожидание этих четырёх заданий и адресная ASan проверка их данных.
Не закрыты полные этапы1–12, широкая compatibility/physics/mode матрица,
Quantized/BestEffort, PostTune/C-trim, migration, production scheduler и
независимые frozen эксперименты. Develop остаётся44334e272de8429f29775512a860584c60350899.
Приёмка feature и children-first --no-ff merges выполняются отдельно;
данный отчёт сам по себе merge-приёмкой не является.
