#include <QtTest/QtTest>
#include <QApplication>
#include <QWidget>
#include <QMessageBox>
#include <QFile>
#include <QDir>
#include <QDebug>
#include <QTimer>
#include <QEventLoop>

/**
 * Тест с различными вариантами применения стилей к QMessageBox
 * Помогает определить точную причину падения
 */
class TestQMessageBoxWithStyles : public QObject
{
    Q_OBJECT

private slots:
    void initTestCase();
    void testQMessageBoxNoStyles();
    void testQMessageBoxStylesBeforeWidget();
    void testQMessageBoxStylesAfterWidget();
    void testQMessageBoxStylesOnParent();
    void testQMessageBoxStylesComplex();
    void cleanupTestCase();

private:
    QString m_testStyleSheet;
    QWidget* m_parentWidget;
    
    void waitForWidgetReady(QWidget* widget);
};

void TestQMessageBoxWithStyles::initTestCase()
{
    // Простой тестовый стиль, который может вызвать проблемы
    m_testStyleSheet = R"(
        QWidget {
            background-color: #f0f0f0;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 5px;
        }
        QMessageBox {
            background-color: white;
        }
    )";
    
    m_parentWidget = nullptr;
    
    qDebug() << "Test stylesheet prepared";
}

void TestQMessageBoxWithStyles::waitForWidgetReady(QWidget* widget)
{
    if (!widget) return;
    
    // Ожидаем, пока виджет станет видимым и активным
    QEventLoop loop;
    QTimer timer;
    timer.setSingleShot(true);
    timer.setInterval(100);
    
    QObject::connect(&timer, &QTimer::timeout, [&loop, widget]() {
        if (widget->isVisible() && widget->isActiveWindow()) {
            loop.quit();
        }
    });
    
    timer.start();
    loop.exec();
    
    // Дополнительная обработка событий
    for (int i = 0; i < 5; ++i) {
        QApplication::processEvents();
        widget->repaint();
        widget->update();
        QApplication::processEvents();
    }
}

void TestQMessageBoxWithStyles::testQMessageBoxNoStyles()
{
    qDebug() << "\n=== Test: QMessageBox without styles ===";
    
    QApplication* app = qobject_cast<QApplication*>(QCoreApplication::instance());
    QVERIFY2(app != nullptr, "QApplication instance not found");
    
    app->setStyleSheet("");
    
    QWidget parentWidget;
    parentWidget.setWindowTitle("Test - No Styles");
    parentWidget.resize(400, 300);
    parentWidget.show();
    parentWidget.raise();
    parentWidget.activateWindow();
    
    waitForWidgetReady(&parentWidget);
    
    qDebug() << "Calling QMessageBox::question without styles...";
    
    QMessageBox::StandardButton reply = QMessageBox::question(
        &parentWidget,
        "Test",
        "Test message without styles?",
        QMessageBox::Yes | QMessageBox::No
    );
    
    qDebug() << "Result:" << reply;
    QVERIFY2(true, "Test passed");
}

void TestQMessageBoxWithStyles::testQMessageBoxStylesBeforeWidget()
{
    qDebug() << "\n=== Test: Styles applied before widget creation ===";
    
    QApplication* app = qobject_cast<QApplication*>(QCoreApplication::instance());
    QVERIFY2(app != nullptr, "QApplication instance not found");
    
    // Применяем стили ДО создания виджета
    app->setStyleSheet(m_testStyleSheet);
    qDebug() << "Styles applied to QApplication";
    
    QWidget parentWidget;
    parentWidget.setWindowTitle("Test - Styles Before");
    parentWidget.resize(400, 300);
    parentWidget.show();
    parentWidget.raise();
    parentWidget.activateWindow();
    
    waitForWidgetReady(&parentWidget);
    
    qDebug() << "Calling QMessageBox::question...";
    
    QMessageBox::StandardButton reply = QMessageBox::question(
        &parentWidget,
        "Test",
        "Test message with styles applied before widget?",
        QMessageBox::Yes | QMessageBox::No
    );
    
    qDebug() << "Result:" << reply;
    QVERIFY2(true, "Test passed");
}

void TestQMessageBoxWithStyles::testQMessageBoxStylesAfterWidget()
{
    qDebug() << "\n=== Test: Styles applied after widget creation ===";
    
    QApplication* app = qobject_cast<QApplication*>(QCoreApplication::instance());
    QVERIFY2(app != nullptr, "QApplication instance not found");
    
    QWidget parentWidget;
    parentWidget.setWindowTitle("Test - Styles After");
    parentWidget.resize(400, 300);
    parentWidget.show();
    parentWidget.raise();
    parentWidget.activateWindow();
    
    waitForWidgetReady(&parentWidget);
    
    // Применяем стили ПОСЛЕ создания виджета
    app->setStyleSheet(m_testStyleSheet);
    qDebug() << "Styles applied to QApplication after widget creation";
    
    QApplication::processEvents();
    
    qDebug() << "Calling QMessageBox::question...";
    
    QMessageBox::StandardButton reply = QMessageBox::question(
        &parentWidget,
        "Test",
        "Test message with styles applied after widget?",
        QMessageBox::Yes | QMessageBox::No
    );
    
    qDebug() << "Result:" << reply;
    QVERIFY2(true, "Test passed");
}

void TestQMessageBoxWithStyles::testQMessageBoxStylesOnParent()
{
    qDebug() << "\n=== Test: Styles applied to parent widget ===";
    
    QApplication* app = qobject_cast<QApplication*>(QCoreApplication::instance());
    QVERIFY2(app != nullptr, "QApplication instance not found");
    
    app->setStyleSheet("");
    
    QWidget* parentWidget = new QWidget();
    parentWidget->setWindowTitle("Test - Styles On Parent");
    parentWidget->resize(400, 300);
    
    // Применяем стили к родительскому виджету
    parentWidget->setStyleSheet(m_testStyleSheet);
    qDebug() << "Styles applied to parent widget";
    
    parentWidget->show();
    parentWidget->raise();
    parentWidget->activateWindow();
    
    waitForWidgetReady(parentWidget);
    
    qDebug() << "Calling QMessageBox::question...";
    
    QMessageBox::StandardButton reply = QMessageBox::question(
        parentWidget,
        "Test",
        "Test message with styles on parent?",
        QMessageBox::Yes | QMessageBox::No
    );
    
    qDebug() << "Result:" << reply;
    QVERIFY2(true, "Test passed");
    
    delete parentWidget;
}

void TestQMessageBoxWithStyles::testQMessageBoxStylesComplex()
{
    qDebug() << "\n=== Test: Complex scenario (exact reproduction) ===";
    
    QApplication* app = qobject_cast<QApplication*>(QCoreApplication::instance());
    QVERIFY2(app != nullptr, "QApplication instance not found");
    
    // Применяем стили к QApplication (как в main.cpp)
    app->setStyleSheet(m_testStyleSheet);
    qDebug() << "Styles applied to QApplication";
    
    // Создаем родительский виджет
    QWidget* parentWidget = new QWidget();
    parentWidget->setWindowTitle("Test - Complex");
    parentWidget->resize(400, 300);
    parentWidget->show();
    parentWidget->raise();
    parentWidget->activateWindow();
    
    waitForWidgetReady(parentWidget);
    
    // Убеждаемся, что виджет видим и активен (как в UGEngineControlWidget)
    if (!parentWidget->isVisible() || !parentWidget->isActiveWindow()) {
        parentWidget->raise();
        parentWidget->activateWindow();
        QApplication::processEvents();
    }
    
    qDebug() << "Parent widget ready - visible:" << parentWidget->isVisible() 
             << "active:" << parentWidget->isActiveWindow();
    
    // Вызываем QMessageBox::question точно так же, как в actionCreateSimple
    qDebug() << "Calling QMessageBox::question (complex scenario)...";
    
    QMessageBox::StandardButton reply = QMessageBox::question(
        parentWidget,
        "Info",
        "Close current config?",
        QMessageBox::Yes | QMessageBox::No
    );
    
    qDebug() << "Result:" << reply;
    QVERIFY2(true, "Test passed");
    
    delete parentWidget;
}

void TestQMessageBoxWithStyles::cleanupTestCase()
{
    if (m_parentWidget) {
        delete m_parentWidget;
        m_parentWidget = nullptr;
    }
    qDebug() << "\n=== Test Complete ===";
}

QTEST_MAIN(TestQMessageBoxWithStyles)
#include "test_qmessagebox_with_styles.moc"
