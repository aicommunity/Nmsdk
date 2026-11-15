# SingleImpulseMaximum: физический ASan38 на M40

Адресный physical SDK gate принят: native38, independent readers25 и
observer unit34 прошли без failures/errors/skips. Это проверка нового schema5
пути на реальных компонентах, не только fast observer executable.

## Точный снимок и область

Compiled Root `038a66413b7a41e75bf3826eda365db1c78c364b`, PulseLib
`217dc53c4b1cc010ad6938852a91ee6d2df09e3c` (Core6c520fb), Bin
`fc67a3b0958e8becdfbe1cd3f0e4e054d966d54f`, Rdk
`10e9d05aa658dd2203c89bc84ba9166595b50014`. RelWithDebInfo,
`-O1 -g1 -fsanitize=address -fno-omit-frame-pointer`, compiler parallel1.
Новый изолированный runtime на Data; source/build обновлены только после
свежей closure/release семи зависимых групп. Лимит4GiB/128tasks, ledger1
не изменён.68 file bindings шести прежних runtime совпали после выполнения.

Набор38 содержит26 прежних storage/prepared controls,7 новых recorder
controls и5 native cases. Проверены меньшие дополнительные экстремумы,
поздний более высокий пик, равные раздельные максимумы, плато, clipped/
incomplete/nonfinite и peak-before-onset; Classic/Branch ×2000/20000Гц,
A/B фактических waveform и восстановление после prepared/sample/final faults.
Новые положительные physical schema5 cases используют N2 и explicit
threshold100. Четыре complete и шесть отдельных rejected schema5 captures
сохранены. C++ проверяет все фактические stimulus/soma samples и raw argmax;
Python6 новых readers независимо проверяет primary и corruption controls.
Прежние19 readers также прошли.

Native38 занял1124.73s по JUnit. Unit34 занял0.005s, повторяет observer
cases и не является ещё34 независимыми физическими условиями.

## Данные, instrumentation и проверка

Evidence `b0864d9c3c5eb6e5bb25f514a6133e48a12894ec`.
[Bundle](../../../Reports/StructTrain/TimeLearner/s07-single-maximum-physical-asan-a1/bundle.json):
295 members,664828 compressed bytes, SHA256
`ce199506c6e5535acef2792f14ee4f660b6bcc07410b3ac46e14923d882a1b94`.
[Независимая сверка](SingleImpulseMaximumPhysicalASanVerification.json)
проверила весь archive,498 Root/265 Pulse source hashes, все38+34 original
JUnit IDs/status,25 reader outcomes, две actual process/runtime identities,
73/19 loaded-file records и8 generated flags/link files.

У обоих выполненных executable проверены actual libasan mappings; flags
подтверждают address instrumentation. `detect_leaks=0` запрошено, отдельного
live readback опции нет; проверка утечек не заявляется. Producer terminal
сохраняет константное `ASan_verified=false` из общего шаблона и отдельное
`ASan_requested=true`; это не результат проверки instrumentation. Этот
исторический producer не переписывается. Отдельные publication и independent
receipts подтверждают flags/mappings и дают scoped sanitizer acceptance.

Локально выполнялись только Git/archive/hash/JUnit metadata проверки. На
локальной машине не исполнялись модель, numerical reader или trace arithmetic.
Worker cgroup закрыта, lease освобождена после closure. Наличие успешного
процесса не превращается в научный PASS.

## Открытые пункты

Console этой ASan SDK только собрана. Normal stock Console replay принят
[отдельно](SingleMaximumConsoleReplay.ru.md); ASan Console replay не заявляется.
Новая [матрица N1/4/6](SingleImpulseMaximumDimensionMatrix.ru.md) добавлена
после compiled snapshot и требует самостоятельной приёмки. Schema5 остаётся
diagnostic_only и не допускается к CapturedReferences/TrainingCertificate.
Принадлежность пиков полной пачки, остальные physics/normalization modes,
convergence, научная оценка и полный план0–12 остаются незавершёнными.
