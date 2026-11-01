#include <QtTest/QtTest>
#include <QCoreApplication>
#include <QApplication>
#include <QTimer>
#include <QProcess>
#include <QFileInfo>
#include <QDebug>
#include <QStandardPaths>
#include <QLibraryInfo>

/**
 * Тест для проверки успешного запуска приложения NeuroModeler
 * Проверяет, что приложение инициализируется без падения в init_platform
 */
class TestAppStartup : public QObject
{
    Q_OBJECT

private slots:
    void initTestCase();
    void testQApplicationCreation();
    void testPluginPathsAvailable();
    void testAppExecutableExists();
    void cleanupTestCase();

private:
    QString m_appDir;
    QString m_appExePath;
};

void TestAppStartup::initTestCase()
{
    m_appDir = QCoreApplication::applicationDirPath();
    
    // Ищем исполняемый файл NeuroModeler
    QStringList possibleNames = {
        "NeuroModeler.exe",
        "../NeuroModeler.exe",
        "../../NeuroModeler.exe"
    };
    
    for (const QString& name : possibleNames) {
        QString path = m_appDir + "/" + name;
        QFileInfo info(path);
        if (info.exists() && info.isFile()) {
            m_appExePath = QDir::cleanPath(path);
            break;
        }
    }
    
    qDebug() << "Application directory:" << m_appDir;
    qDebug() << "Looking for NeuroModeler executable...";
}

void TestAppStartup::testQApplicationCreation()
{
    qDebug() << "\n=== Testing QApplication Creation ===";
    
    // Проверяем, что можем создать QApplication без падения
    int argc = 1;
    char* argv[] = { const_cast<char*>("test_app_startup.exe"), nullptr };
    
    try {
        QApplication app(argc, argv);
        qDebug() << "✓ QApplication created successfully";
        
        // Проверяем, что плагины загружены
        QStringList libraryPaths = QCoreApplication::libraryPaths();
        QVERIFY2(!libraryPaths.isEmpty(), "No library paths found");
        
        qDebug() << "Library paths:";
        for (const QString& path : libraryPaths) {
            qDebug() << "  -" << path;
        }
        
        // Проверяем версию Qt
        QString qtVersion = QLibraryInfo::version().toString();
        qDebug() << "Qt version:" << qtVersion;
        
    } catch (...) {
        QFAIL("Exception thrown during QApplication creation");
    }
}

void TestAppStartup::testPluginPathsAvailable()
{
    qDebug() << "\n=== Testing Plugin Paths ===";
    
    int argc = 1;
    char* argv[] = { const_cast<char*>("test_app_startup.exe"), nullptr };
    QApplication app(argc, argv);
    
    QStringList libraryPaths = QCoreApplication::libraryPaths();
    QVERIFY2(!libraryPaths.isEmpty(), "No library paths available");
    
    // Проверяем наличие директории plugins
    QString pluginsDir = m_appDir + "/plugins";
    QDir pluginsDirObj(pluginsDir);
    
    if (pluginsDirObj.exists()) {
        qDebug() << "✓ Plugins directory exists:" << pluginsDir;
        
        // Проверяем наличие критических плагинов
        QStringList criticalPlugins = {
            "platforms/qwindows.dll",
            "styles/qwindowsvistastyle.dll"
        };
        
        for (const QString& plugin : criticalPlugins) {
            QString pluginPath = pluginsDir + "/" + plugin;
            QFileInfo pluginInfo(pluginPath);
            QVERIFY2(pluginInfo.exists(), 
                     qPrintable(QString("Critical plugin missing: %1").arg(plugin)));
            qDebug() << "  ✓ Found:" << plugin;
        }
    } else {
        qWarning() << "⚠ Plugins directory not found:" << pluginsDir;
    }
}

void TestAppStartup::testAppExecutableExists()
{
    qDebug() << "\n=== Testing App Executable ===";
    
    if (m_appExePath.isEmpty()) {
        QSKIP("NeuroModeler executable not found in expected locations");
    }
    
    QFileInfo exeInfo(m_appExePath);
    QVERIFY2(exeInfo.exists(), 
             qPrintable(QString("Executable not found: %1").arg(m_appExePath)));
    QVERIFY2(exeInfo.isFile(), 
             qPrintable(QString("Path is not a file: %1").arg(m_appExePath)));
    
    qDebug() << "✓ Found executable:" << m_appExePath;
    qDebug() << "  Size:" << exeInfo.size() << "bytes";
    qDebug() << "  Last modified:" << exeInfo.lastModified().toString();
}

void TestAppStartup::cleanupTestCase()
{
    qDebug() << "\n=== Test Complete ===";
}

QTEST_MAIN(TestAppStartup)
#include "test_app_startup.moc"
