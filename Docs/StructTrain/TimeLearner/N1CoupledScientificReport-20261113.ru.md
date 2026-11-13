# Branch N1: измеренная нормализация одного входа и остановка на слитном раннем отклике

В новом холодном обучении третий вход впервые в этой серии одновременно выполнил исходные допуски времени и амплитуды. Дальше второй вход не получил однозначно закреплённого пика, и обучение остановилось с invalid_observation/ambiguous. Общего сертификата сходимости нет. Это конкретный локальный результат исправленного поиска; он ещё не означает работающий классификатор.

## Что сравнивалось

Branch N4, N1,2000Гц, CapturedPerInput, опорный входN−1. Тот же исходный target и stock storage physics без LTMembrane; actual native job и initial-state побайтово совпадают с [baseline](ValidationPlans/M40N1CoupledBranchTrainA1-20261113/actual-condition/comparison.json). Научные бюджеты и допуски не увеличены. В отличие от прежнего one-extra-turn варианта, новый поиск ограниченно уточняет Rs на timing-ready геометрии и использует измеренные Branch length proposal families. [Алгоритмическая постановка](N1CoupledProposalReview-20261113.ru.md), [адресная проверка93/93](ValidationPlans/M40N1CoupledSdkA4-20261113/RESULT.ru.md). Это не изолированная оценка вклада каждого из трёх изменений.

| Показатель | Предыдущий local-turn A3 | Новый coupled A1 |
|---|---:|---:|
| Consumed candidate measurements |52|22|
| Search probes |105|54|
| Timing-ready candidates |5|не используется как итог сходимости|
| Одновременно timing+amplitude-ready |0|1, только input2|
| Outcome |budget_exhausted|invalid_observation: ambiguous input1|
| Финальная all-input проверка и сертификат |нет|нет|

Количество кандидатов и длительность нельзя трактовать как ускорение до одинакового результата: новые и старые траектории поиска заканчиваются по разным причинам. [Предыдущий научный отчёт](N1LocalTurnScientificReport-20261113.ru.md).

## Локально успешный кандидат: третий закреплённый импульс

Группа48/search88, epoch21: L=[28,28,27,1], Rs=[86M,86M,21.232304307596M,86M], Ns=1. Native measured amplitude остаток−1.496405621637109e−8 при абсолютном допуске1e−5, относительный допуск0. Ошибка времени+0.002499999999940883s при SyncTolerance0.02s. Непосредственно перед кандидатом выполнен свежий anchor group47/search87. Значения не получены интерполяцией: интерполяция только предложила реально рассчитанный Rs.

На полном отклике видны вершины около0.3215,0.507 и0.7505s после начала пробы. **Для input2 используется средняя вершина0.507s**, амплитуда0.015781451635265453; самая высокая ранняя вершина0.022641575009082593 относится к другому участку пачки и её не подставляют вместо закреплённого импульса. В omit-2 средняя вершина исчезает; ранняя и поздняя остаются. Это соответствует допустимому отдельному пику при наличии хвостов соседних откликов.

![Group48: полный отклик, исключение каждого импульса и повтор полного отклика](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/figures/group-000048-soma-000-overview.png)

## Почему следующий вход не принят

Последняя группа58/search107, input1: обе ранние входные посылки дают один общий ранний максимум. При исключении первой посылки ранний максимум смещается позже; при исключении второй — раньше. В обоих случаях в соответствующем бассейне остаётся отдельный максимум. По принятому правилу контроля не найден единственный необходимый вход; зафиксировано highest_window_basin_peak_has_ambiguous_necessity. Пик третьего импульса и поздний пик по-прежнему раздельны.

![Group58: неоднозначная ранняя вершина и реальные omission controls](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/figures/group-000058-soma-000-overview.png)

Пять rejection records(search90/95/99/103/107) исчерпали объявленное восстановление4. Запись complete означает закрытие окна и полные данные; она не делает принадлежность пика valid. Эти наблюдения описывают данное состояние и протокол. Они не доказывают физическую невозможность решения для всех геометрий/моделей и не отменяют августовские4/8–6/8.

Фактический terminal vector[28R86M,27R21.232304M,27R21.232304M,1R86M] отличается от group48. Graph SHA совпадает, но полный logical parameter assignment различается; один graph hash не переносит сертификат между ними. Production projection проверяет оба признака и не находит terminal vector среди consumed candidates. Frozen-оценка использует именно terminal state, с этой оговоркой.

## Данные, масштаб и проверки

Сохранено58 complete groups×6 trials=348 CSV. Read-only production report1/1 PASS352.816s, outer completed/closed378.760551495s, heartbeat errors0. Обе выбранные группы имеют по6 законченных проб и3601 native samples в каждой. Четыре оригинальных PNG2880×2880 просмотрены отдельно; потенциал сомы и actual input overlays читаются, Y scale одинаковая для контролей и обеих показанных групп. Данные не прорежены, X — recorded time minus native probe begin. SI единицы не подтверждены.

Overview и detail здесь оба охватывают0..1.8s: окно измерения занимает всю пробу. Название detail не означает дополнительного увеличения по времени; для анализа формы этих широких пиков показанный масштаб достаточен, анализа отдельных timestep по этим изображениям не заявляется. [Исходные metadata/selection](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/figures/manifest.json), [detail48](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/figures/group-000048-soma-000-detail.png), [detail58](../../../Reports/StructTrain/TimeLearner/N1CoupledBranch-20261113/figures/group-000058-soma-000-detail.png).

[Весь primary](ValidationPlans/M40N1CoupledPrimaryA1-20261113/RESULT.ru.md) сохраняется в Git в literal XZ24.11MB вместе с моделями и receipts; полные SVG/PDF остаются воспроизводимым M40 cache. Новый primary пока не проходил независимый restore. [Итог Train и полная provenance](ValidationPlans/M40N1CoupledBranchTrainA1-20261113/RESULT.ru.md), [report receipts](ValidationPlans/M40N1CoupledReportA1-20261113/RESULT.ru.md).

Следующий отдельно объявленный опыт — [frozen diagnostic8patterns](ValidationPlans/M40N1CoupledFrozenA1-20261113/STATUS.ru.md) фактического остановленного состояния, без template fallback. Исходный threshold100 сначала нужен для измерения waveform/LT response; молчание при нём не является успешной классификацией. Подбор Same-Matrix порога требует последующего реального spiking прогона и не становится independent Test. На момент этого отчёта исход нового frozen опыта ещё не установлен.
