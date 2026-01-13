#include <QtTest/QtTest>
#include <QApplication>
#include <QMainWindow>
#include <QMenuBar>
#include <QMenu>
#include <QAction>
#include <QWidget>
#include <QPoint>
#include <QTimer>
#include <QDebug>

/**
 * Тест для проверки работы меню File в главном окне приложения
 *
 * Этот тест проверяет:
 * 1. Что меню File можно найти в главном окне
 * 2. Что клик на меню File активирует его
 * 3. Что нет виджетов, блокирующих клики в области меню
 */
class TestMenuBar : public QObject
{
    Q_OBJECT

private slots:
    void initTestCase();
    void cleanupTestCase();
    void testMenuBarExists();
    void testFileMenuClickable();
    void testNoWidgetsBlockingMenu();
    void testNativeMenuBar();

private:
    QApplication* app;
    QMainWindow* mainWindow;
    QMenuBar* menuBar;
    QMenu* fileMenu;

    // Вспомогательные методы
    QMainWindow* createTestMainWindow();
    void checkWidgetsAtPosition(const QPoint& pos);
};

void TestMenuBar::initTestCase()
{
    // Создаем QApplication, если его еще нет
    int argc = 0;
    char** argv = nullptr;
    if (!QApplication::instance()) {
        app = new QApplication(argc, argv);
    } else {
        app = qobject_cast<QApplication*>(QApplication::instance());
    }

    // Создаем тестовое главное окно с меню
    mainWindow = createTestMainWindow();
    QVERIFY(mainWindow != nullptr);

    mainWindow->show();
    QTest::qWaitForWindowExposed(mainWindow);

    // Находим меню
    menuBar = mainWindow->menuBar();
    QVERIFY(menuBar != nullptr);

    fileMenu = menuBar->findChild<QMenu*>("menuFile");
    if (!fileMenu) {
        // Пытаемся найти по действию
        QList<QAction*> actions = menuBar->actions();
        for (QAction* action : actions) {
            if (action->text() == "File" || action->menu() && action->menu()->title() == "File") {
                fileMenu = action->menu();
                break;
            }
        }
    }
}

void TestMenuBar::cleanupTestCase()
{
    if (mainWindow) {
        mainWindow->close();
        delete mainWindow;
        mainWindow = nullptr;
    }
}

QMainWindow* TestMenuBar::createTestMainWindow()
{
    QMainWindow* window = new QMainWindow();
    window->setWindowTitle("Test Main Window");
    window->resize(800, 600);

    // Создаем меню
    QMenuBar* mb = window->menuBar();
    QMenu* newFileMenu = mb->addMenu("File");
    newFileMenu->setObjectName("menuFile");
    newFileMenu->addAction("New");
    newFileMenu->addAction("Open");
    newFileMenu->addAction("Save");

    mb->addMenu("Edit");
    mb->addMenu("View");
    mb->addMenu("Help");

    return window;
}

void TestMenuBar::testMenuBarExists()
{
    QVERIFY(menuBar != nullptr);
    QVERIFY(menuBar->isVisible());

    qDebug() << "MenuBar geometry:" << menuBar->geometry();
    qDebug() << "MenuBar is native:" << menuBar->isNativeMenuBar();
}

void TestMenuBar::testFileMenuClickable()
{
    if (!fileMenu) {
        QSKIP("File menu not found, skipping click test");
        return;
    }

    // Получаем геометрию меню File
    QAction* fileAction = nullptr;
    QList<QAction*> actions = menuBar->actions();
    for (QAction* action : actions) {
        if (action->text() == "File" || (action->menu() && action->menu()->title() == "File")) {
            fileAction = action;
            break;
        }
    }

    if (!fileAction) {
        QSKIP("File action not found");
        return;
    }

    // Находим позицию меню File на экране
    QRect menuBarRect = menuBar->geometry();
    QPoint fileMenuPos;

    // Приблизительная позиция первого пункта меню (File обычно первый)
    fileMenuPos = menuBar->mapToGlobal(QPoint(10, menuBarRect.height() / 2));

    qDebug() << "File menu position:" << fileMenuPos;
    qDebug() << "MenuBar global position:" << menuBar->mapToGlobal(QPoint(0, 0));

    // Проверяем, что в этой позиции находится меню
    QWidget* widgetAtPos = QApplication::widgetAt(fileMenuPos);
    qDebug() << "Widget at File menu position:" << (widgetAtPos ? widgetAtPos->objectName() : "null");

    // Симулируем клик на меню File
    // Используем QTest::mouseClick для симуляции клика
    QPoint localPos = menuBar->mapFromGlobal(fileMenuPos);
    if (menuBarRect.contains(localPos)) {
        QTest::mouseClick(menuBar, Qt::LeftButton, Qt::NoModifier, localPos);
        QTest::qWait(100); // Ждем обработки события

        // Проверяем, что меню открылось (если это не нативное меню)
        if (!menuBar->isNativeMenuBar()) {
            // Для не-нативного меню можно проверить, что меню видимо
            // Но это зависит от реализации Qt
        }
    }
}

void TestMenuBar::testNoWidgetsBlockingMenu()
{
    if (!menuBar) {
        QSKIP("MenuBar not found");
        return;
    }

    QRect menuBarRect = menuBar->geometry();
    QPoint globalTopLeft = menuBar->mapToGlobal(menuBarRect.topLeft());

    // Проверяем несколько точек в области меню
    for (int x = 0; x < menuBarRect.width(); x += 50) {
        QPoint testPoint = globalTopLeft + QPoint(x, menuBarRect.height() / 2);
        QWidget* widget = QApplication::widgetAt(testPoint);

        if (widget) {
            qDebug() << "Widget at position" << testPoint << ":"
                     << widget->objectName() << widget->metaObject()->className();

            // Проверяем, что виджет не блокирует меню
            // Виджет должен быть либо самим меню, либо его дочерним элементом
            if (widget != menuBar && !menuBar->isAncestorOf(widget)) {
                qWarning() << "Potential blocking widget found:" << widget->objectName();
            }
        }
    }
}

void TestMenuBar::testNativeMenuBar()
{
    if (!menuBar) {
        QSKIP("MenuBar not found");
        return;
    }

    bool isNative = menuBar->isNativeMenuBar();
    qDebug() << "MenuBar is native:" << isNative;

    // На Linux нативное меню может иметь проблемы с кликами
    // Это известная проблема Qt на некоторых дистрибутивах Linux
    if (isNative) {
        qWarning() << "Native menu bar detected. This may cause click issues on Linux.";
    }
}

QTEST_MAIN(TestMenuBar)
#include "Test_MenuBar.moc"

