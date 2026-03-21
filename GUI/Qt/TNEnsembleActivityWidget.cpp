#include "TNEnsembleActivityWidget.h"

#include <QGroupBox>
#include <QHBoxLayout>
#include <QInputDialog>
#include <QLabel>
#include <QLineEdit>
#include <QMessageBox>
#include <QPushButton>
#include <QVBoxLayout>

#include <rdk_application.h>
#include <rdk_init.h>

#include "UWatchTab.h"
#include "UWatchChart.h"

#include <algorithm>
#include <cctype>

namespace {

constexpr double kDefaultTimeIntervalSec = 10.0;

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

TNEnsembleActivityWidget::TNEnsembleActivityWidget(QWidget *parent, RDK::UApplication *app)
    : UVisualControllerWidget(parent, app),
      networkGroup_(nullptr),
      networkNameEdit_(nullptr),
      addSeriesButton_(nullptr),
      addDefaultSeriesButton_(nullptr),
      watchTab_(nullptr)
{
    Name = "TNEnsembleActivityWidget";
    ClassName = "TNEnsembleActivityWidget";

    const QString title = tr("Ensemble activity (Watch)");
    setAccessibleName(title);
    setWindowTitle(title);

    auto *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(4, 4, 4, 4);

    networkGroup_ = new QGroupBox(tr("NLifeNet (model only)"), this);
    auto *netLayout = new QHBoxLayout(networkGroup_);
    netLayout->addWidget(new QLabel(tr("Component name:"), networkGroup_));
    networkNameEdit_ = new QLineEdit(networkGroup_);
    networkNameEdit_->setPlaceholderText(tr("e.g. LifeNet"));
    netLayout->addWidget(networkNameEdit_, 1);
    findButton_ = new QPushButton(tr("Find NLifeNet"), networkGroup_);
    addSeriesButton_ = new QPushButton(tr("Add series..."), networkGroup_);
    addDefaultSeriesButton_ = new QPushButton(tr("Add default Summary*"), networkGroup_);
    netLayout->addWidget(findButton_);
    netLayout->addWidget(addSeriesButton_);
    netLayout->addWidget(addDefaultSeriesButton_);
    mainLayout->addWidget(networkGroup_);

    // Встраиваем существующую вкладку Watch (1x1 график по умолчанию).
    watchTab_ = new UWatchTab(this, app);
    mainLayout->addWidget(watchTab_, 1);

    setLayout(mainLayout);

    connect(networkNameEdit_, &QLineEdit::editingFinished, this, &TNEnsembleActivityWidget::onNetworkNameEdited);
    connect(findButton_, &QPushButton::clicked, this, &TNEnsembleActivityWidget::onFindNLifeNetClicked);
    connect(addSeriesButton_, &QPushButton::clicked, this, &TNEnsembleActivityWidget::onAddSeriesClicked);
    connect(addDefaultSeriesButton_, &QPushButton::clicked, this, &TNEnsembleActivityWidget::onAddDefaultSeriesClicked);
}

TNEnsembleActivityWidget::~TNEnsembleActivityWidget() = default;

void TNEnsembleActivityWidget::AUpdateInterface()
{
    UpdateInterval = 200;
    watchTab_->UpdateInterface(false);
}

void TNEnsembleActivityWidget::AClearInterface()
{
    networkName_.clear();
    networkNameEdit_->clear();
    watchTab_->ClearInterface();
}

void TNEnsembleActivityWidget::ASaveParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("EnsembleActivity");
    xml.WriteString("NetworkName", networkName_);
    xml.SelectUp();

    // UWatchTab умеет сохранять/загружать параметры через XML, но метод сигнатурой отличается
    // от UVisualControllerWidget. Здесь сохраняем минимум (имя компонента),
    // а состав серий пользователь может сохранить через стандартный Watch UI при необходимости.
}

void TNEnsembleActivityWidget::ALoadParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("EnsembleActivity");
    networkName_ = xml.ReadString("NetworkName", "");
    xml.SelectUp();
    networkNameEdit_->setText(QString::fromStdString(networkName_));
    // Если имя не было сохранено — пробуем автопоиск
    if (networkName_.empty())
        findAndSetNLifeNet();
}

void TNEnsembleActivityWidget::onNetworkNameEdited()
{
    networkName_ = networkNameEdit_->text().trimmed().toStdString();
}

void TNEnsembleActivityWidget::onAddSeriesClicked()
{
    // Открываем стандартный диалог выбора свойства для графика 0.
    watchTab_->createSelectionDialog(0);
}

void TNEnsembleActivityWidget::onAddDefaultSeriesClicked()
{
    onNetworkNameEdited();
    if (networkName_.empty())
        return;
    addDefaultSeries(networkName_);
}

void TNEnsembleActivityWidget::onFindNLifeNetClicked()
{
    findAndSetNLifeNet();
}

void TNEnsembleActivityWidget::findAndSetNLifeNet()
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
        }
    }
}

std::vector<std::string> TNEnsembleActivityWidget::splitCsv(const std::string &csv)
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

void TNEnsembleActivityWidget::addDefaultSeries(const std::string &componentName)
{
    UWatchChart *chart = watchTab_->getChart(0);
    if (!chart)
        return;

    const QString comp = QString::fromStdString(componentName);
    const QStringList props = {
        QStringLiteral("SummaryEnergy"),
        QStringLiteral("SummaryFrequency"),
        QStringLiteral("SummaryLiveNeurons"),
        QStringLiteral("SummaryFeeling"),
        QStringLiteral("SummaryWearOut"),
    };

    for (int i = 0; i < props.size(); ++i)
    {
        chart->createSerie(
            /*channelIndex*/ 0,
            comp,
            props[i],
            QStringLiteral("type"),
            /*jx*/ 0,
            /*jy*/ 0,
            kDefaultTimeIntervalSec,
            /*y_shift*/ 0.0);
    }
}

