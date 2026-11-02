# Build: bool и специализированная диагностика

В UContainer::Build остался путь return build_success с false при пойманном
исключении. Git blame относит переменную и возврат к Rdk3478e8f080 (27.12.2025),
раньше текущего рефакторинга. Это противоречит уточнённому пользователем
контракту Build/Calculate/Reset always true. Новый operation ledger уже
позволяет сообщать ошибку без изменения этих bool.

Добавлен failing-baseline test на реальном storage neuron. Перед ABeforeBuild
вводится однократное исключение. Требуется true, IsReady=false, новая Build
диагностика у learner, затем успешный повтор Build и полноценная native проба.
На исходном Rdk03497edf baseline ca3d6f2b ожидает провал bool assertion.
До серверного выполнения это постановка воспроизведения, а не подтверждённый
baseline. Последующие tests также проверяют реальную связь/отказ при failed
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
