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

Native observation schema 2 содержит typed StimulusProfile: класс источника,
amplitude, pulse length, frequency Hz, frequency deviation и transit/pattern
режимы. Recorder требует конечный полный профиль, а FinalVerification связывает
его с references и каждой последующей пробой. Native request может задать
ожидаемый профиль; несовпадение отклоняется до предъявления. Внутри пробы профиль
сравнивается по настоящим численным значениям, включая изменения меньше точности
строкового форматирования. Schema 1 сохраняется для прежнего внутреннего контура
и контролируемых сигналов, без выдуманного source profile. Верификация не
смешивает схемы; recognition CSV остаётся отдельной schema 4.

Frequency/Delay генератора принадлежат Dataset playback. Production-сериализатор
условий должен включать typed source profile и фактическое расписание.
Внутренний Rdk string snapshot не является новым научным fingerprint.
Transient stimuli нельзя смешивать с retarget обучающей цели.

ControllerVersion=2, основной bounded search N0/N1, экспорт сертификата и полного
обученного состояния, conversion/PostTune/calibration и новый experiment runner
ещё не реализованы этим изменением. Сам native result не является сертификатом
сходимости или результатом распознавания.

## Промежуточные серверные результаты

Root ad9e54d прошёл 3/3 Rdk lifecycle checks и 4/4 native controls на двух
серверах, включая отклонение Reset при неизменном semantic hash. Root c143fcf
прошёл 16/16 native controls на двух серверах: вмешательства source/pattern,
pooled removal, external stop и реальные/no-op Build. Root 5b72f21 прошёл
28/28 native controls на обоих серверах: N=1/2/4/6, 2000/20000 в объявленных
случаях, реальные отдельные точки Branch, native FinalVerification для N=1
и Classic N=2. N=1 даёт Exact constraint certificate; исходная N=2 модель —
OutsideTolerance по времени при совпадающих raw targets. Это frozen исходные
модели, не завершённое обучение и не распознавание.

Новые schema 2/source-profile, callbacks/UnInit и ускоренный structural inspector
проверяются отдельно от этих снимков. Их незавершённая проверка не закрывается
результатом старой schema 1. Полные SHA, runtime provenance, первичные CSV/JSON,
negative baselines и публикация Git-артефактов обязательны перед merge подэтапа;
пока результаты находятся в серверных readbacks рабочего контура.

Рабочий контроль Branch N=2 расширен: недостающая reference снимается отдельной
native solo-пробой с проверкой фактических связей выбранной точки. Затем verifier
повторно предъявляет каждую точку в своём порядке, с собственной window и ID.
Подстановка одного наблюдения под два input ID запрещена. Primary CSV сохраняются
для дополнительной reference и каждой verification-пробы; JSON остатка содержит
target и measured raw potential. Это расширение ещё требует серверного результата.

В промежуточном a8 два теста OwnerUnInit выявили особенность общего lifecycle:
UContainer вызывает AUnInit напрямую и обходит UModule::BeforeUnInit. Добавление
только ABeforeUnInit в learner не останавливает его probe. Исправление отслеживает
ревизию в прямых Init/UnInit входах UContainer и отменяет probe в публичном UnInit
learner, сохраняя исходный обход hooks и порядок детей. Отдельный Rdk-тест
проверяет этот обход; a9 на обоих серверах проверяет исправление, не меняя общий
контракт Init/UnInit. До результата это не считается runtime-подтверждением.
