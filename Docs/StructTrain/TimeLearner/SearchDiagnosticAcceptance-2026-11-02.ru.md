# Адресная приёмка поиска и диагностического Test

PulseLib develop merge a18c8a1097a221e5aca3bfc2c1afc07fb2534a56 опубликован
первым. Его Core tree2743819327158d12389221ba8c1cd9a928f28224 точно равен
проверенному225642bd9b3a5651fce2808bd0bef79944d4f1b8. Bin остаётся
14a88195a8a5538d3a2f5c0657981488e38829b7, Rdk —
eda206b6b35de451ae837473d731ba20e7c30bde. Корневая feature закрепляет эти
gitlinks и объединяется в develop через --no-ff после ребёнка.

Приняты в границах адресных отчётов:

1. Конкретные причины search termination и различение sweep exhaustion от
   отсутствия регулируемых входов; negative final не означает convergence.
2. Проверка native scheduling до исполнения и после callbacks/sink;
   Build/import/export/rollback сохраняют штатный lifecycle.
3. Явный diagnostic recognition остановленной модели, публичный Console/CLI,
   strict/partial readers и temporal reports. Ordinary path остаётся строгим.
4. Ранжирование измеренных ошибок при zero tolerance и overflow без изменения
   Exact, CapturedPerInput, bounds и defaults.

Источники и failing baselines: SearchTermination.ru.md, NativeWallSchedule.ru.md,
DiagnosticRecognition.ru.md и FiniteCandidateRanking.ru.md. Общие gates и
primary closure: CompletedASanGates-2026-11-02.ru.md. ASan163/163, recording18/18,
public diagnostic6/6, preflight14/6/2, readers32/32 завершены. Rank дополнительно
прошёл81/81 +4 physical cases на каждом worker, raw readers21/21 и visual QA14
original PNG. Более широкая матрица этим не подтверждается.

## Python-регрессия

На каждом worker60 выполненных tests без failures/errors, плюс один явно
skipped N0 production class. Проверены ConditionSpec, config parser, cleanup,
dynamics, plotting, publisher faults, runtime identity и source aliases.
Все1599 Project.ini из точных Git blobs Bin14/Configs/SpikeSamples/StructTrain
сохраняют bytes при roundtrip. Manifest содержит пути/blob/SHA256. Configs
восстанавливаются из Bin commit; working checkout/runtime не менялись.

Elder proof6f59efed3ffa92b0d4d689690bbc84f77f9d089e:
17 verified members/69327 bytes. M40 proofb96f9712578adc2271098a7e98405c084af2bbc6:
17 verified members/71211 bytes. Это Python, не новый native ASan прогон.
Outer и все member hashes проверены после fetch.

Неудачные общие попытки сохранены. unittest discover не импортирует namespace
package. Следующий запуск122 modules получил13 missing-fixture environment
errors,109 skipped classes и один отказ пустого config corpus sparse checkout.
Подготовка реального corpus исправила последний отказ. Остальные отсутствующие
fixtures не подменены и не объявлены проверенными; assertions не ослаблялись.

## Открытые требования

Полные этапы1–12 остаются частичны; ControllerVersion2 не объявляется общей
рекомендацией. Открыты lifecycle/storage/profile/mode матрица,
Quantized/BestEffort, C-trim/PostTune, independent Test, history/property/source
impact audits, migration, scheduler и остальные пункты RefactoringPlan.ru.md.

Для stage9/10 нужен поддерживаемый реестр validation suites: явные test IDs,
fixture dependencies, Git source/primary closure, команды подготовки и статусы
unavailable/passed. Текущие122 modules не являются единой настроенной suite.
Молчаливые skips или фиктивные данные не являются решением этой проблемы.
