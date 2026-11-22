# Следующий cold Branch: один полный проход

На Elder17.11 в17:51UTC подтверждены running owner и native child
`s10-single-complete-sweep-branch-elder-a3`. Controls commit
ccb172580062996b16521530207edd18a02d191c. [Декларация и параметры](../../../Reports/StructTrain/TimeLearner/SingleSweepCold-20261117/elder-control.json).
Проверенные источники: Scriptsfce044eab6df1f7bc25356cf47fef5ef65e704b7;
native Root0efbf25b074ca4dcf8439dde8160fa9e70697376,
Pulse5dabcb1b0c627d1de52bf2dccec35f33cb755e92. Immutable runtime
d480a889fa70dd9511ed86667884b453af89a7571ebc6385f27b7f48592e7d83.

Это холодное обучение из исходного профиля, не продолжение stopped-модели.
Template восстановлен из внешнего primary6a86940f…,
member s10-finite-train-native-m40-a2/branch/input/job.json,
SHAe8899a3bd7f02cdcebd10cfb96bd69760a672e1dc902cc674968646e530c5067.
Модель N4/N1 Fast3, исходные L1/Ns1/Rs86M, f2000, полная штатная пачка.
Образы, физика, assigned peak, CapturedPerInput и исходные допуски не меняются.

Бюджеты объявлены до запуска: local cap24, global160, sweeps1,
model10000с, whole wall84600с, group model20с/group wall1800с.
Валидный полный путь ограничен154 search probes +4 references,158 группами
и948 native предъявлениями. Group/native/sample capacities проверены;
фактическое завершение всё ещё может ограничиться wall/model/invalid budgets.
Контроль увеличивает group wall по измеренной причине предыдущего Classic:
601.1605 реальных секунд оборвали шестую native пробу, несмотря на расход
лишь8.8165 модельных секунд. Автоматического увеличения после старта нет.

Owner8GiB/native16GiB, reservation24GiB, один worker slot. Output ceiling1.5GiB,
free floor1GiB на Elder; finite owner проверяет их во время исполнения.
При недостатке ресурсов сохраняется явная ошибка исполнения, а не PASS.
Две не допущенные подготовки a1/a2 не создавали процессов расчёта; a3 отдельный
Git control, namespace и run identity. M40 cap16 pair не перезапускался.

Гипотеза: один обеспеченный проход достигает каждого регулируемого входа
и свежего all-input gate, не начиная следующий частичный sweep. K24 выбран
потому, что предыдущее Branch-измерение впервые достигло joint допуска на24-м
кандидате входа2. Это не обещание сходимости, признание физической оптимальности
или замена полного best-graph checkpoint. Несколько execution factors меняются
явно; причинный эффект одного из них этим опытом не изолируется.

После закрытия: проверить фактический outcome, полную модель и current revision;
выполнить8-pattern Test/калибровку по объявленному протоколу. Budget stop можно
исследовать как diagnostic stopped model, без сертификата завершённого Train.
Временные графики Soma со входами обязательны; полный cache вне Git.
