# Native Load/XML: воспроизведённые дефекты и кандидаты исправлений

На M40 выполнены все восемь адресных native проверок без новой сборки:
Root `ff42a22d667c072051726ef5dcd9b340db496897`, PulseLib
`60802ab962e1ae8bf091c331f2a2b02642fc9437`, Rdk
`d6c9df759a3ee20ad42fa0a83841f19385fba60a`, Bin
`8cb6dba07b30432272984c8ce3136b48ad06f064`. Итог **4 PASS / 4 FAIL**.
Это отдельная диагностика существующего SDK, не возобновление завершённого
contract17 и не научный эксперимент классификации.

| Проверка | Наблюдение | Изменение |
|---|---|---|
| XML native NPChannel при существующем классе | Архив принят после изменения XML Capacity и корректного пересчёта checksum, хотя declared model identity остался прежним | PulseLib: native LoadSnapshot/readback обязателен также для уже зарегистрированного образа |
| XML derived NPExcChannelBio при существующем классе | Такой же ошибочный приём | Тот же общий путь; prototype не изменяется |
| ConnectedChildAt2000 и ConnectedChildAt20000 | После полной Load и Init/Reset сохраняется старый connected input 0.75 вместо сохранённого локального 0.25; восемь native ticks дают Feedback 1.5 вместо 0.5 | Rdk: отсоединить прежние связи перед присваиванием свойств полной загрузки |
| Fresh и DetachedChild на обеих частотах | Все четыре проверки проходят | Положительные контроли сохранены |

Предыдущие четыре ошибки SDK24 со старым запрещённым generator child были
ошибками fixture до Load. Их нельзя использовать как доказательство дефекта
Rdk. Нынешние ConnectedChild проверки используют допустимый канал мембраны
и действительно достигают Load, Init/Reset и root scheduler.

[Все 41 исходный файл](../../../Reports/StructTrain/TimeLearner/s05-load-xml8-preimage-m40-a1/primary.tar.gz)
сохранены в архиве 110121 bytes, включая оба полных противоречивых архива,
шесть наблюдений Load, исходный JUnit, runtime/source inventories, producer,
native process binding/closure и released lease. Единственная внутренняя
ссылка журнала материализована с сохранением её исходной цели в capture.json.
SHA256 архива и каждого файла проверены
[независимым reader](../../../Reports/StructTrain/TimeLearner/s05-load-xml8-preimage-root-observation/independent-check.json).
Локально выполнена только проверка Git/архива/схемы/JUnit, без моделей и численных тестов.

Native cgroup закрыт, lease released, source-before/source-after идентичны.
Внешний cgroup Python producer отдельно не аттестован; это ограничение явно
сохранено. Evidence commit `015bbf13b7fce872560173b14f0dce5bfd9d6cf4`
опубликован, exact origin ref проверен и принят в maintained root через
`merge --no-ff`. Он содержит только три новых файла доказательств и не
меняет gitlinks maintained root.

Кандидаты исправлений опубликованы отдельно:

- PulseLib `991d933a5a3f6fe1d17986118656be98cda31392`;
- Rdk `de4134235c0dcb8b91fd9a43b267348ad1a163ca`;
- согласованный SDK Root `f39b9ebdcd0e7a64e388d778ca32374a65ae4e0c`.

Они ещё не приняты runtime-проверкой и не объединены в develop.
Новый frozen gate17 сначала проверяет Load/XML8, затем image replay,
реальные waveform transfers/fresh process и пять package roundtrip/warm
сценариев. Исправление изоляции output/log дочернего процесса включено;
старый contract17 сохраняется как отрицательный результат fixture.

Научная постановка, CapturedPerInput, допуски и выбор закреплённого пика
не изменены. Полный119, reader16, Console cold Train→Test/calibration/frozen
evaluation и матрица физических профилей остаются обязательными.
