# Параллельная проверка Load/XML исправлений — 10.11.2026

Это продолжение [воспроизведения двух дефектов](NativeLoadXmlPreimage-20261110.ru.md).
Одинаковая измеряемая source closure на M40 и Windows:

| Репозиторий | Commit |
|---|---|
| Root SDK | f39b9ebdcd0e7a64e388d778ca32374a65ae4e0c |
| PulseLib | 991d933a5a3f6fe1d17986118656be98cda31392 |
| Rdk | de4134235c0dcb8b91fd9a43b267348ad1a163ca |
| Bin | 8cb6dba07b30432272984c8ce3136b48ad06f064 |

Пять остальных child commits сохранены. На обеих машинах проверены 4074
физических source files и все восемь HEAD; checkout clean, alternates нет.
Source, build и runtime каждой попытки изолированы; работающие каталоги не
обновлялись. Математическая цель и физические профили обучения не меняются.

## M40

Canonical A2 completed0/clear, 80.52 s, 86 previous bindings checked.
Build output `/media/user/Data/TimeLearnerRefactor/readbacks/s05-native-load-xml-repair17-m40-a1`.
Supervisor399987/start338340735 и outer405767/start338342163 наблюдались live.
Configure завершён, фактическая компиляция началась. Затем автоматически
должны выполняться 17 объявленных проверок, начиная с Load/XML8. Запуск и
декларация не являются PASS; при следующем обращении проверяется тот же handle.

## Windows .14

На `.14` свободно 1762399002624 bytes на C:, предыдущие TimeLearner tasks
на момент проверки не имели работающих instances. Создан новый private SDK
`C:/Projects/TimeLearnerWorker/source-native-load-xml-repair-win-a1`.
Пользовательский `C:/Projects/Nmsdk` не изменён.

Frozen declarations в Root `1b2e966fc00c57969dd8b743bb2269d96ac92c6f`:
`ValidationPlans/WindowsNativeLoadXmlRepairPreparation-20261110`.
Namespace Git blob `8552a434870b271a2eaecfeffe671f57604aadfa`,
build specification blob `fa4354ed15ac246d1369bf9c3b6f6738901350bc`.
Доставка выполнена Git pack/index-pack и штатным GitPreparation module;
Test-PreparedSdk подтвердил 4074/4074 files, восемь clean HEAD, no alternates.
Результаты первичного неуспешного SSH-вызова не использовались для повтора:
сначала отдельно подтверждено отсутствие нового destination. Успешная
доставка выполнялась из системного shell; Node child SSH возвращал255.

Штатный `launch-sdk-build.ps1` Tool
`c3ac2470487635c176b4ba7d375f44d667e4f12e` запустил `sdk-build.py`, SHA256
`c31340a8883110ffdf1ac1a57056ada4063ab28d4208cf35652ebd0a1cc381a1`.
Task `TimeLearner-windows-native-load-xml-repair-build-a1`, instance
`E93BB1F3-4DF1-459A-A6B1-120249C2A68F` наблюдалась в state4; producer
python3664/parent6332 с CreationDate1794308528368 ms действительно жив.
Output `C:/Projects/TimeLearnerWorker/jobs/windows-native-load-xml-repair-build-a1`
содержал producer/specification/source-before. Это build-only job:
после завершения нужны проверка whole process closure, runtime/build provenance
и отдельная декларация native checks. Native/scientific PASS не заявляется.

## Elder

Elder доступен, available memory около27 GiB, но свободно только2521448448
bytes на `/` (100% по df). Найдены13 самостоятельных build-каталогов; каждый
занимает примерно40–232 MB. Их удаление само по себе не создаст достаточного
запаса для новой полноценной сборки. Основной объём остаётся в старых source,
runtime и readbacks; нужны проверки опубликованных primary, уникальных файлов,
Git worktrees/stash и действующих зависимостей до удаления.

В этой проверке ничего с Elder не удалялось. Наличие свободной RAM не решает
нехватку диска. Elder остаётся обязательным Linux worker полного плана и
должен вернуться к адресным проверкам после освобождения места.
