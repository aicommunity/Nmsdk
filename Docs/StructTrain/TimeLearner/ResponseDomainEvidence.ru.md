# Независимая проверка portable domain evidence

Production codec PulseLib `Core/TimeLearner/ResponseDomainEvidenceJson.h/.cpp`
связывает успешно закрытый capture, сохранённый native result, declared domains
и канонический primary CSV. Новый формат — отдельный diagnostic packet schema1,
не изменение schemas1–6 штатного ProbeObservation.

Capture хранит собственную closure; encoder повторно вычисляет analysis и
проверяет точные CSV bytes. Нельзя передать чужие native result/analysis.
В native fixtures CSV пишется NewOnly, flush/readback проверяется до encoder.
Рядом сохраняется JSON с hash/размером primary, полным native evidence,
mapping каналов, measured maxima, plateau/source indices, signed offsets и
причинами отказа. Полные samples находятся только в CSV.

Независимый consumer: `Scripts/StructTrain/TimeLearner/response_domain_evidence.py`.
Проверка должна связывать context и actual stimuli с CSV и заново вычислять
features/graph. Исключительность окна не становится доказательством causal
origin. Physical path mapping без отдельного effective graph не считается
независимо подтверждённым; OS/runtime provenance проверяется внешним runner.

Полная серверная приёмка codec/reader ещё не выполнена. Первоначальные 7 integrity
и4 native cases прошли на Elder, но относятся к предшествующему снимку:
[receipt](NativeResponseDomainInitialVerification.json). В нём review нашёл
недостаточную сверку измерений replay. Исправленная версия сравнивает все
поля peaks и burst assignments; добавлен отрицательный тест подмены амплитуды.
PASS старой версии на новое усиление автоматически не переносится.

Следующий gate должен включать8 integrity checks,2 codec checks,4 native
Classic/Branch cases на2000/20000 Гц и независимый Python reader с mutation
tests. ASan/native на M40 и расширенная fault/N=1/4/6 матрица остаются
отдельными требованиями. Ни этот пакет, ни его receipt не подтверждают
завершённый Train, научную классификацию или полный этап7.

На M40 прошли12/12 тестов reader без skipped. Все23 члена архива и467
Python source bindings сверены с Git; идентификаторы тестов сверены с исходным
inventory и журналом. [Независимая квитанция](ResponseDomainReaderM40Verification.json),
evidence `b07c853b84873791d05a3cb87f149492a4839ecd`.
Это independent fixture tests, пока без проверки пакетов C++ producer.
На Elder первая попытка reader отказала до тестов из-за занятой capacity;
ограничение не обходилось. C++ codec10 прошёл, native4 ещё выполняются.
[Задания](ResponseDomainEvidenceJobs.json).

Review выявил конфликт имён старых и новых native fixtures при совместном
output directory. Исправление добавляет `_domain_capture` в trial/artifact
identity. Текущий compiled root0e3d5bca предшествует этому изменению; нужен
отдельный совместный filter старого и нового случая в общий свежий каталог.

Перед сборкой Elder обнаружена нехватка диска. Удалены22 неиспользуемых
бинарных файла/библиотеки из двух старых agent runtimes; EventsLog, ini,
исходники и primary не удалялись. Свободное место выросло с660692992 до
1408937984 bytes. Отказ первоначального задания сохранён; новое использует
отдельный attempt/runtime. Metadata очистки сохранены на сервере в
`readbacks/s00-runtime-space-recovery-elder-20261108-a1` и должны войти
в итоговую публикацию этого подэтапа.
