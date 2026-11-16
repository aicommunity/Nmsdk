# Fast terminal21600: распознавание — 16 ноября 2026

Новый frozen Test исходных восьми PhaseA паттернов завершён и принят: execution completed, validity valid, восемь полных наблюдений, модель неизменна. При исходном threshold100 все восемь реакций без спайков: TP=0, FP=0, FN=1, TN=7. Это пропуск target, а не успешная классификация. Production CLI/DATA/physical/frozen проверка1/1, все процессы закрыты. [Квитанция](FastN1FullTrainingFrozenAcceptance-20261116.json).

## Модель и протокол

Использована целиком фактическая terminal-модель [cold Train21600](FastN1FullTrainingScientificReport-20261116.ru.md): revision07101c0b0b29e746ad601050613786b1450f5a733464b501c5738ab92d3d7b22, L=[201,201,121,1], Rs=[86M,86M,9.73184034290068M,86M]Ω, Ns=1. Branch N4/N1, Fast3 C2.5e-10F/TC0.002с/2000Гц. LTMembrane отсутствует; C-trim Off. Conversion=identity, все физические входы включены, reset-per-trial, rotation0, полное2с окно. Train остановлен по бюджету измерительной группы, общего TrainingCertificate нет; Test маркируется diagnostic.

| sample_id | Метка | Window spikes | Результат |
|---|---|---:|---|
|phasea-row-0|target|0|FN|
|phasea-row-1|foil|0|TN|
|phasea-row-2|foil|0|TN|
|phasea-row-3|foil|0|TN|
|phasea-row-4|foil|0|TN|
|phasea-row-5|foil|0|TN|
|phasea-row-6|foil|0|TN|
|phasea-row-7|foil|0|TN|

Нет также early/late событий. Accuracy7/8 отражает только преобладание отрицательных примеров; target hit rate0. Все фактические входы и полные waveforms сохранены. Прежние Fast TP1/FP3 относятся к другой terminal7200 модели и не переносятся на эту структуру.

## Один объявленный порог и визуальная проверка

После полной приёмки baseline запущен s11-fast-full-training-threshold-m40-a1, source5248368b75194c657163f51f747f4512605e0e1b, controls0e40284ad7900cc709531d24ac739cd11854e63b. [Протокол](FastN1FullTrainingRecognitionProtocol-20261116.ru.md) зафиксирован заранее: сначала точный native baseline repeat всех8, затем один midpoint-кандидат по recorded global LT maxima. На11:13UTC job жив, owned PID2389747; результат ещё неизвестен. Порог — единственное объявленное изменение recognition state; нового Train или независимой scientific partition нет.

Elder независимо восстановил все489 logical members:488 regular files после исключения одного доказанного glog alias. Его production DATA/scorer и Soma/LT report выполняются как отдельное owned задание s11-restored-full-training-frozen8-report-elder-a1, sourcec60560a38eeda634947ae5cd3ef3872ee4258b6f/controls679e41adea204bc4ee515c7fad89a4672909d0d7. Итог и ручная визуальная приёмка пока открыты; самостоятельный replay не создаёт новой научной выборки.

## Первичные данные

Самодостаточный XZ primary28,003,840байт,489 logical members, SHA25678a197ec5897643e095ef1724be7f18038b6a6997ae420fb582772d922cbef6e. Bundle manifest9506f5413a5a63db9bbcee0bc39098be4eccc19209edb0b44e3a85c6d97a691d. Полная provenance/controls квитанцияa31a3d73c4e3c600273c1ed5c5ad9ba79fc9bedd7ec6c8f61f522d0b0f381050. Точные refs/размеры в [приёмке](FastN1FullTrainingFrozenAcceptance-20261116.json).

Архив и будущий воспроизводимый кэш графиков размещаются во внешнем /media/user/Data/Nmsdk-StructTrainExpArchive, каталогexperiments/2026-11-16/fast-profile-wall-budget/full-training-frozen8-primary-a1.json. Тяжёлые файлы в Git не добавляются.
