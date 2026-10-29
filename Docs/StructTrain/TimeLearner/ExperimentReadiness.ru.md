# Переход к контролируемым экспериментам на моделях

29.10.2026. Полная цель этапов 0–12 сохраняется. Ниже — приоритетный сквозной
контур для первой ограниченной серии; он не заменяет оставшуюся часть плана.

Нативное cold обучение, измерения, bounded search и экспорт solo-состояния
уже выполняются на настоящих компонентах. Полный принятый gate c7266dcb:
на каждом worker 491 cases / 480 pass / 11 helper skips и 114 independent Python
tests. Новый guard 0ca75b3 прошёл адресный gate на обоих workers: 46/46 native
и 2/2 Python; дополнительный Python audit связывает pre-edit readback с
первичной boundary пробой. Это integration evidence, не результат selectivity.

## Четыре обязательных блока перед первой серией

| Блок | Уже есть | Оставшееся условие допуска |
|---|---|---|
| Конечная recognition модель | Solo export/import, immutable conversion, frozen owner и новый Test learner/fresh-process transport проверены на обоих workers | Расширить проверенную пару Classic N0 / Branch N1 на объявленную матрицу первой серии; сохранить контроль effective graph и model hash в runner |
| Полное предъявление и наблюдение | Native training probe и строгий аудит training JSON/CSV | Отдельный frozen recognition runner: все входы, полный pattern, real spike timestamps/count, onset, label/ID, полное окно и censoring; silent response остаётся валидным отрицательным результатом |
| Порог и управление | Разделение статусов обучения; фиксированные настройки порога legacy; проверенные model boundaries | Реальный прогон выбранного порога, зафиксированные calibration protocol/data; проверка связанного внешнего IsNeedToTrain; frozen Test не меняет модель, target и порог |
| Сквозной запуск | Immutable runtime manifests, Git closure, ConditionSpec; inventory/analyze CLI | Воспроизводимый job, связывающий Train → actual export → calibration → Test → strict analysis → Git artifacts; никакого шаблонного Test после неудачного переноса |

Каждый блок закрывается реальными контрольными случаями и опубликованными
первичными данными. Потеря узла/связи/индивидуального параметра, неполная проба,
подмена target, изменение frozen hash или недоступные артефакты запрещают PASS.
В данных раздельно хранятся execution, validity, training, calibration и evaluation.

В текущем коде `NativeProbe` не принимает `recordSpikes=true`: он предназначен
для измерений обучения. `PrepareNativeRecognitionState` готовит граф, но ещё
не является сквозным production recognition runner. `BeginNativeTraining`
явно отклоняет включённые C-trim и PostTune/calibration. CLI сейчас имеет
`inventory` и `analyze`; наличие библиотечных классов не означает готовность
всех planned train/evaluate/publish команд.

## Начальная область допуска

Первую серию ограничить объявленными и прошедшими проверки ModelSpec/storage
профилями Classic/Branch и N0/N1, с C-trim и PostTune выключенными. Это не
обещание сходимости/8 из 8: exact, quantized, best-effort, unresolved и invalid
должны честно разделяться. Недопустимо молча отключать запрошенную опцию:
capability preflight обязан отвергнуть неподдерживаемый case до дорогого Train.

Для старта ограниченной серии не требуется закончить полную миграцию старых
инструментов, все удобства очереди и все исторические документы. Требуются
работающий сквозной путь, ограничения ресурсов, сохранность данных и точная
Git provenance именно этого запуска. Полный scheduler/publisher и остальные
CLI команды продолжают оставаться deliverables этапов 9/10.

## Последовательность научных проверок

1. Saved-state replay августа в исходном порядке, ITI, пороге и reset policy
   на согласованном историческом source snapshot. Если часть provenance
   неизвестна, это отмечается явно; certificate обучения не достраивается.
2. Cold retrain в тех же объявленных условиях, с отдельной маркировкой source
   и новой реализации. Сравнение legacy/v2 сохраняет CapturedPerInput.
3. Frozen evaluation с target в каждой позиции и изменениями ITI; reset-per-trial
   и continuous stream исследуются отдельно.
4. Расширение физических профилей, торможения, PostTune и optional C-trim после
   реализации и приёмки соответствующих режимов.

Августовские визуальные 4/8–6/8 остаются рабочими наблюдениями своего протокола.
Проверка другого порядка/ITI является новой проверкой зависимости от протокола.
Серия D автоматически не возобновляется. Глобальная рекомендация V2 требует
всей обязательной матрицы исходного плана, а не только первой ограниченной серии.

## Обновление после owner gates

Import/hold внутри learner прошёл адресные native/independent gates на обоих
workers (подробности в FrozenRecognitionOwner.ru.md). После первоначальной
проверки training owner проверены также новый Test owner и fresh process.
Scoped implementation объединена в develop; root f00989cb1 записывает
PulseLib merge 9902545. Остальные три блока и полный исходный план сохраняются.

Новый destination/fresh-process owner для Classic N0 и Branch N1 теперь
проверен на обоих workers; детали и исходные данные — FrozenRecognitionOwner.ru.md.
Это scoped transfer acceptance, а не вся первая строка physical matrix.
Приоритет следующего шага: реальные spikes, transient foils и frozen windows.
