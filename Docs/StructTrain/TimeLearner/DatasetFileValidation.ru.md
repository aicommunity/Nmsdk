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
размерность и проверка finite/range без подстановок. Negative ISI сохраняют
прежнее skip-значение, канонически-1. Hot reload и clock/lifecycle исправление
являются отдельной зависимостью, не подтверждаемой этим cold fixture.

Новый gate26 сохраняет все22 baseline cases и добавляет защиту от двойного
знака, UTF-8 BOM и whitespace-only строк. Это ещё не runtime-проверенное
исправление. Нельзя восстанавливать старые повреждённые файлы подстановкой0
либо считать ClassID из прежнего atoi доказательством корректной метки.
