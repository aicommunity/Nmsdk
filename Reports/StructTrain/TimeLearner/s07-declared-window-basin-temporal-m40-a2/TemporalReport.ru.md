# Временные отклики: declared-window basin

Набор содержит 14 технических групп: 8 допустимых назначений, 2 неоднозначных слитых отклика и 4 прерванные группы. Это новый проверочный набор, а не историческая матрица разделимости. Полные группы содержат Full before, по одному пропуску каждого входа и Full repeat. Для прерванных групп показаны только реально сохранённые пробы; отсутствующие контроли и геометрия не достраиваются.

На графиках показаны все физически записанные сомы. На каждую панель потенциала и её zoom наложен оранжевый ступенчатый измеренный сигнал Full before из столбца CSV stimulus; справа подписана независимая шкала исходных единиц входа. Высоты входа и потенциала не сравниваются по общей шкале. Нижняя панель сохраняет фактические входы всех записанных контролей. В отдельных контрольных панелях оранжевый вход относится именно к соответствующей пробе. Идентификаторы импульсов и их моменты взяты из observed packet events. Отдельные формы сигнала каждого физического входа не записывались: они не синтезируются из расписания.

Каждая проба переводится из абсолютного времени в τ=(CSV time−observation.specification.begin)×1000 мс; исходные начала указаны в manifest. Кривые не интерполируются, не сглаживаются и не нормируются. Правая колонка использует отдельный локальный диапазон Y для каждой сомы. Голубая область — объявленное окно; янтарная — зафиксированный basin между записанными долинами; крестики — кандидаты; звезда — выбранное измерение. Эти отметки взяты из проверенной записи, алгоритм выбора в renderer не запускается.

Независимый Python replay подтвердил геометрию десяти полных групп и отсутствие продвижения четырёх неполных. Он не является подтверждением native causal lineage и не создаёт сертификат обучения.


| Группа | Модель | Гц | Вход → канал | Результат | Проб |
|---|---|---:|---|---|---:|
| basin_native0 | Classic | 2000 | 0 → 0 | valid | 4 |
| basin_native1 | Classic | 2000 | 1 → 1 | valid | 4 |
| basin_native2 | Branch | 2000 | 0 → 0 | valid | 4 |
| basin_native3 | Branch | 2000 | 1 → 0 | valid | 4 |
| basin_native4 | Classic | 20000 | 0 → 0 | valid | 4 |
| basin_native5 | Classic | 20000 | 1 → 1 | valid | 4 |
| basin_native6 | Branch | 20000 | 0 → 0 | valid | 4 |
| basin_native7 | Branch | 20000 | 1 → 0 | valid | 4 |
| basin_native8 | Classic | 2000 | 0 → 0 | ambiguous | 4 |
| basin_native9 | Branch | 2000 | 0 → 0 | ambiguous | 4 |
| basin_native10 | Classic | 2000 | 0 → 0 | partial / rejected | 1 |
| basin_native11 | Branch | 2000 | 0 → 0 | partial / rejected | 1 |
| basin_native12 | Classic | 2000 | 0 → 0 | partial / rejected | 1 |
| basin_native13 | Branch | 2000 | 0 → 0 | partial / rejected | 1 |

## Выбранные графики

![basin_native0-overview-and-zoom](Figures/basin_native0-overview-and-zoom.png)

![basin_native0-control-panels](Figures/basin_native0-control-panels.png)

![basin_native7-overview-and-zoom](Figures/basin_native7-overview-and-zoom.png)

![basin_native7-control-panels](Figures/basin_native7-control-panels.png)

![basin_native8-overview-and-zoom](Figures/basin_native8-overview-and-zoom.png)

![basin_native9-overview-and-zoom](Figures/basin_native9-overview-and-zoom.png)

![basin_native10-overview-and-zoom](Figures/basin_native10-overview-and-zoom.png)

![basin_native13-overview-and-zoom](Figures/basin_native13-overview-and-zoom.png)

## Полный серверный набор

M40: `/media/user/Data/TimeLearnerRefactor/analysis/declared-window-basin-temporal-m40-a2`. Для каждой из 14 групп сохранены overview+local-Y zoom и отдельные панели всех доступных контролей (PNG и SVG). Полные файлы перечислены с хешами в manifest.json.

## Источники

- C++ primary: `7ec9d4ff731a7775903080d6a96b5d5a9febe340`.
- Python replay: `bcc46e7d797890b47214a866085f5f71027b5c5b`; reader tool `f71c16b46d3c8150eb860be2aeb6949e57247642`.
- Compiled root: `51566b251a087589411d0a6bbb848de7d0273b6e`; Pulse: `c3ac0aad30ccc4b9894e0d4dccb3386d688d504f`.
- Renderer root: `fc5bc42f23b6655906e224c817dc39fa05149586`.
