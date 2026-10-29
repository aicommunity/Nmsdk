# Метрики полной frozen evaluation

Подэтап этапов 3/9. Исторические CSV критерии и августовские наблюдения 4/8–6/8
остаются отдельными результатами своих протоколов. Данный scorer не пересчитывает
их под новый критерий и не завершает весь исходный план.

## Контракт

Production entry point:

```text
python -m Scripts.StructTrain.TimeLearner analyze evaluation.json.gz --format recognition-evaluation --model model.json.gz
```

Входная schema-1 evaluation spec явно задаёт run ID, model revision, ожидаемое
множество trials, sample ID/label/pattern hash, reset policy, presentation index,
duration и относительный путь каждого primary observation. Позиция строки не
определяет target. Дубли, пропуски, подмена меток или моделей запрещают оценку.
Target hash сверяется с объявленным training pattern; одинаковый sample ID не
может обозначать разные паттерны. Все trials проходят общий строгий native
observation auditor с повторным извлечением событий из первичных кадров.

Spec/trial/criterion field sets закрыты: неизвестное поле или версия не
игнорируются. Relative paths остаются внутри каталога spec, без traversal и
выходящих symlinks. Общий JSON loader читает raw и gzip, сохраняя проверки
duplicate keys и NaN/Inf; повреждённый gzip является invalid evidence.
Пакеты опубликованных данных анализируются прямо из чистого Git checkout.

## Явный response criterion

`post_anchor_target_whole_window_foil_v1` задаёт anchor (`onset` либо
`last_stimulus`), begin/end offsets в секундах и требование отсутствия target
spikes вне response window. Окно должно полностью помещаться в наблюдении.
Никакой новый автоматический физический tolerance не вводится; сравнительный
slack NumericChecks служит только округлению timestamp arithmetic.

- TP: target имеет хотя бы один spike в объявленном response window.
- FN: такого target spike нет, включая молчание и только ранний/поздний ответ.
- FP: foil имеет хотя бы один spike во всём observation window, включая late FP.
- TN: foil молчит при полном валидном окне.

Early/late spikes сохраняются отдельно. Target hit с дополнительными spikes
вне окна не удовлетворяет критерию при reject_target_outside_window=true.
Reset-per-trial и preserve-neuron-dynamics имеют отдельные rates/criteria.
Pooled accuracy является описательной величиной, а не единственным verdict.
Группа без target либо foil не получает положительного criterion_satisfied.

`per_trial_windows` оценивает объявленные окна. `continuous_native_stream`
дополнительно требует непрерывное покрытие native ticks между trials; пропуск
между окнами не превращается в отсутствие false positives в ITI. Изменение
физического порядка предъявления видно по timestamps и presentation index,
а перестановка строк с прежними IDs и timestamps не меняет оценку.

При censored/invalid trial counts отсутствуют, invalid IDs перечислены, CLI
возвращает 2. Повреждённые данные и неизвестная схема также не дают положительного
итога. Полная валидная отрицательная evaluation возвращает 0: процесс анализа
завершён, но response criterion может быть false.

## Состояния и provenance

Schema 1 поддерживает recognition package из completed learned-solo state с
его существующим certificate и inherited fixed threshold. Diagnostic/stopped
source не может маскироваться под завершённый Train. Проверяется реальный
binary64 Threshold дочернего LTZone, совпадающий с metadata; произвольный
calibrated claim отвергается. Автоматический подбор порога этим не реализован.

Source training outcome выводится как declared. Наличие пакета не доказывает
нативное исполнение и всю primary training evidence; scorer явно оставляет
native_execution_verified=false, source_training_evidence_checked=false и
global evaluation_verdict=null. Общий job должен связать эти метрики с runtime,
source/conversion audit и execution status. Criterion_satisfied по reset policy
не является сертификатом обучения или итоговым PASS всей кампании.

Evaluation spec digest использует canonical model codec, не зависит от путей
файлов и перестановки строк. Это identity spec, не новый ConditionSpec codec:
научные condition/matrix/attempt identities по-прежнему принадлежат condition.py.

## Проверки на опубликованных native данных

Final scorer source 0164e9357c3ec0196191cfa218e65f1c215bae31: на обоих workers
25/25 Python/CLI, без skips/errors. Это 13 новых metric controls, семь прежних
trial controls и пять CLI regressions. Нативная модель не пересчитывалась:
использованы source 127806a34, четыре заранее объявленных 2 kHz профиля
Classic N0 / Branch N1, 16 полных trials и 3856 primary frames. Отдельный общий
source/conversion audit проверяет 56 primary training trials.

Fixture criterion объявлен заранее: last actual stimulus + [0, 20 ms]. В обоих
типах модели high-threshold контроль имеет TP=0, FP=0, FN=2, TN=2; low-threshold
контроль — TP=0, FP=1, FN=2, TN=1 и один target trial с ранним spike. Criterion
false у обеих reset policies. Это dimensional integration controls с двумя
входами; не результаты исторического восьмипаттернового эксперимента и не
доказательство общей неразделимости семейства моделей.

Тесты отвергают пропуски/дубли, label/model corruption, censored окно, NaN,
пропуск continuous stream, ложную калибровку и diagnostic source. Отдельные
synthetic mutations реальных primary records проверяют early-target и late-foil
правила; они не учитываются как новые native runs.

Первые A1 gates source f2cf8b4ad (24/24) сохранены отдельно. A2 добавляет явное
исключение diagnostic source и даёт 25/25. Данные и CLI output самодостаточны:
evaluation specs ссылаются на соседние trial-N.json.gz и model.json.gz, без
двойного gzip. Source native reports доступны в Git по
60a1bd6fa44be04ce8fb59f2f2813dad84373b74 / 4eb082dd4ae6a5dd9c7fa4d4516ccb3b17bbce70.

A2 reports: Elder f1bd35dfa20a01e2c0a03a4a3372e528f7da3860,
M40 ae44a2a511e3ac9fe2381ee8dc4c3df65f2e9eba. Для каждого A1/A2 пакета
локально проверены все 39 stored и 37 raw hashes, включая декомпрессию.

Совместимость с принятым connected-stop auditor дополнительно проверена на
source 102c1fc15a106060f1f5b37ecb149b0e752baba1: по 30/30 Python/CLI на
обоих workers, без skips/failures/errors, process status 0. Reports:
Elder 2cfcd3ee3944a5abc0da843bd4c3ae43dbddc669;
M40 b4e5f744f829a3f50356874d13c539b8b0ae85ef.
У каждого проверены все пять stored / четыре raw hashes. Это повторный анализ
сохранённых native данных, а не новый физический эксперимент.

Подэтап готов к merge в develop. Этап 3 остаётся частичным: исторические
адаптеры, полная morphology/timing оценка и общий production verdict не закрыты.
Обязательные крупные графические отчёты описаны в VisualTestReports.ru.md;
их renderer и визуальная приёмка остаются отдельной незавершённой работой.
