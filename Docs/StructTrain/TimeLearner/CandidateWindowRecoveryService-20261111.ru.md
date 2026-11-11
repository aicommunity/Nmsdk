# Доставка rejected candidate-window в native service

Статус: новый C++ код и десять real-component integration cases; ещё не
скомпилированы и не приняты на workers. C2 root5643f8319/Pulse0fb035a проверяет
прежний snapshot с service guard и это изменение не подтверждает.

Явная AdvanceRejectedCandidateWindow теперь включает admission factory при
создании свежего native actor. Retry остаётся default. После закрытия группы
service сначала выполняет before-consume sink, проверяет generation/session/
owner, бюджеты, текущий запрос обучения и actual model revision. Только Search
с закрытым RejectedMeasurement допускается к typed core transition. Reference,
Final, partial/nonfinite/budget errors и одна строка причины продвижения не дают.

Service хранит каждую доставленную transition вместе с точным runtime3 этой
попытки. Это producer delivery log, а не доказательство полноты всех событий
контроллера. CandidateWindowRecoveryDeliveryLogIntact означает отсутствие
известной ошибки записи; independent service-ledger completeness остаётся
отдельной незавершённой проверкой. Ошибка записи делает log невалидным, в том
числе после Reset. Control Reset/warm attempt сохраняют записи; retarget/Default
через InvalidateTarget очищают family и log.

Во время доставки удерживаются собственные copies sealed measurement и
rejection, а также shared lifetime текущего search. Если callback сбрасывает
owner/service, старый search может безопасно завершить guard, но не возвращается
в новый контроллер. После callback readbacks и proof validation проверяется
принадлежность к исходной generation. По-прежнему нет вложенного Calculate,
перестройки при каждом тике или передачи ошибок через bool lifecycle методов.

Package6 и summary7 пока явно запрещают экспорт новой policy, исторических
recovery deliveries или повреждённого delivery log. Это относится и к warm
переходу обратно на Retry: он не должен незаметно терять прежние события.
Новая versioned модель/summary, boundary import, Console и сохранение полного
журнала ещё не готовы. Дорогие Train с новой policy пока не запускать.

Адресные cases проверяют Classic/Branch и N0/N1: Missing приводит к следующей
физической точке, original references и delivery bindings сохраняются; каждый
event сверяется с actual record content ID и записывается рядом с полным
archive2/primary. Проверяются warm Retry, Reset/retarget, stop/reset до доставки,
явный отказ прежних exporters. Два дополнительных случая используют штатный
BindNativeTraining и реальные компоненты, внедряя ResetControl только на
public readModelRevision boundary после закрытия группы; выдуманной revision
или копии алгоритма в этих проверках нет.

Следующая приёмка должна включить native positive Missing/Ambiguous DATA joins
через Python reader и проверки общего legacy/composite сервиса. Текущие случаи
не закрывают ambiguous service delivery, C-context recovery, allocation-failure
coverage, interrupted checkpoint или всю обязательную матрицу этапа7.
