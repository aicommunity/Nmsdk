# Перенос активного анализа Branch telemetry в корневой пакет

Цель: действующий read-only анализ динамики не должен оставаться в Bin.
Модуль перенесён в `Scripts/StructTrain/TimeLearner/legacy_dynamics.py`, шесть
прежних регрессий — в root tests. Старые оба `.py` удалены, wrappers отсутствуют.
Буквальный поиск потребителей обнаружил только прежний тест и исторический
отчёт13.10; его ссылка/команда актуализированы без изменения измерений.

Исходник Bin49adcd0208d0c8ab8d70e7cca47ae6e34b05145e; оба old paths,
blob SHA1, content SHA256, последний изменявший commit и `git show` находятся
в `script_migration.json:moved_files`. Mechanical root
`d742cf01b32d60e9ef792216a67c0c55f064e27f` сохраняет весь исходный analyzer;
тест меняет только импорт на root package. Следующий root
`0aa5d92850bef109a81739ebb8b9aad4d8279aa3` отдельно вводит общий CLI и исправления.

```text
python -m Scripts.StructTrain.TimeLearner analyze /path/TimeLearnerTrainingDynamics.log --format branch-dynamics --time-step-hz 2000 --output NEW-summary.json
```

Параметры `--rest-bound`, `--soma-abs-limit`, `--time-step-hz` принимают только
положительные конечные числа и разрешены только этому format. Frequency берётся
из фактической модели. Legacy default envelope1 — диагностическое соглашение,
не требование нулевого rest state или доказательство физических границ каналов.
Порог LTZone из этого soma envelope не выводится.

Сохранены потоковое чтение, полный source SHA256, диапазоны каналов/сомы,
synaptic resistance, declared Type/fallback sign и оценка локального шага
из C, TimeConstant и фактического SynapticInputs. Она не доказывает устойчивость
всей связанной модели. Schema1 Branch не заменяет native observation schema2
и не получает доказательство полных trial windows. Общий результат явно
`validity=unknown`, `classification_verified=false`, `evaluation_verdict=null`.

Исправлены два дефекта. Повреждённый элемент вектора больше не отбрасывается:
его позиция сохраняется, conductance становится nonfinite, gain не вычисляется,
summary фиксирует nonfinite evidence. Корректные записи дают прежние значения.
Общий analyze CLI больше не перехватывает OSError в ветке invalid data: missing
input/занятый output дают process_error/unknown, прежний файл не меняется.

Первоначально на каждом worker19/19 проверок:6 прежних регрессий,8 новых production CLI/
corruption/parity checks и5 прежних CLI checks на реальном native domain preview.
Полный архивный analyzer загружается отдельно из Git; тела функций в тестовую
копию не извлекаются. Сравнены все summary fields и parse result корректного
формата при2k/20kHz/другом envelope, сохранность input, работа из другого cwd,
NaN/Inf/пустые/повреждённые токены, неизвестная схема и output collision.

Первый M40 запуск:14 dynamics checks прошли,3 из5 domain CLI checks упали,
поскольку выбран raw preview другой схемы. Эта неудачная попытка сохранена;
после выбора настоящего native_resistance_domain_evidence19/19 прошли.
Расчёт новых моделей не запускался; эти Python проверки не называются ASan
проверкой алгоритма и не закрывают научную/integrator/lifecycle матрицу.

Primary proofs: Elder `5ca83feee49dd64346b0dc21c76389c0a8a0b95f` (4 members /
8296 xz bytes), M40 `4ed709463760dd77595c2d09be6cb1e16fafaa8d` (8 members /
8860 bytes, обе попытки). Оригинальный модуль и точный domain fixture входят
в сжатые пакеты; outer/member hashes проверяются при приёмке.
[Elder](../../../Reports/StructTrain/TimeLearner/s09-branch-dynamics-migration-elder-a1/README.md),
[M40](../../../Reports/StructTrain/TimeLearner/s09-branch-dynamics-migration-m40-a1/README.md).
Bin accepted develop merge `6304b4a2bc4117c54c185a917850c7f65771c163`.

Дополнительная граница snapshot: `analyze_file` сравнивает inode/device/size/
mtime до и после чтения. Дописываемый/заменённый файл отвергается с
`dynamics_source_changed_during_analysis`, вместо смешения хеша прочитанного
содержимого с новым размером файла. Статистики корректного закрытого файла
не изменены. Test выполняет реальную запись в читаемый временный файл;
не проверяет лишь копию условия guard.

Окончательный код `71df641bbbb61aca9cd3a12667178caeb036d099` прошёл20/20
на каждом worker (6 прежних +9 migration/CLI/corruption +5 native-preview CLI).
Final primary: Elder `f4348013736477ce7c7a88b57ce972f89fbf3ff7` (4/8336B),
M40 `860537391b22528e9afc26e44a54b6ec09be75c2` (4/8420B).
[Elder final](../../../Reports/StructTrain/TimeLearner/s09-branch-dynamics-migration-elder-a2/README.md),
[M40 final](../../../Reports/StructTrain/TimeLearner/s09-branch-dynamics-migration-m40-a2/README.md).
Первоначальные19-check proofs и неудачная M40 попытка не удалены.

Дополнительно проверен настоящий archived C++ лог BR480 от14.10 на M40:
595939433B /26917 telemetry records. Извлечены первые16 и последние16 полных
schema1 записей с line numbers, byte offsets и SHA256 каждой строки. Полный
исходник прочитан для SHA256 и проверен неизменным; это выборка, не полное
наблюдение эксперимента. Последний срез содержит180 каналов /90 мембран.
Все summary fields старого полного модуля и нового production analyzer
совпали для каждого среза; общий CLI отработал с validity=unknown.
Это дополняет синтетические regression/parity cases реальным C++ форматом.
Частота2000Hz взята из исторической команды, effective native model заново
не проверялась. Ни нового Train, ни научного PASS здесь нет.

[Actual trace proof](../../../Reports/StructTrain/TimeLearner/s09-branch-dynamics-actual-native-a1/README.md),
commit `d5cc8b2c504696e128eba6dc89b60d67c35a4db1`:5 members /40656 xz bytes.
Полный595-МБ лог остаётся на M40; в Git достаточно selected raw slices,
CLI summaries и provenance для воспроизводимого анализа этих32 строк.

Миграция остальных активных инструментов Bin, исторических Python Docs,
Reports receipt runners и всего этапа9 остаётся открытой.
