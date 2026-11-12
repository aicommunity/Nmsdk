# Сравнение версий Qt между тестом и штатным приложением

## RU

## Обнаруженная проблема

**Несовместимость версий Qt библиотек!**

### Версии Qt

| Компонент | Тест (vcpkg) | Штатное приложение |
|-----------|--------------|-------------------|
| Qt5Core.dll | **5.15.2.0** | **5.15.10.0** |
| Qt5Gui.dll | **5.15.2.0** | **5.15.10.0** |
| Qt5Widgets.dll | **5.15.2.0** | **5.15.10.0** |
| Qt5Svg.dll | **5.15.2.0** | **5.15.10.0** |

### Разница версий

- **Тест**: Qt 5.15.2 (из vcpkg)
- **Штатное приложение**: Qt 5.15.10 (более новая версия)

## Почему это важно

Между Qt 5.15.2 и Qt 5.15.10 могли быть изменения в:
1. Обработке типов возвращаемых значений `QMessageBox::question()`
2. Поведении модальных диалогов в Windows
3. Обработке типов при прямом сравнении enum значений

## Выводы

1. **Тест проходит** потому что использует Qt 5.15.2, где прямое сравнение может работать
2. **Штатное приложение падает** потому что использует Qt 5.15.10, где поведение могло измениться
3. **Исправление в коде правильное** - использование `QMessageBox::StandardButton reply = QMessageBox::question(...)` должно работать во всех версиях Qt

## Рекомендации

1. ✅ Исправление в `UGEngineControlWidget.cpp` правильное и должно решить проблему
2. ⚠️ Для полной уверенности нужно протестировать исправленный код со штатным приложением, использующим Qt 5.15.10
3. 📝 Возможно, стоит обновить Qt в vcpkg до версии 5.15.10 для консистентности, или использовать ту же версию Qt, что и в штатном приложении

## Следующие шаги

1. Протестировать исправленный код в штатном приложении с Qt 5.15.10
2. Если проблема сохраняется, проверить другие возможные причины
3. Рассмотреть возможность обновления Qt в vcpkg или использования той же версии Qt для тестов

---

## EN

## Discovered issue

**Incompatible Qt library versions!**

### Qt versions

| Component | Test (vcpkg) | Production app |
|-----------|--------------|----------------|
| Qt5Core.dll | **5.15.2.0** | **5.15.10.0** |
| Qt5Gui.dll | **5.15.2.0** | **5.15.10.0** |
| Qt5Widgets.dll | **5.15.2.0** | **5.15.10.0** |
| Qt5Svg.dll | **5.15.2.0** | **5.15.10.0** |

### Version difference

- **Test**: Qt 5.15.2 (from vcpkg)
- **Production app**: Qt 5.15.10 (newer)

## Why this matters

Between Qt 5.15.2 and Qt 5.15.10 there may be changes in:
1. Handling of `QMessageBox::question()` return types
2. Modal dialog behavior on Windows
3. Type handling on direct enum comparison

## Conclusions

1. **Test passes** because it uses Qt 5.15.2 where direct comparison may work
2. **Production app crashes** because it uses Qt 5.15.10 where behavior may have changed
3. **The code fix is correct** — `QMessageBox::StandardButton reply = QMessageBox::question(...)` should work across Qt versions

## Recommendations

1. ✅ The fix in `UGEngineControlWidget.cpp` is correct and should resolve the issue
2. ⚠️ For full confidence, test the fixed code with the production app using Qt 5.15.10
3. 📝 Consider updating Qt in vcpkg to 5.15.10 for consistency, or use the same Qt version as the production app

## Next steps

1. Test the fixed code in the production app with Qt 5.15.10
2. If the issue persists, check other possible causes
3. Consider updating Qt in vcpkg or using the same Qt version for tests
