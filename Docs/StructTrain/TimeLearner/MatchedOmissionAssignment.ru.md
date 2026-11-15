# Matched omission: первый production алгоритмический блок

Добавлены PulseLib `Core/TimeLearner/MatchedOmissionAssignment.h/.cpp` и
детерминированные C++ cases
`Tests/Integration/Libraries/Test_PulseLib_MatchedOmissionAssignment.cpp`.
Точный контракт находится в PulseLib
`Docs/TimeLearner/MatchedOmissionAssignment.ru.md`.

Чистый selector использует настоящие максимумы полной пачки и bounded
группу `fullBefore → omit-each-original-input → fullAfter`. Измеряемая
величина берётся из full potential; omission differences устанавливают
операционную поддержку, не подменяют потенциал и не раскладывают нелинейную
пачку на линейные слагаемые. Отсутствие response peaks посторонних импульсов
не является причиной отказа. Shared/unknown support возможного высшего
assigned максимума остаётся Ambiguous.

Контекст связывает физические каналы, actual Branch selector, source physics,
исходный target, model/base/effective revisions, epoch, native instance/reset
binding и восстановление полного предъявления. Проверяются actual event
ordinals/frame indices, source waveform, сетка и полное покрытие samples,
baseline, отдельная full repeatability и все burst/sample budgets.
Явный timeComparisonTolerance допускает roundoff абсолютных часов и строго
меньше половины tick; никакой сдвиг на tick или интерполяция не разрешены.
Допуски influence/repeatability не берутся из train amplitude/sync tolerances.

Это новый метод `matched-omission-assigned-maximum-v1`. Он не меняет смысл
ProbeRecorder schemas1–6, не превращает старые window/domain diagnostics в
сертификат и сам не создаёт `TrainingCertificate`. Для N1 возвращается
Unsupported с указанием существующего SingleImpulse пути.

## Проверки и границы этапа

Отдельный target `Test_PulseLib_MatchedOmissionAssignment` компилирует тот же
production selector и `MeasuredResponse.cpp`; его cases также включены в
полный `Test_PulseLib_StorageComponents` target. Покрываются actual full
maximum против global/difference maximum, delayed-prior counterexample,
отсутствующие посторонние отклики, minor extrema, shared/unknown/nonlinear
support, ties/plateau/clipping, retained actual timestamps, источник,
model/reset/baseline changes, nonfinite/gaps/budgets и повторяемость.

Во время реализации локальные сборки и численные тесты не выполнялись.
Проверка diff и статическое чтение не являются C++ PASS. Нужны серверные
normal/ASan unit gates и затем production native composite integration:
bounded N+2 FSM, реальные закрытые packet/trace witnesses, controls restore,
reference/search/final-verification transport и отдельная версионированная
certificate/reader проверка. Научная сходимость или избирательность этим
блоком не заявляется; весь план остаётся открытым.


## Native measurement group

`NativeMatchedOmissionGroup` подготовлен для выполненияN+2 штатных проб без
вложенного Calculate и edits между контролями. Native weak/lifecycle handles
проверяют сохранность экземпляров; фактические target pattern/classes readback
проверяются после восстановления каждой пробы. Raw callbacks проходят
production CloseNative/replay отдельно от прежней domain hypothesis.

[Адресные серверные задания](MatchedOmissionJobs.json):35 unit cases,2 boundary
checks,10 прежних capture/codec controls и8 реальных групп Classic/Branch на
2000/20000 Гц, включая stop/edit между контролями. Первая компиляция отклонена
из-за неправильного преобразования const UEPtr; исправление отдельно сохранено,
повторная попытка ещё не принята. Локально численные тесты не запускались.

Группа пока не подключена к NativeTrainingService, CapturedReferences, поиску
и FinalVerification. Старый schema3 validator не ослаблен. Для рабочего нового
Train требуются versioned composite proof, сохранение/replay и интеграция
операционной assignment policy. Это следующий блок работы, а не закрытый этап7.


## Проверенный normal срез

Elder завершил55/55 проверок без skipped:35 unit,2 CloseNative boundary,
10 прежних capture/codec и8 native measurement-group случаев. Все386 членов
архива,23 source bindings, исходные JUnit IDs, loaded executable, неизменность
обоих runtime и закрытие/lease проверены независимо:
[квитанция](MatchedOmissionNormalVerification.json),
evidence `f2802e7f23043391100d0ec85b8ea1c063d47a12`.
Compiled root9e5249421 / PulseLibfcc3fed. Это normal-проверка, не ASan.

Четыре связанные N2 реакции Classic/Branch на2000/20000 Гц дали Ambiguous.
Четыре stop/edit controls не выдали assignment и остановились после первой
пробы. Всего20 настоящих native bursts; четыре полные группы сохраняют16 CSV.
В данном срезе первая завершённая трасса stop/edit controls не экспортировалась
в CSV, хотя native packet сохранён. Artifact follow-up исправляет это,
записывает причины/support sets и добавляет два separated positive controls.
Не переносить на follow-up приёмку только по сходству исходников.

Independent Python replay нового assignment ещё отсутствует. Связанные N2
контроли не являются обученными моделями, не опровергают августовские наблюдения
и не подтверждают классификацию. NativeTrainingService/final proof integration
остаётся следующим обязательным [блоком](MatchedOmissionTrainingIntegration.ru.md).


## Native controls с полными диагностическими полями

Follow-up10/10 на Elder принят по [независимой квитанции](MatchedOmissionNativeControlsVerification.json),
evidence `ffe14543d9055c8c52b1e614b172e8077463ff40`, compiled root58f5b5181 /
PulseLibfcc3fed. Все396 членов архива,23 source bindings, исходные IDs,
loaded executable, runtime freeze и закрытие обеих групп подтверждены.
Сохранён предшествующий disk-preflight refusal без запуска сборки/тестов.

Два новых N2 positive controls (Classic/Branch,2000 Гц, второй межимпульсный интервал внутри пачки0.5s)
дали Valid assignment реального full-максимума. Четыре прежних coupled controls
на2000/20000 Гц явно проверяют Ambiguous. Четыре stop/edit controls не выдали
assignment. Всего28 native bursts/CSV; первая завершённая трасса stop/edit
также сохранена. JSON фиксирует policy, support sets, причины и выбранную
вершину; первичные кривые не заменены только derived summary.

Это10 повторных/дополнительных native cases, не ещё10 новых math cases:
normal55 и follow-up10 вместе покрывают57 разных tests данного среза.
Численные вычисления выполнялись только на серверах; локальная сверка —
Git/hash/metadata/JUnit. Independent Python recomputation, графики этих новых
групп, ASan57 и подключение к обучению остаются открытыми. Valid assignment
контрольного пика не означает Exact Train или успешную классификацию.


## ASan нового блока

M40 прошёл57/57 в одном compiled срезе root58f5b5181/Pulsefcc3fed:
35 unit,2 boundary,10 capture/codec regression и10 native group tests.
Сохранены28 raw CSV. Оба separated controls дали Valid, четыре coupled —
Ambiguous, четыре stop/edit — без assignment. [Независимая квитанция](MatchedOmissionAsanVerification.json),
evidence `9e301ba0b28be4ec64a85ac143ea9db94d6fd884`:460 проверенных членов,
23 source bindings, actual libasan/executable, исходные JUnit IDs,
неизменность двух runtime и закрытие/lease. Leak detection отключён.

Это приёмка selector/native-group блока на данной матрице, не полный этап7:
не проверены все размерности/физические профили, independent Python replay,
новые временные графики и полный training proof path. В частности, правило
full-trace support может консервативно отклонять более поздний shared отклик
из-за остаточного влияния предыдущего импульса. До включения в Train необходимо
сопоставить его область применимости с исходными assigned-impulse windows и
историческими контрольными трассами; не выдавать разделённый toy control за
подтверждение всей постановки и не подменять выбранный assigned пик максимумом
полной пачки. Переход к references/search/final certificate остаётся явным
интеграционным изменением с собственной проверкой.
