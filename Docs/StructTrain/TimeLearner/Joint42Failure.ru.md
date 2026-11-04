# Первый совместный normal gate:34 passed,8 failed

Источник: root `9f92a40b97b5868b84b156e38b91903e6b0d8176`,
Pulse `cc97149c90ce98ff24ca688452f4a40d54e0e63d`, Rdk10e9d05a/Bin99f58da.
Это отдельный joint-кандидат, не принятый в develop алгоритмический срез.

Все42 native test cases завершились и дали полную JUnit inventory.34 passed,
8 failed; каждый отказ — единственный `observedSpikes > 0` в frozen helper.
Отказы относятся к Classic/Branch × N0/N1 × C Off/On ModelSpec2 boundary cases.
Фактическая декларация и сохранённый LTZone имеют threshold100. В32 отдельных
trials проверены valid/complete/uncensored, отсутствие spikes и неизменность
model-before/model-after. Это восемь двухвходовых engineering LT-моделей,
включая реальную LTMembrane; они не подменяют stock August4-input наблюдения.

Общий helper использовал legacy suffix `_spiking`, добавленный для любого
initialThreshold!=1, чтобы потребовать spike. Имя файла ошибочно стало физическим
критерием. Молчание high100 не является успешной детекцией либо доказательством
плохой обучаемости.32 observations не объединяются в научный accuracy разных
моделей. Исходный failed JUnit сохранён и не объявляется прошедшим задним числом.

Proof `3f3a5627647450716cef6bec41b45347cbc7c7d7` содержит полный сжатый primary,
исходный bundle, diagnosis и worker closure. Независимый
[receipt](Joint42FailureVerification.json) сверяет1205 members,510 source blobs,
42 JUnit cases, восемь effective threshold values,32 frozen observations,
закрытие группы и released resources. Primary5726784 bytes. Parent публикации
— принятый inventory branch, а не unaccepted joint root: перенос evidence
в develop не объединяет алгоритмы или Pulsecc971 автоматически.

## Следующее исправление

Кандидат root `8021301e894368aefd045f9d77274fcce9f60245` убирает вывод
expectation из имени. False требует отсутствие spikes, true — реальный response,
nullopt оставляет проверки completeness/validity/immutability. Legacy filenames
сохранены для сопоставления; новый fixture JSON явно пишет expectation,
observed spike count, effective threshold и model revision. Прежние positive
guards четырёх low-threshold callers сохранены явными аргументами; candidate
threshold loop также получает явный contract. Learner/Core/CMake/App и child
gitlinks не меняются, как и математические tolerances/search budgets.

Focused suite расширен42→44 двумя существовавшими low-threshold positive
controls при explicit sync0.2; оба уже входят в full304. Полный набор304
не сокращён. После подтверждения закрытия предыдущей unit пересобирается
только изменённый test и новые outputs в отдельном runtime-a4; закрытые
source/build могут использоваться инкрементально, прежний runtime-a3 и primary
сохранены. Worker1716073/start334541124, outer1716061. Повторный gate ещё не
принят. Необходимы независимые readers и normal/ASan общая regression приёмка.

Временной визуальный отчёт по этим модельным пробам ещё предстоит создать
из сохранённых samples с наложением actual input; полный render/cache должен
находиться на Data M40, выбранные читаемые рисунки — в компактном Git.
Поздний readout0.005 с C On/ModelSpec2 и реальные calibration transactions
также остаются открытыми. Только исправление fixture не закрывает этапы7/8/11.
