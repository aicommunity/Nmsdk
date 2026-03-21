#include "TNNewPositionControlElementWidget.h"

#include <QLabel>
#include <QLineEdit>
#include <QMessageBox>
#include <QPushButton>
#include <QSplitter>
#include <QTableWidget>
#include <QVBoxLayout>

#include <rdk_application.h>
#include <rdk_engine_support.h>

#include <cmath>
#include <string>

TNNewPositionControlElementWidget::TNNewPositionControlElementWidget(QWidget *parent, RDK::UApplication *app)
    : UVisualControllerWidget(parent, app),
      componentNameEdit_(nullptr),
      selectedStateTable_(nullptr),
      trainedStateTable_(nullptr),
      trainPositionButton_(nullptr)
{
    Name = "TNNewPositionControlElementWidget";
    ClassName = "TNNewPositionControlElementWidget";

    const QString title = tr("Position control element");
    setAccessibleName(title);
    setWindowTitle(title);

    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(4, 4, 4, 4);

    layout->addWidget(new QLabel(tr("Component name (NNewPositionControlElement):"), this));
    componentNameEdit_ = new QLineEdit(this);
    componentNameEdit_->setPlaceholderText(tr("e.g. NNewPositionControlElement"));
    layout->addWidget(componentNameEdit_);

    selectedStateTable_ = new QTableWidget(this);
    selectedStateTable_->setHorizontalScrollMode(QTableWidget::ScrollPerPixel);
    trainedStateTable_ = new QTableWidget(this);
    trainedStateTable_->setHorizontalScrollMode(QTableWidget::ScrollPerPixel);

    auto *splitter = new QSplitter(Qt::Vertical, this);
    splitter->addWidget(new QLabel(tr("Selected state (generators Frequency):"), this));
    splitter->addWidget(selectedStateTable_);
    splitter->addWidget(new QLabel(tr("Trained state (post-input neurons):"), this));
    splitter->addWidget(trainedStateTable_);
    layout->addWidget(splitter);

    trainPositionButton_ = new QPushButton(tr("Train position (Remember state)"), this);
    layout->addWidget(trainPositionButton_);

    setLayout(layout);

    connect(componentNameEdit_, &QLineEdit::editingFinished, this, &TNNewPositionControlElementWidget::onComponentNameEdited);
    connect(trainPositionButton_, &QPushButton::clicked, this, &TNNewPositionControlElementWidget::onTrainPositionClicked);
    connect(selectedStateTable_, &QTableWidget::cellChanged, this, &TNNewPositionControlElementWidget::onSelectedCellChanged);
}

TNNewPositionControlElementWidget::~TNNewPositionControlElementWidget() = default;

void TNNewPositionControlElementWidget::AUpdateInterface()
{
    refreshTablesFromModel();
}

void TNNewPositionControlElementWidget::AClearInterface()
{
    componentControlName_.clear();
    componentNameEdit_->clear();
    numMotionElements_ = 0;
    numControlLoops_ = 0;
    selectedStateTable_->setRowCount(0);
    selectedStateTable_->setColumnCount(0);
    trainedStateTable_->setRowCount(0);
    trainedStateTable_->setColumnCount(0);
}

void TNNewPositionControlElementWidget::ASaveParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("PositionControlElement");
    xml.WriteString("ComponentControlName", componentControlName_);
    xml.SelectUp();
}

void TNNewPositionControlElementWidget::ALoadParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("PositionControlElement");
    componentControlName_ = xml.ReadString("ComponentControlName", "");
    xml.SelectUp();
    componentNameEdit_->setText(QString::fromStdString(componentControlName_));
}

void TNNewPositionControlElementWidget::onComponentNameEdited()
{
    componentControlName_ = componentNameEdit_->text().trimmed().toStdString();
}

void TNNewPositionControlElementWidget::onTrainPositionClicked()
{
    if (componentControlName_.empty())
        return;
    try
    {
        RDK::WriteStateValue<bool>(componentControlName_, "RememberState", true);
    }
    catch (...)
    {
        QMessageBox::warning(this, tr("Train position"), tr("Failed to set RememberState. Check component name and model."));
    }
}

void TNNewPositionControlElementWidget::onSelectedCellChanged(int row, int col)
{
    if (UpdateInterfaceFlag)
        return;
    applySelectedCellToModel(row, col);
}

void TNNewPositionControlElementWidget::refreshTablesFromModel()
{
    if (componentControlName_.empty())
        return;

    try
    {
        numMotionElements_ = static_cast<int>(RDK::ReadParameterValue<double>(componentControlName_ + ".MotionControlElement", "NumMotionElements"));
        numControlLoops_ = static_cast<int>(RDK::ReadParameterValue<double>(componentControlName_ + ".MotionControlElement", "NumControlLoops"));
    }
    catch (...)
    {
        numMotionElements_ = 0;
        numControlLoops_ = 0;
    }

    const int cols = numMotionElements_ * 2 + 1;
    const int rows = numControlLoops_ + 1;
    if (cols < 2 || rows < 2)
        return;

    UpdateInterfaceFlag = true;

    selectedStateTable_->blockSignals(true);
    selectedStateTable_->setColumnCount(cols);
    selectedStateTable_->setRowCount(rows);
    for (int c = 0; c < cols; ++c)
    {
        if (c == 0)
            selectedStateTable_->setHorizontalHeaderItem(c, new QTableWidgetItem(tr("")));
        else if (c <= numMotionElements_)
            selectedStateTable_->setHorizontalHeaderItem(c, new QTableWidgetItem(tr("ML%1").arg(c - 1)));
        else
            selectedStateTable_->setHorizontalHeaderItem(c, new QTableWidgetItem(tr("MR%1").arg(c - numMotionElements_ - 1)));
    }
    for (int r = 0; r < rows; ++r)
    {
        if (r == 0)
            selectedStateTable_->setVerticalHeaderItem(r, new QTableWidgetItem(tr("")));
        else
            selectedStateTable_->setVerticalHeaderItem(r, new QTableWidgetItem(tr("CL%1").arg(r - 1)));
    }
    for (int r = 1; r < rows; ++r)
    {
        for (int c = 1; c < cols; ++c)
        {
            std::string genName;
            if (c <= numMotionElements_)
                genName = componentControlName_ + ".NPGeneratorL" + std::to_string(c) + std::to_string(r);
            else
                genName = componentControlName_ + ".NPGeneratorR" + std::to_string(c - numMotionElements_) + std::to_string(r);
            try
            {
                double freq = RDK::ReadParameterValue<double>(genName, "Frequency");
                selectedStateTable_->setItem(r, c, new QTableWidgetItem(QString::number(freq, 'f', 3)));
            }
            catch (...)
            {
                selectedStateTable_->setItem(r, c, new QTableWidgetItem(QStringLiteral("—")));
            }
        }
    }
    selectedStateTable_->blockSignals(false);

    trainedStateTable_->setColumnCount(cols);
    trainedStateTable_->setRowCount(rows);
    for (int c = 0; c < cols; ++c)
    {
        if (c == 0)
            trainedStateTable_->setHorizontalHeaderItem(c, new QTableWidgetItem(tr("")));
        else if (c <= numMotionElements_)
            trainedStateTable_->setHorizontalHeaderItem(c, new QTableWidgetItem(tr("ML%1").arg(c - 1)));
        else
            trainedStateTable_->setHorizontalHeaderItem(c, new QTableWidgetItem(tr("MR%1").arg(c - numMotionElements_ - 1)));
    }
    for (int r = 0; r < rows; ++r)
    {
        if (r == 0)
            trainedStateTable_->setVerticalHeaderItem(r, new QTableWidgetItem(tr("")));
        else
            trainedStateTable_->setVerticalHeaderItem(r, new QTableWidgetItem(tr("CL%1").arg(r - 1)));
    }
    for (int r = 1; r < rows; ++r)
        for (int c = 1; c < cols; ++c)
            trainedStateTable_->setItem(r, c, new QTableWidgetItem(tr("—")));

    UpdateInterfaceFlag = false;
}

void TNNewPositionControlElementWidget::applySelectedCellToModel(int row, int col)
{
    if (componentControlName_.empty() || row < 1 || col < 1)
        return;
    if (col > numMotionElements_ * 2)
        return;
    QTableWidgetItem *item = selectedStateTable_->item(row, col);
    if (!item)
        return;
    bool ok = false;
    double value = item->text().toDouble(&ok);
    if (!ok)
        return;
    std::string genName;
    if (col <= numMotionElements_)
        genName = componentControlName_ + ".NPGeneratorL" + std::to_string(col) + std::to_string(row);
    else
        genName = componentControlName_ + ".NPGeneratorR" + std::to_string(col - numMotionElements_) + std::to_string(row);
    try
    {
        RDK::WriteParameterValue<double>(genName, "Frequency", value);
    }
    catch (...)
    {
    }
}