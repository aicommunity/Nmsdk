# Загрузка полных моделей: байтовый вход и строгий JSON

Статус: код и четыре регрессии подготовлены в отдельной ветке
`codex/timelearner-json-byte-source`; runtime-проверка ещё не выполнена.
Текущий SDK N1 Root93894dd / Pulse52cb953 и два cold Train не менялись.

## Основание и изменение

`App/NeuroModelerConsole/TimeLearnerJobSource.h` читал весь файл в QByteArray,
преобразовывал его в std::string, затем общий parser создавал ещё один
QByteArray. Для сохранённых моделей761851830 и678423634 байт эти явные
полные копии дороги. Это наблюдение по production-пути, а не измерение
peak RSS новой реализации.

Общий parser перенесён из `ConfiguredNativeTraining.cpp` в отдельные
`PulseLib/Core/TimeLearner/StrictNativeJson.{h,cpp}`. Это тот же production
parser для обычного конфигурационного входа и файлового транспорта.
Вход `ParseStrictNativeJsonBytes` принимает исходный QByteArray; старый
`ParseStrictNativeJsonObject(std::string)` сохранён и передаёт временный
read-only view. Возвращаемый QJsonObject владеет разобранными данными.
Пределы размера, глубины, проверки синтаксиса и дублирующихся ключей сохранены.

Дополнительно закрыт обнаруженный разрыв проверки: Qt допускает UTF-8 BOM,
а старый обход duplicate keys начинал с BOM как с primitive и не обходил
члены объекта. Новый обход учитывает BOM, а после корневого объекта требует
конца документа с допустимыми JSON-пробелами. NUL или другие хвостовые байты
не должны превращаться в молчаливо отброшенные данные.

## Проверки

`Test_PulseLib_NativeJson.cpp` содержит четыре случая:

- равенство байтового/строкового входов и сохранность результата после
  изменения исходных буферов; Unicode, NUL внутри строки и128KiB payload;
- nested и escaped duplicate keys;
- обычный и дублирующий объект с UTF-8 BOM;
- точные byte limits, многобайтная строка, malformed framing и trailing NUL.

Production parser компилируется напрямую в `Test_PulseLib_NativeJson` через
`NativeJson.cmake`. Этот малый Qt-only target доступен также из
`Tests/Integration/Algorithms`, использует штатный runtime-capture main.
Те же четыре случая включены в полный `StorageComponents`; тело функции
не копируется в тестовый код. Малый target не подтверждает полный импорт
обученной модели или физическую эквивалентность Train → Test.

После server slot: малый parser gate; затем полный Console/file-source
cohort и actual большие stopped-model Test с прежними лимитами и исходными
моделями. Оценить execution, RSS, model identity, полноту8 наблюдений и
неизменность frozen model. Не выдавать статическое устранение копий за
измеренное уменьшение RSS или научный результат.

## Граница с этапом5

Это **не** компактная новая схема модели. Все существующие пакеты, история,
проверки provenance и сертификатов читаются целиком. Отдельный полноценный
model export должен отделять физический graph/storage/dataset/threshold
от search history и controller checkpoint, иметь версионированную схему
и проверяемую ссылку на доказательства в M40 archive. Удаление полей из
старого пакета или ручной overlay не заменяют этот экспорт. Этот пункт
исходного плана остаётся открытым.

## Зафиксированная серверная подготовка

Root `db483e081732e04620807d870d126b0b98b49a48`, Pulse
`3b51b81495197a3871504867474514657871cc38` доставлены через Git в отдельный
M40 `source-native-json-byte-a1`. Для малого production kernel4 созданы
controls `3cb65bd702c0005e49a5a84f50d4a603603ae914`, job
`s05-native-json-byte-kernel-m40-a1`. Source, suite, compiler и Git gtest
объявлены отдельно; preflight не выполнял тесты.
[Квитанция подготовки](../../../Reports/StructTrain/TimeLearner/NativeJsonByteSource-20261117/kernel-preparation.json).
Запуск ждёт закрытия cold job и свободного slot, не изменяет его runtime.
