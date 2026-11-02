# C-trim: физический baseline и правка ёмкостей

Новая feature от developf1708eb97bc3b412c101dffc468221af2bc87e59.
Pulse исходная точкаa18c8a1097a221e5aca3bfc2c1afc07fb2534a56.
Первая implementation4239b807c37311fe91ca3aae322aab7445795aec.
Серверная приёмка ещё не завершена; develop не меняется до результатов.

Source audit старого C-trim выявил ClassCapacitance из parent MembraneCapacity
и запись scalar DendriteCapacitance[i] одновременно в Exc/Inh каналы всех
выбранных сегментов. Это не сохраняет heterogeneous child physics. Подмена
одной константы другой проблему не решает. Старый режим не переименован в V2.

Новый общий API CaptureNativeCapacitanceBaseline сохраняет actual path→C0
всех каналов с отдельными LT/Soma/Exc/Inh значениями. ApplyNativeCapacitanceScale
работает только на consumed native boundary. Owner guards исключают внешнее
изменение активного Train и frozen recognition. Каждый выбранный dendritic
membrane получает C[path]=C0[path]×scale; повторное применение идемпотентно.
Soma и LT не являются разрешёнными объектами trim. Prototype/parent defaults
не меняются. Нет learner Reset/Build или вложенного Calculate.

Алгоритм физической операции:

```text
validate boundary, ownership, baseline schema/hash/frequency and scales
resolve every selected existing channel and its explicit positive finite C0
clone current physical graph through native snapshot/import
apply candidate C0 * scale independently to actual channels
initialize/reset preview; assess actual native integration equations
capture full predicted semantic identity; dispose preview
verify that live model remained unchanged
apply candidate only if effective C differs; native physical Init/Reset
compare full live identity against preview
on unexpected live failure: restore previous C and verify original identity
```

Неизвестные equations/connected Capacity, отсутствующий channel baseline,
NaN/Inf, bounds, unsafe integration и повреждённый baseline дают явный отказ.
Ни универсальное tau>=2dt, ни fallback1nF не используются. Baseline является
явной декларацией физического исходного состояния; его принадлежность к
profile/ModelSpec и controller persistence ещё не реализованы и не доказаны.

Declared gate8 использует реальные storage/Environment/scheduler fixtures:
Classic/Branch×N0/N1×2000/20000Hz, N0 с двумя tip synapses. Проверяются
heterogeneous Exc/Inh, LT/Soma preservation, scaling/restore, no-reset повтор,
native physical roundtrip, реальные waveform probes, negative candidates и
рост до нового сегмента без baseline. Такой сегмент пока отклоняется.
Численные и интеграционные проверки выполняются только на Elder/M40.

## Оставшаяся интеграция C-trim

1. Связать baseline с immutable ModelSpec/storage profile и сохранить явные
   baseline/correction records в trained state, plan и boundary continuation.
2. Добавить baseline extension после native growth из подтверждённого нового
   storage channel; не переснимать уже trimmed C как новый C0.
3. В общем контроллере реализовать bounded C candidates по свежим timing/amp
   measurements, с исходными targets/tolerances и ограничением поправки.
4. Classic: корректировать выбранный путь. Branch: явный интервал общего кабеля;
   инвалидировать все затронутые observations/certificates и вновь оценить Rs
   domains после C edits. Прогноз задержки не является доказательством пика.
5. Допустить Exact только по fresh all-input pass нового revision; сохранять
   negative/quantized/best-effort/budget reasons раздельно.
6. Проверить Train→export/import→Test, warm continuation, growth/Build/load,
   interruption/rollback и PostTune на поддерживаемых физических профилях.

До этих шагов ControllerVersion2 по-прежнему явно отклоняет optional C-trim.
Этот physical primitive не считается завершением исходных этапов4/5/7/8.
