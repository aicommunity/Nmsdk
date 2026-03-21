#ifndef TNENSEMBLEACTIVITYWIDGET_H
#define TNENSEMBLEACTIVITYWIDGET_H

#include "UVisualControllerWidget.h"

#include <string>

class QPushButton;
class QLineEdit;
class QGroupBox;

class UWatchTab;

// Qt-аналог NEnsembleActivityFrame (GUI/BCB).
// В BCB графики строились по значениям GetEnsembleActivity(i) (C++ API NLifeNet).
// В model-only режиме делаем виджет на базе Qt Watch: пользователь выбирает публичные свойства,
// плюс есть автодобавление стандартных ptPubState NLifeNet (Summary*).
class TNEnsembleActivityWidget : public UVisualControllerWidget
{
    Q_OBJECT

public:
    explicit TNEnsembleActivityWidget(QWidget *parent = nullptr, RDK::UApplication *app = nullptr);
    ~TNEnsembleActivityWidget() override;

    void AUpdateInterface() override;
    void AClearInterface() override;
    void ASaveParameters(RDK::USerStorageXML &xml) override;
    void ALoadParameters(RDK::USerStorageXML &xml) override;

private slots:
    void onNetworkNameEdited();
    void onFindNLifeNetClicked();
    void onAddSeriesClicked();
    void onAddDefaultSeriesClicked();

private:
    std::string networkName_;

    QGroupBox *networkGroup_;
    QLineEdit *networkNameEdit_;
    QPushButton *findButton_;
    QPushButton *addSeriesButton_;
    QPushButton *addDefaultSeriesButton_;
    UWatchTab *watchTab_;

    void addDefaultSeries(const std::string &componentName);
    void findAndSetNLifeNet();
    static std::vector<std::string> splitCsv(const std::string &csv);
};

#endif // TNENSEMBLEACTIVITYWIDGET_H

