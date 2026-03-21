#ifndef NNEURONTRAINERWIDGET_H
#define NNEURONTRAINERWIDGET_H

#include "UVisualControllerWidget.h"

#include <string>

class QGroupBox;
class QLabel;
class QLineEdit;

// Qt-аналог NNeuronTrainerFormUnit / NNeuronTrainerFrameUnit из GUI/BCB.
// Отображает параметры компонента NNeuronTrainer (только модель: ReadParameterValue).
class NNeuronTrainerWidget : public UVisualControllerWidget
{
    Q_OBJECT

public:
    explicit NNeuronTrainerWidget(QWidget *parent = nullptr, RDK::UApplication *app = nullptr);
    ~NNeuronTrainerWidget() override;

    void AAfterLoadProject() override;
    void AUpdateInterface() override;
    void AClearInterface() override;
    void ASaveParameters(RDK::USerStorageXML &xml) override;
    void ALoadParameters(RDK::USerStorageXML &xml) override;

private slots:
    void onTrainerNameEdited();

private:
    std::string trainerName_;

    int numInputDendrite_ = 0;
    double delay_ = 0.0;
    double spikesFrequency_ = 0.0;
    int maxDendriteLength_ = 0;
    double ltzThreshold_ = 0.0;
    bool useFixedLTZThreshold_ = false;
    bool isTraining_ = false;

    QLineEdit *trainerNameEdit_;
    QGroupBox *paramsGroup_;
    QLabel *numInputDendriteLabel_;
    QLabel *delayLabel_;
    QLabel *spikesFrequencyLabel_;
    QLabel *maxDendriteLengthLabel_;
    QLabel *ltzThresholdLabel_;
    QLabel *useFixedLTZLabel_;
    QLabel *isTrainingLabel_;

    void updateLabels();
};

#endif // NNEURONTRAINERWIDGET_H

