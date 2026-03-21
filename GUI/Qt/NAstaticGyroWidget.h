#ifndef NASTATICGYROWIDGET_H
#define NASTATICGYROWIDGET_H

#include "UVisualControllerWidget.h"

#include <string>

class QLabel;
class QLineEdit;

// Qt-аналог TNAstaticGyroUnit из GUI/BCB.
// Отображение углов ориентации астатического гироскопа (alpha, betta, gamma)
// в радианах и градусах. Только модель: ReadStateValue по имени компонента.
class NAstaticGyroWidget : public UVisualControllerWidget
{
    Q_OBJECT

public:
    explicit NAstaticGyroWidget(QWidget *parent = nullptr, RDK::UApplication *app = nullptr);
    ~NAstaticGyroWidget() override;

    void AUpdateInterface() override;
    void AClearInterface() override;
    void ASaveParameters(RDK::USerStorageXML &xml) override;
    void ALoadParameters(RDK::USerStorageXML &xml) override;

private slots:
    void onComponentNameEdited();

private:
    std::string componentName_;
    double alpha_ = 0.0;
    double betta_ = 0.0;
    double gamma_ = 0.0;

    QLineEdit *componentNameEdit_;
    QLabel *radiansLabel_;
    QLabel *degreesLabel_;

    void readComponentData();
};

#endif // NASTATICGYROWIDGET_H
