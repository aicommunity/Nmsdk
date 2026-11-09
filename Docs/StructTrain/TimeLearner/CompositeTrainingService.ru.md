# Native composite Train: сервисная композиция

Подготовлен opt-in protocol4 путь NativeTrainingService к реальному N+2 executor и typed capture/search/final. Состояние — source-only, без локальных численных запусков и без runtime acceptance. Полный контракт находится в PulseLib Docs/TimeLearner/CompositeTrainingService.ru.md, точные22 IDs — в CompositeTrainingServiceGateInventory.json.

Fixtures работают с реальными storage/model/owner lifecycle, а не копиями алгоритма. .2 в positive cases — явный инженерный tolerance; .02 outside-tolerance контролируется отдельно. По22 cases проверяются CalculateMode0/1, warm Reset с сохранением initial source/C0 и ссылок, stop перед final consume, onPrepared cancellation, partial Reset/Default, retarget и primary-byte budget до queue.

Следующий обязательный commit: cold6/protocol4 portable codec, package5/certificate2 с self-contained primary replay и actual model import, Console autostart/export/Train→Test. Эта граница не объявляется завершением конечной интеграции. Ни defaults, ни общие experiments данным commit не включаются.

Регрессионный scope этого этапа169: BoundedTraining74 + FinalVerification23 + typed46 + preparation-cancel4 + service22. Исполняемый инвентарь сверяется через gtest_list_tests, включая настоящие четыре invalid-budget macro expansions.
