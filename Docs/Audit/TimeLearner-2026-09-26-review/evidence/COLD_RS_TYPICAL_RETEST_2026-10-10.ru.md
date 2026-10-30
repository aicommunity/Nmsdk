# Повторная проверка обучения после восстановления cold-start Rs

Дата: 2026-10-10
Цель: проверить типовые Classic и Branch конфигурации после удаления начальной установки `Rs = Rm × InitialRatio` и выяснить, доходит ли C++-обучение до терминального исхода.

## Краткий результат

Предыдущие проверки не давали полного ответа по обоим тренерам: Branch `br50_gen` останавливали после внутреннего EOL синхронизации, до завершения PostTune. В настоящем повторе оба запуска дошли до содержательного исхода:

| Конфигурация | Исход обучения | Отдельный результат качества |
|---|---|---|
| Classic `phase6_480` | C++ отказ `kFailureResistanceMax` (`failure_reason=1`), `Need=1` | Sync EOL достигнут, Amp EOL не достигнут |
| Branch `br50_gen` | PostTune завершён, `Need=0` после flush C++ flag | `NonSeparable`; gate сообщил `fires_missing` (`rc=1`) |

Эти исходы нельзя объединять в одну категорию «обучение не сошлось»: Classic завершился явным отказом по пределу Rs; Branch завершил тренировочную фазу штатно, но не получил разделяющее качество и не детектировал цель.

## Фиксация запуска

- Root на момент запуска: `339f01aab18197926c24cd6e29ca726cfb9e9018`.
- PulseLib: `2bb72a3b6b28812c7b00382929f7461bc9faff30`.
- Bin gitlink на момент запуска: `c64984436db93ce6a4b6cc4672eeee5942046949`.
- Console: `NeuroModelerConsole-4a5b36b-normal.exe`, SHA-256 `1afd07727183837bc5d6a4bc313e632ccb5a0d7dfabd88bd95b715d5259b72e8`.
- Оба запуска создали отдельные чистые workdir из allowlist входных файлов; обучение было в C++ Console. `w3_length_escape=0` в cold-reset/iteration audit.
- Перед запуском подтверждены исходные configured TipR `86,000,000 Ω` на каждом сегменте. C++ reset audit зафиксировал то же начальное значение, длины `[1,1,1,1]`, `NormalizationMode=1`, runtime `Rmin=10,000 Ω`, `Rmax=10,000,000,000 Ω`.
- Harness запускал Console с `-x -S`, `--max-polls 1200`, `--snap-every 10`; `--stall-autosave-n 0` отключал только экспериментальный ранний stop по неизменным `L`/TipR на Rmax. Автоматическое отслеживание C++ training failure и обычный лимит StatisticLog оставались включены.
- На Windows первый запуск runner остановился до старта Console: POSIX-only `os.statvfs` и отсутствующие в каталоге собранного exe Qt/Boost DLL. Для запуска исправлена только проверка места на диске (`shutil.disk_usage` по тому checkout); runtime DLL взяты из установленной поставки NeuroModeler через `PATH`. Эти два preflight-сбоя не являются результатами обучения. Алгоритм и C++ исходники не менялись.

## Classic `phase6_480`

Run ID: `phase6_480_20261010T032452Z_24952_b8877045`

Workdir: `Bin/Configs/SpikeSamples/StructTrain/_repro/runs/phase6_480_20261010T032452Z_24952_c708ab15_work`

Run bundle: `Bin/Configs/SpikeSamples/StructTrain/_repro/runs/phase6_480_20261010T032452Z_24952_b8877045`

Исходный C++ cold reset подтвердил `TipR=[86M,86M,86M,86M] Ω`, `L=[1,1,1,1]`, `w3_length_escape=0`. Console работал около 13 минут до отказа; `-t=900` модельных секунд исчерпан не был.

Итоговая audit-запись: итерация 35, `phase=4`, `failure_reason=1`, `Need=1`, `eol_sync=1`, `eol_amp=0`; все пики валидны. Длины `[51,41,25,1]`, TipR `[95.7M,10G,49.5M,86M] Ω`. Второй Rs достиг именно runtime `Rmax=10 GΩ`, после чего C++ остановил обучение. Амплитудные остатки в момент отказа были `[-0.06204,-0.02224,0.00000471,0]`; поэтому это отказ до выполнения amplitude EOL, а не успешное обучение и не последующий quality-gate failure.

Итог runner: `train_status=cpp_training_failure_1`, `training_convergence=cpp_training_refusal`; quality gate не запускался. Это подтверждает, что восстановление прежнего начального Rs само по себе не устраняет этот Classic D-отказ.

## Branch `br50_gen`

Run ID: `br50_gen_20261010T032452Z_31752_252d2915`

Workdir: `Bin/Configs/SpikeSamples/StructTrain/_repro/runs/br50_gen_20261010T032452Z_31752_b0060698_work`

Run bundle: `Bin/Configs/SpikeSamples/StructTrain/_repro/runs/br50_gen_20261010T032452Z_31752_252d2915`

Полный запуск занял около 91.5 минуты на данной Windows машине (`-t=320` модельных секунд). В итерации 36 C++ достиг внутреннего EOL: `eol_sync=1`, `eol_amp=1`, все четыре `pulse_synced=1`, `failure_reason=0`; длины `[15,12,6,1]`. После этого Branch вошёл в штатную PostTune фазу. Она установила канонические TipR `[20M,20M,20M,86M] Ω` и продолжила свободный прогон по 8 pattern-пробам; это нормальный переход после sync EOL, а не повторная cold-start инициализация.

PostTune выставил `PostTuneResult=2` (`NonSeparable`), `landscape_ok=0`, `mid=1`, `gap=-3.77434e-05`. C++ создал `posttune_complete.flag`; runner дождался сохранения, применил значения из этого текущего flag, и итоговый `IsNeedToTrain=0`. Итого тренировочная фаза завершена штатно, но качество разделения не прошло.

Отдельный phase8 target-detection gate запущен после терминального завершения обучения, вернул `rc=1` и `fires_missing`; runner классифицировал его как `detection_quality=quality_gate_failed`. Это quality/detection failure, не отказ тренера. PostTune-метрики target/foil: `[0.0497069,0.04872,0.0497446,0.0494495,0.0495735,0.048208,0.0493166,0.0468227]`, согласующиеся с `NonSeparable`.

## Вывод

1. Возврат к прежней cold-start инициализации Rs не гарантирует сходимость: проверенный Classic D-кейс по-прежнему заканчивается явным отказом на `Rmax`.
2. Branch на `br50_gen` доходит до sync/amp EOL и завершает C++ PostTune, но результат остаётся `NonSeparable`, а target-detection gate не обнаруживает цель. Это нужно записывать как завершённое обучение с недостаточным качеством, а не как незавершённое обучение.
3. Для Branch переход к TipR `20M` после внутреннего EOL предусмотрен `EnterPostTunePhase()` и выбранным canonical PostTune режимом; эти значения нельзя принимать за начальное Rs обучения.
4. Эти два прогона отвечают на вопрос о терминальном поведении двух типовых конфигураций; они не доказывают универсальную невозможность решений и не заменяют контрольные positive cases или повтор full49.
5. Исходные workdir/run bundle сохранены локально под указанными путями. В git добавлен этот компактный отчёт и отдельно фиксируется только portability-поправка runner; крупные временные каталоги/StatisticLog в git не добавляются.
