# Контроль Rs на границе потери волн: полный граф обязателен

Контроль относится к двум high-threshold stock Train, остановленным на
невалидном измерении: Classic L=54 и Branch prefix=[15,15,15,1], порог100,
2000 Hz, без LT-мембраны. Исходные данные:
`e5fa71d745119af0d818059f497dd226f4c7c25d`. Это не завершённые обучения и
не результат классификации.

`Scripts/StructTrain/TimeLearner/fixed_geometry_resistance.py` готовит
контрольный холодный ModelSpec по фактическим trained_inputs и всей наблюдаемой
длине кабеля. Проверка выполняется штатным Console preflight, без Calculate.
Одинаковые L/Ns/Rs не считаются достаточным совпадением модели.

```text
audit original stopped primary evidence
prepare cold baseline and explicit shared-bank intervention
bind every prepared file to the plan
run native zero-tick baseline preflight
compare complete semantic graph and actual individual parameters
if baseline differs:
    retain diagnostics; do not run either resistance probe
else:
    run baseline and intervention with common native probe runner
    retain every semantic change for review before causal interpretation
```

Команды пакета:

```text
fixed-geometry-resistance prepare STUDY --output NEW_PREPARED
fixed-geometry-resistance run NEW_PREPARED --runtime-manifest R --output NEW_RUN
```

Plan schema2 связывает hash всех jobs и expected files. Неизвестная схема,
symlink или изменённый файл запрещает выполнение. Вмешательство Branch должно
менять общий физический банк attachment=15, то есть значения всех его
логических владельцев [0,1,2]. Classic меняет один банк input0. Предлагаемое
Rs=69551260.1240013 Ω взято из предыдущего реально измеренного кандидата того
же входа; его прежняя геометрия отличается. Само это значение не доказывает,
что оно исправит потерю волн на новой геометрии.

## Фактическая проверка Elder

Native runtime source `07ff1081f88dd020eafa345c3dc0cf4594a0941c`, PulseLib
`541bf89b9966f63ca5131fa57a31a9ae3f5820ea`, Rdk
`10e9d05aa658dd2203c89bc84ba9166595b50014`. Первичная orchestration
`61b1f3fcc40b8d050445efaeff3a9c8a0a1284aa`; усиление bindings и readers
`07517bcf8cf9436fa3b0161ab7102b83ebf8053d`.

Оба preflight прошли собственную проверку валидности и остались zero-tick.
Индивидуальные L/Ns/Rs совпали с сохранёнными. Полные графы не совпали:

| Топология | Узлы в архиве → cold | Дополнительные ExcSynapse1 |
|---|---|---|
| Classic |306 →309|Dendrite1_1, Dendrite1_2, Dendrite1_3|
| Branch |71 →84|Dendrite1_2 … Dendrite1_14|

В архиве этих банков нет: на соответствующих мембранах
NumExcitatorySynapses=0. После cold construction из исходного storage-профиля
там по одному синапсу и другой child_order/набор связей. NativeModelEditor
удаляет прежние управляемые входные банки при перемещении, а NativeModelBuilder
сохраняет неуправляемые элементы исходного образа. Поэтому ModelSpec с
attachment/Rs не заменяет полный learned graph archive. Это не доказательство
дефекта штатного cold builder или бесполезности исходных исторических моделей.

Защитная проверка сработала: **ни baseline probe, ни Rs intervention не
запущены**. Результат не интерпретируется как эффект сопротивления. Настройки
storage, тип мембраны и допуски не менялись. Следующий необходимый шаг —
восстановить полный stopped-state через существующий native import, затем
проверить точный граф и выполнить физически допустимое изменение банка.
Ручное удаление лишних узлов ради совпадения не заменяет проверенный import.

Четыре readers проверяют реальные preflight manifests и отсутствие проб после
отказа gate, shared-bank ownership, отказ при изменённом повторно подписанном
job и сохранение изменений порядка узлов в диагностике. Для повторной
подготовки schema2 восемь первичных файлов побайтно совпали с первоначальной
подготовкой; native preflight не перезапускались ради изменения bindings.

Proof `2d49e6aba30c271c59309f733777b2d7b9f96436` содержит обе исходные
сжатые группы данных и результаты readers:
[артефакты](../../../Reports/StructTrain/TimeLearner/s07-stock-fixed-geometry-elder-a2/README.ru.md),
[независимая проверка](FixedGeometryResistanceVerification.json).
Научный verdict отсутствует; этапы5–8 и11 этим контролем не завершены.
