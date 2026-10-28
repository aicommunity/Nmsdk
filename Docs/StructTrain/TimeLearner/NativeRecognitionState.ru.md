# Native Solo → Recognition: рабочий подэтап

Ветка `stage08/recognition-conversion` создана от develop с отдельными --no-ff
prerequisite merges рабочей ветки native state / sampling. Это не принятие
prerequisites либо всего этапа 8 в develop. Работающие full/ASan jobs сохраняют
свои исходники, cache и runtime.

## Семантика

`ConvertNativeSoloToRecognition` принимает immutable completed solo package,
импортирует отдельные native экземпляры и строит recognition graph. Исходный
learner, его параметры и storage images не меняются; Calculate не вызывается.
Stopped/partial state и уже преобразованный recognition package не принимаются
как solo. Completed SearchUnresolved допускается с сохранением этого outcome,
без объявления научного результата завершённого успешного обучения.

Поддержаны два явных алгоритма:

- Identity: сохраняет L/Ns/Rs и включает все owned input tips через native links.
- Historical Branch N1: `factor[i]=N*A[i]/mean(A[0..N-2])`, включая anchor;
  `Rs[i]=clip(originalRs[i]*factor[i], effectiveBounds[i])`. Для N=1 преобразование
  не меняет Rs. Положительные references обязательны при N>1; fallback к N при
  отсутствующих/невалидных данных не применяется.

Declared bounds каждого входа пересекаются с native Rm/ratio/configured-floor
ограничениями. Оригинальные Rs, factors, requested/effective bounds, applied Rs
и clipping сохраняются отдельно. Совпадающие Branch banks должны иметь один
совместимый proposed Rs; конфликт не исправляется последним writer. Inhibition
сохраняется как в source (`preserve_source`), что явно записано: это отдельное
преобразование, а не продолжение learning policy масштабирования inhibition.
Индивидуальные изменения не заменяются uniform parent overrides.

После применения выполняются effective parameter readback, реальная explicit
NPulseChannel/NPulseSynapse integration assessment и semantic identity capture.
Весь neuron archive, image closure, Dataset snapshot, source solo package и
conversion spec/record сохраняются в versioned recognition package. Порог
наследуется как fixed, а не как откалиброванный для нового состояния.

## Сертификаты и импорт

Solo training certificate остаётся привязанным к source solo identity, даже
если graph identity после масштабирования другая. Новая recognition metadata
schema 1 требует scope=source_solo и отдельную unverified recognition record
с null certificate. Legacy low-level ModelArchive metadata продолжает читаться
в прежнем compatibility-контракте; новый recognition importer её не выдаёт
за формат нового полного пакета.

При импорте source proof проверяется штатным `PrepareNativeLearnedState`.
Из исходного solo снова выводятся ожидаемые conversion record и fingerprint;
затем загружается именно сохранённый recognition archive через native importer.
Возвращаются только neuron/dataset, без controller/service. Повторный load не
умножает уже масштабированные сопротивления. Mid-probe checkpoint не обещается.

## Приёмка и незакрытая работа

Подготовлены восемь production-path integration scenarios с настоящим Train:
Classic/Branch N0/N1 identity, historical scale, clipping, N=1 и shared N=6.
Они проверяют неизменность source, отсутствие physical ticks при преобразовании,
повторяемость graph/decision, rejection подменённого record или recognition
certificate, native roundtrip и парные frozen waveform traces с реальным
стимулом/ненулевым откликом. В normal A2 все восемь прошли; source primary
audit дал 9/9 Python tests, 108 primary trials и 3519 paired frozen samples
старого fixture layout v0. Native archive regressions: 8 pass / 1 helper skip,
четыре parent tests реально выполняют fresh-process transfer при 2/20 kHz.
Отдельный A3 проверил ещё три cases: incompatible shared-bank conversion,
strict spec codec и запрет stopped→completed recognition; все прошли.

Следующая версия fixture заранее сохраняет declared frozen spec, закрывает
окно по absolute end вместо усечённого duration*frequency и сохраняет actual
sample_count/complete/end и обе model revisions. Положительный контроль требует
изменения потенциала, поэтому постоянный ненулевой rest-state не даёт PASS.
`recognition_evidence.py` независимо проверяет Source solo proof, factor/clipping,
разрешённые изменения graph/bindings, неизменность images и остальных properties,
полноту frozen CSV. Native import и scientific selectivity он не подменяет.
Elder-1 normal A4: все 11 native и 23 Python tests прошли; независимо проверены
восемь recognition packages, 108 исходных training trials и 3528 полных paired
samples schema 1. [Артефакты](../../../Reports/StructTrain/TimeLearner/s08-recognition-elder1/README.md)
опубликованы commit `e235f898596b7fe6e9b5ed6291f15329d45683e2`; локально проверены
336 stored / 334 raw hashes. Старый fixture v0 не получает полноту schema 1
задним числом. ASan A4 M40 пока работает; новый source не принят в develop.

Проверки выполняются только на workers. Normal адресная проверка завершена;
полная приёмка этапа и ASan A4 ещё не завершены. Первая normal сборка A1 прошла; первый fixture затем
упал в сравнении QJsonValueRef: test lambda возвращала ссылку на элемент временного
QJsonObject. Рабочая правка возвращает самостоятельный QJsonValue; production
conversion math этим не меняется. A1 сохраняется как crash, не как пройденный test.
PostTune transactions, реальная калибровка порога,
независимый evaluation protocol/scorer, вся physical/mode matrix и подключение
production runner остаются открытыми требованиями полного этапа 8.

Свежий процесс recognition import добавлен как отдельный replay fixture,
который получает опубликованные package/spec, создаёт штатный NModel без learner,
загружает native graph и возвращает single-model waveform с тем же absolute
началом окна. Его нужно отдельно собрать и сравнить с исходной paired trace
на обоих workers; наличие fixture не является доказательством переноса.
