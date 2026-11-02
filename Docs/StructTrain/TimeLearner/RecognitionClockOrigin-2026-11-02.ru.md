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

Контроль без prelude на том же неизменном A2 runtime завершён:
`5c430f4d3f86f1bc6fc46515716c0c7f654b0d95`, unit9/native14/readers24, exit0.
Все454 members и3 584 662 compressed bytes проверены. Все122 CSV и28
standalone *_evidence.json побайтно равны B3, включая абсолютные timestamps.
Тем самым отличие serializer не изменило эти отклики; расхождение появляется
при добавлении prelude. Для выделения именно clock-origin из остальных
эффектов prelude ниже добавлена адресная матрица с явными тремя origins.
Первый запуск контроля A1 не дошёл до native tests: в запускателе был неверный
import verify_runtime. Его negative evidence8d049b14 сохранён отдельно;
правильный владелец функции — process_runner, использованный A2.

## Адресная baseline матрица dataset

В отдельной ветке dataset-clock добавлены12 реальных компонентных проверок:
2000/20000 Гц × timed/continuous × Delay0/5/30ms. Каждый case строит dataset,
генератор и физический нейрон штатно через storage/Environment, подключает
реальный синапс и записывает полные0.25s input/soma traces при origin0/0.1/1s.
Проверяются применение origin в микросекундах UTimeControl, частотная сетка,
отсутствие native failures, неизменность модели, повторные реальные импульсы
и ненулевая реакция сомы. Ожидание — одинаковые реальные input/soma samples
при переносе начала времени; ни пороги, ни физика для совпадения не меняются.
Spec `native-dataset-clock-v1.json`. Это baseline до изменения алгоритма
dataset; серверная проверка нужна, исход заранее не объявляется PASS.

Source review: NDatasetBase::UpdateSpikeTrainPlayback уже допускает1e-12 при
onset/repeat, но использует строгий now<OneShotEndTime для завершения pulse.
TimeGeneration также сравнивается без roundoff guard. Сначала воспроизвести
риск на production-компонентах. Не приписывать наблюдение NPulseGenerator
или этой конкретной ветке сравнения до подтверждающего вмешательства.

Baseline A3 завершил полную матрицу36 recordings:8/12 invariance cases прошли,
4/12 без паузы (оба режима и обе частоты) обнаружили различающиеся реальные
входы и soma. Evidence `43343cbad7fd293a4e42b333534b090543b7a1c5`, numerical
root `e966ca52f01eac845eb4efd20620aa31488577e1`, Pulse Coree360b31d.
Первые A1/A2 versions fixture не доказывали clock bug: A1 не собрался из-за
ожидания bool от void DelComponent; A2 остановился после первого origin из-за
неверного порядка освобождения. Native Free сам разрывает owner и возвращает
объект в storage. A3 сначала отсоединяет оба объекта, затем Free ровно один раз.

Кандидат исправления PulseLib `bf6bdf6164d152f6272a5d80a5ee632961a2ace6`:
сначала вычесть integer microsecond clocks Rdk, затем перевести elapsed в
секунды. Есть отдельные anchors для sample, активного pulse и timed session.
Onset/end/repeat используют согласованный guard относительной арифметики с
прежним floor1e-12. Внешний override OperatingTime сохраняет compatibility
seconds interpretation. Детальный контракт — PulseLib
`Docs/Analysis/DatasetClockPlayback.ru.md`. Нужны normal/ASan, расширение
origins/near-grid/cutoff и regression переноса: это ещё не принятый fix.

Расширение тестов сохраняет исходные12 cases и добавляет8 с origins
0/0.1/1/86400/1e9s. Проверяются обычный repeat, onset на10ns позже grid point
(нельзя предъявить раньше) и timed cutoff точно на первом onset. Все реальные
input/soma samples по-прежнему сравниваются без допуска; допуск машинного
округления применяется только к проверке double-представления абсолютных
timestamps. Native clock Rdk остаётся целочисленным microseconds. Spec
`native-dataset-clock-extended-v1.json`:20 cases,76 полных recordings. Новые
проверки ещё требуют серверного выполнения; они не были частью baseline A3.
