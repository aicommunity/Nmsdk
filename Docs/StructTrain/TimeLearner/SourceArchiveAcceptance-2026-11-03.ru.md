# Приёмка часов источника и архивной telemetry 03.11

Это ограниченная приёмка двух исправлений, не завершение этапов1–12.

NDatasetBase использует относительное время после целочисленного вычитания
ULongTime anchors. В единой частоте предъявление готовится до штатного расчёта
детей; двойного расчёта нет. Файловый reload проходит native Build/Reset,
динамически созданные генераторы получают native Init. Compatibility multirate
сохранён; новая физическая multirate-приёмка не заявлена.

ModelArchive исключает только telemetry StepDuration из приватного XML-образа.
Живые компоненты, физика, wall/search budgets не изменены. Это не полный
checkpoint динамики и не гарантия побайтной стабильности всего XML State.

Проверенный код: root `b9af8990fe56e9b1662ddaceaa8f874e5b3bb143`, Pulse
`9ab6d57f0118ad6564ffd8421d7ab2a7a4040fe2`, Rdk
`48d6548e46f3310537a2d8b59fb5be553307a54f`. Core текущей Pulse feature побайтно
совпадает с этим Core; принятый Rdk develop сохраняет тот же проверенный Core.
Единственное изменение исполняемого Python относительно root снимка — короткие
заголовки renderer, проверенные отдельным visual evidence.

| Проверка | Evidence commit | Результат |
|---|---|---|
| Source normal25/readers41 | `91fd3930ba29d0255c9b2cc2a339ebfa8afe7116` | PASS |
| Source ASan25/readers41 | `6173d8324f7db784bf1f69efef8a60a8893ca081` | PASS, actual libasan |
| Archive normal unit9/native20/readers24 | `69a1c928eed1f0248790ce1dd9c843b6c7d3bf12` | PASS |
| Archive ASan unit9/native20/readers24 | `6d0d1d4c3fc50fe55f6c9b7a04d89a15d92259e4` | PASS, actual libasan |
| Broader normal202/readers8 | `248660b2362308de583e72f1a0ec6b7aa139ef10` | PASS |

Все outer/member SHA256 проверены. Source normal/ASan:83/83 CSV побайтно равны;
archive normal/ASan:122/122 CSV побайтно равны. Таблицы с hashes находятся в
Reports/StructTrain/TimeLearner/s03-source-normal-asan-comparison-a1 и
s05-archive-normal-asan-comparison-a1. Readers41 включают24 controls прежнего
normal C₀ primary, а не новую ASan-серию C₀.

Исторические отрицательные baseline и неудачные setup сохраняются. Для source
selected16 графиков непосредственно проверены: реальные входные импульсы,
сома, читаемые подписи и zoom native samples, включая origin1e9s и cutoff.
Global visual acceptance=false: полный кэш3888 изображений не объявлен
просмотренным. Научная классификация этим не проверялась.

Строгий parser, горячая перезагрузка повреждённого файла после parser-изменения,
автоматическое владение C₀/C-trim, полная матрица режимов, legacy parity и
оставшиеся production/experiment пункты требуют самостоятельной приёмки.
Объединение выполняется через --no-ff: Pulse develop, затем точный gitlink
корневого develop. История не переписывается.
