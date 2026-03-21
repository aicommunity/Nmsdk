#ifndef TNNEWPOSITIONCONTROLELEMENTWIDGET_H
#define TNNEWPOSITIONCONTROLELEMENTWIDGET_H

#include "UVisualControllerWidget.h"

#include <string>

class QLineEdit;
class QPushButton;
class QTableWidget;

// Qt-аналог TNNewPositionControlElementFormUnit из GUI/BCB.
// Элемент управления позицией: имя компонента NNewPositionControlElement,
// таблицы выбранного и обученного состояния (генераторы/нейроны), кнопка «Запомнить» (только модель).
class TNNewPositionControlElementWidget : public UVisualControllerWidget
{
    Q_OBJECT

public:
    explicit TNNewPositionControlElementWidget(QWidget *parent = nullptr, RDK::UApplication *app = nullptr);
    ~TNNewPositionControlElementWidget() override;

    void AUpdateInterface() override;
    void AClearInterface() override;
    void ASaveParameters(RDK::USerStorageXML &xml) override;
    void ALoadParameters(RDK::USerStorageXML &xml) override;

private slots:
    void onComponentNameEdited();
    void onTrainPositionClicked();
    void onSelectedCellChanged(int row, int col);

private:
    std::string componentControlName_;
    int numMotionElements_ = 0;
    int numControlLoops_ = 0;

    QLineEdit *componentNameEdit_;
    QTableWidget *selectedStateTable_;
    QTableWidget *trainedStateTable_;
    QPushButton *trainPositionButton_;

    void refreshTablesFromModel();
    void applySelectedCellToModel(int row, int col);
};

#endif // TNNEWPOSITIONCONTROLELEMENTWIDGET_H

