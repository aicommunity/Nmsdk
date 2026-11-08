# Независимый reader matched omission

`Scripts/StructTrain/TimeLearner/matched_omission_evidence.py` читает новые
fixture group.json и связанные canonical CSV. Он не вызывает C++ и не
использует сохранённые support sets для вычисления результата: независимо
проверяет raw source waveform/events/grid, context, повторяемость full,
измеренные максимумы/плато, influence intervals и выбор версии1.

Область первого выпуска — fixture schema1 с полями policy/maxima, созданный
root58f5b5181/Pulsefcc3fed. Ранние schema1 без этих полей явно отклоняются.
Проверяются неизвестные поля, числа, IDs, requested/actual context, mask,
источник, baseline, окно и полнота CSV. При stop/edit между controls проверяется
сохранённая полная первая проба; assignment не достраивается.

В fixture отсутствуют total budget declarations и самостоятельные OS/instance/
reset attestations. Reader возвращает соответствующие false/unknown, не
придумывает их из успешного числа проб. Raw schema6 и успешная проверка файла
не становятся TrainingCertificate или recognition verdict. Intended presented
ISI hashes по одним quantized timestamps не восстанавливаются.

## Проверка области применимости

Legacy MeasureMaxPotentialAndTime обоих learner ищет собственный пик около
Expected[i]+cable delay и закрывает per-input окно; predictor лишь определяет
область поиска. InitialSomaPotential[i] захватывается из завершённого собственного
окна при unit cable/single synapse. Комментарий о first peak не означает, что
все входы измеряют только pulse0: вызывающий код индексирует Expected[i].

Версия1 matched omission рассматривает все максимумы полной трассы. Поэтому
более поздний shared peak, содержащий остаточный эффект раннего импульса, может
запретить ранний exclusive peak, находящийся в исходном per-input окне. Это
операционная консервативность метода; её нельзя автоматически приравнять к
требованию математической задачи.

`diagnose_declared_window` только сопоставляет уже перепроверенные максимумы с
явно переданной гипотезой окна. Он не меняет verdict/критерий и не создаёт
сертификат. До подключения в NativeTrainingService требуется проверить это
настоящими native данными и историческими контрольными трассами. Нельзя
исправить проблему подстановкой глобального максимума либо ослаблением
старого schema3 validator.

## Проверки

На M40 прошли11 контролируемых Python cases: независимый пересчёт, высокий
shared поздний пик, partial stop, tampered support/selection, потеря/дубли/
extra files, неизвестная schema, changed model/epoch/trial, NaN/Inf, источник,
baseline/event drift, ложная полнота и escaping path. Проверка выполнена на worker, tool root
`fa0c70b7d1e8102e207f6a4852c993615d3a538a`; локально выполнена только проверка
метаданных и hash. Дополнительно reader перепроверил10 реальных native groups
из ASan evidence `9e301ba0b28be4ec64a85ac143ea9db94d6fd884`:
шесть полных назначений пересчитаны независимо от C++, у четырёх остановленных
групп проверена только сохранённая первая полная проба. Новых симуляций не было.

Результаты: два separated controls остаются Valid, четыре coupled controls —
Ambiguous, четыре stop/edit — без assignment. В coupled controls exclusive
первый пик лежит внутри диагностической гипотезы окна [.009,.07] s, а более
высокий shared peak находится снаружи. Это воспроизводит конкретное ограничение
v1, описанное выше; гипотеза окна восстановлена из fixture prototype, а не
зарегистрирована до измерения. Она не разрешает менять результат на Valid.

Evidence commit `515a86c42509c136211d46cc5e021145e804b618`, компактный archive
27 файлов/33 216 bytes. Исходная ASan primary data повторно не копируется:
её commit и hash записаны в primary-git.json. Локальная проверка всех members,
source hashes, original-primary hashes и закрытия lease отражена в
[MatchedOmissionReaderVerification.json](MatchedOmissionReaderVerification.json).
Это проверка reader и границ применимости метода, не завершение Train-интеграции
и не научный результат классификации.
