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


## Inherited-image profile: адресная normal-проверка

В PulseLib добавлен RegisterFeedbackStorageProfile: цепочка существующих
membrane/neuron образов, с изменением только выбранного gain и class names.
Полный физический рецепт RegisterStorageProfile не применяется: в stock
effective graph, например, DissociationTC отличается от default такого рецепта.
Нельзя приписывать его неявную замену эффекту обратной связи.

Подготовлены четыре native функции: нестандартные C/кинетика, growth и
коллизии; invalid/no-LT preflight; Classic/Branch stock-image single-pulse
controls на2000/20000Гц с inherited/explicit2/explicit0. Дополнительно два
reader tests используют actual_model_identity каждого native control и
production audit_profile_delta для строгого сравнения всех остальных полей.
Эти функции и actual graph readers прошли адресную проверку ниже. Они не являются переносом
конкретных опубликованных stopped моделей с порогом0.0117: engineering
порог1e-6 и отдельная fixture-морфология обозначены явно.


Адресная проверка нового inherited-image пути [завершена на M40](InheritedFeedbackProfileJobs.json).
[Сверенная приёмка](InheritedFeedbackProfileNormalVerification.json):22/22 native
за110.494с и15/15 readers без skips,200 primary members/588892B и783 hashes
исходников сверены с Git. Группа процессов закрыта, lease released, три прежних
runtime сохранили byte hashes. Primary commit
b157fd3f9b6dd6ec3f82e48f68c5ff0a57e41a4f.

Native waveform и LT timestamps исходного stock image и explicit2 совпали;
explicit0 даёт нулевой Feedback при фактических LT events и другой отклик.
Два actual graph readers подтвердили строгую эквивалентность всех остальных
полей12 inherited control identities с явными class renames. Это реальные
native fixtures, а не прежние JSON mutations аудиторных unit tests.
Нестандартные child C/кинетика сохраняются при growth; отсутствующая LT
не добавляется. ASan/второй сервер, XML новых образов и применение к конкретным
полным archived learned/stopped states ещё не проверены. Научный вывод о
дополнительных пиках опубликованных stock-моделей этим не получен.


## Полный physical-state import через профиль — кандидат

PulseLib ImportFeedbackProfileGraphForEdit строит новый, не подключённый к
owner граф из полного native snapshot. До преобразования source XML проходит
native Load/Init и проверку собственной identity. После проверенных class
substitutions coefficient берётся из derived membrane images; исходные XML
overlays FeedbackGain удаляются штатным USerStorageXML. Никаких записей во
все живые мембраны или Calculate не добавляется. Результат снова проходит
полную native identity-проверку; исходный граф/контроллер не меняется.

Две новые native функции используют Classic/Branch N4,2000/20000Гц, source
порог0.0117 и явно заданные индивидуальные C1.3e-9/Rs93e6. Проверяются полный
перенос, обычный native export/import roundtrip, отсутствие изменений source,
отказ без derived membrane class, при неверном image gain и при повреждённом
source XML даже с пересчитанной XML checksum. Два независимых Python readers
сравнивают actual identities production-аудитором, включая individual C/Rs.
Новые функции ещё не проверены сервером; отклик полученного candidate в этой
проверке не рассчитывается и не объявляется научным результатом. Применение
к полному archived stopped state и paired waveforms остаются следующим gate.
