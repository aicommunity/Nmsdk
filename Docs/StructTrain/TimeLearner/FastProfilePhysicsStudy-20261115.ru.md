# Storage-физика и разделение закреплённых откликов — 15.11.2026

После [широкого поиска Branch N0](N0RecoveryCoverageScientificReport-20261115.ru.md) input1 остался ambiguous при L28,100,64,46,82. Следующий контраст проверяет реальную физику и форму отклика; исходные assignment, CapturedPerInput и tolerances сохраняются.

## Что установлено фактически

Первая попытка s04-fast-profile-readback-m40-a1 закончилась failed/closed. Stock NSPNeuronGen прошёл native preflight. Первый legacy fast C5e10 отказал native_model_requires_storage_owned_physics: у этих образов UseElementDefaults=true. Это штатная защита V2 от parent-owned uniform physics. Она сохранена. До C25 native readback эта попытка не дошла; C25 не объявляется экспериментально проверенным.

По исходникам legacy D005C25e11 задаёт5e-10, как C5e10. Старые классы сохраняются как compatibility-образы; их названия нельзя использовать как доказательство применённого V2 фактора. Исходный отказ и82 файла controls/receipts сохранены во внешнем архиве313125B, SHA25651b23f58fa41413c88ca98a3ee362239f6d935b13ca477160c5b079075d7a21a.

## Применяемый путь

Используется существующий RegisterStorageProfile после создания Environment. Четыре явных рецепта наследуют параметры фактических stock-дочерних компонентов, не parent defaults и не Asym defaults структуры рецепта. В частности, Inh Rm/RestingResistance остаются stock1e7. Изменяются только C обоих каналов и указанный DissociationTC обоих типов синапсов.

| Variant | C | DissociationTC | Роль |
|---|---:|---:|---|
|0|1e-9|0.005|Реконструкция исходной stock-физики|
|1|5e-10|0.005|Изолированный half-C профиль|
|2|2.5e-10|0.005|Изолированный quarter-C профиль|
|3|2.5e-10|0.002|Объявленное сочетание C и kinetics|

Имена профилей TLNativeFast{variant}F{frequency}_Neuron, частоты2000/20000Гц. UseElementDefaults=false; новые сегменты получают физику дочерних storage-образов. Общий prototype не меняется, исправляющих присваиваний на тиках нет, общий lifecycle Rdk не изменён. Legacy aliases также не меняются.

Root fixture NativeFastStorageProfiles проверяет реальные Take/reuse/Reset/growth при обеих частотах, включая effective child readback до роста, чтобы Build не маскировал ошибочный fresh image. Через штатный ModelArchive экспортируются полные определения images со state_kind=model_spec и training.status=not_trained. Это не обученная модель и не controller checkpoint.

## Gates перед дорогим Train

1. Свежая изолированная сборка s04-fast-profile-sdk-m40-a1: все8 actual C++ cases должны пройти, экспортировать8 полных архивов; затем supervisor и дочерние процессы должны закрыться. Production Pulse Core/Console не меняются относительно принятого исходного кода; этот gate проверяет новые recipes/fixtures, а не заново всю прежнюю матрицу142.
2. Console загружает4 архива2000Гц через штатный PrepareModelArchive, строит реальные cold Branch-модели. Проверяются все дочерние C/Rm/TC/Rs, частота, исходный threshold100, отсутствие LTMembrane и полный граф. Parent overlay и обход guard запрещены.
3. Для variant0 требуется полное native waveform comparison с исходным stock при неизменной частоте, стимуле и графе: cold и выросшая геометрия. Сравниваются реальные полные пачки, не только параметры или аналитическая задержка. При несовпадении physics intervention не допускается до выяснения причины.

SDK source cfcfd327b0b809ebeee1e5abf049c1661d17a860 / Pulse5052cfe1683ca38920b514aedfc3c37f4bd41aef. Каноническая подготовка принята и закрыта, control commit8fa446747ad8a1cc9c883d7f53a26116c390aaec; фактическая native-сборка запущена на M40 в отдельных source/build/runtime. Исходный runtime A5 защищён от записи. PASS8 и экспорт архивов пока не подтверждены.

## Объявляемый следующий научный контраст

После gates — заранее фиксированная пара cold Branch N1 variant0/variant3 при общей области L1..256 и2000Гц. C и kinetics варианта3 являются одним явно составным storage-фактором; нельзя приписывать результат только C. Область256 одинакова для обоих участников и объявляется до запуска; она не является автоматическим увеличением candidate/probe/time budgets после stall. Точные budgets и исходный cold target сохраняются из соответствующей принятой N1 конфигурации и проверяются полным JSON diff перед первым Train.

Цель по-прежнему CapturedPerInput, anchorN−1, amp_abs1e−5/rel0/minamp1e−6/SyncTolerance0.02. Увеличение интервалов самого паттерна, общий максимум вместо закреплённого, C-trim, PostTune, новый порог либо серияD не вводятся. Поиск оценивается по фактическим valid peaks и свежей all-input проверке, не по аналитически ожидаемому L.

Каждый исход сохраняется честно, включая invalid/unresolved. Нужны читаемые временные графики Soma с actual input overlay и omission/repeat controls. Получение Exact не означает готовой классификации; frozen8-pattern evaluation и реальная проверка выбранного порога остаются отдельными этапами. Полные payload — только во внешнем архиве M40, в Git — код, постановка, компактные metadata и проверяемые refs. Полные этапы1–12 остаются открытыми.

## Фактическая приёмка подготовленных моделей

SDK завершён8/8 actual C++ cases; экспортированы8 archives, supervisor/child groups закрыты, heartbeat/capture/record errors отсутствуют. Console readback и baseline waveform gate завершены2/2 и закрыты:5 реальных cold preflight и4 полные burst-пробы. Все C/TC применены, LTMembrane отсутствует. Stock/derived-stock CSV побайтно равны на cold и grown геометриях; это допускает физический контраст, но не означает нового Train.

Перед Train обнаружено ещё одно необходимое ограничение анализа: stock_threshold_study.audit_final_stock жёстко проверяет NSPNeuronGen/NPMembraneBio/TC0.005 и потому не подходит новым явным профилям. Новый отдельный auditor uniform_profile_physics сравнивает реальные effective initial/final trees, разрешая морфологию, число синапсов и положительные individual Rs; C/TC/Rm/classes/threshold/feedback должны сохраняться. Старый stock-контракт не ослаблен. Новая проверка ещё требует серверной регрессии на реальных cold/grown readbacks и повреждённых данных перед подключением к Train.
