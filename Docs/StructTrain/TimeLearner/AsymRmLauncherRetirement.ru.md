Актуализация06.11: оставшиеся10 shell-драйверов также удалены отдельным принятым пакетом [AsymRmDriverRetirement](AsymRmDriverRetirement.ru.md). Упоминание ниже generic run_asymrm как остающегося на review относится к прежнему snapshot. Python-анализаторы и весь этап9 ещё открыты.

# Удаление исторических запускателей AsymRm

Отдельный подэтап9:17 shell entrypoints прежних pilot/finish/scale/sweep волн
удаляются из Bin без wrappers и копий. Общий этап9 остаётся открытым.
Обучение, физика, конфиги, сохранённые модели и исходные измерения не меняются.

## Исходники и назначение

Полный retrieval snapshot Bin — `14a88195a8a5538d3a2f5c0657981488e38829b7`.
Каталог: `Configs/SpikeSamples/StructTrain/SelectivityAsymRm/scripts`.
Каждый файл прочитан; script_migration.json хранит полный commit, last-change
commit, blob SHA1, content SHA256, размер и точную команду git show.
Этот снимок позволяет извлечь инструмент, но не доказывает, что каждый
исторический эксперимент запускался именно этой версией.

| Файлы | Историческая функция и причина удаления |
|---|---|
| finish_packC_gen_fast_amp.sh, finish_packC_gen_preinh_amp.sh, finish_packC_gen_tip_reset_amp.sh | Retry фиксированных Pack C gen: перенос TipR/Initial из других состояний, повторные амплитудные расписания, старые Done/sync gates, местами pruning и восстановление общих отчётов. |
| finish_pilot_amp.sh, finish_pilot_lref.sh | Доведение двух Pack A span25 pilots через общий mutable runner и legacy partial-train policy. |
| run_pilot_span100.sh, run_pilot_span50.sh, run_pilot_v4_gen.sh, run_pilot_v4_preinh.sh, run_pilot_v4_sequence.sh | Предопределённые Pack A cold/warm sequences, ожидание по grep/pgrep, seed существующих состояний и переход к scale gate. |
| run_scale_bc_span100.sh, run_scale_bc_span25.sh, run_scale_bc_span50.sh, run_gate_scale.sh, scale_asymrm.sh | Предопределённые Pack B/C waves и ветвление по прежнему Done, а не по независимому training certificate/validity. scale_asymrm вызывает удаляемый sweep, поэтому тоже входит в пакет. |
| sweep_asymrm_amp.sh, sweep_asymrm_timing.sh | Изменяют shared campaign XML/physics на месте, используют старый runner и допускают продолжение после ошибки; их нельзя механически объявлять новыми production job specs. |

## Ссылки и сохранность результатов

Tracked source scan исходного root develop, Bin и PulseLib по всем17 именам
проверяет исполняемые consumers отдельно от отчётов/inventory. Единственные
выявленные shell callers — внутри удаляемой цепочки sequence/gate/scale.
Root references относятся к JSON inventory snapshots; PulseLib references
не обнаружены. Это буквальный source scan, не утверждение об отсутствии
произвольных внешних скриптов или динамически составленных имён.

Восемь связанных отчётных документов Bin получают историческую оговорку и
immutable Git-ссылку. Их исходные измерения, ошибки и научные выводы сохранены;
старые команды теперь явно относятся к прежней кампании. Generic run_asymrm,
его helpers, analyzers и остающиеся shell tools требуют отдельного review;
они не считаются перенесёнными этим изменением. Для нового запуска используется
корневой пакет с явно подготовленным job spec, а не автоматическое возобновление
старых волн. Эквивалентность прежних mutating scripts новому runner не заявляется.

## Приёмка

Manifest содержит81 запись:79 retired и2 moved. До принятия требуются проверки
на обоих workers через production history verify-migration:

1. Все81 исходных commit/blob/size/SHA256 доступны и соответствуют записи.
2. Все старые пути отсутствуют в точной root/child closure; replacements
   прежних moved records доступны.
3. Отрицательный Git fixture с прежним Bin gitlink должен быть отклонён
   с migration_old_path_still_present и без положительного receipt.
4. Diff Bin ограничен17 удалёнными scripts и оговорками восьми документов;
   конфиги, модели, данные и аналитические helpers побайтово сохранены.
5. Работающие numerical sources/builds/runtimes не меняются. Для metadata
   проверки используются отдельные Git repositories и источник корневых scripts.

Серверная metadata-приёмка завершена на обоих workers. Elder proof
`aadbe4e4b50716f880daf3a4a2250bc87e3ae62c`, M40 proof
`9e190d18b370476b221e40f5e310573d69cbc3ac`; проверены outer hashes и все8 members
каждого архива (86 760/86 776 compressed bytes). Оба подтвердили81 records,
negative fixture `5a6e91174fb8c2ffbcbf1e48c41888d27733edbf` отклонён на первом
возвращённом AsymRm пути. Positive receipt для него не создавался. Полные
source_closure до/после совпали. Это не numerical/ASan-приёмка алгоритмов:
названия normal/asan обозначают workers, а проверялся Git metadata workflow.

Bin feature `07fbeb4357a7337a2fb924330846f8d4ec05ac4b` объединён --no-ff в
develop `39d811e5e0798eecf124f32356c9fc6edbe4538a` и опубликован до root.
Tree merge commit совпадает с проверенным feature tree
`5857a08c2ea1be67c5ade0504bb213e177466bb9`. Root gitlink обновлён на этот merge.
Численные источники текущих owner/transport jobs остаются на своих прежних SHA.
