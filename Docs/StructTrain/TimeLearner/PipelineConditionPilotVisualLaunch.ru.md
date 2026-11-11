# Временные отчёты реального ConditionSpec pilot: подготовка06.11

Статус: выполняется на M40; visual acceptance пока не объявлена.
Первичные данные — неизменяемый Git commit
`bd10072c73d7c8296f1a4d02c051459f29f8c039`,990 archive members,
SHA256 `574eecd5ae76a62b954422c9daeacadda2be9cda4f9184288e08240906774702`.
Планируются все Train probes, все calibration candidates/confirmation и все
frozen patterns Classic-v1/Branch-v2, все soma channels с actual input overlays.
Полный PNG/SVG/PDF cache остаётся на M40 Data; в Git будут первичные данные,
метрики/manifests и выбранные оригиналы после проверки масштаба.

A1 `s11-pipeline-condition-pilot-visual-a1` отказала до первого графика:
worker_event_log_owner_mismatch. Исторический producer при упаковке следовал
служебным glog symlinks, поэтому копия alias выглядела как лишний regular file.
Это подтверждено по реальному PID3801349, именованному INFO log и его побайтно
идентичному NeuroModeler.INFO. Строгий native auditor не ослаблялся.
Оригинальные A1 output/container/stdout/stderr сохраняются для общей публикации.

[Новый production restoration adapter](PortablePrimaryRestoration.ru.md)
прошёл M40 14/14 regression tests. Full actual restoreA2 проверила990 members,
оставила982 regular files и явно перечислила8 избыточных aliases. Source archive,
signed manifests, модели и исходные trace bytes не изменены. Это отдельная
проверка packaging, не повторное обучение и не новый scientific result.

A2 renderer/tool root `2e0f378c97884eceaeb2b3fb864944e250f7347a`, code pack3906120
bytes SHA256 `642add55e4c550ecde66d8958a6cbdaa0fae4ee662ddb9c8a961192a9505664b`.
Данные доставлены отдельно Git pack8434931 bytes SHA256
`29385dc0921978695d90d434d31dbd2bfee6a46ccff5ede0fe6822d4cf63d737`;
sparse checkout явно включает только выбранный Reports prefix вместе с кодом.
Общая строка transport helper omitted_paths не описывает это явное исключение.

Output `/media/user/Data/TimeLearnerRefactor/readbacks/s11-pipeline-condition-pilot-visual-a2`.
Wrapper PID802454/start302213805; worker PID802473/start302213816.
При последней проверке worker R и1054 PNG уже существовали; это промежуточное
наблюдение, не доказательство полного покрытия или визуальной приёмки.
Используются штатные report CLI pipeline-run/calibration-run и прежний plot-venv.
Parent ограничен2GiB/64tasks; preflight требует>20GiB на Data и>4GiB availableRAM.
Общий M40 path ledger не имеет quantitative capacity; его политика не менялась.

До приёмки: завершить все6 phase reports, сверить модели/primary, полное покрытие
всех recorded trials/somas, temporal zoom>=8px/tick без downsampling, размеры
1920×960 и подписи actual inputs; выполнить visual QA выбранных оригиналов,
проверить fresh process closure/released lease и опубликовать компактную Git closure.
Результаты остаются N2 LT same-matrix engineering controls, не stock8-pattern
и не independent evaluation. Полный исходный план остаётся открытым.
