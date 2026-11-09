# Новая подготовка corrected33 после include-дефекта

Предыдущий job остановлен на реальной компиляции:0/33 tests,0 leaves; negative `e79b071271b7a6ef37d04d0d1b3035073ab3e318` сохранён и независимо проверен. Две отсутствовавшие декларации исправлены общим direct include ProbeEvidenceJson.h, без изменения математики/fixture/четырёх deliberate-unfixed реализаций.

Новые source-only SDK: corrected `807da9b50835f4da61cda1e069d3b4d7e750b8c8` / Pulse637; unfixed `dae63c62e98d1e1e907a2443f116f8432e948264` / Pulse81ec. В каждом8cleanrepos,4020Git-byte files,29sameSDKimports; A1→A2 отличается только один общий include-файл. Между парой сохраняются ровно4implementation differences. Старые source/cache/runtime не заменены.

Canonical A2 оставляет33 cases/22leaves,130primary rules,15profile tokens и прежние limits; добавлены19protectedroots и2priorbindings, включая закрытый failedA1. Это подготовка без CMake/native/model выполнения, scientific verdict отсутствует.
