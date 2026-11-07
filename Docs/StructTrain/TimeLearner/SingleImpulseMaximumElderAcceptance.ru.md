# SingleImpulseMaximum: native38/readers25 на Elder

Адресная normal-проверка schema5 принята: все38 C++ tests и25 readers прошли
без failures/errors/skips. Отдельно прошёл unit target34; он использует те же
observer test bodies и не добавляет34 независимые физические проверки.
Остальная матрица, Console replay и whole-burst assignment этим не закрываются.

## Проверенный снимок и поведение

Root `62997ad1e7cb7869012d11da82b5a48b529ac1e7`, PulseLib
`24f9767ace1f498d5dc048a70fc303789adac757` (Core6c520fb), Bin
`fc67a3b0958e8becdfbe1cd3f0e4e054d966d54f`, Rdk
`10e9d05aa658dd2203c89bc84ba9166595b50014`. Release, compiler parallel1,
изолированный `runtime-single-impulse-maximum-elder-normal-a2`.

Набор38 состоит из26 прежних storage/prepared cases, семи новых recorder
controls и пяти native cases. Проверены:

- уникальный самый высокий пик после глубокого спада и меньших экстремумов;
- равные раздельные максимумы, плато, clipped/incomplete окно, максимум до onset;
- прежний отказ schema4 при нескольких пиках и запрет неверной schema/policy;
- Classic/Branch ×2000/20000Гц на настоящих компонентах;
- восстановление native burst после prepared/sample/final-sample fault для обеих топологий;
- запрет использования schema5 как training references/certificate.

Положительные native A/B используют N=2 и явный порог100. Это инженерный
контроль наблюдения, не проверка stock multi-peak динамики при0.0117 и не
смена default. Во всех четырёх A/B парах независимо проверены5284 raw frames:
stimulus и все soma ordinates побитно совпали; относительные clocks совпали
с допуском1e-12, соответствующим проверке roundoff в C++ fixture. Base/effective
model revisions пар совпали. Изменение политики измерения не меняло физику.

Сохранены четыре complete schema5 observations и шесть отдельных fault captures.
Новые6 readers проверяют actual argmax, подмену измеренной амплитуды, schema
relabel, запрет training reader, partial diagnostics и попытку выдать максимум
до фактического входа за валидную реакцию. Прежние19 readers также прошли.
Нативный набор38 занял172.407s по JUnit. Unit34 округлён JUnit до0ms;
это не означает отсутствия исполнения и не служит физическим benchmark.

До смены неактивного source/build свежо проверены closure/release девяти прежних
групп.102 file bindings трёх прежних runtime совпали после build/run. Lease
освобождена только после whole-group closure. Ledger schema2/capacity/slots
не менялись; максимумы worker6GiB/128tasks, один compiler job.

## Неудачная A1 сохранена

Предшествующий Root `0e729b80a63ea0524b8561bb8d3e4756c5c807e5` / Pulse6c520fb
завершил38 tests:37 passed, одна fault-группа failed. Все12 failure messages
относятся к `file.open(...NewOnly)`: три fault subcases повторяли имена файлов
внутри одного gtest. Исправлены artifact suffix и разделение четырёх complete
observations от шести fault captures в reader. Алгоритм не менялся ради PASS.

A1 не переименована в успех, readers после её native failure не выполнялись.
Её evidence `240d2179aa513117ca55009d8a4e4aadda3e6c90` содержит247 members,
647372 compressed bytes, SHA256
`580e093d0e10b6d31f571737f9f06bbac5a88a79395c092ac8ff7a7b125f8862`.
[Независимая сверка A1](SingleImpulseMaximumElderA1Verification.json) проверила
38 IDs, единственный failed test, все12 сообщений и495 root/265 Pulse hashes.
89 прежних runtime bindings дополнительно считаны после closure; это отдельная
collector-запись, не подстановка отсутствовавшего producer after-record.

## Первичные данные A2 и границы

Evidence `a822275717754818668124c39cc02777104ecded`.
[Bundle](../../../Reports/StructTrain/TimeLearner/s07-single-impulse-maximum-elder-normal-a2/bundle.json):
295 members,651312 compressed bytes, SHA256
`899f88231ca306306b0010f3906aabf7edc40c4dea26668df8308bb6ae24b811`.
[Независимая сверка A2](SingleImpulseMaximumElderA2Verification.json) проверила
все members,496 root/265 Pulse hashes,38+34 JUnit IDs и25 reader outcomes,
оба owned-process/runtime bindings,26/16 actual loaded-file records и восемь
generated flags/link command files. Локально — только Git/archive/hash/JUnit
metadata, без numerical execution.

Это normal SDK, не ASan physical integration. [M40 unit ASan34](ProbeAlgorithmsASan.ru.md)
подтверждает observer отдельно. Нужны ASan нового native schema5 пути, Console
admission/replay архивных многопиковых моделей, их временные графики и проверка
всей исходной матрицы. Одиночный source impulse выбранного физического входа
не заменяет закреплённый pulse i штатной пачки. CapturedPerInput и прежние
training certificates не переоцениваются. Новый научный результат классификации
этими gates не получен; общий план остаётся незавершённым.
