#ifndef TNSOURCECONTROLWIDGET_H
#define TNSOURCECONTROLWIDGET_H

#include "UVisualControllerWidget.h"

#include <string>
#include <vector>

class QGroupBox;
class QLabel;
class QLineEdit;
class QListWidget;
class QPushButton;
class QSlider;

class UWatchTab;

// Qt-аналог TNSourceControlFrame (GUI/BCB).
// В BCB использовались указатели NSource* и прямой доступ к NPulseGenerator.
// Здесь работаем только через модель: ищем компоненты по имени класса и читаем/пишем параметры.
class TNSourceControlWidget : public UVisualControllerWidget
{
    Q_OBJECT

public:
    explicit TNSourceControlWidget(QWidget *parent = nullptr, RDK::UApplication *app = nullptr);
    ~TNSourceControlWidget() override;

    void AUpdateInterface() override;
    void AClearInterface() override;
    void ASaveParameters(RDK::USerStorageXML &xml) override;
    void ALoadParameters(RDK::USerStorageXML &xml) override;

private slots:
    void onFindSourcesClicked();
    void onSourceSelectionChanged();
    void onAmplitudeSliderChanged(int value);
    void onAmplitudeEdited();
    void onFrequencySliderChanged(int value);
    void onFrequencyEdited();
    void onAddWatchSeriesClicked();

private:
    std::string selectedSourceName_;
    bool updateInProgress_ = false;

    QGroupBox *sourcesGroup_;
    QListWidget *sourcesList_;
    QPushButton *findPulseGeneratorsButton_;

    QGroupBox *paramsGroup_;
    QLabel *selectedLabel_;

    QSlider *amplitudeSlider_;
    QLineEdit *amplitudeEdit_;
    QSlider *frequencySlider_;
    QLineEdit *frequencyEdit_;
    QPushButton *addWatchSeriesButton_;
    UWatchTab *watchTab_;

    void setSelectedSource(const std::string &name);
    void refreshSelectedFromModel();
    static std::vector<std::string> splitCsv(const std::string &csv);
};

#endif // TNSOURCECONTROLWIDGET_H

