# Общие Soma и LT decision отчёты — 16 ноября2026

## Дефект и изменение

Обычный production renderer показывал Soma и фактические входы, а LT views существовали в теле test_diagnostic_threshold_study_report. Поэтому отдельно принятый baseline отчёт мог не выполнить требование полного LT протокола, хотя специализированный тест рисовал LT корректно. Дублирование перенесено в Scripts/StructTrain/TimeLearner/lt_decision_reports.py и вызывается reports._render_evaluation после существующего единственного scorer.

Новые schema2 recognition/diagnostic/calibration-candidate отчёты автоматически получают отдельные LT decision views всех имеющихся наблюдений, фактический effective_threshold из того же analysis, реальные inputs/spike events и HTML links. Число Soma channels/pairs и Soma figures сохраняет прежний смысл. Порог не наносится на отдельную Soma.

Проекция s.lt_potential в единственную рисуемую колонку существует только внутри renderer; она никогда не передаётся scorer. Исходные observations, модель и метрики не изменяются. Schema1 без LT source отмечается legacy_lt_channel_not_recorded; Soma не заменяет отсутствующий LT. Пропуски/пустые observations сохраняют явный список unavailable_trials. Неполные окна рисуются как неполные, полнота покрытия панелями не означает полноту измерения.

## Масштаб и пики

Обзор содержит всё записанное окно. Native tiles имеют минимум8px на timestep и не прореживаются. Общая LT Y-шкала включает фактический порог; дополнительные локальные Y views дают разглядеть малый сигнал при threshold100. В легенде всегда указано численное значение порога, а находящийся за видимым Y диапазоном порог помечается outside shown Y; metadata содержит reference_level_visible.

Для различимого внутреннего глобального максимума LT дополнительно запрашивается существующий sample-marked local peak detail. Он использует реальные10 отсчётов по обе стороны максимума и не вводит новую интерполяцию. Максимум на границе окна явно помечается; отсутствующий пик не достраивается. Test global maximum не меняет Train assigned-impulse contract. After-children LT samples могут уже отражать event/reset: действительные события показываются по native spike_times, пересечение линии по картинке не пересчитывает метрики.

## Приёмка

- Existing production PlotScaleTest и новые refusal/legacy contracts выполняются на сервере.
- Реальный Fast schema2 baseline из полного независимо восстановленного frozen8: прежние metrics/source сохраняются, восемь Soma и восемь LT panels, actual threshold100 и корректная маркировка локальной Y-шкалы.
- Реальный PSI actual candidate со спайками: тот же общий renderer сохраняет native metrics, реальные spike markers, threshold и complete windows. Тест больше не имеет собственной копии LT-rendering.
- PIL проверяет размер1920×960 и отсутствие downsampling; visual acceptance выбранных оригиналов остаётся отдельным шагом.

Common coverage принят по Elder11/11 и M401/1; positive-lobe дополнение — по отдельному actual Fast candidate1/1. Общая feature объединена через --no-ff в develop c5f05571a9cd1f294ebb5772a55bbd3ab3819459. [Приёмка и внешние refs](FastN1CommonTemporalAcceptance-20261116.json). Старые архивированные отчёты не переписываются; новые полные галереи/primary сохраняются только во внешнем M40 архиве. Научные факты Fast/PSI и оба активных M40 задания этим кодом не изменяются.

## Дополнение после визуальной проверки

На actual Fast target отрицательное восстановление около−1.4 сжимает положительный максимум около0.056. Поэтому общий renderer теперь сохраняет обычные full-recovery виды и дополнительно строит positive-lobe-detail для Soma и LT, если есть положительная область и отрицательные значения. Это только диапазон отображения: native samples, events, threshold и metrics не меняются; отрицательные участки явно обозначены вне Y, их число сохранено в metadata. Есть полный обзор и все native tiles без прореживания. На Soma порог не наносится. Реальный восьмипаттерновый report test проверяет обе шкалы, сохранение полного диапазона, clipped counts и реальные неизменные metrics. Отдельный серверный запуск завершён1/1, процессы закрыты, восемь positive Soma/LT оригиналов просмотрены. Все983 обычных PNG сохранились побайтно; итоговая галерея1403PNG. Полный ручной просмотр галереи не заявляется.
