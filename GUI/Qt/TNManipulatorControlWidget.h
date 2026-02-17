#ifndef TNMANIPULATORCONTROLWIDGET_H
#define TNMANIPULATORCONTROLWIDGET_H

#include "UVisualControllerWidget.h"

// Qt-аналог TNManipulatorControlForm из GUI/BCB.
// На первом этапе содержит базовый каркас, позже сюда будет
// перенесена прикладная логика управления манипулятором.
class TNManipulatorControlWidget : public UVisualControllerWidget
{
    Q_OBJECT

public:
    explicit TNManipulatorControlWidget(QWidget *parent = nullptr, RDK::UApplication *app = nullptr);
    ~TNManipulatorControlWidget() override;

    // UIVisualController API
    void AUpdateInterface() override;
    void AClearInterface() override;
    void ASaveParameters(RDK::USerStorageXML &xml) override;
    void ALoadParameters(RDK::USerStorageXML &xml) override;
};

#endif // TNMANIPULATORCONTROLWIDGET_H

