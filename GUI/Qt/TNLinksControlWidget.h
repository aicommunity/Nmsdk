#ifndef TNLINKSCONTROLWIDGET_H
#define TNLINKSCONTROLWIDGET_H

#include "UVisualControllerWidget.h"

#include <string>

class QComboBox;
class QGroupBox;
class QLineEdit;
class QPushButton;

class UComponentLinksWidget;

// Qt-аналог NLinksFrame (GUI/BCB), но через переиспользование UComponentLinksWidget.
// Позволяет открыть режим "один компонент" или "два компонента", задавая имена строками.
class TNLinksControlWidget : public UVisualControllerWidget
{
    Q_OBJECT

public:
    explicit TNLinksControlWidget(QWidget *parent = nullptr, RDK::UApplication *app = nullptr);
    ~TNLinksControlWidget() override;

    void AUpdateInterface() override;
    void AClearInterface() override;
    void ASaveParameters(RDK::USerStorageXML &xml) override;
    void ALoadParameters(RDK::USerStorageXML &xml) override;

private slots:
    void onModeChanged(int index);
    void onOpenClicked();

private:
    QGroupBox *topGroup_;
    QComboBox *modeCombo_;
    QLineEdit *firstEdit_;
    QLineEdit *secondEdit_;
    QPushButton *openButton_;
    UComponentLinksWidget *linksWidget_;

    int mode_ = 0; // 0=single,1=double
    std::string firstName_;
    std::string secondName_;

    void applyModeUi();
    void initLinksWidget();
};

#endif // TNLINKSCONTROLWIDGET_H

