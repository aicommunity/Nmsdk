# Имена квитанций и ссылок внешнего архива

Проверка production publisher на исходном root bc81b4c4bd953e310d13aad3626414d495bf8f9b
выявила пять составных квитанций с суффиксом `.archive.json`. Этот суффикс
зарезервирован для одного `nmsdk_structtrain_external_object` с точными
bytes и SHA256. Составные документы закономерно отвергались с причиной
`archive_reference_schema`; отказ не был ошибкой алгоритма обучения.

Пять квитанций переименованы в `.json` без изменения их содержимого.
Обновлены Markdown-ссылки. Каждая вложенная ссылка на object получила
отдельный строгий marker в
`Reports/StructTrain/TimeLearner/PublishedDependencies-20261117`.
[Реестр переименований и исходные hashes](PublicationReceiptNaming-20261117.json)
сохраняет прежние пути и связь с исходным commit.

Правила validator не ослаблены; физика, численные результаты, исходные
архивы и выпущенные DOCX не изменены. Полный новый Git tree
97342b5ff1c9136253c1c1b1e3af82cbff35930b принят production
`verify_experiment_tree`:71995 markers,411.097с wall, включая фактические
bytes и SHA256 внешних objects. [Квитанция приёмки](FiniteScienceAcceptance-20261117.json)
содержит внешний ref исходного gate result. Дополнение описания N0 после
этого commit изменяет только Markdown, не измерения или алгоритм.
