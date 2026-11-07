# Точное воспроизведение многопикового отклика, 07.11.2026

**Два low/Retry candidate воспроизведены после полного import и native Reset.**
Все соматические и входные отсчёты совпали точно с исходными пробами Train;
relative clock совпал с действующим допуском округления. Для Classic сохранились
burst_ambiguous/peak_ambiguous input0, для Branch — input2. Ни одна проба не
объявлена валидной ради совпадения, обучение не запускалось.

Это исключает необходимость накопленной динамики предыдущих проб для
получения этих двух конкретных волн. Не устанавливает роль feedback,
одиночного отклика или timestep и не доказывает исправность всего Reset/storage.
Высокий порог, Advance и иные промежуточные модели этой проверкой не охвачены.

## Штатный путь и ограничения

Новый модуль `Scripts/StructTrain/TimeLearner/stock_wave_replay.py` использует
существующий version2 probe job, полный ImportNativeLearnedState и production
runner. Первая невалидная проба выбирается из исходной истории. До запуска
требуется точное равенство её base revision, source model revision и archived
graph hash. Если candidate отличается от конечного stopped state, инструмент
отказывается от replay: подстановка ближайшей модели запрещена.

Оба jobs записаны до первого native запуска. Actual import identity проверена;
controller остался idle и неизменным, model graph/parameters заморожены.
Физика, minimumAmplitude, порог и ordered-whole-burst критерий сохранены.
Полный цикл выполнялся в отдельной contained группе на M40 с read leases
исходного runtime; source/build/runtime работающих заданий не обновлялись.

```text
python -m Scripts.StructTrain.TimeLearner.stock_wave_replay STUDY \
  --runtime RUNTIME_MANIFEST --output NEW_DIRECTORY
```

STUDY — полная восьмиусловная recovery study с original primary siblings.
Команда исследует два low/Retry controls, а не запускает обучение или всю
научную матрицу. Самостоятельный CLI передаёт управление production runner;
на сервере его следует запускать через managed worker с лимитами и leases.
Import модуля сам по себе ничего не запускает.

## Приёмка

[Verification](StockWaveReplayVerification.json): шесть адресных серверных
проверок без skips, две реальные native пробы;227 members/1003484B xz.
Tool root e7379b4beed7be6454cd0cb85356972da85d4423; compiled SDK root36f598 /
Pulse8f057, тот же runtime, что исходный Train. Это разные identities:
изменение Python-инструмента не выдаётся за новую C++ сборку.

Тесты проверяют обе топологии, выбор первой invalid, отказ при несовпадении
более раннего candidate/graph, отсутствие invalid и повреждённый CSV.
Self-comparison проверяет путь сравнения; его нельзя считать третьим native
replay. Две реальные пробы отдельно подтверждены process/run manifests.
Все процессы закрыты, lease released. Нет ASan/второго сервера в этой приёмке.

Артефакты сохранены в Git evidence1abdfa87c257fa7aa732353ae05d7c89c7fd0fa9,
`Reports/StructTrain/TimeLearner/s07-stock-wave-replay-normal-m40-a1`.
Каждый member и tool source hash сверены с Git. Архив включает фактические
пробы, input snapshots, source/graph/clock readback и результаты тестов.
[Временные графики replay](StockWaveReplayVisualVerification.json) завершены:
пять trial/soma pairs,251 view; шесть PNG проверены вручную. Полный cache
остаётся на M40. All-pattern графики предыдущей серии этим не заменяются.

[Аудит участка до второго импульса](StockFirstPulse.ru.md) установил три
максимума Classic ещё до следующего предъявления. Следующий шаг — Exc/Inh/LT
диагностика; отдельная single-pulse characterization остаётся открытой. Отождествлять число локальных
максимумов с числом физических откликов пока нельзя. Этап7 и общий план открыты.
