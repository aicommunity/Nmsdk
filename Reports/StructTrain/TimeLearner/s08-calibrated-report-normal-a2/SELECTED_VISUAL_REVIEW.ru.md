# Выборочная визуальная проверка

Просмотрены в исходном размере 1920×960:

- `primary-bundle/selected/Branch-trial-0-overview.png`;
- `primary-bundle/selected/Branch-trial-2-overview.png`;
- `primary-bundle/selected/Branch-trial-2-spike-zoom.png`;
- `primary-bundle/selected/Classic-trial-2-last-input-zoom.png`.

Подписи, шкалы, синий потенциал сомы и оранжевые реальные входные импульсы
читаемы; заголовок, легенда и оси не перекрываются. Фиолетовый пунктир обозначает
измеренные spike events LT-зоны, а не дополнительный входной импульс.
В zoom различимы форма входного импульса и положение spike event.
Единицы потенциала сохранены как model units, SI не приписаны.

В Branch overview trial 2 начальный потенциал отличен от reset-per-trial trial 0;
первый максимум выше, а spike event находится до второго входного импульса.
Это согласуется с полными метриками: target не имеет spike внутри объявленного
post-last-stimulus окна и имеет outside spike. В reset-per-trial паре criterion
выполнен; суммарно обе модели дают TP=1,FN=1,TN=2,FP=0.

Порядок/позиция и reset policy здесь совместно изменяются. Контроль не отделяет
их причинные эффекты, не является независимым held-out Test и не переоценивает
августовские 4/8–6/8.

Это выборочная проверка четырёх изображений. Остальные изображения и полный
кэш не объявляются просмотренными вручную. Автоматические проверки подтвердили
покрытие 12 trial/soma pairs, native-tick zoom, отсутствие downsampling,
размеры PNG, SVG/PDF и хеши файлов. Флаг `visual_acceptance_complete=false`
сохраняется.
