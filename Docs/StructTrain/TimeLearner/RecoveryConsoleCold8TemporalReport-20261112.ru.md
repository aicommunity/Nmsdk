# Console cold8: временные графики технического пилота — 12.11.2026

Classic и Branch завершили реальное холодное обучение, калибровку и frozen Test. На каждой модели:TP2/FP0/FN0/TN2. Это ограниченный N2/N0/SyncTolerance0.2 same-matrix контроль, один target и один foil по два раза; он не заменяет научную N4 матрицу. [Условия и первичные результаты](ValidationPlans/M40RecoveryConsoleCold8A1-20261111/RESULT.ru.md).

На графиках синий — фактический Soma.SumPotential, оранжевый — реальный вход, пунктир — фактическое событие LT. После события видна сильная отрицательная фаза. Для малых положительных откликов используйте увеличения:общий масштаб Y на обзоре их сжимает. Единицы модели не объявляются проверенными SI.

Автоматическая проверка охватила все8предъявлений/12пар trial×soma, без прореживания samples; полный кэш M40 содержит смежные увеличения и SVG/PDF. В Git сохранено24PNG. Вручную просмотрены10PNG, весь кэш не заявлен проверенным. [Приёмка, исходный код, хеши и ограничения](ValidationPlans/M40RecoveryConsoleCold8ReportsA2-20261112/RESULT.ru.md).

## Classic-window-N0

### target

![Classic-window-N0 target overview](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Classic-window-N0/trial-0000-soma-001/overview.png)

### foil

![Classic-window-N0 foil overview](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Classic-window-N0/trial-0001-soma-001/overview.png)

## Branch-window-N0

### target

![Branch-window-N0 target overview](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Branch-window-N0/trial-0000-soma-001/overview.png)

### foil

![Branch-window-N0 foil overview](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Branch-window-N0/trial-0001-soma-001/overview.png)

## Все выбранные графики

- [Classic-window-N0 | target | $.Soma1.SumPotential | 0 | overview](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Classic-window-N0/trial-0000-soma-001/overview.png)
- [Classic-window-N0 | target | $.Soma1.SumPotential | 0 | zoom-002-detail](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Classic-window-N0/trial-0000-soma-001/zoom-002-detail.png)
- [Classic-window-N0 | target | $.Soma2.SumPotential | 0 | overview](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Classic-window-N0/trial-0000-soma-002/overview.png)
- [Classic-window-N0 | target | $.Soma2.SumPotential | 0 | zoom-002-detail](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Classic-window-N0/trial-0000-soma-002/zoom-002-detail.png)
- [Classic-window-N0 | foil | $.Soma1.SumPotential | 1 | overview](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Classic-window-N0/trial-0001-soma-001/overview.png)
- [Classic-window-N0 | foil | $.Soma1.SumPotential | 1 | zoom-002-detail](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Classic-window-N0/trial-0001-soma-001/zoom-002-detail.png)
- [Classic-window-N0 | foil | $.Soma2.SumPotential | 1 | overview](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Classic-window-N0/trial-0001-soma-002/overview.png)
- [Classic-window-N0 | foil | $.Soma2.SumPotential | 1 | zoom-002-detail](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Classic-window-N0/trial-0001-soma-002/zoom-002-detail.png)
- [Classic-window-N0 | foil | $.Soma1.SumPotential | 2 | overview](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Classic-window-N0/trial-0002-soma-001/overview.png)
- [Classic-window-N0 | foil | $.Soma1.SumPotential | 2 | zoom-002-detail](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Classic-window-N0/trial-0002-soma-001/zoom-002-detail.png)
- [Classic-window-N0 | foil | $.Soma2.SumPotential | 2 | overview](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Classic-window-N0/trial-0002-soma-002/overview.png)
- [Classic-window-N0 | foil | $.Soma2.SumPotential | 2 | zoom-002-detail](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Classic-window-N0/trial-0002-soma-002/zoom-002-detail.png)
- [Classic-window-N0 | target | $.Soma1.SumPotential | 3 | overview](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Classic-window-N0/trial-0003-soma-001/overview.png)
- [Classic-window-N0 | target | $.Soma1.SumPotential | 3 | zoom-002-detail](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Classic-window-N0/trial-0003-soma-001/zoom-002-detail.png)
- [Classic-window-N0 | target | $.Soma2.SumPotential | 3 | overview](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Classic-window-N0/trial-0003-soma-002/overview.png)
- [Classic-window-N0 | target | $.Soma2.SumPotential | 3 | zoom-002-detail](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Classic-window-N0/trial-0003-soma-002/zoom-002-detail.png)
- [Branch-window-N0 | target | $.Soma1.SumPotential | 0 | overview](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Branch-window-N0/trial-0000-soma-001/overview.png)
- [Branch-window-N0 | target | $.Soma1.SumPotential | 0 | zoom-002-detail](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Branch-window-N0/trial-0000-soma-001/zoom-002-detail.png)
- [Branch-window-N0 | foil | $.Soma1.SumPotential | 1 | overview](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Branch-window-N0/trial-0001-soma-001/overview.png)
- [Branch-window-N0 | foil | $.Soma1.SumPotential | 1 | zoom-002-detail](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Branch-window-N0/trial-0001-soma-001/zoom-002-detail.png)
- [Branch-window-N0 | foil | $.Soma1.SumPotential | 2 | overview](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Branch-window-N0/trial-0002-soma-001/overview.png)
- [Branch-window-N0 | foil | $.Soma1.SumPotential | 2 | zoom-002-detail](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Branch-window-N0/trial-0002-soma-001/zoom-002-detail.png)
- [Branch-window-N0 | target | $.Soma1.SumPotential | 3 | overview](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Branch-window-N0/trial-0003-soma-001/overview.png)
- [Branch-window-N0 | target | $.Soma1.SumPotential | 3 | zoom-002-detail](../../../Reports/StructTrain/TimeLearner/RecoveryConsoleCold8VisualSelection-20261112/Branch-window-N0/trial-0003-soma-001/zoom-002-detail.png)
