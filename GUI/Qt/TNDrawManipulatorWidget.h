#ifndef TNDRAWMANIPULATORWIDGET_H
#define TNDRAWMANIPULATORWIDGET_H

#include "UVisualControllerWidget.h"

// Qt-аналог TNDrawManipulatorFormUnit из GUI/BCB.
// На старте реализует простую область отрисовки, позднее будет
// использовать либо UDrawEngineImageWidget, либо UModernDiagramWidget.
class TNDrawManipulatorWidget : public UVisualControllerWidget
{
    Q_OBJECT

public:
    explicit TNDrawManipulatorWidget(QWidget *parent = nullptr, RDK::UApplication *app = nullptr);
    ~TNDrawManipulatorWidget() override;

    void AUpdateInterface() override;
    void AClearInterface() override;
};

#endif // TNDRAWMANIPULATORWIDGET_H

