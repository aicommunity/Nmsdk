# Classic N0 завершён: нормализация амплитуды ещё не достигнута

M40 s11-stock-n0-classic-train-m40-a1: production1/1 PASS1852.633с, outer completed/closed1874.2019382650033с, heartbeat errors0. Native process completed/closed1224.3366667111404с. [Test log](completed/worker/validation/unittest.log), [controller result](completed/controller-result.json), [whole-group closure](completed/process/whole-group-closure.json). PASS означает корректное исполнение и полный DATA/physical audit; научная сходимость не получена.

Training invalid_observation, reason rejected_candidate_window:ambiguous.13 допустимых measured candidates,0 timing-ready,0 jointly-ready,36 search probes,17 edits. Полны40 logical groups/240 native trials/864240 frames (3601 на пробу); число CSV-файлов на диске не является числом проб, поскольку экспорт может хранить дополнительные копии. Certificate=null, финальной all-input проверки и классификации нет. [Run index с audit](completed/worker/native-stock-n0-classic-train/Classic-stock-cold8-N0/index.json), [оригинальный summary](completed/worker/native-stock-n0-classic-train/Classic-stock-cold8-N0/runs/train/native/train_stopped_summary.json).

В13 измеренных кандидатах проверены L0=1..13; все Ns=1 и Rs=86M. До временного допуска input0 поиск не дошёл, поэтому амплитудный N0 actuator Ns>1 на этой траектории не применён. Это не положительный контроль действия нормализации и не доказательство бесполезности N0. Лучший измеренный timing candidate L=[13,1,1,1], epoch16/search50, fresh anchor search49/group37: timing residual−0.36299999999999955с, amplitude residual−0.010436733241943275, оба допуска нарушены.

|Отказ search|L0 при остальных L=1|Disposition|
|---|---:|---|
|11|54|cursor_advanced|
|17|52|cursor_advanced|
|41|49|cursor_advanced|
|47|48|cursor_advanced|
|53|45|invalid_budget_stop|

Первый/последний и промежуточные отказы относятся к разным фактическим структурам. **Третий отказ N0 — L49; в N1 был L50**, истории не копируются между режимами. Пять ambiguous observations исчерпали объявленный allowance4. Отказ не превращается в measured peak или PhysicalInfeasible.

Terminal parameters L=[45,1,1,1], Ns=[1,1,1,1], Rs=[86M,86M,86M,86M]. Соответствующие полный logical vector и reported model revision35d849faa2aaea5d2620f0fd59d9934c77760b7fde0dd49d3284539f69f68263 совпали с [Classic N1 recovery4](../../ClassicCoupledCold4ScientificReport-20261114.ru.md). Это совпадение конкретного остановленного состояния; оно не доказывает эквивалентность алгоритмов, полное совпадение checkpoint dynamics или две независимые успешные классификации. Различия количества/порядка посещённых точек не являются ускорением до одинаковой сходимости.

[Объявленные условия](../../StockNormalizationControl.ru.md) сохранены: stock без LTMembrane,2000Гц, CapturedPerInput, anchorN−1, ampabs1e-5/relative0/min1e-6/sync.02; native wall1800s/probes128/edits1280/candidates128/input/sweeps4/invalid4, process finalization300s отдельно. N0 разрешает Ns1..128 неопорным входам, фиксирует собственные исходные Rs, anchorNs1/L1/Rs86M. Выбор режима включает его штатный порядок поиска; этот контроль не изолирует чистое действие Ns от всех mode-specific ветвей алгоритма. Физика:52 membranes/104 channels проверены, threshold и feedback connections сохранены.

Python source69e985df6654ac64cc34571e6862119cf26b90c5, controlb2ed995b5f797d4a331ccba6d021f578a3f95edb. Неизменный native SDK root74e5d206d4b619fcf81f77f11b54ebec7b8f0f6e/Pulse7c6c94785af0c83104d348bb3b733ed1f149c8a8, runtime105ccc46bf2d23aa093ee6ec5fb088d9f33faa8e572f8191869f8cc279377a8a. [Actual native job](completed/worker/native-stock-n0-classic-train/Classic-stock-cold8-N0/runs/train/native/job.json) SHA256fff060023273e7b5118cfd32db681eff6056db2855576e270598836d7518b6b1.

Producer3f1ebf009de47457abe63552da7eec2121bac11e, pack162532B SHA256b861a16583f9493b9ac1f36a3e96b09fbce057d7d81348512d8e42848fb7e9f7;33 raw Git blobs сохранены без JSON rewrite. [Полный compressed primary собран](../M40StockN0ClassicPrimaryA1-20261114/RESULT.ru.md),28,455,532B XZ. Собственные N0 временные графики ещё ожидаются. Collector выполнен после закрытия timed Branch, чтобы не менять его ресурсные условия. Графики N1 не выдаются за N0. Train/Test повторно не запускались, порог не подбирался. Августовские4/8–6/8 относятся к своему протоколу и этим исходом не отменяются.
