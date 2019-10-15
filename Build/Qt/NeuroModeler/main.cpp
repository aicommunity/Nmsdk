#include <QApplication>
#include <QMessageBox>

#include "UGEngineControllWidget.h"
#include "../../../Rdk/Core/Utilities/UIniFile.h"

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);

    RDK::UAppCore<RDK::UApplication, UEngineControlQt, RDK::UProject, RDK::UServerControl, RDK::UTestManager, RDK::URpcDispatcher, RDK::URpcDecoderInternal, RDK::URpcDecoderCommon> AppCore;

     int init_res=AppCore.Init(QApplication::applicationFilePath().toLocal8Bit().constData(),
                  (QApplication::applicationDirPath()+"/EventsLog/").toLocal8Bit().constData(),
                  argc, argv);

     if(init_res != 0)
      return init_res;

    UGEngineControllWidget w(NULL, &AppCore.application);

    if(AppCore.hideAdminForm)
      w.hide();
    else
      w.show();

    RDK::UIVisualControllerStorage::UpdateInterface(true);

    if(AppCore.startMinimized)
      w.showMinimized();

    return a.exec();
}
