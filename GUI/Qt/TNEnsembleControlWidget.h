#ifndef TNENSEMBLECONTROLWIDGET_H
#define TNENSEMBLECONTROLWIDGET_H

#include "UVisualControllerWidget.h"

#include <string>

class QGroupBox;
class QLabel;
class QLineEdit;
class QPushButton;
class QRadioButton;
class QSlider;
class QTableWidget;

// Qt-аналог TNEnsembleControlFrame из GUI/BCB.
// Управление параметрами NLifeNet (порог ансамблей, режим) только через модель.
// Таблицы бета-ансамблей, ансамблей и связей — заглушки (данные требуют доступа к NLifeNet*).
class TNEnsembleControlWidget : public UVisualControllerWidget
{
    Q_OBJECT

public:
    explicit TNEnsembleControlWidget(QWidget *parent = nullptr, RDK::UApplication *app = nullptr);
    ~TNEnsembleControlWidget() override;

    void AUpdateInterface() override;
    void AClearInterface() override;
    void ASaveParameters(RDK::USerStorageXML &xml) override;
    void ALoadParameters(RDK::USerStorageXML &xml) override;

private slots:
    void onNetworkNameEdited();
    void onFindNLifeNetClicked();
    void onThresholdSliderChanged(int value);
    void onThresholdEditEdited();
    void onThresholdModeToggled();

private:
    std::string networkName_;

    QLineEdit *networkNameEdit_;
    QPushButton *findButton_;
    QGroupBox *thresholdGroup_;
    QSlider *thresholdSlider_;
    QLineEdit *thresholdEdit_;
    QGroupBox *thresholdModeGroup_;
    QRadioButton *thresholdMode0_;
    QRadioButton *thresholdMode1_;
    QRadioButton *thresholdMode2_;
    QGroupBox *betaEnsembleGroup_;
    QTableWidget *betaEnsembleTable_;
    QGroupBox *ensembleGroup_;
    QTableWidget *ensembleTable_;
    QGroupBox *linksGroup_;
    QTableWidget *linksTable_;

    bool updateInProgress_ = false;

    void updateThresholdFromModel();
    void updateThresholdModeFromModel();
    void setPlaceholderTables();
    void updateTablesFromNetwork();
    void findAndSetNLifeNet();
    static std::vector<std::string> splitCsv(const std::string &csv);
};

#endif // TNENSEMBLECONTROLWIDGET_H
