# Диагностические восемь паттернов на незавершённых stock-моделях

Новый workflow `stock-stopped-evaluation` относится к этапам3/5/9/11.
Он подготовлен для серверной проверки; факт численного выполнения пока не заявлен.
Исходник — четыре реальные остановленные модели из threshold pair A3,
evidence `e5fa71d745119af0d818059f497dd226f4c7c25d`. Не используется исходный
шаблон вместо обучавшейся структуры. Source study повторно проходит production
reader, все четыре исходных пакета и их первичные пробы сохраняются.

Команды из корня checkout:

```
python -m Scripts.StructTrain.TimeLearner stock-stopped-evaluation prepare SOURCE_STUDY --bin-repository BIN_GIT --output NEW_DIRECTORY
python -m Scripts.StructTrain.TimeLearner stock-stopped-evaluation run SOURCE_STUDY --bin-repository BIN_GIT --output NEW_DIRECTORY
python -m Scripts.StructTrain.TimeLearner stock-stopped-evaluation analyze COMPLETED_DIRECTORY --output NEW_ANALYSIS.json
```

`prepare` не запускает физическую модель. `run` требует нового каталога и
проверяет точный исходный runtime перед/после32 native probes. Используется
штатный public diagnostic-evaluate с полным import stopped package, identity
conversion, reset-per-trial и frozen semantic hash. Native scheduler/Reset
не заменяются Python-моделью. Исходный порог0.0117 или100 не подбирается и не
снижается; результат при100 может быть молчанием и сохраняется таким.

Каждая модель получает восемь сохранённых августовских паттернов из точного
Bin commit `1c1464e248f8744e858bd66df0be99e39969fd65` через phasea_matrix.
Окно каждой пробы2 s,2000 Hz, реальное сохранение всех сом и threshold potential.
Это32 пробы /80 trial-soma pairs: по четыре сомы Classic и одной Branch.
Данный reset-per-trial протокол не объявляется воспроизведением исторического
scheduler/ITI. На этом шаге порядок единственный; robustness остаётся отдельно.

Проверяются исходная и конечная физика без LT, полные source packages,
модель до/после evaluation, runtime, все jobs/IDs/observations и отсутствие
сертификата. Любая ошибка/неполное окно запрещает полный diagnostic verdict.
Даже при хороших diagnostic counts поля training_completed=false и
scientific_verdict=null сохраняются. Это не подтверждение сходимости,
независимая Test выборка или причинное сравнение наличия LT.

Пять адресных server readers в tests/test_stock_stopped_evaluation.py:
четыре работают с actual source study и historical Git data; пятый требует
фактического32-trial результата. Skip не засчитывается как успешная проверка.
После выполнения следует сформировать production temporal reports: все
паттерны/сомы, реальные входные импульсы, полный обзор и читаемый zoom.
Компактный Git хранит primary/models/metrics и выбранные изображения;
полный воспроизводимый кэш — M40 Data. Этот документ не закрывает весь этап11.
