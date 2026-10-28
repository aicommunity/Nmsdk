# PostTune: транзакция кандидата — рабочая реализация

Ветка `stage08/posttune-boundary-transaction` создана от develop; проверенные
prerequisites объединены через --no-ff. Этот подэтап пока не принят в develop.

## Реализованная основа

NativeLearnerGraphCheckpoint в Core/TimeLearner/NativeModelBuilder сохраняет
immutable native snapshots обоих детей: Neuron и DatasetMatrix. Снимок делается
до изменения кандидата. Сохраняются реальный граф, индивидуальные параметры,
heterogeneous C, generator и настройки Dataset. Нейрон при восстановлении
соединяется с новым Generator1, не с возвращаемым старым объектом.

Capture проверяет uniform ready/initialized дерево и возможность безопасной
замены. Restore допускается для того же owner/storage/environment/frequency.
Изменение множества детей owner или внешний listener приводит к rejection.
Сначала оба новых объекта создаются через common native Load/Init, затем
подключаются. Старые объекты не возвращаются в pool до успешной проверки обоих
графов и порядка вычисления. Ошибка attach возвращает текущий speculative graph;
она не выдаёт его за восстановленный source. После устранения ошибки можно
повторить Restore из того же immutable source. Вызывающая сторона обязана
обновить cached child aliases после любого результата.

Здесь нет nested Calculate, перезаписи общих образов, parent C fallback или
распространения ошибок через bool Build/Reset/Calculate. Возвращается отдельный
NativeModelBuildResult. Snapshot не обещает восстановления физической динамики
посреди пробы или старого model time. Это same-storage edit state, не архив
публикуемого научного результата и не training certificate.

## Текущие проверки

Source root `8e7b9e8800d30e88eabd84799f97169cb5acb946`, PulseLib
`436e7020136e18d4ab95a2ac96c684cf8ec96aa4`: запущены normal Elder-1 и ASan M40, attempt s08-boundary-*-a1.
Результаты ожидаются; до окончания jobs не объявляются пройденными.

Десять новых native cases: Classic/Branch × N0/N1 × 2000/20000 Гц и attach failure
для обеих топологий. Изменяются child C, реальный Rs, stimulus amplitude, матрица,
Delay и one-pass policy Dataset. Проверяются возврат исходных значений, Ns=3
для N0, отсутствие продвижения часов и повторный Restore. Полный native Probe
до/после сохраняет первичные CSV/evidence и сравнивает stimulus/soma samples.
В том же запуске выполняются ранее проверенные reconstruction/transient cases.

## Остаток до полной транзакции

Этот graph checkpoint ещё не подключён к production Enter/Finalize/candidate
loop. Следующий шаг — отдельный typed controller/threshold boundary state:
training goal, policy Fixed/Auto/Calibrated thresholds, conversion provenance,
история кандидатов и counters. Он должен захватываться до scaling/mode edits.
После commit/reject требуется новая verification именно конечной модели.
Полная матрица mode/failure/timeout/external stop и реальная проверка выбранного
порога остаются обязательными. Снимок графа не закрывает этап 8.

Independent audit source `c174c98b237cd241fbae1d46850d7cbdc0d0c100` добавляет
проверку всех primary ProbeEvidence/CSV общим production audit_probe и точное
сравнение пар CSV. Запуск анализа ожидает завершения native jobs. Этот source
не подменяет SHA native binary.
