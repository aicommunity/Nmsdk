#include "TNManipulatorStatisticsWidget.h"

#include <QGroupBox>
#include <QHBoxLayout>
#include <QHeaderView>
#include <QLabel>
#include <QLineEdit>
#include <QPushButton>
#include <QTableWidget>
#include <QVBoxLayout>

#include <rdk_application.h>
#include <rdk_cpp_init.h>
#include <rdk_engine_support.h>

#include <UContainer.h>

#include <cmath>

namespace {

QTableWidgetItem *makeItem(const QString &text)
{
    auto *it = new QTableWidgetItem(text);
    it->setFlags(it->flags() & ~Qt::ItemIsEditable);
    return it;
}

} // namespace

TNManipulatorStatisticsWidget::TNManipulatorStatisticsWidget(QWidget *parent, RDK::UApplication *app)
    : UVisualControllerWidget(parent, app),
      namesGroup_(nullptr),
      controlSystemNameEdit_(nullptr),
      statisticNameEdit_(nullptr),
      resetButton_(nullptr),
      saveStatsButton_(nullptr),
      newStatsButton_(nullptr),
      propsTable_(nullptr)
{
    Name = "TNManipulatorStatisticsWidget";
    ClassName = "TNManipulatorStatisticsWidget";

    const QString title = tr("Manipulator statistics");
    setAccessibleName(title);
    setWindowTitle(title);

    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(4, 4, 4, 4);

    namesGroup_ = new QGroupBox(tr("Components"), this);
    auto *namesLayout = new QVBoxLayout(namesGroup_);
    namesLayout->addWidget(new QLabel(tr("Control system name:"), namesGroup_));
    controlSystemNameEdit_ = new QLineEdit(namesGroup_);
    controlSystemNameEdit_->setPlaceholderText(tr("e.g. MotionControlEngine"));
    namesLayout->addWidget(controlSystemNameEdit_);

    namesLayout->addWidget(new QLabel(tr("Statistic component name (child):"), namesGroup_));
    statisticNameEdit_ = new QLineEdit(namesGroup_);
    statisticNameEdit_->setText(QString::fromStdString(statisticComponentName_));
    namesLayout->addWidget(statisticNameEdit_);
    layout->addWidget(namesGroup_);

    auto *buttonsRow = new QHBoxLayout();
    resetButton_ = new QPushButton(tr("Reset"), this);
    newStatsButton_ = new QPushButton(tr("New stats"), this);
    saveStatsButton_ = new QPushButton(tr("Save stats"), this);
    buttonsRow->addWidget(resetButton_);
    buttonsRow->addWidget(newStatsButton_);
    buttonsRow->addWidget(saveStatsButton_);
    buttonsRow->addStretch(1);
    layout->addLayout(buttonsRow);

    propsTable_ = new QTableWidget(0, 2, this);
    propsTable_->setHorizontalHeaderLabels({tr("Property"), tr("Value")});
    propsTable_->horizontalHeader()->setStretchLastSection(true);
    propsTable_->verticalHeader()->setVisible(false);
    layout->addWidget(propsTable_, 1);

    layout->addStretch();
    setLayout(layout);

    connect(controlSystemNameEdit_, &QLineEdit::editingFinished, this, &TNManipulatorStatisticsWidget::onControlSystemNameEdited);
    connect(statisticNameEdit_, &QLineEdit::editingFinished, this, &TNManipulatorStatisticsWidget::onStatisticNameEdited);
    connect(resetButton_, &QPushButton::clicked, this, &TNManipulatorStatisticsWidget::onResetClicked);
    connect(saveStatsButton_, &QPushButton::clicked, this, &TNManipulatorStatisticsWidget::onSaveStatsClicked);
    connect(newStatsButton_, &QPushButton::clicked, this, &TNManipulatorStatisticsWidget::onNewStatsClicked);

    updateButtonsEnabled(false);
    updatePropertiesTable(false);
}

TNManipulatorStatisticsWidget::~TNManipulatorStatisticsWidget() = default;

std::string TNManipulatorStatisticsWidget::statisticFullName() const
{
    if (controlSystemName_.empty() || statisticComponentName_.empty())
        return "";
    return controlSystemName_ + "." + statisticComponentName_;
}

bool TNManipulatorStatisticsWidget::tryResolveStatisticExists() const
{
    const std::string fullName = statisticFullName();
    if (fullName.empty())
        return false;
    try
    {
        (void)RDK::ReadParameterValue<int>(fullName, "Activity");
        return true;
    }
    catch (...)
    {
        return false;
    }
}

void TNManipulatorStatisticsWidget::updateButtonsEnabled(bool hasStatistic)
{
    resetButton_->setEnabled(hasStatistic);
    newStatsButton_->setEnabled(hasStatistic);
    saveStatsButton_->setEnabled(hasStatistic);
}

void TNManipulatorStatisticsWidget::updatePropertiesTable(bool hasStatistic)
{
    propsTable_->setRowCount(0);
    if (!hasStatistic)
    {
        propsTable_->setRowCount(1);
        propsTable_->setItem(0, 0, makeItem(tr("—")));
        propsTable_->setItem(0, 1, makeItem(tr("Specify control system + statistic child name")));
        propsTable_->setSpan(0, 0, 1, 2);
        return;
    }

    const std::string fullName = statisticFullName();

    struct Row { const char *key; bool isState; };
    const Row rows[] = {
        {"SavePath", false},
        {"PrefixName", false},
        {"SaveMode", false},
        {"AverageMode", false},
        {"AverageNumber", false},
        {"ManualModeEnabled", false},
        {"ManualModeSwitch", false},
        {"CurrentAverageNumber", true},
    };

    propsTable_->setRowCount(int(std::size(rows)));
    for (int i = 0; i < int(std::size(rows)); ++i)
    {
        propsTable_->setItem(i, 0, makeItem(QString::fromLatin1(rows[i].key)));
        QString value = tr("—");
        try
        {
            if (rows[i].isState)
            {
                double v = RDK::ReadStateValue<double>(fullName, rows[i].key);
                value = QString::number(v, 'f', 3);
            }
            else
            {
                // часть свойств строковые, часть числовые/булевы — пробуем по очереди
                try
                {
                    std::string s = RDK::ReadParameterValue<std::string>(fullName, rows[i].key);
                    value = QString::fromStdString(s);
                }
                catch (...)
                {
                    double v = RDK::ReadParameterValue<double>(fullName, rows[i].key);
                    value = QString::number(v, 'f', 3);
                }
            }
        }
        catch (...)
        {
        }
        propsTable_->setItem(i, 1, makeItem(value));
    }
}

bool TNManipulatorStatisticsWidget::tryResetStatisticComponent()
{
    const std::string fullName = statisticFullName();
    if (fullName.empty())
        return false;

    try
    {
        RDK::UELockPtr<RDK::UContainer> model = RDK::GetModelLock<RDK::UContainer>();
        if (!model)
            return false;
        return model->ResetComponentAll(fullName);
    }
    catch (...)
    {
        return false;
    }
}

void TNManipulatorStatisticsWidget::AUpdateInterface()
{
    UpdateInterval = 200;

    const bool hasStat = tryResolveStatisticExists();
    updateButtonsEnabled(hasStat);
    updatePropertiesTable(hasStat);
}

void TNManipulatorStatisticsWidget::AClearInterface()
{
    controlSystemName_.clear();
    statisticComponentName_ = "StatisticDoubleMatrix";
    controlSystemNameEdit_->clear();
    statisticNameEdit_->setText(QString::fromStdString(statisticComponentName_));
    updateButtonsEnabled(false);
    updatePropertiesTable(false);
}

void TNManipulatorStatisticsWidget::ASaveParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("ManipulatorStatistics");
    xml.WriteString("ControlSystemName", controlSystemName_);
    xml.WriteString("StatisticChildName", statisticComponentName_);
    xml.SelectUp();
}

void TNManipulatorStatisticsWidget::ALoadParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("ManipulatorStatistics");
    controlSystemName_ = xml.ReadString("ControlSystemName", "");
    statisticComponentName_ = xml.ReadString("StatisticChildName", "StatisticDoubleMatrix");
    xml.SelectUp();
    controlSystemNameEdit_->setText(QString::fromStdString(controlSystemName_));
    statisticNameEdit_->setText(QString::fromStdString(statisticComponentName_));
}

void TNManipulatorStatisticsWidget::onControlSystemNameEdited()
{
    controlSystemName_ = controlSystemNameEdit_->text().trimmed().toStdString();
}

void TNManipulatorStatisticsWidget::onStatisticNameEdited()
{
    statisticComponentName_ = statisticNameEdit_->text().trimmed().toStdString();
}

void TNManipulatorStatisticsWidget::onResetClicked()
{
    if (UpdateInterfaceFlag)
        return;
    (void)tryResetStatisticComponent();
}

void TNManipulatorStatisticsWidget::onSaveStatsClicked()
{
    if (UpdateInterfaceFlag)
        return;
    const std::string fullName = statisticFullName();
    if (fullName.empty())
        return;
    try
    {
        RDK::WriteParameterValue<int>(fullName, "ManualModeSwitch", 1);
    }
    catch (...)
    {
    }
}

void TNManipulatorStatisticsWidget::onNewStatsClicked()
{
    if (UpdateInterfaceFlag)
        return;
    const std::string fullName = statisticFullName();
    if (fullName.empty())
        return;
    try
    {
        RDK::WriteParameterValue<int>(fullName, "ManualModeSwitch", 0);
        RDK::WriteParameterValue<int>(fullName, "ManualModeEnabled", 1);
    }
    catch (...)
    {
    }
    (void)tryResetStatisticComponent();
}

