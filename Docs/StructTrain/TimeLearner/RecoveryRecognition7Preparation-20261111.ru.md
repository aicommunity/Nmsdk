# Подготовка распознавания из recovery model7

Новая реализация ещё не принята серверными проверками. Текущая native18
сборка использует неизменный rootbdefc540/Pulse1110808 и этих добавлений не содержит.
Они предназначены для отдельного следующего source и набора.

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
