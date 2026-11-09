# Подготовка исправленной парной source-конфигурации

Roothelper a208 объединён обычными merge commits: corrected `2504bb86062867b4028106a120e724b8b86bcb84` / Pulse4b, deliberate-unfixed `7852d259f4abe1744989b4e23c25c1ad868b69c1` / Pulsefeb. В каждом SDK4020 файлов проверены по Gitblob и29 импортов из своего дерева; C++ и gitlinks при helpermerge не менялись. Старые E11/BB1/A4runtime, A4cache и LLAMA byte-identical.

Первый source-update отказал до reservation/checkout из-за file resource; freshA2 с directoryresource выполнен и kernelclosed/released. Donor-only первая передача пропустила root tree; полные exactpacks доставлены до sourceupdate, исходныйmetadata сохранён. Никаких CMake/build/native/model запусков здесь нет.

Подготовлен canonical33:11 codec→2 cold7guards→R20,22 leaves,38 source selection с5 excludedConsole.15 explicit cache entries,130 artifact/JUnit rules; LLAMA read-only protected. Freshbuild budget10800s/whole21600s,parallel2,8GiB reservation/4GiB leaf,16GiB disk. Это inputs для следующего отдельного review и запуска; не runtime/scientific acceptance.
