# Неизменяемая граница Train → finalization: runtime-приёмка ожидается

NativeFinalizationBoundary хранит значения, а не ссылки на owner/storage или
checkpoint динамики. CaptureNativeFinalizationBoundary читает настоящий экспорт
Solo, исходные phase parameters и фактические связи параметров (путь provider,
имя свойства, порядок sources, connected/external kind). Getter не пишет во
внешний источник и не вызывает Build/Init/Reset/Calculate.

Допустима только ready/initialized Solo-модель с Finished training service и
полностью освобождённой границей probe: ни queued/running, ни непотреблённого
результата/физического routing state. NativeProbeOwnsControl сам по себе этого
не доказывает; новый IsNativeProbeAtEditBoundary учитывает состояние executor.
Lifecycle всех живых descendants, session/epoch/outcome и значения/связи controls сравниваются до и
после экспорта. Исходный training outcome/certificate сохраняется без повышения.

Stopped package по умолчанию отвергается; явный allowDiagnostic сохраняет
его как diagnostic_only с null certificate. Это не разрешение conversion или
продолжения обучения посреди пробы. Class value не содержит Rdk pointers и
должен переживать recognition import, Reset/Default и teardown реального owner.

В частности, независимо сохраняются AutoCalibrate, PostTune, Mid и silent
probe threshold; foil count не превращается в бюджет weight candidates.
Legacy Branch parallel-peak path отмечается отдельно даже при AutoCalibrate=false.
Public mode enums переводятся явным switch: legacy CanonRmin=1 и KeepDone=3
не совпадают с порядком NativePostTuneControllerMode. Неактивные параметры
сохраняются как декларация; неизвестный используемый enum отвергается.

Реальный InstallNativeRecognitionState не просто очищает NativeConfiguredPlan:
он заменяет его восстановленной cold configuration из Solo. Training service
заменяется пустым, а VisitNativeRecognitionControls зеркалирует Need/PostTune/
AutoCalibrate=false. Поэтому исходная phase declaration не восстанавливается из
последующих live mirrors. Внешний stop через connected property нельзя получить
проверкой setter: UProperty может пропустить setter при равенстве значения либо
получать значение из provider. Это требование к будущему phase dispatcher.

Здесь реализован только захват независимой границы. Он ещё не установлен в
Calculate/Reset hooks, не снимает guards optional modes и не заявляет поддержку
target-reference/parallel-peak/mid dispatch. Родительскую модель следует Init/Reset
до импорта завершённого learner: последующий явный parent Reset штатно сбрасывает
контроллер. Не добавлять обходные «будящие» Build/Reset ради сохранения checkpoint.

Приёмка: реальные Classic/Branch source packages, source bindings, queued probe,
external stop и распознавание полного объявленного набора после import; неизменность
снимка после Default/teardown; отсутствие зависимости от порядка public enums.


## Проверяемая последовательность

1. Штатно инициализировать/reset cold parent, затем импортировать полный Solo.
2. Выполнить штатные owner Build/Init и проверить Finished / свободную probe boundary.
3. Захватить immutable boundary; проверить неизменность lifecycle, модели, controls,
   provider values и глобального model clock.
4. Выполнить полный recognition import. Его transient controls и service могут
   измениться; frozen original declaration и training outcome не меняются.
5. Предъявить все объявленные target/foil patterns штатным scheduler, сохранить
   реальные наблюдения; проверить recognition revision и исходный frozen hash.
6. После Default/teardown owner читать только значения frozen document. Нельзя
   выполнять rollback/import или обращаться к уничтоженному owner из snapshot.

Девять native tests охватывают Classic/Branch × Snapshot, ConnectedRequest,
QueuedProbe, ExternalStop плюс явное сопоставление всех public PostTune enums.
Connected true request штатно блокирует импорт, требующий Need=false, без записи
в provider и подмены графа. После внешнего снятия запроса полный import разрешён;
снимок исходного true/connected остаётся. Stopped snapshot разрешён только с
явным diagnostic opt-in и не получает certificate. Это API захвата, не phase
scheduler и не рекомендация включать ранее неподдерживаемые optional modes.


Снимок фиксирует finalization intent именно в момент Capture, а не историю
изменения параметров во время Train. Будущий dispatcher должен отдельно
замораживать декларацию при Start и различать собственные переходы controls.
Нельзя поднимать IsNeedToTrain после восстановления Finished ради тестового
снимка: для ControllerVersion=2 это штатный запрос новой сессии/ResetControl.
Connected provider может иметь true без вызова setter; этот реальный случай
проверяется отдельно. Принимается фактический request value, а не желаемый.
