#ifndef TNNEWPOSITIONCONTROLELEMENTWIDGET_H
#define TNNEWPOSITIONCONTROLELEMENTWIDGET_H

#include "UVisualControllerWidget.h"

// Qt-аналог TNNewPositionControlElementFormUnit из GUI/BCB.
// Универсальный элемент управления позицией, который затем может
// встраиваться в другие панели управления (например, манипулятором).
class TNNewPositionControlElementWidget : public UVisualControllerWidget
{
    Q_OBJECT

public:
    explicit TNNewPositionControlElementWidget(QWidget *parent = nullptr, RDK::UApplication *app = nullptr);
    ~TNNewPositionControlElementWidget() override;

    void AUpdateInterface() override;
    void AClearInterface() override;
};

#endif // TNNEWPOSITIONCONTROLELEMENTWIDGET_H

