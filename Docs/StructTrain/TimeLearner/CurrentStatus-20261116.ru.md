# Статус полного плана TimeLearner — 16 ноября 2026

План целиком не выполнен. Полностью принят исходный этап 0; этапы 1–12 частичны. Сквозной контур cold Train → export/import → frozen diagnostic Test → анализ → временной отчёт уже реально работает. Полная приёмка режимов и итоговое научное сравнение остаются открытыми. Устойчивый современный классификатор пока не подтверждён; число пройденных инженерных проверок не измеряет близость к этому результату.

[Проверенный снимок серверных результатов и версий](PlanStatusSnapshot-20261116.json). Эта сводка заменяет прежние оперативные формулировки «выполняется» в отчётах своих снимков; исходные наблюдения и статусы исторических запусков сохраняются.

## Последние завершённые научные проверки

1. **Умеренный поиск Branch N4/N1 завершён.** Native SDK 154/154 и адресный kernel corpus 116/116 до/после приняты в своей области. В cold Train получены 58 полных групп, 22 scalar candidates, один локально готовый input2. Новые L56/42/35 измерены полностью, но input1 остаётся ambiguous: ранние отклики сливаются. Общего сертификата нет. Изменение порядка поиска объединено через child-first --no-ff в develop. [Научный отчёт](N1ModerateRecoveryScientificReport-20261116.ru.md).
2. **Frozen diagnostic восьми паттернов завершён.** При threshold100 модель молчит: TP0/FP0/FN1/TN7. Все восемь наблюдений полны; молчание не является рабочей классификацией. [Приёмка и внешние primary refs](N1ModerateFrozenDiagnosticAcceptance-20261116.json).
3. **Один заранее выбранный Same-Matrix порог проверен реальными спайками.** Две серии по восемь valid observations завершены: threshold100 даёт TP0/FP0/FN1/TN7, threshold0.11468361216368189 — TP1/FP6/FN0/TN1. Оба target event (.343/.3775с) раньше последнего входа .49с. Полный primary71.31MB и1107-PNG галерея опубликованы во внешнем M40 архиве;32 выбранных Soma/LT originals просмотрены. [Читаемый научный отчёт всех паттернов](N1ModerateRecognitionScientificReport-20261116.ru.md). Independent restore нового threshold пакета ещё не принят.
4. **Elder независимо восстановил frozen8 primary и воспроизвёл метрики.** s11-restored-moderate-frozen8-report-elder-a1 completed, assertion1/1, процессы закрыты. Проверены436 members, один verified duplicate alias исключён явно. Галерея восьми trial/Soma с overview/native zoom опубликована,561 PNG; просмотрены8 overview и8 peak zoom, полный просмотр561 не заявляется. [Приёмка и primary104.29MB](N1ModerateFrozenTemporalAcceptance-20261116.json). Нового native расчёта на Elder в этом задании не было.
5. **PSI storage preflight и исправление подготовки окон приняты адресно.** Effective graph подтверждает штатные Stock/PSI2.5 образы и сохранность остальной физики; LTMembrane отсутствует. [Stock cold A1 завершён](PresynapticStockColdAcceptance-20261116.json):22 scalar candidates/один jointly-ready input2, затем ambiguous input1. PSI A1 дал четыре полных references и отказ окна [12,3612] вне [0,3600], без поиска: это setup error скрипта, native refusal корректен. [Production prepare на реальных данных прошёл1/1](PresynapticWindowPreparationAcceptance-20261116.json), включая чужой класс/target. Новый PSI A2 запущен с корректными relative guards, одинаковым эффективным полным окном, свежими references и прежними допусками/бюджетами. Последний readback подтверждает живой native PID3408629; научного итога A2 пока нет.

Более ранние современные Same-Matrix результаты Classic TP1/FP2/TN5 и Branch TP1/FP5/TN2 показывают частичную разделимость со значительными ложными и ранними срабатываниями. Исторические визуально подтверждённые августовские 4/8–6/8 сохраняют силу для исходного протокола; современные отрицательные проверки их не отменяют.

## Сверка исходных этапов

| Этап | Статус | Что выполнено и что остаётся |
|---|---|---|
|0. Начальное объединение|Принят|Исходные develop/gitlinks согласованы; новые принятые подэтапы объединяются отдельными merge commits.|
|1. Доказательства и параметры|Частично|Есть исторические anchors, реестры параметров/дефектов; остаются semantic/effective-factor review, inherited properties и unknowns.|
|2. Изолированные сборки/runtime|Частично|Работают изолированные runtime, manifests и учёт процессов; полная resource/build/fault matrix не закрыта.|
|3. Наблюдения/scorer|Частично|Strict IDs, finite/completeness, реальные frozen данные и единый аудит проверены адресно; остаются все применимые legacy adapters/режимы.|
|4. Lifecycle/storage|Частично|Есть реальные native fixtures и effective graph/physics checks; полная fresh/reuse/Copy/Load/Build/growth/heterogeneous матрица открыта.|
|5. Export/import|Частично|Работают полное состояние, Train→Test и boundary continuation; все варианты физики/связей и independent corpus replay ещё не приняты.|
|6. Общий контроллер|Частично|Общий native service, configured controller, Classic/Branch adapters работают; остаются legacy/V2 A/B, остаточное дублирование и multirate.|
|7. Алгоритмы обучения|Частично|Реализованы measured bounded L/Ns/Rs search, revision-bound observations и fresh final gate. Открыты полная matrix, C-search и проблема слияния закреплённых откликов; stock всей модели не сошёлся.|
|8. Conversion/PostTune/calibration|Частично|Есть versioned solo/recognition, транзакции и реальные threshold/frozen проверки; все режимы, rollback/interruption и independent evaluation не приняты.|
|9. Пакет экспериментов/миграция|Частично|Корневой пакет/CLI и 357 записей migration manifest проверены; complete=false, остаются инструменты Bin и callers.|
|10. Runner/provenance/publish|Частично|Работают owned groups/leases, ConditionSpec и fail-closed публикация; полная fault/effective-factor matrix не закрыта.|
|11. Научная матрица|Частично|Есть исторические replay/cold, современные Train/Test и временные отчёты; итоговое legacy/V2, order/ITI/reset/physics сравнение не завершено.|
|12. Документация|Частично|Поддерживаемая сводка отделена от истории; финальная root/PulseLib/Bin/config/ClDesc сверка и завершение миграции остаются.|

## Следующие действия по научной задаче

1. Дождаться закрытия уже работающего PSI A2, проверить полный native/DATA/physical результат и сравнить с завершённым Stock A1. Начальный PSI A1 сохраняется как ошибка постановки. Raw guards различаются из-за измеренного сдвига reference-пика; эффективное окно [0,3600] и остальные факторы совпадают. Не перезапускать задание из-за потери наблюдения.
2. Независимо восстановить новый71.31MB threshold primary на Elder и воспроизвести обе серии через production audit/scorer. Галереи и выбранный визуальный просмотр уже опубликованы; нового моделирования для этой проверки не требуется.
3. По измеренному Stock/PSI сравнению принять следующее адресное решение по физике/поиску, затем свежая проверка всех входов и frozen оценка фактической модели. Ещё одна непроверенная перестановка L или увеличение бюджета не считаются исправлением.
4. После адресных алгоритмических проверок закрыть оставшуюся legacy/V2 и режимную/физическую/order/ITI/reset матрицу, миграцию и документацию. Результат 8/8 не обязателен; честные отрицательные результаты и проверка заявленных алгоритмов обязательны.

Надёжного срока получения успешной классификации сейчас нет: ограничение находится в измеряемых свойствах откликов и поиске всей модели. Новый corrected PSI A2 рассчитывается на M40; перечисленные threshold/report/collector задания завершены.

Принятый develop: root e8f7a53c6bca3a1d095ab2955f2a65c8f4a81e20, Pulse23d039e44f927eb8040473845d3c391270d9d15e, Bin8cb6dba07b30432272984c8ce3136b48ad06f064, Rdkde4134235c0dcb8b91fd9a43b267348ad1a163ca. Текущая PSI feature и её ещё не принятые изменения не объявлены завершённым develop-релизом.

Техническая очистка истории завершена. Тяжёлые данные и полные галереи находятся в /media/user/Data/Nmsdk-StructTrainExpArchive на M40; [Samba](//10.245.1.12/Nmsdk-StructTrainExpArchive). Git содержит код, настройки, документы и компактные проверяемые refs. [Подробная карта реализации](ImplementationStatus.ru.md).
