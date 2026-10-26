# Native executor: рабочая интеграция, приёмка открыта

Код находится в ветках stage07/native-probe-executor корня/PulseLib и
stage07/lifecycle-observation Rdk. В develop этот подэтап ещё не принят.
Последняя принятая closure остаётся 71a1b7f4412a8e769ec487104b7b8b94675f98f0.

## Путь исполнения

QueueNativeProbe ставит относительную ProbeSpec в очередь. Learner BeforeCalculate
проверяет готовность/частоты, фактический Dataset ISI, отсутствие concurrent
legacy PostTune/C-trim edits и поддерживаемый generator-режим. Затем сбрасывает
только Dataset/Neuron, считывает model-defined baseline и применяет временный
Branch solo overlay. Callback onPrepared вызывается до первого native stimulus.
После обычного расчёта children learner ACalculate собирает physical soma samples
и реальные OutputPulseTimes в общий ProbeRecorder. Вложенного Calculate нет.

Legacy Training/Experiment/inference-калибровка не исполняются, пока executor
владеет управлением. Между пробами владение сохраняется; оно не означает Done.
Явный learner Reset/Default освобождает управление. Косвенный Reset из
Build/Init должен отменять пробу и сохранять удержание управления до явного
решения caller. Обёртки сохраняют native порядок и не добавляют Build/Init.
Снятие IsNeedToTrain во время этого управления означает external_stop без
legacy обнуления паттерна/смены порога.

Scoped overlay использует штатные typed property bindings. Persistent UNet link
records не изменяются; перед проверкой base revision восстанавливаются исходные
связи. Checkpoint/export посреди пробы не поддерживается. Result содержит
prepared context, observation, текущий base revision, adapter reasons и
requiresFreshVerification; этот флаг требует отбросить ранее накопленную частичную
верификацию при неизвестном вмешательстве, даже если semantic hash восстановился.

## Проверенная зависимость: Reset без изменения semantic hash

Root 2298736 (полный SHA в manifest) на M40 воспроизводит два failures:
Classic/Branch Neuron.Reset на 0.04 с не меняет model hash, но старый executor
возвращает completed/valid. Два обычных native controls на том же снимке проходят.
Это дефект рабочего executor, не доказательство дефекта общей семантики Reset.

Первый smoke root 6c99881 также проходил 2/2, но использовал ResetToUntrained и
получал coincident L=1 вместо объявленных {2,1}. Этот контроль не доказывал
переключения разных точек Branch. В 2298736 fixture сохраняет явно заданную
начальную морфологию, проверяет наличие Dendrite1_2, выбирает другое подключение
и проверяет различие effective/base hash и восстановление исходного base.
Положительный baseline не подменяет последующие отрицательные controls.

В Rdk добавлен отдельный process-local ObserveLifecycle. Он инвалидируется
до native lifecycle hooks и при уничтожении объекта; математический hash
не меняется из-за этого диагностического токена. UEPtr — слабый указатель.
Executor должен проверять lifetime/текущий live graph перед чтением или
восстановлением узлов, а при недопустимом графе пропускать его дальнейший расчёт.
Штатные Dataset generator resets разрешены отдельно; Reset нейронного поддерева
посреди пробы делает наблюдение непригодным.

## Открытые проверки и ограничения

Нужны адресные отрицательные случаи Reset/Build/UnInit/Copy/deletion, изменения
source/паттерна/параметров, callback errors, отмена и повторная очередь; native
цепочка FinalVerification; размерности 1/2/4/>4, совпадающие attach points и
торможение; полный CTest на обоих серверах и ASan. Требуется отдельное A/B legacy
поведения после hooks/Build/Init wrappers. Пока эти gates не пройдены, API нельзя
выдавать за проверенную версию контроллера 2.

Source parameters проверяются в рамках пробы отдельно от neuron semantic hash;
Frequency/Delay принадлежат Dataset playback. Production-сериализатор условий
должен также связать source physics и фактическое расписание с протоколом между
пробами. Внутренний Rdk string snapshot не является новым научным fingerprint.
Transient stimuli нельзя смешивать с retarget обучающей цели.

ControllerVersion=2, основной bounded search N0/N1, экспорт сертификата и полного
обученного состояния, conversion/PostTune/calibration и новый experiment runner
ещё не реализованы этим изменением. Сам native result не является сертификатом
сходимости или результатом распознавания.
