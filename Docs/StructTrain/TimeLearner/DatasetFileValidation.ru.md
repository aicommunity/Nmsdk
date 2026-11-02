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

Baseline пока не выполнен. До его публикации production parser не меняется.
После воспроизведения нужен locale-independent full-token parse, точная
размерность и проверка finite/range без подстановок. Negative ISI сохраняют
прежнее skip-значение, канонически-1. Hot reload и clock/lifecycle исправление
являются отдельной зависимостью, не подтверждаемой этим cold fixture.
