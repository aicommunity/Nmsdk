# Ограниченное завершение owned Windows Job

Подготовка исходников, runtime и выходы задания остаются неизменяемыми во время
исполнения. Windows backend применяет лимиты Job до resume главного процесса.

## Исходное наблюдение

A2 компиляция дала 89 compile и 2 executable link, main exit0; backend честно
отказал из-за PID15228 после завершения main. Его identity неизвестен. Evidence:
`2483362581205cffacd487888d6466730110f051`, отдельная origin-ветка
`codex/windows-composite-build-a2-refusal-20261108`.

A3 выполнил реальную повторную компиляцию одного файла в новый object, сохранив
source, cache, оригинальный object и четыре runtime. Наблюдатель привязался к
owned Job до toolchain через bootstrap barrier. Оставшийся **A3** PID15260:
`vctip.exe`, creation_filetime134386169850981313, SHA256
`41fe46f8a0b41f6dd94c68c85fba20a10aacb662a9ef04784a632e37f3692371`.
Шесть snapshot gaps сохранены; полный spawn history не заявляется. Это не
устанавливает identity старого A2 PID15228. Evidence:
`661c9d713bce154588f764c0be3ed16f69c4c043`, origin-ветка
`codex/windows-composite-diagnostic-a3-refusal-20261108`.
Обе попытки остаются negative; native tests/model runs0, admission=false.

## Новый opt-in контракт

`windows_process.execute(..., owned_job_drain_seconds=0)` сохраняет прежний
немедленный отказ, если manifest не содержит нового поля. Ненулевой grace
разрешён только при совпадении с
`manifest.build_flags.owned_job_drain_seconds`: значение включено в runtime
fingerprint и request. Bool, NaN/Inf, отрицательное значение, unsigned grace и
расхождение caller/manifest отвергаются до создания output/Job.

После main exit0 backend наблюдает **тот же** Job до меньшего из
`main-exit + grace` и исходного whole-attempt wall deadline. Main exit code и
whole-Job execution хранятся отдельно. Success допустим только при естественно
пустом Job. Cancel, nonzero main, wall deadline и оставшиеся процессы сохраняют
отказ; завершение ограничено своим Job. Исключений по имени executable нет.

Живые оставшиеся процессы проверяются pinned handles: PID, creation filetime,
image path/hash, membership и реальные modules. Потеря identity живого owned
процесса запрещает admission. Гонки естественного завершения фиксируются как
snapshot gaps; отсутствующие identities не восстанавливаются по позднему PID.
Глобальное перечисление процессов и настройки VS не используются.

`owned-job-drain-started.json` задаёт наблюдаемый вход в фазу и effective
deadline; `owned-job-drain.json` сохраняет natural/forced outcome, snapshots,
identities/gaps. Legacy request/result без opt-in не получают этих полей.

## Проверка до применения к сборкам

Новый actual Win32 suite проверяет default0, естественное завершение child,
persistent child, whole-wall cap, cancellation именно в drain, nonzero main,
signed0 и invalid/mismatched policy. Дополнительно запускается существующий
WindowsProcess suite как compatibility control. Локально только AST/static
review; все API tests выполняются на .14 из Git-pushed source.

После unit gates требуются две реальные компиляции одного файла с policy0 и
policy30, свежими output/PDB paths, before/after source/cache/object/4runtime
guards. No-op не заменяет этот контроль. Full build и native admission остаются
следующими отдельными gate; подготовленный source не означает их прохождения.
