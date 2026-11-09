# Согласованность подготовки native-проверок

08.11.2026. Это открытая задача этапов9/10, а не приёмка полного runner.
Новый scoped helper должен войти в корневой пакет. Подготовленные вне пакета
worker/supervisor scripts пока не являются целевой архитектурой экспериментов.

## Подтверждённые дефекты

При подготовке `s07-composite-cancellation-m40-asan-a1` обнаружены:

1. Вложенный `archive_contract.source_sha256` содержал hash исходника старого
   Root540 (`05f5...`), хотя фактически выбран Rootcc23 и TU `a35fc01...`.
   Исправлено до запуска, историческая ссылка сохранена отдельно.
2. Старое поле `prior_scope=179` нельзя складывать с27 архивными случаями и
   объявлять248. Активная матрица248 содержит221 неархивный случай и27
   архивных/growth/source controls; архивный leaf запускает23 из последних27.
   Историческая матрица206 сохраняет собственный смысл.
3. Широкая текстовая замена206 на248 затронула три hash-привязки процессов.
   До запуска восстановлены все58 привязок из actual binding JSON;
   baseline служебных OS helpers восстановлен из исходной попытки.
4. Проверка сохранности старого runtime через `assert` внутри `finally`
   могла прервать запись terminal и остальных snapshots. До запуска заменена
   на запись ошибки/дрейфа, `passed=false` и продолжение финализации.
5. После запуска обнаружен оставшийся старый верхнеуровневый `inventory.root`:
   записан540 вместо actualcc23. Исходный файл и live worker не изменяются;
   требуется явная errata и независимый inventory из actual Git.

Фактический source closure, scope и runtime строятся на Root
`cc23d9fff8baba3c5dca89f5e2a0131d7ad1c237` / Pulse
`88ea9c7ab3583da601b1f01ec84bf6f122875a34`. Точные handles и errata находятся
в [индексе заданий](TypedCompositeTrainingJobs.json).

## Обязательное исправление подготовки

Добавить небольшой maintained `native_preparation` helper. Он переиспользует
`source_closure` и `collector_provenance.capture_git_case_inventory`, без
нового C++/Git parser и без отдельного framework запуска кампаний.

```text
capture actual immutable Git closure and selected test sources
derive test IDs and source hashes once
validate declared partition, unique IDs and exact leaf union/order
validate all duplicated root/Pulse/TU/count claims against that capture
validate prior binding records and their digests against retained originals
serialize a typed job specification
verify supervisor embedded worker bytes against the selected worker bytes
reject inconsistency before any source update, build or model run
```

Запрещена глобальная замена чисел/идентификаторов в произвольном script text.
Изменения выполняются в именованных типизированных полях. Исторические SHA,
counts и binding bytes не обновляются вместе с active declaration.
Helper описывает подготовленные условия; он не аттестует compilation,
kernel closure, выполнение assertions или научный результат.

Адресные negative fixtures берутся из сохранённых исходных bytes: старый
root540, nested05f при actuala35, три изменённых binding hashes, ошибочный
count/order, несовпадающие embedded worker bytes. Positive control должен
показывать один согласованный источник root/Pulse/TU/count/order. Проверки
выполняются на сервере; локальный source review не является runtime PASS.

## Интерпретация текущей попытки

Полный producer output сохраняется без исправления raw metadata. Независимый
collector заново выводит248 IDs из actual Git и проверяет реальные compiled
IDs, JUnit, loaded files и source closure. При достаточном доказательстве
можно принять именно фактические C++ assertions этого source snapshot.

Это не закрывает согласованность production preparation/RunManifest.
Ошибочная copied declaration не становится корректной из-за зелёных assertions;
причина, correction и оставшееся ограничение должны быть отдельными полями
отчёта. Текущая техническая попытка не имеет scientific verdict.

После её закрытия helper внедряется и проверяется отдельно; работающие
source/cache/runtime не обновляются ради исправления метаданных.

Подэтап принят на M40:24/24 metadata tests, source5ebb/evidence4ff9,
[квитанция](NativePreparation24M40A1IndependentVerification.json).
Утверждения API ограничены подготовкой данных и указанными проверками;
интеграция actual canonicalSpec в maintained worker и полный248 ещё открыты.
Desired source snapshot может сначала размещаться отдельным preparation-only
шагом в свободном owned workspace. Проверка данных должна завершиться до
сборки/проб; сам helper ничего не обновляет и не выполняет.
