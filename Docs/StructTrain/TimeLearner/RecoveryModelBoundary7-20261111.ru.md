# Recovery: модель7 и сводка8

Уточнение11.11: independent Python audit фактического package7/summary8 принят9/9 на Elder; native transfer после Build пока не принят. В production pipeline обнаружен отдельный пропуск: _snapshot_source распознавал только5/6, поэтому7 шёл по legacy trial-file пути. Добавлена явная передача7 через общий composite reader и обязательная сверка внешних primary с embedded bytes до записи снимка. Три новые проверки используют тот же настоящий C++ corpus: полный перенос package+summary+48CSV, повреждение внешнего CSV и отсутствие CSV. Это новое изменение ещё не принято серверным прогоном; предыдущие9/9 его не проверяли.

Статус: реализация и адресные tests добавлены; серверная компиляция и runtime
приёмка ещё не выполнены. Наличие этих файлов не закрывает этапы5/7/8 плана.

Package7 сохраняет весь прежний native boundary: storage definitions, начальный
snapshot, обученный граф, dataset, индивидуальные параметры, C0/corrections,
частоту, исходные references, актуальный runtime, certificate либо диагностический
outcome. Дополнительно сохраняется recovery ledger с runtime каждой попытки.
Его hash входит и в metadata физического архива. Summary8 содержит тот же ledger.

Native dispatcher выбирает7/8, если исходная family cold8, текущая policy recovery,
сохранились прежние deliveries либо обнаружена ошибка записи журнала. Последний
случай запрещает экспорт. Warm Retry с историей не понижает формат до6/7.
Явные старые factory/summary entry points продолжают отказывать при новой family.
Загрузка7 через общий native import проверяет данные до замены живых компонентов.

Порядок загрузки:

```text
validate exact schema/content hashes
decode initial configuration and active runtime
replay archive2 primary/context/window/reference/final evidence
bind recovery deliveries to actual groups/parameters/C/runtime budgets
check metadata, storage closure and native source dependency graph
import initial and current physical graphs through native mechanisms
read back full model identity, individual inputs and effective C
install Finished boundary and preserved delivery DATA
leave probe idle and IsNeedToTrain=false
```

Это boundary import, не продолжение посреди пробы. Не восстанавливаются search
traversal, старые callbacks, prepared objects, live authority или физическая
динамика. Следующий Start создаёт новую попытку, сохраняя исходные targets.
Ledger явно содержит independent_delivery_completeness_verified=false:
связность supplied entries не доказывает полноту всех действий контроллера.
Сертификат проверяется по свежим final measurements конкретного графа, отдельно
от утверждения о полноте search history.

Новые real-component cases охватывают Classic/Branch, N0/N1, stopped state с
реальным recovery, completed state без rejected events, asymmetric C0,
public export/import/re-export, неизменность живой динамики при экспорте,
повторный raw burst response с фактическими входами, warm Retry, повреждённый,
чужой и дублированный ledger, сохранение legacy6 и запрет его переименования в7.
Сравнение image definitions использует штатный semantic fingerprint; все
остальные поля package и текущий граф остаются в сравнении.

Raw response fixture — полный native burst при activeInput0, а не независимый
научный Test всех паттернов. Допуски сравнения transport response не меняют
SyncTolerance или amplitude tolerances обучения. Научные отчёты и обязательная
матрица остаются отдельной работой.

Console, independent Python package7/summary8 audit, frozen recognition source7,
полнота controller ledger, interruption/checkpoint и stockN4 A/B пока не приняты.
Новый дорогой Train до их требуемых проверок не запускать.

Для раннего поиска compiler errors добавлен cpp_syntax_preflight: реальный
GCC проверяет исходные translation units с флагами закрытой production сборки,
без линковки и изменения reference build/runtime. Процессы ограничены cgroup,
резервируются ресурсы, сохраняются compiler/flags/source identities и closure.
Эта проверка не заменяет свежую SDK сборку и native tests. Generated headers
берутся из явно указанного закрытого reference context; герметичная сборка
либо runtime-совместимость таким результатом не утверждаются.
