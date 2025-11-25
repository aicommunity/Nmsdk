#include <QApplication>
#include <QCommandLineParser>
#include <QMessageBox>
#include <QTimer>
#include <QString>
#include <QDebug>
#include <algorithm>
#include "../../../Rdk/Deploy/Include/rdk_cpp_initdll.h"

#include "UGEngineControlWidget.h"
#include "../../../Rdk/Core/Utilities/UIniFile.h"
#include "../../../Rdk/Core/Application/Qt/UProjectDeployerQt.h"

QProgressDialog* d(NULL);

void progress_bar_callback(int complete_percent, const std::string &text)
{
 if(d)
 {
  d->setValue(complete_percent);
  if(!text.empty())
   d->setLabelText(text.c_str());
  QApplication::processEvents();
 }
}

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);

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
    int x=d->width()*2;
    int y=d->height()*1;
    d->setFixedSize(x,y);
    d->setMaximum(100);
    d->setValue(10);
    d->show();
    QApplication::processEvents();

    std::string default_user_name;
    QString name = qgetenv("USER");
    if (name.isEmpty())
        name = qgetenv("USERNAME");
    default_user_name = name.toLocal8Bit().constData();

    RDK::UAppCore<RDK::UApplication, UEngineControlQt, RDK::UProject, RDK::UServerControl, RDK::UTestManager, RDK::URpcDispatcher, RDK::URpcDecoderInternal, RDK::URpcDecoderCommon, UServerTransportTcpQt, RDK::UProjectDeployerQt> AppCore(progress_bar_callback);

     int init_res=AppCore.Init(QApplication::applicationFilePath().toLocal8Bit().constData(), "NeuroModeler.ini",
                  (QApplication::applicationDirPath()+"/EventsLog/").toLocal8Bit().constData(), default_user_name,
                  argc, argv);

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
