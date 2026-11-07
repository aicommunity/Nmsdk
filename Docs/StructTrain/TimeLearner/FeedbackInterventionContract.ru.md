# Проверка состава вмешательства в обратную связь

Адресно проверенный аудитор этапов4/7/11. Production auditor feedback_intervention.audit_profile_delta
сопоставляет два полных semantic model identity с проверкой собственных hash.
Baseline reconstruction допускает только явно объявленное взаимно однозначное
переименование storage-классов. Uniform-feedback режим дополнительно требует
объявленного конечного неотрицательного gain во всех фактических мембранах,
включая существующую LT membrane. Новая LT membrane не создаётся.

Не исключаются из сравнения индивидуальные Rs/C, кинетика, averaging, threshold,
граф связей и ports, caches, порядок расчёта и timestep. Изменение любого
необъявленного поля запрещает положительный delta audit. Connected gain,
дубли path, stale hash и неиспользованные rename entries запрещены.

Аудитор не создаёт и не изменяет компонентов. Его вывод не доказывает native
import, соответствие storage image closure, сохранность после growth или
waveform equivalence. Эти флаги остаются false; training certificate и научный
verdict отсутствуют. Нельзя выдавать успешную проверку JSON за causal result.

Server tests используют обе реальные импортированные stock identities
одноимпульсной серии. Мутации проверяют именно отказ/допуск аудитора, а не
работу изменённой физической модели. [Адресная проверка аудитора](FeedbackInterventionAuditorVerification.json) на M40:
10/10 tests без skips. Все11 primary members и368 source hashes сверены с Git;
обе исходные identities совпадают с опубликованными primary Console-проб.
Процессы закрыты, lease released. Primary commit
1bd9be8f297458760ab2f32fab150744df06b25d. Native intervention и baseline
waveform reconstruction этим не выполнялись.

Последовательность научной приёмки: native storage image variant → native
construction/import → полный effective graph audit → исходный paired baseline
с точным совпадением soma/stimulus waveform → объявленное изменение gain →
paired native probes с каналами и временными графиками. CapturedPerInput,
порог0.0117, индивидуальные параметры, stimulus и reset policy сохраняются.
