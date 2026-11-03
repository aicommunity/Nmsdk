# Перенос положительных N1-моделей в frozen recognition

Уточнение03.11: сохранённые модели имеют изменённый integration-профиль с
отдельной LT-мембраной. Это не stock `NSPNeuronGen` и не августовская физика.
[Источник LT и исправление научной постановки](ScientificProfileDrift.ru.md).

## Цель и исходное доказательство

Подэтап следует принятому [measured refinement](MeasuredResistanceRefinement.ru.md),
root develop `ff98c7fef96eb4f947eca756528834877d14492d`, PulseLib develop
`d1c3df4cd0749e5869b977fb5e69417400ce1112`. Оба реальных cold Train при2000 Гц,
двух входах, CapturedPerInput и исходных допусках дали Exact на обоих workers.
Теперь требуется проверить полный native export/import и фактические реакции
зафиксированных моделей, не переносить Exact в научный PASS.

Train повторно не выполняется. Используются реальные завершённые пакеты и все
их source probes из `s07-native-n1-refined-{normal,asan}-a1`. Original models,
references, geometry/Rs и порог не меняются. Source corpus проверяется до/после.

## Явный протокол

- Для каждой topology выполняется штатный CLI `export`, conversion identity.
  Этот выбор не проверяет historical Branch parallel rescaling и PostTune.
- Затем native CLI `evaluate` импортирует полный recognition package и
  замораживает модель/порог. На выходе сравниваются model-before/model-after,
  сохранённый source Solo и фактические параметры средствами production audit.
- Target из metadata обученной модели и protocol hash: ISI `[0.01,0.03]`.
  Семь явно объявленных foil ISI: первый интервал0.01, второй
  0.015,0.02,0.025,0.04,0.05,0.08,0.15 секунд.
- Восемь циклических порядков по восемь паттернов: target в каждой позиции.
  У каждого предъявления собственный trial ID; одинаковый sample ID относится
  только к тому же pattern hash/label. Всего64 пробы на модель,128 на worker.
- Reset-per-trial, окно0.4 s, не более805 отсчётов,2000 Гц. Wall budget1800 s
  на native operation и200000 model ticks на evaluation заданы раздельно.
- Порог унаследован из Solo без калибровки. Target hit оценивается после onset
  до конца полного окна; любой foil spike считается FP, ранние/поздние target
  spikes учитываются отдельно. Молчание target остаётся FN независимо от TN.
- Recording включает реальные stimuli, soma/LTZ samples и spike timestamps.
  Полные временные отчёты обязаны включать каждую пробу/сому и входные импульсы,
  overview и читаемые zoom без downsampling. Полный cache хранится на M40;
  compressed primary, модели, метрики, metadata и выбранные рисунки — в Git.

Это инженерный frozen-контроль порядка и переноса с новым объявленным набором
foils. Независимый научный split не доказан. Восемь детерминированных порядков
не являются восемью независимыми обучениями. Continuous stream/изменение ITI,
другие профили/размерности и подбор порога этим подэтапом не проверяются.
Августовские4/8–6/8 сохраняют собственный исторический протокол и критерий.

## Проверки

Production paths: `native_pipeline_worker`, `learned_evidence`,
`recognition_evidence`, `recognition_metrics`, фактический Console runtime.
Новый corpus `tests/native_n1_handoff_corpus.py` не выполняет работу при import.
Четыре independent reader checks проверяют source/operation closure, полный
набор trials и позиции target, frozen model/threshold, независимость scorer от
порядка строк и отказ для пропусков/дублей/censoring. Успех этих checks не
требует положительной классификации: отрицательные реальные метрики сохраняются.

Producer source `764a8faca30d241ea2d3364141a473c4302e7180`;
reader/renderer `58fd12cf6a5e356530ca48172948c6fc68805164`.
Новые численные сборки не создаются: используются проверенные immutable runtime
root `6ab3b0b3953b132c54a0c4db3662cec80f7f81b9` / PulseLib
`521df5450c3655e0f08b3a01a7aed7d18351c250`, normal a3 и ASan a2.
ASan leak detection выключен.

## Адресный результат

Подэтап принят корневым develop merge
`7ba19818740e91a810112232b6cc9edb2f95decc`; дочерние gitlinks не менялись.

На каждом worker завершены4 реальные owned операции (2 export и2 evaluate),
128 полных проб;4/4 primary reader checks. Wall time normal93.36 s,
ASan300.26 s. При неизменённом пороге1 обе topology дали TP0/FP0/FN8/TN56:
87.5% accuracy объясняются молчанием всех паттернов, target hit rate0.
Сходимость Train не превращена в сертификат recognition; RecognitionCertificate
остаётся null. Положительный результат здесь — корректный полный перенос,
frozen state и достоверное измерение отрицательного распознавания.

Первые попытки a1 на обоих workers были отклонены guard окружения до запуска
Console: отсутствовал QT_QPA_PLATFORM=offscreen. Их receipts сохранены вместе
с исправленными a2; это setup failure, а не ошибка модели и не научный результат.

Primary proofs: normal `34c628d011df939de77a3f403d616fad3a035df2` (669 members,
102699638 raw bytes →1876396 bytes xz), ASan
`121b470640cfab1460759bdcff66a8cf19d0b6cc` (670 members,102875411 →1903084).
Все134 native frozen trial/model/evaluation JSON совпали по значениям между
workers, runtime manifests остаются отдельными; это не независимые обучения.

Полные temporal reports содержат192 пары trial/soma,3 production report checks,
535 source files не изменены. Все22 выбранных PNG прямо просмотрены1920x960:
overview всех8 паттернов каждой topology, zoom target и вторая сома Classic.
Visual source `c3436e46da977993827eefb2f39e7ac306d658f8`, отдельный selected QA
в `Reports/StructTrain/TimeLearner/s05-positive-n1-handoff-visual-a1`.
Полная ручная проверка cache не заявлена.

Отдельная [реальная сетка порогов](PositiveN1Calibration.ru.md) проверена
и принята в root develop `fa53680d62ce9dedbee464fc55418dd3f76a0ca6`.
Лучший реально измеренный target-detecting кандидат даёт5/8 (TP1/FP3/FN0/TN4),
строгая калибровка на сетке NonSeparable и исходный порог1 восстановлен.
Offline LTZ maxima предложили точки; классификацию измеряли реальными
spiking runs. Глобальная физическая неразделимость не доказана.
Полные исходные этапы5/8/11 остаются открытыми.
