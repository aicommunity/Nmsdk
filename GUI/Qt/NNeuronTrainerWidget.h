#ifndef NNEURONTRAINERWIDGET_H
#define NNEURONTRAINERWIDGET_H

#include "UVisualControllerWidget.h"

// Qt-аналог NNeuronTrainerFormUnit из GUI/BCB.
// Виджет для настройки и запуска обучения нейронов.
class NNeuronTrainerWidget : public UVisualControllerWidget
{
    Q_OBJECT

public:
    explicit NNeuronTrainerWidget(QWidget *parent = nullptr, RDK::UApplication *app = nullptr);
    ~NNeuronTrainerWidget() override;

    void AUpdateInterface() override;
    void AClearInterface() override;
};

#endif // NNEURONTRAINERWIDGET_H

