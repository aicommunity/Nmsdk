# Реальная сетка порогов для положительных моделей N1

Уточнение03.11: это изменённый двухвходовый integration-профиль с отдельной
LT-мембраной, а не исходный stock `NSPNeuronGen`. Реальные измерения сохраняются,
но не заменяют его научную проверку. [Различия и исправление](ScientificProfileDrift.ru.md).

## Постановка

После measured-refinement Train получены реальные Exact Solo модели Classic и
Branch при2000 Гц и двух входах. Последующий native identity export и frozen
Test при унаследованном пороге1 дали TP0/FP0/FN8/TN56 на каждую модель:
восемь паттернов в восьми порядках, reset-per-trial. Это корректный перенос,
но молчание target, а не87.5% успешного распознавания.

Проверяется отдельная следующая операция: **Historical Same-Matrix calibration**
на этих моделях. Общая физика, структура, обученные Rs/C и target references
не меняются; меняется только порог через штатную транзакцию калибровки.
Это не независимый Test и не новая математическая цель структурного обучения.

## Предложение кандидатов и реальное измерение

1. Строго проверить завершённый frozen run, полный source Solo и его Exact
   certificate. Взять восемь различных паттернов первого объявленного порядка.
2. Потребовать реальные complete nonspiking LTZ observations schema2. Для
   каждого паттерна сохранить raw maximum после фактического onset. Значения
   берутся из native `LTZone.Potential`, не из somatic сумм и не из анализа
   произвольно выбранного spiking CSV. Единицы остаются model units/SI unverified.
3. Предложить пороги между соседними различными уровнями,0.9×нижний и1.1×верхний
   уровни; добавить унаследованный порог как silent control. Сетку и source IDs
   зафиксировать до начала поиска. Для текущих восьми уровней получается10 точек.
4. Для каждой точки выполнить **реальный native calibration matrix** на восьми
   паттернах с полными окнами0.4 s. Offline пики задают только предложения и
   не подтверждают spike criterion: порог влияет на физическую динамику.
5. При найденном кандидате production transaction обязана провести свежую
   реальную confirmation с выбранным порогом. При отрицательном исходе сохранить
   исходную модель/порог и отрицательный статус без фиктивного calibrated package.

Native grid: максимум200000 model ticks и1800 wall seconds на operation;
normal/ASan workers и immutable runtime те же, что в положительном N1 Train.
Сетка не обрывается при первом подходящем варианте. Все наблюдения, модели,
источники предложений, actual FP/FN и source-restoration proofs сохраняются.
Полные soma/input temporal reports для всех измеренных matrices — cache на M40;
primary/model/metrics, metadata и выбранные рисунки — компактный Git.

## Ограничения и приёмка

Нативный `NonSeparable` здесь означает отсутствие подходящего порога **в
объявленной измеренной сетке**, не доказанную глобальную физическую невозможность.
Сравнение raw maxima может предложить гипотезу, но не заменяет native search.
Не приписывать результату независимость данных, continuous-stream robustness,
поддержку прочих физических профилей, PostTune или historical Branch scaling.
Не отменять августовские наблюдения: это другая двухвходовая V2 модель/постановка.

Четыре проверки первичных данных: реальный owned import/operation closure;
grid coverage относительно измеренных LTZ peaks; полные real matrices для всей
сетки и честный commit/rollback; запрет terminal claim после удаления кандидата
даже с пересчитанным hash. Production audits используются напрямую.

Producer `4c069e005ee9bc43c34154c4a603e8267b3dfd47`; source и reader получают
отдельные полные SHA в отчётах. Приёмка требует обоих workers, compressed Git
proofs и temporal reports, затем --no-ff merge. Пока эти проверки не завершены,
успех калибровки и качество классификации не заявляются.

## Измеренный результат и границы вывода

На обоих workers завершены2 owned Console операции,20 полных matrices/160
pattern trials. Все10 порогов измерены для каждой topology;4/4 independent
reader checks на worker. Wall time normal373.22 s, ASan662.12 s;
reader252.81/205.86 s. Никакое научное утверждение не выводится из wall time.

| Модель | Лучший измеренный порог с target hit | TP/FP/FN/TN | Accuracy этого кандидата |
|---|---:|---|---:|
| Classic |0.005104094175900908|1/3/0/4|5/8|
| Branch |0.01023534737566667|1/3/0/4|5/8|

Это реальные кандидаты калибровки: response criterion на заданной same-matrix
выборке, не независимый frozen Test и не подтверждённый calibrated package.
При порогах без FP target не обнаруживается (TP0/FP0/FN1/TN7). Ни одна точка
не удовлетворяет строгому target-hit/zero-FP критерию. Обе транзакции вернули
`nonseparable`, `source_restored=true`, `calibrated_package=null`; исходный порог1
сохранён, лучший5/8 не подменяет успешную калибровку. В то же время эти реальные
5/8 не следует стирать словом NonSeparable либо заменять7/8 молчания.

Normal proof `27c5120e06d61be2244fd92111a4b062774880a8`:210 members,
202052941 raw bytes →3253356 xz bytes. ASan proof
`bd2e283bd9410367aa7cb063ac2eaa2a3901839a`:210 members,202114684 →3260224.
Reader `7eac18f6077ec6e9f0d6a77cdf96ce252b69e731`.
Полные native transactions (все160 наблюдений, candidate models и assessments)
и restored models совпали по значениям между workers; runtime provenance
отдельный, независимость научных повторов не заявляется.

Полные temporal reports завершены на M40 из Git-restored normal primary,
renderer `1f2196e673e36007b690b02fceb08185669238c0`:20 матриц /160 проб /
240 trial-soma pairs,3/3 production report checks,206 исходных файлов без
изменений. Wall1156.35 s включает построение и проверки, не model time.
Metadata proof `d13ad580638b00e89a3973aee8fc02d6565c1c2d`:92 members /
502804 xz bytes;28 выбранных PNG /4175776B непосредственно просмотрены
при1920x960. Все8 паттернов обеих топологий представлены с наложением
фактических входов; target и FP имеют50 ms zoom,14.208 px/native tick.
Пики не обрезаны, оси читаются; вторая сома Classic и silent threshold1
представлены отдельно. Полный кэш вручную не принят и в Git не копируется.

[Визуальная приёмка](../../../Reports/StructTrain/TimeLearner/s08-positive-n1-calibration-visual-a1/SELECTED_VISUAL_REVIEW.ru.md)
подтверждает именно измеренное5/8 на same-matrix calibration candidates,
а не успешную калибровку или independent Test. Все outer/member hashes
обоих первичных пакетов (210+210) и metadata (92) дополнительно проверены.
Scoped подэтап принят root develop merge
`fa53680d62ce9dedbee464fc55418dd3f76a0ca6` с неизменными child gitlinks.
Полный stage8, другие режимы/профили и исторический replay остаются открытыми.

SyncTolerance0.02 допускает измеренный остаток около19 ms у исходных Exact
моделей. Это часть объявленной задачи, не причина молча изменить default.
Гипотезы о влиянии допуска, иных физических профилей или торможения требуют
отдельных холодных контролей. Текущие данные не доказывают такую причинность
и не отменяют августовские визуальные4/8–6/8 в ином исходном протоколе.
