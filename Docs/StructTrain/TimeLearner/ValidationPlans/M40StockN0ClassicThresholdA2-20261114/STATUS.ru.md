# Classic N0 threshold A2: отдельный повтор выполняется

Job s11-stock-n0-classic-threshold-m40-a2, control40b7cea22a21f48f6926837a682b11a7f5753346. Итога actual spikes пока нет. Исходный Console/INI/compiler побайтово прежние; текущие libc/libm/loader записаны отдельным runtime377e0ebdee7bb1fa1cc11346438a1d2102b2124f08e3054b6347400c10a4f335. Старый105ccc не менялся. [Переход среды](controls/fixture/runtime-transition.json), [исходный manifest](controls/fixture/predecessor-runtime.json).

До candidate требуется реальный baseline100 replay с точным равенством исходных waveform. Единственный заранее выбранный threshold0.012765548843211696 должен совпасть с [ранее сохранённым proposal](controls/fixture/predecessor-proposal.json); несоответствие запрещает принятие результата. Ни новые thresholds по исходу, ни independent Test/training certificate этой процедурой не создаются.

[A1 отказал до native execution](../M40StockN0ClassicThresholdA1-20261114/RESULT.ru.md); nonspiking proxy не выдан за классификацию. [Literal controls](declaration-integrity.json) опубликованы до результата A2.
