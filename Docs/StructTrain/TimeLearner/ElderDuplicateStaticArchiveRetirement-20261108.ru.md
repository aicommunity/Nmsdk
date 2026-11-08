# Удаление дубликатов link caches Elder

08.11.2026. Удалены ровно89 дублирующих статических `.a` из14 явно выбранных
закрытых runtime-каталогов. Каждый удалённый файл имел сохраняемую побайтно
идентичную копию. Production `static_archive_cleanup.apply_plan` из Root6dac
не изменялся; план `923bd5a49e0bbf6893d9fad350a2380dc104f26ebe366bad05dae298c0571406`
проверен до выполнения.

[Независимая квитанция](ElderDuplicateStaticRetirementA4Verification.json)
подтверждает89 удалений,419 неизменных остальных regular files,29 сохранённых
glog symlinks и все keeper hashes. ELF, INI, логи, модели, primary data,
source и общий build cache сохранены. Для symlinks проверены lstat identity
и link text без следования ссылкам.

Использованы whole-root write reservation, heartbeat, fsynced journal180
событий и92 свежие проверки. Перед удалениями проверялись81 известная группа
ядра ОС и192 прежних owner identity; legacy ownership не выдаётся за kernel
containment. Ограниченная видимость двух заранее исследованных OS helpers
явно сохранена в отчёте. Собственная maintenance group закрыта, lease released.

Объём удалённых файлов:765663074 логических и765812736 выделенных байт.
Фактический `df` изменился с1136148480 до1897406464 свободных байт;
дельта761257984 отличается из-за других записей на файловую систему.
После публикации наблюдалось1888792576 свободных байт: запас над следующим
порогом1792MiB — всего9744384 байт. Новые source donors требуют отдельного
fresh preflight; готовность следующей Elder-сборки этим не доказана.

Evidence `242607634228fd36d17b8f3b5ad2266a0df7fa98` включён merge commit
в integration branch. [Сжатый primary](../../../Reports/StructTrain/TimeLearner/s02-duplicate-static-retirement-elder-a4/primary.tar.xz)
содержит64 проверенных файла, включая original worker/client, approved plan,
before/after snapshots, журнал, closure/lease records и retirement ledger.
Ledger SHA `085f945e74ccb7286f9949bd8abff508d6049c855a09d421db5c7b04d469f24e`;
future baselines SHA `bd7f2bd18d4cf6f65a0bd1ad55a920b2df918b94f8d005b772dd31a2278459c4`.
Старые полные runtime manifests сохраняются историческими preimages; новые
проверки должны учитывать89 удалённых AR через ledger.

Предыдущая A3 завершилась до первого unlink: wrapper inventory ошибочно
требовал regular file для уже известных non-target glog aliases. Удалений0;
[отрицательная квитанция](ElderDuplicateStaticRetirementA3NegativeVerification.json)
и evidence `71e57051728c6f83f88da8dbca484fb99eff574a` сохранены отдельно.
A4 исправила только wrapper inventory для29 ссылок, сохранив AR guards.

В A4 клиентский launcher после `Popen` завершился с TypeError в выводе hash.
Worker уже выполнялся; повторный запуск не производился. Его успешный итог
установлен по фактическому состоянию ОС, журналу и файлам. Client failure и
явно обозначенная реконструкция submission сохранены в primary; они не
подменены утверждением об успешном клиентском запуске.

Независимый verifier при повторном запуске сначала отказал из-за уже
существовавших derived ledger files. Исправлен только этот локальный вывод:
существующие файлы сравниваются побайтно с primary и не перезаписываются;
при несовпадении отказ сохраняется. Повторная проверка завершилась exit0,
receipt и derived file hashes неизменны. Это не приёмка общего production
launcher; переход к maintained launcher/declarative spec остаётся задачей9/10.

Следующая отдельная операция `s02-extra13-static-retirement-elder-a1` выполнена через maintained `owned_python_job` Root `edaaa836e27b0ecef1c2f9203fb04ee82d62bd93`. Удалены ровно13 дополнительных подтверждённых дубликатов в двух явно перечисленных старых runtimes:121819188 logical bytes,121843712 allocated bytes. Общий итог двух успешных операций —102 AR-файла. Никакие ELF, INI, модели, primary data, логи, source или общий build-cache этой операцией не удалялись.

Evidence `f1f2aa133385fd930828d671316c56e76724e1c9`, [проверка операции](ElderExtra13StaticRetirementA1Verification.json), [проверка owned launcher](ElderExtra13StaticRetirementA1GeneralVerification.json). Проверены exact plan/review SHA,13 keepers,102→89 retained regular files,5 сохранённых aliases,16 fresh guards,28 fsynced journal events, закрытие всей собственной группы и освобождение lease. Каждый guard сохраняет84 известных kernel closures и207 legacy records с прежним ограничением видимости двух OS helpers. Наличие legacy identity не объявляется kernel proof.

Фактическое свободное место1814167552→1934655488 bytes; delta120487936 не приравнивается сумме allocated removed bytes из-за параллельных расходов файловой системы. Это около1,93GB после удаления, не гарантия места для полной сборки. Перед следующим C++ job обязателен свежий preflight.

После удаления будущие проверки шести затронутых target/keeper runtimes используют actual postimage из primary, а не прежний whole-runtime equality. Derived future-baseline SHA `a883d175f774b1c2f24366e1107cbf61df5386608cb3c2199277cd91b047fc2a`; остальные прежние baselines сохраняются. В raw stderr оставлены два предупреждения Git о запрещённом lazy fetch; fetch не включался, исходники и кэш SDK не обновлялись. Журнал, исходные plan/review и снимки доступны в compact primary этой операции.
