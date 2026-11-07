# Storage-профили обратной связи: адресная normal-проверка

Подэтапы4/7 исходного плана. Статус: код и реальные integration fixtures
подготовлены и прошли адресную normal-проверку на M40; ASan и второй сервер открыты.

MembraneProfile.feedbackGain необязателен: отсутствие сохраняет значение
базового образа, явный конечный gain>=0 задаётся при создании immutable образа.
Body и LT membrane имеют независимые рецепты. Частота задаётся до финального
построения. Новые сегменты получают профиль штатно через storage; научная
цель CapturedPerInput, referenceN−1, SyncTolerance и амплитудные допуски сохранены.

Проверки используют actual storage/Environment и native scheduler:

* inherited custom gain3.5 и сохранность исходного образа/живого экземпляра;
* body0/LT0.75 при росте, Build/Reset и XML, с сохранением обученных Rs/C;
* NaN/Inf/negative до публикации зависимостей и коллизия одного имени с другим gain;
* Classic/Branch,2000/20000Гц: реальный Feedback и LT timestamps при одном импульсе,
  равенство inherited/explicit2 и отличие response для explicit0.

Для динамических fixtures явно используется инженерный порог1e-6, одинаковый
во всех трёх сравниваемых вариантах. Это другой профиль, чем опубликованные
stock0.0117 models. До вмешательства в них требуется baseline reconstruction
всего эффективного профиля: поля рецепта C/Rm/kinetics/averaging задаются явно
и могут отличаться от физики исходного образа. Одного совпадения FeedbackGain
или имени нейрона недостаточно. Индивидуальные обученные параметры и связи
переносятся через полный native state/import и проверяются по actual graph.

Операция не меняет prototype во время работы экземпляров и не добавляет
поправляющие записи в Calculate. Общий lifecycle Rdk сохраняется. Старые
конфигурации не получают автоматически новые физические значения. Полная
матрица физики, general storage reuse, причинный разбор и assignment остаются
открытыми до фактической приёмки соответствующих проверок.


Legacy learner Reset штатно применяет TrainingLTZThreshold либо
FixedLTZThreshold. Поэтому engineering fixture задаёт оба owner-параметра
равными объявленному порогу до построения и проверяет effective LT threshold
после Init/Reset. Порог не восстанавливается скрытой записью на каждом тике;
различается только объявленный gain. Это учитывает штатное владение калибровкой.


Адресная normal-проверка на M40 завершена: [точный job и handle](StorageFeedbackProfilesJobs.json),
[сверенная приёмка](StorageFeedbackProfilesNormalVerification.json). Rootb54330482/Pulsed09613c:
18/18 native функций за95.934с и13/13 readers без skips. Все161 members
сжатого primary365876B и781 source hashes сверены с Git. Проверены12 actual
feedback control packets. Группа процессов полностью закрыта, lease released;
оба прежних runtime сохранили записанные byte hashes. Primary commit
080d21dcff3940df3ce72bf4a21d1c0ceb003e26.

Inherited/explicit2 дали одинаковые sample arrays и LT timestamps; explicit0
имел нулевой фактический Feedback при существующих LT events и отличающийся
отклик. Это подтверждает чувствительность инженерного контроля, не механизм
дополнительных пиков stock-модели. Её коэффициенты и waveform не менялись.
Уже работающий ASan другого SDK использует отдельные source/build и не
подтверждает этот профиль; второй сервер и полная матрица также открыты.
