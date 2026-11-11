# Подготовка частичной Git-проекции кода

В M40 execution5 DATA A1 исходные тесты не выполнялись: guard чистоты кода
остановился на отсутствующем Git blob корневого .gitignore. Ранее checkout
отказал на .gitattributes. Ошибки связаны с неполным набором объектов
транспортного pack, а не с доступом SSH или алгоритмом модели.
Первый недостаток .gitattributes был дополнен до первой source проверки;
первоначальные outcomes не заменяются успешным тестовым результатом.

Новый production инструмент Scripts/StructTrain/TimeLearner/git_source_projection.py
строит pack по точному commit SHA и явным префиксам, включая все Git trees,
выбранные blobs и все .gitattributes/.gitignore/.gitmodules blobs независимо
от sparse selection. UTF-8 имена разбираются без кодировки окружения; читаются
и проверяются также policy blobs. Output создаётся исключительно новым файлом.
Наличие pack не удостоверяет полную SDK, native execution или научный результат.

Пример metadata-only подготовки:

```text
python -B -m Scripts.StructTrain.TimeLearner.git_source_projection REPOSITORY FULL_COMMIT_SHA NEW_OUTPUT.pack --prefix Scripts/StructTrain/TimeLearner/
```

Три серверных теста проверяют настоящий Git init/pack/index-pack/sparse checkout
и git status --untracked-files=all без доступного promisor remote, UTF-8 имя,
доступность policy blobs вне выбранного поддерева, отсутствие лишних файлов,
new-only output и отказ неверного SHA/unsafe/пустого selection.
После доставки необходим тот же strict source guard, который использует
owned_python_job; проверка только tracked status была недостаточной.
Приёмка реализации и повтор execution5 DATA пока не выполнены.
