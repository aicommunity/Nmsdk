# Возврат к измеренному состоянию: контракт оставшегося исправления

Статус: дополнительная проверка исходников, не реализованное исправление и
не runtime-проверка. Root code d55a32cc7b47fb848a9d09ee443baa1a04db8711,
Pulse c54d9c0a65ac6eadeccfe1793672b7a9472ea559. Развивает пункт 1
[анализа полного cold поиска](LongColdSearchInspection-20261117.ru.md).

## Что подтверждает код

| Путь PulseLib | Фактическая граница |
|---|---|
| Core/TimeLearner/BoundedTraining.cpp, NextAction | При локальном исчерпании выбираются best.fullParameters и восстановленный C map; затем native edit и свежие anchor/input. Проверка пары probe budget предотвращает новый edit при нечётном остатке, но не гарантирует время на измерение. |
| Там же, Stop/ExhaustBudget | Очищаются pending/armed/compositeArmed/anchor; current, revision и фактический граф не возвращаются к best. Поэтому global wall/model deadline после edit действительно может оставить неизмеренный кандидат. |
| Core/TimeLearner/NativeTrainingService.cpp, CheckBudget/Finish | Deadline останавливает поиск и завершает service. Finish не выполняет native edit. |
| Core/TimeLearner/NativeTrainingServiceComposite.cpp, StopComposite/CaptureCompositeInterrupt | Сначала инвалидируется owner-control lifetime, прерывается и архивируется текущая группа, увеличивается generation; затем поиск переводится в terminal. Поздний callback прежнего actor не является разрешением на восстановление. |
| Core/TimeLearner/NativeModelBuilder.cpp, NativeLearnerGraphCheckpoint | Сохраняются полные neuron/Dataset snapshots, owner order, lifetime/context. При Restore создаются новые private children и проверяется graph identity. Owner mirrors, search cursor, references/certificate, epoch и C-control state этим helper не восстанавливаются. |
| Core/TimeLearner/NativeModelEditor.cpp, ApplyNativeInputParametersImpl | Этот же graph checkpoint уже штатно используется для отката неуспешного C edit до принятия его контроллером. После отката обновляются aliases детей и проверяется исходная identity. Это текущая транзакция, а не исторический best. |
| Core/TimeLearner/NativePostTuneBoundary.h | Owner-aware wrapper дополнительно сохраняет owner policy/aliases, проверяет quiet state и требует IsNeedToTrain=false. Он явно отвергает active training и потому не заменяет будущий возврат best во время завершения поиска. |

Следовательно, запрещать graph checkpoint при любом активном service было бы
ошибкой: это сломает уже существующий штатный C-edit rollback. В то же время
простое использование PostTune wrapper либо запись прежних L/Rs/Ns в parent
свойства не решают задачу terminal selection.

## Обязательная реализация этапа 7

1. Выбор best остаётся решением production controller по исходным timing,
   amplitude и cost ranks. Native adapter сохраняет полный физический snapshot
   именно выбранной измеренной границы; связывает его с input/search context,
   reference/protocol, model revision/epoch, полным parameters и C baseline/map.
   Нельзя заново выбирать best в Python по другой формуле.
2. Различать локальное завершение входа, глобальный search budget, deadline,
   invalid observation/model и external stop. Внешний stop не запускает
   последующий поиск или скрытый физический edit. Invalid model нельзя
   автоматически считать восстановленным без readback.
3. Вводится явная стадия завершения с отдельно разрешённой native транзакцией
   на закрытой/отменённой и полностью собранной probe boundary. Уже отозванный
   composite actor не переиспользуется как полномочие новой операции.
4. До любого commit проверить остаток edit budget, owner lifetime, неизменность
   target/profile/frequency и возможность полного восстановления. Пробы и
   итерации не пополнять; расход/пределы операции завершения объявить отдельно
   от уже истёкшего measurement deadline. Нельзя бесконечно восстанавливать
   кандидата, ожидая научного успеха.
5. Восстанавливать native neuron/Dataset, реальные связи/order, storage physics,
   learned Rs/Ns/L/C, owner mirrors и соответствующий C-control readback.
   Обновить все aliases, revision и epoch; удалить применимость устаревших
   domain/measurement/certificate к новому текущему состоянию. Не восстанавливать
   динамику середины пробы или весь старый controller через Copy.
6. Сохранить событие выбора: причина остановки, selected candidate/trials,
   source/restored identities, pre/post epoch, edit charge, результат readback
   и причина отказа. Model export, composite archive replay и summary должны
   описывать одну фактическую модель. Нельзя менять только поля summary.
7. Возврат измеренной точки не делает её Exact: требуется свежая all-input
   проверка одной конечной revision. Если бюджет её не допускает, оставить
   BudgetExhausted/SearchUnresolved с явным состоянием проверки. Branch shared
   cable не переносит прежние локальные certificates на другой общий граф.

## Минимальные проверки до нового научного A/B

- Оба topology: deadline после successful edit, во время anchor, между anchor
  и input, при local cap и при final verification; различать full measured
  candidate, partial candidate и unmeasured terminal state.
- Лучший кандидат имеет другие C, Ns, неоднородные дочерние свойства, extra
  cable и bindings: после возврата совпадает весь semantic graph и отклик,
  а не только три parent vectors. На Branch затронутый общий кабель проверяется
  для всех входов.
- Edit cap/epoch overflow, отсутствующий snapshot, заменённый owner, Reset,
  retarget, sink reentrancy и restore failure дают честную причину. External
  stop сохраняет отсутствие неожиданного edit/restart.
- Старый C-edit failure rollback и stopped PostTune rollback продолжают
  проходить: новый terminal transaction не должен разрушать их границы.
- Новый archive export/import/replay соответствует restored graph и не
  восстанавливает live search authority; старые schema сохраняют свой смысл.
- Затем same-budget cold A/B и actual frozen8 Test, с читаемыми Soma/input
  графиками, publication full primary и разделением execution/training/quality.

Пока эти условия не выполнены, существующие terminal-модели оцениваются как
фактически сохранённые stopped graph. Лучший scalar из истории не подменяет
их модель или Test. Уже запущенные опыты продолжают исходный протокол.
