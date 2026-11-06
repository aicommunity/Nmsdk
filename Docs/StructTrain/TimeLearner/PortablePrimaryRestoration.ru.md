# Восстановление primary: dereferenced glog aliases

Постановка06.11.2026, ещё не принята. Реальный архив пилота `bd10072c73d7c8296f1a4d02c051459f29f8c039`
содержит служебный `NeuroModeler.INFO` как обычный файл: старый producer следовал
symlink при упаковке. Native run manifest правильно включает только реальный
именованный log с PID. После обычной распаковки строгий production auditor
возвращает worker_event_log_owner_mismatch. Первые графики не были построены;
модель не запускалась повторно.

Новый модуль `Scripts.StructTrain.TimeLearner.portable_primary` проверяет archive
hash/size, каждый member и точное множество файлов. Любые symlink/hardlink tar
members, выходы за пределы, дубли и повреждения отвергаются. Существующий output
не изменяется. Частичный output при ошибке остаётся диагностическим, а не PASS.

Совместимость включается явно: `--compatibility dereferenced-glog-aliases-v1`.
Только в новом производном дереве пропускается избыточная копия alias, если она
не объявлена первичным артефактом, точный PID связан с manifest-owned-process,
а bytes/hash совпадают с единственным реальным log соответствующей severity,
который включён в signed run manifest. Все кандидаты проверяются до удаления
любой копии. Исходный архив и signed manifests не меняются. Исходная топология
symlinks не объявляется доказанной; receipt перечисляет каждое пропущенное имя.
Native artifact/provenance auditors остаются строгими и неизменными.

Пример серверного восстановления:

```text
python -m Scripts.StructTrain.TimeLearner.portable_primary BUNDLE.json NEW_DIR --compatibility dereferenced-glog-aliases-v1
```

Четыре byte-exact fixture records взяты из настоящего архива пилота: signed
run manifest, process owner, реальный log и dereferenced alias. Это regression
fixture упаковки, не полный native job и не научное доказательство.
Подготовлены14 адресных проверок; требуется серверный запуск на обоих workers,
затем полное восстановление990 members и повторное построение реальных графиков.
Наличие этой функции не закрывает исходные этапы2/3/9/10.
