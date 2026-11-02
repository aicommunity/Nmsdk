# Открытое сравнение frozen recognition при смещении времени

Наблюдение, не установленная причинность. Новый normal telemetry gate прошёл
unit9/native20/readers24, но это не доказывает cross-run эквивалентность всем
предшествующим трассам.

Сравнены Git primary:

- B3: `57383f8d93ebf660bd2f80d08ac315a67abe2896`, root58d941c2, Pulse69d463aa.
- A2: `69a1c928eed1f0248790ce1dd9c843b6c7d3bf12`, root1e0988be, Pulsee360b31d.

Оба native-result/native содержат122 соответствующих CSV /44162 строки данных.
Абсолютное время в A2 смещено на +0.1s, максимальный остаток относительно
этой трансляции2.1371793224034263e-15s.119 трасс имеют побайтно одинаковые
stimulus/soma ячейки после исключения колонки времени. В трёх остальные
ячейки различаются; среди1092 отличающихся ячеек есть входные0/1, максимум1:

- Branch N0 recognition_1 `_recognition_roundtrip.csv`;
- Branch N1 configured recognition_8 spiking `_owner_recognition_wave.csv`;
- Classic N0 configured recognition_7 spiking `_owner_recognition_wave.csv`.

В28 соответствующих standalone *_evidence.json нечисловых различий не найдено;
числовые различия находятся в абсолютных timestamps и производных временных
разностях. Это не сравнение всех embedded training packets.

Новый NativeArchiveTelemetry выполняет реальный Waveform, оставляющий model
time0.1s перед следующими fixtures. Paired recognition loops в
Test_PulseLib_NativeModelEditor.cpp запускают оба dataset через StateGeneration1
и читают реальные NPulseGeneratorTransit.Output. Внутри каждого прогона paired
graphs совпадают. Между прогонами изменились и serializer, и prelude/clock;
причинность требует отдельного вмешательства. Нельзя считать это доказанной
регрессией serialization либо убрать расхождение округлением soma.

Следующий контроль: на неизменном A2 runtime выполнить прежний native14 без
archive prelude, с отдельными runtime/result manifests и полной публикацией.
Сравнить все входы и soma, реальные stimulus timestamps, absolute/relative
clock и model revisions с A2 и B3. Затем изолировать origin0/0.1/ITI через
штатное время Environment, сохраняя native scheduler и reset policy. Только
после source review NPulseGeneratorTransit/NDatasetMatrix выбирать исправление
у владельца. Не менять обученную физику, target или tolerance для совпадения.

Нынешние результаты приёмки переноса сохраняются в своём протоколе. Этот
открытый контроль относится также к обязательной robustness/порядок/ITI матрице;
он не отменяет визуально подтверждённые августовские4/8–6/8.
