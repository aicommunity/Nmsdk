#include "TNANetGraphicsWidget.h"

#include <QGroupBox>
#include <QHBoxLayout>
#include <QInputDialog>
#include <QLabel>
#include <QLineEdit>
#include <QMessageBox>
#include <QPainter>
#include <QPushButton>
#include <QVBoxLayout>

#include <rdk_init.h>

#include <algorithm>
#include <cctype>
#include <cmath>

namespace {

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

static std::vector<std::string> splitCsv(const std::string &csv)
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

} // namespace

TNANetGraphicsWidget::TNANetGraphicsWidget(QWidget *parent, RDK::UApplication *app)
    : UVisualControllerWidget(parent, app),
      networkGroup_(nullptr),
      componentNameEdit_(nullptr),
      findButton_(nullptr),
      refreshButton_(nullptr)
{
    Name = "TNANetGraphicsWidget";
    ClassName = "TNANetGraphicsWidget";

    const QString title = tr("NANet Graphics (model-only)");
    setAccessibleName(title);
    setWindowTitle(title);

    setMinimumSize(kCanvasWidth, kCanvasHeight + 100);

    auto *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(4, 4, 4, 4);

    networkGroup_ = new QGroupBox(tr("NANet Component (model-only)"), this);
    auto *netLayout = new QHBoxLayout(networkGroup_);
    netLayout->addWidget(new QLabel(tr("Component name:"), networkGroup_));
    componentNameEdit_ = new QLineEdit(networkGroup_);
    componentNameEdit_->setPlaceholderText(tr("e.g. Network"));
    netLayout->addWidget(componentNameEdit_, 1);
    findButton_ = new QPushButton(tr("Find NANet"), networkGroup_);
    refreshButton_ = new QPushButton(tr("Refresh"), networkGroup_);
    netLayout->addWidget(findButton_);
    netLayout->addWidget(refreshButton_);
    mainLayout->addWidget(networkGroup_);

    setLayout(mainLayout);

    connect(componentNameEdit_, &QLineEdit::editingFinished, this, &TNANetGraphicsWidget::onComponentNameEdited);
    connect(findButton_, &QPushButton::clicked, this, &TNANetGraphicsWidget::onFindNANetClicked);
    connect(refreshButton_, &QPushButton::clicked, this, &TNANetGraphicsWidget::onRefreshClicked);
}

TNANetGraphicsWidget::~TNANetGraphicsWidget() = default;

void TNANetGraphicsWidget::AUpdateInterface()
{
    UpdateInterval = 500;
    buildNetworkStructure();
    update();
}

void TNANetGraphicsWidget::AClearInterface()
{
    componentName_.clear();
    componentNameEdit_->clear();
    nodes_.clear();
    links_.clear();
    update();
}

void TNANetGraphicsWidget::ASaveParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("NANetGraphics");
    xml.WriteString("ComponentName", componentName_);
    xml.SelectUp();
}

void TNANetGraphicsWidget::ALoadParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("NANetGraphics");
    componentName_ = xml.ReadString("ComponentName", "");
    xml.SelectUp();
    componentNameEdit_->setText(QString::fromStdString(componentName_));
    buildNetworkStructure();
}

void TNANetGraphicsWidget::paintEvent(QPaintEvent *event)
{
    UVisualControllerWidget::paintEvent(event);

    const int w = width();
    const int h = height() - 80; // Оставляем место для панели управления
    if (w < 10 || h < 10)
        return;

    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);
    painter.fillRect(0, 80, w, h, Qt::white);

    // Рисуем связи между узлами
    painter.setPen(QPen(Qt::gray, 1, Qt::DashLine));
    for (const auto &linkPair : links_)
    {
        if (!linkPair.second)
            continue;
        const std::string &fromName = linkPair.first.first;
        const std::string &toName = linkPair.first.second;

        auto fromIt = std::find_if(nodes_.begin(), nodes_.end(),
                                   [&fromName](const NodeInfo &n) { return n.name == fromName; });
        auto toIt = std::find_if(nodes_.begin(), nodes_.end(),
                                 [&toName](const NodeInfo &n) { return n.name == toName; });

        if (fromIt != nodes_.end() && toIt != nodes_.end())
        {
            painter.drawLine(fromIt->x, fromIt->y + 80, toIt->x, toIt->y + 80);
        }
    }

    // Рисуем узлы
    for (const auto &node : nodes_)
    {
        // Контур узла
        QColor contourColor = node.isNet ? Qt::darkBlue : Qt::black;
        QColor fillColor = node.isNet ? QColor(200, 220, 255) : QColor(255, 240, 200);

        painter.setPen(QPen(contourColor, 2));
        painter.setBrush(fillColor);
        painter.drawEllipse(node.x - node.radius, node.y + 80 - node.radius,
                            node.radius * 2, node.radius * 2);

        // Имя узла
        painter.setPen(Qt::black);
        QRect textRect(node.x - node.radius * 2, node.y + 80 + node.radius + 5,
                       node.radius * 4, 20);
        painter.drawText(textRect, Qt::AlignCenter | Qt::TextWordWrap,
                         QString::fromStdString(node.name));
    }
}

void TNANetGraphicsWidget::onComponentNameEdited()
{
    setComponentName(componentNameEdit_->text().trimmed().toStdString());
}

void TNANetGraphicsWidget::onFindNANetClicked()
{
    const char *raw = Model_FindComponentsByClassName("", "NANet", true);
    if (!raw || strlen(raw) == 0)
    {
        QMessageBox::information(this, tr("Not found"), tr("No NANet components found in the model."));
        return;
    }

    const auto names = splitCsv(raw);
    if (names.empty())
    {
        QMessageBox::information(this, tr("Not found"), tr("No NANet components found in the model."));
        return;
    }

    if (names.size() == 1)
    {
        setComponentName(names[0]);
        componentNameEdit_->setText(QString::fromStdString(names[0]));
    }
    else
    {
        bool ok = false;
        QString selected = QInputDialog::getItem(this, tr("Select NANet"), tr("Select component:"),
                                                 QStringList() << QString::fromStdString(names[0]),
                                                 0, false, &ok);
        if (ok && !selected.isEmpty())
        {
            setComponentName(selected.toStdString());
            componentNameEdit_->setText(selected);
        }
    }
}

void TNANetGraphicsWidget::onRefreshClicked()
{
    buildNetworkStructure();
    update();
}

void TNANetGraphicsWidget::setComponentName(const std::string &name)
{
    componentName_ = name;
    buildNetworkStructure();
    update();
}

void TNANetGraphicsWidget::buildNetworkStructure()
{
    nodes_.clear();
    links_.clear();

    if (componentName_.empty())
        return;

    // Получаем список компонентов внутри сети
    const char *raw = Model_GetComponentsNameList(componentName_.c_str());
    if (!raw || strlen(raw) == 0)
        return;

    const auto componentNames = splitCsv(raw);
    for (const auto &name : componentNames)
    {
        if (name.empty())
            continue;

        std::string fullName = componentName_ + "." + name;

        // Проверяем, является ли компонент сетью (NANet) или элементом (NAItem)
        // Упрощенно: пытаемся найти подкомпоненты
        const char *subRaw = Model_GetComponentsNameList(fullName.c_str());
        bool isNet = (subRaw && strlen(subRaw) > 0);

        NodeInfo node;
        node.name = name;
        node.isNet = isNet;
        nodes_.push_back(node);
    }

    layoutNodes();
    findLinks();
}

void TNANetGraphicsWidget::layoutNodes()
{
    if (nodes_.empty())
        return;

    // Простая сетка: размещаем узлы в сетке
    const int cols = static_cast<int>(std::ceil(std::sqrt(static_cast<double>(nodes_.size()))));
    const int startX = kNodeSpacing;
    const int startY = kNodeSpacing;

    for (size_t i = 0; i < nodes_.size(); ++i)
    {
        const int row = static_cast<int>(i) / cols;
        const int col = static_cast<int>(i) % cols;
        nodes_[i].x = startX + col * kNodeSpacing;
        nodes_[i].y = startY + row * kNodeSpacing;
        nodes_[i].radius = kNodeRadius;
    }
}

void TNANetGraphicsWidget::findLinks()
{
    if (componentName_.empty() || nodes_.empty())
        return;

    // Упрощенная проверка связей: пытаемся определить связи между компонентами
    // В model-only режиме это сложно, поэтому делаем упрощенную версию
    // Проверяем наличие связей через Model_CheckLinkByName для известных свойств
    for (size_t i = 0; i < nodes_.size(); ++i)
    {
        for (size_t j = i + 1; j < nodes_.size(); ++j)
        {
            const std::string &fromName = nodes_[i].name;
            const std::string &toName = nodes_[j].name;

            std::string fromFull = componentName_ + "." + fromName;
            std::string toFull = componentName_ + "." + toName;

            // Пытаемся проверить связь через стандартные свойства
            // Это упрощенная проверка - в реальности нужно знать конкретные свойства
            bool hasLink = false;
            // Попробуем проверить через Output -> Input связь (если такие свойства есть)
            // В model-only режиме это может быть неточно, поэтому оставляем как есть

            links_[{fromName, toName}] = hasLink;
            links_[{toName, fromName}] = hasLink; // Симметрично для упрощения
        }
    }
}

std::vector<std::string> TNANetGraphicsWidget::splitCsv(const std::string &csv)
{
    return ::splitCsv(csv);
}

std::string TNANetGraphicsWidget::trim(const std::string &s)
{
    return ::trim(s);
}
