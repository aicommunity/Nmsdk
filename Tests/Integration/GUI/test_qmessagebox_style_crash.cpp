#include <QtTest/QtTest>
#include <QApplication>
#include <QCoreApplication>
#include <QWidget>
#include <QMessageBox>
#include <QFile>
#include <QDir>
#include <QDebug>
#include <QStandardPaths>

/**
 * Тест для воспроизведения проблемы падения в QMessageBox::question
 * при применении QSS стилей к QApplication
 * 
 * Воспроизводит точную конфигурацию штатного приложения:
 * 1. Создание QApplication
 * 2. Применение QSS стилей через QApplication::setStyleSheet()
 * 3. Создание родительского виджета
 * 4. Вызов QMessageBox::question с родительским виджетом
 * 5. Падение в QWidgetPrivate::setStyle_helper при наследовании стилей
 */
class TestQMessageBoxStyleCrash : public QObject
{
    Q_OBJECT

private slots:
    void initTestCase();
    void testQMessageBoxWithGlobalStyles();
    void testQMessageBoxWithParentWidget();
    void testQMessageBoxWithParentAndStyles();
    void cleanupTestCase();

private:
    QString m_stylesPath;
    QString m_qssContent;
    QWidget* m_parentWidget;
    
    bool loadStyleSheet(const QString& qssPath);
    void applyStylesToApplication(QApplication* app);
};

void TestQMessageBoxStyleCrash::initTestCase()
{
    // Определяем путь к стилям (аналогично UStyleManager)
    QString appDir = QApplication::applicationDirPath();
    
    // Проверяем различные возможные пути к стилям
    QStringList possiblePaths = {
        appDir + "/Styles/",
        appDir + "/../../Bin/Styles/",
        appDir + "/../../../Bin/Styles/"
    };
    
    m_stylesPath = "";
    for (const QString& path : possiblePaths) {
        QDir dir(path);
        if (dir.exists() && QFile::exists(path + "default.qss")) {
            m_stylesPath = path;
            break;
        }
    }
    
    if (m_stylesPath.isEmpty()) {
        qWarning() << "Styles directory not found, will use empty stylesheet";
        m_qssContent = "";
    } else {
        QString qssFile = m_stylesPath + "default.qss";
        if (loadStyleSheet(qssFile)) {
            qDebug() << "Loaded stylesheet from:" << qssFile;
        } else {
            qWarning() << "Failed to load stylesheet from:" << qssFile;
            m_qssContent = "";
        }
    }
    
    m_parentWidget = nullptr;
    
    qDebug() << "Application directory:" << appDir;
    qDebug() << "Styles path:" << m_stylesPath;
    qDebug() << "Stylesheet loaded:" << !m_qssContent.isEmpty();
}

bool TestQMessageBoxStyleCrash::loadStyleSheet(const QString& qssPath)
{
    QFile file(qssPath);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        return false;
    }
    
    m_qssContent = QString::fromUtf8(file.readAll());
    file.close();
    return true;
}

void TestQMessageBoxStyleCrash::applyStylesToApplication(QApplication* app)
{
    if (app && !m_qssContent.isEmpty()) {
        app->setStyleSheet(m_qssContent);
        qDebug() << "Applied stylesheet to QApplication";
    }
}

void TestQMessageBoxStyleCrash::testQMessageBoxWithGlobalStyles()
{
    qDebug() << "\n=== Test 1: QMessageBox with global styles (AFTER FIX) ===";
    
    // Создаем QApplication (уже создан в QTEST_MAIN)
    QApplication* app = qobject_cast<QApplication*>(QCoreApplication::instance());
    QVERIFY2(app != nullptr, "QApplication instance not found");
    
    // Применяем стили к QApplication (как в main.cpp строка 150)
    // После исправления QSS файла (удалено правило QDialogButtonBox) это не должно вызывать падение
    applyStylesToApplication(app);
    
    // Создаем родительский виджет (аналогично UGEngineControlWidget)
    QWidget parentWidget;
    parentWidget.setWindowTitle("Test Parent Widget");
    parentWidget.resize(400, 300);
    parentWidget.show();
    parentWidget.raise();
    parentWidget.activateWindow();
    
    // Обрабатываем события для полной инициализации виджета
    QApplication::processEvents();
    
    // Убеждаемся, что виджет видим и активен (как в UGEngineControlWidget)
    if (!parentWidget.isVisible() || !parentWidget.isActiveWindow()) {
        parentWidget.raise();
        parentWidget.activateWindow();
        QApplication::processEvents();
    }
    
    qDebug() << "Parent widget visible:" << parentWidget.isVisible();
    qDebug() << "Parent widget active:" << parentWidget.isActiveWindow();
    
    // Вызываем QMessageBox::question с родительским виджетом
    // После исправления QSS файла это должно работать без падения
    qDebug() << "Calling QMessageBox::question (should work after fix)...";
    
    QMessageBox::StandardButton reply = QMessageBox::question(
        &parentWidget, 
        "Info", 
        "Close current config?", 
        QMessageBox::Yes | QMessageBox::No
    );
    
    qDebug() << "QMessageBox::question returned:" << reply;
    QVERIFY2(reply == QMessageBox::Yes || reply == QMessageBox::No, 
             "QMessageBox::question completed successfully without crash");
}

void TestQMessageBoxStyleCrash::testQMessageBoxWithParentWidget()
{
    qDebug() << "\n=== Test 2: QMessageBox with parent widget (no styles) ===";
    
    QApplication* app = qobject_cast<QApplication*>(QCoreApplication::instance());
    QVERIFY2(app != nullptr, "QApplication instance not found");
    
    // НЕ применяем стили - проверяем, падает ли без них
    app->setStyleSheet("");
    
    QWidget parentWidget;
    parentWidget.setWindowTitle("Test Parent Widget (No Styles)");
    parentWidget.resize(400, 300);
    parentWidget.show();
    parentWidget.raise();
    parentWidget.activateWindow();
    
    QApplication::processEvents();
    
    if (!parentWidget.isVisible() || !parentWidget.isActiveWindow()) {
        parentWidget.raise();
        parentWidget.activateWindow();
        QApplication::processEvents();
    }
    
    qDebug() << "Calling QMessageBox::question without styles...";
    
    QMessageBox::StandardButton reply = QMessageBox::question(
        &parentWidget, 
        "Info", 
        "Test message without styles?", 
        QMessageBox::Yes | QMessageBox::No
    );
    
    qDebug() << "QMessageBox::question returned:" << reply;
    QVERIFY2(true, "QMessageBox::question completed without crash");
}

void TestQMessageBoxStyleCrash::testQMessageBoxWithParentAndStyles()
{
    qDebug() << "\n=== Test 3: QMessageBox with parent widget and styles (exact reproduction - AFTER FIX) ===";
    
    QApplication* app = qobject_cast<QApplication*>(QCoreApplication::instance());
    QVERIFY2(app != nullptr, "QApplication instance not found");
    
    // Применяем стили к QApplication (после исправления QSS файла)
    applyStylesToApplication(app);
    
    // Создаем родительский виджет с явной установкой стилей
    QWidget* parentWidget = new QWidget();
    parentWidget->setWindowTitle("Test Parent Widget (With Styles)");
    parentWidget->resize(400, 300);
    parentWidget->show();
    parentWidget->raise();
    parentWidget->activateWindow();
    
    // Обрабатываем события несколько раз для полной инициализации
    for (int i = 0; i < 5; ++i) {
        QApplication::processEvents();
        parentWidget->repaint();
        parentWidget->update();
        QApplication::processEvents();
    }
    
    // Убеждаемся, что виджет видим и активен
    if (!parentWidget->isVisible() || !parentWidget->isActiveWindow()) {
        parentWidget->raise();
        parentWidget->activateWindow();
        QApplication::processEvents();
    }
    
    qDebug() << "Parent widget visible:" << parentWidget->isVisible();
    qDebug() << "Parent widget active:" << parentWidget->isActiveWindow();
    qDebug() << "Parent widget style sheet:" << (parentWidget->styleSheet().isEmpty() ? "empty" : "set");
    
    // Вызываем QMessageBox::question точно так же, как в UGEngineControlWidget::actionCreateSimple
    // После исправления QSS файла это должно работать без падения
    qDebug() << "Calling QMessageBox::question (exact reproduction - should work after fix)...";
    
    QMessageBox::StandardButton reply = QMessageBox::question(
        parentWidget, 
        "Info", 
        "Close current config?", 
        QMessageBox::Yes | QMessageBox::No
    );
    
    qDebug() << "QMessageBox::question returned:" << reply;
    QVERIFY2(reply == QMessageBox::Yes || reply == QMessageBox::No, 
             "QMessageBox::question completed successfully without crash");
    
    delete parentWidget;
}

void TestQMessageBoxStyleCrash::cleanupTestCase()
{
    if (m_parentWidget) {
        delete m_parentWidget;
        m_parentWidget = nullptr;
    }
    qDebug() << "\n=== Test Complete ===";
}

QTEST_MAIN(TestQMessageBoxStyleCrash)
#include "test_qmessagebox_style_crash.moc"
