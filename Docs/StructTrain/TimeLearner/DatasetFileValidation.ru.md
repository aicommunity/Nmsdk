# Строгий файловый вход NDataset

Открытый дефект: atoi/atof принимают числовой префикс либо превращают мусор в0;
ParseFeatureRow не проверяет лишние поля. Неверный header из старого документа
`f0;f1` задавал одну фичу вместо двух, а второе значение молча терялось.
Правильный header для двух фич: `class;f0;f1`.

Первый commit содержит только baseline fixtures:22 native cases над настоящим
NDataset из storage, реальным файлом и публичным Build. Проверяются Ready и
operation diagnostics; bool Build всегда должен бытьtrue. Файл и наблюдаемая
матрица (диагностические hexfloat strings, включая NaN/Inf отрицательного
baseline) сохраняются с SHA256. Это cold configuration tests, не вычисление
нейрона, не имитация parser в Python и не научная классификация.

Положительные контроли: прежний single-slot формат без metadata, два способа
записи поздних слотов, signed/scientific numbers и CRLF/whitespace, missing file
как idle/retryable. Отрицательные: испорченные class/ISI, диапазон int,
не-конечные числа, пустые/лишние поля, trailing delimiter, metadata suffix,
неизвестная metadata, неполный блок и недостаточная ширина строки.

Baseline22 выполнен на M40 под ASan:7 PASS,15 failures из-за ошибочного
Ready=true/отсутствия диагностики. Actual loaded mappings и все primary
проверены: evidence `e37135ab04f244a1e680452366fb872826cfab94`. Исходный build
fixture A1 не собрался: имя helper Run затенялось private testing::Test::Run;
отказ `a66b8cca0f438108494970331daef44377357087` сохранён отдельно. Исправлено
только имя helper, assertions не ослаблялись.

Кандидат Pulse `e686297ad10084429f7220fd2c5674f6d9869f25` вводит
locale-independent full-token parse, точную
размерность и проверку finite/range без подстановок. Negative ISI сохраняют
прежнее skip-значение, канонически-1. Hot reload и clock/lifecycle исправление
являются отдельной зависимостью, не подтверждаемой этим cold fixture.

Новый gate26 сохраняет все22 baseline cases и добавляет защиту от двойного
знака, UTF-8 BOM и whitespace-only строк. На M40 ASan B1 прошли26/26 native
cases и7 JUnit/environment readers. Evidence
`22a037fd0f7f345ada4c5aa1260d3389662ca5dc`: проверены85 members,
48 012 compressed bytes, actual libasan mappings. Исходный root
`8555f348b2274cec68b3cf5419b53423e60b99ae`, Pulse — указанный выше кандидат.
Обычный counterpart Elder завершён:26/26 native и7 readers PASS, evidence
`ea03ae8d2c752d87c46d899c90d4431c2622a021`, проверены87 members/32 195 bytes.
Все26 входных файлов и26 JSON observations normal/ASan совпали побайтно;
поимённые hashes сохранены в Reports/StructTrain/TimeLearner/
s03-dataset-file-normal-asan-comparison-b1/comparison.json. Приёмка parser
в develop пока не назначена: integrated53 на обоих серверах дополняет cold26
двумя проверками corrupt reload/recovery при активном импульсе и25 принятыми
clock/lifecycle/dispatch controls. Assertions не заменяют научную классификацию.
Нельзя восстанавливать старые повреждённые файлы подстановкой0
либо считать ClassID из прежнего atoi доказательством корректной метки.

## Горячий reload: обнаруженный дефект

Integrated ASan A3, бинарник из source root
`e13019653c4789e43513eca52a59fc67e1c51ef1`, обнаружил отдельный дефект при
2000 и20000 Гц: после замены файла повреждённым на высоком уровне выход
генератора оставался высоким на всех трёх проверенных invalid ticks. Ready=false
и operation diagnostics не обнуляли наблюдаемый выход. После восстановления
валидного файла исходные проверки recovery проходили. Это дефект физического
источника при отказе reload, а не отсутствие strict parser-диагностики.

Pulse кандидат `6a60f5c63c23a8f0645480408a5f60b64ed85957` вызывает штатный
SilenceGenerators при FileLoadResult::Invalid в PrepareDataset. Последняя
принятая матрица сохраняется для диагностики; старый сигнал не должен
продолжать предъявляться. Native Build/Reset восстанавливает playback при
валидном файле. Bool lifecycle не меняется; nested Calculate и модификация
storage prototypes не добавлены.

Normal integrated B1 завершён:53/53 native,17/17 readers PASS, evidence
`5c94d5490be958145989c5d019015c6acd0ccd51`, проверены261 members/3 047 522 bytes.
Normal baseline A2 `e4f4a1fa7e349ced8f1f736e01717e84b0de614c` имеет полный
inventory53 и ровно2 hot-reload failures; проверены257 members/3 047 513 bytes.
Все83 остальных CSV побайтно равны. В каждом из двух hot CSV изменились
исключительно3 invalid-phase samples: input1→0. Валидное исходное и recovery
расписание сохранено. Поимённые hashes и changed cells — в Reports/StructTrain/
TimeLearner/s03-dataset-invalid-reload-normal-comparison-b1/comparison.json.
ASan baseline и повторный B1 ещё выполняются последовательно; приёмка в develop
до их завершения не назначена.

Два отказа fixture A1 (неверный include) сохранены: M40
`924a2ec3b2af48c7bb1d724412f148458ec2d6da`, Elder
`458ae7046d8cd2102a2c731ae8aecfb3921f274a`; все13 members каждого пакета проверены.
ASan A2 собран, но CLI отклонил spec без обязательного asan_options:
`2892eae0fdb40e0eca7a80866e690c5ee369dda0`,18 members проверены. A3 использует
тот же immutable runtime с исправленным spec из
`a0bc101d83ab7f2f10743c3467051820c6a2baa9`. Исправление include/spec не меняет
assertions. Результат A3 сохраняется отрицательным; не подменяется поздним fix.
