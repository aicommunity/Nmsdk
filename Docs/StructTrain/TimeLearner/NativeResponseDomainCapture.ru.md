# Связь native callbacks и диагностического анализа областей

Подготовлен `Core/TimeLearner/NativeResponseDomainCapture.h` в PulseLib.
Это read-only sink, без вызовов Calculate, Reset, Build или изменения модели.
Arm принимает actual абсолютную спецификацию после штатной подготовки,
Append — фактические NativeProbeSample, Close — результат после восстановления
native routing. Base revision сравнивается с base, не effective revision.

Адаптер сохраняет отсчёты всех каналов, actual events, stimulus samples,
physical channel paths и prepared context. Пути передаются в порядке реальных
bindings.somas; их независимая проверка остаётся обязанностью model adapter.
Ошибка содержания данных в Arm/Append повреждает capture необратимо: хороший следующий
отсчёт не исправляет пропуск. Повторное закрытие запрещено.

При Close сверяются полный actual spec, prepared context, count и events.
Production ProbeRecorder повторно обрабатывает сохранённые отсчёты: legacy
assignment diagnostics должны воспроизводиться. Полная waveform с прежним
valid=false допускается; неизвестная причина отказа не игнорируется.
После проверки вызывается ResponseDomainAssociation. Его Hypothesis остаётся
диагностической гипотезой и не становится reference/certificate.

Добавлены восемь адресных проверок целостности и четыре native fixtures:
Classic/Branch на 2000/20000 Гц через существующие onPrepared/onSample/result.
Старые fixtures по умолчанию не включают новый sink. Серверная приёмка этого
нового шага ещё не выполнена; unit26 прежнего utility её не заменяет.

Остаётся реализовать portable serializer и независимый reader, расширить
fault/native матрицу и выполнить контролируемый разбор исторических 14 условий.
Не заявляются: проверка причинного происхождения максимума, новый алгоритм
Train, готовность этапа7 или полный объём native bridge.

Review выявил и исправил пробел replay: совпадение complete/valid/reasons не
доказывало совпадение самих измерений. Теперь сравниваются все поля peaks и
burst assignments/waves, включая candidateCount, optional amplitude/time и
plateau. Отдельный негативный fixture меняет амплитуду при прежних valid и
reasons. Первый серверный снимок 8c336ab/aa67b438c не содержит этого усиления;
его результаты нельзя переносить на исправленную версию без нового gate.
