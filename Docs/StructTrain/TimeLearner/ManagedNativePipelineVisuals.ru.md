# Frozen Test после managed Train: реальные временные графики

[Открыть выбранные графики всех объявленных проб](../../../Reports/StructTrain/TimeLearner/s10-managed-native-pipeline-visual-a2/index.html).

Реальный M40 plotting gate прошёл1/1 без failures/errors/skips. Для четырёх моделей Classic/Branch × ModelSpec1/2 N1 построены все четыре объявленные frozen пробы каждого случая:24 пары «проба–сома»,360 PNG-видов с соответствующими SVG/PDF, включая временные/амплитудные увеличения и последовательности проб. Every-native-tick данные сохраняются;1920×960 и минимум8 пикселей на шаг на увеличениях. Входные импульсы наложены на фактический SumPotential всех объявленных сом. Независимые вычисления модели не запускались.

Полные1136 файлов,67 671 061B, остаются воспроизводимым кэшем на Data M40:
`/media/user/Data/TimeLearnerRefactor/readbacks/s10-managed-native-pipeline-visual-a2/full-report-cache`.
В Git —30 выбранных PNG: overview каждой из24 пар и первые temporal zoom для всех6 каналов четырёх моделей. Полные SVG/PDF, все увеличения и повторные копии primary в корневой Git не переносятся. Сжатые исходные данные остаются в отдельном proof `28f7d2fe6f59232f19b33e5b24f4d4011eddfffb`.

Proof графиков `9ddb86b94898da72d8d4e0c84522c5f497de405e`, renderer/test source `821ea680c48bb6eff43fcc3b1d61f5c3d33cce07`. Все опубликованные файлы сверены по SHA256; [receipt и scope](ManagedNativePipelineVisualVerification.json). Вручную просмотрены8 изображений: target overview/zoom всех четырёх случаев и foil overview всех четырёх случаев, включая Soma2 Classic. Подписи, оси и наложенные импульсы читаемы; просмотр всего кэша не заявляется, исходный `visual_acceptance_complete=false` сохраняется.

## Результат и его интерпретация

Во всех четырёх случаях validity=valid, effective threshold=1.0, TP=0,FP=0,FN=2,TN=2. Целевые пробы также молчат: это отрицательная классификация при сохранённом фиксированном пороге. Рефакторинговые проверки подтверждают настоящий Exact Train, полный перенос и неизменность frozen модели, но не успешное распознавание. Порог в этом transfer gate не калибровался. Из такого сравнения нельзя заключить причинную роль инерции LT-мембраны; парного LT/no-LT вмешательства нет. Это двухвходовый engineering профиль, не новая оценка августовской четырёхвходовой модели или independent Test.

Первый plotting запуск полностью построил данные, но тест ошибочно ожидал12 вместо24 пар. Неудачный результат, журналы и закрытие группы сохранены в verification.tar.xz. Во второй версии тест сверяет идентификаторы всех четырёх declared trials и24 пары; renderer и первичные данные не менялись, полный комплект построен заново. Никакие missing observations не дополнялись.

## Воспроизведение

Восстановить a3/primary.tar.xz и проверить bundle.json из primary proof. Для каждого положительного случая использовать код указанного renderer source и Python с matplotlib/Pillow:

```text
python3 -m Scripts.StructTrain.TimeLearner report ACTUAL_RUN/run-manifest.json --format pipeline-run --output NEW_REPORT
```

ACTUAL_RUN — `actual-controls/CASE/runs/evaluate` из распакованного primary; CASE — Classic-v1,Classic-v2,Branch-v1,Branch-v2. Output — новый каталог за пределами primary. Для полноты и масштаба предусмотрен серверный test_managed_native_pipeline_reports с этими реальными источниками.
