# Следующий физический контроль: native PSI k=2.5 — 16.11.2026

В Stock moderate A1 полные пробы L56/42/35 не устранили неоднозначность input1.
Следующий объявленный вопрос — может ли существующее пресинаптическое торможение
изменить форму отклика и ход обучения. Новый механизм физики и ещё одна
перестановка L не вводятся. Улучшение или сходимость не предполагаются заранее.

## Постановка до исполнения

Два холодных условия создаются из принятого moderate Stock job:

|Условие|Штатный storage-образ|
|---|---|
|stock|NSPNeuronGen|
|psi|NSPNeuronGenPreinh2_5|

Оба образа зарегистрированы цепочкой CreateClassSamples. Runtime prototypes и
живые экземпляры не исправляются параметрическими overlays. Внешний профиль0
не импортируется ни в одном условии. Поэтому для новой пары требуется свежий
stock Train; эквивалентность прежнему TLNativeFast0 не подставляется вместо опыта.
Повтор детерминированного stock не считается независимым случайным обучением.

Branch N4/N1, 2000Гц, C1nF, DissociationTC.005с, начальные L1/Ns1/Rs86МОм,
target ISI .01/.08/.16/.24с, anchor3, полная пачка1.8с и threshold100 сохраняются.
CapturedPerInput references измеряются заново в каждом условии; общей амплитудной
цели нет. C-trim/PostTune/calibration Off. Bounds, допуски и все model/wall/probe/
edit/recovery budgets наследуются без изменения. Различаются run_id и имя образа.

## Входная проверка и ограничения

Пакет Scripts/StructTrain/TimeLearner/presynaptic_storage_study.py предоставляет
prepare/preflight без действий при import. Оба job подписываются и проверяются
штатным parser до native execution. Preflight строит обе модели штатно, сохраняет
runtime manifests и читает effective model identities.
Native preflight требует bound-cgroup policy от действующей reservation и
подтверждает закрытие обоих дочерних процессов; fallback на бесконтрольный запуск
не предусмотрен. Входные job/runtime files проверяются на неизменность.

Сравнивается весь эффективный граф: связи, computing order, частота, все узлы и
параметры, включая LTZone и отсутствие LTMembrane. Разрешены только точные замены
трёх именованных образов/соответствующих image selectors и физические изменения
UsePresynapticInhibition false→true, InhibitionCoeff0→2.5 у всех синапсов тела.
Ёмкости, остальные сопротивления, кинетика, feedback, порог и связи обязаны
совпасть. Неожиданное расхождение запрещает последующий Train.

Отрицательные controls изменяют C, PSI coefficient или связь в настоящем native
readback и заново вычисляют semantic hash. Они проверяют отказ по смыслу модели,
не только по повреждённой контрольной сумме. Предварительная проверка не делает
Calculate модели и ещё не подтверждает функциональное изменение waveform.

После принятого preflight — по одному matched cold Train на том же зафиксированном
runtime. После каждого изменения структуры проверяются эффективные дочерние
параметры, реальные проводимости и допустимые Rs. Влияние PSI на численную
устойчивость не заменяется универсальным tau/dt правилом. Свежие наблюдения и
сертификат требуются для конкретного конечного графа.

Результатами считаются также missing/ambiguous, BudgetExhausted и отсутствие
сертификата. Число валидных измерений, остатки, причины отказов и временные графики
с omission/repeat controls сохраняются. Нельзя переносить прежние residual на
новую физику или считать сильный общий максимум доказательством принадлежности
закреплённому импульсу. При Test рассматривается полный отклик и реальные спайки.

Полные primary и графики — только внешний архив/cache M40; Git содержит код,
постановку и компактные refs. Перед завершением этого подэтапа нужны адресная
native приёмка, реальные результаты и merge --no-ff в develop. Этот протокол
не закрывает полную матрицу режимов исходного плана.

## Фактическая входная приёмка

[M40 native preflight A2 принят1/1](PresynapticStoragePreflightAcceptance-20261116.json), все процессы закрыты. Два реальных image readbacks и три rehashed semantic negative controls подтверждены. Stock model5a916bc7c77f2176c065d57e3d68dd0783902b40418eec42cf089eb10b36abf5; PSI1c2511badd52a622e02814e31f74fd89ab0fa99b3b44b4a0e402bb8daea0f356. Native Calculate ещё не проверялся этим preflight. Исторический A1 сохранён; A2 уточняет название флага сохранённой физики, сами модели не изменились. Общий внешний archive226файлов/736454байта, SHA256fbef418ddccfc5c733d2ed6158aba7a6b58f71e3dbab83037f175c6adcaa2e4b.

После приёмки и архивирования запущены Stock и PSI cold A1, controls9303d484ea011bead0f2b18ab07c149a9496ad6a, producer root64327e103d7085972f6512db77a2195f27c5b2fc. Runtime остаётся7b495ebf753259ae8b78c6d0eadd561fb3d2c835/Pulse9e7653a400761d6c2f3ea68fddcd40a4307d85e7. Ресурсная проверка перед запуском:12 CPU в affinity,44.62GB доступной RAM,444.77GB свободного Data. Научных результатов новой пары ещё нет.

## Исправление подготовки Train после первого PSI запуска

Первый PSI cold A1 не проверил обучение: четыре reference группы полны/валидны, затем отказ candidate_window_proposal_arithmetic_rejected, search_probes=0/edits=0. Скрипт перенёс reference-relative guards из Stock. При PSI reference frames61/221/541/1021 вместо Stock49/209/529/1009 эти guards предложили [12,3612] вне hard domain [0,3600]. Native отказ корректен; менять C++ arithmetic или обрезать окно нельзя. Исходный запуск сохраняется как setup error, не как отрицательное свидетельство о PSI.

Обязательный путь подготовки дорогого Train теперь — presynaptic_storage_study prepare-train. Он выполняет production DATA replay закрытого same-physics/protocol reference пакета, проверяет совпадение всей configuration за исключением run_id и двух производных base guards, затем кодирует прежнее полное окно относительно фактического seed: left_guard=first_frame, right_guard=frame_count−1−last_frame. Длительность, hard domain, все prediction/feature coefficients, физика, target, бюджеты и допуски сохраняются. Source hash/origin/initial model revision записываются в window-characterization.json. Перед Train источник перепроверяется; cold Train заново захватывает собственные амплитудные и временные references, прежние references/state не импортируются.

Уточнение прежнего требования «все job fields равны кроме класса/run_id»: оно относится к исходным физическим preflight templates, но оказалось недостаточным для научной cold пары. Относительные guards являются производными координатами и должны различаться при сдвиге reference-пика. Для корректного Stock/PSI сравнения сохраняются одинаковое эффективное полное окно [0,3600] и остальные факторы, а различие производных guards явно фиксируется. Уже завершённый Stock A1 не изменяется и не перезапускается; PSI A2 получает новую identity попытки.

Проверка исправления разделена: production prepare на фактическом PSI A1 primary с контрпримерами чужого класса/target, затем новый native cold PSI. Локальное наличие правки не означает её удалённую приёмку. [Причина и исходный архив](PresynapticWindowSetupFailure-20261116.json).
