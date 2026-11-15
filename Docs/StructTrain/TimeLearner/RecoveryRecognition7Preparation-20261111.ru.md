# Подготовка распознавания из recovery model7

**Native-приёмка принята на Elder: 10/10.** Rootca8be945/Pulse1110808, свежая сборка, десять реальных conversions/import и двадцать frozen target/foil trials. [Результат и точные ограничения](ValidationPlans/ElderRecoveryRecognition7Native10A2-20261111/RESULT.ru.md). Полный primary corpus опубликован в Git (4.27MB сжатых данных); [независимый Python replay принят6/6](ValidationPlans/ElderRecoveryRecognition7Independent6A2-20261111/RESULT.ru.md), включая полное восстановление и source/fixture before/after checks. Это технические N=2/Sync0.2 cases, не N4 научная матрица.

Исторический native18 использовал rootbdefc540/Pulse1110808 и этих добавлений не содержал; его частичный исход не подменяет новый native10.

В recognition_evidence.py исправляется dispatch опорных амплитуд Branch/N1:
package7, как5/6, должен читать независимые принятые reference groups, а не
legacy summary.references. Это позволяет проверять completed source7 и
сохраняет CapturedPerInput и фактические per-input clipping bounds.

Общий DATA reader допускает stopped composite для исследования. Обычный
recognition reader теперь отдельно требует timelearner_completed_state и
learned_solo. Даже согласованное переименование diagnostic recognition
и его archive metadata с пересчитанными hashes не должно повышать статус
остановленного источника. Native converter уже имеет это ограничение.

Десять новых real-component cases NativeRecoveryRecognition7 охватывают обе
топологии, N0/N1, completed/stopped, Branch N1 historical conversion и
heterogeneous C0 обеих топологий. Два преобразования одной immutable solo
модели должны иметь те же revision/decisions/parameters: масштабирование
никогда не применяется повторно к live Rs. Импорт, native Build/Init/Reset
и полный public recognition export проверяются отдельно.

Каждый case предъявляет target и foil с reset-per-trial. Не применяется
окно закреплённого Train импульса: сохраняются все samples полного Test
окна, actual input/spike timestamps, все soma каналы и реальный LT Potential.
Из них вычисляются общий максимум каждого soma канала и LT Potential.
Оба trial должны сохранить frozen model hash и source target provenance.
Требований target hit, отсутствия FP или научной разделимости здесь нет.

Новый Python набор test_recovery_recognition7_native.py требует настоящий
закрытый C++ corpus всех10cases, восстанавливает весь primary bundle,
независимо проверяет source7/summary8/CSV и conversion, обе формы import
provenance и все20полных trial. Отдельные отрицательные проверки повреждают
фактор преобразования, status происхождения, spike count и frozen revision.
Приёмка не может быть объявлена по synthetic модели либо отсутствующему
корпусу. Дальнейший Console pipeline и научная матрица остаются отдельными.

Технические fixtures используют N=2 и явно объявленный SyncTolerance0.2 для completed source, как предыдущий package7 roundtrip cohort. Это не default0.02 и не результат научного N4 обучения. Default и математические допуски production не изменяются. На Elder отдельно принят legacy recognition reader/CLI regression14/14 на восьми старых actual models; новый source7 corpus он не заменяет.
