#include <QApplication>
#include <QCommandLineParser>
#include <QMessageBox>
#include <QTimer>
#include <QString>
#include <QDebug>
#include <QDir>
#include <QPushButton>
#include <QDialogButtonBox>
#include <algorithm>
#include <utility>
#include <vector>
#include <atomic>
#include "../../../Rdk/Deploy/Include/rdk_cpp_initdll.h"

#include "UGEngineControlWidget.h"
#include "UStyleManager.h"
#include "../../../Rdk/Core/Utilities/UIniFile.h"
#include "../../../Rdk/Core/Application/Qt/UProjectDeployerQt.h"
#include "../../../Rdk/GUI/Qt/UGuiModelSnapshot.h"

QProgressDialog* d(NULL);
std::atomic<bool> g_cancelRequested(false);

void progress_bar_callback(int complete_percent, const std::string &text)
{
 if(d)
 {
  if(g_cancelRequested.load())
  {
   d->setLabelText("Отмена инициализации...");
   // Обрабатываем все события для обеспечения отзывчивости окна
   QApplication::processEvents(QEventLoop::AllEvents, 0);
   return;
  }
  d->setValue(complete_percent);
  if(!text.empty())
   d->setLabelText(text.c_str());

  // Обрабатываем события для обеспечения отзывчивости окна во время блокирующих операций
  // Используем AllEvents без таймаута для немедленной обработки всех событий включая клики
  // Это критично для того, чтобы окно прогресса могло получать сообщения даже во время
  // длительных блокирующих операций инициализации
  QApplication::processEvents(QEventLoop::AllEvents, 0);

  // Проверяем отмену после обработки событий
  if(g_cancelRequested.load())
  {
   d->setLabelText("Отмена инициализации...");
   return;
  }
 }
}

// Функция для диагностики загрузки плагинов Qt
void diagnoseQtPlugins()
{
    qDebug() << "=== Qt Plugin Diagnostics ===";

    // Получаем путь к плагинам
    QStringList pluginPaths = QCoreApplication::libraryPaths();
    qDebug() << "Qt library paths:";
    for (const QString& path : pluginPaths) {
        qDebug() << "  -" << path;
    }

    // Проверяем qt.conf
    QString appDir = QCoreApplication::applicationDirPath();
    QString qtConfPath = appDir + "/qt.conf";
    QFileInfo qtConfInfo(qtConfPath);
    if (qtConfInfo.exists()) {
        qDebug() << "qt.conf found at:" << qtConfPath;
        QFile qtConfFile(qtConfPath);
        if (qtConfFile.open(QIODevice::ReadOnly | QIODevice::Text)) {
            QString content = QString::fromUtf8(qtConfFile.readAll());
            qDebug() << "qt.conf content:\n" << content;
            qtConfFile.close();
        }
    } else {
        qWarning() << "qt.conf NOT found at:" << qtConfPath;
    }

    // Проверяем наличие критически важных плагинов
    QString pluginsDir = appDir + "/plugins";
    QStringList criticalPlugins = {
        "platforms/qwindows.dll",
        "styles/qwindowsvistastyle.dll"
    };

    qDebug() << "Checking critical plugins in:" << pluginsDir;
    for (const QString& plugin : criticalPlugins) {
        QString pluginPath = pluginsDir + "/" + plugin;
        QFileInfo pluginInfo(pluginPath);
        if (pluginInfo.exists()) {
            qDebug() << "  ✓ Found:" << plugin;
        } else {
            qWarning() << "  ✗ Missing:" << plugin << "at" << pluginPath;
        }
    }

    // Проверяем версию Qt
    QString qtVersion = QLibraryInfo::version().toString();
    qDebug() << "Qt version:" << qtVersion;
    qDebug() << "Qt location:" << QLibraryInfo::location(QLibraryInfo::PrefixPath);

    // Проверяем наличие debug плагинов (не должны быть в production)
    QDir pluginsDirObj(pluginsDir);
    if (pluginsDirObj.exists()) {
        QStringList debugPlugins;
        QDirIterator it(pluginsDir, QStringList() << "*d.dll", QDir::Files, QDirIterator::Subdirectories);
        while (it.hasNext()) {
            debugPlugins << it.next();
        }
        if (!debugPlugins.isEmpty()) {
            qWarning() << "WARNING: Found" << debugPlugins.size() << "debug plugin(s):";
            for (const QString& debugPlugin : debugPlugins) {
                qWarning() << "  -" << debugPlugin;
            }
            qWarning() << "Debug plugins should not be present in production builds!";
        } else {
            qDebug() << "  ✓ No debug plugins found (correct)";
        }
    }

    qDebug() << "=== End Plugin Diagnostics ===";
}

int main(int argc, char *argv[])
{
    // Создаем QApplication
    QApplication a(argc, argv);

    // Регистрируем типы для использования в Qt signals/slots с queued connections
    qRegisterMetaType<NMSDK::UGuiSnapshotPtr>("NMSDK::UGuiSnapshotPtr");

    // Выполняем диагностику плагинов после создания QApplication
    // (QApplication наследуется от QCoreApplication, поэтому можем использовать его методы)
    diagnoseQtPlugins();

    // Initialize style manager and apply global styles
    UStyleManager* styleManager = UStyleManager::instance();

    // Get styles path (handles Bin/Platform/Linux/ case)
    QString stylesDir = styleManager->getStylesPath();

    if (!styleManager->loadTheme(stylesDir + "theme.json"))
    {
        qWarning() << "Failed to load theme from:" << (stylesDir + "theme.json");
    }
    if (!styleManager->loadStyleSheet(stylesDir + "default.qss"))
    {
        qWarning() << "Failed to load stylesheet from:" << (stylesDir + "default.qss");
    }
    styleManager->applyGlobalStyleSheet(&a);

    QCommandLineParser parser;
    parser.setApplicationDescription("NeuroModeler automation arguments");
    parser.addHelpOption();
    const QCommandLineOption configOption(QStringList() << "c" << "config",
                                          "Path to project ini to open.",
                                          "path");
    const QCommandLineOption startCalcOption(QStringList() << "s" << "start-calc",
                                             "Start calculations immediately after launch.");
    const QCommandLineOption calcTimeOption(QStringList() << "t" << "calc-time",
                                            "Calculation time interval in seconds.",
                                            "seconds");
    const QCommandLineOption exitAfterOption(QStringList() << "x" << "exit-after-calc",
                                             "Exit application after calculations finish.");
    parser.addOption(configOption);
    parser.addOption(startCalcOption);
    parser.addOption(calcTimeOption);
    parser.addOption(exitAfterOption);
    parser.process(a);

    auto buildForwardArgs = []() {
        QStringList original = QCoreApplication::arguments();
        std::vector<std::string> storage;
        storage.reserve(original.size());
        std::vector<char*> pointers;

        auto push_arg = [&](const QString& value) {
            storage.emplace_back(value.toLocal8Bit().constData());
            pointers.push_back(storage.back().data());
        };

        if(!original.isEmpty())
            push_arg(original.front());

        auto optionNeedsValue = [](const QString& option) {
            return option == "--config" || option == "-c" ||
                   option == "--calc-time" || option == "-t";
        };

        for(int i=1; i<original.size(); ++i)
        {
            const QString token = original[i];
            if(token == "--config" || token == "-c" ||
               token == "--start-calc" || token == "-s" ||
               token == "--calc-time" || token == "-t" ||
               token == "--exit-after-calc" || token == "-x")
            {
                if(optionNeedsValue(token) && i + 1 < original.size())
                    ++i;
                continue;
            }
            push_arg(token);
        }

        return std::pair<std::vector<std::string>, std::vector<char*>>{std::move(storage), std::move(pointers)};
    };

    auto [forwardStorage, forwardPointers] = buildForwardArgs();
    int forwardedArgc = static_cast<int>(forwardPointers.size());
    char** forwardedArgv = forwardPointers.data();

    const QString cliConfigPath = parser.value(configOption).trimmed();
    const bool cliStartCalc = parser.isSet(startCalcOption);
    const bool cliExitAfterCalc = parser.isSet(exitAfterOption);
    double cliCalcTimeSec = 0.0;
    if(parser.isSet(calcTimeOption))
    {
        bool ok=false;
        const double parsed = parser.value(calcTimeOption).toDouble(&ok);
        if(ok && parsed > 0.0)
            cliCalcTimeSec = parsed;
    }

    d=new QProgressDialog;
    d->setWindowFlag(Qt::WindowStaysOnTopHint);
    d->setLabelText("Launching application");
    d->setCancelButtonText("Отмена");
    d->setWindowModality(Qt::NonModal); // NonModal чтобы окно могло получать события
    d->setAutoClose(false); // Не закрывать автоматически
    d->setAutoReset(false); // Не сбрасывать автоматически
    d->setMinimumDuration(0); // Показывать окно сразу, без задержки
    d->setMaximum(100);
    d->setValue(10);

    // Устанавливаем минимальные размеры явно, чтобы избежать черного прямоугольника
    d->setMinimumSize(400, 100);
    d->resize(400, 100);

    // Применяем стили к окну прогресса явно
    if(styleManager)
    {
        d->setStyleSheet(styleManager->getStyleSheet());
    }

    // Обработка отмены через кнопку Cancel (подключаем ДО show())
    QObject::connect(d, &QProgressDialog::canceled, []() {
        g_cancelRequested.store(true);
        if(d)
        {
            // Мгновенно изменяем текст кнопки Cancel на "Cancelling..." для обратной связи
            QPushButton* cancelButton = nullptr;
            // Пробуем найти через buttonBox (стандартный способ для QProgressDialog)
            QDialogButtonBox* buttonBox = d->findChild<QDialogButtonBox*>();
            if(buttonBox)
            {
                cancelButton = buttonBox->button(QDialogButtonBox::Cancel);
            }
            // Если не нашли через buttonBox, ищем все кнопки и выбираем ту, у которой текст "Отмена"
            if(!cancelButton)
            {
                QList<QPushButton*> buttons = d->findChildren<QPushButton*>();
                for(QPushButton* btn : buttons)
                {
                    if(btn->text() == "Отмена" || btn->text() == "Cancel")
                    {
                        cancelButton = btn;
                        break;
                    }
                }
            }
            if(cancelButton)
            {
                cancelButton->setText("Cancelling...");
                // Немедленно обрабатываем события для обновления UI
                QApplication::processEvents(QEventLoop::AllEvents, 0);
            }
            d->setLabelText("Отмена инициализации...");
        }
    });

    // Показываем окно
    d->show();
    d->raise(); // Поднимаем окно наверх
    d->activateWindow(); // Активируем окно для получения фокуса

    // Принудительно обрабатываем события несколько раз для полной отрисовки окна
    // Это критично для избежания черного прямоугольника при первом показе
    for(int i = 0; i < 5; ++i)
    {
        QApplication::processEvents(QEventLoop::AllEvents, 0);
        d->repaint();
        d->update();
        QApplication::processEvents(QEventLoop::AllEvents, 0);
    }

    std::string default_user_name;
    QString name = qgetenv("USER");
    if (name.isEmpty())
        name = qgetenv("USERNAME");
    default_user_name = name.toLocal8Bit().constData();

    RDK::UAppCore<RDK::UApplication, UEngineControlQt, RDK::UProject, RDK::UServerControl, RDK::UTestManager, RDK::URpcDispatcher, RDK::URpcDecoderInternal, RDK::URpcDecoderCommon, UServerTransportTcpQt, RDK::UProjectDeployerQt> AppCore(progress_bar_callback);

    // Сброс флага отмены перед инициализацией
    g_cancelRequested.store(false);

    // Создаем таймер для периодической обработки событий во время длительных блокирующих операций инициализации
    // Это критично для обеспечения отзывчивости окна прогресса, особенно во время InitRTlibs, BuildStorage, LoadClassesDescription
    // Таймер обрабатывает события даже после отмены, чтобы UI мог обновиться (например, текст кнопки "Cancelling...")
    QTimer* eventTimer = new QTimer(&a);
    QObject::connect(eventTimer, &QTimer::timeout, []() {
        // Обрабатываем события пока окно прогресса существует
        // Это позволяет окну получать сообщения даже во время длительных блокирующих операций
        if(d) {
            QApplication::processEvents(QEventLoop::AllEvents, 0);
        }
    });
    eventTimer->start(50); // Обрабатывать события каждые 50 мс для обеспечения отзывчивости

     int init_res=AppCore.Init(QApplication::applicationFilePath().toLocal8Bit().constData(), "NeuroModeler.ini",
                  (QApplication::applicationDirPath()+"/EventsLog/").toLocal8Bit().constData(), default_user_name,
                  forwardedArgc, forwardedArgv);

     // Останавливаем таймер после завершения инициализации (включая случай отмены)
     eventTimer->stop();
     delete eventTimer;

     // Проверка отмены после инициализации
     if(g_cancelRequested.load())
     {
         if(d)
         {
             d->hide();
             delete d;
             d = NULL;
         }
         return 1; // Код отмены
     }

     if(init_res != 0)
      return init_res;

    if(!cliConfigPath.isEmpty())
    {
        AppCore.startProjectName = cliConfigPath.toLocal8Bit().constData();
        AppCore.autoexecLastProjectFlag = 0;
    }
    if(cliStartCalc)
        AppCore.autoStartProjectFlag = 1;
    if(cliCalcTimeSec > 0.0)
        AppCore.calcTimeIntervalSec = cliCalcTimeSec;
    if(cliExitAfterCalc)
        AppCore.exitAfterCalcFlag = 1;

    UGEngineControlWidget w(NULL, &AppCore.application);

    if(AppCore.hideAdminForm)
      w.hide();
    else
      w.show();

    AppCore.PostInit();

    auto configureAutomation = [&AppCore]()
    {
        if(AppCore.calcTimeIntervalSec > 0.0 && AppCore.application.GetProjectOpenFlag())
        {
            const auto& config = AppCore.application.GetProjectConfig();
            const int channel_count = std::max(1, config.NumChannels);
            for(int channel = 0; channel < channel_count; ++channel)
            {
                auto env = RDK::GetEnvironmentLock(channel);
                if(env)
                    env->SetMaxCalcTime(AppCore.calcTimeIntervalSec);
            }
        }
        if(AppCore.exitAfterCalcFlag)
        {
            QTimer* monitor = new QTimer(QApplication::instance());
            QObject::connect(monitor, &QTimer::timeout, [&AppCore]()
            {
                if(!AppCore.application.GetProjectOpenFlag())
                    return;
                const auto& cfg = AppCore.application.GetProjectConfig();
                const int channel_count = std::max(1, cfg.NumChannels);
                for(int channel = 0; channel < channel_count; ++channel)
                {
                    auto env = RDK::GetEnvironmentLock(channel);
                    if(env && !env->IsCalcFinished())
                        return;
                }
                QApplication::quit();
            });
            monitor->start(500);
        }
    };

    configureAutomation();

    RDK::UIVisualControllerStorage::UpdateInterface(true);

    if(AppCore.startMinimized)
      w.showMinimized();

    d->setValue(100);
    d->hide();
    delete d;
    d=NULL;
    return a.exec();
}
