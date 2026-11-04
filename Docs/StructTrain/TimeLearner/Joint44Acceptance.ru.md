# Совместный normal44: исправление expectations проверено

Источник `8021301e894368aefd045f9d77274fcce9f60245`, PulseLib
`cc97149c90ce98ff24ca688452f4a40d54e0e63d`. Elder выполнил44/44 native cases
за764501ms. JUnit полный, failures/errors отсутствуют. Все1275 members
архива и510 исходных blobs независимо сверены с Git. Worker cgroup закрыта,
ресурсный резерв освобождён. [Receipt](Joint44Verification.json).

Proof `82910cad87425fcad0ef67480d612bb917c6d933` сохраняет сжатые первичные
данные, manifest, JUnit, declared inventory, диагностику и kernel closure в
`Reports/StructTrain/TimeLearner/s07-csearch-threshold-joint-normal-a4`.
Первоначальный failed42 сохранён отдельно: [разбор](Joint42Failure.ru.md).

Восемь high100 controls явно требуют ноль spikes и выполняют это требование.
Два дополнительных уже существовавших low0.0001 positive controls дали
по2 spikes. Ни молчание, ни прохождение fixture не объявляются успешной
классификацией. Это engineering LT fixtures, а не августовский stock граф.

Прямое A/B с failed42: восемь effective graph identities совпали. В32 frozen
observations после удаления только общего сдвига абсолютных часов совпадают
потенциалы сомы, LT output, входные сигналы, состояния/метаданные и события.
Сдвиг около3.517s вызван двумя дополнительными ранее выполняемыми тестами.
Абсолютные event/history/sample times проверены на одинаковый сдвиг,
relative times — на равенство в пределах1e-10s; фактический максимальный
остаток1.4210854715202004e-14s. Амплитудные данные сравнивались точно,
численные допуски обучения не менялись. Raw observations не побайтно равны;
их исходные метки времени сохранены в обоих архивах.

Полная normal304 regression запущена отдельно, без checkout/сборки/изменения
runtime-a4. Новый worker держит read leases источника, build и runtime до
окончания упаковки и завершения всей группы; release выполняется контроллером
через проверенный `recover_closed_worker` после свежего kernel readback.
Это pending gate, не304 passed. ASan joint native и дополнительные readers
также pending. Рекомендуемость V2 и завершение этапов1–12 не присваиваются.
Отдельно требуются temporal reports всех предъявлений с soma/input overlays,
совместные C On/ModelSpec2 calibration и оставшаяся исходная матрица.
