# PLAN 2026-10-25 — пределы дендритной схемы (одноканальный вариант)

Статус: **в работе** на ветке `plan/2026-10-25-dendrite-limits` (от `timelearner_audit3`). Дополнение Тима 2026-10-24 (dual-host / диск / offload) — §H ниже.
Ссылки: PulseLib `2e5308e` (F4), Bin `b7706a07` (§0 F1–F3); контроль W0 = `br25_nextseg`.

## H. Хосты, диск, offload (дополнение Тима)

### H1. Dual-host

| Host | Адрес | Корень | Прогоны | Лимит Console | GPU |
| --- | --- | --- | --- | --- | --- |
| Elder-1 | `.11` (локально) | `/home/user/Nmsdk` | `/home/user/TLAgent-20261020/runs` | ≤8 | n/a |
| M40 | **`10.245.1.17`** (не `192.168.1.17`) | `~/tl-agent/Nmsdk` | `$DATA/runs` после `source ~/tl-agent/env.sh` | ≤12 | **CPU only** (driver mismatch; **не перезагружать** M40) |

Перед волнами на M40: синхронизировать `~/tl-agent/Nmsdk` с активной веткой плана (`git stash -u` локальных правок — **не терять**), `git submodule update --init`, собрать Console/PulseLib, пройти положительный контроль `br25_nextseg`. Волны распределять между `.11` и `.17`.

### H2. Диск во время волн

На **обеих** машинах перед каждой волной и в мониторинге: следить за Avail на корне прогонов. Порог — **предупреждение + перенос** завершённых учтённых артефактов, **не** kill активных Console/`posttune_verify`. Активные прогоны не останавливать из‑за диска; освобождать место offload’ом фоном.

### H3. Offload на `/media/user/Data` (M40)

- Цель журналов: `/media/user/Data/TLAgent-offload/journals/<host>/<date>/` — **только** текстовые журналы NMSDK/Console (`*.log`, `*Audit.log`, `TimeLearnerTrainingAudit.log`, launch `*posttune*.out` / `*console*.out`). Модели, конфиги, `results.csv`, StatisticLog и чужие файлы **не трогать**.
- Упаковка: `tar | zstd` по каталогу прогона; проверка `zstd -t` + сверка списка файлов; удаление исходных журналов **только** после OK. Активные прогоны / текущие волны — skip. `nice`/`ionice`. Скрипт: [`../evidence/tools/archive_nmsdk_journals.sh`](../evidence/tools/archive_nmsdk_journals.sh).
- Реестр: [`../evidence/RUN_REGISTRY`](../evidence/RUN_REGISTRY/) (строки `jarch_*`).
- **Стоп archive/offload:** если на `/media/user/Data` свободно **&lt; 5%**, записать в [`CAMPAIGN_STATUS_LATEST.md`](../evidence/CAMPAIGN_STATUS_LATEST.md) и остановиться. (Порог снижен с 15%→5% 2026-10-24; при free≈11% перенос журналов **разрешён**.)

## 0. Что исправить ДО любых новых прогонов (блокеры валидности)

| # | Дефект | Где | Исправление | Проверка |
|---|---|---|---|---|
| F1 | InhGrid подменил нейрон: NEURON=NSPNeuronGenSymInhC1e9 (DissociationTC 5 мс, InhRm=1e7) вместо HIST NSPNeuronGenAsymRmD001C1e9 (1 мс, InhRm=1e8) | clone_inh_grid.py (NEURON=...), NPulseLibrary.cpp:1132-1148 | Базовый класс = класс HIST-эксперимента (AsymRmD001C1e9; для preinh: NSPNeuronGenPreinh2_5AsymRmD001C1e9). SymInh — только как отдельный фактор | provenance: класс + Dissociation/Secretion/RestingResistance из сохранённой Train Model |
| F2 | PSI не включается: патч только в Model_00.xml; Parameters_00.xml держит PSI=0; BuildStructure пересоздаёт нейрон из класса, где мембрана NPMembraneBio (без PSI) | clone_inh_grid.py `_patch_model_psi`; NNeuronTimeLearner.cpp BuildStructure (удаление/AddMissingComponent) | PSI задавать ТОЛЬКО классом нейрона (NSPNeuronGenPreinh{2_5,3_0,4_0}…, MembraneClassName=NPMembraneBioPreinh*) | assert после загрузки: UsePresynapticInhibition/InhibitionCoeff на ExcSynapse1 каждого кончика печатаются в аудит |
| F3 | N0: NumSynapse упирается в kMaxSynapsesPerDend=128 (все c25 N0: [128,128,128,x]); в Test NumSynapse=1 1 1 1 не переносится → мёртвый Test | NNeuronTimeLearner.h:587, ChangeSynapseNumber (~4168-4230); phase9_preinh_bc_gate.py overlay_train_params (43-121) не копирует NumSynapse | (а) overlay копирует NumSynapse, NormalizationMode и все поля топологии; (б) Ns==kMax → статус not_converged/saturated, а не converged_posttune_finalized | Test-assert: L, Ns, TipR, R каждого синапса кончика == финал Train |
| F4 | «Resistance bounds could not be derived» | UpdateResistanceBoundsFromMembranes (292-465), вызов из BuildStructure (~3196) при дефолтах ADefault: NumInputDendrite=1, NormalizationMode=parametric, StructureBuildMode=1 → target_count=0 | при target_count==0 вернуть true без ERROR (или пропуск при загрузке) | лог без ERROR на старте; поведение не меняется |
| F5 | Train/Test ×2 (N1) — причина не доказана | см. §A4 | Replay-тест (ниже R0) | расхождение ltz Train-replay vs Test ≤5% |

## 1. Q1 — масштабирование на S50/S100/S480

Гипотеза H-sim (точное подобие): если умножить на k=S/25 ВСЕ временные константы (Cm всех мембран → τm, SecretionTC, DissociationTC, длительность импульса генератора, EstDelayPerSeg, SyncTolerance, IterationGap, пауза между паттернами, окно Test test_t, MaxCalculationModelTime), не меняя сопротивлений и порогов, то система ОДУ — та же во времени t/k, и br25_nextseg должен воспроизвестись с теми же L и TipR. dt=50 мкс остаётся ≪ τs.
Почему прежние S50/S100 не воспроизводились: τm=10 мс, τs=1 мс, задержка на сегмент — фиксированы (класс C1e9 на всех S; EstDelayPerSeg=0.002) → L должно расти ∝S → затухание по кабелю → TipR в Rmax (S100 N1: 1e10), not_converged; SegEI на S100 блокирует рост L (L=1 1 1 1).

Классы (новые имена, правка NPulseLibrary — решение Тима): Cm=1e-9·k, SecretionTC=DissociationTC=1e-3·k, Rm как AsymRm (1e7/1e8), Rsyn 8.6e7/8.6e8; варианты с NPMembraneBioPreinh2_5.
k: S50→2, S100→4, S480→19.2.

Серия Q1 (Branch, NextSegInh, N1; плюс N0 после F3):
| Волна | Состав | Прогонов | Оценка |
|---|---|---|---|
| W0 | позитивный контроль br25_nextseg (HIST-конфиг как есть) ×3 seeds/повтора + replay R0 | 4 | ~3 ч (параллельно) |
| W1 | S50 sim (k=2) ×3; S50 naive (C1e9) ×1; контроль W0 ×1 | 5 | ~4-6 ч |
| W2 | S100 sim (k=4) ×3; контроль ×1 | 4 | ~6-10 ч |
| W3 | только если W1,W2 прошли: S480 sim ×2; контроль ×1 | 3 | >24 ч (оценка) |
| W4 | частичное подобие на S100: масштабировать только Cm / только τs / только delay | 3 | ~6-10 ч |
Итого 19 прогонов; времена — оценка по c25 (~2.8 ч на прогон, 16 параллельно) и c100, не проверено для S50/S480.

Общие настройки всех волн: Done_exact и Done_BE фиксируются раздельно; EstDelayPerSeg=τseg (масштабированный); tol×1 (SyncTolerance = S/24000·…, как в HIST, без расширения); amp_eps относительный (1e-3·целевой амплитуды); ResetBeforeTrainBurst=1; Test: test_t∝S.
Критерии успеха волны: (1) контроль W0 PASS детекции в этой же волне (иначе волна недействительна); (2) детекция целевого паттерна: target fires, sep_margin = (min_target − max_foil)/min_target ≥ 0.10 на аудите; (3) L(S)/L(25) в пределах ±20% (для sim); (4) TipR < 0.5·Rmax.
Правила решения: sim PASS на S50 и S100 → длина паттерна не предел, предел задаётся τ/S; sim FAIL при PASS контроля → искать нескалированную константу (W4 + список выше); контроль FAIL → сначала устойчивость br25 (известно E1.5 0/9), серию не интерпретировать.

## 2. Q2 — почему не работает пре+пост сегментное торможение

Факты: (1) PSI в InhGrid фактически выключен (F2) → «preinh ≡ gen» бит-в-бит — артефакт, не физика; (2) PSI в коде — самогейт синапса g=C(1−k·p)p с нормировкой пика C=4k/R (NPulseSynapse.h:138-156), т.е. укорочение EPSC, а не торможение от тормозного входа; (3) NextSeg/SegEI вешают тормозной синапс на тот же входной канал на сегмент tip+1 / tip+8 (дистальнее возбуждения) и добавляют пассивные «головные» сегменты (кабель L+1 / L+8), т.е. меняют и нагрузку кончика; (4) SegEI в N1 = gen (эффект через 8 сегментов ничтожен), в N0 «оживление» Test — побочный эффект (F3), а не торможение.

C1. Console доза-ответ (ручная структура, IsNeedToTrain=0, L=13 11 7 1, TipR br25, AsymRm C1e9):
- PSI: классы k∈{0, 2.5, 3.0, 4.0} (готовые NSPNeuronGenPreinh*), 8 паттернов → пик сомы, FWHM ВПСП, ltz max, sep_margin, m(Δ). 4 прогона.
- Post (NextSeg): вес тормоза w=TipR/R_inh ∈ {0, 0.25, 0.5, 1, 2, 4} (нужна настройка R_inh отдельно от TipR — сейчас R_inh=TipR жёстко; правка или ручной XML). 6 прогонов.
- SegEI: d∈{1,2,4,8} × α∈{0.5,1,2} → 12 прогонов. Контроль: тот же d с Input тормоза отключён (только головные сегменты) — отделить эффект нагрузки кабеля. +4.
- Комбинация PSI k=2.5 + лучшая точка post. 2 прогона.
Итого ~28 коротких Console-прогонов (минуты каждый).
Критерий: торможение «работает», если при равной амплитуде цели FWHM↓ ≥20% и sep_margin растёт ≥0.05 абсолютных.

C2. Тренер (только после F1-F3 и если C1 дал эффект): Branch S25 N1: {gen, PSI k*, post w*, PSI+post} × 3 повтора + абляции (PSI класс с k=0; тормоз без входа) + контроль br25_nextseg. ≈16 прогонов, ~3 ч волна.

## 3. Порядок
F1-F5 (код/скрипты, решение Тима) → W0+R0 → C1 → W1/W2 → C2 → W3/W4 → решение о потолке. F1b — после завершения дендритов.

## 4. Синтетический датасет (только дизайн, см. отчёт §E)
- 4 спайка/паттерн, совместимо с 32 строками матрицы / maxSpikes 4; цель T(S) = {0, 1, 4, 6}·S/6 (линейка Голомба) и текущая {0, 4.15, 12.5, 25}·S/25 как контроль.
- Фойлы на каждую цель: 5 перестановок ISI; сдвиг одного внутреннего спайка на Δ ∈ {S/24, S/12, S/8, S/4} (без Δ, кратных шагу сетки S/6); изменение плотности (3 и 5 спайков); 4 пуассоновских паттерна с той же длиной.
- Пауза между паттернами ≥ 3τm + max D_i (+ ResetBeforeBurst).
- Оценка: sep_margin на тесте; обязательная детекция (цель выше порога, все фойлы с Δ ≥ Δ* ниже); кривая m(Δ).
- Линейный оракул (/tmp/oracle.py на box): при τm/S=0.4 (C1e9, S25) линейные отступы отрицательны; при τm/S ≤ 0.1 и τs/S ≤ 0.04 m_perm ≈ +0.17…+0.24, m(S/12) ≈ +0.07…+0.21.
