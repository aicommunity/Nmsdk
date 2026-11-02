# Build: bool и специализированная диагностика

В UContainer::Build остался путь return build_success с false при пойманном
исключении. Git blame относит переменную и возврат к
Rdk3478e8f080704d6ed092d64d7206d5959915d332 (27.12.2025),
раньше текущего рефакторинга. Это противоречит уточнённому пользователем
контракту Build/Calculate/Reset always true. Новый operation ledger уже
позволяет сообщать ошибку без изменения этих bool.

Добавлен failing-baseline test на реальном storage neuron. Перед ABeforeBuild
вводится однократное исключение. Требуется true, IsReady=false, новая Build
диагностика у learner, затем успешный повтор Build и полноценная native проба.
На исходном Rdk03497edf baseline ca3d6f2b ожидает провал bool assertion.
Elder baseline выполнен: один testcase, единственный failure — returned=false
вместо true. Ready, специализированная диагностика, повторный Build, отказ
в linking при failed Build, положительная связь и последующая проба прошли.
Evidence738985c742f881e3fca3ff23229f68db7d3adf68:33 verified members.
Последующие tests также проверяют реальную связь/отказ при failed
Build и Environment с полным Model либо выбранным numeric component path.
Borrowed environment не меняет владельца графа и не уничтожает его повторно.

При исправлении сохранить порядок hooks/children, Ready=false при исключении,
существующее логирование и специализированный ledger. Потребители bool в
UItem::Connect, UConnector::ConnectToItem, UEnvironment::CreateStructure и
UEnvironment::ABuild должны сохранять смысл отказа через состояние ошибки;
нельзя случайно разрешить связывание после failed Build. Math-классы со своим
независимым Build не относятся к компонентному контракту и не изменяются.

Не распространять ошибки через новые проверки bool и не заменять отсутствие
storage требованием IsReady=true: исторический native no-storage no-op имеет
другую семантику. Общий scheduler и вложенный порядок Build/Reset сохраняются.

Исправление Rdkc3850711b2cd73f33956aae18a8db6cd1c4ead41 находится в feature,
ещё не принято. Build возвращает true; Ready/logging сохраняются. Connect и
CreateStructure используют marker специализированной диагностики. Environment
переносит ошибки отдельного Model ownership root в собственный ledger, сохраняя
существующее поведение ABuild hook. Следующий native gate содержит13 cases
(прежние12 плюс Build), дополнительно требуется9 unit Rdk на обоих workers.
Прежние9/12 результаты относятся к Rdk03497edf и не подтверждают этот patch.
Новая Elder сборка root5d73cd0858abc1e93655d5fa10189225da990201 завершена;
9/9 Rdk unit,13/13 native и4/4 дополнительных explicit0.2 transport passed.
Evidence094bced1b7431e726b052e315eceb2e04e2ad277 содержит37 raw probes,
baseline исправлен: bool true при сохранённом отказе linking и Environment
diagnostics. ASan этой коррекции ещё требуется; develop не менялся.
Docs-only Rdk48d6548e46f3310537a2d8b59fb5be553307a54f
имеет тот же Core tree b204ef8da698476898394aa1d5b6a2679e5a91ed, что numerical c385.
