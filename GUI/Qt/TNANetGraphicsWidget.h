#ifndef TNANETGRAPHICSWIDGET_H
#define TNANETGRAPHICSWIDGET_H

#include "UVisualControllerWidget.h"

#include <string>
#include <vector>
#include <map>

class QGroupBox;
class QLabel;
class QLineEdit;
class QPushButton;

// Qt-аналог NANetGraphicsFrameUnit (GUI/BCB).
// В BCB использовался NGraphics с UBitmap и UGraphics для рисования структуры NANet.
// Здесь создаем упрощенную версию на QPainter для model-only режима:
// - Получаем список компонентов через Model_GetComponentsNameList
// - Рисуем их как узлы на QPainter
// - Пытаемся определить связи между компонентами (упрощенно)
class TNANetGraphicsWidget : public UVisualControllerWidget
{
    Q_OBJECT

public:
    explicit TNANetGraphicsWidget(QWidget *parent = nullptr, RDK::UApplication *app = nullptr);
    ~TNANetGraphicsWidget() override;

    void AUpdateInterface() override;
    void AClearInterface() override;
    void ASaveParameters(RDK::USerStorageXML &xml) override;
    void ALoadParameters(RDK::USerStorageXML &xml) override;

protected:
    void paintEvent(QPaintEvent *event) override;

private slots:
    void onComponentNameEdited();
    void onFindNANetClicked();
    void onRefreshClicked();

private:
    struct NodeInfo
    {
        std::string name;
        int x = 0;
        int y = 0;
        int radius = 20;
        bool isNet = false; // true если это подсеть (NANet), false если элемент (NAItem)
    };

    std::string componentName_;
    std::vector<NodeInfo> nodes_;
    std::map<std::pair<std::string, std::string>, bool> links_; // (from, to) -> exists

    QGroupBox *networkGroup_;
    QLineEdit *componentNameEdit_;
    QPushButton *findButton_;
    QPushButton *refreshButton_;

    static constexpr int kCanvasWidth = 800;
    static constexpr int kCanvasHeight = 600;
    static constexpr int kNodeSpacing = 120;
    static constexpr int kNodeRadius = 25;

    void setComponentName(const std::string &name);
    void buildNetworkStructure();
    void layoutNodes();
    void findLinks();
    static std::vector<std::string> splitCsv(const std::string &csv);
    static std::string trim(const std::string &s);
};

#endif // TNANETGRAPHICSWIDGET_H
