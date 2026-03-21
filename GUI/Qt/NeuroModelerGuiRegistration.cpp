#include "NeuroModelerGuiRegistration.h"

#include "TNManipulatorControlWidget.h"
#include "TNDrawManipulatorWidget.h"
#include "TNDCEngineControlWidget.h"
#include "NNeuronTrainerWidget.h"
#include "TNNewPositionControlElementWidget.h"
#include "NAstaticGyroWidget.h"
#include "TNNewManipulatorControlWidget.h"
#include "TNEnsembleControlWidget.h"
#include "TNEnsembleActivityWidget.h"
#include "TNSourceControlWidget.h"
#include "TNLinksControlWidget.h"
#include "TNANetGraphicsWidget.h"
#include "TManipulatorTestWidget.h"
#include "TNManipulatorStatisticsWidget.h"

void RegisterNeuroModelerWidgets(UGEngineControlWidget &mainWindow, RDK::UApplication &app)
{
    Q_UNUSED(app);

    // Панель управления манипулятором (вкладка MDI в той же области, что и схема)
    {
        UCustomWidgetDescriptor desc;
        desc.id = QStringLiteral("neuro.manipulator.control");
        desc.title = QObject::tr("Manipulator control");
        desc.factory = [](RDK::UApplication *application) -> UVisualControllerWidget* {
            return new TNManipulatorControlWidget(nullptr, application);
        };
        desc.placement = UCustomWidgetPlacement::Mdi;
        desc.singleInstance = true;
        // Все действия группируем в одном подменю NeuroModeler
        desc.menuPath = QStringLiteral("Window/NeuroModeler");
        mainWindow.registerCustomWidget(desc);
    }

    // Визуализация манипулятора (MDI)
    {
        UCustomWidgetDescriptor desc;
        desc.id = QStringLiteral("neuro.manipulator.draw");
        desc.title = QObject::tr("Manipulator visualization");
        desc.factory = [](RDK::UApplication *application) -> UVisualControllerWidget* {
            return new TNDrawManipulatorWidget(nullptr, application);
        };
        desc.placement = UCustomWidgetPlacement::Mdi;
        desc.singleInstance = false;
        desc.menuPath = QStringLiteral("Window/NeuroModeler");
        mainWindow.registerCustomWidget(desc);
    }

    // Управление DC-двигателем (вкладка MDI)
    {
        UCustomWidgetDescriptor desc;
        desc.id = QStringLiteral("neuro.dcengine.control");
        desc.title = QObject::tr("DC engine control");
        desc.factory = [](RDK::UApplication *application) -> UVisualControllerWidget* {
            return new TNDCEngineControlWidget(nullptr, application);
        };
        desc.placement = UCustomWidgetPlacement::Mdi;
        desc.singleInstance = true;
        desc.menuPath = QStringLiteral("Window/NeuroModeler");
        mainWindow.registerCustomWidget(desc);
    }

    // Статистика манипуляторного контроллера (MDI)
    {
        UCustomWidgetDescriptor desc;
        desc.id = QStringLiteral("neuro.manipulator.statistics");
        desc.title = QObject::tr("Manipulator statistics");
        desc.factory = [](RDK::UApplication *application) -> UVisualControllerWidget* {
            return new TNManipulatorStatisticsWidget(nullptr, application);
        };
        desc.placement = UCustomWidgetPlacement::Mdi;
        desc.singleInstance = false;
        desc.menuPath = QStringLiteral("Window/NeuroModeler");
        mainWindow.registerCustomWidget(desc);
    }

    // Тренер нейронов (вкладка MDI)
    {
        UCustomWidgetDescriptor desc;
        desc.id = QStringLiteral("neuro.neuron.trainer");
        desc.title = QObject::tr("Neuron trainer");
        desc.factory = [](RDK::UApplication *application) -> UVisualControllerWidget* {
            return new NNeuronTrainerWidget(nullptr, application);
        };
        desc.placement = UCustomWidgetPlacement::Mdi;
        desc.singleInstance = true;
        desc.menuPath = QStringLiteral("Window/NeuroModeler");
        mainWindow.registerCustomWidget(desc);
    }

    // Элемент управления позицией (вкладка MDI)
    {
        UCustomWidgetDescriptor desc;
        desc.id = QStringLiteral("neuro.position.control.element");
        desc.title = QObject::tr("Position control element");
        desc.factory = [](RDK::UApplication *application) -> UVisualControllerWidget* {
            return new TNNewPositionControlElementWidget(nullptr, application);
        };
        desc.placement = UCustomWidgetPlacement::Mdi;
        desc.singleInstance = false;
        desc.menuPath = QStringLiteral("Window/NeuroModeler");
        mainWindow.registerCustomWidget(desc);
    }

    // Астатический гироскоп (углы alpha, betta, gamma)
    {
        UCustomWidgetDescriptor desc;
        desc.id = QStringLiteral("neuro.astatic.gyro");
        desc.title = QObject::tr("Astatic gyro");
        desc.factory = [](RDK::UApplication *application) -> UVisualControllerWidget* {
            return new NAstaticGyroWidget(nullptr, application);
        };
        desc.placement = UCustomWidgetPlacement::Mdi;
        desc.singleInstance = false;
        desc.menuPath = QStringLiteral("Window/NeuroModeler");
        mainWindow.registerCustomWidget(desc);
    }

    // New manipulator control (порт TNewManipulatorControlForm, только модель)
    {
        UCustomWidgetDescriptor desc;
        desc.id = QStringLiteral("neuro.new.manipulator.control");
        desc.title = QObject::tr("New manipulator control");
        desc.factory = [](RDK::UApplication *application) -> UVisualControllerWidget* {
            return new TNNewManipulatorControlWidget(nullptr, application);
        };
        desc.placement = UCustomWidgetPlacement::Mdi;
        desc.singleInstance = true;
        desc.menuPath = QStringLiteral("Window/NeuroModeler");
        mainWindow.registerCustomWidget(desc);
    }

    // Управление ансамблями NLifeNet (порог, режим)
    {
        UCustomWidgetDescriptor desc;
        desc.id = QStringLiteral("neuro.ensemble.control");
        desc.title = QObject::tr("Ensemble control");
        desc.factory = [](RDK::UApplication *application) -> UVisualControllerWidget* {
            return new TNEnsembleControlWidget(nullptr, application);
        };
        desc.placement = UCustomWidgetPlacement::Mdi;
        desc.singleInstance = false;
        desc.menuPath = QStringLiteral("Window/NeuroModeler");
        mainWindow.registerCustomWidget(desc);
    }

    // Графики Summary* NLifeNet и ручной выбор серий (Watch)
    {
        UCustomWidgetDescriptor desc;
        desc.id = QStringLiteral("neuro.ensemble.activity");
        desc.title = QObject::tr("Ensemble activity");
        desc.factory = [](RDK::UApplication *application) -> UVisualControllerWidget* {
            return new TNEnsembleActivityWidget(nullptr, application);
        };
        desc.placement = UCustomWidgetPlacement::Mdi;
        desc.singleInstance = false;
        desc.menuPath = QStringLiteral("Window/NeuroModeler");
        mainWindow.registerCustomWidget(desc);
    }

    // Управление источниками (NPulseGenerator): Frequency/Amplitude
    {
        UCustomWidgetDescriptor desc;
        desc.id = QStringLiteral("neuro.source.control");
        desc.title = QObject::tr("Source control");
        desc.factory = [](RDK::UApplication *application) -> UVisualControllerWidget* {
            return new TNSourceControlWidget(nullptr, application);
        };
        desc.placement = UCustomWidgetPlacement::Mdi;
        desc.singleInstance = false;
        desc.menuPath = QStringLiteral("Window/NeuroModeler");
        mainWindow.registerCustomWidget(desc);
    }

    // Управление связями через UComponentLinksWidget
    {
        UCustomWidgetDescriptor desc;
        desc.id = QStringLiteral("neuro.links.control");
        desc.title = QObject::tr("Links");
        desc.factory = [](RDK::UApplication *application) -> UVisualControllerWidget* {
            return new TNLinksControlWidget(nullptr, application);
        };
        desc.placement = UCustomWidgetPlacement::Mdi;
        desc.singleInstance = false;
        desc.menuPath = QStringLiteral("Window/NeuroModeler");
        mainWindow.registerCustomWidget(desc);
    }

    // Графическая визуализация структуры NANet (model-only)
    {
        UCustomWidgetDescriptor desc;
        desc.id = QStringLiteral("neuro.net.graphics");
        desc.title = QObject::tr("NANet graphics");
        desc.factory = [](RDK::UApplication *application) -> UVisualControllerWidget* {
            return new TNANetGraphicsWidget(nullptr, application);
        };
        desc.placement = UCustomWidgetPlacement::Mdi;
        desc.singleInstance = false;
        desc.menuPath = QStringLiteral("Window/NeuroModeler");
        mainWindow.registerCustomWidget(desc);
    }

    // Тест манипулятора (model-only: визуализация + IO-графики)
    {
        UCustomWidgetDescriptor desc;
        desc.id = QStringLiteral("neuro.manipulator.test");
        desc.title = QObject::tr("Manipulator test");
        desc.factory = [](RDK::UApplication *application) -> UVisualControllerWidget* {
            return new TManipulatorTestWidget(nullptr, application);
        };
        desc.placement = UCustomWidgetPlacement::Mdi;
        desc.singleInstance = false;
        desc.menuPath = QStringLiteral("Window/NeuroModeler");
        mainWindow.registerCustomWidget(desc);
    }
}

