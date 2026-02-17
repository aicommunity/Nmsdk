#include "NeuroModelerGuiRegistration.h"

#include "TNManipulatorControlWidget.h"
#include "TNDrawManipulatorWidget.h"
#include "TNDCEngineControlWidget.h"
#include "NNeuronTrainerWidget.h"
#include "TNNewPositionControlElementWidget.h"

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
}

