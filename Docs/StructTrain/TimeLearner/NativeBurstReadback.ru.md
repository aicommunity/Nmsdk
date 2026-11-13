# Полный отклик пачки при фиксированной геометрии

Новый probe job schema7 предназначен для диагностики stopped-моделей и влияния Rs на форму полного отклика. Он не принимает решение о принадлежности пика, не изменяет CapturedPerInput, не запускает Train и не выдаёт сертификат обучения или классификации. Публичный builder: native_characterization.prepare_burst_readback_job.

## Контракт

presentation.kind=native_burst_readback, source_ordinals содержит строго все исходные индексы 0..N−1. peak_selection=none, window=null, record_spikes=false. Stimulus profile побайтно по семантике равен исходному; замена пачки одиночным импульсом или пропуск неудобного импульса запрещены. Число физических входов и полный исходный pattern сохраняются. Classic использует input_index=0, Branch — объявленную активную точку подключения.

Полный набор source_ordinals проходит существующий native subset/presentation механизм schema6, который уже записывает реальные импульсы, полные временные ряды и восстановление presentation. У нового job и execution отдельная версия7; прежний job6 по-прежнему запрещает resistance_intervention. Схема6 низкоуровневого observation не превращается в измеритель обучаемого пика. Rest-state остаётся штатным состоянием модели.

Необязательный resistance_intervention в N1 меняет индивидуальные значения через ApplyNativeParameters после настоящей завершённой исходной пробы. Для каждого изменяемого входа перед edit выполняется свежая AssessNativeResistanceDomain: available, неизменность live model, соответствие base revision, полный geometry и попадание в per-input bounds обязательны. Полные физические preview сохраняются в resistance-domains.json; Python audit независимо пересчитывает domain и связывает его с фактическим конечным графом. N0 допускает raw replay; изменение Rs этим режимом для N0 не поддержано. При незавершённой baseline редактирование и основная проба не выполняются. Пустой intervention даёт один исходный replay; явный no-op intervention с исходным Rs даёт baseline+основную пробу и служит контролем абсолютного model clock для changed-Rs случая. Shared Branch bank требует согласованных значений для всех логических владельцев; геометрия, storage-образы и C не меняются.

Каждая проба проходит native scheduler и штатные boundary reset/build. Дополнительных Calculate, tick-патчей и проверки bool Build/Reset не добавляется. Сохраняются полная импортированная модель, проверка её графа и параметров, неизменность controller snapshot, полная artifact closure, исходная и конечная semantic identity, реальные timestamps и отдельные baseline CSV. Канальная диагностика включается явно.

## Проверки и границы приёмки

Добавлены7 declaration controls: N=1 и >4, Classic/Branch; no-op и индивидуальное изменение Rs; запрет omissions/reorder/duplicates; запрет window/peak/profile/schema overrides; прежний запрет Rs в job6; согласованность общей Branch bank. Это синтетические wire declarations, не native runtime evidence. [Elder7/7 приняты](ValidationPlans/ElderNativeBurstReadbackA1-20261113/RESULT.ru.md), исходные receipts сохранены в Git.

Перед фактической N4 диагностикой требуются серверная сборка Console, эти проверки и реальные production probes на импортированном stopped package7: unchanged replay, matched no-op, changed Rs с полной проверкой graph diff, clocks и входов. Приёмка schema7 пока не заявляется. Большая N4 модель не заменяется синтетической моделью или неполным legacy overlay. Конечный список Rs фиксируется после свежей native domain assessment для конкретной revision; границы другого графа не переносятся автоматически.

Результат нужен для решения о порядке поиска L/Rs и причинах ambiguous assignment. Даже отчётливо видимый общий максимум не становится максимумом закреплённого импульса. Для обучения остаётся действующий composite/candidate-window протокол, а scientific Test требует отдельного frozen evaluation с проверенным порогом.

## Дополнительная проверка Console перед N4

Подготовлен NativeBurstReadbackConsoleTest: реальные Classic/Branch stopped N1 package7, для каждого исходный replay, time-matched no-op Rs и Rs×0.75. Штатные production run_job/audit_run_manifest проверяют импорт и полный граф, managed child groups, domain preview, actual inputs, byte-equal warm baseline и неизменность геометрии. Изменённый Rs обязан реально менять выходной потенциал. Это6 настоящих Console probes; их выполнение пока не принято.

Consumer native_pipeline_worker теперь направляет структурированный exit2 probe job7 на полный аудит, как для прежних версий. Сам exit2 и наличие execution.json не становятся valid/PASS; добавлен отдельный отрицательный declaration control. Ранее7/7 относятся к Root1ae882633; новый набор из8 declaration controls ещё требует серверного запуска. Бинарник schema7 остаётся из отдельной сборки Root1ae882633; последующие Python-only проверки не требуют его повторной сборки.
