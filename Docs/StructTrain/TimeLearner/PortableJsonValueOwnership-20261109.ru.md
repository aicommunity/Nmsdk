# Владение JSON-значениями при portable replay

Статус: исправление в исходниках, без заявления о пройденной сборке или runtime-проверке. Общая Pulse-ветка `f7a0e3e63ec29d4647790a695606d1ca32164ef3` продолжает compile fixes637/de26. Это исправление времени жизни данных, а не изменение цели, окон, допусков, физики или порядка scheduler.

## Подтверждённые дефекты

1. `CandidateWindowPortableReferences.cpp`, `CandidateWindowPortableReferenceFactory::Replay`: `auto` сохранял результат mutable `operator[]` временного объекта `toObject()`. После окончания выражения proxy `QJsonValueRef` обращался к уже уничтоженной обёртке. Чтение массива начальных параметров заменено на owning `.value("parameters")`.
2. `CandidateWindowProposalReplay.cpp`, lambda `binary64`: функция `parameter(...)` возвращает `QJsonObject` по значению. Сохранение `auto ...["value"]` давало такой же proxy к временному объекту. `.value("value")` сохраняет самостоятельный `QJsonValue`; проверки типа строки, canonical hexadecimal binary64, конечности и положительности сопротивления остаются прежними.
3. `Test_PulseLib_CompositeTraining.cpp`, `NativeCandidateWindowBudgetReplay/RetainedGroupsCannotReverseIssuedOrder`: `const auto first=r[0]` сохранял изменяемый proxy. После первой записи в массив он уже обозначал второй record, поэтому тест создавал дубликат вместо перестановки. Теперь используются owning-копии обоих значений, проверяются непустые различные group IDs и фактический обмен. Decoder должен отказать именно с `candidate_window_archive_group_order`, а не с произвольной ошибкой дубликата.

На M40 прочитан фактический `QtCore/qjsonvalue.h`: в используемой ветви Qt ниже7 proxy хранит `QJsonObject*`/`QJsonArray*`, а не владеющий экземпляр. Это source evidence; локальная компиляция или выполнение фрагментов не применялись. Такой вывод нельзя автоматически переносить на другую реализацию Qt.

Не являются новыми дефектами просмотренные выражения, где `toObject()/toArray()/toString()` выполняется до конца полного выражения и возвращает владеющий результат. В частности, `ModelArchive.cpp::ValidateMetadata` получает `identity` как `const QJsonObject&`; условное выражение `expectedIdentity` приводит оба плеча к owning `QJsonValue`. Эти места не переписывались.

## Обязательная проверка на серверах

Сохранить прежние33 controls и дополнить их настоящими production-путями:

- `NativeCandidateWindowArchive/ClassicActualPrimaryReplaysCompleteReferencesAndProposal`;
- `NativeCandidateWindowArchive/BranchActualPrimaryReplaysCompleteReferencesAndProposal`;
- `NativeCandidateWindowArchive/ActualBoundC0MapsReplayedWithoutFakeBaseline`;
- исправленный `NativeCandidateWindowBudgetReplay/RetainedGroupsCannotReverseIssuedOrder`.

Это37 выбранных assertions при сохранении исходных33, а не число всех тестов бинарника или всего source suite. Точные source selections, исключённые cases, output collision review, budgets и compiled inventory должны быть заново получены production preparer. Новые пути создают исходные native primary и вызывают реальные archive decoder/reference replay/physical graph validation; извлечение функции в тестовую копию не является проверкой.

Использовать ASan-профиль с сохранением actual flags. Проверить полные all-input references, proposal replay, strict rejection перестановки, source/runtime hashes и закрытие собственного задания. Сохранённый partial build разрешён только после завершения прежнего задания и фиксации его отрицательного результата; явно маркировать incremental reuse и записывать cache/object/flags переход. Ни один текущий работающий source/runtime не обновлять.

Поправки одинаково применяются к corrected и deliberately-unfixed lifetime-веткам. Их прежние различия сохраняются; общий owning fix не должен становиться скрытым исправлением отрицательного контроля.

Эти новые файлы portable replay отсутствуют в принятом baseline Pulse4a. Нельзя задним числом объяснять ими августовские4/8–6/8 или прежние stock-эксперименты на других commits. До отдельной серверной проверки не заявлять, что устранены наблюдавшиеся научные ошибки, получен Train certificate или закрыт весь этап5/7.
