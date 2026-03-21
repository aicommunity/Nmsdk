#include "TNSourceControlWidget.h"

#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QListWidget>
#include <QPushButton>
#include <QSlider>
#include <QSplitter>
#include <QVBoxLayout>

#include <rdk_application.h>
#include <rdk_engine_support.h>
#include <rdk_init.h>

#include "UWatchTab.h"

#include <algorithm>
#include <cctype>

namespace {

constexpr int kAmpSliderMax = 1000;   // 0..100.0 (scale 0.1)
constexpr int kFreqSliderMax = 2000;  // 0..200.0 (scale 0.1)
constexpr double kScale = 0.1;

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

} // namespace

TNSourceControlWidget::TNSourceControlWidget(QWidget *parent, RDK::UApplication *app)
    : UVisualControllerWidget(parent, app),
      sourcesGroup_(nullptr),
      sourcesList_(nullptr),
      findPulseGeneratorsButton_(nullptr),
      paramsGroup_(nullptr),
      selectedLabel_(nullptr),
      amplitudeSlider_(nullptr),
      amplitudeEdit_(nullptr),
      frequencySlider_(nullptr),
      frequencyEdit_(nullptr),
      addWatchSeriesButton_(nullptr),
      watchTab_(nullptr)
{
    Name = "TNSourceControlWidget";
    ClassName = "TNSourceControlWidget";

    const QString title = tr("Source control (NPulseGenerator)");
    setAccessibleName(title);
    setWindowTitle(title);

    auto *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(4, 4, 4, 4);

    auto *splitter = new QSplitter(Qt::Vertical, this);

    sourcesGroup_ = new QGroupBox(tr("Sources"), this);
    auto *srcLayout = new QVBoxLayout(sourcesGroup_);
    findPulseGeneratorsButton_ = new QPushButton(tr("Find NPulseGenerator"), sourcesGroup_);
    sourcesList_ = new QListWidget(sourcesGroup_);
    srcLayout->addWidget(findPulseGeneratorsButton_);
    srcLayout->addWidget(sourcesList_, 1);

    paramsGroup_ = new QGroupBox(tr("Parameters (model only)"), this);
    auto *pLayout = new QVBoxLayout(paramsGroup_);
    selectedLabel_ = new QLabel(tr("Selected: —"), paramsGroup_);
    pLayout->addWidget(selectedLabel_);

    pLayout->addWidget(new QLabel(tr("Amplitude"), paramsGroup_));
    amplitudeSlider_ = new QSlider(Qt::Horizontal, paramsGroup_);
    amplitudeSlider_->setRange(0, kAmpSliderMax);
    amplitudeEdit_ = new QLineEdit(paramsGroup_);
    amplitudeEdit_->setPlaceholderText("0.0");
    pLayout->addWidget(amplitudeSlider_);
    pLayout->addWidget(amplitudeEdit_);

    pLayout->addWidget(new QLabel(tr("Frequency"), paramsGroup_));
    frequencySlider_ = new QSlider(Qt::Horizontal, paramsGroup_);
    frequencySlider_->setRange(0, kFreqSliderMax);
    frequencyEdit_ = new QLineEdit(paramsGroup_);
    frequencyEdit_->setPlaceholderText("0.0");
    pLayout->addWidget(frequencySlider_);
    pLayout->addWidget(frequencyEdit_);

    addWatchSeriesButton_ = new QPushButton(tr("Add watch series..."), paramsGroup_);
    pLayout->addWidget(addWatchSeriesButton_);

    auto *top = new QWidget(this);
    auto *topLayout = new QVBoxLayout(top);
    topLayout->setContentsMargins(0, 0, 0, 0);
    topLayout->addWidget(sourcesGroup_, 1);
    topLayout->addWidget(paramsGroup_);
    top->setLayout(topLayout);

    watchTab_ = new UWatchTab(this, app);

    splitter->addWidget(top);
    splitter->addWidget(watchTab_);
    splitter->setStretchFactor(0, 1);
    splitter->setStretchFactor(1, 2);
    mainLayout->addWidget(splitter, 1);
    setLayout(mainLayout);

    connect(findPulseGeneratorsButton_, &QPushButton::clicked, this, &TNSourceControlWidget::onFindSourcesClicked);
    connect(sourcesList_, &QListWidget::currentRowChanged, this, &TNSourceControlWidget::onSourceSelectionChanged);
    connect(amplitudeSlider_, &QSlider::valueChanged, this, &TNSourceControlWidget::onAmplitudeSliderChanged);
    connect(amplitudeEdit_, &QLineEdit::editingFinished, this, &TNSourceControlWidget::onAmplitudeEdited);
    connect(frequencySlider_, &QSlider::valueChanged, this, &TNSourceControlWidget::onFrequencySliderChanged);
    connect(frequencyEdit_, &QLineEdit::editingFinished, this, &TNSourceControlWidget::onFrequencyEdited);
    connect(addWatchSeriesButton_, &QPushButton::clicked, this, &TNSourceControlWidget::onAddWatchSeriesClicked);
}

TNSourceControlWidget::~TNSourceControlWidget() = default;

void TNSourceControlWidget::AUpdateInterface()
{
    UpdateInterval = 200;
    refreshSelectedFromModel();
    watchTab_->UpdateInterface(false);
}

void TNSourceControlWidget::AClearInterface()
{
    selectedSourceName_.clear();
    sourcesList_->clear();
    selectedLabel_->setText(tr("Selected: —"));
    amplitudeEdit_->clear();
    frequencyEdit_->clear();
    amplitudeSlider_->setValue(0);
    frequencySlider_->setValue(0);
    watchTab_->ClearInterface();
}

void TNSourceControlWidget::ASaveParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("SourceControl");
    xml.WriteString("SelectedSource", selectedSourceName_);
    xml.SelectUp();
}

void TNSourceControlWidget::ALoadParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("SourceControl");
    selectedSourceName_ = xml.ReadString("SelectedSource", "");
    xml.SelectUp();
    refreshSelectedFromModel();
}

void TNSourceControlWidget::onFindSourcesClicked()
{
    sourcesList_->clear();

    // Ищем компоненты по классу NPulseGenerator во всей модели.
    const char *raw = Model_FindComponentsByClassName("", "NPulseGenerator", true);
    if (!raw)
        return;

    const auto names = splitCsv(raw);
    for (const auto &n : names)
    {
        if (!n.empty())
            sourcesList_->addItem(QString::fromStdString(n));
    }

    // Если ранее был выбран источник — попробуем выбрать его в списке.
    if (!selectedSourceName_.empty())
    {
        for (int i = 0; i < sourcesList_->count(); ++i)
        {
            if (sourcesList_->item(i)->text().toStdString() == selectedSourceName_)
            {
                sourcesList_->setCurrentRow(i);
                break;
            }
        }
    }
}

void TNSourceControlWidget::onSourceSelectionChanged()
{
    const auto *item = sourcesList_->currentItem();
    if (!item)
        return;
    setSelectedSource(item->text().toStdString());
}

void TNSourceControlWidget::setSelectedSource(const std::string &name)
{
    selectedSourceName_ = name;
    selectedLabel_->setText(tr("Selected: %1").arg(QString::fromStdString(selectedSourceName_)));
    refreshSelectedFromModel();

    // Auto WatchUpdate: add a few default series for the selected source output.
    if (watchTab_ && watchTab_->getChart(0))
    {
        struct SerieSpec { const char *prop; };
        const SerieSpec defaults[] = {
            {"Output"},
            {"OutputFrequency"},
            {"OutputPotential"},
            {"ActionCounter"},
        };

        UWatchChart *chart = watchTab_->getChart(0);
        for (const auto &spec : defaults)
        {
            bool exists = false;
            for (int i = 0; i < chart->countSeries(); ++i)
            {
                UWatchSerie *s = chart->getSerie(i);
                if (!s)
                    continue;
                if (s->nameComponent.toStdString() == selectedSourceName_
                    && s->nameProperty.toStdString() == spec.prop
                    && s->Jx == 0 && s->Jy == 0)
                {
                    exists = true;
                    break;
                }
            }
            if (!exists)
            {
                chart->createSerie(0,
                                   QString::fromStdString(selectedSourceName_),
                                   QString::fromLatin1(spec.prop),
                                   QStringLiteral("double"),
                                   0, 0,
                                   10.0,
                                   0.0);
            }
        }
    }
}

void TNSourceControlWidget::refreshSelectedFromModel()
{
    if (selectedSourceName_.empty())
        return;

    updateInProgress_ = true;
    try
    {
        const double amp = RDK::ReadParameterValue<double>(selectedSourceName_, "Amplitude");
        amplitudeEdit_->setText(QString::number(amp, 'f', 3));
        amplitudeSlider_->setValue(std::clamp(int(amp / kScale), 0, kAmpSliderMax));
    }
    catch (...)
    {
    }

    try
    {
        const double freq = RDK::ReadParameterValue<double>(selectedSourceName_, "Frequency");
        frequencyEdit_->setText(QString::number(freq, 'f', 3));
        frequencySlider_->setValue(std::clamp(int(freq / kScale), 0, kFreqSliderMax));
    }
    catch (...)
    {
    }
    updateInProgress_ = false;
}

void TNSourceControlWidget::onAmplitudeSliderChanged(int value)
{
    if (updateInProgress_ || selectedSourceName_.empty())
        return;
    const double amp = double(value) * kScale;
    amplitudeEdit_->setText(QString::number(amp, 'f', 3));
    try
    {
        RDK::WriteParameterValue<double>(selectedSourceName_, "Amplitude", amp);
    }
    catch (...)
    {
    }
}

void TNSourceControlWidget::onAmplitudeEdited()
{
    if (updateInProgress_ || selectedSourceName_.empty())
        return;
    bool ok = false;
    const double amp = amplitudeEdit_->text().trimmed().toDouble(&ok);
    if (!ok)
        return;
    try
    {
        RDK::WriteParameterValue<double>(selectedSourceName_, "Amplitude", amp);
    }
    catch (...)
    {
    }
    updateInProgress_ = true;
    amplitudeSlider_->setValue(std::clamp(int(amp / kScale), 0, kAmpSliderMax));
    updateInProgress_ = false;
}

void TNSourceControlWidget::onFrequencySliderChanged(int value)
{
    if (updateInProgress_ || selectedSourceName_.empty())
        return;
    const double freq = double(value) * kScale;
    frequencyEdit_->setText(QString::number(freq, 'f', 3));
    try
    {
        RDK::WriteParameterValue<double>(selectedSourceName_, "Frequency", freq);
    }
    catch (...)
    {
    }
}

void TNSourceControlWidget::onFrequencyEdited()
{
    if (updateInProgress_ || selectedSourceName_.empty())
        return;
    bool ok = false;
    const double freq = frequencyEdit_->text().trimmed().toDouble(&ok);
    if (!ok)
        return;
    try
    {
        RDK::WriteParameterValue<double>(selectedSourceName_, "Frequency", freq);
    }
    catch (...)
    {
    }
    updateInProgress_ = true;
    frequencySlider_->setValue(std::clamp(int(freq / kScale), 0, kFreqSliderMax));
    updateInProgress_ = false;
}

std::vector<std::string> TNSourceControlWidget::splitCsv(const std::string &csv)
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

void TNSourceControlWidget::onAddWatchSeriesClicked()
{
    if (selectedSourceName_.empty())
        return;
    // Открываем стандартный диалог выбора свойства для графика 0.
    watchTab_->createSelectionDialog(0);
}

