# Установка recognition-состояния в learner: рабочий подэтап

Ветка `stage08/frozen-recognition-owner`. Новый код ещё не принят и не является
готовым scientific Test runner. Исходный gate: root
`6ff1d43a9af8df7a97111ba04b259aa207454ce0`, PulseLib
`0b9d0ff992238b6f72bc1046d50c5d80fecee6d7`.

## Новый путь

`PrepareNativeRecognitionState` сохраняет не только частные готовые Neuron и
Dataset, но и проверенную исходную конфигурацию и режимы владельца. Для конечного
recognition графа выключено разрешение muted solo baseline: все объявленные
входы должны быть действительно подключены.

`ImportNativeRecognitionState` обоих learner:

1. Требует idle boundary, проверяет overrides, пакет, исходный solo proof,
   topology, conversion и effective graph через существующий native import.
2. До замены детей проверяет совместимость всех зеркалируемых параметров и
   control/threshold fields с внешними источниками Rdk.
3. Устанавливает Neuron/Dataset через общий CommitNativeLearnerChildren,
   зеркалирует подтверждённые значения, сохраняя совпадающие read-only sources.
4. Сохраняет immutable recognition package и отдельный frozen owner state.
   Training service очищается: его certificate/references не переносятся на
   recognition модель. Source solo proof остаётся внутри пакета в своей области.

Физический порог наследуется из проверенного архива и зеркалируется в owner
LTZThreshold/FixedLTZThreshold. CalibratedFixedLTZThreshold=0 и auto-calibration
выключена: новой калибровки не было. Порог не записывается в дочерние каналы
на каждом тике; граф уже содержит проверенную физику.

В frozen ветке обычный scheduler рассчитывает детей один раз. Before/after hooks
проверяют owner metadata, target, объявленный stimulus profile, частоту и
семантический hash реального нейрона через ModelRevisionObserver. Этот observer
читает параметры/связи/порядок/частоту/cache/lifecycle на каждом тике; это не
доверие к собственному edit counter. Несовпадение даёт NativeModelEditFailure.
Ни один helper не вызывает вложенный Calculate.

Build/Init/Reset сохраняют frozen модель; Default завершает этот scope. Begin
training, solo export, training probe и parameter editor не могут неявно
использовать frozen recognition как solo. Выход из scope — явный cold construct
или успешный import solo state. Повторная установка того же recognition package
загружает тот же архив, а не умножает текущие сопротивления заново.

## Проверки

Начальный серверный gate включает восемь новых cases: Classic/Branch N0/N1,
historical Branch N1 scaling/clipping, один вход и шесть общих точек Branch.
Каждый выполняет реальное обучение, экспорт, conversion и установку в learner;
после Build/Init/Reset и повторного импорта сравнивает frozen waveform со вторым
независимо импортированным графом на том же native scheduler. Также проверяются
отсутствие installed certificate, отказ forged recognition certificate, запрет
изменений и обнаружение прямого изменения физики до следующего расчёта детей.
Дополнительно запущены четыре существующих cold training regressions.

Контроль шести входов имеет явно расширенный timing tolerance 1 s и фиксированную
геометрию: это dimensional transport, не сходимость при default 0.02 s. Первые
owner cases имеют 2 кГц; проверки всей частотной/физической матрицы не заявлены.
Два дополнительных configured ControllerVersion=2 controls добавлены в source,
но не входят в исходный native gate 6ff1d43a.

## Что этим не закрывается

Paired waveform проверяет установку и удержание реального графа; `record_spikes`
в этих controls остаётся false, scientific verdict и recognition certificate —
null. Полный runner ещё должен управлять разрешёнными transient presentations
отдельно от training target, регистрировать реальные stimulus/spike timestamps,
проверять полные окна, независимые Test данные и выбранный порог.

Исходная hidden frozen state не является XML/controller checkpoint. Обычный
component Load/Copy не получает права продолжать признанное обучение или Test
без явного versioned import. Runtime external-stop training controls, все
PostTune/C-trim режимы, калибровка и весь исходный план остаются открытыми.
