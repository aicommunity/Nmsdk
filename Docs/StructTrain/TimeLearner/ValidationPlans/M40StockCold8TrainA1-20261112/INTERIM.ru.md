# Промежуточный результат строгого N4 cold8 Train — 12.11.2026

Branch native Train завершился штатно за403.24s, его process group закрыт. Независимый production DATA auditor завершил проверку Branch package7/summary8:28logical groups,168native probes,604968sampled frames,24442733primary bytes; артефакты валидны, stock physics audit принят. Это **не валидность всех наблюдений и не сходимость**.

Обучение Branch остановлено как invalid_observation, reason rejected_candidate_window:missing. Search probes24, edits11; конечные/accepted L[7,7,7,1], Rs86MΩ, Ns1. Certificate=null; classification_assessed=false; Test не запускался. [Точные производные поля и source-summary SHA256](interim-Branch-outcome.json).

Проверены реальные recovery переходы:четыре cursor_advanced, пятое delivery — invalid_budget_stop (invalid4→5). Поэтому delivery_count5 не означает пять успешно выполненных восстановлений. Этот прогон подтверждает работу recovery-пути на настоящих N4 данных, но не его достаточность для обучения. Не объявляется PhysicalInfeasible или отрицательная классификация.

После Branch начался отдельный Classic native Train; [последнее наблюдение](classic-progress-after-Branch.txt). Общий cohort ещё не принят, полный job не закрыт и не архивируется до завершения второго случая. Следующий алгоритмический разбор должен использовать реальные full/omission waveform и проверить, означает ли missing отсутствие assigned peak или промах объявленного prediction window. Подмена общим максимумом пачки запрещена; genuine merged peak остаётся ambiguous.
