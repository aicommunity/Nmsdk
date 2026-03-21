#include "TNEnsembleControlWidget.h"

#include <QGroupBox>
#include <QHeaderView>
#include <QHBoxLayout>
#include <QInputDialog>
#include <QLabel>
#include <QLineEdit>
#include <QMessageBox>
#include <QPushButton>
#include <QRadioButton>
#include <QSlider>
#include <QTableWidget>
#include <QVBoxLayout>

#include <rdk_application.h>
#include <rdk_engine_support.h>
#include <rdk_init.h>
#include <rdk_cpp_init.h>

#include <NLifeNet.h>

#include <algorithm>
#include <cctype>

#include <cmath>

namespace {

const int kThresholdSliderScale = 10000;
const double kThresholdDefault = 0.0;

static std::string trim(const std::string &s)
{
    size_t b = 0;
    while (b < s.size() && std::isspace(static_cast<unsigned char>(s[b])))
        ++b;
    size_t e = s.size();
    while (e > b && std::isspace(static_cast<unsigned char>(s[e - 1])))
        --e;
    return s.substr(b, e - b);
}

}

TNEnsembleControlWidget::TNEnsembleControlWidget(QWidget *parent, RDK::UApplication *app)
    : UVisualControllerWidget(parent, app),
      networkNameEdit_(nullptr),
      thresholdGroup_(nullptr),
      thresholdSlider_(nullptr),
      thresholdEdit_(nullptr),
      thresholdModeGroup_(nullptr),
      thresholdMode0_(nullptr),
      thresholdMode1_(nullptr),
      thresholdMode2_(nullptr),
      betaEnsembleGroup_(nullptr),
      betaEnsembleTable_(nullptr),
      ensembleGroup_(nullptr),
      ensembleTable_(nullptr),
      linksGroup_(nullptr),
      linksTable_(nullptr),
      updateInProgress_(false)
{
    Name = "TNEnsembleControlWidget";
    ClassName = "TNEnsembleControlWidget";

    const QString title = tr("Ensemble control (NLifeNet)");
    setAccessibleName(title);
    setWindowTitle(title);

    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(4, 4, 4, 4);

    auto *namesGroup = new QGroupBox(tr("Component (model only)"), this);
    auto *namesLayout = new QVBoxLayout(namesGroup);
    auto *nameRow = new QHBoxLayout();
    nameRow->addWidget(new QLabel(tr("NLifeNet component name:"), this));
    networkNameEdit_ = new QLineEdit(this);
    networkNameEdit_->setPlaceholderText(tr("e.g. LifeNet or path to NLifeNet"));
    nameRow->addWidget(networkNameEdit_, 1);
    findButton_ = new QPushButton(tr("Find NLifeNet"), this);
    nameRow->addWidget(findButton_);
    namesLayout->addLayout(nameRow);
    layout->addWidget(namesGroup);

    thresholdGroup_ = new QGroupBox(tr("Ensemble threshold"), this);
    auto *thLayout = new QVBoxLayout(thresholdGroup_);
    thresholdSlider_ = new QSlider(Qt::Horizontal, thresholdGroup_);
    thresholdSlider_->setRange(0, kThresholdSliderScale);
    thresholdSlider_->setValue(0);
    thresholdEdit_ = new QLineEdit(thresholdGroup_);
    thresholdEdit_->setPlaceholderText("0.00000");
    thLayout->addWidget(thresholdSlider_);
    thLayout->addWidget(thresholdEdit_);
    layout->addWidget(thresholdGroup_);

    thresholdModeGroup_ = new QGroupBox(tr("Ensemble threshold mode"), this);
    auto *modeLayout = new QVBoxLayout(thresholdModeGroup_);
    thresholdMode0_ = new QRadioButton(tr("Mode 0"), thresholdModeGroup_);
    thresholdMode1_ = new QRadioButton(tr("Mode 1 (Gs)"), thresholdModeGroup_);
    thresholdMode2_ = new QRadioButton(tr("Mode 2 (Gs)"), thresholdModeGroup_);
    thresholdMode0_->setChecked(true);
    modeLayout->addWidget(thresholdMode0_);
    modeLayout->addWidget(thresholdMode1_);
    modeLayout->addWidget(thresholdMode2_);
    layout->addWidget(thresholdModeGroup_);

    betaEnsembleGroup_ = new QGroupBox(tr("Beta ensembles"), this);
    betaEnsembleTable_ = new QTableWidget(0, 3, betaEnsembleGroup_);
    betaEnsembleTable_->setHorizontalHeaderLabels({tr("Power"), tr("#1"), tr("#2")});
    betaEnsembleTable_->horizontalHeader()->setStretchLastSection(true);
    auto *betaLayout = new QVBoxLayout(betaEnsembleGroup_);
    betaLayout->addWidget(betaEnsembleTable_);
    layout->addWidget(betaEnsembleGroup_);

    ensembleGroup_ = new QGroupBox(tr("Ensembles"), this);
    ensembleTable_ = new QTableWidget(0, 5, ensembleGroup_);
    ensembleTable_->setHorizontalHeaderLabels({tr("Power"), tr("Activity"), tr("Rel. activity"), tr("#1"), tr("#2")});
    ensembleTable_->horizontalHeader()->setStretchLastSection(true);
    auto *ensLayout = new QVBoxLayout(ensembleGroup_);
    ensLayout->addWidget(ensembleTable_);
    layout->addWidget(ensembleGroup_);

    linksGroup_ = new QGroupBox(tr("Ensemble links"), this);
    linksTable_ = new QTableWidget(0, 4, linksGroup_);
    linksTable_->setHorizontalHeaderLabels({tr("#"), tr("Power"), tr("Source"), tr("Target")});
    linksTable_->horizontalHeader()->setStretchLastSection(true);
    auto *linksLayout = new QVBoxLayout(linksGroup_);
    linksLayout->addWidget(linksTable_);
    layout->addWidget(linksGroup_);

    setPlaceholderTables();

    layout->addStretch();
    setLayout(layout);

    connect(networkNameEdit_, &QLineEdit::editingFinished, this, &TNEnsembleControlWidget::onNetworkNameEdited);
    connect(findButton_, &QPushButton::clicked, this, &TNEnsembleControlWidget::onFindNLifeNetClicked);
    connect(thresholdSlider_, &QSlider::valueChanged, this, &TNEnsembleControlWidget::onThresholdSliderChanged);
    connect(thresholdEdit_, &QLineEdit::editingFinished, this, &TNEnsembleControlWidget::onThresholdEditEdited);
    connect(thresholdMode0_, &QRadioButton::toggled, this, &TNEnsembleControlWidget::onThresholdModeToggled);
    connect(thresholdMode1_, &QRadioButton::toggled, this, &TNEnsembleControlWidget::onThresholdModeToggled);
    connect(thresholdMode2_, &QRadioButton::toggled, this, &TNEnsembleControlWidget::onThresholdModeToggled);
}

TNEnsembleControlWidget::~TNEnsembleControlWidget() = default;

void TNEnsembleControlWidget::AUpdateInterface()
{
    UpdateInterval = 100;
    networkName_ = networkNameEdit_->text().trimmed().toStdString();
    if (networkName_.empty())
    {
        setPlaceholderTables();
        return;
    }
    updateThresholdFromModel();
    updateThresholdModeFromModel();
    updateTablesFromNetwork();
}

void TNEnsembleControlWidget::AClearInterface()
{
    networkName_.clear();
    setPlaceholderTables();
}

void TNEnsembleControlWidget::ASaveParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("EnsembleControl");
    xml.WriteString("NetworkName", networkName_);
    xml.SelectUp();
}

void TNEnsembleControlWidget::ALoadParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("EnsembleControl");
    networkName_ = xml.ReadString("NetworkName", "");
    xml.SelectUp();
    networkNameEdit_->setText(QString::fromStdString(networkName_));
    UpdateInterval = 100;
    // Если имя не было сохранено — пробуем автопоиск
    if (networkName_.empty())
        findAndSetNLifeNet();
}

void TNEnsembleControlWidget::onNetworkNameEdited()
{
    networkName_ = networkNameEdit_->text().trimmed().toStdString();
}

void TNEnsembleControlWidget::onThresholdSliderChanged(int value)
{
    if (updateInProgress_ || networkName_.empty())
        return;
    double th = double(value) / kThresholdSliderScale;
    try
    {
        RDK::WriteParameterValue<double>(networkName_, "EnsembleThreshold", th);
    }
    catch (...)
    {
    }
    thresholdEdit_->setText(QString::number(th, 'f', 5));
}

void TNEnsembleControlWidget::onThresholdEditEdited()
{
    if (updateInProgress_ || networkName_.empty())
        return;
    bool ok = false;
    double th = thresholdEdit_->text().trimmed().toDouble(&ok);
    if (!ok)
        return;
    try
    {
        RDK::WriteParameterValue<double>(networkName_, "EnsembleThreshold", th);
    }
    catch (...)
    {
    }
    thresholdSlider_->blockSignals(true);
    thresholdSlider_->setValue(static_cast<int>(std::round(th * kThresholdSliderScale)));
    thresholdSlider_->blockSignals(false);
}

void TNEnsembleControlWidget::onThresholdModeToggled()
{
    if (updateInProgress_ || networkName_.empty())
        return;
    int mode = 0;
    if (thresholdMode1_->isChecked())
        mode = 1;
    else if (thresholdMode2_->isChecked())
        mode = 2;
    try
    {
        RDK::WriteParameterValue<int>(networkName_, "EnsembleThresholdMode", mode);
    }
    catch (...)
    {
    }
}

void TNEnsembleControlWidget::updateThresholdFromModel()
{
    try
    {
        double th = RDK::ReadParameterValue<double>(networkName_, "EnsembleThreshold");
        updateInProgress_ = true;
        thresholdSlider_->setValue(static_cast<int>(std::round(th * kThresholdSliderScale)));
        thresholdEdit_->setText(QString::number(th, 'f', 5));
        updateInProgress_ = false;
    }
    catch (...)
    {
    }
}

void TNEnsembleControlWidget::updateThresholdModeFromModel()
{
    try
    {
        int mode = static_cast<int>(RDK::ReadParameterValue<double>(networkName_, "EnsembleThresholdMode"));
        updateInProgress_ = true;
        thresholdMode0_->setChecked(mode == 0);
        thresholdMode1_->setChecked(mode == 1);
        thresholdMode2_->setChecked(mode == 2);
        updateInProgress_ = false;
    }
    catch (...)
    {
    }
}

void TNEnsembleControlWidget::setPlaceholderTables()
{
    betaEnsembleTable_->setRowCount(0);
    betaEnsembleTable_->setRowCount(1);
    betaEnsembleTable_->setItem(0, 0, new QTableWidgetItem(networkName_.empty()
        ? tr("— Specify NLifeNet component name —")
        : tr("— NLifeNet ensemble data requires engine API —")));
    betaEnsembleTable_->setSpan(0, 0, 1, 3);

    ensembleTable_->setRowCount(0);
    ensembleTable_->setRowCount(1);
    ensembleTable_->setItem(0, 0, new QTableWidgetItem(networkName_.empty()
        ? tr("— Specify NLifeNet component name —")
        : tr("— NLifeNet ensemble data requires engine API —")));
    ensembleTable_->setSpan(0, 0, 1, 5);

    linksTable_->setRowCount(0);
    linksTable_->setRowCount(1);
    linksTable_->setItem(0, 0, new QTableWidgetItem(networkName_.empty()
        ? tr("— Specify NLifeNet component name —")
        : tr("— NLifeNet links data requires engine API —")));
    linksTable_->setSpan(0, 0, 1, 4);
}

void TNEnsembleControlWidget::updateTablesFromNetwork()
{
    if (networkName_.empty())
    {
        setPlaceholderTables();
        return;
    }

    try
    {
        RDK::UELockPtr<RDK::UContainer> model = RDK::GetModelLock<RDK::UContainer>();
        if (!model)
        {
            setPlaceholderTables();
            return;
        }

        RDK::UEPtr<NMSDK::NLifeNet> lifeNet = model->GetComponentL<NMSDK::NLifeNet>(networkName_, true);
        if (!lifeNet)
        {
            setPlaceholderTables();
            return;
        }

        // Update Beta Ensembles table
        size_t numBetaEnsembles = lifeNet->GetNumBetaEnsembles();
        betaEnsembleTable_->setRowCount(static_cast<int>(numBetaEnsembles));
        for (size_t i = 0; i < numBetaEnsembles; ++i)
        {
            double power = lifeNet->GetBetaEnsemblePower(i);
            const NMSDK::NEnsemble &ensemble = lifeNet->GetBetaEnsemble(i);
            QString neuron1, neuron2;
            if (ensemble.size() > 0)
                neuron1 = QString::fromStdString(ensemble[0]->GetName());
            if (ensemble.size() > 1)
                neuron2 = QString::fromStdString(ensemble[1]->GetName());

            betaEnsembleTable_->setItem(static_cast<int>(i), 0, new QTableWidgetItem(QString::number(power, 'f', 3)));
            betaEnsembleTable_->setItem(static_cast<int>(i), 1, new QTableWidgetItem(neuron1));
            betaEnsembleTable_->setItem(static_cast<int>(i), 2, new QTableWidgetItem(neuron2));
        }

        // Update Ensembles table
        size_t numEnsembles = lifeNet->GetNumEnsembles();
        ensembleTable_->setRowCount(static_cast<int>(numEnsembles));
        for (size_t i = 0; i < numEnsembles; ++i)
        {
            double power = lifeNet->GetEnsemblePower(i);
            double activity = lifeNet->GetEnsembleActivity(i);
            double relActivity = lifeNet->GetRelativeEnsembleActivity(i);
            const NMSDK::NEnsemble &ensemble = lifeNet->GetEnsemble(i);
            QString neuron1, neuron2;
            if (ensemble.size() > 0)
                neuron1 = QString::fromStdString(ensemble[0]->GetName());
            if (ensemble.size() > 1)
                neuron2 = QString::fromStdString(ensemble[1]->GetName());

            ensembleTable_->setItem(static_cast<int>(i), 0, new QTableWidgetItem(QString::number(power, 'f', 3)));
            ensembleTable_->setItem(static_cast<int>(i), 1, new QTableWidgetItem(QString::number(activity, 'f', 3)));
            ensembleTable_->setItem(static_cast<int>(i), 2, new QTableWidgetItem(QString::number(relActivity, 'f', 3)));
            ensembleTable_->setItem(static_cast<int>(i), 3, new QTableWidgetItem(neuron1));
            ensembleTable_->setItem(static_cast<int>(i), 4, new QTableWidgetItem(neuron2));
        }

        // Update Ensemble Links table
        size_t numLinks = lifeNet->GetNumEnsembleLinks();
        linksTable_->setRowCount(static_cast<int>(numLinks));
        for (size_t i = 0; i < numLinks; ++i)
        {
            const NMSDK::NEnsembleLink &link = lifeNet->GetEnsembleLink(i);
            linksTable_->setItem(static_cast<int>(i), 0, new QTableWidgetItem(QString::number(i)));
            linksTable_->setItem(static_cast<int>(i), 1, new QTableWidgetItem(QString::number(link.Power, 'f', 3)));
            linksTable_->setItem(static_cast<int>(i), 2, new QTableWidgetItem(QString::fromStdString(link.In)));
            linksTable_->setItem(static_cast<int>(i), 3, new QTableWidgetItem(QString::fromStdString(link.Out)));
        }
    }
    catch (...)
    {
        // Fallback to placeholder tables if engine API is not available
        setPlaceholderTables();
    }
}

void TNEnsembleControlWidget::onFindNLifeNetClicked()
{
    findAndSetNLifeNet();
}

void TNEnsembleControlWidget::findAndSetNLifeNet()
{
    const char *raw = Model_FindComponentsByClassName("", "NLifeNet", true);
    if (!raw || !*raw)
    {
        QMessageBox::information(this, tr("Not found"), tr("No NLifeNet components found in the model."));
        return;
    }

    const auto names = splitCsv(raw);
    if (names.empty())
    {
        QMessageBox::information(this, tr("Not found"), tr("No NLifeNet components found in the model."));
        return;
    }

    if (names.size() == 1)
    {
        // Автоподстановка единственного найденного компонента
        networkName_ = names[0];
        networkNameEdit_->setText(QString::fromStdString(networkName_));
        updateThresholdFromModel();
        updateThresholdModeFromModel();
    }
    else
    {
        // Несколько компонентов — показываем список для выбора
        QStringList items;
        for (const auto &n : names)
            items << QString::fromStdString(n);

        bool ok = false;
        QString selected = QInputDialog::getItem(this, tr("Select NLifeNet"), tr("Found %1 NLifeNet components:").arg(names.size()),
                                                 items, 0, false, &ok);
        if (ok && !selected.isEmpty())
        {
            networkName_ = selected.toStdString();
            networkNameEdit_->setText(selected);
            updateThresholdFromModel();
            updateThresholdModeFromModel();
        }
    }
}

std::vector<std::string> TNEnsembleControlWidget::splitCsv(const std::string &csv)
{
    std::vector<std::string> out;
    std::string cur;
    for (char c : csv)
    {
        if (c == ',')
        {
            const auto t = trim(cur);
            if (!t.empty())
                out.push_back(t);
            cur.clear();
        }
        else
        {
            cur.push_back(c);
        }
    }
    const auto t = trim(cur);
    if (!t.empty())
        out.push_back(t);
    return out;
}
