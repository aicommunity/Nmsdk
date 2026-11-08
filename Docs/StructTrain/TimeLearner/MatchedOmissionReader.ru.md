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

Подготовлены11 контролируемых Python cases: независимый пересчёт, высокий
shared поздний пик, partial stop, tampered support/selection, потеря/дубли/
extra files, неизвестная schema, changed model/epoch/trial, NaN/Inf, источник,
baseline/event drift, ложная полнота и escaping path. На момент подготовки
численные тесты и анализ ещё не запускались. Они выполняются только на workers.
