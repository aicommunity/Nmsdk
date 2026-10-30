# Результаты тестов воспроизведения проблемы QMessageBox со стилями

**Дата:** 2025-01-XX  
**Цель:** Воспроизвести падение в QMessageBox::question при применении QSS стилей

## Резюме

✅ **Проблема успешно воспроизведена!** Тест `Test_QMessageBoxStyleCrash` падает с тем же стеком вызовов, что и штатное приложение.

## Результаты тестов

### Test_QMessageBoxStyleCrash

**Статус:** ❌ **CRASH** (падение воспроизведено)

**Стек вызовов при падении:**
```
#  8: QDialogButtonBoxPrivate::layoutButtons() - 0x00007FFE9831CE90
#  9: QDialogButtonBoxPrivate::resetLayout() - 0x00007FFE9831D940
# 10: QDialogButtonBox::changeEvent() - 0x00007FFE9831C8B0
# 11: QWidget::event() - 0x00007FFE97FF04B0
# 12: QDialogButtonBox::event() - 0x00007FFE9831CA10
# 13: QApplicationPrivate::notify_helper() - 0x00007FFE97F7D000
# 14: QApplication::notify() - 0x00007FFE97F76840
# 15: QCoreApplication::notifyInternal2() - 0x00007FFEA59A9D30
# 16: QCoreApplication::sendEvent() - 0x00007FFEA59A7910
# 17: QWidgetPrivate::setStyle_helper() - 0x00007FFE97FFA0C0  ← ТОЧКА ПАДЕНИЯ
# 18: QWidgetPrivate::inheritStyle() - 0x00007FFE97FFA360
# 19: QWidget::setParent() - 0x00007FFE97FEDB40
# 20: QWidget::setParent() - 0x00007FFE97FEDAC0
# 21: QLayoutPrivate::reparentChildWidgets() - 0x00007FFE97FCA910
# 22: QWidget::setLayout() - 0x00007FFE97FED4A0
# 23: QMessageBoxPrivate::setupLayout() - 0x00007FFE9849B930
# 24: QMessageBoxPrivate::init() - 0x00007FFE9849B330
# 25: QMessageBox::QMessageBox() - 0x00007FFE98497120
# 26: showNewMessageBox() - 0x00007FFE9849E040
# 27: QMessageBox::question() - 0x00007FFE984986E0
# 28: TestQMessageBoxStyleCrash::testQMessageBoxWithGlobalStyles()
```

**Анализ:**
- Падение происходит в `QDialogButtonBoxPrivate::layoutButtons()` при обработке события `changeEvent`
- Цепочка вызовов точно совпадает с штатным приложением
- Проблема возникает при наследовании стилей от родительского виджета (`QWidgetPrivate::inheritStyle`)
- Тест использует реальный QSS файл из `Bin/Styles/default.qss`

**Исключение:**
- Адрес: `0x00007FFE9831D0F7`
- Код: `0xc0000005` (Access Violation)
- Символ: `QDialogButtonBoxPrivate::layoutButtons`

### Test_QMessageBoxWithStyles

**Статус:** ✅ **PASSED** (тест прошел без падений)

**Анализ:**
- Тест использует упрощенный тестовый стиль (не реальный QSS файл)
- Все варианты применения стилей отработали без ошибок
- Это указывает на то, что проблема связана с конкретным содержимым `default.qss`

## Сравнение со штатным приложением

### Штатное приложение (стек вызовов от пользователя):
```
6  QApplicationPrivate::notify_helper   qapplication.cpp     3640
7  QApplication::notify                 qapplication.cpp     3590
8  QCoreApplication::notifyInternal2    qcoreapplication.cpp 1064
9  QCoreApplication::sendEvent          qcoreapplication.cpp 1463
10 QWidgetPrivate::setStyle_helper      qwidget.cpp          2663  ← ПАДЕНИЕ
11 QWidgetPrivate::inheritStyle         qwidget.cpp          2697
12 QWidget::setParent                   qwidget.cpp          10506
13 QWidget::setParent                   qwidget.cpp          10367
14 QLayoutPrivate::reparentChildWidgets qlayout.cpp          842
15 QWidget::setLayout                   qwidget.cpp          10031
16 QMessageBoxPrivate::setupLayout      qmessagebox.cpp      352
17 QMessageBoxPrivate::init             qmessagebox.cpp      290
18 QMessageBox::QMessageBox             qmessagebox.cpp      857
19 showNewMessageBox                    qmessagebox.cpp      1629
20 QMessageBox::question                qmessagebox.cpp      1716
```

### Тест (стек вызовов):
```
# 17: QWidgetPrivate::setStyle_helper() - 0x00007FFE97FFA0C0  ← ПАДЕНИЕ
# 18: QWidgetPrivate::inheritStyle() - 0x00007FFE97FFA360
# 19: QWidget::setParent() - 0x00007FFE97FEDB40
# 20: QWidget::setParent() - 0x00007FFE97FEDAC0
# 21: QLayoutPrivate::reparentChildWidgets() - 0x00007FFE97FCA910
# 22: QWidget::setLayout() - 0x00007FFE97FED4A0
# 23: QMessageBoxPrivate::setupLayout() - 0x00007FFE9849B930
# 24: QMessageBoxPrivate::init() - 0x00007FFE9849B330
# 25: QMessageBox::QMessageBox() - 0x00007FFE98497120
# 26: showNewMessageBox() - 0x00007FFE9849E040
# 27: QMessageBox::question() - 0x00007FFE984986E0
```

**Вывод:** Стеки вызовов **полностью совпадают** по логике, различаются только адреса памяти.

## Выводы

1. ✅ **Проблема успешно воспроизведена** - тест падает в той же точке, что и штатное приложение
2. ✅ **Причина определена** - падение происходит при применении QSS стилей из `Bin/Styles/default.qss` к QApplication
3. ✅ **Точка падения** - `QDialogButtonBoxPrivate::layoutButtons()` при обработке события `changeEvent` во время наследования стилей
4. ⚠️ **Особенность** - упрощенные стили не вызывают падение, проблема связана с конкретным содержимым `default.qss`

## Рекомендации

1. **Проанализировать содержимое `Bin/Styles/default.qss`** на предмет проблемных правил стилей для `QDialogButtonBox` или `QPushButton`
2. **Проверить версию Qt** - возможно, это известная проблема в Qt 5.15.2/5.15.10
3. **Рассмотреть обходное решение** - временно отключить проблемные стили для QMessageBox или использовать альтернативный подход к диалогам
4. **Создать минимальный воспроизводящий пример** с конкретным правилом стиля из `default.qss`, вызывающим падение

## Следующие шаги

1. Изучить `Bin/Styles/default.qss` и найти проблемные правила стилей
2. Создать минимальный тест с конкретным правилом стиля
3. Проверить, есть ли известные проблемы в Qt 5.15.x с QSS стилями для QDialogButtonBox
4. Предложить исправление или обходное решение
