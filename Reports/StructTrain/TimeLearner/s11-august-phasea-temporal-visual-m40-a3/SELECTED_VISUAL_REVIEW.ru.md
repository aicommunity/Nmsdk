# Визуальная приёмка выбранных графиков August replay

01.11.2026 непосредственно просмотрены все15 выбранных PNG в исходном1920×1200.
Полный cache содержит96 PNG для24 предъявлений ×4 сомы: full, detail100ms,
signal и signal_detail. Ручной просмотр всех96 файлов не заявляется.

| Группа | Просмотрено | Наблюдение |
|---|---:|---|
| Baseline: signal для trial0–7 |8|Все4 входных импульса, четыре сомы и индивидуальные волны различимы; target и FP имеют красную отметку LT output; молчащие foil1/3/7 её не имеют.|
| Target0 и foil4: signal_detail всех трёх случаев |6|100ms около последнего импульса; различимы сам импульс, момент LT spike и последующая реакция. Изменение порога сдвигает момент ответа; это реально записанные прогоны, не offline threshold sweep.|
| Baseline target0: full |1|Отрицательный выброс после LT spike и восстановление показаны полностью; сигнал не удалён из первичных данных.|

Дополнительные signal-шкалы включают все положительные запаздывающие волны
окна и исходный pre-spike baseline. Отрицательный feedback может выходить
за вертикальную шкалу; число точек вне неё явно подписано. Полные full/detail
виды сохраняют весь диапазон. Значения потенциала подписаны как native units;
самовольного пересчёта в mV нет. Легенда вынесена из области кривых.

Первая версия a1 оказалась недостаточной для амплитудного анализа: feedback
около−0.38 сжимал полезные волны0.01–0.03. Версия a2 добавила pre-spike
масштаб, но часть запаздывающих положительных волн выходила выше него.
Актуальная версия a3 устраняет эту потерю видимости, сохраняя full companions.
Эти изменения относятся только к renderer; модель и первичные данные неизменны.

## Выбранные изображения

| Baseline trial | Рисунок |
|---|---|
|0 target|[signal](selected/baseline/trial-0-signal.png), [detail](selected/baseline/trial-0-signal_detail.png), [full](selected/baseline/trial-0-full.png)|
|1 foil|[signal](selected/baseline/trial-1-signal.png)|
|2 foil|[signal](selected/baseline/trial-2-signal.png)|
|3 foil|[signal](selected/baseline/trial-3-signal.png)|
|4 foil|[signal](selected/baseline/trial-4-signal.png), [detail](selected/baseline/trial-4-signal_detail.png)|
|5 foil|[signal](selected/baseline/trial-5-signal.png)|
|6 foil|[signal](selected/baseline/trial-6-signal.png)|
|7 foil|[signal](selected/baseline/trial-7-signal.png)|

Другие пороги: [0.0130 target](selected/threshold0130/trial-0-signal_detail.png),
[0.0130 foil4](selected/threshold0130/trial-4-signal_detail.png),
[0.0135 target](selected/threshold0135/trial-0-signal_detail.png),
[0.0135 foil4](selected/threshold0135/trial-4-signal_detail.png).

## Проверки и воспроизведение

Reader source`5a2204d90e1b5db7bff5270a3a6a3581b9b949e8`.
На Elder7/7 и M407/7 проверок реальных native
потоков/corruption. Последующие изменения затрагивают renderer, не reader.
Фактический final renderer root:
`41a2b70d95931af6f10da14a6065259a3cfe4782`;
proof`dc9f8f43a2945cfefc9fc1efa6eb8abfe1e4cead`.

Каждая из трёх записей содержит12 потоков ×80000 samples,2000Гц/40s,
32 actual input edges и8 окон. Soma_i = ExcChannel.Output + InhChannel.Output
совпадает с native learner vector на каждом отсчёте. CSV всех трёх случаев
побайтно равен untouched replay. Число LT edges5/4/3; во всём записанном
40s интервале дополнительных LT edges вне восьми окон не обнаружено.
Это не приписывает старой CSV-схеме отсутствующие в ней поля.

Все113 members первичного пакета после отрисовки неизменны. Размеры и наличие
всех96 PNG проверены на M40; outer/member/selected SHA256 дополнительно
проверены при локальной приёмке. В Git15 selected PNG /2704518B и metadata
6840B; полный cache —
`/media/user/Data/TimeLearnerRefactor/reports-august-phasea-temporal-m40-a3/index.html`.

Сжатые raw traces и модели:
[primary](../s11-august-phasea-temporal-primary-elder-a2/README.md),
commit`2376e1c3d6a17d0edcdcf9ce8d10272009ebfadd`,113 members/7533332B.
Для воспроизведения восстановить проверенные members из primary.tar.xz,
затем выполнить с root указанного renderer:

```text
python -m Scripts.StructTrain.TimeLearner.historical_phasea_temporal --input RESTORED/replay --output NEW_EMPTY_OUTPUT --plots
```

Python/matplotlib/Pillow runtime, полный перечень PNG с hash и команда
сохранены в manifest/metadata.tar.xz. Начальный manifest с pending manual review
сохранён как исходная квитанция публикации; этот документ фиксирует последующую
непосредственную приёмку. Это адресный historical saved-state/temporal milestone;
cold Train, robustness, legacy/V2 A/B и весь этап11 остаются открытыми.
