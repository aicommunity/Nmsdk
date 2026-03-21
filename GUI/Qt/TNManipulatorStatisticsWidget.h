#ifndef TNMANIPULATORSTATISTICSWIDGET_H
#define TNMANIPULATORSTATISTICSWIDGET_H

#include "UVisualControllerWidget.h"

#include <string>

class QGroupBox;
class QLineEdit;
class QPushButton;
class QTableWidget;

// Qt-аналог части DrawGrid/Statistic-кнопок из BCB форм управления манипулятором.
// Управляет дочерним компонентом статистики (обычно StatisticDoubleMatrix) через модель/engine API:
// - NewStats: включает ManualMode и делает Reset()
// - SaveStats: триггер ManualModeSwitch
// - Reset: сбрасывает компонент статистики
class TNManipulatorStatisticsWidget : public UVisualControllerWidget
{
    Q_OBJECT

public:
    explicit TNManipulatorStatisticsWidget(QWidget *parent = nullptr, RDK::UApplication *app = nullptr);
    ~TNManipulatorStatisticsWidget() override;

    void AUpdateInterface() override;
    void AClearInterface() override;
    void ASaveParameters(RDK::USerStorageXML &xml) override;
    void ALoadParameters(RDK::USerStorageXML &xml) override;

private slots:
    void onControlSystemNameEdited();
    void onStatisticNameEdited();
    void onResetClicked();
    void onSaveStatsClicked();
    void onNewStatsClicked();

private:
    std::string controlSystemName_;
    std::string statisticComponentName_ = "StatisticDoubleMatrix";

    QGroupBox *namesGroup_;
    QLineEdit *controlSystemNameEdit_;
    QLineEdit *statisticNameEdit_;

    QPushButton *resetButton_;
    QPushButton *saveStatsButton_;
    QPushButton *newStatsButton_;

    QTableWidget *propsTable_;

    std::string statisticFullName() const;
    void updateButtonsEnabled(bool hasStatistic);
    void updatePropertiesTable(bool hasStatistic);
    bool tryResolveStatisticExists() const;
    bool tryResetStatisticComponent();
};

#endif // TNMANIPULATORSTATISTICSWIDGET_H

