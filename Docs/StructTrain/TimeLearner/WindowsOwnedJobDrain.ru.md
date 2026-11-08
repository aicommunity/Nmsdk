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

## Фактическая проверка 2026-11-08

Source `034b72ff703362500f07ccfbcf0e24408f144a60`: 415 Python blobs,
package fingerprint `4d166c7fd5d299b50ae649693def6dc0fc160e984eba17e582d388b0d07d7ae9`.
Новый immutable tools checkout отделён от SDK d433/Pulse f925; оба источника
явно записаны в receipts. Первоначальный запуск API-A1 выполнил **0** тестов:
validation.run_suite очистил environment paths, и две setUpClass были skipped.
Этот bootstrap отказ сохранён в `2e966e03848a184611df82882eb11990f952af51`.

Fresh API-A2 использует maintained validation.preflight с точным inventory,
затем стандартный unittest.TextTestRunner и три явно объявленных environment
bindings. Никакого override `_environment` или изменения validation API нет.
Результат: **26 выполнено, 0 skipped/errors/failures**. Для 23 actual Job requests
проверено закрытие в kernel; default0 refusal сохранён. Естественное завершение,
grace timeout, whole-wall timeout, cancel и nonzero различаются. NULL OpenProcess
проверен явно помеченной fault injection на реальном owned child: unknown-alive
ещё присутствующий процесс даёт provenance_missing, не success. Это не наблюдение
фактического OS access denial. Evidence `a7333a2f15416642be8b26787900b128d7dc09df`.

Реальные compile A/B сохранены в `683e32714837daa5e6e70ad6e1c690bf7f00335f`:
обе получили main exit0 и новые object files; оригинальный object, cache, SDK,
tools и четыре runtime не изменились. Signed0 control честно отказал по
descendants_remaining. Signed30 treatment также **отказал**: pinned vctip PID8836,
creation_filetime134386191573170570, SHA25641fe46... оставался живым все 30 секунд.
В drain захвачены 89 module files, identity gaps отсутствуют; отдельный observer
всей компиляции сохранил 6 fast-exit gaps, полный spawn history не заявляется.
После deadline закрыт только owned Job; свежий collector подтвердил kernel absence.

API gate подтверждает контракт backend, но 30s не устранил наблюдаемый отказ
реального toolchain. Windows full build/native admission остаются **не приняты**.
Увеличение deadline, глобальные настройки VS и исключения по executable не
применялись. Исходные отрицательные A2/A3 не переоценены.
