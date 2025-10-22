#include <QApplication>
#include <QMessageBox>
#include <QString>
#include <QDebug>

#include "UGEngineControlWidget.h"

using namespace RDK;
#include "../../../Rdk/Core/Utilities/UIniFile.h"
#include "../../../Rdk/Core/Application/Qt/UProjectDeployerQt.h"
#include "../../../Rdk/Core/Engine/ModernSmartPointers.h"
#include "../../../Rdk/Core/Engine/ModernContainers.h"
#include "../../../Rdk/Core/System/ModernChrono.h"
#include "../../../Rdk/Core/System/ModernMutex.h"

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

// Modern C++20 application management functions
namespace RDK {
    namespace ModernApp {
        // Application performance optimization
        void OptimizeApplicationPerformance() {
            // Reserve memory for common operations
            std::vector<std::string> reserved_strings;
            reserved_strings.reserve(1000);
            
            // Optimize Qt application settings
            QApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
            QApplication::setAttribute(Qt::AA_UseHighDpiPixmaps);
        }
        
        // Application validation
        bool IsApplicationValid() {
            return QApplication::instance() != nullptr;
        }
        
        // Modern application initialization
        std::optional<int> InitializeApplication(int argc, char* argv[]) {
            try {
                OptimizeApplicationPerformance();
                
                auto app = make_ueptr<QApplication>(argc, argv);
                if (!app) {
                    return std::nullopt;
                }
                
                return 0;
            } catch (const std::exception& ex) {
                qDebug() << "Application initialization failed:" << ex.what();
                return std::nullopt;
            }
        }
        
        // Application resource management
        void ReserveApplicationMemory(size_t components_count) {
            // Reserve memory for application components
            std::vector<std::shared_ptr<void>> reserved_components;
            reserved_components.reserve(components_count);
        }
        
        // Application timing
        TimePoint GetApplicationStartTime() {
            return GetCurrentTime();
        }
        
        // Modern error handling
        void HandleApplicationError(const std::string& error_message) {
            qDebug() << "Application error:" << error_message.c_str();
            // Could implement modern error reporting here
        }
    }
}

int main(int argc, char *argv[])
{
    // Modern C++20 application initialization
    auto start_time = RDK::ModernApp::GetApplicationStartTime();
    RDK::ModernApp::OptimizeApplicationPerformance();
    RDK::ModernApp::ReserveApplicationMemory(1000);
    
    QApplication a(argc, argv);

    // Modern smart pointer for progress dialog
    auto progress_dialog = make_ueptr<QProgressDialog>();
    d = progress_dialog.get();
    
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

    UGEngineControlWidget w(NULL, &AppCore.application);

    if(AppCore.hideAdminForm)
      w.hide();
    else
      w.show();

    AppCore.PostInit();

    RDK::UIVisualControllerStorage::UpdateInterface(true);

    if(AppCore.startMinimized)
      w.showMinimized();

    d->setValue(100);
    d->hide();
    delete d;
    d=NULL;
    return a.exec();
}
