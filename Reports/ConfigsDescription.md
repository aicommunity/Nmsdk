# Описание конфигурационных проектов

Данный документ содержит подробное описание всех конфигурационных проектов в `Bin/Configs`.

## Структура описания

Для каждого конфига указаны:
- Название и путь
- Назначение (на основе названия и структуры)
- Структура схемы (основные компоненты)
- Входы и выходы системы
- Особенности конфигурации

---

## !OldConfigs

### EyeRetina

**Путь:** `Bin\Configs\!OldConfigs\EyeRetina`

**Назначение:** Модель сетчатки глаза с управлением мышцами

**Основные компоненты:**
- **NEyeRetina**: EyeRetina
- **Reduce**: Reduce
- **TCaptureImageSequence**: Capture
- **VideoSimulatorSimple**: VideoSimulatorSimple

**Входы системы:**
- `Reduce.Input`
- `VideoSimulatorSimple.Input`

**Выходы системы:**
- `Capture.OutputImage`
- `Reduce.Output`
- `VideoSimulatorSimple.Output`

**Количество связей:** 3

**Связанные публикации:**
- [The Neuromorphic Model of the Human Visual System](https://link.springer.com/chapter/10.1007%2F978-3-030-60577-3_40) - Публикация 18: Korsakov, A., Bakhshiev, A.

---

### EyeRetinaMuscle

**Путь:** `Bin\Configs\!OldConfigs\EyeRetinaMuscle`

**Назначение:** Модель сетчатки глаза с управлением мышцами

**Основные компоненты:**
- **NCGenerator**: CGenerator
- **NEyeMuscle**: LeftEyeMuscle, TopEyeMuscle, RightEyeMuscle, BottomEyeMuscle
- **NEyeRetina**: EyeRetina
- **NPGenerator**: LeftAfferentNeuron.LTZone.PGenerator, LeftAfferentNeuron.PGenerator, RightAfferentNeuron.LTZone.PGenerator, RightAfferentNeuron.PGenerator, BottomAfferentNeuron.LTZone.PGenerator (и еще 5)
- **NPSimpleLTZone**: LeftAfferentNeuron.LTZone, RightAfferentNeuron.LTZone, BottomAfferentNeuron.LTZone, TopAfferentNeuron.LTZone, LTZone
- **NReceptor**: LeftAfferentNeuron.Receptor, RightAfferentNeuron.Receptor, BottomAfferentNeuron.Receptor, TopAfferentNeuron.Receptor, Receptor
- **NSimpleAfferentNeuron**: LeftAfferentNeuron, RightAfferentNeuron, BottomAfferentNeuron, TopAfferentNeuron
- **Reduce**: Reduce
- **TCaptureImageSequence**: Capture
- **VideoSimulatorSimple**: VideoSimulatorSimple

**Входы системы:**
- `BottomAfferentNeuron.LTZone.Inputs`
- `BottomAfferentNeuron.LTZone.PGenerator`
- `BottomAfferentNeuron.PGenerator`
- `BottomAfferentNeuron.Receptor.Input`
- `BottomEyeMuscle.Inputs`
- `CGenerator`
- `LTZone.PGenerator`
- `LeftAfferentNeuron.LTZone.Inputs`
- `LeftAfferentNeuron.LTZone.PGenerator`
- `LeftAfferentNeuron.PGenerator`
- ... (всего 25 входов)

**Выходы системы:**
- `BottomAfferentNeuron.LTZone.Output`
- `BottomAfferentNeuron.Receptor.Output`
- `Capture.OutputImage`
- `LeftAfferentNeuron.LTZone.Output`
- `LeftAfferentNeuron.Receptor.Output`
- `Reduce.Output`
- `RightAfferentNeuron.LTZone.Output`
- `RightAfferentNeuron.Receptor.Output`
- `TopAfferentNeuron.LTZone.Output`
- `TopAfferentNeuron.Receptor.Output`
- ... (всего 11 выходов)

**Количество связей:** 15

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев
- [The Neuromorphic Model of the Human Visual System](https://link.springer.com/chapter/10.1007%2F978-3-030-60577-3_40) - Публикация 18: Korsakov, A., Bakhshiev, A.

---

### MEM-OneNeuron3

**Путь:** `Bin\Configs\!OldConfigs\MEM-OneNeuron3`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPExcChannel**: MemNeuron.Soma1.ExcChannel, MemNeuron.Dendrite1_1.ExcChannel, MemNeuron.Dendrite1_2.ExcChannel, MemNeuron.Soma2.ExcChannel, MemNeuron.Dendrite2_1.ExcChannel (и еще 9)
- **NPGenerator**: E_Gen, E_Gen2, R_Gen, F_Gen
- **NPInhChannel**: MemNeuron.Soma1.InhChannel, MemNeuron.Dendrite1_1.InhChannel, MemNeuron.Dendrite1_2.InhChannel, MemNeuron.Soma2.InhChannel, MemNeuron.Dendrite2_1.InhChannel (и еще 9)
- **NPLTZone**: MemNeuron.LTZone, LTZone
- **NPMembrane**: MemNeuron.Soma1, MemNeuron.Dendrite1_1, MemNeuron.Dendrite1_2, MemNeuron.Soma2, MemNeuron.Dendrite2_1 (и еще 7)
- **NPNeuron**: MemNeuron
- **NPNeuronNegCGenerator**: MemNeuron.NegGenerator, NegGenerator
- **NPNeuronPosCGenerator**: MemNeuron.PosGenerator, PosGenerator
- **NPSynapse**: MemNeuron.Soma1.ExcSynapse, MemNeuron.Soma1.InhSynapse, MemNeuron.Dendrite1_1.ExcSynapse1, MemNeuron.Dendrite1_1.InhSynapse1, MemNeuron.Dendrite1_1.InhSynapse2 (и еще 35)

**Входы системы:**
- `E_Gen`
- `E_Gen2`
- `F_Gen`
- `MemNeuron.Dendrite1_1.ExcChannel.ChannelInputs`
- `MemNeuron.Dendrite1_1.ExcChannel.SynapticInputs`
- `MemNeuron.Dendrite1_1.InhChannel.ChannelInputs`
- `MemNeuron.Dendrite1_1.InhChannel.SynapticInputs`
- `MemNeuron.Dendrite1_1.InhSynapse1.Input`
- `MemNeuron.Dendrite1_1.InhSynapse2.Input`
- `MemNeuron.Dendrite1_2.ExcChannel.ChannelInputs`
- ... (всего 40 входов)

**Выходы системы:**
- `E_Gen.Output`
- `E_Gen2.Output`
- `F_Gen.Output`
- `MemNeuron.Dendrite1_1.ExcChannel.Output`
- `MemNeuron.Dendrite1_1.ExcSynapse1.Output`
- `MemNeuron.Dendrite1_1.InhChannel.Output`
- `MemNeuron.Dendrite1_1.InhSynapse1.Output`
- `MemNeuron.Dendrite1_1.InhSynapse2.Output`
- `MemNeuron.Dendrite1_2.ExcChannel.Output`
- `MemNeuron.Dendrite1_2.ExcSynapse1.Output`
- ... (всего 33 выходов)

**Количество связей:** 38

---

### MEM-SimpleMemory2

**Путь:** `Bin\Configs\!OldConfigs\MEM-SimpleMemory2`

**Назначение:** Модель памяти для навигации в лабиринте

**Основные компоненты:**
- **NPExcChannel**: MemNeuron.Soma1.ExcChannel, MemNeuron.Dendrite1_1.ExcChannel, MemNeuron.Dendrite1_2.ExcChannel, MemNeuron.Soma2.ExcChannel, MemNeuron.Dendrite2_1.ExcChannel (и еще 23)
- **NPGenerator**: E_Gen, E_Gen2, E_Gen3, R_Gen, R_Gen2 (и еще 1)
- **NPInhChannel**: MemNeuron.Soma1.InhChannel, MemNeuron.Dendrite1_1.InhChannel, MemNeuron.Dendrite1_2.InhChannel, MemNeuron.Soma2.InhChannel, MemNeuron.Dendrite2_1.InhChannel (и еще 23)
- **NPLTZone**: MemNeuron.LTZone, MemNeuron2.LTZone, MemNeuron3.LTZone, LTZone
- **NPMembrane**: MemNeuron.Soma1, MemNeuron.Dendrite1_1, MemNeuron.Dendrite1_2, MemNeuron.Soma2, MemNeuron.Dendrite2_1 (и еще 19)
- **NPNeuron**: MemNeuron, MemNeuron2, MemNeuron3
- **NPNeuronNegCGenerator**: MemNeuron.NegGenerator, MemNeuron2.NegGenerator, MemNeuron3.NegGenerator, NegGenerator
- **NPNeuronPosCGenerator**: MemNeuron.PosGenerator, MemNeuron2.PosGenerator, MemNeuron3.PosGenerator, PosGenerator
- **NPSynapse**: MemNeuron.Soma1.ExcSynapse, MemNeuron.Soma1.InhSynapse, MemNeuron.Dendrite1_1.ExcSynapse1, MemNeuron.Dendrite1_1.InhSynapse1, MemNeuron.Dendrite1_1.InhSynapse2 (и еще 73)

**Входы системы:**
- `E_Gen`
- `E_Gen2`
- `E_Gen3`
- `MemNeuron.Dendrite1_1.ExcChannel.ChannelInputs`
- `MemNeuron.Dendrite1_1.ExcChannel.SynapticInputs`
- `MemNeuron.Dendrite1_1.InhChannel.ChannelInputs`
- `MemNeuron.Dendrite1_1.InhChannel.SynapticInputs`
- `MemNeuron.Dendrite1_1.InhSynapse1.Input`
- `MemNeuron.Dendrite1_1.InhSynapse2.Input`
- `MemNeuron.Dendrite1_2.ExcChannel.ChannelInputs`
- ... (всего 109 входов)

**Выходы системы:**
- `E_Gen.Output`
- `E_Gen2.Output`
- `E_Gen3.Output`
- `MemNeuron.Dendrite1_1.ExcChannel.Output`
- `MemNeuron.Dendrite1_1.ExcSynapse1.Output`
- `MemNeuron.Dendrite1_1.InhChannel.Output`
- `MemNeuron.Dendrite1_1.InhSynapse1.Output`
- `MemNeuron.Dendrite1_1.InhSynapse2.Output`
- `MemNeuron.Dendrite1_2.ExcChannel.Output`
- `MemNeuron.Dendrite1_2.ExcSynapse1.Output`
- ... (всего 93 выходов)

**Количество связей:** 110

**Связанные публикации:**
- [Исследование метода запоминания пространственных конфигураций робототехнической системы](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 7: Бахшиев А.В., Гунделах Ф.В.

---

### NReceptor

**Путь:** `Bin\Configs\!OldConfigs\NReceptor`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NCGenerator**: CGenerator
- **NReceptor**: Receptor, Receptor2, Receptor3, Receptor4, Receptor5

**Входы системы:**
- `CGenerator`
- `Receptor.Input`
- `Receptor2.Input`
- `Receptor3.Input`
- `Receptor4.Input`
- `Receptor5.Input`

**Выходы системы:**
- `CGenerator.Output`

**Количество связей:** 5

---

### NeuronComparation

**Путь:** `Bin\Configs\!OldConfigs\NeuronComparation`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPExcChannel**: PNeuronGenOpt.Soma1.ExcChannel, PNeuronGenOpt.ExcChannel, PNeuronGen.Soma1.ExcChannel, PNeuronGen.ExcChannel, PNeuronOld.Soma1.ExcChannel (и еще 3)
- **NPExcChannelBio**: PNeuronBio.Soma1.ExcChannel, PNeuronBio.ExcChannel
- **NPGenerator**: PGenerator
- **NPInhChannel**: PNeuronGenOpt.Soma1.InhChannel, PNeuronGenOpt.InhChannel, PNeuronGen.Soma1.InhChannel, PNeuronGen.InhChannel, PNeuronOld.Soma1.InhChannel (и еще 3)
- **NPInhChannelBio**: PNeuronBio.Soma1.InhChannel, PNeuronBio.InhChannel
- **NPLTZone**: PNeuronOld.LTZone, LTZone
- **NPMembrane**: PNeuronGenOpt.Soma1, PNeuronGen.Soma1, PNeuronOld.Soma1, Soma1
- **NPMembraneBio**: PNeuronBio.Soma1
- **NPNeuronNegCGenerator**: PNeuronGenOpt.NegGenerator, PNeuronGen.NegGenerator, PNeuronOld.NegGenerator, NegGenerator
- **NPNeuronNegCGeneratorBio**: PNeuronBio.NegGenerator
- **NPNeuronPosCGenerator**: PNeuronGenOpt.PosGenerator, PNeuronGen.PosGenerator, PNeuronOld.PosGenerator, PosGenerator
- **NPNeuronPosCGeneratorBio**: PNeuronBio.PosGenerator
- **NPSynapse**: PNeuronGenOpt.Soma1.ExcSynapse1, PNeuronGenOpt.Soma1.InhSynapse1, PNeuronGenOpt.ExcSynapse1, PNeuronGenOpt.InhSynapse1, PNeuronGen.Soma1.ExcSynapse1 (и еще 11)
- **NPSynapseBio**: PNeuronBio.Soma1.ExcSynapse1, PNeuronBio.Soma1.InhSynapse1, PNeuronBio.ExcSynapse1, PNeuronBio.InhSynapse1
- **NPulseLTZoneThreshold**: PNeuronGenOpt.LTZone, PNeuronGen.LTZone
- **NPulseLTZoneThresholdBio**: PNeuronBio.LTZone
- **NSPNeuron**: PNeuronOld
- **NSPNeuronBio**: PNeuronBio
- **NSPNeuronGen**: PNeuronGenOpt, PNeuronGen

**Входы системы:**
- `NegGenerator`
- `PGenerator`
- `PNeuronBio.LTZone.Inputs`
- `PNeuronBio.NegGenerator`
- `PNeuronBio.PosGenerator`
- `PNeuronBio.Soma1.ExcChannel.ChannelInputs`
- `PNeuronBio.Soma1.ExcChannel.SynapticInputs`
- `PNeuronBio.Soma1.ExcSynapse1.Input`
- `PNeuronBio.Soma1.InhChannel.ChannelInputs`
- `PNeuronBio.Soma1.InhChannel.SynapticInputs`
- ... (всего 39 входов)

**Выходы системы:**
- `PGenerator.Output`
- `PNeuronBio.LTZone.Output`
- `PNeuronBio.NegGenerator.Output`
- `PNeuronBio.PosGenerator.Output`
- `PNeuronBio.Soma1.ExcChannel.Output`
- `PNeuronBio.Soma1.ExcSynapse1.Output`
- `PNeuronBio.Soma1.InhChannel.Output`
- `PNeuronBio.Soma1.InhSynapse1.Output`
- `PNeuronGen.LTZone.Output`
- `PNeuronGen.NegGenerator.Output`
- ... (всего 29 выходов)

**Количество связей:** 32

---

### NewCodeTest

**Путь:** `Bin\Configs\!OldConfigs\NewCodeTest`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NNeuronTrainer**: NeuronTrainer
- **NPExcChannelBio**: NeuronTrainer.Neuron.Soma1.ExcChannel, NeuronTrainer.Neuron.Dendrite1_1.ExcChannel, NeuronTrainer.Neuron.Soma2.ExcChannel, NeuronTrainer.Neuron.Dendrite2_1.ExcChannel, NeuronTrainer.Neuron.Dendrite1_2.ExcChannel (и еще 23)
- **NPInhChannelBio**: NeuronTrainer.Neuron.Soma1.InhChannel, NeuronTrainer.Neuron.Dendrite1_1.InhChannel, NeuronTrainer.Neuron.Soma2.InhChannel, NeuronTrainer.Neuron.Dendrite2_1.InhChannel, NeuronTrainer.Neuron.Dendrite1_2.InhChannel (и еще 23)
- **NPMembraneBio**: NeuronTrainer.Neuron.Soma1, NeuronTrainer.Neuron.Dendrite1_1, NeuronTrainer.Neuron.Soma2, NeuronTrainer.Neuron.Dendrite2_1, NeuronTrainer.Neuron.Dendrite1_2 (и еще 19)
- **NPNeuronNegCGenerator**: NeuronTrainer.Neuron.NegGenerator, NeuronTrainer.NegGenerator, Neuron.NegGenerator, NegGenerator
- **NPNeuronPosCGenerator**: NeuronTrainer.Neuron.PosGenerator, NeuronTrainer.PosGenerator, Neuron.PosGenerator, PosGenerator
- **NPSynapseBio**: NeuronTrainer.Neuron.Soma1.ExcSynapse1, NeuronTrainer.Neuron.Soma1.InhSynapse1, NeuronTrainer.Neuron.Dendrite1_1.ExcSynapse1, NeuronTrainer.Neuron.Dendrite1_1.InhSynapse1, NeuronTrainer.Neuron.Soma2.ExcSynapse1 (и еще 91)
- **NPulseGeneratorTransit**: NeuronTrainer.Source1, NeuronTrainer.Source2, Source1, Source2
- **NPulseLTZoneThreshold**: NeuronTrainer.Neuron.LTZone, NeuronTrainer.LTZone, Neuron.LTZone, LTZone
- **NSPNeuronGen**: NeuronTrainer.Neuron, Neuron

**Входы системы:**
- `NegGenerator`
- `Neuron.NegGenerator`
- `Neuron.PosGenerator`
- `NeuronTrainer.NegGenerator`
- `NeuronTrainer.Neuron.Dendrite1_1.ExcChannel.ChannelInputs`
- `NeuronTrainer.Neuron.Dendrite1_1.ExcChannel.SynapticInputs`
- `NeuronTrainer.Neuron.Dendrite1_1.InhChannel.ChannelInputs`
- `NeuronTrainer.Neuron.Dendrite1_1.InhChannel.SynapticInputs`
- `NeuronTrainer.Neuron.Dendrite1_2.ExcChannel.ChannelInputs`
- `NeuronTrainer.Neuron.Dendrite1_2.ExcChannel.SynapticInputs`
- ... (всего 46 входов)

**Выходы системы:**
- `.Output`
- `NeuronTrainer.Neuron.Dendrite1_1.ExcChannel.Output`
- `NeuronTrainer.Neuron.Dendrite1_1.ExcSynapse1.Output`
- `NeuronTrainer.Neuron.Dendrite1_1.InhChannel.Output`
- `NeuronTrainer.Neuron.Dendrite1_1.InhSynapse1.Output`
- `NeuronTrainer.Neuron.Dendrite1_2.ExcChannel.Output`
- `NeuronTrainer.Neuron.Dendrite1_2.ExcSynapse1.Output`
- `NeuronTrainer.Neuron.Dendrite1_2.InhChannel.Output`
- `NeuronTrainer.Neuron.Dendrite1_2.InhSynapse1.Output`
- `NeuronTrainer.Neuron.Dendrite1_3.ExcChannel.Output`
- ... (всего 35 выходов)

**Количество связей:** 43

---

### NewCodeTest1

**Путь:** `Bin\Configs\!OldConfigs\NewCodeTest1`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NNeuronTrainer**: NeuronTrainer
- **NPExcChannelBio**: NeuronTrainer.Neuron.Soma1.ExcChannel, NeuronTrainer.Neuron.Dendrite1_1.ExcChannel, NeuronTrainer.Neuron.Soma2.ExcChannel, NeuronTrainer.Neuron.Dendrite2_1.ExcChannel, NeuronTrainer.Neuron.Soma3.ExcChannel (и еще 103)
- **NPInhChannelBio**: NeuronTrainer.Neuron.Soma1.InhChannel, NeuronTrainer.Neuron.Dendrite1_1.InhChannel, NeuronTrainer.Neuron.Soma2.InhChannel, NeuronTrainer.Neuron.Dendrite2_1.InhChannel, NeuronTrainer.Neuron.Soma3.InhChannel (и еще 103)
- **NPMembraneBio**: NeuronTrainer.Neuron.Soma1, NeuronTrainer.Neuron.Dendrite1_1, NeuronTrainer.Neuron.Soma2, NeuronTrainer.Neuron.Dendrite2_1, NeuronTrainer.Neuron.Soma3 (и еще 99)
- **NPNeuronNegCGenerator**: NeuronTrainer.Neuron.NegGenerator, NeuronTrainer.NegGenerator, Neuron.NegGenerator, NegGenerator
- **NPNeuronPosCGenerator**: NeuronTrainer.Neuron.PosGenerator, NeuronTrainer.PosGenerator, Neuron.PosGenerator, PosGenerator
- **NPSynapseBio**: NeuronTrainer.Neuron.Soma1.ExcSynapse1, NeuronTrainer.Neuron.Soma1.InhSynapse1, NeuronTrainer.Neuron.Dendrite1_1.ExcSynapse1, NeuronTrainer.Neuron.Dendrite1_1.InhSynapse1, NeuronTrainer.Neuron.Soma2.ExcSynapse1 (и еще 439)
- **NPulseGeneratorTransit**: NeuronTrainer.Source1, NeuronTrainer.Source2, NeuronTrainer.Source3, NeuronTrainer.Source4, Source1 (и еще 3)
- **NPulseLTZoneThreshold**: NeuronTrainer.Neuron.LTZone, NeuronTrainer.LTZone, Neuron.LTZone, LTZone
- **NSPNeuronGen**: NeuronTrainer.Neuron, Neuron

**Входы системы:**
- `NegGenerator`
- `Neuron.NegGenerator`
- `Neuron.PosGenerator`
- `NeuronTrainer.NegGenerator`
- `NeuronTrainer.Neuron.Dendrite1_1.ExcChannel.ChannelInputs`
- `NeuronTrainer.Neuron.Dendrite1_1.ExcChannel.SynapticInputs`
- `NeuronTrainer.Neuron.Dendrite1_1.InhChannel.ChannelInputs`
- `NeuronTrainer.Neuron.Dendrite1_1.InhChannel.SynapticInputs`
- `NeuronTrainer.Neuron.Dendrite1_10.ExcChannel.ChannelInputs`
- `NeuronTrainer.Neuron.Dendrite1_10.ExcChannel.SynapticInputs`
- ... (всего 168 входов)

**Выходы системы:**
- `.Output`
- `NeuronTrainer.Neuron.Dendrite1_1.ExcChannel.Output`
- `NeuronTrainer.Neuron.Dendrite1_1.ExcSynapse1.Output`
- `NeuronTrainer.Neuron.Dendrite1_1.InhChannel.Output`
- `NeuronTrainer.Neuron.Dendrite1_1.InhSynapse1.Output`
- `NeuronTrainer.Neuron.Dendrite1_10.ExcChannel.Output`
- `NeuronTrainer.Neuron.Dendrite1_10.ExcSynapse1.Output`
- `NeuronTrainer.Neuron.Dendrite1_10.ExcSynapse10.Output`
- `NeuronTrainer.Neuron.Dendrite1_10.ExcSynapse11.Output`
- `NeuronTrainer.Neuron.Dendrite1_10.ExcSynapse12.Output`
- ... (всего 151 выходов)

**Количество связей:** 199

---

### OrNeuron_4generators

**Путь:** `Bin\Configs\!OldConfigs\OrNeuron_4generators`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NClassifier**: Classifier
- **NNeuronTrainer**: Classifier.NeuronTrainer1_1, Classifier.NeuronTrainer1_2, Classifier.NeuronTrainer1_3, Classifier.NeuronTrainer1_4, NeuronTrainer1_1 (и еще 3)
- **NPExcChannelBio**: Classifier.NeuronTrainer1_1.Neuron.Soma1.ExcChannel, Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.ExcChannel, Classifier.NeuronTrainer1_1.Neuron.Soma2.ExcChannel, Classifier.NeuronTrainer1_1.Neuron.Dendrite2_1.ExcChannel, Classifier.NeuronTrainer1_1.Neuron.Soma3.ExcChannel (и еще 1231)
- **NPInhChannelBio**: Classifier.NeuronTrainer1_1.Neuron.Soma1.InhChannel, Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.InhChannel, Classifier.NeuronTrainer1_1.Neuron.Soma2.InhChannel, Classifier.NeuronTrainer1_1.Neuron.Dendrite2_1.InhChannel, Classifier.NeuronTrainer1_1.Neuron.Soma3.InhChannel (и еще 1231)
- **NPMembraneBio**: Classifier.NeuronTrainer1_1.Neuron.Soma1, Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1, Classifier.NeuronTrainer1_1.Neuron.Soma2, Classifier.NeuronTrainer1_1.Neuron.Dendrite2_1, Classifier.NeuronTrainer1_1.Neuron.Soma3 (и еще 1209)
- **NPNeuronNegCGenerator**: Classifier.NeuronTrainer1_1.Neuron.NegGenerator, Classifier.NeuronTrainer1_1.NegGenerator, Classifier.OrNeuron1.NegGenerator, Classifier.NeuronTrainer1_2.Neuron.NegGenerator, Classifier.NeuronTrainer1_2.NegGenerator (и еще 17)
- **NPNeuronPosCGenerator**: Classifier.NeuronTrainer1_1.Neuron.PosGenerator, Classifier.NeuronTrainer1_1.PosGenerator, Classifier.OrNeuron1.PosGenerator, Classifier.NeuronTrainer1_2.Neuron.PosGenerator, Classifier.NeuronTrainer1_2.PosGenerator (и еще 17)
- **NPSynapse**: Classifier.NeuronTrainer1_1.Neuron.Dendrite3_9.ExcSynapse2, Classifier.NeuronTrainer1_1.Neuron.Dendrite3_9.ExcSynapse3, Classifier.NeuronTrainer1_1.Neuron.Dendrite3_9.ExcSynapse4, Classifier.NeuronTrainer1_1.Neuron.Dendrite3_9.ExcSynapse5, Classifier.NeuronTrainer1_1.Neuron.Dendrite3_9.ExcSynapse6 (и еще 1719)
- **NPSynapseBio**: Classifier.NeuronTrainer1_1.Neuron.Soma1.ExcSynapse1, Classifier.NeuronTrainer1_1.Neuron.Soma1.InhSynapse1, Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.ExcSynapse1, Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.InhSynapse1, Classifier.NeuronTrainer1_1.Neuron.Soma2.ExcSynapse1 (и еще 2485)
- **NPulseGeneratorTransit**: Classifier.NeuronTrainer1_1.Source1, Classifier.NeuronTrainer1_1.Source2, Classifier.NeuronTrainer1_1.Source3, Classifier.NeuronTrainer1_1.Source4, Classifier.NeuronTrainer1_1.Source5 (и еще 49)
- **NPulseLTZoneThreshold**: Classifier.NeuronTrainer1_1.Neuron.LTZone, Classifier.NeuronTrainer1_1.LTZone, Classifier.OrNeuron1.LTZone, Classifier.NeuronTrainer1_2.Neuron.LTZone, Classifier.NeuronTrainer1_2.LTZone (и еще 17)
- **NSPNeuronGen**: Classifier.NeuronTrainer1_1.Neuron, Classifier.OrNeuron1, Classifier.NeuronTrainer1_2.Neuron, Classifier.NeuronTrainer1_3.Neuron, Classifier.NeuronTrainer1_4.Neuron (и еще 7)

**Входы системы:**
- `Classifier.NegGenerator`
- `Classifier.Neuron.NegGenerator`
- `Classifier.Neuron.PosGenerator`
- `Classifier.NeuronTrainer1_1.NegGenerator`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.ExcChannel.ChannelInputs`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.ExcChannel.SynapticInputs`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.InhChannel.ChannelInputs`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.InhChannel.SynapticInputs`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_10.ExcChannel.ChannelInputs`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_10.ExcChannel.SynapticInputs`
- ... (всего 1295 входов)

**Выходы системы:**
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.ExcChannel.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.ExcSynapse1.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.InhChannel.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.InhSynapse1.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_10.ExcChannel.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_10.ExcSynapse1.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_10.InhChannel.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_10.InhSynapse1.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_11.ExcChannel.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_11.ExcSynapse1.Output`
- ... (всего 1170 выходов)

**Количество связей:** 1428

---

### PCATest

**Путь:** `Bin\Configs\!OldConfigs\PCATest`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **UCRPrincipalComponentAnalysis**: CRPrincipalComponentAnalysis
- **UMatrixSourceTimeSeries**: MatrixSourceTimeSeries

**Количество связей:** 2

---

### RotCamSim

**Путь:** `Bin\Configs\!OldConfigs\RotCamSim`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NCGenerator**: CGenerator
- **NEyeMuscle**: LeftEyeMuscle, TopEyeMuscle, RightEyeMuscle, BottomEyeMuscle
- **NEyeRetina**: EyeRetina
- **NPGenerator**: LeftAfferentNeuron.LTZone.PGenerator, LeftAfferentNeuron.PGenerator, RightAfferentNeuron.LTZone.PGenerator, RightAfferentNeuron.PGenerator, BottomAfferentNeuron.LTZone.PGenerator (и еще 5)
- **NPSimpleLTZone**: LeftAfferentNeuron.LTZone, RightAfferentNeuron.LTZone, BottomAfferentNeuron.LTZone, TopAfferentNeuron.LTZone, LTZone
- **NReceptor**: LeftAfferentNeuron.Receptor, RightAfferentNeuron.Receptor, BottomAfferentNeuron.Receptor, TopAfferentNeuron.Receptor, Receptor
- **NSimpleAfferentNeuron**: LeftAfferentNeuron, RightAfferentNeuron, BottomAfferentNeuron, TopAfferentNeuron
- **Reduce**: Reduce
- **RotCameraSimulator**: RotCameraSimulator
- **TCaptureImageSequence**: Capture

**Входы системы:**
- `BottomAfferentNeuron.LTZone.Inputs`
- `BottomAfferentNeuron.LTZone.PGenerator`
- `BottomAfferentNeuron.PGenerator`
- `BottomAfferentNeuron.Receptor.Input`
- `BottomEyeMuscle.Inputs`
- `CGenerator`
- `LTZone.PGenerator`
- `LeftAfferentNeuron.LTZone.Inputs`
- `LeftAfferentNeuron.LTZone.PGenerator`
- `LeftAfferentNeuron.PGenerator`
- ... (всего 25 входов)

**Выходы системы:**
- `BottomAfferentNeuron.LTZone.Output`
- `BottomAfferentNeuron.Receptor.Output`
- `BottomEyeMuscle.OutputLength`
- `Capture.OutputImage`
- `LeftAfferentNeuron.LTZone.Output`
- `LeftAfferentNeuron.Receptor.Output`
- `LeftEyeMuscle.OutputLength`
- `Reduce.Output`
- `RightAfferentNeuron.LTZone.Output`
- `RightAfferentNeuron.Receptor.Output`
- ... (всего 15 выходов)

**Количество связей:** 19

---

### STDP-Simple-01

**Путь:** `Bin\Configs\!OldConfigs\STDP-Simple-01`

**Назначение:** Простая тестовая модель с генератором сигналов

**Основные компоненты:**
- **NPGenerator**: PresynActivity, PossynActivity
- **NSynapseStdp**: SynapseStdp

**Входы системы:**
- `PossynActivity`
- `PresynActivity`
- `SynapseStdp.Input`
- `SynapseStdp.PsActivityInput`

**Выходы системы:**
- `PossynActivity.Output`
- `PresynActivity.Output`

**Количество связей:** 2

---

### SpikeANPA1+2

**Путь:** `Bin\Configs\!OldConfigs\SpikeANPA1+2`

**Назначение:** Модель спайковой нейронной сети

**Основные компоненты:**
- **NNeuronTrainer**: SpikeClassifier.NeuronTrainer1, SpikeClassifier.NeuronTrainer2, SpikeClassifier.NeuronTrainer3, NeuronTrainer1, NeuronTrainer2 (и еще 1)
- **NPExcChannelBio**: SpikeClassifier.NeuronTrainer1.Neuron.Soma1.ExcChannel, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.ExcChannel, SpikeClassifier.NeuronTrainer1.Neuron.Soma2.ExcChannel, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite2_1.ExcChannel, SpikeClassifier.NeuronTrainer1.Neuron.Soma3.ExcChannel (и еще 451)
- **NPInhChannelBio**: SpikeClassifier.NeuronTrainer1.Neuron.Soma1.InhChannel, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.InhChannel, SpikeClassifier.NeuronTrainer1.Neuron.Soma2.InhChannel, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite2_1.InhChannel, SpikeClassifier.NeuronTrainer1.Neuron.Soma3.InhChannel (и еще 451)
- **NPMembraneBio**: SpikeClassifier.NeuronTrainer1.Neuron.Soma1, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1, SpikeClassifier.NeuronTrainer1.Neuron.Soma2, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite2_1, SpikeClassifier.NeuronTrainer1.Neuron.Soma3 (и еще 435)
- **NPNeuronNegCGenerator**: SpikeClassifier.NeuronTrainer1.Neuron.NegGenerator, SpikeClassifier.NeuronTrainer1.NegGenerator, SpikeClassifier.NeuronTrainer2.Neuron.NegGenerator, SpikeClassifier.NeuronTrainer2.NegGenerator, SpikeClassifier.NeuronTrainer3.Neuron.NegGenerator (и еще 11)
- **NPNeuronPosCGenerator**: SpikeClassifier.NeuronTrainer1.Neuron.PosGenerator, SpikeClassifier.NeuronTrainer1.PosGenerator, SpikeClassifier.NeuronTrainer2.Neuron.PosGenerator, SpikeClassifier.NeuronTrainer2.PosGenerator, SpikeClassifier.NeuronTrainer3.Neuron.PosGenerator (и еще 11)
- **NPSynapseBio**: SpikeClassifier.NeuronTrainer1.Neuron.Soma1.ExcSynapse1, SpikeClassifier.NeuronTrainer1.Neuron.Soma1.InhSynapse1, SpikeClassifier.NeuronTrainer1.Neuron.Soma1.InhSynapse2, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.ExcSynapse1, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.InhSynapse1 (и еще 2279)
- **NPulseGeneratorTransit**: SpikeClassifier.NeuronTrainer1.Source1, SpikeClassifier.NeuronTrainer1.Source2, SpikeClassifier.NeuronTrainer1.Source3, SpikeClassifier.Source1, SpikeClassifier.NeuronTrainer2.Source1 (и еще 19)
- **NPulseLTZoneThreshold**: SpikeClassifier.NeuronTrainer1.Neuron.LTZone, SpikeClassifier.NeuronTrainer1.LTZone, SpikeClassifier.NeuronTrainer2.Neuron.LTZone, SpikeClassifier.NeuronTrainer2.LTZone, SpikeClassifier.NeuronTrainer3.Neuron.LTZone (и еще 11)
- **NSPNeuronGen**: SpikeClassifier.NeuronTrainer1.Neuron, SpikeClassifier.NeuronTrainer2.Neuron, SpikeClassifier.NeuronTrainer3.Neuron, SpikeClassifier.Neuron, NeuronTrainer1.Neuron (и еще 3)
- **NSpikeClassifier**: SpikeClassifier

**Входы системы:**
- `NegGenerator`
- `Neuron.NegGenerator`
- `Neuron.PosGenerator`
- `NeuronTrainer1.NegGenerator`
- `NeuronTrainer1.Neuron.NegGenerator`
- `NeuronTrainer1.Neuron.PosGenerator`
- `NeuronTrainer1.PosGenerator`
- `NeuronTrainer1.Source1`
- `NeuronTrainer1.Source2`
- `NeuronTrainer1.Source3`
- ... (всего 522 входов)

**Выходы системы:**
- `.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.ExcChannel.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.ExcSynapse1.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.InhChannel.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.InhSynapse1.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_2.ExcChannel.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_2.ExcSynapse1.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_2.InhChannel.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_2.InhSynapse1.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_3.ExcChannel.Output`
- ... (всего 449 выходов)

**Количество связей:** 601

---

### SpikeANPA3

**Путь:** `Bin\Configs\!OldConfigs\SpikeANPA3`

**Назначение:** Модель спайковой нейронной сети

**Основные компоненты:**
- **NNeuronTrainer**: SpikeClassifier.NeuronTrainer1, SpikeClassifier.NeuronTrainer2, SpikeClassifier.NeuronTrainer3, NeuronTrainer1, NeuronTrainer2 (и еще 1)
- **NPExcChannelBio**: SpikeClassifier.NeuronTrainer1.Neuron.Soma1.ExcChannel, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.ExcChannel, SpikeClassifier.NeuronTrainer1.Neuron.Soma2.ExcChannel, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite2_1.ExcChannel, SpikeClassifier.NeuronTrainer1.Neuron.Soma3.ExcChannel (и еще 451)
- **NPInhChannelBio**: SpikeClassifier.NeuronTrainer1.Neuron.Soma1.InhChannel, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.InhChannel, SpikeClassifier.NeuronTrainer1.Neuron.Soma2.InhChannel, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite2_1.InhChannel, SpikeClassifier.NeuronTrainer1.Neuron.Soma3.InhChannel (и еще 451)
- **NPMembraneBio**: SpikeClassifier.NeuronTrainer1.Neuron.Soma1, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1, SpikeClassifier.NeuronTrainer1.Neuron.Soma2, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite2_1, SpikeClassifier.NeuronTrainer1.Neuron.Soma3 (и еще 435)
- **NPNeuronNegCGenerator**: SpikeClassifier.NeuronTrainer1.Neuron.NegGenerator, SpikeClassifier.NeuronTrainer1.NegGenerator, SpikeClassifier.NeuronTrainer2.Neuron.NegGenerator, SpikeClassifier.NeuronTrainer2.NegGenerator, SpikeClassifier.NeuronTrainer3.Neuron.NegGenerator (и еще 11)
- **NPNeuronPosCGenerator**: SpikeClassifier.NeuronTrainer1.Neuron.PosGenerator, SpikeClassifier.NeuronTrainer1.PosGenerator, SpikeClassifier.NeuronTrainer2.Neuron.PosGenerator, SpikeClassifier.NeuronTrainer2.PosGenerator, SpikeClassifier.NeuronTrainer3.Neuron.PosGenerator (и еще 11)
- **NPSynapseBio**: SpikeClassifier.NeuronTrainer1.Neuron.Soma1.ExcSynapse1, SpikeClassifier.NeuronTrainer1.Neuron.Soma1.InhSynapse1, SpikeClassifier.NeuronTrainer1.Neuron.Soma1.InhSynapse2, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.ExcSynapse1, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.InhSynapse1 (и еще 2279)
- **NPulseGeneratorTransit**: SpikeClassifier.NeuronTrainer1.Source1, SpikeClassifier.NeuronTrainer1.Source2, SpikeClassifier.NeuronTrainer1.Source3, SpikeClassifier.Source1, SpikeClassifier.NeuronTrainer2.Source1 (и еще 19)
- **NPulseLTZoneThreshold**: SpikeClassifier.NeuronTrainer1.Neuron.LTZone, SpikeClassifier.NeuronTrainer1.LTZone, SpikeClassifier.NeuronTrainer2.Neuron.LTZone, SpikeClassifier.NeuronTrainer2.LTZone, SpikeClassifier.NeuronTrainer3.Neuron.LTZone (и еще 11)
- **NSPNeuronGen**: SpikeClassifier.NeuronTrainer1.Neuron, SpikeClassifier.NeuronTrainer2.Neuron, SpikeClassifier.NeuronTrainer3.Neuron, SpikeClassifier.Neuron, NeuronTrainer1.Neuron (и еще 3)
- **NSpikeClassifier**: SpikeClassifier

**Входы системы:**
- `NegGenerator`
- `Neuron.NegGenerator`
- `Neuron.PosGenerator`
- `NeuronTrainer1.NegGenerator`
- `NeuronTrainer1.Neuron.NegGenerator`
- `NeuronTrainer1.Neuron.PosGenerator`
- `NeuronTrainer1.PosGenerator`
- `NeuronTrainer1.Source1`
- `NeuronTrainer1.Source2`
- `NeuronTrainer1.Source3`
- ... (всего 522 входов)

**Выходы системы:**
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.ExcChannel.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.ExcSynapse1.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.InhChannel.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.InhSynapse1.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_2.ExcChannel.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_2.ExcSynapse1.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_2.InhChannel.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_2.InhSynapse1.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_3.ExcChannel.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_3.ExcSynapse1.Output`
- ... (всего 448 выходов)

**Количество связей:** 600

---

### SpikeAnsTrainer

**Путь:** `Bin\Configs\!OldConfigs\SpikeAnsTrainer`

**Назначение:** Модель спайковой нейронной сети

**Основные компоненты:**
- **NNeuronTrainer**: SpikeClassifier1.NeuronTrainer1, SpikeClassifier1.NeuronTrainer2, SpikeClassifier1.NeuronTrainer3, NeuronTrainer, NeuronTrainer2 (и еще 8)
- **NPExcChannel**: SpikeClassifier1.NeuronTrainer1.Neuron.Soma1.ExcChannel, SpikeClassifier1.NeuronTrainer1.Neuron.Dendrite1_1.ExcChannel, SpikeClassifier1.NeuronTrainer1.Neuron.Soma2.ExcChannel, SpikeClassifier1.NeuronTrainer1.Neuron.Dendrite2_1.ExcChannel, SpikeClassifier1.NeuronTrainer1.Neuron.Soma3.ExcChannel (и еще 1353)
- **NPInhChannel**: SpikeClassifier1.NeuronTrainer1.Neuron.Soma1.InhChannel, SpikeClassifier1.NeuronTrainer1.Neuron.Dendrite1_1.InhChannel, SpikeClassifier1.NeuronTrainer1.Neuron.Soma2.InhChannel, SpikeClassifier1.NeuronTrainer1.Neuron.Dendrite2_1.InhChannel, SpikeClassifier1.NeuronTrainer1.Neuron.Soma3.InhChannel (и еще 1353)
- **NPLTZone**: SpikeClassifier1.NeuronTrainer1.Neuron.LTZone, SpikeClassifier1.NeuronTrainer1.LTZone, SpikeClassifier1.NeuronTrainer2.Neuron.LTZone, SpikeClassifier1.NeuronTrainer2.LTZone, SpikeClassifier1.NeuronTrainer3.Neuron.LTZone (и еще 29)
- **NPMembrane**: SpikeClassifier1.NeuronTrainer1.Neuron.Soma1, SpikeClassifier1.NeuronTrainer1.Neuron.Dendrite1_1, SpikeClassifier1.NeuronTrainer1.Neuron.Soma2, SpikeClassifier1.NeuronTrainer1.Neuron.Dendrite2_1, SpikeClassifier1.NeuronTrainer1.Neuron.Soma3 (и еще 1319)
- **NPNeuronNegCGenerator**: SpikeClassifier1.NeuronTrainer1.Neuron.NegGenerator, SpikeClassifier1.NeuronTrainer1.NegGenerator, SpikeClassifier1.NeuronTrainer2.Neuron.NegGenerator, SpikeClassifier1.NeuronTrainer2.NegGenerator, SpikeClassifier1.NeuronTrainer3.Neuron.NegGenerator (и еще 29)
- **NPNeuronPosCGenerator**: SpikeClassifier1.NeuronTrainer1.Neuron.PosGenerator, SpikeClassifier1.NeuronTrainer1.PosGenerator, SpikeClassifier1.NeuronTrainer2.Neuron.PosGenerator, SpikeClassifier1.NeuronTrainer2.PosGenerator, SpikeClassifier1.NeuronTrainer3.Neuron.PosGenerator (и еще 29)
- **NPSynapse**: SpikeClassifier1.NeuronTrainer1.Neuron.Soma1.ExcSynapse1, SpikeClassifier1.NeuronTrainer1.Neuron.Soma1.InhSynapse1, SpikeClassifier1.NeuronTrainer1.Neuron.Dendrite1_1.ExcSynapse1, SpikeClassifier1.NeuronTrainer1.Neuron.Dendrite1_1.InhSynapse1, SpikeClassifier1.NeuronTrainer1.Neuron.Soma2.ExcSynapse1 (и еще 2963)
- **NPulseGeneratorTransit**: SpikeClassifier1.NeuronTrainer1.Source1, SpikeClassifier1.NeuronTrainer1.Source2, SpikeClassifier1.NeuronTrainer1.Source3, SpikeClassifier1.NeuronTrainer1.Source4, SpikeClassifier1.Source1 (и еще 75)
- **NSPNeuron**: SpikeClassifier1.NeuronTrainer1.Neuron, SpikeClassifier1.NeuronTrainer2.Neuron, SpikeClassifier1.NeuronTrainer3.Neuron, SpikeClassifier1.Neuron, NeuronTrainer.Neuron (и еще 12)
- **NSpikeClassifier**: SpikeClassifier1, SpikeClassifierIris1, SpikeClassifier

**Входы системы:**
- `NegGenerator`
- `Neuron.NegGenerator`
- `Neuron.PosGenerator`
- `NeuronTrainer.NegGenerator`
- `NeuronTrainer.Neuron.Dendrite1_1.ExcChannel.ChannelInputs`
- `NeuronTrainer.Neuron.Dendrite1_1.ExcChannel.SynapticInputs`
- `NeuronTrainer.Neuron.Dendrite1_1.InhChannel.ChannelInputs`
- `NeuronTrainer.Neuron.Dendrite1_1.InhChannel.SynapticInputs`
- `NeuronTrainer.Neuron.Dendrite2_1.ExcChannel.ChannelInputs`
- `NeuronTrainer.Neuron.Dendrite2_1.ExcChannel.SynapticInputs`
- ... (всего 1549 входов)

**Выходы системы:**
- `NeuronTrainer.Neuron.Dendrite1_1.ExcChannel.Output`
- `NeuronTrainer.Neuron.Dendrite1_1.ExcSynapse1.Output`
- `NeuronTrainer.Neuron.Dendrite1_1.InhChannel.Output`
- `NeuronTrainer.Neuron.Dendrite1_1.InhSynapse1.Output`
- `NeuronTrainer.Neuron.Dendrite2_1.ExcChannel.Output`
- `NeuronTrainer.Neuron.Dendrite2_1.ExcSynapse1.Output`
- `NeuronTrainer.Neuron.Dendrite2_1.InhChannel.Output`
- `NeuronTrainer.Neuron.Dendrite2_1.InhSynapse1.Output`
- `NeuronTrainer.Neuron.Dendrite3_1.ExcChannel.Output`
- `NeuronTrainer.Neuron.Dendrite3_1.ExcSynapse1.Output`
- ... (всего 1303 выходов)

**Количество связей:** 1560

---

### SpikeAssociationPlus

**Путь:** `Bin\Configs\!OldConfigs\SpikeAssociationPlus`

**Назначение:** Модель спайковой нейронной сети

**Основные компоненты:**
- **NConditionedReflex**: ConditionedReflex, ConditionedReflex2, ConditionedReflex3
- **NNeuronTrainer**: ConditionedReflex.ConditionalStimulus, ConditionedReflex.UnconditionalStimulus, ConditionedReflex.AndNeuron, ConditionedReflex2.ConditionalStimulus, ConditionedReflex2.UnconditionalStimulus (и еще 7)
- **NPExcChannelBio**: ConditionedReflex.ConditionalStimulus.Neuron.Soma1.ExcChannel, ConditionedReflex.ConditionalStimulus.Neuron.Dendrite1_1.ExcChannel, ConditionedReflex.ConditionalStimulus.Neuron.Soma2.ExcChannel, ConditionedReflex.ConditionalStimulus.Neuron.Dendrite2_1.ExcChannel, ConditionedReflex.ConditionalStimulus.Neuron.Soma3.ExcChannel (и еще 1009)
- **NPInhChannelBio**: ConditionedReflex.ConditionalStimulus.Neuron.Soma1.InhChannel, ConditionedReflex.ConditionalStimulus.Neuron.Dendrite1_1.InhChannel, ConditionedReflex.ConditionalStimulus.Neuron.Soma2.InhChannel, ConditionedReflex.ConditionalStimulus.Neuron.Dendrite2_1.InhChannel, ConditionedReflex.ConditionalStimulus.Neuron.Soma3.InhChannel (и еще 1009)
- **NPMembraneBio**: ConditionedReflex.ConditionalStimulus.Neuron.Soma1, ConditionedReflex.ConditionalStimulus.Neuron.Dendrite1_1, ConditionedReflex.ConditionalStimulus.Neuron.Soma2, ConditionedReflex.ConditionalStimulus.Neuron.Dendrite2_1, ConditionedReflex.ConditionalStimulus.Neuron.Soma3 (и еще 967)
- **NPNeuronNegCGenerator**: ConditionedReflex.ConditionalStimulus.Neuron.NegGenerator, ConditionedReflex.ConditionalStimulus.NegGenerator, ConditionedReflex.UnconditionalStimulus.Neuron.NegGenerator, ConditionedReflex.UnconditionalStimulus.NegGenerator, ConditionedReflex.AndNeuron.Neuron.NegGenerator (и еще 37)
- **NPNeuronPosCGenerator**: ConditionedReflex.ConditionalStimulus.Neuron.PosGenerator, ConditionedReflex.ConditionalStimulus.PosGenerator, ConditionedReflex.UnconditionalStimulus.Neuron.PosGenerator, ConditionedReflex.UnconditionalStimulus.PosGenerator, ConditionedReflex.AndNeuron.Neuron.PosGenerator (и еще 37)
- **NPSynapseBio**: ConditionedReflex.ConditionalStimulus.Neuron.Soma1.ExcSynapse1, ConditionedReflex.ConditionalStimulus.Neuron.Soma1.InhSynapse1, ConditionedReflex.ConditionalStimulus.Neuron.Dendrite1_1.ExcSynapse1, ConditionedReflex.ConditionalStimulus.Neuron.Dendrite1_1.InhSynapse1, ConditionedReflex.ConditionalStimulus.Neuron.Soma2.ExcSynapse1 (и еще 4263)
- **NPulseGeneratorTransit**: ConditionedReflex.ConditionalStimulus.Source1, ConditionedReflex.ConditionalStimulus.Source2, ConditionedReflex.ConditionalStimulus.Source3, ConditionedReflex.ConditionalStimulus.Source4, ConditionedReflex.UnconditionalStimulus.Source1 (и еще 51)
- **NPulseLTZoneThreshold**: ConditionedReflex.ConditionalStimulus.Neuron.LTZone, ConditionedReflex.ConditionalStimulus.LTZone, ConditionedReflex.UnconditionalStimulus.Neuron.LTZone, ConditionedReflex.UnconditionalStimulus.LTZone, ConditionedReflex.AndNeuron.Neuron.LTZone (и еще 37)
- **NSPNeuronGen**: ConditionedReflex.ConditionalStimulus.Neuron, ConditionedReflex.UnconditionalStimulus.Neuron, ConditionedReflex.AndNeuron.Neuron, ConditionedReflex.ConditionalNeuron, ConditionedReflex.UnconditionalNeuron (и еще 21)

**Входы системы:**
- `AndNeuron.NegGenerator`
- `AndNeuron.Neuron.NegGenerator`
- `AndNeuron.Neuron.PosGenerator`
- `AndNeuron.PosGenerator`
- `AndNeuron.Source1`
- `AndNeuron.Source2`
- `ConditionalNeuron.NegGenerator`
- `ConditionalNeuron.PosGenerator`
- `ConditionalStimulus.NegGenerator`
- `ConditionalStimulus.Neuron.NegGenerator`
- ... (всего 1468 входов)

**Выходы системы:**
- `ConditionedReflex.AndNeuron.Neuron.Dendrite1_1.ExcChannel.Output`
- `ConditionedReflex.AndNeuron.Neuron.Dendrite1_1.ExcSynapse1.Output`
- `ConditionedReflex.AndNeuron.Neuron.Dendrite1_1.ExcSynapse2.Output`
- `ConditionedReflex.AndNeuron.Neuron.Dendrite1_1.ExcSynapse3.Output`
- `ConditionedReflex.AndNeuron.Neuron.Dendrite1_1.ExcSynapse4.Output`
- `ConditionedReflex.AndNeuron.Neuron.Dendrite1_1.ExcSynapse5.Output`
- `ConditionedReflex.AndNeuron.Neuron.Dendrite1_1.InhChannel.Output`
- `ConditionedReflex.AndNeuron.Neuron.Dendrite1_1.InhSynapse1.Output`
- `ConditionedReflex.AndNeuron.Neuron.Dendrite2_1.ExcChannel.Output`
- `ConditionedReflex.AndNeuron.Neuron.Dendrite2_1.ExcSynapse1.Output`
- ... (всего 1299 выходов)

**Количество связей:** 1747

---

### SpikeConditionalReflex

**Путь:** `Bin\Configs\!OldConfigs\SpikeConditionalReflex`

**Назначение:** Модель спайковой нейронной сети

**Основные компоненты:**
- **NConditionedReflex**: ConditionedReflex
- **NNeuronTrainer**: ConditionedReflex.ConditionalStimulus, ConditionedReflex.UnconditionalStimulus, ConditionedReflex.AndNeuron, NeuronTrainer, ConditionalStimulus (и еще 2)
- **NPExcChannel**: ConditionedReflex.ConditionalStimulus.Neuron.Soma1.ExcChannel, ConditionedReflex.ConditionalStimulus.Neuron.Dendrite1_1.ExcChannel, ConditionedReflex.ConditionalStimulus.Neuron.Soma2.ExcChannel, ConditionedReflex.ConditionalStimulus.Neuron.Dendrite2_1.ExcChannel, ConditionedReflex.ConditionalStimulus.Neuron.Soma3.ExcChannel (и еще 171)
- **NPInhChannel**: ConditionedReflex.ConditionalStimulus.Neuron.Soma1.InhChannel, ConditionedReflex.ConditionalStimulus.Neuron.Dendrite1_1.InhChannel, ConditionedReflex.ConditionalStimulus.Neuron.Soma2.InhChannel, ConditionedReflex.ConditionalStimulus.Neuron.Dendrite2_1.InhChannel, ConditionedReflex.ConditionalStimulus.Neuron.Soma3.InhChannel (и еще 171)
- **NPLTZone**: ConditionedReflex.ConditionalStimulus.Neuron.LTZone, ConditionedReflex.ConditionalStimulus.LTZone, ConditionedReflex.UnconditionalStimulus.Neuron.LTZone, ConditionedReflex.UnconditionalStimulus.LTZone, ConditionedReflex.AndNeuron.Neuron.LTZone (и еще 17)
- **NPMembrane**: ConditionedReflex.ConditionalStimulus.Neuron.Soma1, ConditionedReflex.ConditionalStimulus.Neuron.Dendrite1_1, ConditionedReflex.ConditionalStimulus.Neuron.Soma2, ConditionedReflex.ConditionalStimulus.Neuron.Dendrite2_1, ConditionedReflex.ConditionalStimulus.Neuron.Soma3 (и еще 149)
- **NPNeuronNegCGenerator**: ConditionedReflex.ConditionalStimulus.Neuron.NegGenerator, ConditionedReflex.ConditionalStimulus.NegGenerator, ConditionedReflex.UnconditionalStimulus.Neuron.NegGenerator, ConditionedReflex.UnconditionalStimulus.NegGenerator, ConditionedReflex.AndNeuron.Neuron.NegGenerator (и еще 17)
- **NPNeuronPosCGenerator**: ConditionedReflex.ConditionalStimulus.Neuron.PosGenerator, ConditionedReflex.ConditionalStimulus.PosGenerator, ConditionedReflex.UnconditionalStimulus.Neuron.PosGenerator, ConditionedReflex.UnconditionalStimulus.PosGenerator, ConditionedReflex.AndNeuron.Neuron.PosGenerator (и еще 17)
- **NPSynapse**: ConditionedReflex.ConditionalStimulus.Neuron.Soma1.ExcSynapse1, ConditionedReflex.ConditionalStimulus.Neuron.Soma1.InhSynapse1, ConditionedReflex.ConditionalStimulus.Neuron.Dendrite1_1.ExcSynapse1, ConditionedReflex.ConditionalStimulus.Neuron.Dendrite1_1.InhSynapse1, ConditionedReflex.ConditionalStimulus.Neuron.Soma2.ExcSynapse1 (и еще 355)
- **NPulseGeneratorTransit**: ConditionedReflex.ConditionalStimulus.Source1, ConditionedReflex.ConditionalStimulus.Source2, ConditionedReflex.ConditionalStimulus.Source3, ConditionedReflex.ConditionalStimulus.Source4, ConditionedReflex.UnconditionalStimulus.Source1 (и еще 25)
- **NSPNeuron**: ConditionedReflex.ConditionalStimulus.Neuron, ConditionedReflex.UnconditionalStimulus.Neuron, ConditionedReflex.AndNeuron.Neuron, ConditionedReflex.ConditionalNeuron, ConditionedReflex.UnconditionalNeuron (и еще 8)

**Входы системы:**
- `AndNeuron.NegGenerator`
- `AndNeuron.Neuron.NegGenerator`
- `AndNeuron.Neuron.PosGenerator`
- `AndNeuron.PosGenerator`
- `AndNeuron.Source1`
- `AndNeuron.Source2`
- `ConditionalNeuron.NegGenerator`
- `ConditionalNeuron.PosGenerator`
- `ConditionalStimulus.NegGenerator`
- `ConditionalStimulus.Neuron.NegGenerator`
- ... (всего 248 входов)

**Выходы системы:**
- `ConditionedReflex.AndNeuron.Neuron.Dendrite1_1.ExcChannel.Output`
- `ConditionedReflex.AndNeuron.Neuron.Dendrite1_1.ExcSynapse1.Output`
- `ConditionedReflex.AndNeuron.Neuron.Dendrite1_1.InhChannel.Output`
- `ConditionedReflex.AndNeuron.Neuron.Dendrite1_1.InhSynapse1.Output`
- `ConditionedReflex.AndNeuron.Neuron.Dendrite2_1.ExcChannel.Output`
- `ConditionedReflex.AndNeuron.Neuron.Dendrite2_1.ExcSynapse1.Output`
- `ConditionedReflex.AndNeuron.Neuron.Dendrite2_1.InhChannel.Output`
- `ConditionedReflex.AndNeuron.Neuron.Dendrite2_1.InhSynapse1.Output`
- `ConditionedReflex.AndNeuron.Neuron.LTZone.Output`
- `ConditionedReflex.AndNeuron.Neuron.NegGenerator.Output`
- ... (всего 163 выходов)

**Количество связей:** 215

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов
- [Application of the Compartmental Spiking Neuron Model for the Conditioned Reflex Implementation](https://doi.org/10.1007/978-3-030-91581-0_25) - Публикация 23: Korsakov, A., Bakhshiev, A., Astapova, L., Stankevich, L.

---

### SpikeEEG

**Путь:** `Bin\Configs\!OldConfigs\SpikeEEG`

**Назначение:** Модель спайковой нейронной сети

**Основные компоненты:**
- **NNeuronTrainer**: SpikeClassifier.NeuronTrainer1, SpikeClassifier2.NeuronTrainer1, SpikeClassifier3.NeuronTrainer1, SpikeClassifier4.NeuronTrainer1, NeuronTrainer1
- **NPExcChannelBio**: SpikeClassifier.NeuronTrainer1.Neuron.Soma1.ExcChannel, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.ExcChannel, SpikeClassifier.NeuronTrainer1.Neuron.Soma2.ExcChannel, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite2_1.ExcChannel, SpikeClassifier.NeuronTrainer1.Neuron.Soma3.ExcChannel (и еще 1055)
- **NPInhChannelBio**: SpikeClassifier.NeuronTrainer1.Neuron.Soma1.InhChannel, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.InhChannel, SpikeClassifier.NeuronTrainer1.Neuron.Soma2.InhChannel, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite2_1.InhChannel, SpikeClassifier.NeuronTrainer1.Neuron.Soma3.InhChannel (и еще 1055)
- **NPMembraneBio**: SpikeClassifier.NeuronTrainer1.Neuron.Soma1, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1, SpikeClassifier.NeuronTrainer1.Neuron.Soma2, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite2_1, SpikeClassifier.NeuronTrainer1.Neuron.Soma3 (и еще 1035)
- **NPNeuronNegCGenerator**: SpikeClassifier.NeuronTrainer1.Neuron.NegGenerator, SpikeClassifier.NeuronTrainer1.NegGenerator, SpikeClassifier.Neuron.NegGenerator, SpikeClassifier.NegGenerator, SpikeClassifier2.NeuronTrainer1.Neuron.NegGenerator (и еще 15)
- **NPNeuronPosCGenerator**: SpikeClassifier.NeuronTrainer1.Neuron.PosGenerator, SpikeClassifier.NeuronTrainer1.PosGenerator, SpikeClassifier.Neuron.PosGenerator, SpikeClassifier.PosGenerator, SpikeClassifier2.NeuronTrainer1.Neuron.PosGenerator (и еще 15)
- **NPSynapseBio**: SpikeClassifier.NeuronTrainer1.Neuron.Soma1.ExcSynapse1, SpikeClassifier.NeuronTrainer1.Neuron.Soma1.InhSynapse1, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.ExcSynapse1, SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.InhSynapse1, SpikeClassifier.NeuronTrainer1.Neuron.Soma2.ExcSynapse1 (и еще 4711)
- **NPulseGeneratorTransit**: SpikeClassifier.NeuronTrainer1.Source1, SpikeClassifier.NeuronTrainer1.Source2, SpikeClassifier.NeuronTrainer1.Source3, SpikeClassifier.NeuronTrainer1.Source4, SpikeClassifier.NeuronTrainer1.Source5 (и еще 49)
- **NPulseLTZoneThreshold**: SpikeClassifier.NeuronTrainer1.Neuron.LTZone, SpikeClassifier.NeuronTrainer1.LTZone, SpikeClassifier.Neuron.LTZone, SpikeClassifier.LTZone, SpikeClassifier2.NeuronTrainer1.Neuron.LTZone (и еще 15)
- **NSPNeuronGen**: SpikeClassifier.NeuronTrainer1.Neuron, SpikeClassifier.Neuron, SpikeClassifier2.NeuronTrainer1.Neuron, SpikeClassifier2.Neuron, SpikeClassifier3.NeuronTrainer1.Neuron (и еще 5)
- **NSpikeClassifier**: SpikeClassifier, SpikeClassifier2, SpikeClassifier3, SpikeClassifier4

**Входы системы:**
- `NegGenerator`
- `Neuron.NegGenerator`
- `Neuron.PosGenerator`
- `NeuronTrainer1.NegGenerator`
- `NeuronTrainer1.Neuron.NegGenerator`
- `NeuronTrainer1.Neuron.PosGenerator`
- `NeuronTrainer1.PosGenerator`
- `NeuronTrainer1.Source1`
- `NeuronTrainer1.Source2`
- `NeuronTrainer1.Source3`
- ... (всего 1245 входов)

**Выходы системы:**
- `.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.ExcChannel.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.ExcSynapse1.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.InhChannel.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite1_1.InhSynapse1.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite2_1.ExcChannel.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite2_1.ExcSynapse1.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite2_1.InhChannel.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite2_1.InhSynapse1.Output`
- `SpikeClassifier.NeuronTrainer1.Neuron.Dendrite2_2.ExcChannel.Output`
- ... (всего 1139 выходов)

**Количество связей:** 1488

---

### SpikeIrisClassifier

**Путь:** `Bin\Configs\!OldConfigs\SpikeIrisClassifier`

**Назначение:** Модель спайковой нейронной сети

**Связанные публикации:**
- [Application of a compartmental spiking neuron model with structural adaptation for solving classification problems](https://doi.org/10.15622/ia.21.3.2) - Публикация 25: Korsakov, A. M., Astapova, L. A., & Bakhshiev, A. V.

---

### SpikeTrainer

**Путь:** `Bin\Configs\!OldConfigs\SpikeTrainer`

**Назначение:** Модель спайковой нейронной сети

**Основные компоненты:**
- **NNeuronTrainer**: NeuronTrainer
- **NPExcChannel**: NeuronTrainer.Neuron.Soma1.ExcChannel, NeuronTrainer.Neuron.Dendrite1_1.ExcChannel, NeuronTrainer.Neuron.ExcChannel, NeuronTrainer.Soma1.ExcChannel, NeuronTrainer.Dendrite1_1.ExcChannel (и еще 7)
- **NPGenerator**: NeuronTrainer.Generator1, Generator1
- **NPInhChannel**: NeuronTrainer.Neuron.Soma1.InhChannel, NeuronTrainer.Neuron.Dendrite1_1.InhChannel, NeuronTrainer.Neuron.InhChannel, NeuronTrainer.Soma1.InhChannel, NeuronTrainer.Dendrite1_1.InhChannel (и еще 7)
- **NPLTZone**: NeuronTrainer.Neuron.LTZone, NeuronTrainer.LTZone, Neuron.LTZone, LTZone
- **NPMembrane**: NeuronTrainer.Neuron.Soma1, NeuronTrainer.Neuron.Dendrite1_1, NeuronTrainer.Soma1, NeuronTrainer.Dendrite1_1, Neuron.Soma1 (и еще 3)
- **NPNeuronNegCGenerator**: NeuronTrainer.Neuron.NegGenerator, NeuronTrainer.NegGenerator, Neuron.NegGenerator, NegGenerator
- **NPNeuronPosCGenerator**: NeuronTrainer.Neuron.PosGenerator, NeuronTrainer.PosGenerator, Neuron.PosGenerator, PosGenerator
- **NPSynapse**: NeuronTrainer.Neuron.Soma1.ExcSynapse1, NeuronTrainer.Neuron.Soma1.InhSynapse1, NeuronTrainer.Neuron.Dendrite1_1.ExcSynapse1, NeuronTrainer.Neuron.Dendrite1_1.InhSynapse1, NeuronTrainer.Neuron.ExcSynapse1 (и еще 19)
- **NSPNeuron**: NeuronTrainer.Neuron, Neuron
- **UStatisticDoubleMatrix**: StatisticDoubleMatrix

**Входы системы:**
- `Generator1`
- `NegGenerator`
- `Neuron.NegGenerator`
- `Neuron.PosGenerator`
- `NeuronTrainer.Generator1`
- `NeuronTrainer.NegGenerator`
- `NeuronTrainer.Neuron.Dendrite1_1.ExcChannel.ChannelInputs`
- `NeuronTrainer.Neuron.Dendrite1_1.ExcChannel.SynapticInputs`
- `NeuronTrainer.Neuron.Dendrite1_1.ExcSynapse1.Input`
- `NeuronTrainer.Neuron.Dendrite1_1.InhChannel.ChannelInputs`
- ... (всего 21 входов)

**Выходы системы:**
- `NeuronTrainer.Generator1.Output`
- `NeuronTrainer.Neuron.Dendrite1_1.ExcChannel.Output`
- `NeuronTrainer.Neuron.Dendrite1_1.ExcSynapse1.Output`
- `NeuronTrainer.Neuron.Dendrite1_1.InhChannel.Output`
- `NeuronTrainer.Neuron.Dendrite1_1.InhSynapse1.Output`
- `NeuronTrainer.Neuron.LTZone.Output`
- `NeuronTrainer.Neuron.NegGenerator.Output`
- `NeuronTrainer.Neuron.PosGenerator.Output`
- `NeuronTrainer.Neuron.Soma1.ExcChannel.Output`
- `NeuronTrainer.Neuron.Soma1.ExcSynapse1.Output`
- ... (всего 12 выходов)

**Количество связей:** 12

---

### TSNETest

**Путь:** `Bin\Configs\!OldConfigs\TSNETest`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **UCRBarnesHutTSNE**: CRBarnesHutTSNE
- **UMatrixSourceDataFile**: UMatrixSourceDataFile

**Входы системы:**
- `CRBarnesHutTSNE.InputComponents`

**Количество связей:** 1

---

### Test_3classes_4ex

**Путь:** `Bin\Configs\!OldConfigs\Test_3classes_4ex`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NClassifier**: Classifier
- **NNeuronTrainer**: Classifier.NeuronTrainer1_1, Classifier.NeuronTrainer2_1, Classifier.NeuronTrainer1_2, Classifier.NeuronTrainer1_3, Classifier.NeuronTrainer1_4 (и еще 19)
- **NPExcChannelBio**: Classifier.NeuronTrainer1_1.Neuron.Soma1.ExcChannel, Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.ExcChannel, Classifier.NeuronTrainer1_1.Neuron.Soma2.ExcChannel, Classifier.NeuronTrainer1_1.Neuron.Dendrite2_1.ExcChannel, Classifier.NeuronTrainer1_1.Neuron.Soma3.ExcChannel (и еще 2991)
- **NPInhChannelBio**: Classifier.NeuronTrainer1_1.Neuron.Soma1.InhChannel, Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.InhChannel, Classifier.NeuronTrainer1_1.Neuron.Soma2.InhChannel, Classifier.NeuronTrainer1_1.Neuron.Dendrite2_1.InhChannel, Classifier.NeuronTrainer1_1.Neuron.Soma3.InhChannel (и еще 2991)
- **NPMembraneBio**: Classifier.NeuronTrainer1_1.Neuron.Soma1, Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1, Classifier.NeuronTrainer1_1.Neuron.Soma2, Classifier.NeuronTrainer1_1.Neuron.Dendrite2_1, Classifier.NeuronTrainer1_1.Neuron.Soma3 (и еще 2933)
- **NPNeuronNegCGenerator**: Classifier.NeuronTrainer1_1.Neuron.NegGenerator, Classifier.NeuronTrainer1_1.NegGenerator, Classifier.OrNeuron1.NegGenerator, Classifier.NeuronTrainer2_1.Neuron.NegGenerator, Classifier.NeuronTrainer2_1.NegGenerator (и еще 53)
- **NPNeuronPosCGenerator**: Classifier.NeuronTrainer1_1.Neuron.PosGenerator, Classifier.NeuronTrainer1_1.PosGenerator, Classifier.OrNeuron1.PosGenerator, Classifier.NeuronTrainer2_1.Neuron.PosGenerator, Classifier.NeuronTrainer2_1.PosGenerator (и еще 53)
- **NPSynapseBio**: Classifier.NeuronTrainer1_1.Neuron.Soma1.ExcSynapse1, Classifier.NeuronTrainer1_1.Neuron.Soma1.InhSynapse1, Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.ExcSynapse1, Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.InhSynapse1, Classifier.NeuronTrainer1_1.Neuron.Soma2.ExcSynapse1 (и еще 13853)
- **NPulseGeneratorTransit**: Classifier.NeuronTrainer1_1.Source1, Classifier.NeuronTrainer1_1.Source2, Classifier.NeuronTrainer1_1.Source3, Classifier.NeuronTrainer1_1.Source4, Classifier.NeuronTrainer1_1.Source5 (и еще 125)
- **NPulseLTZoneThreshold**: Classifier.NeuronTrainer1_1.Neuron.LTZone, Classifier.NeuronTrainer1_1.LTZone, Classifier.OrNeuron1.LTZone, Classifier.NeuronTrainer2_1.Neuron.LTZone, Classifier.NeuronTrainer2_1.LTZone (и еще 53)
- **NSPNeuronGen**: Classifier.NeuronTrainer1_1.Neuron, Classifier.OrNeuron1, Classifier.NeuronTrainer2_1.Neuron, Classifier.OrNeuron2, Classifier.NeuronTrainer1_2.Neuron (и еще 27)

**Входы системы:**
- `Classifier.NegGenerator`
- `Classifier.Neuron.NegGenerator`
- `Classifier.Neuron.PosGenerator`
- `Classifier.NeuronTrainer1_1.NegGenerator`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.ExcChannel.ChannelInputs`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.ExcChannel.SynapticInputs`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.InhChannel.ChannelInputs`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.InhChannel.SynapticInputs`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_10.ExcChannel.ChannelInputs`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_10.ExcChannel.SynapticInputs`
- ... (всего 4012 входов)

**Выходы системы:**
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.ExcChannel.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.ExcSynapse1.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.InhChannel.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.InhSynapse1.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_10.ExcChannel.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_10.ExcSynapse1.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_10.InhChannel.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_10.InhSynapse1.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_11.ExcChannel.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_11.ExcSynapse1.Output`
- ... (всего 3673 выходов)

**Количество связей:** 4842

---

### TimeSeriesTest

**Путь:** `Bin\Configs\!OldConfigs\TimeSeriesTest`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **UMatrixSourceTimeSeries**: MatrixSourceTimeSeries

---

### XOR

**Путь:** `Bin\Configs\!OldConfigs\XOR`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NClassifier**: Classifier
- **NNeuronTrainer**: Classifier.NeuronTrainer1_1, Classifier.NeuronTrainer1_2, NeuronTrainer1_1, NeuronTrainer1_2
- **NPExcChannelBio**: Classifier.NeuronTrainer1_1.Neuron.Soma1.ExcChannel, Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.ExcChannel, Classifier.NeuronTrainer1_1.Neuron.Soma2.ExcChannel, Classifier.NeuronTrainer1_1.Neuron.Dendrite2_1.ExcChannel, Classifier.NeuronTrainer1_1.Neuron.Dendrite1_2.ExcChannel (и еще 91)
- **NPInhChannelBio**: Classifier.NeuronTrainer1_1.Neuron.Soma1.InhChannel, Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.InhChannel, Classifier.NeuronTrainer1_1.Neuron.Soma2.InhChannel, Classifier.NeuronTrainer1_1.Neuron.Dendrite2_1.InhChannel, Classifier.NeuronTrainer1_1.Neuron.Dendrite1_2.InhChannel (и еще 91)
- **NPMembraneBio**: Classifier.NeuronTrainer1_1.Neuron.Soma1, Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1, Classifier.NeuronTrainer1_1.Neuron.Soma2, Classifier.NeuronTrainer1_1.Neuron.Dendrite2_1, Classifier.NeuronTrainer1_1.Neuron.Dendrite1_2 (и еще 77)
- **NPNeuronNegCGenerator**: Classifier.NeuronTrainer1_1.Neuron.NegGenerator, Classifier.NeuronTrainer1_1.NegGenerator, Classifier.OrNeuron1.NegGenerator, Classifier.NeuronTrainer1_2.Neuron.NegGenerator, Classifier.NeuronTrainer1_2.NegGenerator (и еще 9)
- **NPNeuronPosCGenerator**: Classifier.NeuronTrainer1_1.Neuron.PosGenerator, Classifier.NeuronTrainer1_1.PosGenerator, Classifier.OrNeuron1.PosGenerator, Classifier.NeuronTrainer1_2.Neuron.PosGenerator, Classifier.NeuronTrainer1_2.PosGenerator (и еще 9)
- **NPSynapseBio**: Classifier.NeuronTrainer1_1.Neuron.Soma1.ExcSynapse1, Classifier.NeuronTrainer1_1.Neuron.Soma1.InhSynapse1, Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.ExcSynapse1, Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.InhSynapse1, Classifier.NeuronTrainer1_1.Neuron.Soma2.ExcSynapse1 (и еще 333)
- **NPulseGeneratorTransit**: Classifier.NeuronTrainer1_1.Source1, Classifier.NeuronTrainer1_1.Source2, Classifier.Source1, Classifier.NeuronTrainer1_2.Source1, Classifier.NeuronTrainer1_2.Source2 (и еще 7)
- **NPulseLTZoneThreshold**: Classifier.NeuronTrainer1_1.Neuron.LTZone, Classifier.NeuronTrainer1_1.LTZone, Classifier.OrNeuron1.LTZone, Classifier.NeuronTrainer1_2.Neuron.LTZone, Classifier.NeuronTrainer1_2.LTZone (и еще 9)
- **NSPNeuronGen**: Classifier.NeuronTrainer1_1.Neuron, Classifier.OrNeuron1, Classifier.NeuronTrainer1_2.Neuron, Classifier.Neuron, NeuronTrainer1_1.Neuron (и еще 3)

**Входы системы:**
- `Classifier.NegGenerator`
- `Classifier.Neuron.NegGenerator`
- `Classifier.Neuron.PosGenerator`
- `Classifier.NeuronTrainer1_1.NegGenerator`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.ExcChannel.ChannelInputs`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.ExcChannel.SynapticInputs`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.InhChannel.ChannelInputs`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.InhChannel.SynapticInputs`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_2.ExcChannel.ChannelInputs`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_2.ExcChannel.SynapticInputs`
- ... (всего 120 входов)

**Выходы системы:**
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.ExcChannel.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.ExcSynapse1.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.InhChannel.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_1.InhSynapse1.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_2.ExcChannel.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_2.ExcSynapse1.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_2.InhChannel.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_2.InhSynapse1.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_3.ExcChannel.Output`
- `Classifier.NeuronTrainer1_1.Neuron.Dendrite1_3.ExcSynapse1.Output`
- ... (всего 78 выходов)

**Количество связей:** 98

---

## 1_MotionControl_Test

### MotionControl_Test

**Путь:** `Bin\Configs\a.demcheva\1_MotionControl_Test\MotionControl_Test`

**Назначение:** Система управления движением

**Основные компоненты:**
- **NCGenerator**: AngleGen, VoltageGen, EngineMotionControl.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineMotionControl.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NEngineMotionControl**: EngineMotionControl
- **NIntervalSeparator**: IntervalSeparator, IntervalSeparator2, EngineMotionControl.NegIntervalSeparator11, EngineMotionControl.PosIntervalSeparator11, NegIntervalSeparator11 (и еще 1)
- **NManipulatorInput**: ManipulatorInput, EngineMotionControl.NManipulatorInput1, NManipulatorInput1
- **NManipulatorSource**: ManipulatorSource
- **NNewMotionElement**: MotionElement, EngineMotionControl.MotionElement0, MotionElement0
- **NNewSPNeuron**: MotionElement.MotoneuronL, MotionElement.MotoneuronR, MotionElement.PostAfferentL1, MotionElement.PostAfferentR1, EngineMotionControl.MotionElement0.MotoneuronL (и еще 9)
- **NPExcChannel**: MotionElement.MotoneuronL.Soma1.ExcChannel, MotionElement.MotoneuronR.Soma1.ExcChannel, MotionElement.PostAfferentL1.Soma1.ExcChannel, MotionElement.PostAfferentR1.Soma1.ExcChannel, MotionElement.Soma1.ExcChannel (и еще 14)
- **NPGenerator**: MotionElement.AfferentR1.LTZone.PGenerator, MotionElement.AfferentR1.PGenerator, MotionElement.AfferentL1.LTZone.PGenerator, MotionElement.AfferentL1.PGenerator, MotionElement.LTZone.PGenerator (и еще 31)
- **NPInhChannel**: MotionElement.MotoneuronL.Soma1.InhChannel, MotionElement.MotoneuronR.Soma1.InhChannel, MotionElement.PostAfferentL1.Soma1.InhChannel, MotionElement.PostAfferentR1.Soma1.InhChannel, MotionElement.Soma1.InhChannel (и еще 14)
- **NPLTExcChannel**: MotionElement.MotoneuronL.LTMembrane.ExcChannel, MotionElement.MotoneuronL.ExcChannel, MotionElement.MotoneuronR.LTMembrane.ExcChannel, MotionElement.MotoneuronR.ExcChannel, MotionElement.PostAfferentL1.LTMembrane.ExcChannel (и еще 33)
- **NPLTInhChannel**: MotionElement.MotoneuronL.LTMembrane.InhChannel, MotionElement.MotoneuronL.InhChannel, MotionElement.MotoneuronR.LTMembrane.InhChannel, MotionElement.MotoneuronR.InhChannel, MotionElement.PostAfferentL1.LTMembrane.InhChannel (и еще 33)
- **NPLTZone**: MotionElement.MotoneuronL.LTZone, MotionElement.MotoneuronR.LTZone, MotionElement.PostAfferentL1.LTZone, MotionElement.PostAfferentR1.LTZone, MotionElement.LTZone (и еще 10)
- **NPLTZoneNeuronMembrane**: MotionElement.MotoneuronL.LTMembrane, MotionElement.MotoneuronR.LTMembrane, MotionElement.PostAfferentL1.LTMembrane, MotionElement.PostAfferentR1.LTMembrane, MotionElement.LTMembrane (и еще 14)
- **NPMembrane**: MotionElement.MotoneuronL.Soma1, MotionElement.MotoneuronR.Soma1, MotionElement.PostAfferentL1.Soma1, MotionElement.PostAfferentR1.Soma1, MotionElement.Soma1 (и еще 14)
- **NPNeuronNegCGenerator**: MotionElement.MotoneuronL.NegGenerator, MotionElement.MotoneuronR.NegGenerator, MotionElement.PostAfferentL1.NegGenerator, MotionElement.PostAfferentR1.NegGenerator, MotionElement.NegGenerator (и еще 14)
- **NPNeuronPosCGenerator**: MotionElement.MotoneuronL.PosGenerator, MotionElement.MotoneuronR.PosGenerator, MotionElement.PostAfferentL1.PosGenerator, MotionElement.PostAfferentR1.PosGenerator, MotionElement.PosGenerator (и еще 14)
- **NPSimpleLTZone**: MotionElement.AfferentR1.LTZone, MotionElement.AfferentL1.LTZone, EngineMotionControl.MotionElement0.AfferentR1.LTZone, EngineMotionControl.MotionElement0.AfferentL1.LTZone, EngineMotionControl.MotionElement0.LTZone (и еще 9)
- **NPSynapse**: MotionElement.MotoneuronL.Soma1.ExcSynapse1, MotionElement.MotoneuronL.Soma1.InhSynapse1, MotionElement.MotoneuronL.LTMembrane.ExcSynapse1, MotionElement.MotoneuronL.LTMembrane.InhSynapse1, MotionElement.MotoneuronL.ExcSynapse1 (и еще 109)
- **NPac**: Pac, EngineMotionControl.Pac
- **NReceptor**: MotionElement.AfferentR1.Receptor, MotionElement.AfferentL1.Receptor, MotionElement.Receptor, EngineMotionControl.MotionElement0.AfferentR1.Receptor, EngineMotionControl.MotionElement0.AfferentL1.Receptor (и еще 10)
- **NSimpleAfferentNeuron**: MotionElement.AfferentR1, MotionElement.AfferentL1, EngineMotionControl.MotionElement0.AfferentR1, EngineMotionControl.MotionElement0.AfferentL1, EngineMotionControl.AfferentR1 (и еще 5)
- **UStatisticDoubleMatrix**: EngineMotionControl.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentL1.LTZone.PGenerator`
- `AfferentL1.PGenerator`
- `AfferentR1.LTZone.PGenerator`
- `AfferentR1.PGenerator`
- `AfferentSource1`
- `AngleGen`
- `DCEngine.InputVoltage`
- `EngineMotionControl.AfferentL1.LTZone.PGenerator`
- `EngineMotionControl.AfferentL1.PGenerator`
- `EngineMotionControl.AfferentR1.LTZone.PGenerator`
- ... (всего 167 входов)

**Выходы системы:**
- `DCEngine.OutputAngle`
- `EngineMotionControl.MotionElement0.AfferentL1.LTZone.Output`
- `EngineMotionControl.MotionElement0.AfferentL1.Receptor.Output`
- `EngineMotionControl.MotionElement0.AfferentR1.LTZone.Output`
- `EngineMotionControl.MotionElement0.AfferentR1.Receptor.Output`
- `EngineMotionControl.MotionElement0.MotoneuronL.LTMembrane.ExcChannel.Output`
- `EngineMotionControl.MotionElement0.MotoneuronL.LTMembrane.ExcSynapse1.Output`
- `EngineMotionControl.MotionElement0.MotoneuronL.LTMembrane.InhChannel.Output`
- `EngineMotionControl.MotionElement0.MotoneuronL.LTMembrane.InhSynapse1.Output`
- `EngineMotionControl.MotionElement0.MotoneuronL.LTZone.Output`
- ... (всего 84 выходов)

**Количество связей:** 97

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

## Alexab

### SpikingNeuron

**Путь:** `Bin\Configs\Alexab\SpikingNeuron`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPExcChannelBio**: PNeuronS1D0Syn1.Soma1.ExcChannel, PNeuronS1D0Syn1.ExcChannel, PNeuronS1D1Syn1.Dendrite1_1.ExcChannel, PNeuronS1D1Syn1.Soma1.ExcChannel, PNeuronS1D1Syn1.ExcChannel (и еще 27)
- **NPGenerator**: PGenerator
- **NPInhChannelBio**: PNeuronS1D0Syn1.Soma1.InhChannel, PNeuronS1D0Syn1.InhChannel, PNeuronS1D1Syn1.Dendrite1_1.InhChannel, PNeuronS1D1Syn1.Soma1.InhChannel, PNeuronS1D1Syn1.InhChannel (и еще 27)
- **NPMembraneBio**: PNeuronS1D0Syn1.Soma1, PNeuronS1D1Syn1.Dendrite1_1, PNeuronS1D1Syn1.Soma1, PNeuronS1D2Syn1.Dendrite1_2, PNeuronS1D2Syn1.Dendrite1_1 (и еще 18)
- **NPNeuronNegCGenerator**: PNeuronS1D0Syn1.NegGenerator, PNeuronS1D1Syn1.NegGenerator, PNeuronS1D2Syn1.NegGenerator, PNeuronS1D3Syn1.NegGenerator, PNeuronS2D0Syn1.NegGenerator (и еще 4)
- **NPNeuronPosCGenerator**: PNeuronS1D0Syn1.PosGenerator, PNeuronS1D1Syn1.PosGenerator, PNeuronS1D2Syn1.PosGenerator, PNeuronS1D3Syn1.PosGenerator, PNeuronS2D0Syn1.PosGenerator (и еще 4)
- **NPSynapseBio**: PNeuronS1D0Syn1.Soma1.ExcSynapse1, PNeuronS1D0Syn1.Soma1.InhSynapse1, PNeuronS1D0Syn1.ExcSynapse1, PNeuronS1D0Syn1.InhSynapse1, PNeuronS1D1Syn1.Dendrite1_1.ExcSynapse1 (и еще 79)
- **NPulseLTZoneThreshold**: PNeuronS1D0Syn1.LTZone, PNeuronS1D1Syn1.LTZone, PNeuronS1D2Syn1.LTZone, PNeuronS1D3Syn1.LTZone, PNeuronS2D0Syn1.LTZone (и еще 4)
- **NSPNeuronGen**: PNeuronS1D0Syn1, PNeuronS1D1Syn1, PNeuronS1D2Syn1, PNeuronS1D3Syn1, PNeuronS2D0Syn1 (и еще 3)

**Входы системы:**
- `NegGenerator`
- `PGenerator`
- `PNeuronS1D0Syn1.LTZone.Inputs`
- `PNeuronS1D0Syn1.NegGenerator`
- `PNeuronS1D0Syn1.PosGenerator`
- `PNeuronS1D0Syn1.Soma1.ExcChannel.ChannelInputs`
- `PNeuronS1D0Syn1.Soma1.ExcChannel.SynapticInputs`
- `PNeuronS1D0Syn1.Soma1.ExcSynapse1.Input`
- `PNeuronS1D0Syn1.Soma1.InhChannel.ChannelInputs`
- `PNeuronS1D0Syn1.Soma1.InhChannel.SynapticInputs`
- ... (всего 117 входов)

**Выходы системы:**
- `PGenerator.Output`
- `PNeuronS1D0Syn1.LTZone.Output`
- `PNeuronS1D0Syn1.NegGenerator.Output`
- `PNeuronS1D0Syn1.PosGenerator.Output`
- `PNeuronS1D0Syn1.Soma1.ExcChannel.Output`
- `PNeuronS1D0Syn1.Soma1.ExcSynapse1.Output`
- `PNeuronS1D0Syn1.Soma1.InhChannel.Output`
- `PNeuronS1D0Syn1.Soma1.InhSynapse1.Output`
- `PNeuronS1D0Syn2.LTZone.Output`
- `PNeuronS1D0Syn2.NegGenerator.Output`
- ... (всего 99 выходов)

**Количество связей:** 118

---

## Boiko

### ChannelTs0.00001

**Путь:** `Bin\Configs\Boiko\ChannelTs0.00001`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NPChannel**: ChannelSpikeTest, ChannelStepTest
- **NPGenerator**: PGenerator3, PGenerator32
- **NPNeuronPosCGenerator**: PNeuronPosCGenerator, PNeuronPosCGenerator2
- **UStatisticDoubleMatrix**: StatisticDoubleMatrix

**Входы системы:**
- `ChannelSpikeTest.ChannelInputs`
- `ChannelSpikeTest.SynapticInputs`
- `ChannelStepTest.ChannelInputs`
- `ChannelStepTest.SynapticInputs`
- `PGenerator3`
- `PGenerator32`
- `PNeuronPosCGenerator`
- `PNeuronPosCGenerator2`
- `StatisticDoubleMatrix.InputMatrixData`

**Выходы системы:**
- `ChannelSpikeTest.Output`
- `ChannelStepTest.Output`
- `PGenerator3.Output`
- `PGenerator32.Output`
- `PNeuronPosCGenerator.Output`
- `PNeuronPosCGenerator2.Output`

**Количество связей:** 6

---

### ChannelTs0.0005

**Путь:** `Bin\Configs\Boiko\ChannelTs0.0005`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NPChannel**: ChannelSpikeTest, ChannelStepTest
- **NPGenerator**: PGenerator3, PGenerator32
- **NPNeuronPosCGenerator**: PNeuronPosCGenerator, PNeuronPosCGenerator2
- **UStatisticDoubleMatrix**: StatisticDoubleMatrix

**Входы системы:**
- `ChannelSpikeTest.ChannelInputs`
- `ChannelSpikeTest.SynapticInputs`
- `ChannelStepTest.ChannelInputs`
- `ChannelStepTest.SynapticInputs`
- `PGenerator3`
- `PGenerator32`
- `PNeuronPosCGenerator`
- `PNeuronPosCGenerator2`
- `StatisticDoubleMatrix.InputMatrixData`

**Выходы системы:**
- `ChannelSpikeTest.Output`
- `ChannelStepTest.Output`
- `PGenerator3.Output`
- `PGenerator32.Output`
- `PNeuronPosCGenerator.Output`
- `PNeuronPosCGenerator2.Output`

**Количество связей:** 6

---

### SynapseTs0.00001

**Путь:** `Bin\Configs\Boiko\SynapseTs0.00001`

**Назначение:** Простая тестовая модель с генератором сигналов

**Основные компоненты:**
- **NPGenerator**: PGenerator
- **NPSynapse**: SynapseStepTest, SynapseSpikeTest
- **UStatisticDoubleMatrix**: StatisticDoubleMatrix

**Входы системы:**
- `PGenerator`
- `StatisticDoubleMatrix.InputMatrixData`
- `SynapseSpikeTest.Input`
- `SynapseStepTest.Input`

**Выходы системы:**
- `PGenerator.Output`
- `SynapseSpikeTest.Output`
- `SynapseStepTest.Output`

**Количество связей:** 4

---

### SynapseTs0.0005

**Путь:** `Bin\Configs\Boiko\SynapseTs0.0005`

**Назначение:** Простая тестовая модель с генератором сигналов

**Основные компоненты:**
- **NPGenerator**: PGenerator
- **NPSynapse**: SynapseStepTest, SynapseSpikeTest
- **UStatisticDoubleMatrix**: StatisticDoubleMatrix

**Входы системы:**
- `PGenerator`
- `StatisticDoubleMatrix.InputMatrixData`
- `SynapseSpikeTest.Input`
- `SynapseStepTest.Input`

**Выходы системы:**
- `PGenerator.Output`
- `SynapseSpikeTest.Output`
- `SynapseStepTest.Output`

**Количество связей:** 4

---

## CognitiveNavigation

### Ivan_VKR_3-4_13

**Путь:** `Bin\Configs\User\CognitiveNavigation\Ivan_VKR_3-4_13`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NPExcChannelBio**: NOTNeuron1.Dendrite1_1.ExcChannel, NOTNeuron1.Soma1.ExcChannel, NOTNeuron1.ExcChannel, NOTNeuron2.Dendrite1_1.ExcChannel, NOTNeuron2.Soma1.ExcChannel (и еще 22)
- **NPInhChannelBio**: NOTNeuron1.Dendrite1_1.InhChannel, NOTNeuron1.Soma1.InhChannel, NOTNeuron1.InhChannel, NOTNeuron2.Dendrite1_1.InhChannel, NOTNeuron2.Soma1.InhChannel (и еще 22)
- **NPMembraneBio**: NOTNeuron1.Dendrite1_1, NOTNeuron1.Soma1, NOTNeuron2.Dendrite1_1, NOTNeuron2.Soma1, NOTNeuron3.Dendrite1_1 (и еще 15)
- **NPNeuronNegCGenerator**: NOTNeuron1.NegGenerator, NOTNeuron2.NegGenerator, NOTNeuron3.NegGenerator, NOTNeuron4.NegGenerator, ORNeuron.NegGenerator (и еще 2)
- **NPNeuronPosCGenerator**: NOTNeuron1.PosGenerator, NOTNeuron2.PosGenerator, NOTNeuron3.PosGenerator, NOTNeuron4.PosGenerator, ORNeuron.PosGenerator (и еще 2)
- **NPSynapseBio**: NOTNeuron1.Dendrite1_1.ExcSynapse1, NOTNeuron1.Dendrite1_1.InhSynapse1, NOTNeuron1.Soma1.ExcSynapse1, NOTNeuron1.Soma1.InhSynapse1, NOTNeuron1.ExcSynapse1 (и еще 53)
- **NPulseGeneratorTransit**: NOTGenerator1, NOTGenerator2, NOTGenerator3, NOTGenerator4, Forward (и еще 5)
- **NPulseLTZoneThreshold**: NOTNeuron1.LTZone, NOTNeuron2.LTZone, NOTNeuron3.LTZone, NOTNeuron4.LTZone, ORNeuron.LTZone (и еще 2)
- **NSPNeuronGen**: NOTNeuron1, NOTNeuron2, NOTNeuron3, NOTNeuron4, ORNeuron (и еще 1)

**Входы системы:**
- `ANDNeuron.LTZone.Inputs`
- `ANDNeuron.NegGenerator`
- `ANDNeuron.PosGenerator`
- `ANDNeuron.Soma1.ExcChannel.ChannelInputs`
- `ANDNeuron.Soma1.ExcChannel.SynapticInputs`
- `ANDNeuron.Soma1.ExcSynapse1.Input`
- `ANDNeuron.Soma1.InhChannel.ChannelInputs`
- `ANDNeuron.Soma1.InhChannel.SynapticInputs`
- `ANDNeuron.Soma1.InputFeedbackSignal`
- `ANDNeuron.Soma2.ExcChannel.ChannelInputs`
- ... (всего 111 входов)

**Выходы системы:**
- `ANDNeuron.LTZone.Output`
- `ANDNeuron.NegGenerator.Output`
- `ANDNeuron.PosGenerator.Output`
- `ANDNeuron.Soma1.ExcChannel.Output`
- `ANDNeuron.Soma1.ExcSynapse1.Output`
- `ANDNeuron.Soma1.InhChannel.Output`
- `ANDNeuron.Soma1.InhSynapse1.Output`
- `ANDNeuron.Soma2.ExcChannel.Output`
- `ANDNeuron.Soma2.ExcSynapse1.Output`
- `ANDNeuron.Soma2.InhChannel.Output`
- ... (всего 85 выходов)

**Количество связей:** 102

---

### Ivan_VKR_3-4_21

**Путь:** `Bin\Configs\User\CognitiveNavigation\Ivan_VKR_3-4_21`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NPExcChannelBio**: NOTNeuron1.Dendrite1_1.ExcChannel, NOTNeuron1.Soma1.ExcChannel, NOTNeuron1.ExcChannel, NOTNeuron2.Dendrite1_1.ExcChannel, NOTNeuron2.Soma1.ExcChannel (и еще 19)
- **NPInhChannelBio**: NOTNeuron1.Dendrite1_1.InhChannel, NOTNeuron1.Soma1.InhChannel, NOTNeuron1.InhChannel, NOTNeuron2.Dendrite1_1.InhChannel, NOTNeuron2.Soma1.InhChannel (и еще 19)
- **NPMembraneBio**: NOTNeuron1.Dendrite1_1, NOTNeuron1.Soma1, NOTNeuron2.Dendrite1_1, NOTNeuron2.Soma1, NOTNeuron3.Dendrite1_1 (и еще 11)
- **NPNeuronNegCGenerator**: NOTNeuron1.NegGenerator, NOTNeuron2.NegGenerator, NOTNeuron3.NegGenerator, ANDNeuron1.NegGenerator, ANDNeuron2.NegGenerator (и еще 3)
- **NPNeuronPosCGenerator**: NOTNeuron1.PosGenerator, NOTNeuron2.PosGenerator, NOTNeuron3.PosGenerator, ANDNeuron1.PosGenerator, ANDNeuron2.PosGenerator (и еще 3)
- **NPSynapseBio**: NOTNeuron1.Dendrite1_1.ExcSynapse1, NOTNeuron1.Dendrite1_1.InhSynapse1, NOTNeuron1.Soma1.ExcSynapse1, NOTNeuron1.Soma1.InhSynapse1, NOTNeuron1.ExcSynapse1 (и еще 47)
- **NPulseGeneratorTransit**: ObstacleAhead, ObstacleLeft, ObstacleRight, NOTGenerator1, NOTGenerator2 (и еще 1)
- **NPulseLTZoneThreshold**: NOTNeuron1.LTZone, NOTNeuron2.LTZone, NOTNeuron3.LTZone, ANDNeuron1.LTZone, ANDNeuron2.LTZone (и еще 3)
- **NSPNeuronGen**: NOTNeuron1, NOTNeuron2, NOTNeuron3, ANDNeuron1, ANDNeuron2 (и еще 2)

**Входы системы:**
- `ANDNeuron.LTZone.Inputs`
- `ANDNeuron.NegGenerator`
- `ANDNeuron.PosGenerator`
- `ANDNeuron.Soma1.ExcChannel.ChannelInputs`
- `ANDNeuron.Soma1.ExcChannel.SynapticInputs`
- `ANDNeuron.Soma1.ExcSynapse1.Input`
- `ANDNeuron.Soma1.InhChannel.ChannelInputs`
- `ANDNeuron.Soma1.InhChannel.SynapticInputs`
- `ANDNeuron.Soma1.InputFeedbackSignal`
- `ANDNeuron.Soma2.ExcChannel.ChannelInputs`
- ... (всего 105 входов)

**Выходы системы:**
- `ANDNeuron.LTZone.Output`
- `ANDNeuron.NegGenerator.Output`
- `ANDNeuron.PosGenerator.Output`
- `ANDNeuron.Soma1.ExcChannel.Output`
- `ANDNeuron.Soma1.ExcSynapse1.Output`
- `ANDNeuron.Soma1.InhChannel.Output`
- `ANDNeuron.Soma1.InhSynapse1.Output`
- `ANDNeuron.Soma2.ExcChannel.Output`
- `ANDNeuron.Soma2.ExcSynapse1.Output`
- `ANDNeuron.Soma2.InhChannel.Output`
- ... (всего 80 выходов)

**Количество связей:** 97

---

### Ivan_VKR_3-4_4

**Путь:** `Bin\Configs\User\CognitiveNavigation\Ivan_VKR_3-4_4`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NPDelay**: Delay05To15
- **NPExcChannelBio**: IsForward.Soma1.ExcChannel, IsForward.Soma2.ExcChannel, IsForward.ExcChannel, IsBack.Soma1.ExcChannel, IsBack.Soma2.ExcChannel (и еще 66)
- **NPInhChannelBio**: IsForward.Soma1.InhChannel, IsForward.Soma2.InhChannel, IsForward.InhChannel, IsBack.Soma1.InhChannel, IsBack.Soma2.InhChannel (и еще 66)
- **NPMembraneBio**: IsForward.Soma1, IsForward.Soma2, IsBack.Soma1, IsBack.Soma2, IsLeft.Dendrite1_10 (и еще 54)
- **NPNeuronNegCGenerator**: IsForward.NegGenerator, IsBack.NegGenerator, IsLeft.NegGenerator, IsRight.NegGenerator, Forward.NegGenerator (и еще 7)
- **NPNeuronPosCGenerator**: IsForward.PosGenerator, IsBack.PosGenerator, IsLeft.PosGenerator, IsRight.PosGenerator, Forward.PosGenerator (и еще 7)
- **NPSynapseBio**: IsForward.Soma1.ExcSynapse1, IsForward.Soma1.InhSynapse1, IsForward.Soma2.ExcSynapse1, IsForward.Soma2.InhSynapse1, IsForward.ExcSynapse1 (и еще 149)
- **NPulseGeneratorTransit**: LeftEngine, RightEngine, Sinchro05, Sinchro15, NOTGenerator
- **NPulseLTZoneThreshold**: IsForward.LTZone, IsBack.LTZone, IsLeft.LTZone, IsRight.LTZone, Forward.LTZone (и еще 7)
- **NSPNeuronGen**: IsForward, IsBack, IsLeft, IsRight, Forward (и еще 6)

**Входы системы:**
- `Back.LTZone.Inputs`
- `Back.NegGenerator`
- `Back.PosGenerator`
- `Back.Soma1.ExcChannel.ChannelInputs`
- `Back.Soma1.ExcChannel.SynapticInputs`
- `Back.Soma1.ExcSynapse1.Input`
- `Back.Soma1.InhChannel.ChannelInputs`
- `Back.Soma1.InhChannel.SynapticInputs`
- `Back.Soma1.InputFeedbackSignal`
- `Delay05To15.Input`
- ... (всего 231 входов)

**Выходы системы:**
- `Back.LTZone.Output`
- `Back.NegGenerator.Output`
- `Back.PosGenerator.Output`
- `Back.Soma1.ExcChannel.Output`
- `Back.Soma1.ExcSynapse1.Output`
- `Back.Soma1.InhChannel.Output`
- `Back.Soma1.InhSynapse1.Output`
- `Delay05To15.Output`
- `Forward.LTZone.Output`
- `Forward.NegGenerator.Output`
- ... (всего 190 выходов)

**Количество связей:** 224

---

## Cv

### ImageProcess

**Путь:** `Bin\Configs\!OldConfigs\Cv\ImageProcess`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **BStatisticSimple**: BStatisticSimple
- **BackgroundAvg**: Background
- **ColorConvert**: ColorConvert
- **DifferenceFrameSimple**: DifferenceFrameSimple
- **Reduce**: Reduce
- **TBinarizationSimple**: Binarization
- **TCaptureImageSequence**: Capture

**Входы системы:**
- `BStatisticSimple.Input`
- `Background.Input`
- `Binarization.Input`
- `ColorConvert.Input`
- `DifferenceFrameSimple.Input1`
- `DifferenceFrameSimple.Input2`
- `Reduce.Input`

**Выходы системы:**
- `Binarization.Output`
- `Capture.OutputImage`
- `ColorConvert.Output`
- `DifferenceFrameSimple.Output`
- `Reduce.Output`

**Количество связей:** 8

---

## Demcheva

### Cable Model

**Путь:** `Bin\Configs\Demcheva\Cable Model`

**Назначение:** Модель кабельного нейрона (компартментальная модель CSNM - Compartmental Spiking Neuron Model)

**Основные компоненты:**
- **CableModel**: CableModel

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuron

**Путь:** `Bin\Configs\Demcheva\CableNeuron`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPExcChannel**: PNeuron.Soma1.ExcChannel, PNeuron.ExcChannel
- **NPGenerator**: PGenerator
- **NPInhChannel**: PNeuron.Soma1.InhChannel, PNeuron.InhChannel, Soma1.InhChannel, InhChannel
- **NPLTExcChannel**: PNeuron.LTMembrane.ExcChannel, LTMembrane.ExcChannel
- **NPLTInhChannel**: PNeuron.LTMembrane.InhChannel, LTMembrane.InhChannel
- **NPLTZone**: PNeuron.LTZone
- **NPLTZoneNeuronMembrane**: PNeuron.LTMembrane, LTMembrane
- **NPMembrane**: PNeuron.Soma1
- **NPNeuron**: PNeuron
- **NPNeuronNegCGenerator**: PNeuron.NegGenerator
- **NPNeuronPosCGenerator**: PNeuron.PosGenerator, PosGenerator
- **NPNeuronPosCGeneratorCable**: CableNeuron.NegGenerator, NegGenerator
- **NPSynapse**: PNeuron.LTMembrane.ExcSynapse1, PNeuron.LTMembrane.InhSynapse1, PNeuron.Soma1.ExcSynapse1, PNeuron.Soma1.InhSynapse1, PNeuron.ExcSynapse1 (и еще 5)
- **NPulseChannelCable**: CableNeuron.Soma1.ExcChannel, CableNeuron.ExcChannel
- **NPulseChannelIaF**: IaFNeuron.Soma1.ExcChannel, IaFNeuron.ExcChannel, Soma1.ExcChannel, ExcChannel
- **NPulseLTZoneCable**: CableNeuron.LTZone
- **NPulseLTZoneIaF**: IaFNeuron.LTZone, LTZone
- **NPulseMembraneCable**: CableNeuron.Soma1
- **NPulseMembraneIaF**: IaFNeuron.Soma1, Soma1
- **NPulseNeuronCable**: CableNeuron
- **NPulseNeuronIaF**: IaFNeuron
- **NSynapseCable**: CableNeuron.Soma1.ExcSynapse1, CableNeuron.ExcSynapse1
- **NSynapseIaF**: IaFNeuron.Soma1.ExcSynapse1, IaFNeuron.ExcSynapse1, Soma1.ExcSynapse1, ExcSynapse1

**Входы системы:**
- `CableNeuron.LTZone.Inputs`
- `CableNeuron.NegGenerator`
- `CableNeuron.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron.Soma1.ExcSynapse1.Input`
- `CableNeuron.Soma1.InputFeedbackSignal`
- `IaFNeuron.LTZone.Inputs`
- `IaFNeuron.Soma1.ExcChannel.SynapticInputs`
- `IaFNeuron.Soma1.ExcSynapse1.Input`
- `IaFNeuron.Soma1.InputFeedbackSignal`
- ... (всего 26 входов)

**Выходы системы:**
- `CableNeuron.LTZone.Output`
- `CableNeuron.NegGenerator.Output`
- `CableNeuron.Soma1.ExcChannel.Output`
- `CableNeuron.Soma1.ExcSynapse1.Output`
- `IaFNeuron.LTZone.Output`
- `IaFNeuron.Soma1.ExcChannel.Output`
- `IaFNeuron.Soma1.ExcSynapse1.Output`
- `PGenerator.Output`
- `PNeuron.LTMembrane.ExcChannel.Output`
- `PNeuron.LTMembrane.ExcSynapse1.Output`
- ... (всего 19 выходов)

**Количество связей:** 21

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronClassic

**Путь:** `Bin\Configs\Demcheva\CableNeuronClassic`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPExcChannelBio**: PNeuron.Soma1.ExcChannel, PNeuron.ExcChannel, Soma1.ExcChannel, ExcChannel
- **NPGenerator**: PGenerator
- **NPInhChannelBio**: PNeuron.Soma1.InhChannel, PNeuron.InhChannel, Soma1.InhChannel, InhChannel
- **NPMembraneBio**: PNeuron.Soma1, Soma1
- **NPNeuronNegCGeneratorBio**: PNeuron.NegGenerator, NegGenerator
- **NPNeuronPosCGeneratorBio**: PNeuron.PosGenerator, PosGenerator
- **NPNeuronPosCGeneratorCable**: CableNeuron3.NegGenerator
- **NPSynapseBio**: PNeuron.Soma1.ExcSynapse1, PNeuron.Soma1.InhSynapse1, PNeuron.ExcSynapse1, PNeuron.InhSynapse1, Soma1.ExcSynapse1 (и еще 3)
- **NPulseChannelCable**: CableNeuron3.Soma1.ExcChannel, CableNeuron3.ExcChannel
- **NPulseChannelIaF**: IaFNeuron.Soma1.ExcChannel, IaFNeuron.ExcChannel
- **NPulseLTZoneCable**: CableNeuron3.LTZone
- **NPulseLTZoneIaF**: IaFNeuron.LTZone
- **NPulseLTZoneThresholdBio**: PNeuron.LTZone, LTZone
- **NPulseMembraneCable**: CableNeuron3.Soma1
- **NPulseMembraneIaF**: IaFNeuron.Soma1
- **NPulseNeuronCable**: CableNeuron3
- **NPulseNeuronIaF**: IaFNeuron
- **NSPNeuronBio**: PNeuron
- **NSynapseCable**: CableNeuron3.Soma1.ExcSynapse1, CableNeuron3.ExcSynapse1
- **NSynapseIaF**: IaFNeuron.Soma1.ExcSynapse1, IaFNeuron.ExcSynapse1

**Входы системы:**
- `CableNeuron3.LTZone.Inputs`
- `CableNeuron3.NegGenerator`
- `CableNeuron3.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron3.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron3.Soma1.ExcSynapse1.Input`
- `CableNeuron3.Soma1.InputFeedbackSignal`
- `IaFNeuron.LTZone.Inputs`
- `IaFNeuron.Soma1.ExcChannel.SynapticInputs`
- `IaFNeuron.Soma1.ExcSynapse1.Input`
- `IaFNeuron.Soma1.InputFeedbackSignal`
- ... (всего 22 входов)

**Выходы системы:**
- `CableNeuron3.LTZone.Output`
- `CableNeuron3.NegGenerator.Output`
- `CableNeuron3.Soma1.ExcChannel.Output`
- `CableNeuron3.Soma1.ExcSynapse1.Output`
- `IaFNeuron.LTZone.Output`
- `IaFNeuron.Soma1.ExcChannel.Output`
- `IaFNeuron.Soma1.ExcSynapse1.Output`
- `PGenerator.Output`
- `PNeuron.LTZone.Output`
- `PNeuron.NegGenerator.Output`
- ... (всего 15 выходов)

**Количество связей:** 17

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPExcChannelBio**: PNeuron.Soma1.ExcChannel, PNeuron.ExcChannel, PNeuron2.Soma1.ExcChannel, PNeuron2.ExcChannel, PNeuron3.Soma1.ExcChannel (и еще 1)
- **NPExcChannelBio2**: PNeuron4.Soma1.ExcChannel, PNeuron4.ExcChannel, Soma1.ExcChannel, ExcChannel
- **NPGenerator**: PGenerator
- **NPInhChannelBio**: PNeuron.Soma1.InhChannel, PNeuron.InhChannel, PNeuron2.Soma1.InhChannel, PNeuron2.InhChannel, PNeuron3.Soma1.InhChannel (и еще 1)
- **NPInhChannelBio2**: PNeuron4.Soma1.InhChannel, PNeuron4.InhChannel, Soma1.InhChannel, InhChannel
- **NPMembraneBio**: PNeuron.Soma1, PNeuron2.Soma1, PNeuron3.Soma1
- **NPMembraneBio2**: PNeuron4.Soma1, Soma1
- **NPNeuronNegCGenerator**: PNeuron3.NegGenerator
- **NPNeuronNegCGeneratorBio**: PNeuron.NegGenerator, PNeuron2.NegGenerator, PNeuron4.NegGenerator, NegGenerator
- **NPNeuronPosCGenerator**: PNeuron3.PosGenerator
- **NPNeuronPosCGeneratorBio**: PNeuron.PosGenerator, PNeuron2.PosGenerator, PNeuron4.PosGenerator, PosGenerator
- **NPNeuronPosCGeneratorCable**: CableNeuron3.NegGenerator, CableNeuron.NegGenerator
- **NPSynapseBio**: PNeuron.Soma1.ExcSynapse1, PNeuron.Soma1.InhSynapse1, PNeuron.ExcSynapse1, PNeuron.InhSynapse1, PNeuron2.Soma1.ExcSynapse1 (и еще 7)
- **NPSynapseBio2**: PNeuron4.Soma1.ExcSynapse1, PNeuron4.Soma1.InhSynapse1, PNeuron4.ExcSynapse1, PNeuron4.InhSynapse1, Soma1.ExcSynapse1 (и еще 3)
- **NPulseChannelCable**: CableNeuron3.Soma1.ExcChannel, CableNeuron3.ExcChannel
- **NPulseChannelCableMulti**: CableNeuron.Soma1.ExcChannel, CableNeuron.ExcChannel
- **NPulseChannelIaF**: IaFNeuron.Soma1.ExcChannel, IaFNeuron.ExcChannel
- **NPulseLTZoneCable**: CableNeuron3.LTZone, CableNeuron.LTZone
- **NPulseLTZoneIaF**: IaFNeuron.LTZone
- **NPulseLTZoneThreshold**: PNeuron3.LTZone
- **NPulseLTZoneThresholdBio**: PNeuron.LTZone, PNeuron2.LTZone
- **NPulseLTZoneThresholdBio2**: PNeuron4.LTZone, LTZone
- **NPulseMembraneCable**: CableNeuron3.Soma1
- **NPulseMembraneCableMulti**: CableNeuron.Soma1
- **NPulseMembraneIaF**: IaFNeuron.Soma1
- **NPulseNeuronCable**: CableNeuron3
- **NPulseNeuronCableMulti**: CableNeuron
- **NPulseNeuronIaF**: IaFNeuron
- **NSPNeuronBio**: PNeuron, PNeuron2
- **NSPNeuronBio2**: PNeuron4
- **NSPNeuronGen**: PNeuron3
- **NSynapseCable**: CableNeuron3.Soma1.ExcSynapse1, CableNeuron3.ExcSynapse1
- **NSynapseCableMulti**: CableNeuron.Soma1.ExcSynapse1, CableNeuron.ExcSynapse1
- **NSynapseIaF**: IaFNeuron.Soma1.ExcSynapse1, IaFNeuron.ExcSynapse1

**Входы системы:**
- `CableNeuron.LTZone.Inputs`
- `CableNeuron.NegGenerator`
- `CableNeuron.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron.Soma1.ExcSynapse1.Input`
- `CableNeuron.Soma1.InputFeedbackSignal`
- `CableNeuron3.LTZone.Inputs`
- `CableNeuron3.NegGenerator`
- `CableNeuron3.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron3.Soma1.ExcChannel.SynapticInputs`
- ... (всего 55 входов)

**Выходы системы:**
- `CableNeuron.LTZone.Output`
- `CableNeuron.NegGenerator.Output`
- `CableNeuron.Soma1.ExcChannel.Output`
- `CableNeuron.Soma1.ExcSynapse1.Output`
- `CableNeuron3.LTZone.Output`
- `CableNeuron3.NegGenerator.Output`
- `CableNeuron3.Soma1.ExcChannel.Output`
- `CableNeuron3.Soma1.ExcSynapse1.Output`
- `IaFNeuron.LTZone.Output`
- `IaFNeuron.Soma1.ExcChannel.Output`
- ... (всего 40 выходов)

**Количество связей:** 46

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti_CSNM

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti_CSNM`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPExcChannelBio**: PNeuron.Soma1.ExcChannel, PNeuron.ExcChannel, PNeuron2.Soma1.ExcChannel, PNeuron2.ExcChannel, Soma1.ExcChannel (и еще 1)
- **NPGenerator**: PGenerator
- **NPInhChannelBio**: PNeuron.Soma1.InhChannel, PNeuron.InhChannel, PNeuron2.Soma1.InhChannel, PNeuron2.InhChannel, Soma1.InhChannel (и еще 1)
- **NPMembraneBio**: PNeuron.Soma1, PNeuron2.Soma1, Soma1
- **NPNeuronNegCGenerator**: PNeuron2.NegGenerator, NegGenerator
- **NPNeuronNegCGeneratorBio**: PNeuron.NegGenerator
- **NPNeuronPosCGenerator**: PNeuron2.PosGenerator, PosGenerator
- **NPNeuronPosCGeneratorBio**: PNeuron.PosGenerator
- **NPNeuronPosCGeneratorCable**: CableNeuron.NegGenerator, CableNeuron2.NegGenerator, CableNeuron3.NegGenerator, CableNeuron4.NegGenerator, CableNeuron5.NegGenerator (и еще 3)
- **NPSynapseBio**: PNeuron.Soma1.ExcSynapse1, PNeuron.Soma1.InhSynapse1, PNeuron.ExcSynapse1, PNeuron.InhSynapse1, PNeuron2.Soma1.ExcSynapse1 (и еще 7)
- **NPulseChannelCableMulti**: CableNeuron.Soma1.ExcChannel, CableNeuron.Dendrite1_1.ExcChannel, CableNeuron.ExcChannel, CableNeuron2.Soma1.ExcChannel, CableNeuron2.Dendrite1_1.ExcChannel (и еще 28)
- **NPulseLTZoneCable**: CableNeuron.LTZone, CableNeuron2.LTZone, CableNeuron3.LTZone, CableNeuron4.LTZone, CableNeuron5.LTZone (и еще 3)
- **NPulseLTZoneThreshold**: PNeuron2.LTZone, LTZone
- **NPulseLTZoneThresholdBio**: PNeuron.LTZone
- **NPulseMembraneCableMulti**: CableNeuron.Soma1, CableNeuron.Dendrite1_1, CableNeuron2.Soma1, CableNeuron2.Dendrite1_1, CableNeuron2.Dendrite1_2 (и еще 20)
- **NPulseNeuronCableMulti**: CableNeuron, CableNeuron2, CableNeuron3, CableNeuron4, CableNeuron5 (и еще 3)
- **NSPNeuronBio**: PNeuron
- **NSPNeuronGen**: PNeuron2
- **NSynapseCableMulti**: CableNeuron.Soma1.ExcSynapse1, CableNeuron.Dendrite1_1.ExcSynapse1, CableNeuron.ExcSynapse1, CableNeuron2.Soma1.ExcSynapse1, CableNeuron2.Dendrite1_1.ExcSynapse1 (и еще 28)

**Входы системы:**
- `CableNeuron.Dendrite1_1.ExcChannel.ChannelInputs`
- `CableNeuron.Dendrite1_1.ExcChannel.SynapticInputs`
- `CableNeuron.Dendrite1_1.ExcSynapse1.Input`
- `CableNeuron.LTZone.Inputs`
- `CableNeuron.NegGenerator`
- `CableNeuron.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron.Soma1.InputFeedbackSignal`
- `CableNeuron2.Dendrite1_1.ExcChannel.ChannelInputs`
- `CableNeuron2.Dendrite1_1.ExcChannel.SynapticInputs`
- ... (всего 95 входов)

**Выходы системы:**
- `CableNeuron.Dendrite1_1.ExcChannel.Output`
- `CableNeuron.Dendrite1_1.ExcSynapse1.Output`
- `CableNeuron.LTZone.Output`
- `CableNeuron.NegGenerator.Output`
- `CableNeuron.Soma1.ExcChannel.Output`
- `CableNeuron.Soma1.ExcSynapse1.Output`
- `CableNeuron2.Dendrite1_1.ExcChannel.Output`
- `CableNeuron2.Dendrite1_1.ExcSynapse1.Output`
- `CableNeuron2.Dendrite1_2.ExcChannel.Output`
- `CableNeuron2.Dendrite1_2.ExcSynapse1.Output`
- ... (всего 73 выходов)

**Количество связей:** 82

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti_CSNM_Nd

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti_CSNM_Nd`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPExcChannelBio2**: PNeuron.Soma1.ExcChannel, PNeuron.ExcChannel, PNeuron2.Soma1.ExcChannel, PNeuron2.Dendrite1_1.ExcChannel, PNeuron2.ExcChannel (и еще 29)
- **NPGenerator**: PGenerator
- **NPInhChannelBio2**: PNeuron.Soma1.InhChannel, PNeuron.InhChannel, PNeuron2.Soma1.InhChannel, PNeuron2.Dendrite1_1.InhChannel, PNeuron2.InhChannel (и еще 29)
- **NPMembraneBio2**: PNeuron.Soma1, PNeuron2.Soma1, PNeuron2.Dendrite1_1, PNeuron3.Soma1, PNeuron3.Dendrite1_1 (и еще 22)
- **NPNeuronNegCGeneratorBio**: PNeuron.NegGenerator, PNeuron2.NegGenerator, PNeuron3.NegGenerator, PNeuron4.NegGenerator, PNeuron5.NegGenerator (и еще 2)
- **NPNeuronPosCGeneratorBio**: PNeuron.PosGenerator, PNeuron2.PosGenerator, PNeuron3.PosGenerator, PNeuron4.PosGenerator, PNeuron5.PosGenerator (и еще 2)
- **NPSynapseBio2**: PNeuron.Soma1.ExcSynapse1, PNeuron.Soma1.InhSynapse1, PNeuron.Soma1.ExcSynapse2, PNeuron.Soma1.ExcSynapse3, PNeuron.Soma1.ExcSynapse4 (и еще 329)
- **NPulseLTZoneThresholdBio2**: PNeuron.LTZone, PNeuron2.LTZone, PNeuron3.LTZone, PNeuron4.LTZone, PNeuron5.LTZone (и еще 2)
- **NSPNeuronBio2**: PNeuron, PNeuron2, PNeuron3, PNeuron4, PNeuron5 (и еще 1)

**Входы системы:**
- `NegGenerator`
- `PGenerator`
- `PNeuron.LTZone.Inputs`
- `PNeuron.NegGenerator`
- `PNeuron.PosGenerator`
- `PNeuron.Soma1.ExcChannel.ChannelInputs`
- `PNeuron.Soma1.ExcChannel.SynapticInputs`
- `PNeuron.Soma1.ExcSynapse1.Input`
- `PNeuron.Soma1.ExcSynapse10.Input`
- `PNeuron.Soma1.ExcSynapse11.Input`
- ... (всего 201 входов)

**Выходы системы:**
- `PGenerator.Output`
- `PNeuron.LTZone.Output`
- `PNeuron.NegGenerator.Output`
- `PNeuron.PosGenerator.Output`
- `PNeuron.Soma1.ExcChannel.Output`
- `PNeuron.Soma1.ExcSynapse1.Output`
- `PNeuron.Soma1.ExcSynapse10.Output`
- `PNeuron.Soma1.ExcSynapse11.Output`
- `PNeuron.Soma1.ExcSynapse12.Output`
- `PNeuron.Soma1.ExcSynapse13.Output`
- ... (всего 187 выходов)

**Количество связей:** 276

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti_CSNM_Nsyn

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti_CSNM_Nsyn`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPExcChannelBio2**: PNeuron.Soma1.ExcChannel, PNeuron.Dendrite1_1.ExcChannel, PNeuron.ExcChannel, PNeuron2.Soma1.ExcChannel, PNeuron2.Dendrite1_1.ExcChannel (и еще 13)
- **NPGenerator**: PGenerator
- **NPInhChannelBio2**: PNeuron.Soma1.InhChannel, PNeuron.Dendrite1_1.InhChannel, PNeuron.InhChannel, PNeuron2.Soma1.InhChannel, PNeuron2.Dendrite1_1.InhChannel (и еще 13)
- **NPMembraneBio2**: PNeuron.Soma1, PNeuron.Dendrite1_1, PNeuron2.Soma1, PNeuron2.Dendrite1_1, PNeuron3.Soma1 (и еще 7)
- **NPNeuronNegCGeneratorBio**: PNeuron.NegGenerator, PNeuron2.NegGenerator, PNeuron3.NegGenerator, PNeuron4.NegGenerator, PNeuron5.NegGenerator (и еще 1)
- **NPNeuronPosCGeneratorBio**: PNeuron.PosGenerator, PNeuron2.PosGenerator, PNeuron3.PosGenerator, PNeuron4.PosGenerator, PNeuron5.PosGenerator (и еще 1)
- **NPSynapseBio2**: PNeuron.Soma1.ExcSynapse1, PNeuron.Soma1.InhSynapse1, PNeuron.Dendrite1_1.ExcSynapse1, PNeuron.Dendrite1_1.InhSynapse1, PNeuron.ExcSynapse1 (и еще 59)
- **NPulseLTZoneThresholdBio2**: PNeuron.LTZone, PNeuron2.LTZone, PNeuron3.LTZone, PNeuron4.LTZone, PNeuron5.LTZone (и еще 1)
- **NSPNeuronBio2**: PNeuron, PNeuron2, PNeuron3, PNeuron4, PNeuron5

**Входы системы:**
- `NegGenerator`
- `PGenerator`
- `PNeuron.Dendrite1_1.ExcChannel.ChannelInputs`
- `PNeuron.Dendrite1_1.ExcChannel.SynapticInputs`
- `PNeuron.Dendrite1_1.ExcSynapse1.Input`
- `PNeuron.Dendrite1_1.InhChannel.ChannelInputs`
- `PNeuron.Dendrite1_1.InhChannel.SynapticInputs`
- `PNeuron.LTZone.Inputs`
- `PNeuron.NegGenerator`
- `PNeuron.PosGenerator`
- ... (всего 78 входов)

**Выходы системы:**
- `PGenerator.Output`
- `PNeuron.Dendrite1_1.ExcChannel.Output`
- `PNeuron.Dendrite1_1.ExcSynapse1.Output`
- `PNeuron.Dendrite1_1.InhChannel.Output`
- `PNeuron.Dendrite1_1.InhSynapse1.Output`
- `PNeuron.LTZone.Output`
- `PNeuron.NegGenerator.Output`
- `PNeuron.PosGenerator.Output`
- `PNeuron.Soma1.ExcChannel.Output`
- `PNeuron.Soma1.ExcSynapse1.Output`
- ... (всего 66 выходов)

**Количество связей:** 80

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti_CSNM_ver95

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti_CSNM_ver95`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPGenerator**: PGenerator
- **NPNeuronPosCGeneratorCable**: CableNeuron2.NegGenerator, NegGenerator
- **NPulseChannelCableMulti**: CableNeuron2.Soma1.ExcChannel, CableNeuron2.Soma2.ExcChannel, CableNeuron2.Soma3.ExcChannel, CableNeuron2.Soma4.ExcChannel, CableNeuron2.Soma5.ExcChannel (и еще 11)
- **NPulseLTZoneCable**: CableNeuron2.LTZone, LTZone
- **NPulseMembraneCableMulti**: CableNeuron2.Soma1, CableNeuron2.Soma2, CableNeuron2.Soma3, CableNeuron2.Soma4, CableNeuron2.Soma5 (и еще 9)
- **NPulseNeuronCableMulti**: CableNeuron2
- **NSynapseCableMulti**: CableNeuron2.Soma1.ExcSynapse1, CableNeuron2.Soma2.ExcSynapse1, CableNeuron2.Soma3.ExcSynapse1, CableNeuron2.Soma4.ExcSynapse1, CableNeuron2.Soma5.ExcSynapse1 (и еще 11)

**Входы системы:**
- `CableNeuron2.LTZone.Inputs`
- `CableNeuron2.NegGenerator`
- `CableNeuron2.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron2.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron2.Soma1.ExcSynapse1.Input`
- `CableNeuron2.Soma1.InputFeedbackSignal`
- `CableNeuron2.Soma2.ExcChannel.ChannelInputs`
- `CableNeuron2.Soma2.ExcChannel.SynapticInputs`
- `CableNeuron2.Soma2.InputFeedbackSignal`
- `CableNeuron2.Soma3.ExcChannel.ChannelInputs`
- ... (всего 26 входов)

**Выходы системы:**
- `CableNeuron2.LTZone.Output`
- `CableNeuron2.NegGenerator.Output`
- `CableNeuron2.Soma1.ExcChannel.Output`
- `CableNeuron2.Soma1.ExcSynapse1.Output`
- `CableNeuron2.Soma2.ExcChannel.Output`
- `CableNeuron2.Soma2.ExcSynapse1.Output`
- `CableNeuron2.Soma3.ExcChannel.Output`
- `CableNeuron2.Soma3.ExcSynapse1.Output`
- `CableNeuron2.Soma4.ExcChannel.Output`
- `CableNeuron2.Soma4.ExcSynapse1.Output`
- ... (всего 17 выходов)

**Количество связей:** 29

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti_Diameters

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti_Diameters`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPExcChannelBio**: PNeuron.Soma1.ExcChannel, PNeuron.ExcChannel
- **NPGenerator**: PGenerator
- **NPInhChannelBio**: PNeuron.Soma1.InhChannel, PNeuron.InhChannel, Soma1.InhChannel, InhChannel
- **NPMembraneBio**: PNeuron.Soma1
- **NPNeuronNegCGeneratorBio**: PNeuron.NegGenerator
- **NPNeuronPosCGeneratorBio**: PNeuron.PosGenerator, PosGenerator
- **NPNeuronPosCGeneratorCable**: CableNeuron.NegGenerator, CableNeuron2.NegGenerator, CableNeuron3.NegGenerator, CableNeuron4.NegGenerator, CableNeuron5.NegGenerator (и еще 3)
- **NPSynapseBio**: PNeuron.Soma1.ExcSynapse1, PNeuron.Soma1.InhSynapse1, PNeuron.ExcSynapse1, PNeuron.InhSynapse1, Soma1.InhSynapse1 (и еще 1)
- **NPulseChannelCableMulti**: CableNeuron.Soma1.ExcChannel, CableNeuron.ExcChannel, CableNeuron2.Soma1.ExcChannel, CableNeuron2.ExcChannel, CableNeuron3.Soma1.ExcChannel (и еще 11)
- **NPulseChannelIaF**: IaFNeuron.Soma1.ExcChannel, IaFNeuron.ExcChannel
- **NPulseLTZoneCable**: CableNeuron.LTZone, CableNeuron2.LTZone, CableNeuron3.LTZone, CableNeuron4.LTZone, CableNeuron5.LTZone (и еще 3)
- **NPulseLTZoneIaF**: IaFNeuron.LTZone
- **NPulseLTZoneThresholdBio**: PNeuron.LTZone
- **NPulseMembraneCableMulti**: CableNeuron.Soma1, CableNeuron2.Soma1, CableNeuron3.Soma1, CableNeuron4.Soma1, CableNeuron5.Soma1 (и еще 3)
- **NPulseMembraneIaF**: IaFNeuron.Soma1
- **NPulseNeuronCableMulti**: CableNeuron, CableNeuron2, CableNeuron3, CableNeuron4, CableNeuron5 (и еще 2)
- **NPulseNeuronIaF**: IaFNeuron
- **NSPNeuronBio**: PNeuron
- **NSynapseCableMulti**: CableNeuron.Soma1.ExcSynapse1, CableNeuron.ExcSynapse1, CableNeuron2.Soma1.ExcSynapse1, CableNeuron2.ExcSynapse1, CableNeuron3.Soma1.ExcSynapse1 (и еще 11)
- **NSynapseIaF**: IaFNeuron.Soma1.ExcSynapse1, IaFNeuron.ExcSynapse1

**Входы системы:**
- `CableNeuron.LTZone.Inputs`
- `CableNeuron.NegGenerator`
- `CableNeuron.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron.Soma1.ExcSynapse1.Input`
- `CableNeuron.Soma1.InputFeedbackSignal`
- `CableNeuron2.LTZone.Inputs`
- `CableNeuron2.NegGenerator`
- `CableNeuron2.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron2.Soma1.ExcChannel.SynapticInputs`
- ... (всего 58 входов)

**Выходы системы:**
- `CableNeuron.LTZone.Output`
- `CableNeuron.NegGenerator.Output`
- `CableNeuron.Soma1.ExcChannel.Output`
- `CableNeuron.Soma1.ExcSynapse1.Output`
- `CableNeuron2.LTZone.Output`
- `CableNeuron2.NegGenerator.Output`
- `CableNeuron2.Soma1.ExcChannel.Output`
- `CableNeuron2.Soma1.ExcSynapse1.Output`
- `CableNeuron3.LTZone.Output`
- `CableNeuron3.NegGenerator.Output`
- ... (всего 39 выходов)

**Количество связей:** 47

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti_Diameters_ver101

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti_Diameters_ver101`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPGenerator**: PGenerator
- **NPNeuronPosCGeneratorCable**: CableNeuron.NegGenerator, CableNeuron2.NegGenerator, CableNeuron3.NegGenerator, CableNeuron4.NegGenerator, CableNeuron5.NegGenerator (и еще 6)
- **NPulseChannelCableMulti**: CableNeuron.Soma1.ExcChannel, CableNeuron.ExcChannel, CableNeuron2.Soma1.ExcChannel, CableNeuron2.ExcChannel, CableNeuron3.Soma1.ExcChannel (и еще 17)
- **NPulseLTZoneCable**: CableNeuron.LTZone, CableNeuron2.LTZone, CableNeuron3.LTZone, CableNeuron4.LTZone, CableNeuron5.LTZone (и еще 6)
- **NPulseMembraneCableMulti**: CableNeuron.Soma1, CableNeuron2.Soma1, CableNeuron3.Soma1, CableNeuron4.Soma1, CableNeuron5.Soma1 (и еще 6)
- **NPulseNeuronCableMulti**: CableNeuron, CableNeuron2, CableNeuron3, CableNeuron4, CableNeuron5 (и еще 5)
- **NSynapseCableMulti**: CableNeuron.Soma1.ExcSynapse1, CableNeuron.ExcSynapse1, CableNeuron2.Soma1.ExcSynapse1, CableNeuron2.ExcSynapse1, CableNeuron3.Soma1.ExcSynapse1 (и еще 17)

**Входы системы:**
- `CableNeuron.LTZone.Inputs`
- `CableNeuron.NegGenerator`
- `CableNeuron.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron.Soma1.ExcSynapse1.Input`
- `CableNeuron.Soma1.InputFeedbackSignal`
- `CableNeuron10.LTZone.Inputs`
- `CableNeuron10.NegGenerator`
- `CableNeuron10.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron10.Soma1.ExcChannel.SynapticInputs`
- ... (всего 62 входов)

**Выходы системы:**
- `CableNeuron.LTZone.Output`
- `CableNeuron.NegGenerator.Output`
- `CableNeuron.Soma1.ExcChannel.Output`
- `CableNeuron.Soma1.ExcSynapse1.Output`
- `CableNeuron10.LTZone.Output`
- `CableNeuron10.NegGenerator.Output`
- `CableNeuron10.Soma1.ExcChannel.Output`
- `CableNeuron10.Soma1.ExcSynapse1.Output`
- `CableNeuron2.LTZone.Output`
- `CableNeuron2.NegGenerator.Output`
- ... (всего 41 выходов)

**Количество связей:** 50

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti_Diameters_ver93

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti_Diameters_ver93`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPGenerator**: PGenerator
- **NPNeuronPosCGeneratorCable**: CableNeuron.NegGenerator, NegGenerator
- **NPulseChannelCableMulti**: CableNeuron.Soma1.ExcChannel, CableNeuron.ExcChannel, Soma1.ExcChannel, ExcChannel
- **NPulseLTZoneCable**: CableNeuron.LTZone, LTZone
- **NPulseMembraneCableMulti**: CableNeuron.Soma1, Soma1
- **NPulseNeuronCableMulti**: CableNeuron
- **NSynapseCableMulti**: CableNeuron.Soma1.ExcSynapse1, CableNeuron.ExcSynapse1, Soma1.ExcSynapse1, ExcSynapse1

**Входы системы:**
- `CableNeuron.LTZone.Inputs`
- `CableNeuron.NegGenerator`
- `CableNeuron.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron.Soma1.ExcSynapse1.Input`
- `CableNeuron.Soma1.InputFeedbackSignal`
- `NegGenerator`
- `PGenerator`

**Выходы системы:**
- `CableNeuron.LTZone.Output`
- `CableNeuron.NegGenerator.Output`
- `CableNeuron.Soma1.ExcChannel.Output`
- `CableNeuron.Soma1.ExcSynapse1.Output`
- `PGenerator.Output`

**Количество связей:** 5

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti_Diameters_ver94

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti_Diameters_ver94`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPGenerator**: PGenerator
- **NPNeuronPosCGeneratorCable**: CableNeuron.NegGenerator, NegGenerator
- **NPulseChannelCableMulti**: CableNeuron.Soma1.ExcChannel, CableNeuron.ExcChannel, Soma1.ExcChannel, ExcChannel
- **NPulseLTZoneCable**: CableNeuron.LTZone, LTZone
- **NPulseMembraneCableMulti**: CableNeuron.Soma1, Soma1
- **NPulseNeuronCableMulti**: CableNeuron
- **NSynapseCableMulti**: CableNeuron.Soma1.ExcSynapse1, CableNeuron.ExcSynapse1, Soma1.ExcSynapse1, ExcSynapse1

**Входы системы:**
- `CableNeuron.LTZone.Inputs`
- `CableNeuron.NegGenerator`
- `CableNeuron.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron.Soma1.ExcSynapse1.Input`
- `CableNeuron.Soma1.InputFeedbackSignal`
- `NegGenerator`
- `PGenerator`

**Выходы системы:**
- `CableNeuron.LTZone.Output`
- `CableNeuron.NegGenerator.Output`
- `CableNeuron.Soma1.ExcChannel.Output`
- `CableNeuron.Soma1.ExcSynapse1.Output`
- `PGenerator.Output`

**Количество связей:** 5

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti_Diameters_ver95

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti_Diameters_ver95`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPGenerator**: PGenerator
- **NPNeuronPosCGeneratorCable**: CableNeuron.NegGenerator, CableNeuron2.NegGenerator, CableNeuron3.NegGenerator, CableNeuron4.NegGenerator, CableNeuron5.NegGenerator (и еще 9)
- **NPulseChannelCableMulti**: CableNeuron.Soma1.ExcChannel, CableNeuron.ExcChannel, CableNeuron2.Soma1.ExcChannel, CableNeuron2.ExcChannel, CableNeuron3.Soma1.ExcChannel (и еще 23)
- **NPulseLTZoneCable**: CableNeuron.LTZone, CableNeuron2.LTZone, CableNeuron3.LTZone, CableNeuron4.LTZone, CableNeuron5.LTZone (и еще 9)
- **NPulseMembraneCableMulti**: CableNeuron.Soma1, CableNeuron2.Soma1, CableNeuron3.Soma1, CableNeuron4.Soma1, CableNeuron5.Soma1 (и еще 9)
- **NPulseNeuronCableMulti**: CableNeuron, CableNeuron2, CableNeuron3, CableNeuron4, CableNeuron5 (и еще 8)
- **NSynapseCableMulti**: CableNeuron.Soma1.ExcSynapse1, CableNeuron.ExcSynapse1, CableNeuron2.Soma1.ExcSynapse1, CableNeuron2.ExcSynapse1, CableNeuron3.Soma1.ExcSynapse1 (и еще 23)

**Входы системы:**
- `CableNeuron.LTZone.Inputs`
- `CableNeuron.NegGenerator`
- `CableNeuron.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron.Soma1.ExcSynapse1.Input`
- `CableNeuron.Soma1.InputFeedbackSignal`
- `CableNeuron10.LTZone.Inputs`
- `CableNeuron10.NegGenerator`
- `CableNeuron10.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron10.Soma1.ExcChannel.SynapticInputs`
- ... (всего 80 входов)

**Выходы системы:**
- `CableNeuron.LTZone.Output`
- `CableNeuron.NegGenerator.Output`
- `CableNeuron.Soma1.ExcChannel.Output`
- `CableNeuron.Soma1.ExcSynapse1.Output`
- `CableNeuron10.LTZone.Output`
- `CableNeuron10.NegGenerator.Output`
- `CableNeuron10.Soma1.ExcChannel.Output`
- `CableNeuron10.Soma1.ExcSynapse1.Output`
- `CableNeuron11.LTZone.Output`
- `CableNeuron11.NegGenerator.Output`
- ... (всего 53 выходов)

**Количество связей:** 65

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti_II_Diameters

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti_II_Diameters`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPGenerator**: PGenerator
- **NPNeuronPosCGeneratorCable**: CableNeuron.NegGenerator, CableNeuron2.NegGenerator, CableNeuron3.NegGenerator, CableNeuron4.NegGenerator, CableNeuron5.NegGenerator (и еще 8)
- **NPulseChannelCableMulti**: CableNeuron.Soma1.ExcChannel, CableNeuron.ExcChannel, CableNeuron2.Soma1.ExcChannel, CableNeuron2.ExcChannel, CableNeuron3.Soma1.ExcChannel (и еще 21)
- **NPulseLTZoneCable**: CableNeuron.LTZone, CableNeuron2.LTZone, CableNeuron3.LTZone, CableNeuron4.LTZone, CableNeuron5.LTZone (и еще 8)
- **NPulseMembraneCableMulti**: CableNeuron.Soma1, CableNeuron2.Soma1, CableNeuron3.Soma1, CableNeuron4.Soma1, CableNeuron5.Soma1 (и еще 8)
- **NPulseNeuronCableMulti**: CableNeuron, CableNeuron2, CableNeuron3, CableNeuron4, CableNeuron5 (и еще 7)
- **NSynapseCableMulti**: CableNeuron.Soma1.ExcSynapse1, CableNeuron.ExcSynapse1, CableNeuron2.Soma1.ExcSynapse1, CableNeuron2.ExcSynapse1, CableNeuron3.Soma1.ExcSynapse1 (и еще 21)

**Входы системы:**
- `CableNeuron.LTZone.Inputs`
- `CableNeuron.NegGenerator`
- `CableNeuron.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron.Soma1.ExcSynapse1.Input`
- `CableNeuron.Soma1.InputFeedbackSignal`
- `CableNeuron10.LTZone.Inputs`
- `CableNeuron10.NegGenerator`
- `CableNeuron10.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron10.Soma1.ExcChannel.SynapticInputs`
- ... (всего 74 входов)

**Выходы системы:**
- `CableNeuron.LTZone.Output`
- `CableNeuron.NegGenerator.Output`
- `CableNeuron.Soma1.ExcChannel.Output`
- `CableNeuron.Soma1.ExcSynapse1.Output`
- `CableNeuron10.LTZone.Output`
- `CableNeuron10.NegGenerator.Output`
- `CableNeuron10.Soma1.ExcChannel.Output`
- `CableNeuron10.Soma1.ExcSynapse1.Output`
- `CableNeuron11.LTZone.Output`
- `CableNeuron11.NegGenerator.Output`
- ... (всего 49 выходов)

**Количество связей:** 60

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti_II_Lengths

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti_II_Lengths`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPGenerator**: PGenerator
- **NPNeuronPosCGeneratorCable**: CableNeuron.NegGenerator, CableNeuron2.NegGenerator, CableNeuron3.NegGenerator, CableNeuron4.NegGenerator, CableNeuron5.NegGenerator (и еще 5)
- **NPulseChannelCableMulti**: CableNeuron.Soma1.ExcChannel, CableNeuron.ExcChannel, CableNeuron2.Soma1.ExcChannel, CableNeuron2.ExcChannel, CableNeuron3.Soma1.ExcChannel (и еще 15)
- **NPulseLTZoneCable**: CableNeuron.LTZone, CableNeuron2.LTZone, CableNeuron3.LTZone, CableNeuron4.LTZone, CableNeuron5.LTZone (и еще 5)
- **NPulseMembraneCableMulti**: CableNeuron.Soma1, CableNeuron2.Soma1, CableNeuron3.Soma1, CableNeuron4.Soma1, CableNeuron5.Soma1 (и еще 5)
- **NPulseNeuronCableMulti**: CableNeuron, CableNeuron2, CableNeuron3, CableNeuron4, CableNeuron5 (и еще 4)
- **NSynapseCableMulti**: CableNeuron.Soma1.ExcSynapse1, CableNeuron.ExcSynapse1, CableNeuron2.Soma1.ExcSynapse1, CableNeuron2.ExcSynapse1, CableNeuron3.Soma1.ExcSynapse1 (и еще 15)

**Входы системы:**
- `CableNeuron.LTZone.Inputs`
- `CableNeuron.NegGenerator`
- `CableNeuron.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron.Soma1.ExcSynapse1.Input`
- `CableNeuron.Soma1.InputFeedbackSignal`
- `CableNeuron2.LTZone.Inputs`
- `CableNeuron2.NegGenerator`
- `CableNeuron2.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron2.Soma1.ExcChannel.SynapticInputs`
- ... (всего 56 входов)

**Выходы системы:**
- `CableNeuron.LTZone.Output`
- `CableNeuron.NegGenerator.Output`
- `CableNeuron.Soma1.ExcChannel.Output`
- `CableNeuron.Soma1.ExcSynapse1.Output`
- `CableNeuron2.LTZone.Output`
- `CableNeuron2.NegGenerator.Output`
- `CableNeuron2.Soma1.ExcChannel.Output`
- `CableNeuron2.Soma1.ExcSynapse1.Output`
- `CableNeuron3.LTZone.Output`
- `CableNeuron3.NegGenerator.Output`
- ... (всего 37 выходов)

**Количество связей:** 45

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti_Lenghts_ver101

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti_Lenghts_ver101`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPGenerator**: PGenerator
- **NPNeuronPosCGeneratorCable**: CableNeuron.NegGenerator, CableNeuron2.NegGenerator, CableNeuron3.NegGenerator, CableNeuron4.NegGenerator, CableNeuron5.NegGenerator (и еще 6)
- **NPulseChannelCableMulti**: CableNeuron.Soma1.ExcChannel, CableNeuron.ExcChannel, CableNeuron2.Soma1.ExcChannel, CableNeuron2.ExcChannel, CableNeuron3.Soma1.ExcChannel (и еще 17)
- **NPulseLTZoneCable**: CableNeuron.LTZone, CableNeuron2.LTZone, CableNeuron3.LTZone, CableNeuron4.LTZone, CableNeuron5.LTZone (и еще 6)
- **NPulseMembraneCableMulti**: CableNeuron.Soma1, CableNeuron2.Soma1, CableNeuron3.Soma1, CableNeuron4.Soma1, CableNeuron5.Soma1 (и еще 6)
- **NPulseNeuronCableMulti**: CableNeuron, CableNeuron2, CableNeuron3, CableNeuron4, CableNeuron5 (и еще 5)
- **NSynapseCableMulti**: CableNeuron.Soma1.ExcSynapse1, CableNeuron.ExcSynapse1, CableNeuron2.Soma1.ExcSynapse1, CableNeuron2.ExcSynapse1, CableNeuron3.Soma1.ExcSynapse1 (и еще 17)

**Входы системы:**
- `CableNeuron.LTZone.Inputs`
- `CableNeuron.NegGenerator`
- `CableNeuron.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron.Soma1.ExcSynapse1.Input`
- `CableNeuron.Soma1.InputFeedbackSignal`
- `CableNeuron10.LTZone.Inputs`
- `CableNeuron10.NegGenerator`
- `CableNeuron10.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron10.Soma1.ExcChannel.SynapticInputs`
- ... (всего 62 входов)

**Выходы системы:**
- `CableNeuron.LTZone.Output`
- `CableNeuron.NegGenerator.Output`
- `CableNeuron.Soma1.ExcChannel.Output`
- `CableNeuron.Soma1.ExcSynapse1.Output`
- `CableNeuron10.LTZone.Output`
- `CableNeuron10.NegGenerator.Output`
- `CableNeuron10.Soma1.ExcChannel.Output`
- `CableNeuron10.Soma1.ExcSynapse1.Output`
- `CableNeuron2.LTZone.Output`
- `CableNeuron2.NegGenerator.Output`
- ... (всего 41 выходов)

**Количество связей:** 50

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti_Lenghts_ver95

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti_Lenghts_ver95`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPGenerator**: PGenerator
- **NPNeuronPosCGeneratorCable**: CableNeuron.NegGenerator, CableNeuron2.NegGenerator, CableNeuron3.NegGenerator, CableNeuron4.NegGenerator, CableNeuron5.NegGenerator (и еще 10)
- **NPulseChannelCableMulti**: CableNeuron.Soma1.ExcChannel, CableNeuron.ExcChannel, CableNeuron2.Soma1.ExcChannel, CableNeuron2.ExcChannel, CableNeuron3.Soma1.ExcChannel (и еще 25)
- **NPulseLTZoneCable**: CableNeuron.LTZone, CableNeuron2.LTZone, CableNeuron3.LTZone, CableNeuron4.LTZone, CableNeuron5.LTZone (и еще 10)
- **NPulseMembraneCableMulti**: CableNeuron.Soma1, CableNeuron2.Soma1, CableNeuron3.Soma1, CableNeuron4.Soma1, CableNeuron5.Soma1 (и еще 10)
- **NPulseNeuronCableMulti**: CableNeuron, CableNeuron2, CableNeuron3, CableNeuron4, CableNeuron5 (и еще 9)
- **NSynapseCableMulti**: CableNeuron.Soma1.ExcSynapse1, CableNeuron.ExcSynapse1, CableNeuron2.Soma1.ExcSynapse1, CableNeuron2.ExcSynapse1, CableNeuron3.Soma1.ExcSynapse1 (и еще 25)

**Входы системы:**
- `CableNeuron.LTZone.Inputs`
- `CableNeuron.NegGenerator`
- `CableNeuron.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron.Soma1.ExcSynapse1.Input`
- `CableNeuron.Soma1.InputFeedbackSignal`
- `CableNeuron10.LTZone.Inputs`
- `CableNeuron10.NegGenerator`
- `CableNeuron10.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron10.Soma1.ExcChannel.SynapticInputs`
- ... (всего 86 входов)

**Выходы системы:**
- `CableNeuron.LTZone.Output`
- `CableNeuron.NegGenerator.Output`
- `CableNeuron.Soma1.ExcChannel.Output`
- `CableNeuron.Soma1.ExcSynapse1.Output`
- `CableNeuron10.LTZone.Output`
- `CableNeuron10.NegGenerator.Output`
- `CableNeuron10.Soma1.ExcChannel.Output`
- `CableNeuron10.Soma1.ExcSynapse1.Output`
- `CableNeuron11.LTZone.Output`
- `CableNeuron11.NegGenerator.Output`
- ... (всего 57 выходов)

**Количество связей:** 70

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti_Lengths

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti_Lengths`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPExcChannelBio**: PNeuron.Soma1.ExcChannel, PNeuron.ExcChannel
- **NPGenerator**: PGenerator
- **NPInhChannelBio**: PNeuron.Soma1.InhChannel, PNeuron.InhChannel, Soma1.InhChannel, InhChannel
- **NPMembraneBio**: PNeuron.Soma1
- **NPNeuronNegCGeneratorBio**: PNeuron.NegGenerator
- **NPNeuronPosCGeneratorBio**: PNeuron.PosGenerator, PosGenerator
- **NPNeuronPosCGeneratorCable**: CableNeuron3.NegGenerator, CableNeuron.NegGenerator, CableNeuron2.NegGenerator, CableNeuron4.NegGenerator, CableNeuron5.NegGenerator (и еще 6)
- **NPSynapseBio**: PNeuron.Soma1.ExcSynapse1, PNeuron.Soma1.InhSynapse1, PNeuron.ExcSynapse1, PNeuron.InhSynapse1, Soma1.InhSynapse1 (и еще 1)
- **NPulseChannelCable**: CableNeuron3.Soma1.ExcChannel, CableNeuron3.ExcChannel
- **NPulseChannelCableMulti**: CableNeuron.Soma1.ExcChannel, CableNeuron.ExcChannel, CableNeuron2.Soma1.ExcChannel, CableNeuron2.ExcChannel, CableNeuron4.Soma1.ExcChannel (и еще 15)
- **NPulseChannelIaF**: IaFNeuron.Soma1.ExcChannel, IaFNeuron.ExcChannel
- **NPulseLTZoneCable**: CableNeuron3.LTZone, CableNeuron.LTZone, CableNeuron2.LTZone, CableNeuron4.LTZone, CableNeuron5.LTZone (и еще 6)
- **NPulseLTZoneIaF**: IaFNeuron.LTZone
- **NPulseLTZoneThresholdBio**: PNeuron.LTZone
- **NPulseMembraneCable**: CableNeuron3.Soma1
- **NPulseMembraneCableMulti**: CableNeuron.Soma1, CableNeuron2.Soma1, CableNeuron4.Soma1, CableNeuron5.Soma1, CableNeuron6.Soma1 (и еще 5)
- **NPulseMembraneIaF**: IaFNeuron.Soma1
- **NPulseNeuronCable**: CableNeuron3
- **NPulseNeuronCableMulti**: CableNeuron, CableNeuron2, CableNeuron4, CableNeuron5, CableNeuron6 (и еще 4)
- **NPulseNeuronIaF**: IaFNeuron
- **NSPNeuronBio**: PNeuron
- **NSynapseCable**: CableNeuron3.Soma1.ExcSynapse1, CableNeuron3.ExcSynapse1
- **NSynapseCableMulti**: CableNeuron.Soma1.ExcSynapse1, CableNeuron.ExcSynapse1, CableNeuron2.Soma1.ExcSynapse1, CableNeuron2.ExcSynapse1, CableNeuron4.Soma1.ExcSynapse1 (и еще 15)
- **NSynapseIaF**: IaFNeuron.Soma1.ExcSynapse1, IaFNeuron.ExcSynapse1

**Входы системы:**
- `CableNeuron.LTZone.Inputs`
- `CableNeuron.NegGenerator`
- `CableNeuron.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron.Soma1.ExcSynapse1.Input`
- `CableNeuron.Soma1.InputFeedbackSignal`
- `CableNeuron10.LTZone.Inputs`
- `CableNeuron10.NegGenerator`
- `CableNeuron10.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron10.Soma1.ExcChannel.SynapticInputs`
- ... (всего 76 входов)

**Выходы системы:**
- `CableNeuron.LTZone.Output`
- `CableNeuron.NegGenerator.Output`
- `CableNeuron.Soma1.ExcChannel.Output`
- `CableNeuron.Soma1.ExcSynapse1.Output`
- `CableNeuron10.LTZone.Output`
- `CableNeuron10.NegGenerator.Output`
- `CableNeuron10.Soma1.ExcChannel.Output`
- `CableNeuron10.Soma1.ExcSynapse1.Output`
- `CableNeuron2.LTZone.Output`
- `CableNeuron2.NegGenerator.Output`
- ... (всего 51 выходов)

**Количество связей:** 62

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti_Lengths_ver93

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti_Lengths_ver93`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPGenerator**: PGenerator
- **NPNeuronPosCGeneratorCable**: CableNeuron.NegGenerator, NegGenerator
- **NPulseChannelCableMulti**: CableNeuron.Soma1.ExcChannel, CableNeuron.ExcChannel, Soma1.ExcChannel, ExcChannel
- **NPulseLTZoneCable**: CableNeuron.LTZone, LTZone
- **NPulseMembraneCableMulti**: CableNeuron.Soma1, Soma1
- **NPulseNeuronCableMulti**: CableNeuron
- **NSynapseCableMulti**: CableNeuron.Soma1.ExcSynapse1, CableNeuron.ExcSynapse1, Soma1.ExcSynapse1, ExcSynapse1

**Входы системы:**
- `CableNeuron.LTZone.Inputs`
- `CableNeuron.NegGenerator`
- `CableNeuron.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron.Soma1.ExcSynapse1.Input`
- `CableNeuron.Soma1.InputFeedbackSignal`
- `NegGenerator`
- `PGenerator`

**Выходы системы:**
- `CableNeuron.LTZone.Output`
- `CableNeuron.NegGenerator.Output`
- `CableNeuron.Soma1.ExcChannel.Output`
- `CableNeuron.Soma1.ExcSynapse1.Output`
- `PGenerator.Output`

**Количество связей:** 5

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti_Lengths_ver94

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti_Lengths_ver94`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NLogicalNot**: StatePredictor.LogicalNot, LogicalNot
- **NNeuronTrainer**: StatePredictor.InputNeuron1, StatePredictor.InputNeuron2, StatePredictor.InputNeuron3, StatePredictor.InputNeuron4, StatePredictor.OutputNeuron (и еще 9)
- **NPExcChannelBio**: StatePredictor.InputNeuron1.Neuron.Soma1.ExcChannel, StatePredictor.InputNeuron1.Neuron.Dendrite1_1.ExcChannel, StatePredictor.InputNeuron1.Neuron.Soma2.ExcChannel, StatePredictor.InputNeuron1.Neuron.Dendrite2_1.ExcChannel, StatePredictor.InputNeuron1.Neuron.Soma3.ExcChannel (и еще 1779)
- **NPGenerator**: PGenerator
- **NPInhChannelBio**: StatePredictor.InputNeuron1.Neuron.Soma1.InhChannel, StatePredictor.InputNeuron1.Neuron.Dendrite1_1.InhChannel, StatePredictor.InputNeuron1.Neuron.Soma2.InhChannel, StatePredictor.InputNeuron1.Neuron.Dendrite2_1.InhChannel, StatePredictor.InputNeuron1.Neuron.Soma3.InhChannel (и еще 1779)
- **NPMembraneBio**: StatePredictor.InputNeuron1.Neuron.Soma1, StatePredictor.InputNeuron1.Neuron.Dendrite1_1, StatePredictor.InputNeuron1.Neuron.Soma2, StatePredictor.InputNeuron1.Neuron.Dendrite2_1, StatePredictor.InputNeuron1.Neuron.Soma3 (и еще 1735)
- **NPNeuronNegCGenerator**: StatePredictor.InputNeuron1.Neuron.NegGenerator, StatePredictor.InputNeuron1.NegGenerator, StatePredictor.InputNeuron2.Neuron.NegGenerator, StatePredictor.InputNeuron2.NegGenerator, StatePredictor.InputNeuron3.Neuron.NegGenerator (и еще 39)
- **NPNeuronPosCGenerator**: StatePredictor.InputNeuron1.Neuron.PosGenerator, StatePredictor.InputNeuron1.PosGenerator, StatePredictor.InputNeuron2.Neuron.PosGenerator, StatePredictor.InputNeuron2.PosGenerator, StatePredictor.InputNeuron3.Neuron.PosGenerator (и еще 39)
- **NPNeuronPosCGeneratorCable**: CableNeuron.NegGenerator
- **NPSynapseBio**: StatePredictor.InputNeuron1.Neuron.Soma1.ExcSynapse1, StatePredictor.InputNeuron1.Neuron.Soma1.InhSynapse1, StatePredictor.InputNeuron1.Neuron.Dendrite1_1.ExcSynapse1, StatePredictor.InputNeuron1.Neuron.Dendrite1_1.InhSynapse1, StatePredictor.InputNeuron1.Neuron.Soma2.ExcSynapse1 (и еще 7675)
- **NPredictor**: StatePredictor.Predictor, Predictor
- **NPulseChannelCableMulti**: CableNeuron.Soma1.ExcChannel, CableNeuron.Soma2.ExcChannel, CableNeuron.Dendrite1_1.ExcChannel, CableNeuron.Dendrite1_2.ExcChannel, CableNeuron.ExcChannel
- **NPulseGeneratorTransit**: StatePredictor.InputNeuron1.Source1, StatePredictor.InputNeuron1.Source2, StatePredictor.InputNeuron1.Source3, StatePredictor.InputNeuron1.Source4, StatePredictor.InputNeuron1.Source5 (и еще 93)
- **NPulseLTZoneCable**: CableNeuron.LTZone
- **NPulseLTZoneThreshold**: StatePredictor.InputNeuron1.Neuron.LTZone, StatePredictor.InputNeuron1.LTZone, StatePredictor.InputNeuron2.Neuron.LTZone, StatePredictor.InputNeuron2.LTZone, StatePredictor.InputNeuron3.Neuron.LTZone (и еще 39)
- **NPulseMembraneCableMulti**: CableNeuron.Soma1, CableNeuron.Soma2, CableNeuron.Dendrite1_1, CableNeuron.Dendrite1_2
- **NPulseNeuronCableMulti**: CableNeuron
- **NSPNeuronGen**: StatePredictor.InputNeuron1.Neuron, StatePredictor.InputNeuron2.Neuron, StatePredictor.InputNeuron3.Neuron, StatePredictor.InputNeuron4.Neuron, StatePredictor.OutputNeuron.Neuron (и еще 21)
- **NStatePredictor**: StatePredictor
- **NSynapseCableMulti**: CableNeuron.Soma1.ExcSynapse1, CableNeuron.Soma2.ExcSynapse1, CableNeuron.Dendrite1_1.ExcSynapse1, CableNeuron.Dendrite1_2.ExcSynapse1, CableNeuron.ExcSynapse1

**Входы системы:**
- `CableNeuron.Dendrite1_1.ExcChannel.ChannelInputs`
- `CableNeuron.Dendrite1_1.ExcChannel.SynapticInputs`
- `CableNeuron.Dendrite1_2.ExcChannel.ChannelInputs`
- `CableNeuron.Dendrite1_2.ExcChannel.SynapticInputs`
- `CableNeuron.Dendrite1_2.ExcSynapse1.Input`
- `CableNeuron.LTZone.Inputs`
- `CableNeuron.NegGenerator`
- `CableNeuron.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron.Soma1.InputFeedbackSignal`
- ... (всего 1590 входов)

**Выходы системы:**
- `.Output`
- `CableNeuron.Dendrite1_1.ExcChannel.Output`
- `CableNeuron.Dendrite1_1.ExcSynapse1.Output`
- `CableNeuron.Dendrite1_2.ExcChannel.Output`
- `CableNeuron.Dendrite1_2.ExcSynapse1.Output`
- `CableNeuron.LTZone.Output`
- `CableNeuron.NegGenerator.Output`
- `CableNeuron.Soma1.ExcChannel.Output`
- `CableNeuron.Soma1.ExcSynapse1.Output`
- `CableNeuron.Soma2.ExcChannel.Output`
- ... (всего 1384 выходов)

**Количество связей:** 1814

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti_NSPNeuronBio2

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti_NSPNeuronBio2`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPExcChannelBio2**: PNeuron.Soma1.ExcChannel, PNeuron.ExcChannel, PNeuron2.Soma1.ExcChannel, PNeuron2.Dendrite1_1.ExcChannel, PNeuron2.ExcChannel (и еще 29)
- **NPGenerator**: PGenerator
- **NPInhChannelBio2**: PNeuron.Soma1.InhChannel, PNeuron.InhChannel, PNeuron2.Soma1.InhChannel, PNeuron2.Dendrite1_1.InhChannel, PNeuron2.InhChannel (и еще 29)
- **NPMembraneBio2**: PNeuron.Soma1, PNeuron2.Soma1, PNeuron2.Dendrite1_1, PNeuron3.Soma1, PNeuron3.Dendrite1_1 (и еще 22)
- **NPNeuronNegCGeneratorBio**: PNeuron.NegGenerator, PNeuron2.NegGenerator, PNeuron3.NegGenerator, PNeuron4.NegGenerator, PNeuron5.NegGenerator (и еще 2)
- **NPNeuronPosCGeneratorBio**: PNeuron.PosGenerator, PNeuron2.PosGenerator, PNeuron3.PosGenerator, PNeuron4.PosGenerator, PNeuron5.PosGenerator (и еще 2)
- **NPSynapseBio2**: PNeuron.Soma1.ExcSynapse1, PNeuron.Soma1.InhSynapse1, PNeuron.ExcSynapse1, PNeuron.InhSynapse1, PNeuron2.Soma1.ExcSynapse1 (и еще 63)
- **NPulseLTZoneThresholdBio2**: PNeuron.LTZone, PNeuron2.LTZone, PNeuron3.LTZone, PNeuron4.LTZone, PNeuron5.LTZone (и еще 2)
- **NSPNeuronBio2**: PNeuron, PNeuron2, PNeuron3, PNeuron4, PNeuron5 (и еще 1)

**Входы системы:**
- `NegGenerator`
- `PGenerator`
- `PNeuron.LTZone.Inputs`
- `PNeuron.NegGenerator`
- `PNeuron.PosGenerator`
- `PNeuron.Soma1.ExcChannel.ChannelInputs`
- `PNeuron.Soma1.ExcChannel.SynapticInputs`
- `PNeuron.Soma1.ExcSynapse1.Input`
- `PNeuron.Soma1.InhChannel.ChannelInputs`
- `PNeuron.Soma1.InhChannel.SynapticInputs`
- ... (всего 117 входов)

**Выходы системы:**
- `PGenerator.Output`
- `PNeuron.LTZone.Output`
- `PNeuron.NegGenerator.Output`
- `PNeuron.PosGenerator.Output`
- `PNeuron.Soma1.ExcChannel.Output`
- `PNeuron.Soma1.ExcSynapse1.Output`
- `PNeuron.Soma1.InhChannel.Output`
- `PNeuron.Soma1.InhSynapse1.Output`
- `PNeuron2.Dendrite1_1.ExcChannel.Output`
- `PNeuron2.Dendrite1_1.ExcSynapse1.Output`
- ... (всего 103 выходов)

**Количество связей:** 108

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti_NSPNeuronBio2_syns

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti_NSPNeuronBio2_syns`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPExcChannelBio2**: PNeuron.Soma1.ExcChannel, PNeuron.Dendrite1_1.ExcChannel, PNeuron.Dendrite1_2.ExcChannel, PNeuron.Dendrite1_3.ExcChannel, PNeuron.Dendrite1_4.ExcChannel (и еще 15)
- **NPGenerator**: PGenerator
- **NPInhChannelBio2**: PNeuron.Soma1.InhChannel, PNeuron.Dendrite1_1.InhChannel, PNeuron.Dendrite1_2.InhChannel, PNeuron.Dendrite1_3.InhChannel, PNeuron.Dendrite1_4.InhChannel (и еще 15)
- **NPMembraneBio2**: PNeuron.Soma1, PNeuron.Dendrite1_1, PNeuron.Dendrite1_2, PNeuron.Dendrite1_3, PNeuron.Dendrite1_4 (и еще 13)
- **NPNeuronNegCGeneratorBio**: PNeuron.NegGenerator, NegGenerator
- **NPNeuronPosCGeneratorBio**: PNeuron.PosGenerator, PosGenerator
- **NPSynapseBio2**: PNeuron.Soma1.ExcSynapse1, PNeuron.Soma1.InhSynapse1, PNeuron.Dendrite1_1.ExcSynapse1, PNeuron.Dendrite1_1.InhSynapse1, PNeuron.Dendrite1_2.ExcSynapse1 (и еще 151)
- **NPulseLTZoneThresholdBio2**: PNeuron.LTZone, LTZone
- **NSPNeuronBio2**: PNeuron

**Входы системы:**
- `NegGenerator`
- `PGenerator`
- `PNeuron.Dendrite1_1.ExcChannel.ChannelInputs`
- `PNeuron.Dendrite1_1.ExcChannel.SynapticInputs`
- `PNeuron.Dendrite1_1.InhChannel.ChannelInputs`
- `PNeuron.Dendrite1_1.InhChannel.SynapticInputs`
- `PNeuron.Dendrite1_2.ExcChannel.ChannelInputs`
- `PNeuron.Dendrite1_2.ExcChannel.SynapticInputs`
- `PNeuron.Dendrite1_2.InhChannel.ChannelInputs`
- `PNeuron.Dendrite1_2.InhChannel.SynapticInputs`
- ... (всего 68 входов)

**Выходы системы:**
- `PGenerator.Output`
- `PNeuron.Dendrite1_1.ExcChannel.Output`
- `PNeuron.Dendrite1_1.ExcSynapse1.Output`
- `PNeuron.Dendrite1_1.InhChannel.Output`
- `PNeuron.Dendrite1_1.InhSynapse1.Output`
- `PNeuron.Dendrite1_2.ExcChannel.Output`
- `PNeuron.Dendrite1_2.ExcSynapse1.Output`
- `PNeuron.Dendrite1_2.InhChannel.Output`
- `PNeuron.Dendrite1_2.InhSynapse1.Output`
- `PNeuron.Dendrite1_3.ExcChannel.Output`
- ... (всего 69 выходов)

**Количество связей:** 99

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti_short_dx

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti_short_dx`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPExcChannelBio**: PNeuron.Soma1.ExcChannel, PNeuron.ExcChannel
- **NPGenerator**: PGenerator
- **NPInhChannelBio**: PNeuron.Soma1.InhChannel, PNeuron.InhChannel, Soma1.InhChannel, InhChannel
- **NPMembraneBio**: PNeuron.Soma1
- **NPNeuronNegCGeneratorBio**: PNeuron.NegGenerator
- **NPNeuronPosCGeneratorBio**: PNeuron.PosGenerator, PosGenerator
- **NPNeuronPosCGeneratorCable**: CableNeuron3.NegGenerator, CableNeuron.NegGenerator, NegGenerator
- **NPSynapseBio**: PNeuron.Soma1.ExcSynapse1, PNeuron.Soma1.InhSynapse1, PNeuron.ExcSynapse1, PNeuron.InhSynapse1, Soma1.InhSynapse1 (и еще 1)
- **NPulseChannelCable**: CableNeuron3.Soma1.ExcChannel, CableNeuron3.ExcChannel
- **NPulseChannelCableMulti**: CableNeuron.Soma1.ExcChannel, CableNeuron.ExcChannel, Soma1.ExcChannel, ExcChannel
- **NPulseChannelIaF**: IaFNeuron.Soma1.ExcChannel, IaFNeuron.ExcChannel
- **NPulseLTZoneCable**: CableNeuron3.LTZone, CableNeuron.LTZone, LTZone
- **NPulseLTZoneIaF**: IaFNeuron.LTZone
- **NPulseLTZoneThresholdBio**: PNeuron.LTZone
- **NPulseMembraneCable**: CableNeuron3.Soma1
- **NPulseMembraneCableMulti**: CableNeuron.Soma1, Soma1
- **NPulseMembraneIaF**: IaFNeuron.Soma1
- **NPulseNeuronCable**: CableNeuron3
- **NPulseNeuronCableMulti**: CableNeuron
- **NPulseNeuronIaF**: IaFNeuron
- **NSPNeuronBio**: PNeuron
- **NSynapseCable**: CableNeuron3.Soma1.ExcSynapse1, CableNeuron3.ExcSynapse1
- **NSynapseCableMulti**: CableNeuron.Soma1.ExcSynapse1, CableNeuron.ExcSynapse1, Soma1.ExcSynapse1, ExcSynapse1
- **NSynapseIaF**: IaFNeuron.Soma1.ExcSynapse1, IaFNeuron.ExcSynapse1

**Входы системы:**
- `CableNeuron.LTZone.Inputs`
- `CableNeuron.NegGenerator`
- `CableNeuron.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron.Soma1.ExcSynapse1.Input`
- `CableNeuron.Soma1.InputFeedbackSignal`
- `CableNeuron3.LTZone.Inputs`
- `CableNeuron3.NegGenerator`
- `CableNeuron3.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron3.Soma1.ExcChannel.SynapticInputs`
- ... (всего 28 входов)

**Выходы системы:**
- `CableNeuron.LTZone.Output`
- `CableNeuron.NegGenerator.Output`
- `CableNeuron.Soma1.ExcChannel.Output`
- `CableNeuron.Soma1.ExcSynapse1.Output`
- `CableNeuron3.LTZone.Output`
- `CableNeuron3.NegGenerator.Output`
- `CableNeuron3.Soma1.ExcChannel.Output`
- `CableNeuron3.Soma1.ExcSynapse1.Output`
- `IaFNeuron.LTZone.Output`
- `IaFNeuron.Soma1.ExcChannel.Output`
- ... (всего 19 выходов)

**Количество связей:** 22

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti_ver101_Nd

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti_ver101_Nd`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPGenerator**: PGenerator
- **NPNeuronPosCGeneratorCable**: CableNeuron2.NegGenerator, CableNeuron3.NegGenerator, CableNeuron4.NegGenerator, CableNeuron5.NegGenerator, CableNeuron6.NegGenerator (и еще 2)
- **NPulseChannelCableMulti**: CableNeuron2.Soma1.ExcChannel, CableNeuron2.Dendrite1_1.ExcChannel, CableNeuron2.ExcChannel, CableNeuron3.Soma1.ExcChannel, CableNeuron3.Dendrite1_1.ExcChannel (и еще 29)
- **NPulseLTZoneCable**: CableNeuron2.LTZone, CableNeuron3.LTZone, CableNeuron4.LTZone, CableNeuron5.LTZone, CableNeuron6.LTZone (и еще 2)
- **NPulseMembraneCableMulti**: CableNeuron2.Soma1, CableNeuron2.Dendrite1_1, CableNeuron3.Soma1, CableNeuron3.Dendrite1_1, CableNeuron3.Dendrite1_2 (и еще 22)
- **NPulseNeuronCableMulti**: CableNeuron2, CableNeuron3, CableNeuron4, CableNeuron5, CableNeuron6 (и еще 1)
- **NSynapseCableMulti**: CableNeuron2.Soma1.ExcSynapse1, CableNeuron2.Dendrite1_1.ExcSynapse1, CableNeuron2.Dendrite1_1.ExcSynapse2, CableNeuron2.Dendrite1_1.ExcSynapse3, CableNeuron2.Dendrite1_1.ExcSynapse4 (и еще 295)

**Входы системы:**
- `CableNeuron.LTZone.Inputs`
- `CableNeuron.NegGenerator`
- `CableNeuron.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron.Soma1.ExcSynapse1.Input`
- `CableNeuron.Soma1.ExcSynapse10.Input`
- `CableNeuron.Soma1.ExcSynapse11.Input`
- `CableNeuron.Soma1.ExcSynapse12.Input`
- `CableNeuron.Soma1.ExcSynapse13.Input`
- `CableNeuron.Soma1.ExcSynapse14.Input`
- ... (всего 152 входов)

**Выходы системы:**
- `CableNeuron.LTZone.Output`
- `CableNeuron.NegGenerator.Output`
- `CableNeuron.Soma1.ExcChannel.Output`
- `CableNeuron.Soma1.ExcSynapse1.Output`
- `CableNeuron.Soma1.ExcSynapse10.Output`
- `CableNeuron.Soma1.ExcSynapse11.Output`
- `CableNeuron.Soma1.ExcSynapse12.Output`
- `CableNeuron.Soma1.ExcSynapse13.Output`
- `CableNeuron.Soma1.ExcSynapse14.Output`
- `CableNeuron.Soma1.ExcSynapse15.Output`
- ... (всего 139 выходов)

**Количество связей:** 228

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti_ver101_Nd_matching

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti_ver101_Nd_matching`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPGenerator**: PGenerator
- **NPNeuronPosCGeneratorCable**: CableNeuron2.NegGenerator, CableNeuron3.NegGenerator, CableNeuron4.NegGenerator, CableNeuron5.NegGenerator, CableNeuron6.NegGenerator (и еще 26)
- **NPulseChannelCableMulti**: CableNeuron2.Soma1.ExcChannel, CableNeuron2.Dendrite1_1.ExcChannel, CableNeuron2.ExcChannel, CableNeuron3.Soma1.ExcChannel, CableNeuron3.Dendrite1_1.ExcChannel (и еще 137)
- **NPulseLTZoneCable**: CableNeuron2.LTZone, CableNeuron3.LTZone, CableNeuron4.LTZone, CableNeuron5.LTZone, CableNeuron6.LTZone (и еще 26)
- **NPulseMembraneCableMulti**: CableNeuron2.Soma1, CableNeuron2.Dendrite1_1, CableNeuron3.Soma1, CableNeuron3.Dendrite1_1, CableNeuron3.Dendrite1_2 (и еще 106)
- **NPulseNeuronCableMulti**: CableNeuron2, CableNeuron3, CableNeuron4, CableNeuron5, CableNeuron6 (и еще 25)
- **NSynapseCableMulti**: CableNeuron2.Soma1.ExcSynapse1, CableNeuron2.Dendrite1_1.ExcSynapse1, CableNeuron2.Dendrite1_1.ExcSynapse2, CableNeuron2.Dendrite1_1.ExcSynapse3, CableNeuron2.Dendrite1_1.ExcSynapse4 (и еще 1089)

**Входы системы:**
- `CableNeuron.LTZone.Inputs`
- `CableNeuron.NegGenerator`
- `CableNeuron.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron.Soma1.ExcSynapse1.Input`
- `CableNeuron.Soma1.ExcSynapse10.Input`
- `CableNeuron.Soma1.ExcSynapse11.Input`
- `CableNeuron.Soma1.ExcSynapse12.Input`
- `CableNeuron.Soma1.ExcSynapse13.Input`
- `CableNeuron.Soma1.ExcSynapse14.Input`
- ... (всего 752 входов)

**Выходы системы:**
- `CableNeuron.LTZone.Output`
- `CableNeuron.NegGenerator.Output`
- `CableNeuron.Soma1.ExcChannel.Output`
- `CableNeuron.Soma1.ExcSynapse1.Output`
- `CableNeuron.Soma1.ExcSynapse10.Output`
- `CableNeuron.Soma1.ExcSynapse11.Output`
- `CableNeuron.Soma1.ExcSynapse12.Output`
- `CableNeuron.Soma1.ExcSynapse13.Output`
- `CableNeuron.Soma1.ExcSynapse14.Output`
- `CableNeuron.Soma1.ExcSynapse15.Output`
- ... (всего 705 выходов)

**Количество связей:** 1154

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronMulti_ver101_Nsyn

**Путь:** `Bin\Configs\Demcheva\CableNeuronMulti_ver101_Nsyn`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPGenerator**: PGenerator
- **NPNeuronPosCGeneratorCable**: CableNeuron.NegGenerator, CableNeuron2.NegGenerator, CableNeuron3.NegGenerator, CableNeuron4.NegGenerator, CableNeuron5.NegGenerator (и еще 1)
- **NPulseChannelCableMulti**: CableNeuron.Soma1.ExcChannel, CableNeuron.Dendrite1_1.ExcChannel, CableNeuron.ExcChannel, CableNeuron2.Soma1.ExcChannel, CableNeuron2.Dendrite1_1.ExcChannel (и еще 13)
- **NPulseLTZoneCable**: CableNeuron.LTZone, CableNeuron2.LTZone, CableNeuron3.LTZone, CableNeuron4.LTZone, CableNeuron5.LTZone (и еще 1)
- **NPulseMembraneCableMulti**: CableNeuron.Soma1, CableNeuron.Dendrite1_1, CableNeuron2.Soma1, CableNeuron2.Dendrite1_1, CableNeuron3.Soma1 (и еще 7)
- **NPulseNeuronCableMulti**: CableNeuron, CableNeuron2, CableNeuron3, CableNeuron4, CableNeuron5
- **NSynapseCableMulti**: CableNeuron.Soma1.ExcSynapse1, CableNeuron.Dendrite1_1.ExcSynapse1, CableNeuron.ExcSynapse1, CableNeuron2.Soma1.ExcSynapse1, CableNeuron2.Dendrite1_1.ExcSynapse1 (и еще 41)

**Входы системы:**
- `CableNeuron.Dendrite1_1.ExcChannel.ChannelInputs`
- `CableNeuron.Dendrite1_1.ExcChannel.SynapticInputs`
- `CableNeuron.Dendrite1_1.ExcSynapse1.Input`
- `CableNeuron.LTZone.Inputs`
- `CableNeuron.NegGenerator`
- `CableNeuron.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron.Soma1.InputFeedbackSignal`
- `CableNeuron2.Dendrite1_1.ExcChannel.ChannelInputs`
- `CableNeuron2.Dendrite1_1.ExcChannel.SynapticInputs`
- ... (всего 52 входов)

**Выходы системы:**
- `CableNeuron.Dendrite1_1.ExcChannel.Output`
- `CableNeuron.Dendrite1_1.ExcSynapse1.Output`
- `CableNeuron.LTZone.Output`
- `CableNeuron.NegGenerator.Output`
- `CableNeuron.Soma1.ExcChannel.Output`
- `CableNeuron.Soma1.ExcSynapse1.Output`
- `CableNeuron2.Dendrite1_1.ExcChannel.Output`
- `CableNeuron2.Dendrite1_1.ExcSynapse1.Output`
- `CableNeuron2.Dendrite1_1.ExcSynapse2.Output`
- `CableNeuron2.LTZone.Output`
- ... (всего 41 выходов)

**Количество связей:** 55

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

### CableNeuronParametersTest

**Путь:** `Bin\Configs\Demcheva\CableNeuronParametersTest`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPExcChannelBio**: PNeuron.Soma1.ExcChannel, PNeuron.ExcChannel
- **NPGenerator**: PGenerator
- **NPInhChannelBio**: PNeuron.Soma1.InhChannel, PNeuron.InhChannel, Soma1.InhChannel, InhChannel
- **NPMembraneBio**: PNeuron.Soma1
- **NPNeuronNegCGeneratorBio**: PNeuron.NegGenerator
- **NPNeuronPosCGeneratorBio**: PNeuron.PosGenerator, PosGenerator
- **NPNeuronPosCGeneratorCable**: CableNeuron3.NegGenerator, CableNeuron2.NegGenerator, CableNeuron4.NegGenerator, CableNeuron5.NegGenerator, CableNeuron.NegGenerator (и еще 1)
- **NPSynapseBio**: PNeuron.Soma1.ExcSynapse1, PNeuron.Soma1.InhSynapse1, PNeuron.ExcSynapse1, PNeuron.InhSynapse1, Soma1.InhSynapse1 (и еще 1)
- **NPulseChannelCable**: CableNeuron3.Soma1.ExcChannel, CableNeuron3.ExcChannel, CableNeuron2.Soma1.ExcChannel, CableNeuron2.ExcChannel, CableNeuron4.Soma1.ExcChannel (и еще 7)
- **NPulseChannelIaF**: IaFNeuron.Soma1.ExcChannel, IaFNeuron.ExcChannel
- **NPulseLTZoneCable**: CableNeuron3.LTZone, CableNeuron2.LTZone, CableNeuron4.LTZone, CableNeuron5.LTZone, CableNeuron.LTZone (и еще 1)
- **NPulseLTZoneIaF**: IaFNeuron.LTZone
- **NPulseLTZoneThresholdBio**: PNeuron.LTZone
- **NPulseMembraneCable**: CableNeuron3.Soma1, CableNeuron2.Soma1, CableNeuron4.Soma1, CableNeuron5.Soma1, CableNeuron.Soma1 (и еще 1)
- **NPulseMembraneIaF**: IaFNeuron.Soma1
- **NPulseNeuronCable**: CableNeuron3, CableNeuron2, CableNeuron4, CableNeuron5, CableNeuron
- **NPulseNeuronIaF**: IaFNeuron
- **NSPNeuronBio**: PNeuron
- **NSynapseCable**: CableNeuron3.Soma1.ExcSynapse1, CableNeuron3.ExcSynapse1, CableNeuron2.Soma1.ExcSynapse1, CableNeuron2.ExcSynapse1, CableNeuron4.Soma1.ExcSynapse1 (и еще 7)
- **NSynapseIaF**: IaFNeuron.Soma1.ExcSynapse1, IaFNeuron.ExcSynapse1

**Входы системы:**
- `CableNeuron.LTZone.Inputs`
- `CableNeuron.NegGenerator`
- `CableNeuron.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron.Soma1.ExcSynapse1.Input`
- `CableNeuron.Soma1.InputFeedbackSignal`
- `CableNeuron2.LTZone.Inputs`
- `CableNeuron2.NegGenerator`
- `CableNeuron2.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron2.Soma1.ExcChannel.SynapticInputs`
- ... (всего 46 входов)

**Выходы системы:**
- `CableNeuron.LTZone.Output`
- `CableNeuron.NegGenerator.Output`
- `CableNeuron.Soma1.ExcChannel.Output`
- `CableNeuron.Soma1.ExcSynapse1.Output`
- `CableNeuron2.LTZone.Output`
- `CableNeuron2.NegGenerator.Output`
- `CableNeuron2.Soma1.ExcChannel.Output`
- `CableNeuron2.Soma1.ExcSynapse1.Output`
- `CableNeuron3.LTZone.Output`
- `CableNeuron3.NegGenerator.Output`
- ... (всего 31 выходов)

**Количество связей:** 37

**Связанные публикации:**
- [Compartmental spiking neuron model CSNM](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 24: Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM

---

## MC-Muscles

### MC-M-00-EyeMuscle

**Путь:** `Bin\Configs\!OldConfigs\MC-Muscles\MC-M-00-EyeMuscle`

**Назначение:** Модель управления мышцами

**Основные компоненты:**
- **NEyeMuscle**: EyeMuscle
- **NPGenerator**: PGenerator

**Входы системы:**
- `EyeMuscle.Inputs`
- `PGenerator`

**Выходы системы:**
- `PGenerator.Output`

**Количество связей:** 1

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев
- [The Neuromorphic Model of the Human Visual System](https://link.springer.com/chapter/10.1007%2F978-3-030-60577-3_40) - Публикация 18: Korsakov, A., Bakhshiev, A.

---

### MC-M-01-EyeMuscle

**Путь:** `Bin\Configs\!OldConfigs\MC-Muscles\MC-M-01-EyeMuscle`

**Назначение:** Модель управления мышцами

**Основные компоненты:**
- **NEyeMuscle**: EyeMuscle
- **NPGenerator**: PGenerator
- **UStatisticDoubleMatrix**: StatisticDoubleMatrix

**Входы системы:**
- `EyeMuscle.Inputs`
- `PGenerator`
- `StatisticDoubleMatrix.InputMatrixData`

**Выходы системы:**
- `EyeMuscle.OutputLength`
- `PGenerator.Output`

**Количество связей:** 2

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев
- [The Neuromorphic Model of the Human Visual System](https://link.springer.com/chapter/10.1007%2F978-3-030-60577-3_40) - Публикация 18: Korsakov, A., Bakhshiev, A.

---

## MC-RCN

### MC-RCN-01-NumMotionElements-Pendulum

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-01-NumMotionElements-Pendulum`

**Назначение:** Система управления движением

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfNewSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, EngineControlRangeAfferent.NegIntervalSeparator13 (и еще 11)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTZone (и еще 39)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronNegCGenerator (и еще 39)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronPosCGenerator (и еще 39)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR3.LTZone (и еще 27)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane.PosChannel (и еще 171)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronMembrane (и еще 39)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR3.Receptor (и еще 31)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.MotionElement0.AfferentR3 (и еще 27)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotionElement0.PostAfferentL2 (и еще 35)

**Входы системы:**
- `AfferentSource1`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL3.LTZone.DataInput0`
- ... (всего 202 входов)

**Выходы системы:**
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL3.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL3.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL4.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL4.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- ... (всего 84 выходов)

**Количество связей:** 109

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

## MC-RCN-00-1CL-All-DcEngine

### MC-RCN-00-01-1CL-SimpleME-SimpleA-woBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-1CL-All-DcEngine\MC-RCN-00-01-1CL-SimpleME-SimpleA-woBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, NegIntervalSeparator11, PosIntervalSeparator11
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.LTZone (и еще 15)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 15)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 15)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.AfferentR1.LTZone, EngineControlRangeAfferent.AfferentL1.LTZone, MotionElement0.AfferentR1.LTZone (и еще 3)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane.PosChannel (и еще 75)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PNeuronMembrane (и еще 15)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.AfferentR1.Receptor, EngineControlRangeAfferent.AfferentL1.Receptor (и еще 7)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.AfferentR1, EngineControlRangeAfferent.AfferentL1, MotionElement0.AfferentR1 (и еще 3)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotoneuronL (и еще 11)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `DCEngine.DataInput0`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataInput0`
- ... (всего 88 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel.DataOutput0`
- ... (всего 32 выходов)

**Количество связей:** 51

**Описание:** Simple Motion Element
Simple Afferents
With Post Afferents
Without Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-02-1CL-SimpleME-SimpleA-wBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-1CL-All-DcEngine\MC-RCN-00-02-1CL-SimpleME-SimpleA-wBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, NegIntervalSeparator11, PosIntervalSeparator11
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.LTZone (и еще 15)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 15)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 15)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.AfferentR1.LTZone, EngineControlRangeAfferent.AfferentL1.LTZone, MotionElement0.AfferentR1.LTZone (и еще 3)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel (и еще 99)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane (и еще 27)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.AfferentR1.Receptor, EngineControlRangeAfferent.AfferentL1.Receptor (и еще 7)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.AfferentR1, EngineControlRangeAfferent.AfferentL1, MotionElement0.AfferentR1 (и еще 3)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotoneuronL (и еще 11)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `DCEngine.DataInput0`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataInput0`
- ... (всего 98 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel.DataOutput0`
- ... (всего 36 выходов)

**Количество связей:** 50

**Описание:** Simple Motion Element
Simple Afferents
With Post Afferents
With Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-03-1CL-SimpleME-SimpleA-woBranches-wRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-1CL-All-DcEngine\MC-RCN-00-03-1CL-SimpleME-SimpleA-woBranches-wRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator21, EngineControlRangeAfferent.PosIntervalSeparator21, EngineControlRangeAfferent.NegIntervalSeparator31 (и еще 15)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent.MotionElement1, EngineControlRangeAfferent.MotionElement2, EngineControlRangeAfferent.MotionElement3, EngineControlRangeAfferent.MotionElement4 (и еще 5)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowL.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone (и еще 79)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator (и еще 79)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator (и еще 79)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement1.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement1.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement2.AfferentR1.LTZone (и еще 19)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane.PosChannel (и еще 331)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane (и еще 79)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.MotionElement1.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement1.AfferentL1.Receptor (и еще 31)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement1.AfferentR1, EngineControlRangeAfferent.MotionElement1.AfferentL1, EngineControlRangeAfferent.MotionElement2.AfferentR1 (и еще 19)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.RenshowL, EngineControlRangeAfferent.MotionElement0.RenshowR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1 (и еще 67)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `DCEngine.DataInput0`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataInput0`
- ... (всего 422 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel.DataOutput0`
- ... (всего 186 выходов)

**Количество связей:** 246

**Описание:** Simple Motion Element
Simple Afferents
With Post Afferents
Without Branches
With Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-04-1CL-TS-SimpleME-SimpleA-woBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-1CL-All-DcEngine\MC-RCN-00-04-1CL-TS-SimpleME-SimpleA-woBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, NegIntervalSeparator11, PosIntervalSeparator11
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotoneuronL (и еще 11)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.LTZone (и еще 15)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTMembrane, EngineControlRangeAfferent.MotionElement0.LTMembrane (и еще 15)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 15)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 15)
- **NPNewSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PNeuronMembrane (и еще 15)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.AfferentR1.LTZone, EngineControlRangeAfferent.AfferentL1.LTZone, MotionElement0.AfferentR1.LTZone (и еще 3)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel (и еще 115)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.AfferentR1.Receptor, EngineControlRangeAfferent.AfferentL1.Receptor (и еще 7)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.AfferentR1, EngineControlRangeAfferent.AfferentL1, MotionElement0.AfferentR1 (и еще 3)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `DCEngine.DataInput0`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataInput0`
- ... (всего 96 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone.DataOutput0`
- ... (всего 40 выходов)

**Количество связей:** 48

**Описание:** Simple Motion Element
New neurons with temporal summation
Simple Afferents
With Post Afferents
Without Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-05-1CL-TS-SimpleME-SimpleA-wBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-1CL-All-DcEngine\MC-RCN-00-05-1CL-TS-SimpleME-SimpleA-wBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, NegIntervalSeparator11, PosIntervalSeparator11
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotoneuronL (и еще 11)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.LTZone (и еще 15)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTMembrane, EngineControlRangeAfferent.MotionElement0.LTMembrane (и еще 15)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 15)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 15)
- **NPNewSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane (и еще 27)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.AfferentR1.LTZone, EngineControlRangeAfferent.AfferentL1.LTZone, MotionElement0.AfferentR1.LTZone (и еще 3)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.PosChannel (и еще 139)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.AfferentR1.Receptor, EngineControlRangeAfferent.AfferentL1.Receptor (и еще 7)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.AfferentR1, EngineControlRangeAfferent.AfferentL1, MotionElement0.AfferentR1 (и еще 3)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `DCEngine.DataInput0`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataInput0`
- ... (всего 104 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone.DataOutput0`
- ... (всего 44 выходов)

**Количество связей:** 56

**Описание:** Simple Motion Element
New neurons (with temporal summation)
Simple Afferents
With Post Afferents
With Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-06-1CL-TS-SimpleME-SimpleA-woBranches-wRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-1CL-All-DcEngine\MC-RCN-00-06-1CL-TS-SimpleME-SimpleA-woBranches-wRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, NegIntervalSeparator11, PosIntervalSeparator11
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.RenshowL, EngineControlRangeAfferent.MotionElement0.RenshowR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1 (и еще 19)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowL.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone (и еще 23)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTMembrane, EngineControlRangeAfferent.MotionElement0.RenshowL.LTMembrane, EngineControlRangeAfferent.MotionElement0.RenshowR.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTMembrane (и еще 23)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator (и еще 23)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator (и еще 23)
- **NPNewSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane (и еще 23)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.AfferentR1.LTZone, EngineControlRangeAfferent.AfferentL1.LTZone, MotionElement0.AfferentR1.LTZone (и еще 3)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel (и еще 163)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.AfferentR1.Receptor, EngineControlRangeAfferent.AfferentL1.Receptor (и еще 7)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.AfferentR1, EngineControlRangeAfferent.AfferentL1, MotionElement0.AfferentR1 (и еще 3)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `DCEngine.DataInput0`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataInput0`
- ... (всего 130 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone.DataOutput0`
- ... (всего 54 выходов)

**Количество связей:** 66

**Описание:** Simple Motion Element
New neurons (with temporal summation)
Simple Afferents
With Post Afferents
Without Branches
With Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-07-1CL-SimpleME-FullA-woBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-1CL-All-DcEngine\MC-RCN-00-07-1CL-SimpleME-FullA-woBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, NegIntervalSeparator11, PosIntervalSeparator11
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone (и еще 23)
- **NPNeuronChannel**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel (и еще 27)
- **NPNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane, EngineControlRangeAfferent.AfferentR1.PNeuronMembrane, EngineControlRangeAfferent.AfferentL1.PNeuronMembrane, MotionElement0.AfferentR1.PNeuronMembrane (и еще 3)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator (и еще 23)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator (и еще 23)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane.PosChannel (и еще 75)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PNeuronMembrane (и еще 15)
- **NPSynapse**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse2, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse3, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse2 (и еще 211)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.AfferentR1.Receptor, EngineControlRangeAfferent.AfferentL1.Receptor (и еще 7)
- **NSAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.AfferentR1, EngineControlRangeAfferent.AfferentL1, MotionElement0.AfferentR1 (и еще 3)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotoneuronL (и еще 11)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentL1.PNeuronNegCGenerator`
- `AfferentL1.PNeuronPosCGenerator`
- `AfferentR1.PNeuronNegCGenerator`
- `AfferentR1.PNeuronPosCGenerator`
- `AfferentSource1`
- `DCEngine.DataInput0`
- `EngineControlRangeAfferent.AfferentL1.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.AfferentL1.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.AfferentR1.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.AfferentR1.PNeuronPosCGenerator`
- ... (всего 112 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronNegCGenerator.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.DataOutput0`
- ... (всего 38 выходов)

**Количество связей:** 48

**Описание:** Simple Motion Element
Full Afferents
With Post Afferents
Without Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-08-1CL-SimpleME-FullA-wBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-1CL-All-DcEngine\MC-RCN-00-08-1CL-SimpleME-FullA-wBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, NegIntervalSeparator11, PosIntervalSeparator11
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone (и еще 23)
- **NPNeuronChannel**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel (и еще 27)
- **NPNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane, EngineControlRangeAfferent.AfferentR1.PNeuronMembrane, EngineControlRangeAfferent.AfferentL1.PNeuronMembrane, MotionElement0.AfferentR1.PNeuronMembrane (и еще 3)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator (и еще 23)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator (и еще 23)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel (и еще 99)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane (и еще 27)
- **NPSynapse**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse2, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse3, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse2 (и еще 211)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.AfferentR1.Receptor, EngineControlRangeAfferent.AfferentL1.Receptor (и еще 7)
- **NSAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.AfferentR1, EngineControlRangeAfferent.AfferentL1, MotionElement0.AfferentR1 (и еще 3)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotoneuronL (и еще 11)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentL1.PNeuronNegCGenerator`
- `AfferentL1.PNeuronPosCGenerator`
- `AfferentR1.PNeuronNegCGenerator`
- `AfferentR1.PNeuronPosCGenerator`
- `AfferentSource1`
- `DCEngine.DataInput0`
- `EngineControlRangeAfferent.AfferentL1.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.AfferentL1.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.AfferentR1.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.AfferentR1.PNeuronPosCGenerator`
- ... (всего 122 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronNegCGenerator.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.DataOutput0`
- ... (всего 42 выходов)

**Количество связей:** 58

**Описание:** Simple Motion Element
Full Afferents
With Post Afferents
With Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-09-1CL-SimpleME-FullA-woBranches-wRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-1CL-All-DcEngine\MC-RCN-00-09-1CL-SimpleME-FullA-woBranches-wRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, NegIntervalSeparator11, PosIntervalSeparator11
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowL.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowR.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone (и еще 31)
- **NPNeuronChannel**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel (и еще 27)
- **NPNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane, EngineControlRangeAfferent.AfferentR1.PNeuronMembrane, EngineControlRangeAfferent.AfferentL1.PNeuronMembrane, MotionElement0.AfferentR1.PNeuronMembrane (и еще 3)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronNegCGenerator (и еще 31)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronPosCGenerator (и еще 31)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane.PosChannel (и еще 107)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane (и еще 23)
- **NPSynapse**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse2, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse3, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse2 (и еще 211)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.AfferentR1.Receptor, EngineControlRangeAfferent.AfferentL1.Receptor (и еще 7)
- **NSAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.AfferentR1, EngineControlRangeAfferent.AfferentL1, MotionElement0.AfferentR1 (и еще 3)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.RenshowL, EngineControlRangeAfferent.MotionElement0.RenshowR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1 (и еще 19)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentL1.PNeuronNegCGenerator`
- `AfferentL1.PNeuronPosCGenerator`
- `AfferentR1.PNeuronNegCGenerator`
- `AfferentR1.PNeuronPosCGenerator`
- `AfferentSource1`
- `DCEngine.DataInput0`
- `EngineControlRangeAfferent.AfferentL1.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.AfferentL1.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.AfferentR1.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.AfferentR1.PNeuronPosCGenerator`
- ... (всего 142 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronNegCGenerator.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.DataOutput0`
- ... (всего 48 выходов)

**Количество связей:** 62

**Описание:** Simple Motion Element
Full Afferents
With Post Afferents
Without Branches
With Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

## MC-RCN-00-1CL-All-Pendulum

### MC-RCN-00-01-1CL-SimpleME-SimpleA-woBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-1CL-All-Pendulum\MC-RCN-00-01-1CL-SimpleME-SimpleA-woBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, NegIntervalSeparator11, PosIntervalSeparator11
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.LTZone (и еще 15)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 15)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 15)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.AfferentR1.LTZone, EngineControlRangeAfferent.AfferentL1.LTZone, MotionElement0.AfferentR1.LTZone (и еще 3)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane.PosChannel (и еще 75)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PNeuronMembrane (и еще 15)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.AfferentR1.Receptor, EngineControlRangeAfferent.AfferentL1.Receptor (и еще 7)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.AfferentR1, EngineControlRangeAfferent.AfferentL1, MotionElement0.AfferentR1 (и еще 3)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotoneuronL (и еще 11)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone.DataInput0`
- ... (всего 90 входов)

**Выходы системы:**
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone.DataOutput0`
- ... (всего 34 выходов)

**Количество связей:** 53

**Описание:** Simple Motion Element
Simple Afferents
With Post Afferents
Without Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-02-1CL-SimpleME-SimpleA-wBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-1CL-All-Pendulum\MC-RCN-00-02-1CL-SimpleME-SimpleA-wBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, NegIntervalSeparator11, PosIntervalSeparator11
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.LTZone (и еще 15)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 15)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 15)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.AfferentR1.LTZone, EngineControlRangeAfferent.AfferentL1.LTZone, MotionElement0.AfferentR1.LTZone (и еще 3)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel (и еще 99)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane (и еще 27)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.AfferentR1.Receptor, EngineControlRangeAfferent.AfferentL1.Receptor (и еще 7)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.AfferentR1, EngineControlRangeAfferent.AfferentL1, MotionElement0.AfferentR1 (и еще 3)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotoneuronL (и еще 11)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone.DataInput0`
- ... (всего 100 входов)

**Выходы системы:**
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator.DataOutput0`
- ... (всего 38 выходов)

**Количество связей:** 52

**Описание:** Simple Motion Element
Simple Afferents
With Post Afferents
With Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-03-1CL-SimpleME-SimpleA-woBranches-wRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-1CL-All-Pendulum\MC-RCN-00-03-1CL-SimpleME-SimpleA-woBranches-wRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, NegIntervalSeparator11, PosIntervalSeparator11
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowL.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone (и еще 23)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator (и еще 23)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator (и еще 23)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.AfferentR1.LTZone, EngineControlRangeAfferent.AfferentL1.LTZone, MotionElement0.AfferentR1.LTZone (и еще 3)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane.PosChannel (и еще 107)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane (и еще 23)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.AfferentR1.Receptor, EngineControlRangeAfferent.AfferentL1.Receptor (и еще 7)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.AfferentR1, EngineControlRangeAfferent.AfferentL1, MotionElement0.AfferentR1 (и еще 3)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.RenshowL, EngineControlRangeAfferent.MotionElement0.RenshowR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1 (и еще 19)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone.DataInput0`
- ... (всего 120 входов)

**Выходы системы:**
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone.DataOutput0`
- ... (всего 44 выходов)

**Количество связей:** 56

**Описание:** Simple Motion Element
Simple Afferents
With Post Afferents
Without Branches
With Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-04-1CL-TS-SimpleME-SimpleA-woBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-1CL-All-Pendulum\MC-RCN-00-04-1CL-TS-SimpleME-SimpleA-woBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, NegIntervalSeparator11, PosIntervalSeparator11
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotoneuronL (и еще 11)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.LTZone (и еще 15)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTMembrane, EngineControlRangeAfferent.MotionElement0.LTMembrane (и еще 15)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 15)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 15)
- **NPNewSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PNeuronMembrane (и еще 15)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.AfferentR1.LTZone, EngineControlRangeAfferent.AfferentL1.LTZone, MotionElement0.AfferentR1.LTZone (и еще 3)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel (и еще 115)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.AfferentR1.Receptor, EngineControlRangeAfferent.AfferentL1.Receptor (и еще 7)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.AfferentR1, EngineControlRangeAfferent.AfferentL1, MotionElement0.AfferentR1 (и еще 3)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.DataInput0`
- ... (всего 98 входов)

**Выходы системы:**
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator.DataOutput0`
- ... (всего 42 выходов)

**Количество связей:** 50

**Описание:** Simple Motion Element
New neurons with temporal summation
Simple Afferents
With Post Afferents
Without Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-05-1CL-TS-SimpleME-SimpleA-wBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-1CL-All-Pendulum\MC-RCN-00-05-1CL-TS-SimpleME-SimpleA-wBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, NegIntervalSeparator11, PosIntervalSeparator11
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotoneuronL (и еще 11)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.LTZone (и еще 15)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTMembrane, EngineControlRangeAfferent.MotionElement0.LTMembrane (и еще 15)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 15)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 15)
- **NPNewSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane (и еще 27)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.AfferentR1.LTZone, EngineControlRangeAfferent.AfferentL1.LTZone, MotionElement0.AfferentR1.LTZone (и еще 3)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.PosChannel (и еще 139)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.AfferentR1.Receptor, EngineControlRangeAfferent.AfferentL1.Receptor (и еще 7)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.AfferentR1, EngineControlRangeAfferent.AfferentL1, MotionElement0.AfferentR1 (и еще 3)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.DataInput0`
- ... (всего 106 входов)

**Выходы системы:**
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.NegChannel.DataOutput0`
- ... (всего 46 выходов)

**Количество связей:** 58

**Описание:** Simple Motion Element
New neurons (with temporal summation)
Simple Afferents
With Post Afferents
With Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-06-1CL-TS-SimpleME-SimpleA-woBranches-wRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-1CL-All-Pendulum\MC-RCN-00-06-1CL-TS-SimpleME-SimpleA-woBranches-wRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, NegIntervalSeparator11, PosIntervalSeparator11
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.RenshowL, EngineControlRangeAfferent.MotionElement0.RenshowR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1 (и еще 19)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowL.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone (и еще 23)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTMembrane, EngineControlRangeAfferent.MotionElement0.RenshowL.LTMembrane, EngineControlRangeAfferent.MotionElement0.RenshowR.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTMembrane (и еще 23)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator (и еще 23)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator (и еще 23)
- **NPNewSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane (и еще 23)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.AfferentR1.LTZone, EngineControlRangeAfferent.AfferentL1.LTZone, MotionElement0.AfferentR1.LTZone (и еще 3)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel (и еще 163)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.AfferentR1.Receptor, EngineControlRangeAfferent.AfferentL1.Receptor (и еще 7)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.AfferentR1, EngineControlRangeAfferent.AfferentL1, MotionElement0.AfferentR1 (и еще 3)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.DataInput0`
- ... (всего 132 входов)

**Выходы системы:**
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator.DataOutput0`
- ... (всего 56 выходов)

**Количество связей:** 68

**Описание:** Simple Motion Element
New neurons (with temporal summation)    
Simple Afferents
With Post Afferents
Without Branches
With Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-07-1CL-SimpleME-FullA-woBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-1CL-All-Pendulum\MC-RCN-00-07-1CL-SimpleME-FullA-woBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, NegIntervalSeparator11, PosIntervalSeparator11
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone (и еще 23)
- **NPNeuronChannel**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel (и еще 27)
- **NPNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane, EngineControlRangeAfferent.AfferentR1.PNeuronMembrane, EngineControlRangeAfferent.AfferentL1.PNeuronMembrane, MotionElement0.AfferentR1.PNeuronMembrane (и еще 3)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator (и еще 23)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator (и еще 23)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane.PosChannel (и еще 75)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PNeuronMembrane (и еще 15)
- **NPSynapse**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse2, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse3, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse2 (и еще 211)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.AfferentR1.Receptor, EngineControlRangeAfferent.AfferentL1.Receptor (и еще 7)
- **NSAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.AfferentR1, EngineControlRangeAfferent.AfferentL1, MotionElement0.AfferentR1 (и еще 3)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotoneuronL (и еще 11)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentL1.PNeuronNegCGenerator`
- `AfferentL1.PNeuronPosCGenerator`
- `AfferentR1.PNeuronNegCGenerator`
- `AfferentR1.PNeuronPosCGenerator`
- `AfferentSource1`
- `EngineControlRangeAfferent.AfferentL1.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.AfferentL1.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.AfferentR1.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.AfferentR1.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.AfferentSource1`
- ... (всего 114 входов)

**Выходы системы:**
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronNegCGenerator.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronNegCGenerator.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- ... (всего 40 выходов)

**Количество связей:** 50

**Описание:** Simple Motion Element
Full Afferents
With Post Afferents
Without Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-08-1CL-SimpleME-FullA-wBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-1CL-All-Pendulum\MC-RCN-00-08-1CL-SimpleME-FullA-wBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, NegIntervalSeparator11, PosIntervalSeparator11
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone (и еще 23)
- **NPNeuronChannel**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel (и еще 27)
- **NPNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane, EngineControlRangeAfferent.AfferentR1.PNeuronMembrane, EngineControlRangeAfferent.AfferentL1.PNeuronMembrane, MotionElement0.AfferentR1.PNeuronMembrane (и еще 3)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator (и еще 23)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator (и еще 23)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel (и еще 99)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane (и еще 27)
- **NPSynapse**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse2, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse3, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse2 (и еще 211)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.AfferentR1.Receptor, EngineControlRangeAfferent.AfferentL1.Receptor (и еще 7)
- **NSAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.AfferentR1, EngineControlRangeAfferent.AfferentL1, MotionElement0.AfferentR1 (и еще 3)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotoneuronL (и еще 11)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentL1.PNeuronNegCGenerator`
- `AfferentL1.PNeuronPosCGenerator`
- `AfferentR1.PNeuronNegCGenerator`
- `AfferentR1.PNeuronPosCGenerator`
- `AfferentSource1`
- `EngineControlRangeAfferent.AfferentL1.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.AfferentL1.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.AfferentR1.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.AfferentR1.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.AfferentSource1`
- ... (всего 124 входов)

**Выходы системы:**
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronNegCGenerator.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronNegCGenerator.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- ... (всего 44 выходов)

**Количество связей:** 60

**Описание:** Simple Motion Element
Full Afferents
With Post Afferents
With Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-09-1CL-SimpleME-FullA-woBranches-wRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-1CL-All-Pendulum\MC-RCN-00-09-1CL-SimpleME-FullA-woBranches-wRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, NegIntervalSeparator11, PosIntervalSeparator11
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowL.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowR.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone (и еще 31)
- **NPNeuronChannel**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel (и еще 27)
- **NPNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane, EngineControlRangeAfferent.AfferentR1.PNeuronMembrane, EngineControlRangeAfferent.AfferentL1.PNeuronMembrane, MotionElement0.AfferentR1.PNeuronMembrane (и еще 3)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronNegCGenerator (и еще 31)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronPosCGenerator (и еще 31)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane.PosChannel (и еще 107)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane (и еще 23)
- **NPSynapse**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse2, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse3, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse2 (и еще 211)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.AfferentR1.Receptor, EngineControlRangeAfferent.AfferentL1.Receptor (и еще 7)
- **NSAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.AfferentR1, EngineControlRangeAfferent.AfferentL1, MotionElement0.AfferentR1 (и еще 3)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.RenshowL, EngineControlRangeAfferent.MotionElement0.RenshowR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1 (и еще 19)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentL1.PNeuronNegCGenerator`
- `AfferentL1.PNeuronPosCGenerator`
- `AfferentR1.PNeuronNegCGenerator`
- `AfferentR1.PNeuronPosCGenerator`
- `AfferentSource1`
- `EngineControlRangeAfferent.AfferentL1.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.AfferentL1.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.AfferentR1.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.AfferentR1.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.AfferentSource1`
- ... (всего 144 входов)

**Выходы системы:**
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronNegCGenerator.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronNegCGenerator.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- ... (всего 50 выходов)

**Количество связей:** 64

**Описание:** Simple Motion Element
Full Afferents
With Post Afferents
Without Branches
With Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

## MC-RCN-00-2CL-All-DcEngine

### MC-RCN-00-01-2CL-SimpleME-SimpleA-woBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-2CL-All-DcEngine\MC-RCN-00-01-2CL-SimpleME-SimpleA-woBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, NegIntervalSeparator11 (и еще 3)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTZone (и еще 23)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronNegCGenerator (и еще 23)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronPosCGenerator (и еще 23)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone, EngineControlRangeAfferent.AfferentR1.LTZone (и еще 11)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane.PosChannel (и еще 107)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronMembrane (и еще 23)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor (и еще 15)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.AfferentR1 (и еще 11)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotionElement0.PostAfferentL2 (и еще 19)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `DCEngine.DataInput0`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataInput0`
- ... (всего 126 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone.DataOutput0`
- ... (всего 49 выходов)

**Количество связей:** 62

**Описание:** 2 Control loops: angle, angle speed
Simple Motion Element
Simple Afferents
With Post Afferents
Without Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-02-2CL-SimpleME-SimpleA-wBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-2CL-All-DcEngine\MC-RCN-00-02-2CL-SimpleME-SimpleA-wBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, NegIntervalSeparator11 (и еще 3)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTZone (и еще 23)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronNegCGenerator (и еще 23)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronPosCGenerator (и еще 23)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone, EngineControlRangeAfferent.AfferentR1.LTZone (и еще 11)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane3.PosChannel (и еще 155)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane3, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane2 (и еще 47)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor (и еще 15)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.AfferentR1 (и еще 11)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotionElement0.PostAfferentL2 (и еще 19)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `DCEngine.DataInput0`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataInput0`
- ... (всего 146 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone.DataOutput0`
- ... (всего 57 выходов)

**Количество связей:** 82

**Описание:** 2 Control loops: angle, angle speed   
Simple Motion Element
Simple Afferents
With Post Afferents
With Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-03-2CL-SimpleME-SimpleA-woBranches-wRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-2CL-All-DcEngine\MC-RCN-00-03-2CL-SimpleME-SimpleA-woBranches-wRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, NegIntervalSeparator11 (и еще 3)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowL.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone (и еще 31)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator (и еще 31)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator (и еще 31)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone, EngineControlRangeAfferent.AfferentR1.LTZone (и еще 11)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane.PosChannel (и еще 139)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane (и еще 31)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor (и еще 15)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.AfferentR1 (и еще 11)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.RenshowL, EngineControlRangeAfferent.MotionElement0.RenshowR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1 (и еще 27)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `DCEngine.DataInput0`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataInput0`
- ... (всего 156 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone.DataOutput0`
- ... (всего 59 выходов)

**Количество связей:** 76

**Описание:** 2 Control loops: angle, angle speed
Simple Motion Element
Simple Afferents
With Post Afferents
Without Branches
With Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-04-2CL-TS-SimpleME-SimpleA-woBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-2CL-All-DcEngine\MC-RCN-00-04-2CL-TS-SimpleME-SimpleA-woBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, NegIntervalSeparator11 (и еще 3)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotionElement0.PostAfferentL2 (и еще 19)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTZone (и еще 23)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTMembrane (и еще 23)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronNegCGenerator (и еще 23)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronPosCGenerator (и еще 23)
- **NPNewSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronMembrane (и еще 23)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone, EngineControlRangeAfferent.AfferentR1.LTZone (и еще 11)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel (и еще 163)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor (и еще 15)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.AfferentR1 (и еще 11)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `DCEngine.DataInput0`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataInput0`
- ... (всего 138 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone.DataOutput0`
- ... (всего 61 выходов)

**Количество связей:** 74

**Описание:** 2 Control loops: angle, angle speed
Simple Motion Element
New neurons with temporal summation
Simple Afferents
With Post Afferents
Without Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-05-2CL-TS-SimpleME-SimpleA-wBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-2CL-All-DcEngine\MC-RCN-00-05-2CL-TS-SimpleME-SimpleA-wBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, NegIntervalSeparator11 (и еще 3)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotionElement0.PostAfferentL2 (и еще 19)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTZone (и еще 23)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTMembrane (и еще 23)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronNegCGenerator (и еще 23)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronPosCGenerator (и еще 23)
- **NPNewSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane3, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane2 (и еще 47)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone, EngineControlRangeAfferent.AfferentR1.LTZone (и еще 11)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.PosChannel (и еще 211)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor (и еще 15)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.AfferentR1 (и еще 11)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `DCEngine.DataInput0`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataInput0`
- ... (всего 154 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone.DataOutput0`
- ... (всего 69 выходов)

**Количество связей:** 90

**Описание:** 2 Control loops: angle, angle speed
Simple Motion Element
New neurons (with temporal summation)
Simple Afferents
With Post Afferents
With Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-06-2CL-TS-SimpleME-SimpleA-woBranches-wRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-2CL-All-DcEngine\MC-RCN-00-06-2CL-TS-SimpleME-SimpleA-woBranches-wRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, NegIntervalSeparator11 (и еще 3)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.RenshowL, EngineControlRangeAfferent.MotionElement0.RenshowR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1 (и еще 27)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowL.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone (и еще 31)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTMembrane, EngineControlRangeAfferent.MotionElement0.RenshowL.LTMembrane, EngineControlRangeAfferent.MotionElement0.RenshowR.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTMembrane (и еще 31)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator (и еще 31)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator (и еще 31)
- **NPNewSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane (и еще 31)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone, EngineControlRangeAfferent.AfferentR1.LTZone (и еще 11)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel (и еще 211)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor (и еще 15)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.AfferentR1 (и еще 11)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `DCEngine.DataInput0`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataInput0`
- ... (всего 172 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone.DataOutput0`
- ... (всего 75 выходов)

**Количество связей:** 92

**Описание:** 2 Control loops: angle, angle speed
Simple Motion Element
New neurons (with temporal summation)
Simple Afferents
With Post Afferents
Without Branches
With Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-07-2CL-SimpleME-FullA-woBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-2CL-All-DcEngine\MC-RCN-00-07-2CL-SimpleME-FullA-woBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, NegIntervalSeparator11 (и еще 3)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone (и еще 39)
- **NPNeuronChannel**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel (и еще 59)
- **NPNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentR2.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentL2.PNeuronMembrane, EngineControlRangeAfferent.AfferentR1.PNeuronMembrane (и еще 11)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR2.PNeuronNegCGenerator (и еще 39)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR2.PNeuronPosCGenerator (и еще 39)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane.PosChannel (и еще 107)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronMembrane (и еще 23)
- **NPSynapse**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse2, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse3, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse2 (и еще 355)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor (и еще 15)
- **NSAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.AfferentR1 (и еще 11)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotionElement0.PostAfferentL2 (и еще 19)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentL1.PNeuronNegCGenerator`
- `AfferentL1.PNeuronPosCGenerator`
- `AfferentL2.PNeuronNegCGenerator`
- `AfferentL2.PNeuronPosCGenerator`
- `AfferentR1.PNeuronNegCGenerator`
- `AfferentR1.PNeuronPosCGenerator`
- `AfferentR2.PNeuronNegCGenerator`
- `AfferentR2.PNeuronPosCGenerator`
- `AfferentSource1`
- `DCEngine.DataInput0`
- ... (всего 174 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronNegCGenerator.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.PNeuronMembrane.NegChannel.DataOutput0`
- ... (всего 61 выходов)

**Количество связей:** 78

**Описание:** 2 Control loops: angle, angle speed
Simple Motion Element
Full Afferents
With Post Afferents
Without Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-08-2CL-SimpleME-FullA-wBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-2CL-All-DcEngine\MC-RCN-00-08-2CL-SimpleME-FullA-wBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, NegIntervalSeparator11 (и еще 3)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone (и еще 39)
- **NPNeuronChannel**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel (и еще 59)
- **NPNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentR2.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentL2.PNeuronMembrane, EngineControlRangeAfferent.AfferentR1.PNeuronMembrane (и еще 11)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR2.PNeuronNegCGenerator (и еще 39)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR2.PNeuronPosCGenerator (и еще 39)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane3.PosChannel (и еще 155)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane3, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane2 (и еще 47)
- **NPSynapse**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse2, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse3, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse2 (и еще 355)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor (и еще 15)
- **NSAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.AfferentR1 (и еще 11)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotionElement0.PostAfferentL2 (и еще 19)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentL1.PNeuronNegCGenerator`
- `AfferentL1.PNeuronPosCGenerator`
- `AfferentL2.PNeuronNegCGenerator`
- `AfferentL2.PNeuronPosCGenerator`
- `AfferentR1.PNeuronNegCGenerator`
- `AfferentR1.PNeuronPosCGenerator`
- `AfferentR2.PNeuronNegCGenerator`
- `AfferentR2.PNeuronPosCGenerator`
- `AfferentSource1`
- `DCEngine.DataInput0`
- ... (всего 194 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronNegCGenerator.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.PNeuronMembrane.NegChannel.DataOutput0`
- ... (всего 69 выходов)

**Количество связей:** 98

**Описание:** 2 Control loops: angle, angle speed
Simple Motion Element
Full Afferents
With Post Afferents
With Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-09-2CL-SimpleME-FullA-woBranches-wRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-2CL-All-DcEngine\MC-RCN-00-09-2CL-SimpleME-FullA-woBranches-wRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, NegIntervalSeparator11 (и еще 3)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowL.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowR.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone (и еще 47)
- **NPNeuronChannel**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel (и еще 59)
- **NPNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentR2.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentL2.PNeuronMembrane, EngineControlRangeAfferent.AfferentR1.PNeuronMembrane (и еще 11)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronNegCGenerator (и еще 47)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronPosCGenerator (и еще 47)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane.PosChannel (и еще 139)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane (и еще 31)
- **NPSynapse**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse2, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse3, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse2 (и еще 355)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor (и еще 15)
- **NSAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.AfferentR1 (и еще 11)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.RenshowL, EngineControlRangeAfferent.MotionElement0.RenshowR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1 (и еще 27)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentL1.PNeuronNegCGenerator`
- `AfferentL1.PNeuronPosCGenerator`
- `AfferentL2.PNeuronNegCGenerator`
- `AfferentL2.PNeuronPosCGenerator`
- `AfferentR1.PNeuronNegCGenerator`
- `AfferentR1.PNeuronPosCGenerator`
- `AfferentR2.PNeuronNegCGenerator`
- `AfferentR2.PNeuronPosCGenerator`
- `AfferentSource1`
- `DCEngine.DataInput0`
- ... (всего 204 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronNegCGenerator.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.PNeuronMembrane.NegChannel.DataOutput0`
- ... (всего 71 выходов)

**Количество связей:** 92

**Описание:** 2 Control loops: angle, angle speed
Simple Motion Element
Full Afferents
With Post Afferents
Without Branches
With Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

## MC-RCN-00-2CL-All-Pendulum

### MC-RCN-00-01-2CL-SimpleME-SimpleA-woBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-2CL-All-Pendulum\MC-RCN-00-01-2CL-SimpleME-SimpleA-woBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, EngineControlRangeAfferent.NegIntervalSeparator21 (и еще 19)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent.MotionElement1, EngineControlRangeAfferent.MotionElement2, MotionElement0, MotionElement1 (и еще 1)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTZone (и еще 51)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronNegCGenerator (и еще 51)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronPosCGenerator (и еще 51)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone, EngineControlRangeAfferent.MotionElement1.AfferentR1.LTZone (и еще 27)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane.PosChannel (и еще 219)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronMembrane (и еще 51)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor (и еще 35)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.MotionElement1.AfferentR1 (и еще 27)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotionElement0.PostAfferentL2 (и еще 43)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataInput0`
- ... (всего 296 входов)

**Выходы системы:**
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel.DataOutput0`
- ... (всего 135 выходов)

**Количество связей:** 254

**Описание:** 2 Control loops: angle, angle speed
Simple Motion Element
Simple Afferents
With Post Afferents
Without Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-02-2CL-SimpleME-SimpleA-wBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-2CL-All-Pendulum\MC-RCN-00-02-2CL-SimpleME-SimpleA-wBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, EngineControlRangeAfferent.NegIntervalSeparator21 (и еще 19)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent.MotionElement1, EngineControlRangeAfferent.MotionElement2, MotionElement0, MotionElement1 (и еще 1)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTZone (и еще 51)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronNegCGenerator (и еще 51)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronPosCGenerator (и еще 51)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone, EngineControlRangeAfferent.MotionElement1.AfferentR1.LTZone (и еще 27)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane3.PosChannel (и еще 315)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane3, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane2 (и еще 99)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor (и еще 35)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.MotionElement1.AfferentR1 (и еще 27)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotionElement0.PostAfferentL2 (и еще 43)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataInput0`
- ... (всего 356 входов)

**Выходы системы:**
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel.DataOutput0`
- ... (всего 159 выходов)

**Количество связей:** 319

**Описание:** 2 Control loops: angle, angle speed   
Simple Motion Element
Simple Afferents
With Post Afferents
With Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-03-2CL-SimpleME-SimpleA-woBranches-wRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-2CL-All-Pendulum\MC-RCN-00-03-2CL-SimpleME-SimpleA-woBranches-wRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, EngineControlRangeAfferent.NegIntervalSeparator21 (и еще 19)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent.MotionElement1, EngineControlRangeAfferent.MotionElement2, MotionElement0, MotionElement1 (и еще 1)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowL.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone (и еще 67)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator (и еще 67)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator (и еще 67)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone, EngineControlRangeAfferent.MotionElement1.AfferentR1.LTZone (и еще 27)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane.PosChannel (и еще 283)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane (и еще 67)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor (и еще 35)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.MotionElement1.AfferentR1 (и еще 27)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.RenshowL, EngineControlRangeAfferent.MotionElement0.RenshowR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1 (и еще 59)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataInput0`
- ... (всего 370 входов)

**Выходы системы:**
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel.DataOutput0`
- ... (всего 165 выходов)

**Количество связей:** 218

**Описание:** 2 Control loops: angle, angle speed
Simple Motion Element
Simple Afferents
With Post Afferents
Without Branches
With Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-04-2CL-TS-SimpleME-SimpleA-woBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-2CL-All-Pendulum\MC-RCN-00-04-2CL-TS-SimpleME-SimpleA-woBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, EngineControlRangeAfferent.NegIntervalSeparator21 (и еще 19)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent.MotionElement1, EngineControlRangeAfferent.MotionElement2, MotionElement0, MotionElement1 (и еще 1)
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotionElement0.PostAfferentL2 (и еще 43)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTZone (и еще 51)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTMembrane (и еще 51)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronNegCGenerator (и еще 51)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronPosCGenerator (и еще 51)
- **NPNewSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronMembrane (и еще 51)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone, EngineControlRangeAfferent.MotionElement1.AfferentR1.LTZone (и еще 27)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel (и еще 331)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor (и еще 35)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.MotionElement1.AfferentR1 (и еще 27)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataInput0`
- ... (всего 346 входов)

**Выходы системы:**
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel.DataOutput0`
- ... (всего 171 выходов)

**Количество связей:** 300

**Описание:** 2 Control loops: angle, angle speed
Simple Motion Element
New neurons with temporal summation
Simple Afferents
With Post Afferents
Without Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-05-2CL-TS-SimpleME-SimpleA-wBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-2CL-All-Pendulum\MC-RCN-00-05-2CL-TS-SimpleME-SimpleA-wBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, EngineControlRangeAfferent.NegIntervalSeparator21 (и еще 19)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent.MotionElement1, EngineControlRangeAfferent.MotionElement2, MotionElement0, MotionElement1 (и еще 1)
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotionElement0.PostAfferentL2 (и еще 43)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTZone (и еще 51)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTMembrane (и еще 51)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronNegCGenerator (и еще 51)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronPosCGenerator (и еще 51)
- **NPNewSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane3, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane2 (и еще 99)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone, EngineControlRangeAfferent.MotionElement1.AfferentR1.LTZone (и еще 27)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.PosChannel (и еще 427)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor (и еще 35)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.MotionElement1.AfferentR1 (и еще 27)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataInput0`
- ... (всего 380 входов)

**Выходы системы:**
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel.DataOutput0`
- ... (всего 195 выходов)

**Количество связей:** 260

**Описание:** 2 Control loops: angle, angle speed
Simple Motion Element
New neurons (with temporal summation)
Simple Afferents
With Post Afferents
With Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-06-2CL-TS-SimpleME-SimpleA-woBranches-wRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-2CL-All-Pendulum\MC-RCN-00-06-2CL-TS-SimpleME-SimpleA-woBranches-wRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, EngineControlRangeAfferent.NegIntervalSeparator21 (и еще 19)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent.MotionElement1, EngineControlRangeAfferent.MotionElement2, MotionElement0, MotionElement1 (и еще 1)
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.RenshowL, EngineControlRangeAfferent.MotionElement0.RenshowR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1 (и еще 59)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowL.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone (и еще 67)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTMembrane, EngineControlRangeAfferent.MotionElement0.RenshowL.LTMembrane, EngineControlRangeAfferent.MotionElement0.RenshowR.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTMembrane (и еще 67)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator (и еще 67)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator (и еще 67)
- **NPNewSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane (и еще 67)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone, EngineControlRangeAfferent.MotionElement1.AfferentR1.LTZone (и еще 27)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel (и еще 427)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor (и еще 35)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.MotionElement1.AfferentR1 (и еще 27)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentSource1`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataInput0`
- ... (всего 418 входов)

**Выходы системы:**
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel.DataOutput0`
- ... (всего 213 выходов)

**Количество связей:** 266

**Описание:** 2 Control loops: angle, angle speed
Simple Motion Element
New neurons (with temporal summation)    
Simple Afferents
With Post Afferents
Without Branches
With Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-07-2CL-SimpleME-FullA-woBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-2CL-All-Pendulum\MC-RCN-00-07-2CL-SimpleME-FullA-woBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, EngineControlRangeAfferent.NegIntervalSeparator21 (и еще 19)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent.MotionElement1, EngineControlRangeAfferent.MotionElement2, MotionElement0, MotionElement1 (и еще 1)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone (и еще 83)
- **NPNeuronChannel**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel (и еще 123)
- **NPNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentR2.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentL2.PNeuronMembrane, EngineControlRangeAfferent.MotionElement1.AfferentR1.PNeuronMembrane (и еще 27)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR2.PNeuronNegCGenerator (и еще 83)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR2.PNeuronPosCGenerator (и еще 83)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane.PosChannel (и еще 219)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronMembrane (и еще 51)
- **NPSynapse**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse2, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse3, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse2 (и еще 715)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor (и еще 35)
- **NSAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.MotionElement1.AfferentR1 (и еще 27)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotionElement0.PostAfferentL2 (и еще 43)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentL1.PNeuronNegCGenerator`
- `AfferentL1.PNeuronPosCGenerator`
- `AfferentL2.PNeuronNegCGenerator`
- `AfferentL2.PNeuronPosCGenerator`
- `AfferentR1.PNeuronNegCGenerator`
- `AfferentR1.PNeuronPosCGenerator`
- `AfferentR2.PNeuronNegCGenerator`
- `AfferentR2.PNeuronPosCGenerator`
- `AfferentSource1`
- `EngineControlRangeAfferent.AfferentL1.PNeuronNegCGenerator`
- ... (всего 408 входов)

**Выходы системы:**
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronNegCGenerator.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.PNeuronNegCGenerator.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataOutput0`
- ... (всего 171 выходов)

**Количество связей:** 224

**Описание:** 2 Control loops: angle, angle speed
Simple Motion Element
Full Afferents
With Post Afferents
Without Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-08-2CL-SimpleME-FullA-wBranches-woRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-2CL-All-Pendulum\MC-RCN-00-08-2CL-SimpleME-FullA-wBranches-woRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, EngineControlRangeAfferent.NegIntervalSeparator21 (и еще 19)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent.MotionElement1, EngineControlRangeAfferent.MotionElement2, MotionElement0, MotionElement1 (и еще 1)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone (и еще 83)
- **NPNeuronChannel**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel (и еще 123)
- **NPNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentR2.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentL2.PNeuronMembrane, EngineControlRangeAfferent.MotionElement1.AfferentR1.PNeuronMembrane (и еще 27)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR2.PNeuronNegCGenerator (и еще 83)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR2.PNeuronPosCGenerator (и еще 83)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane3.PosChannel (и еще 315)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane3, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane2 (и еще 99)
- **NPSynapse**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse2, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse3, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse2 (и еще 715)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor (и еще 35)
- **NSAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.MotionElement1.AfferentR1 (и еще 27)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotionElement0.PostAfferentL2 (и еще 43)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentL1.PNeuronNegCGenerator`
- `AfferentL1.PNeuronPosCGenerator`
- `AfferentL2.PNeuronNegCGenerator`
- `AfferentL2.PNeuronPosCGenerator`
- `AfferentR1.PNeuronNegCGenerator`
- `AfferentR1.PNeuronPosCGenerator`
- `AfferentR2.PNeuronNegCGenerator`
- `AfferentR2.PNeuronPosCGenerator`
- `AfferentSource1`
- `EngineControlRangeAfferent.AfferentL1.PNeuronNegCGenerator`
- ... (всего 468 входов)

**Выходы системы:**
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronNegCGenerator.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.PNeuronNegCGenerator.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataOutput0`
- ... (всего 195 выходов)

**Количество связей:** 284

**Описание:** 2 Control loops: angle, angle speed
Simple Motion Element
Full Afferents
With Post Afferents
With Branches
Without Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-09-2CL-SimpleME-FullA-woBranches-wRenshow-wPA

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-2CL-All-Pendulum\MC-RCN-00-09-2CL-SimpleME-FullA-woBranches-wRenshow-wPA`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Название проекта:** Num motion elements test

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, EngineControlRangeAfferent.NegIntervalSeparator21 (и еще 19)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent.MotionElement1, EngineControlRangeAfferent.MotionElement2, MotionElement0, MotionElement1 (и еще 1)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowL.LTZone, EngineControlRangeAfferent.MotionElement0.RenshowR.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone (и еще 99)
- **NPNeuronChannel**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.PosChannel, EngineControlRangeAfferent.MotionElement0.AfferentR1.NegChannel, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel (и еще 123)
- **NPNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentR2.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentL2.PNeuronMembrane, EngineControlRangeAfferent.MotionElement1.AfferentR1.PNeuronMembrane (и еще 27)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronNegCGenerator (и еще 99)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronPosCGenerator (и еще 99)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane.PosChannel (и еще 283)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.RenshowR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane (и еще 67)
- **NPSynapse**: EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse2, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.PosChannel.Synapse3, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane.NegChannel.Synapse2 (и еще 715)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor (и еще 35)
- **NSAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.MotionElement1.AfferentR1 (и еще 27)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.RenshowL, EngineControlRangeAfferent.MotionElement0.RenshowR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1 (и еще 59)
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentL1.PNeuronNegCGenerator`
- `AfferentL1.PNeuronPosCGenerator`
- `AfferentL2.PNeuronNegCGenerator`
- `AfferentL2.PNeuronPosCGenerator`
- `AfferentR1.PNeuronNegCGenerator`
- `AfferentR1.PNeuronPosCGenerator`
- `AfferentR2.PNeuronNegCGenerator`
- `AfferentR2.PNeuronPosCGenerator`
- `AfferentSource1`
- `EngineControlRangeAfferent.AfferentL1.PNeuronNegCGenerator`
- ... (всего 482 входов)

**Выходы системы:**
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronNegCGenerator.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.PNeuronMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.PNeuronMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.PNeuronNegCGenerator.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataOutput0`
- ... (всего 201 выходов)

**Количество связей:** 266

**Описание:** 2 Control loops: angle, angle speed
Simple Motion Element
Full Afferents
With Post Afferents
Without Branches
With Renshow cells

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### MC-RCN-00-2CL-Old

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-2CL-All-Pendulum\MC-RCN-00-2CL-Old`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfNewSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: CGenerator, EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, EngineControlRangeAfferent.NegIntervalSeparator13 (и еще 11)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTZone (и еще 39)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronNegCGenerator (и еще 39)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronPosCGenerator (и еще 39)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR3.LTZone (и еще 27)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane.PosChannel (и еще 171)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronMembrane (и еще 39)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR3.Receptor (и еще 31)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.MotionElement0.AfferentR3 (и еще 27)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotionElement0.PostAfferentL2 (и еще 35)

**Входы системы:**
- `AfferentSource1`
- `CGenerator`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataInput0`
- ... (всего 203 входов)

**Выходы системы:**
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL3.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL3.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL4.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL4.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- ... (всего 84 выходов)

**Количество связей:** 109

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

## MC-RCN-00-MotionElementsComparation-DcEngine

### MultiComparation

**Путь:** `Bin\Configs\!OldConfigs\MC-RCN\MC-RCN-00-MotionElementsComparation-DcEngine\MultiComparation`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfNewSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent5
- **N2AsfSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent6
- **NAsfNewSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NAsfNewSimplestAfferentBranchedMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent.MotionElement1, EngineControlRangeAfferent.MotionElement2
- **NBranchedCrosslinksEngineControlRangeAfferent**: EngineControlRangeAfferent3
- **NBranchedEngineControlRangeAfferent**: EngineControlRangeAfferent2
- **NBranchedMotionElement**: EngineControlRangeAfferent2.MotionElement0, EngineControlRangeAfferent3.MotionElement0
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, EngineControlRangeAfferent2.AfferentSource1, EngineControlRangeAfferent3.AfferentSource1, EngineControlRangeAfferent4.AfferentSource1, EngineControlRangeAfferent5.AfferentSource1 (и еще 2)
- **NControlObjectSource**: EngineControlRangeAfferent6.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine, DCEngine2, DCEngine3, DCEngine4, DCEngine5 (и еще 1)
- **NEngineControlRangeAfferent**: EngineControlRangeAfferent4
- **NFrequencyReceiver**: EngineControlRangeAfferent2.PosMNFrequencyReceiver1, EngineControlRangeAfferent2.NegMNFrequencyReceiver1, EngineControlRangeAfferent3.PosMNFrequencyReceiver1, EngineControlRangeAfferent3.NegMNFrequencyReceiver1, EngineControlRangeAfferent4.PosMNFrequencyReceiver1 (и еще 3)
- **NIntervalSeparator**: EngineControlRangeAfferent.Ib_NegIntervalSeparator1, EngineControlRangeAfferent.Ib_NegIntervalSeparator2, EngineControlRangeAfferent.Ib_NegIntervalSeparator3, EngineControlRangeAfferent.Ib_PosIntervalSeparator1, EngineControlRangeAfferent.Ib_PosIntervalSeparator2 (и еще 95)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, EngineControlRangeAfferent2.NManipulatorInput1, EngineControlRangeAfferent3.NManipulatorInput1, EngineControlRangeAfferent4.NManipulatorInput1, EngineControlRangeAfferent5.NManipulatorInput1 (и еще 2)
- **NManipulatorSource**: EngineControlRangeAfferent.NManipulatorSource1, EngineControlRangeAfferent2.NManipulatorSource1, EngineControlRangeAfferent3.NManipulatorSource1, EngineControlRangeAfferent4.NManipulatorSource1, EngineControlRangeAfferent5.NManipulatorSource1
- **NMotionElement**: EngineControlRangeAfferent4.MotionElement0
- **NNewMotionElement**: EngineControlRangeAfferent5.MotionElement0, EngineControlRangeAfferent5.MotionElement1, EngineControlRangeAfferent5.MotionElement2, EngineControlRangeAfferent5.MotionElement3, EngineControlRangeAfferent5.MotionElement4 (и еще 8)
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.Motoneuron1, EngineControlRangeAfferent.MotionElement0.Motoneuron2, EngineControlRangeAfferent.MotionElement0.PostAfferent14, EngineControlRangeAfferent.MotionElement0.PostAfferent24, EngineControlRangeAfferent.MotionElement1.Motoneuron1 (и еще 35)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent2.IIPosAfferentGenerator, EngineControlRangeAfferent2.IINegAfferentGenerator, EngineControlRangeAfferent3.IIPosAfferentGenerator (и еще 12)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTZone, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTZone, EngineControlRangeAfferent.MotionElement1.Motoneuron1.LTZone (и еще 201)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTMembrane, EngineControlRangeAfferent.MotionElement0.LTMembrane (и еще 67)
- **NPNeuronChannel**: EngineControlRangeAfferent2.MotionElement0.Afferent_Ia1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent2.MotionElement0.Afferent_Ia1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent2.MotionElement0.Afferent_Ia1.PosChannel, EngineControlRangeAfferent2.MotionElement0.Afferent_Ia1.NegChannel, EngineControlRangeAfferent2.MotionElement0.Afferent_Ia2.PNeuronMembrane.PosChannel (и еще 211)
- **NPNeuronMembrane**: EngineControlRangeAfferent2.MotionElement0.Afferent_Ia1.PNeuronMembrane, EngineControlRangeAfferent2.MotionElement0.Afferent_Ia2.PNeuronMembrane, EngineControlRangeAfferent2.MotionElement0.Afferent_Ib1.PNeuronMembrane, EngineControlRangeAfferent2.MotionElement0.Afferent_Ib2.PNeuronMembrane, EngineControlRangeAfferent2.MotionElement0.Afferent_II1.PNeuronMembrane (и еще 49)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 221)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 221)
- **NPNewSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane3, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronMembrane2 (и еще 83)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_II2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.LTZone (и еще 107)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2.PosChannel (и еще 1295)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent2.MotionElement0.Renshow1.PNeuronMembrane, EngineControlRangeAfferent2.MotionElement0.Renshow1.PNeuronMembrane2, EngineControlRangeAfferent2.MotionElement0.Renshow2.PNeuronMembrane, EngineControlRangeAfferent2.MotionElement0.Renshow2.PNeuronMembrane2, EngineControlRangeAfferent2.MotionElement0.Motoneuron1.PNeuronMembrane (и еще 313)
- **NPSynapse**: EngineControlRangeAfferent2.MotionElement0.Afferent_Ia1.PNeuronMembrane.PosChannel.Synapse, EngineControlRangeAfferent2.MotionElement0.Afferent_Ia1.PNeuronMembrane.PosChannel.Synapse2, EngineControlRangeAfferent2.MotionElement0.Afferent_Ia1.PNeuronMembrane.PosChannel.Synapse3, EngineControlRangeAfferent2.MotionElement0.Afferent_Ia1.PNeuronMembrane.NegChannel.Synapse, EngineControlRangeAfferent2.MotionElement0.Afferent_Ia1.PNeuronMembrane.NegChannel.Synapse2 (и еще 1003)
- **NPac**: EngineControlRangeAfferent.Pac, EngineControlRangeAfferent2.Pac, EngineControlRangeAfferent3.Pac, EngineControlRangeAfferent4.Pac, EngineControlRangeAfferent5.Pac (и еще 2)
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_II2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.Receptor (и еще 161)
- **NSAfferentNeuron**: EngineControlRangeAfferent2.MotionElement0.Afferent_Ia1, EngineControlRangeAfferent2.MotionElement0.Afferent_Ia2, EngineControlRangeAfferent2.MotionElement0.Afferent_Ib1, EngineControlRangeAfferent2.MotionElement0.Afferent_Ib2, EngineControlRangeAfferent2.MotionElement0.Afferent_II1 (и еще 43)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.Afferent_II1, EngineControlRangeAfferent.MotionElement0.Afferent_II2, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1 (и еще 87)
- **NSynMotoneuron**: EngineControlRangeAfferent4.MotionElement0.Motoneuron1, EngineControlRangeAfferent4.MotionElement0.Motoneuron2, EngineControlRangeAfferent4.Motoneuron1, EngineControlRangeAfferent4.Motoneuron2, MotionElement0.Motoneuron1 (и еще 3)
- **NSynRenshowCell**: EngineControlRangeAfferent4.MotionElement0.Renshow1, EngineControlRangeAfferent4.MotionElement0.Renshow2, EngineControlRangeAfferent4.Renshow1, EngineControlRangeAfferent4.Renshow2, MotionElement0.Renshow1 (и еще 3)
- **NSynSPNeuron**: EngineControlRangeAfferent2.MotionElement0.Renshow1, EngineControlRangeAfferent2.MotionElement0.Renshow2, EngineControlRangeAfferent2.MotionElement0.Motoneuron1, EngineControlRangeAfferent2.MotionElement0.Motoneuron2, EngineControlRangeAfferent2.MotionElement0.PostAfferent11 (и еще 91)

**Входы системы:**
- `AfferentSource1`
- `Afferent_II1.PNeuronNegCGenerator`
- `Afferent_II1.PNeuronPosCGenerator`
- `Afferent_II2.PNeuronNegCGenerator`
- `Afferent_II2.PNeuronPosCGenerator`
- `Afferent_Ia1.PNeuronNegCGenerator`
- `Afferent_Ia1.PNeuronPosCGenerator`
- `Afferent_Ia2.PNeuronNegCGenerator`
- `Afferent_Ia2.PNeuronPosCGenerator`
- `Afferent_Ib1.PNeuronNegCGenerator`
- ... (всего 1644 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `DCEngine2.DataOutput0`
- `DCEngine2.DataOutput1`
- `DCEngine2.DataOutput2`
- `DCEngine3.DataOutput0`
- `DCEngine3.DataOutput1`
- `DCEngine3.DataOutput2`
- `DCEngine4.DataOutput0`
- ... (всего 748 выходов)

**Количество связей:** 1174

---

## MotionControl_Test

### MotionControl_Test

**Путь:** `Bin\Configs\a.demcheva\MotionControl_Test\MotionControl_Test`

**Назначение:** Система управления движением

**Основные компоненты:**
- **NCGenerator**: AngleGen, VoltageGen, EngineMotionControl.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineMotionControl.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NEngineMotionControl**: EngineMotionControl
- **NIntervalSeparator**: IntervalSeparator, IntervalSeparator2, EngineMotionControl.NegIntervalSeparator11, EngineMotionControl.PosIntervalSeparator11, NegIntervalSeparator11 (и еще 1)
- **NManipulatorInput**: ManipulatorInput, EngineMotionControl.NManipulatorInput1, NManipulatorInput1
- **NManipulatorSource**: ManipulatorSource
- **NNewMotionElement**: MotionElement, EngineMotionControl.MotionElement0, MotionElement0
- **NNewSPNeuron**: MotionElement.MotoneuronL, MotionElement.MotoneuronR, MotionElement.PostAfferentL1, MotionElement.PostAfferentR1, EngineMotionControl.MotionElement0.MotoneuronL (и еще 9)
- **NPExcChannel**: MotionElement.MotoneuronL.Soma1.ExcChannel, MotionElement.MotoneuronR.Soma1.ExcChannel, MotionElement.PostAfferentL1.Soma1.ExcChannel, MotionElement.PostAfferentR1.Soma1.ExcChannel, MotionElement.Soma1.ExcChannel (и еще 14)
- **NPGenerator**: MotionElement.AfferentR1.LTZone.PGenerator, MotionElement.AfferentR1.PGenerator, MotionElement.AfferentL1.LTZone.PGenerator, MotionElement.AfferentL1.PGenerator, MotionElement.LTZone.PGenerator (и еще 31)
- **NPInhChannel**: MotionElement.MotoneuronL.Soma1.InhChannel, MotionElement.MotoneuronR.Soma1.InhChannel, MotionElement.PostAfferentL1.Soma1.InhChannel, MotionElement.PostAfferentR1.Soma1.InhChannel, MotionElement.Soma1.InhChannel (и еще 14)
- **NPLTExcChannel**: MotionElement.MotoneuronL.LTMembrane.ExcChannel, MotionElement.MotoneuronL.ExcChannel, MotionElement.MotoneuronR.LTMembrane.ExcChannel, MotionElement.MotoneuronR.ExcChannel, MotionElement.PostAfferentL1.LTMembrane.ExcChannel (и еще 33)
- **NPLTInhChannel**: MotionElement.MotoneuronL.LTMembrane.InhChannel, MotionElement.MotoneuronL.InhChannel, MotionElement.MotoneuronR.LTMembrane.InhChannel, MotionElement.MotoneuronR.InhChannel, MotionElement.PostAfferentL1.LTMembrane.InhChannel (и еще 33)
- **NPLTZone**: MotionElement.MotoneuronL.LTZone, MotionElement.MotoneuronR.LTZone, MotionElement.PostAfferentL1.LTZone, MotionElement.PostAfferentR1.LTZone, MotionElement.LTZone (и еще 10)
- **NPLTZoneNeuronMembrane**: MotionElement.MotoneuronL.LTMembrane, MotionElement.MotoneuronR.LTMembrane, MotionElement.PostAfferentL1.LTMembrane, MotionElement.PostAfferentR1.LTMembrane, MotionElement.LTMembrane (и еще 14)
- **NPMembrane**: MotionElement.MotoneuronL.Soma1, MotionElement.MotoneuronR.Soma1, MotionElement.PostAfferentL1.Soma1, MotionElement.PostAfferentR1.Soma1, MotionElement.Soma1 (и еще 14)
- **NPNeuronNegCGenerator**: MotionElement.MotoneuronL.NegGenerator, MotionElement.MotoneuronR.NegGenerator, MotionElement.PostAfferentL1.NegGenerator, MotionElement.PostAfferentR1.NegGenerator, MotionElement.NegGenerator (и еще 14)
- **NPNeuronPosCGenerator**: MotionElement.MotoneuronL.PosGenerator, MotionElement.MotoneuronR.PosGenerator, MotionElement.PostAfferentL1.PosGenerator, MotionElement.PostAfferentR1.PosGenerator, MotionElement.PosGenerator (и еще 14)
- **NPSimpleLTZone**: MotionElement.AfferentR1.LTZone, MotionElement.AfferentL1.LTZone, EngineMotionControl.MotionElement0.AfferentR1.LTZone, EngineMotionControl.MotionElement0.AfferentL1.LTZone, EngineMotionControl.MotionElement0.LTZone (и еще 9)
- **NPSynapse**: MotionElement.MotoneuronL.Soma1.ExcSynapse1, MotionElement.MotoneuronL.Soma1.InhSynapse1, MotionElement.MotoneuronL.LTMembrane.ExcSynapse1, MotionElement.MotoneuronL.LTMembrane.InhSynapse1, MotionElement.MotoneuronL.ExcSynapse1 (и еще 109)
- **NPac**: Pac, EngineMotionControl.Pac
- **NReceptor**: MotionElement.AfferentR1.Receptor, MotionElement.AfferentL1.Receptor, MotionElement.Receptor, EngineMotionControl.MotionElement0.AfferentR1.Receptor, EngineMotionControl.MotionElement0.AfferentL1.Receptor (и еще 10)
- **NSimpleAfferentNeuron**: MotionElement.AfferentR1, MotionElement.AfferentL1, EngineMotionControl.MotionElement0.AfferentR1, EngineMotionControl.MotionElement0.AfferentL1, EngineMotionControl.AfferentR1 (и еще 5)
- **UStatisticDoubleMatrix**: EngineMotionControl.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentL1.LTZone.PGenerator`
- `AfferentL1.PGenerator`
- `AfferentR1.LTZone.PGenerator`
- `AfferentR1.PGenerator`
- `AfferentSource1`
- `AngleGen`
- `DCEngine.InputVoltage`
- `EngineMotionControl.AfferentL1.LTZone.PGenerator`
- `EngineMotionControl.AfferentL1.PGenerator`
- `EngineMotionControl.AfferentR1.LTZone.PGenerator`
- ... (всего 167 входов)

**Выходы системы:**
- `DCEngine.OutputAngle`
- `EngineMotionControl.MotionElement0.AfferentL1.LTZone.Output`
- `EngineMotionControl.MotionElement0.AfferentL1.Receptor.Output`
- `EngineMotionControl.MotionElement0.AfferentR1.LTZone.Output`
- `EngineMotionControl.MotionElement0.AfferentR1.Receptor.Output`
- `EngineMotionControl.MotionElement0.MotoneuronL.LTMembrane.ExcChannel.Output`
- `EngineMotionControl.MotionElement0.MotoneuronL.LTMembrane.ExcSynapse1.Output`
- `EngineMotionControl.MotionElement0.MotoneuronL.LTMembrane.InhChannel.Output`
- `EngineMotionControl.MotionElement0.MotoneuronL.LTMembrane.InhSynapse1.Output`
- `EngineMotionControl.MotionElement0.MotoneuronL.LTZone.Output`
- ... (всего 84 выходов)

**Количество связей:** 97

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

## NM-AfferentNeurons

### NM-AN-00-AfferentModelComparation

**Путь:** `Bin\Configs\!OldConfigs\NM-AfferentNeurons\NM-AN-00-AfferentModelComparation`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NCGenerator**: CGenerator
- **NPExcChannel**: AfferentNeuron.PMembrane.ExcChannel, AfferentNeuron.ExcChannel, PMembrane.ExcChannel, ExcChannel
- **NPGenerator**: AfferentNeuron2.LTZone.PGenerator, AfferentNeuron2.PGenerator, LTZone.PGenerator, PGenerator
- **NPInhChannel**: AfferentNeuron.PMembrane.InhChannel, AfferentNeuron.InhChannel, PMembrane.InhChannel, InhChannel
- **NPLTZone**: AfferentNeuron.LTZone, LTZone
- **NPMembrane**: AfferentNeuron.PMembrane, PMembrane
- **NPNeuronNegCGenerator**: AfferentNeuron.NegGenerator, NegGenerator
- **NPSimpleLTZone**: AfferentNeuron2.LTZone
- **NPSynapse**: AfferentNeuron.PMembrane.ExcSynapse, AfferentNeuron.PMembrane.InhSynapse, AfferentNeuron.ExcSynapse, AfferentNeuron.InhSynapse, PMembrane.ExcSynapse (и еще 3)
- **NReceptor**: AfferentNeuron2.Receptor, AfferentNeuron.Receptor, Receptor
- **NSAfferentNeuron**: AfferentNeuron
- **NSimpleAfferentNeuron**: AfferentNeuron2

**Входы системы:**
- `AfferentNeuron.LTZone.Inputs`
- `AfferentNeuron.NegGenerator`
- `AfferentNeuron.PMembrane.ExcChannel.ChannelInputs`
- `AfferentNeuron.PMembrane.ExcChannel.SynapticInputs`
- `AfferentNeuron.PMembrane.InhChannel.ChannelInputs`
- `AfferentNeuron.PMembrane.InhChannel.SynapticInputs`
- `AfferentNeuron.PMembrane.InputFeedbackSignal`
- `AfferentNeuron.Receptor.Input`
- `AfferentNeuron2.LTZone.Inputs`
- `AfferentNeuron2.LTZone.PGenerator`
- ... (всего 16 входов)

**Выходы системы:**
- `AfferentNeuron.LTZone.Output`
- `AfferentNeuron.NegGenerator.Output`
- `AfferentNeuron.PMembrane.ExcChannel.Output`
- `AfferentNeuron.PMembrane.ExcSynapse.Output`
- `AfferentNeuron.PMembrane.InhChannel.Output`
- `AfferentNeuron.PMembrane.InhSynapse.Output`
- `AfferentNeuron.Receptor.Output`
- `AfferentNeuron2.Receptor.Output`
- `CGenerator.Output`

**Количество связей:** 10

**Описание:** Compare activity of the next afferent neuron models:
- Based on the membrane and LT-zone models (class NSAfferentNeuron).
- Based on simple pulse generator (class NSimpleAfferentNeuron).

---

### NM-AN-01-NSAfferentNeuron

**Путь:** `Bin\Configs\!OldConfigs\NM-AfferentNeurons\NM-AN-01-NSAfferentNeuron`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NCGenerator**: CGenerator
- **NPExcChannel**: AfferentNeuron.PMembrane.ExcChannel, AfferentNeuron.ExcChannel, PMembrane.ExcChannel, ExcChannel
- **NPInhChannel**: AfferentNeuron.PMembrane.InhChannel, AfferentNeuron.InhChannel, PMembrane.InhChannel, InhChannel
- **NPLTZone**: AfferentNeuron.LTZone, LTZone
- **NPMembrane**: AfferentNeuron.PMembrane, PMembrane
- **NPNeuronNegCGenerator**: AfferentNeuron.NegGenerator, NegGenerator
- **NPSynapse**: AfferentNeuron.PMembrane.ExcSynapse, AfferentNeuron.PMembrane.InhSynapse, AfferentNeuron.ExcSynapse, AfferentNeuron.InhSynapse, PMembrane.ExcSynapse (и еще 3)
- **NReceptor**: AfferentNeuron.Receptor, Receptor
- **NSAfferentNeuron**: AfferentNeuron

**Входы системы:**
- `AfferentNeuron.LTZone.Inputs`
- `AfferentNeuron.NegGenerator`
- `AfferentNeuron.PMembrane.ExcChannel.ChannelInputs`
- `AfferentNeuron.PMembrane.ExcChannel.SynapticInputs`
- `AfferentNeuron.PMembrane.InhChannel.ChannelInputs`
- `AfferentNeuron.PMembrane.InhChannel.SynapticInputs`
- `AfferentNeuron.PMembrane.InputFeedbackSignal`
- `AfferentNeuron.Receptor.Input`
- `CGenerator`
- `NegGenerator`

**Выходы системы:**
- `AfferentNeuron.LTZone.Output`
- `AfferentNeuron.NegGenerator.Output`
- `AfferentNeuron.PMembrane.ExcChannel.Output`
- `AfferentNeuron.PMembrane.ExcSynapse.Output`
- `AfferentNeuron.PMembrane.InhChannel.Output`
- `AfferentNeuron.PMembrane.InhSynapse.Output`
- `AfferentNeuron.Receptor.Output`
- `CGenerator.Output`

**Количество связей:** 8

**Описание:** Based on the membrane and LT-zone models (class NSAfferentNeuron).

---

### NM-AN-02-NSimpleAfferentNeuron

**Путь:** `Bin\Configs\!OldConfigs\NM-AfferentNeurons\NM-AN-02-NSimpleAfferentNeuron`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NCGenerator**: CGenerator
- **NEyeMuscle**: EyeMuscle
- **NPGenerator**: AfferentNeuron.LTZone.PGenerator, AfferentNeuron.PGenerator, LTZone.PGenerator, PGenerator
- **NPSimpleLTZone**: AfferentNeuron.LTZone, LTZone
- **NReceptor**: AfferentNeuron.Receptor, Receptor
- **NSimpleAfferentNeuron**: AfferentNeuron

**Входы системы:**
- `AfferentNeuron.LTZone.Inputs`
- `AfferentNeuron.LTZone.PGenerator`
- `AfferentNeuron.PGenerator`
- `AfferentNeuron.Receptor.Input`
- `CGenerator`
- `EyeMuscle.Inputs`
- `LTZone.PGenerator`
- `PGenerator`

**Выходы системы:**
- `AfferentNeuron.LTZone.Output`
- `AfferentNeuron.Receptor.Output`
- `CGenerator.Output`

**Количество связей:** 3

**Описание:** Based on simple pulse generator (class NSimpleAfferentNeuron).

---

## NM-Neurons

### NM-PN-01-HebbNeuron-1M1St1In1

**Путь:** `Bin\Configs\!OldConfigs\NM-Neurons\NM-PN-01-HebbNeuron-1M1St1In1`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPExcChannel**: PHebbNeuron.Soma1.ExcChannel, PHebbNeuron.ExcChannel, Soma1.ExcChannel, ExcChannel
- **NPGenerator**: PosPGenerator, NegPGenerator
- **NPHebbNeuron**: PHebbNeuron
- **NPHebbSynapse**: PHebbNeuron.Soma1.ExcSynapse, PHebbNeuron.Soma1.InhSynapse, PHebbNeuron.ExcSynapse, PHebbNeuron.InhSynapse, Soma1.ExcSynapse (и еще 3)
- **NPInhChannel**: PHebbNeuron.Soma1.InhChannel, PHebbNeuron.InhChannel, Soma1.InhChannel, InhChannel
- **NPLTExcChannel**: PHebbNeuron.LTMembrane.ExcChannel, LTMembrane.ExcChannel
- **NPLTInhChannel**: PHebbNeuron.LTMembrane.InhChannel, LTMembrane.InhChannel
- **NPLTZone**: PHebbNeuron.LTZone, LTZone
- **NPLTZoneNeuronMembrane**: PHebbNeuron.LTMembrane, LTMembrane
- **NPNeuronHebbMembrane**: PHebbNeuron.Soma1, Soma1
- **NPNeuronNegCGenerator**: PHebbNeuron.NegGenerator, NegGenerator
- **NPNeuronPosCGenerator**: PHebbNeuron.PosGenerator, PosGenerator
- **NPSynapse**: PHebbNeuron.LTMembrane.ExcSynapse, PHebbNeuron.LTMembrane.InhSynapse, LTMembrane.ExcSynapse, LTMembrane.InhSynapse
- **UStatisticDoubleMatrix**: StatisticDoubleMatrix

**Входы системы:**
- `NegGenerator`
- `NegPGenerator`
- `PHebbNeuron.LTMembrane.ExcChannel.ChannelInputs`
- `PHebbNeuron.LTMembrane.ExcChannel.SynapticInputs`
- `PHebbNeuron.LTMembrane.InhChannel.ChannelInputs`
- `PHebbNeuron.LTMembrane.InhChannel.SynapticInputs`
- `PHebbNeuron.LTMembrane.InputFeedbackSignal`
- `PHebbNeuron.LTZone.Inputs`
- `PHebbNeuron.NegGenerator`
- `PHebbNeuron.PosGenerator`
- ... (всего 19 входов)

**Выходы системы:**
- `NegPGenerator.DataOutput0`
- `NegPGenerator.Output`
- `PHebbNeuron.LTMembrane.ExcChannel.Output`
- `PHebbNeuron.LTMembrane.ExcSynapse.Output`
- `PHebbNeuron.LTMembrane.InhChannel.Output`
- `PHebbNeuron.LTMembrane.InhSynapse.Output`
- `PHebbNeuron.LTZone.Output`
- `PHebbNeuron.NegGenerator.Output`
- `PHebbNeuron.PosGenerator.Output`
- `PHebbNeuron.Soma1.ExcChannel.Output`
- ... (всего 15 выходов)

**Количество связей:** 16

---

### NM-PN-01-Neuron-1M1St1In1

**Путь:** `Bin\Configs\!OldConfigs\NM-Neurons\NM-PN-01-Neuron-1M1St1In1`

**Назначение:** Модель LIF нейрона

**Основные компоненты:**
- **NPExcChannel**: PNeuron.LTMembrane.ExcChannel, PNeuron.Soma1.ExcChannel, PNeuron.ExcChannel, LTMembrane.ExcChannel, Soma1.ExcChannel (и еще 1)
- **NPGenerator**: PosPGenerator, NegPGenerator
- **NPInhChannel**: PNeuron.LTMembrane.InhChannel, PNeuron.Soma1.InhChannel, PNeuron.InhChannel, LTMembrane.InhChannel, Soma1.InhChannel (и еще 1)
- **NPLTZone**: PNeuron.LTZone, LTZone
- **NPLTZoneNeuronMembrane**: PNeuron.LTMembrane, LTMembrane
- **NPMembrane**: PNeuron.Soma1, Soma1
- **NPNeuron**: PNeuron
- **NPNeuronNegCGenerator**: PNeuron.NegGenerator, NegGenerator
- **NPNeuronPosCGenerator**: PNeuron.PosGenerator, PosGenerator
- **NPSynapse**: PNeuron.Soma1.ExcSynapse, PNeuron.Soma1.InhSynapse, PNeuron.ExcSynapse, PNeuron.InhSynapse, Soma1.ExcSynapse (и еще 3)
- **UStatisticDoubleMatrix**: StatisticDoubleMatrix

**Входы системы:**
- `NegGenerator`
- `NegPGenerator`
- `PNeuron.LTMembrane.ExcChannel.ChannelInputs`
- `PNeuron.LTMembrane.InhChannel.ChannelInputs`
- `PNeuron.LTMembrane.InputFeedbackSignal`
- `PNeuron.LTZone.Inputs`
- `PNeuron.NegGenerator`
- `PNeuron.PosGenerator`
- `PNeuron.Soma1.ExcChannel.ChannelInputs`
- `PNeuron.Soma1.ExcChannel.SynapticInputs`
- ... (всего 17 входов)

**Выходы системы:**
- `NegPGenerator.DataOutput0`
- `NegPGenerator.Output`
- `PNeuron.LTMembrane.ExcChannel.Output`
- `PNeuron.LTMembrane.InhChannel.Output`
- `PNeuron.LTZone.Output`
- `PNeuron.NegGenerator.Output`
- `PNeuron.PosGenerator.Output`
- `PNeuron.Soma1.ExcChannel.Output`
- `PNeuron.Soma1.ExcSynapse.Output`
- `PNeuron.Soma1.InhChannel.Output`
- ... (всего 13 выходов)

**Количество связей:** 13

---

### NM-PN-02-Neuron-1M1St3In3

**Путь:** `Bin\Configs\!OldConfigs\NM-Neurons\NM-PN-02-Neuron-1M1St3In3`

**Назначение:** Модель LIF нейрона

**Название проекта:** Minimalistic neuron

**Количество каналов:** 0

**Основные компоненты:**
- **NPGenerator**: PosPGenerator, NegPGenerator
- **NPLTZone**: Neuron.LTZone, LTZone
- **NPNeuronChannel**: Neuron.PNeuronMembrane.PosChannel, Neuron.PNeuronMembrane.NegChannel, Neuron.PosChannel, Neuron.NegChannel, PNeuronMembrane.PosChannel (и еще 3)
- **NPNeuronMembrane**: Neuron.PNeuronMembrane, PNeuronMembrane
- **NPNeuronNegCGenerator**: Neuron.PNeuronNegCGenerator, PNeuronNegCGenerator
- **NPNeuronPosCGenerator**: Neuron.PNeuronPosCGenerator, PNeuronPosCGenerator
- **NPSynapse**: Neuron.PNeuronMembrane.PosChannel.Synapse, Neuron.PNeuronMembrane.PosChannel.Synapse2, Neuron.PNeuronMembrane.PosChannel.Synapse3, Neuron.PNeuronMembrane.NegChannel.Synapse, Neuron.PNeuronMembrane.NegChannel.Synapse2 (и еще 31)
- **NSPNeuron**: Neuron
- **UStatisticDoubleMatrix**: StatisticDoubleMatrix

**Входы системы:**
- `NegPGenerator`
- `Neuron.LTZone.DataInput0`
- `Neuron.LTZone.DataInput1`
- `Neuron.PNeuronMembrane.DataInput0`
- `Neuron.PNeuronMembrane.NegChannel.DataInput0`
- `Neuron.PNeuronMembrane.NegChannel.Synapse.DataInput0`
- `Neuron.PNeuronMembrane.PosChannel.DataInput0`
- `Neuron.PNeuronMembrane.PosChannel.Synapse.DataInput0`
- `Neuron.PNeuronNegCGenerator`
- `Neuron.PNeuronPosCGenerator`
- ... (всего 14 входов)

**Выходы системы:**
- `NegPGenerator.DataOutput0`
- `Neuron.LTZone.DataOutput0`
- `Neuron.LTZone.DataOutput1`
- `Neuron.LTZone.DataOutput2`
- `Neuron.LTZone.DataOutput3`
- `Neuron.PNeuronMembrane.NegChannel.DataOutput0`
- `Neuron.PNeuronMembrane.PosChannel.DataOutput0`
- `Neuron.PNeuronNegCGenerator.DataOutput0`
- `Neuron.PNeuronPosCGenerator.DataOutput0`
- `PosPGenerator.DataOutput0`

**Количество связей:** 13

---

### NM-PN-03-Neuron-4M4D3St3In

**Путь:** `Bin\Configs\!OldConfigs\NM-Neurons\NM-PN-03-Neuron-4M4D3St3In`

**Назначение:** Модель LIF нейрона

**Название проекта:** Minimalistic neuron

**Количество каналов:** 0

**Основные компоненты:**
- **NPGenerator**: PosPGenerator11, NegPGenerator11, PosPGenerator12, PosPGenerator13, PosPGenerator14 (и еще 5)
- **NPLTZone**: Neuron.LTZone, LTZone
- **NPNeuron4x4**: Neuron
- **NPNeuronChannel**: Neuron.PNeuronMembrane11.PosChannel, Neuron.PNeuronMembrane11.NegChannel, Neuron.PNeuronMembrane12.PosChannel, Neuron.PNeuronMembrane12.NegChannel, Neuron.PNeuronMembrane13.PosChannel (и еще 63)
- **NPNeuronMembrane**: Neuron.PNeuronMembrane11, Neuron.PNeuronMembrane12, Neuron.PNeuronMembrane13, Neuron.PNeuronMembrane14, Neuron.PNeuronMembrane21 (и еще 27)
- **NPNeuronNegCGenerator**: Neuron.PNeuronNegCGenerator, PNeuronNegCGenerator
- **NPNeuronPosCGenerator**: Neuron.PNeuronPosCGenerator, PNeuronPosCGenerator
- **NPSynapse**: Neuron.PNeuronMembrane11.PosChannel.Synapse, Neuron.PNeuronMembrane11.PosChannel.Synapse2, Neuron.PNeuronMembrane11.PosChannel.Synapse3, Neuron.PNeuronMembrane11.NegChannel.Synapse, Neuron.PNeuronMembrane11.NegChannel.Synapse2 (и еще 301)
- **UStatisticDoubleMatrix**: StatisticDoubleMatrix

**Входы системы:**
- `NegPGenerator11`
- `NegPGenerator12`
- `NegPGenerator13`
- `NegPGenerator14`
- `NegPGenerator24`
- `Neuron.LTZone.DataInput0`
- `Neuron.LTZone.DataInput1`
- `Neuron.LTZone.DataInput2`
- `Neuron.LTZone.DataInput3`
- `Neuron.LTZone.DataInput4`
- ... (всего 69 входов)

**Выходы системы:**
- `NegPGenerator11.DataOutput0`
- `NegPGenerator12.DataOutput0`
- `NegPGenerator13.DataOutput0`
- `NegPGenerator14.DataOutput0`
- `NegPGenerator24.DataOutput0`
- `Neuron.LTZone.DataOutput0`
- `Neuron.LTZone.DataOutput1`
- `Neuron.LTZone.DataOutput2`
- `Neuron.PNeuronMembrane11.NegChannel.DataOutput0`
- `Neuron.PNeuronMembrane11.PosChannel.DataOutput0`
- ... (всего 47 выходов)

**Количество связей:** 65

---

### NM-PN-04-Neuron-3M1St3In3

**Путь:** `Bin\Configs\!OldConfigs\NM-Neurons\NM-PN-04-Neuron-3M1St3In3`

**Назначение:** Модель LIF нейрона

**Название проекта:** Minimalistic neuron

**Количество каналов:** 0

**Основные компоненты:**
- **NLPNeuron**: Neuron
- **NPGenerator**: PosPGenerator, NegPGenerator
- **NPLTZone**: Neuron.LTZone, LTZone
- **NPNeuronChannel**: Neuron.PNeuronMembrane.PosChannel, Neuron.PNeuronMembrane.NegChannel, Neuron.PNeuronMembrane2.PosChannel, Neuron.PNeuronMembrane2.NegChannel, Neuron.PNeuronMembrane3.PosChannel (и еще 11)
- **NPNeuronMembrane**: Neuron.PNeuronMembrane, Neuron.PNeuronMembrane2, Neuron.PNeuronMembrane3, PNeuronMembrane, PNeuronMembrane2 (и еще 1)
- **NPNeuronNegCGenerator**: Neuron.PNeuronNegCGenerator, PNeuronNegCGenerator
- **NPNeuronPosCGenerator**: Neuron.PNeuronPosCGenerator, PNeuronPosCGenerator
- **NPSynapse**: Neuron.PNeuronMembrane.PosChannel.Synapse, Neuron.PNeuronMembrane.PosChannel.Synapse2, Neuron.PNeuronMembrane.PosChannel.Synapse3, Neuron.PNeuronMembrane.NegChannel.Synapse, Neuron.PNeuronMembrane.NegChannel.Synapse2 (и еще 67)
- **UStatisticDoubleMatrix**: StatisticDoubleMatrix

**Входы системы:**
- `NegPGenerator`
- `Neuron.LTZone.DataInput0`
- `Neuron.LTZone.DataInput1`
- `Neuron.LTZone.DataInput2`
- `Neuron.LTZone.DataInput3`
- `Neuron.LTZone.DataInput4`
- `Neuron.LTZone.DataInput5`
- `Neuron.PNeuronMembrane.DataInput0`
- `Neuron.PNeuronMembrane.NegChannel.DataInput0`
- `Neuron.PNeuronMembrane.NegChannel.Synapse.DataInput0`
- ... (всего 24 входов)

**Выходы системы:**
- `NegPGenerator.DataOutput0`
- `Neuron.LTZone.DataOutput0`
- `Neuron.LTZone.DataOutput1`
- `Neuron.LTZone.DataOutput2`
- `Neuron.PNeuronMembrane.NegChannel.DataOutput0`
- `Neuron.PNeuronMembrane.PosChannel.DataOutput0`
- `Neuron.PNeuronMembrane2.NegChannel.DataOutput0`
- `Neuron.PNeuronMembrane2.PosChannel.DataOutput0`
- `Neuron.PNeuronMembrane3.NegChannel.DataOutput0`
- `Neuron.PNeuronMembrane3.PosChannel.DataOutput0`
- ... (всего 13 выходов)

**Количество связей:** 22

---

### NM-PN-05-Neuron-4M1D3St3In

**Путь:** `Bin\Configs\!OldConfigs\NM-Neurons\NM-PN-05-Neuron-4M1D3St3In`

**Назначение:** Модель LIF нейрона

**Название проекта:** Minimalistic neuron

**Количество каналов:** 0

**Основные компоненты:**
- **NPGenerator**: PosPGenerator11, NegPGenerator11, PosPGenerator12, PosPGenerator13, PosPGenerator14 (и еще 5)
- **NPLTZone**: Neuron.LTZone, LTZone
- **NPNeuron4x1**: Neuron
- **NPNeuronChannel**: Neuron.PNeuronMembrane11.PosChannel, Neuron.PNeuronMembrane11.NegChannel, Neuron.PNeuronMembrane12.PosChannel, Neuron.PNeuronMembrane12.NegChannel, Neuron.PNeuronMembrane13.PosChannel (и еще 27)
- **NPNeuronMembrane**: Neuron.PNeuronMembrane11, Neuron.PNeuronMembrane12, Neuron.PNeuronMembrane13, Neuron.PNeuronMembrane14, Neuron.PNeuronMembrane21 (и еще 9)
- **NPNeuronNegCGenerator**: Neuron.PNeuronNegCGenerator, PNeuronNegCGenerator
- **NPNeuronPosCGenerator**: Neuron.PNeuronPosCGenerator, PNeuronPosCGenerator
- **NPSynapse**: Neuron.PNeuronMembrane11.PosChannel.Synapse, Neuron.PNeuronMembrane11.PosChannel.Synapse2, Neuron.PNeuronMembrane11.PosChannel.Synapse3, Neuron.PNeuronMembrane11.NegChannel.Synapse, Neuron.PNeuronMembrane11.NegChannel.Synapse2 (и еще 139)
- **UStatisticDoubleMatrix**: StatisticDoubleMatrix

**Входы системы:**
- `NegPGenerator11`
- `NegPGenerator12`
- `NegPGenerator13`
- `NegPGenerator14`
- `NegPGenerator21`
- `Neuron.LTZone.DataInput0`
- `Neuron.LTZone.DataInput1`
- `Neuron.LTZone.DataInput2`
- `Neuron.LTZone.DataInput3`
- `Neuron.LTZone.DataInput4`
- ... (всего 51 входов)

**Выходы системы:**
- `NegPGenerator11.DataOutput0`
- `NegPGenerator12.DataOutput0`
- `NegPGenerator13.DataOutput0`
- `NegPGenerator14.DataOutput0`
- `NegPGenerator21.DataOutput0`
- `Neuron.LTZone.DataOutput0`
- `Neuron.LTZone.DataOutput1`
- `Neuron.LTZone.DataOutput2`
- `Neuron.PNeuronMembrane11.NegChannel.DataOutput0`
- `Neuron.PNeuronMembrane11.PosChannel.DataOutput0`
- ... (всего 29 выходов)

**Количество связей:** 47

---

### NM-PN-06-Neuron-1M4D3St3In

**Путь:** `Bin\Configs\!OldConfigs\NM-Neurons\NM-PN-06-Neuron-1M4D3St3In`

**Назначение:** Модель LIF нейрона

**Название проекта:** Minimalistic neuron

**Количество каналов:** 0

**Основные компоненты:**
- **NPGenerator**: PosPGenerator11, NegPGenerator11, PosPGenerator12, PosPGenerator13, PosPGenerator14 (и еще 5)
- **NPLTZone**: Neuron.LTZone, LTZone
- **NPNeuron1x4**: Neuron
- **NPNeuronChannel**: Neuron.PNeuronMembrane11.PosChannel, Neuron.PNeuronMembrane11.NegChannel, Neuron.PNeuronMembrane12.PosChannel, Neuron.PNeuronMembrane12.NegChannel, Neuron.PNeuronMembrane13.PosChannel (и еще 15)
- **NPNeuronMembrane**: Neuron.PNeuronMembrane11, Neuron.PNeuronMembrane12, Neuron.PNeuronMembrane13, Neuron.PNeuronMembrane14, PNeuronMembrane11 (и еще 3)
- **NPNeuronNegCGenerator**: Neuron.PNeuronNegCGenerator, PNeuronNegCGenerator
- **NPNeuronPosCGenerator**: Neuron.PNeuronPosCGenerator, PNeuronPosCGenerator
- **NPSynapse**: Neuron.PNeuronMembrane11.PosChannel.Synapse, Neuron.PNeuronMembrane11.PosChannel.Synapse2, Neuron.PNeuronMembrane11.PosChannel.Synapse3, Neuron.PNeuronMembrane11.NegChannel.Synapse, Neuron.PNeuronMembrane11.NegChannel.Synapse2 (и еще 85)
- **UStatisticDoubleMatrix**: StatisticDoubleMatrix

**Входы системы:**
- `NegPGenerator11`
- `NegPGenerator12`
- `NegPGenerator13`
- `NegPGenerator14`
- `NegPGenerator14_2`
- `Neuron.LTZone.DataInput0`
- `Neuron.LTZone.DataInput1`
- `Neuron.PNeuronMembrane11.DataInput0`
- `Neuron.PNeuronMembrane11.NegChannel.DataInput0`
- `Neuron.PNeuronMembrane11.NegChannel.Synapse.DataInput0`
- ... (всего 36 входов)

**Выходы системы:**
- `NegPGenerator11.DataOutput0`
- `NegPGenerator12.DataOutput0`
- `NegPGenerator13.DataOutput0`
- `NegPGenerator14.DataOutput0`
- `NegPGenerator14_2.DataOutput0`
- `Neuron.LTZone.DataOutput0`
- `Neuron.LTZone.DataOutput1`
- `Neuron.LTZone.DataOutput2`
- `Neuron.PNeuronMembrane11.NegChannel.DataOutput0`
- `Neuron.PNeuronMembrane11.PosChannel.DataOutput0`
- ... (всего 23 выходов)

**Количество связей:** 32

---

### NM-PN-07-LtmNeuron-1M1St3In3

**Путь:** `Bin\Configs\!OldConfigs\NM-Neurons\NM-PN-07-LtmNeuron-1M1St3In3`

**Назначение:** Модель LIF нейрона

**Название проекта:** Minimalistic neuron

**Количество каналов:** 0

**Основные компоненты:**
- **NNewSPNeuron**: SPNeuron
- **NPGenerator**: PosPGenerator, NegPGenerator
- **NPLTZone**: SPNeuron.LTZone, LTZone
- **NPLTZoneNeuronMembrane**: SPNeuron.LTMembrane, LTMembrane
- **NPNeuronChannel**: SPNeuron.LTMembrane.PosChannel, SPNeuron.LTMembrane.NegChannel, SPNeuron.PNeuronMembrane.PosChannel, SPNeuron.PNeuronMembrane.NegChannel, SPNeuron.PosChannel (и еще 7)
- **NPNeuronNegCGenerator**: SPNeuron.PNeuronNegCGenerator, PNeuronNegCGenerator
- **NPNeuronPosCGenerator**: SPNeuron.PNeuronPosCGenerator, PNeuronPosCGenerator
- **NPNewNeuronMembrane**: SPNeuron.PNeuronMembrane, PNeuronMembrane
- **NPSynapse**: SPNeuron.LTMembrane.PosChannel.Synapse, SPNeuron.LTMembrane.PosChannel.Synapse2, SPNeuron.LTMembrane.PosChannel.Synapse3, SPNeuron.LTMembrane.NegChannel.Synapse, SPNeuron.LTMembrane.NegChannel.Synapse2 (и еще 49)
- **UStatisticDoubleMatrix**: StatisticDoubleMatrix

**Входы системы:**
- `NegPGenerator`
- `PNeuronNegCGenerator`
- `PNeuronPosCGenerator`
- `PosPGenerator`
- `SPNeuron.LTMembrane.DataInput0`
- `SPNeuron.LTMembrane.NegChannel.DataInput0`
- `SPNeuron.LTMembrane.PosChannel.DataInput0`
- `SPNeuron.LTZone.DataInput0`
- `SPNeuron.LTZone.DataInput1`
- `SPNeuron.PNeuronMembrane.NegChannel.DataInput0`
- ... (всего 16 входов)

**Выходы системы:**
- `NegPGenerator.DataOutput0`
- `PosPGenerator.DataOutput0`
- `SPNeuron.LTMembrane.NegChannel.DataOutput0`
- `SPNeuron.LTMembrane.PosChannel.DataOutput0`
- `SPNeuron.LTZone.DataOutput0`
- `SPNeuron.LTZone.DataOutput1`
- `SPNeuron.LTZone.DataOutput2`
- `SPNeuron.PNeuronMembrane.NegChannel.DataOutput0`
- `SPNeuron.PNeuronMembrane.PosChannel.DataOutput0`
- `SPNeuron.PNeuronNegCGenerator.DataOutput0`
- ... (всего 11 выходов)

**Количество связей:** 14

---

### NM-PN-08-LtmNeuron-3M1St3In3

**Путь:** `Bin\Configs\!OldConfigs\NM-Neurons\NM-PN-08-LtmNeuron-3M1St3In3`

**Назначение:** Модель LIF нейрона

**Название проекта:** Minimalistic neuron

**Количество каналов:** 0

**Основные компоненты:**
- **NNewLPNeuron**: LPNeuron
- **NPGenerator**: PosPGenerator, NegPGenerator
- **NPLTZone**: LPNeuron.LTZone, LTZone
- **NPLTZoneNeuronMembrane**: LPNeuron.LTMembrane, LTMembrane
- **NPNeuronChannel**: LPNeuron.LTMembrane.PosChannel, LPNeuron.LTMembrane.NegChannel, LPNeuron.PNeuronMembrane.PosChannel, LPNeuron.PNeuronMembrane.NegChannel, LPNeuron.PNeuronMembrane2.PosChannel (и еще 15)
- **NPNeuronNegCGenerator**: LPNeuron.PNeuronNegCGenerator, PNeuronNegCGenerator
- **NPNeuronPosCGenerator**: LPNeuron.PNeuronPosCGenerator, PNeuronPosCGenerator
- **NPNewNeuronMembrane**: LPNeuron.PNeuronMembrane, LPNeuron.PNeuronMembrane2, LPNeuron.PNeuronMembrane3, PNeuronMembrane, PNeuronMembrane2 (и еще 1)
- **NPSynapse**: LPNeuron.LTMembrane.PosChannel.Synapse, LPNeuron.LTMembrane.PosChannel.Synapse2, LPNeuron.LTMembrane.PosChannel.Synapse3, LPNeuron.LTMembrane.NegChannel.Synapse, LPNeuron.LTMembrane.NegChannel.Synapse2 (и еще 85)
- **UStatisticDoubleMatrix**: StatisticDoubleMatrix

**Входы системы:**
- `LPNeuron.LTMembrane.DataInput0`
- `LPNeuron.LTMembrane.NegChannel.DataInput0`
- `LPNeuron.LTMembrane.NegChannel.DataInput1`
- `LPNeuron.LTMembrane.NegChannel.DataInput2`
- `LPNeuron.LTMembrane.PosChannel.DataInput0`
- `LPNeuron.LTMembrane.PosChannel.DataInput1`
- `LPNeuron.LTMembrane.PosChannel.DataInput2`
- `LPNeuron.LTZone.DataInput0`
- `LPNeuron.LTZone.DataInput1`
- `LPNeuron.PNeuronMembrane.NegChannel.DataInput0`
- ... (всего 24 входов)

**Выходы системы:**
- `LPNeuron.LTMembrane.NegChannel.DataOutput0`
- `LPNeuron.LTMembrane.PosChannel.DataOutput0`
- `LPNeuron.LTZone.DataOutput0`
- `LPNeuron.LTZone.DataOutput1`
- `LPNeuron.LTZone.DataOutput2`
- `LPNeuron.PNeuronMembrane.NegChannel.DataOutput0`
- `LPNeuron.PNeuronMembrane.PosChannel.DataOutput0`
- `LPNeuron.PNeuronMembrane2.NegChannel.DataOutput0`
- `LPNeuron.PNeuronMembrane2.PosChannel.DataOutput0`
- `LPNeuron.PNeuronMembrane3.NegChannel.DataOutput0`
- ... (всего 15 выходов)

**Количество связей:** 22

---

### NM-PN-NeuronSizeActivity

**Путь:** `Bin\Configs\!OldConfigs\NM-Neurons\NM-PN-NeuronSizeActivity`

**Назначение:** Модель LIF нейрона

**Название проекта:** Minimalistic neuron

**Количество каналов:** 0

**Основные компоненты:**
- **NPGenerator**: PosPGenerator11, NegPGenerator11, PosPGenerator12, PosPGenerator13, PosPGenerator14 (и еще 5)
- **NPLTZone**: Neuron.LTZone, Neuron2.LTZone, LTZone
- **NPNeuron1x4**: Neuron, Neuron2
- **NPNeuronChannel**: Neuron.PNeuronMembrane11.PosChannel, Neuron.PNeuronMembrane11.NegChannel, Neuron.PNeuronMembrane12.PosChannel, Neuron.PNeuronMembrane12.NegChannel, Neuron.PNeuronMembrane13.PosChannel (и еще 35)
- **NPNeuronMembrane**: Neuron.PNeuronMembrane11, Neuron.PNeuronMembrane12, Neuron.PNeuronMembrane13, Neuron.PNeuronMembrane14, Neuron.PNeuronMembrane23 (и еще 12)
- **NPNeuronNegCGenerator**: Neuron.PNeuronNegCGenerator, Neuron2.PNeuronNegCGenerator, PNeuronNegCGenerator
- **NPNeuronPosCGenerator**: Neuron.PNeuronPosCGenerator, Neuron2.PNeuronPosCGenerator, PNeuronPosCGenerator
- **NPSynapse**: Neuron.PNeuronMembrane11.PosChannel.Synapse, Neuron.PNeuronMembrane11.PosChannel.Synapse2, Neuron.PNeuronMembrane11.PosChannel.Synapse3, Neuron.PNeuronMembrane11.NegChannel.Synapse, Neuron.PNeuronMembrane11.NegChannel.Synapse2 (и еще 175)
- **UStatisticDoubleMatrix**: StatisticDoubleMatrix

**Входы системы:**
- `NegPGenerator11`
- `NegPGenerator12`
- `NegPGenerator13`
- `NegPGenerator14`
- `NegPGenerator23`
- `Neuron.LTZone.DataInput0`
- `Neuron.LTZone.DataInput1`
- `Neuron.PNeuronMembrane11.DataInput0`
- `Neuron.PNeuronMembrane11.NegChannel.DataInput0`
- `Neuron.PNeuronMembrane11.NegChannel.Synapse.DataInput0`
- ... (всего 69 входов)

**Выходы системы:**
- `NegPGenerator11.DataOutput0`
- `NegPGenerator12.DataOutput0`
- `NegPGenerator13.DataOutput0`
- `NegPGenerator14.DataOutput0`
- `NegPGenerator23.DataOutput0`
- `Neuron.LTZone.DataOutput0`
- `Neuron.LTZone.DataOutput1`
- `Neuron.LTZone.DataOutput2`
- `Neuron.PNeuronMembrane11.NegChannel.DataOutput0`
- `Neuron.PNeuronMembrane11.PosChannel.DataOutput0`
- ... (всего 42 выходов)

**Количество связей:** 68

---

## NavSchemes

### 32_pic1

**Путь:** `Bin\Configs\ivan\NavSchemes\32_pic1`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NPExcChannelBio**: ORNeuron.Soma1.ExcChannel, ORNeuron.ExcChannel, DecidingNeuron.Soma1.ExcChannel, DecidingNeuron.ExcChannel, ANDNeuron.Soma1.ExcChannel (и еще 5)
- **NPInhChannelBio**: ORNeuron.Soma1.InhChannel, ORNeuron.InhChannel, DecidingNeuron.Soma1.InhChannel, DecidingNeuron.InhChannel, ANDNeuron.Soma1.InhChannel (и еще 5)
- **NPMembraneBio**: ORNeuron.Soma1, DecidingNeuron.Soma1, ANDNeuron.Soma1, ANDNeuron.Soma2, Soma1 (и еще 1)
- **NPNeuronNegCGenerator**: ORNeuron.NegGenerator, DecidingNeuron.NegGenerator, ANDNeuron.NegGenerator, NegGenerator
- **NPNeuronPosCGenerator**: ORNeuron.PosGenerator, DecidingNeuron.PosGenerator, ANDNeuron.PosGenerator, PosGenerator
- **NPSynapseBio**: ORNeuron.Soma1.ExcSynapse1, ORNeuron.Soma1.ExcSynapse2, ORNeuron.ExcSynapse1, ORNeuron.ExcSynapse2, DecidingNeuron.Soma1.ExcSynapse1 (и еще 23)
- **NPulseGeneratorMulti**: Cls1SpikeFr, ClsNSpikeFr
- **NPulseGeneratorTransit**: t0, t1, t2, InhibitoryGen1, InhibitoryGen2 (и еще 2)
- **NPulseLTZoneThreshold**: ORNeuron.LTZone, DecidingNeuron.LTZone, ANDNeuron.LTZone, LTZone
- **NSPNeuronGen**: ORNeuron, DecidingNeuron, ANDNeuron

**Входы системы:**
- `ANDNeuron.LTZone.Inputs`
- `ANDNeuron.NegGenerator`
- `ANDNeuron.PosGenerator`
- `ANDNeuron.Soma1.ExcChannel.ChannelInputs`
- `ANDNeuron.Soma1.ExcChannel.SynapticInputs`
- `ANDNeuron.Soma1.ExcSynapse1.Input`
- `ANDNeuron.Soma1.InhChannel.ChannelInputs`
- `ANDNeuron.Soma1.InhChannel.SynapticInputs`
- `ANDNeuron.Soma1.InputFeedbackSignal`
- `ANDNeuron.Soma2.ExcChannel.ChannelInputs`
- ... (всего 49 входов)

**Выходы системы:**
- `ANDNeuron.LTZone.Output`
- `ANDNeuron.NegGenerator.Output`
- `ANDNeuron.PosGenerator.Output`
- `ANDNeuron.Soma1.ExcChannel.Output`
- `ANDNeuron.Soma1.ExcSynapse1.Output`
- `ANDNeuron.Soma1.ExcSynapse2.Output`
- `ANDNeuron.Soma1.InhChannel.Output`
- `ANDNeuron.Soma1.InhSynapse1.Output`
- `ANDNeuron.Soma2.ExcChannel.Output`
- `ANDNeuron.Soma2.ExcSynapse1.Output`
- ... (всего 35 выходов)

**Количество связей:** 40

---

### 33_pic1314_scheme

**Путь:** `Bin\Configs\ivan\NavSchemes\33_pic1314_scheme`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NPDelay**: DelayBlock
- **NPExcChannelBio**: SupprBlock.Soma1.ExcChannel, SupprBlock.ExcChannel, CompNeuron.Dendrite1_1.ExcChannel, CompNeuron.Soma1.ExcChannel, CompNeuron.ExcChannel (и еще 3)
- **NPInhChannelBio**: SupprBlock.Soma1.InhChannel, SupprBlock.InhChannel, CompNeuron.Dendrite1_1.InhChannel, CompNeuron.Soma1.InhChannel, CompNeuron.InhChannel (и еще 3)
- **NPMembraneBio**: SupprBlock.Soma1, CompNeuron.Dendrite1_1, CompNeuron.Soma1, Soma1, Dendrite1_1
- **NPNeuronNegCGenerator**: SupprBlock.NegGenerator, CompNeuron.NegGenerator, NegGenerator
- **NPNeuronPosCGenerator**: SupprBlock.PosGenerator, CompNeuron.PosGenerator, PosGenerator
- **NPSynapseBio**: SupprBlock.Soma1.ExcSynapse1, SupprBlock.Soma1.InhSynapse1, SupprBlock.ExcSynapse1, SupprBlock.InhSynapse1, CompNeuron.Dendrite1_1.ExcSynapse1 (и еще 11)
- **NPulseGeneratorMulti**: CurKFClsSeq, NextKFClsSeq
- **NPulseGeneratorTransit**: SupprGen, t0
- **NPulseLTZoneThreshold**: SupprBlock.LTZone, CompNeuron.LTZone, LTZone
- **NSPNeuronGen**: SupprBlock, CompNeuron

**Входы системы:**
- `CompNeuron.Dendrite1_1.ExcChannel.ChannelInputs`
- `CompNeuron.Dendrite1_1.ExcChannel.SynapticInputs`
- `CompNeuron.Dendrite1_1.ExcSynapse1.Input`
- `CompNeuron.Dendrite1_1.InhChannel.ChannelInputs`
- `CompNeuron.Dendrite1_1.InhChannel.SynapticInputs`
- `CompNeuron.LTZone.Inputs`
- `CompNeuron.NegGenerator`
- `CompNeuron.PosGenerator`
- `CompNeuron.Soma1.ExcChannel.ChannelInputs`
- `CompNeuron.Soma1.ExcChannel.SynapticInputs`
- ... (всего 32 входов)

**Выходы системы:**
- `CompNeuron.Dendrite1_1.ExcChannel.Output`
- `CompNeuron.Dendrite1_1.ExcSynapse1.Output`
- `CompNeuron.Dendrite1_1.InhChannel.Output`
- `CompNeuron.Dendrite1_1.InhSynapse1.Output`
- `CompNeuron.LTZone.Output`
- `CompNeuron.NegGenerator.Output`
- `CompNeuron.PosGenerator.Output`
- `CompNeuron.Soma1.ExcChannel.Output`
- `CompNeuron.Soma1.ExcSynapse1.Output`
- `CompNeuron.Soma1.InhChannel.Output`
- ... (всего 23 выходов)

**Количество связей:** 24

---

### AndSample

**Путь:** `Bin\Configs\ivan\NavSchemes\AndSample`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NPExcChannelBio**: AndNeuron.Soma1.ExcChannel, AndNeuron.Soma2.ExcChannel, AndNeuron.ExcChannel, Soma1.ExcChannel, Soma2.ExcChannel (и еще 1)
- **NPInhChannelBio**: AndNeuron.Soma1.InhChannel, AndNeuron.Soma2.InhChannel, AndNeuron.InhChannel, Soma1.InhChannel, Soma2.InhChannel (и еще 1)
- **NPMembraneBio**: AndNeuron.Soma1, AndNeuron.Soma2, Soma1, Soma2
- **NPNeuronNegCGenerator**: AndNeuron.NegGenerator, NegGenerator
- **NPNeuronPosCGenerator**: AndNeuron.PosGenerator, PosGenerator
- **NPSynapseBio**: AndNeuron.Soma1.ExcSynapse1, AndNeuron.Soma1.InhSynapse1, AndNeuron.Soma2.ExcSynapse1, AndNeuron.Soma2.InhSynapse1, AndNeuron.ExcSynapse1 (и еще 7)
- **NPulseGeneratorTransit**: Input_1, Input_2
- **NPulseLTZoneThreshold**: AndNeuron.LTZone, LTZone
- **NSPNeuronGen**: AndNeuron

**Входы системы:**
- `AndNeuron.LTZone.Inputs`
- `AndNeuron.NegGenerator`
- `AndNeuron.PosGenerator`
- `AndNeuron.Soma1.ExcChannel.ChannelInputs`
- `AndNeuron.Soma1.ExcChannel.SynapticInputs`
- `AndNeuron.Soma1.ExcSynapse1.Input`
- `AndNeuron.Soma1.InhChannel.ChannelInputs`
- `AndNeuron.Soma1.InhChannel.SynapticInputs`
- `AndNeuron.Soma1.InputFeedbackSignal`
- `AndNeuron.Soma2.ExcChannel.ChannelInputs`
- ... (всего 19 входов)

**Выходы системы:**
- `AndNeuron.LTZone.Output`
- `AndNeuron.NegGenerator.Output`
- `AndNeuron.PosGenerator.Output`
- `AndNeuron.Soma1.ExcChannel.Output`
- `AndNeuron.Soma1.ExcSynapse1.Output`
- `AndNeuron.Soma1.InhChannel.Output`
- `AndNeuron.Soma1.InhSynapse1.Output`
- `AndNeuron.Soma2.ExcChannel.Output`
- `AndNeuron.Soma2.ExcSynapse1.Output`
- `AndNeuron.Soma2.InhChannel.Output`
- ... (всего 13 выходов)

**Количество связей:** 16

---

### Ivan_VKR_3-2_8

**Путь:** `Bin\Configs\ivan\NavSchemes\Ivan_VKR_3-2_8`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NPExcChannelBio**: ORNeuron1.Soma1.ExcChannel, ORNeuron1.ExcChannel, ORNeuron2.Soma1.ExcChannel, ORNeuron2.ExcChannel, ORNeuron3.Soma1.ExcChannel (и еще 12)
- **NPInhChannelBio**: ORNeuron1.Soma1.InhChannel, ORNeuron1.InhChannel, ORNeuron2.Soma1.InhChannel, ORNeuron2.InhChannel, ORNeuron3.Soma1.InhChannel (и еще 12)
- **NPMembraneBio**: ORNeuron1.Soma1, ORNeuron2.Soma1, ORNeuron3.Soma1, ANDNeuron1.Soma1, ANDNeuron1.Soma2 (и еще 5)
- **NPNeuronNegCGenerator**: ORNeuron1.NegGenerator, ORNeuron2.NegGenerator, ORNeuron3.NegGenerator, ANDNeuron1.NegGenerator, ANDNeuron2.NegGenerator (и еще 2)
- **NPNeuronPosCGenerator**: ORNeuron1.PosGenerator, ORNeuron2.PosGenerator, ORNeuron3.PosGenerator, ANDNeuron1.PosGenerator, ANDNeuron2.PosGenerator (и еще 2)
- **NPSynapseBio**: ORNeuron1.Soma1.ExcSynapse1, ORNeuron1.Soma1.ExcSynapse2, ORNeuron1.Soma1.InhSynapse1, ORNeuron1.ExcSynapse1, ORNeuron1.ExcSynapse2 (и еще 39)
- **NPulseGeneratorTransit**: Class1Object, Class2Object, KF1InZone, KF2InZone, PartOfKF3InZone (и еще 2)
- **NPulseLTZoneThreshold**: ORNeuron1.LTZone, ORNeuron2.LTZone, ORNeuron3.LTZone, ANDNeuron1.LTZone, ANDNeuron2.LTZone (и еще 2)
- **NSPNeuronGen**: ORNeuron1, ORNeuron2, ORNeuron3, ANDNeuron1, ANDNeuron2 (и еще 1)

**Входы системы:**
- `ANDNeuron1.LTZone.Inputs`
- `ANDNeuron1.NegGenerator`
- `ANDNeuron1.PosGenerator`
- `ANDNeuron1.Soma1.ExcChannel.ChannelInputs`
- `ANDNeuron1.Soma1.ExcChannel.SynapticInputs`
- `ANDNeuron1.Soma1.ExcSynapse1.Input`
- `ANDNeuron1.Soma1.InhChannel.ChannelInputs`
- `ANDNeuron1.Soma1.InhChannel.SynapticInputs`
- `ANDNeuron1.Soma1.InputFeedbackSignal`
- `ANDNeuron1.Soma2.ExcChannel.ChannelInputs`
- ... (всего 79 входов)

**Выходы системы:**
- `ANDNeuron1.LTZone.Output`
- `ANDNeuron1.NegGenerator.Output`
- `ANDNeuron1.PosGenerator.Output`
- `ANDNeuron1.Soma1.ExcChannel.Output`
- `ANDNeuron1.Soma1.ExcSynapse1.Output`
- `ANDNeuron1.Soma1.InhChannel.Output`
- `ANDNeuron1.Soma1.InhSynapse1.Output`
- `ANDNeuron1.Soma2.ExcChannel.Output`
- `ANDNeuron1.Soma2.ExcSynapse1.Output`
- `ANDNeuron1.Soma2.InhChannel.Output`
- ... (всего 61 выходов)

**Количество связей:** 72

---

### Ivan_VKR_3-2_9

**Путь:** `Bin\Configs\ivan\NavSchemes\Ivan_VKR_3-2_9`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NPExcChannelBio**: NOTNeuron1.Soma1.ExcChannel, NOTNeuron1.ExcChannel, ORNeuron1.Soma1.ExcChannel, ORNeuron1.ExcChannel, NOTNeuron2.Soma1.ExcChannel (и еще 18)
- **NPInhChannelBio**: NOTNeuron1.Soma1.InhChannel, NOTNeuron1.InhChannel, ORNeuron1.Soma1.InhChannel, ORNeuron1.InhChannel, NOTNeuron2.Soma1.InhChannel (и еще 18)
- **NPMembraneBio**: NOTNeuron1.Soma1, ORNeuron1.Soma1, NOTNeuron2.Soma1, ANDNeuron1.Soma1, ANDNeuron1.Soma2 (и еще 9)
- **NPNeuronNegCGenerator**: NOTNeuron1.NegGenerator, ORNeuron1.NegGenerator, NOTNeuron2.NegGenerator, ANDNeuron1.NegGenerator, ANDNeuron2.NegGenerator (и еще 4)
- **NPNeuronPosCGenerator**: NOTNeuron1.PosGenerator, ORNeuron1.PosGenerator, NOTNeuron2.PosGenerator, ANDNeuron1.PosGenerator, ANDNeuron2.PosGenerator (и еще 4)
- **NPSynapseBio**: NOTNeuron1.Soma1.ExcSynapse1, NOTNeuron1.Soma1.InhSynapse1, NOTNeuron1.ExcSynapse1, NOTNeuron1.InhSynapse1, ORNeuron1.Soma1.ExcSynapse1 (и еще 47)
- **NPulseGeneratorTransit**: Person, Backpack, KF1InZone, KF2InZone, PartOfKF3InZone (и еще 4)
- **NPulseLTZoneThreshold**: NOTNeuron1.LTZone, ORNeuron1.LTZone, NOTNeuron2.LTZone, ANDNeuron1.LTZone, ANDNeuron2.LTZone (и еще 4)
- **NSPNeuronGen**: NOTNeuron1, ORNeuron1, NOTNeuron2, ANDNeuron1, ANDNeuron2 (и еще 3)

**Входы системы:**
- `ANDNeuron1.LTZone.Inputs`
- `ANDNeuron1.NegGenerator`
- `ANDNeuron1.PosGenerator`
- `ANDNeuron1.Soma1.ExcChannel.ChannelInputs`
- `ANDNeuron1.Soma1.ExcChannel.SynapticInputs`
- `ANDNeuron1.Soma1.ExcSynapse1.Input`
- `ANDNeuron1.Soma1.InhChannel.ChannelInputs`
- `ANDNeuron1.Soma1.InhChannel.SynapticInputs`
- `ANDNeuron1.Soma1.InputFeedbackSignal`
- `ANDNeuron1.Soma2.ExcChannel.ChannelInputs`
- ... (всего 111 входов)

**Выходы системы:**
- `ANDNeuron1.LTZone.Output`
- `ANDNeuron1.NegGenerator.Output`
- `ANDNeuron1.PosGenerator.Output`
- `ANDNeuron1.Soma1.ExcChannel.Output`
- `ANDNeuron1.Soma1.ExcSynapse1.Output`
- `ANDNeuron1.Soma1.InhChannel.Output`
- `ANDNeuron1.Soma1.InhSynapse1.Output`
- `ANDNeuron1.Soma2.ExcChannel.Output`
- `ANDNeuron1.Soma2.ExcSynapse1.Output`
- `ANDNeuron1.Soma2.InhChannel.Output`
- ... (всего 83 выходов)

**Количество связей:** 102

---

### NotSample

**Путь:** `Bin\Configs\ivan\NavSchemes\NotSample`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NPExcChannelBio**: NotNeuron.Soma1.ExcChannel, NotNeuron.ExcChannel, Soma1.ExcChannel, ExcChannel
- **NPInhChannelBio**: NotNeuron.Soma1.InhChannel, NotNeuron.InhChannel, Soma1.InhChannel, InhChannel
- **NPMembraneBio**: NotNeuron.Soma1, Soma1
- **NPNeuronNegCGenerator**: NotNeuron.NegGenerator, NegGenerator
- **NPNeuronPosCGenerator**: NotNeuron.PosGenerator, PosGenerator
- **NPSynapseBio**: NotNeuron.Soma1.ExcSynapse1, NotNeuron.Soma1.InhSynapse1, NotNeuron.ExcSynapse1, NotNeuron.InhSynapse1, Soma1.ExcSynapse1 (и еще 3)
- **NPulseGeneratorTransit**: Input, NotGenerator
- **NPulseLTZoneThreshold**: NotNeuron.LTZone, LTZone
- **NSPNeuronGen**: NotNeuron

**Входы системы:**
- `Input`
- `NegGenerator`
- `NotGenerator`
- `NotNeuron.LTZone.Inputs`
- `NotNeuron.NegGenerator`
- `NotNeuron.PosGenerator`
- `NotNeuron.Soma1.ExcChannel.ChannelInputs`
- `NotNeuron.Soma1.ExcChannel.SynapticInputs`
- `NotNeuron.Soma1.ExcSynapse1.Input`
- `NotNeuron.Soma1.InhChannel.ChannelInputs`
- ... (всего 14 входов)

**Выходы системы:**
- `Input.Output`
- `NotGenerator.Output`
- `NotNeuron.LTZone.Output`
- `NotNeuron.NegGenerator.Output`
- `NotNeuron.PosGenerator.Output`
- `NotNeuron.Soma1.ExcChannel.Output`
- `NotNeuron.Soma1.ExcSynapse1.Output`
- `NotNeuron.Soma1.InhChannel.Output`
- `NotNeuron.Soma1.InhSynapse1.Output`

**Количество связей:** 9

---

### OrSample

**Путь:** `Bin\Configs\ivan\NavSchemes\OrSample`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NPExcChannelBio**: OrNeuron.Soma1.ExcChannel, OrNeuron.ExcChannel, Soma1.ExcChannel, ExcChannel
- **NPInhChannelBio**: OrNeuron.Soma1.InhChannel, OrNeuron.InhChannel, Soma1.InhChannel, InhChannel
- **NPMembraneBio**: OrNeuron.Soma1, Soma1
- **NPNeuronNegCGenerator**: OrNeuron.NegGenerator, NegGenerator
- **NPNeuronPosCGenerator**: OrNeuron.PosGenerator, PosGenerator
- **NPSynapseBio**: OrNeuron.Soma1.ExcSynapse1, OrNeuron.Soma1.InhSynapse1, OrNeuron.Soma1.ExcSynapse12, OrNeuron.ExcSynapse1, OrNeuron.InhSynapse1 (и еще 7)
- **NPulseGeneratorTransit**: Input_1, Input_2
- **NPulseLTZoneThreshold**: OrNeuron.LTZone, LTZone
- **NSPNeuronGen**: OrNeuron

**Входы системы:**
- `Input_1`
- `Input_2`
- `NegGenerator`
- `OrNeuron.LTZone.Inputs`
- `OrNeuron.NegGenerator`
- `OrNeuron.PosGenerator`
- `OrNeuron.Soma1.ExcChannel.ChannelInputs`
- `OrNeuron.Soma1.ExcChannel.SynapticInputs`
- `OrNeuron.Soma1.ExcSynapse1.Input`
- `OrNeuron.Soma1.ExcSynapse12.Input`
- ... (всего 14 входов)

**Выходы системы:**
- `Input_1.Output`
- `Input_2.Output`
- `OrNeuron.LTZone.Output`
- `OrNeuron.NegGenerator.Output`
- `OrNeuron.PosGenerator.Output`
- `OrNeuron.Soma1.ExcChannel.Output`
- `OrNeuron.Soma1.ExcSynapse1.Output`
- `OrNeuron.Soma1.ExcSynapse12.Output`
- `OrNeuron.Soma1.InhChannel.Output`
- `OrNeuron.Soma1.InhSynapse1.Output`

**Количество связей:** 10

---

## NeuroMouse

### 23ab2

**Путь:** `Bin\Configs\ivan\NeuroMouse\23ab2`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NPExcChannelBio**: NOTNeuron.Dendrite1_2.ExcChannel, NOTNeuron.Dendrite1_1.ExcChannel, NOTNeuron.Soma1.ExcChannel, NOTNeuron.ExcChannel, NOTNeuron2.Dendrite1_2.ExcChannel (и еще 33)
- **NPInhChannelBio**: NOTNeuron.Dendrite1_2.InhChannel, NOTNeuron.Dendrite1_1.InhChannel, NOTNeuron.Soma1.InhChannel, NOTNeuron.InhChannel, NOTNeuron2.Dendrite1_2.InhChannel (и еще 33)
- **NPMembraneBio**: NOTNeuron.Dendrite1_2, NOTNeuron.Dendrite1_1, NOTNeuron.Soma1, NOTNeuron2.Dendrite1_2, NOTNeuron2.Dendrite1_1 (и еще 24)
- **NPNeuronNegCGenerator**: NOTNeuron.NegGenerator, NOTNeuron2.NegGenerator, NOTNeuron3.NegGenerator, NOTNeuron4.NegGenerator, ANDNeuron.NegGenerator (и еще 4)
- **NPNeuronPosCGenerator**: NOTNeuron.PosGenerator, NOTNeuron2.PosGenerator, NOTNeuron3.PosGenerator, NOTNeuron4.PosGenerator, ANDNeuron.PosGenerator (и еще 4)
- **NPSynapseBio**: NOTNeuron.Dendrite1_2.ExcSynapse1, NOTNeuron.Dendrite1_2.InhSynapse1, NOTNeuron.Dendrite1_1.ExcSynapse1, NOTNeuron.Dendrite1_1.InhSynapse1, NOTNeuron.Soma1.ExcSynapse1 (и еще 71)
- **NPulseGeneratorTransit**: AheadObstacle, LeftObstacle, RightObstacle, AheadObstacle2, LeftObstacle2 (и еще 5)
- **NPulseLTZoneThreshold**: NOTNeuron.LTZone, NOTNeuron2.LTZone, NOTNeuron3.LTZone, NOTNeuron4.LTZone, ANDNeuron.LTZone (и еще 4)
- **NSPNeuronGen**: NOTNeuron, NOTNeuron2, NOTNeuron3, NOTNeuron4, ANDNeuron (и еще 3)

**Входы системы:**
- `ANDNeuron.LTZone.Inputs`
- `ANDNeuron.NegGenerator`
- `ANDNeuron.PosGenerator`
- `ANDNeuron.Soma1.ExcChannel.ChannelInputs`
- `ANDNeuron.Soma1.ExcChannel.SynapticInputs`
- `ANDNeuron.Soma1.ExcSynapse1.Input`
- `ANDNeuron.Soma1.InhChannel.ChannelInputs`
- `ANDNeuron.Soma1.InhChannel.SynapticInputs`
- `ANDNeuron.Soma1.InputFeedbackSignal`
- `ANDNeuron.Soma2.ExcChannel.ChannelInputs`
- ... (всего 160 входов)

**Выходы системы:**
- `ANDNeuron.LTZone.Output`
- `ANDNeuron.NegGenerator.Output`
- `ANDNeuron.PosGenerator.Output`
- `ANDNeuron.Soma1.ExcChannel.Output`
- `ANDNeuron.Soma1.ExcSynapse1.Output`
- `ANDNeuron.Soma1.InhChannel.Output`
- `ANDNeuron.Soma1.InhSynapse1.Output`
- `ANDNeuron.Soma2.ExcChannel.Output`
- `ANDNeuron.Soma2.ExcSynapse1.Output`
- `ANDNeuron.Soma2.InhChannel.Output`
- ... (всего 130 выходов)

**Количество связей:** 148

---

### Ivan_VKR_3-4_12

**Путь:** `Bin\Configs\ivan\NeuroMouse\Ivan_VKR_3-4_12`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NPExcChannelBio**: ANDNeuron.Soma1.ExcChannel, ANDNeuron.Soma2.ExcChannel, ANDNeuron.ExcChannel, ANDNeuron2.Soma1.ExcChannel, ANDNeuron2.Soma2.ExcChannel (и еще 6)
- **NPInhChannelBio**: ANDNeuron.Soma1.InhChannel, ANDNeuron.Soma2.InhChannel, ANDNeuron.InhChannel, ANDNeuron2.Soma1.InhChannel, ANDNeuron2.Soma2.InhChannel (и еще 6)
- **NPMembraneBio**: ANDNeuron.Soma1, ANDNeuron.Soma2, ANDNeuron2.Soma1, ANDNeuron2.Soma2, ORNeuron.Soma1 (и еще 2)
- **NPNeuronNegCGenerator**: ANDNeuron.NegGenerator, ANDNeuron2.NegGenerator, ORNeuron.NegGenerator, NegGenerator
- **NPNeuronPosCGenerator**: ANDNeuron.PosGenerator, ANDNeuron2.PosGenerator, ORNeuron.PosGenerator, PosGenerator
- **NPSynapseBio**: ANDNeuron.Soma1.ExcSynapse1, ANDNeuron.Soma1.ExcSynapse2, ANDNeuron.Soma1.InhSynapse1, ANDNeuron.Soma2.ExcSynapse1, ANDNeuron.Soma2.InhSynapse1 (и еще 25)
- **NPulseGeneratorTransit**: DangerR, ForwardMotion, DangerB, BackwardsMotion
- **NPulseLTZoneThreshold**: ANDNeuron.LTZone, ANDNeuron2.LTZone, ORNeuron.LTZone, LTZone
- **NSPNeuronGen**: ANDNeuron, ANDNeuron2, ORNeuron

**Входы системы:**
- `ANDNeuron.LTZone.Inputs`
- `ANDNeuron.NegGenerator`
- `ANDNeuron.PosGenerator`
- `ANDNeuron.Soma1.ExcChannel.ChannelInputs`
- `ANDNeuron.Soma1.ExcChannel.SynapticInputs`
- `ANDNeuron.Soma1.ExcSynapse1.Input`
- `ANDNeuron.Soma1.ExcSynapse2.Input`
- `ANDNeuron.Soma1.InhChannel.ChannelInputs`
- `ANDNeuron.Soma1.InhChannel.SynapticInputs`
- `ANDNeuron.Soma1.InputFeedbackSignal`
- ... (всего 46 входов)

**Выходы системы:**
- `ANDNeuron.LTZone.Output`
- `ANDNeuron.NegGenerator.Output`
- `ANDNeuron.PosGenerator.Output`
- `ANDNeuron.Soma1.ExcChannel.Output`
- `ANDNeuron.Soma1.ExcSynapse1.Output`
- `ANDNeuron.Soma1.ExcSynapse2.Output`
- `ANDNeuron.Soma1.InhChannel.Output`
- `ANDNeuron.Soma1.InhSynapse1.Output`
- `ANDNeuron.Soma2.ExcChannel.Output`
- `ANDNeuron.Soma2.ExcSynapse1.Output`
- ... (всего 36 выходов)

**Количество связей:** 44

---

### Ivan_VKR_3-4_13

**Путь:** `Bin\Configs\ivan\NeuroMouse\Ivan_VKR_3-4_13`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NPExcChannelBio**: NOTNeuron1.Dendrite1_1.ExcChannel, NOTNeuron1.Soma1.ExcChannel, NOTNeuron1.ExcChannel, NOTNeuron2.Dendrite1_1.ExcChannel, NOTNeuron2.Soma1.ExcChannel (и еще 22)
- **NPInhChannelBio**: NOTNeuron1.Dendrite1_1.InhChannel, NOTNeuron1.Soma1.InhChannel, NOTNeuron1.InhChannel, NOTNeuron2.Dendrite1_1.InhChannel, NOTNeuron2.Soma1.InhChannel (и еще 22)
- **NPMembraneBio**: NOTNeuron1.Dendrite1_1, NOTNeuron1.Soma1, NOTNeuron2.Dendrite1_1, NOTNeuron2.Soma1, NOTNeuron3.Dendrite1_1 (и еще 15)
- **NPNeuronNegCGenerator**: NOTNeuron1.NegGenerator, NOTNeuron2.NegGenerator, NOTNeuron3.NegGenerator, NOTNeuron4.NegGenerator, ORNeuron.NegGenerator (и еще 2)
- **NPNeuronPosCGenerator**: NOTNeuron1.PosGenerator, NOTNeuron2.PosGenerator, NOTNeuron3.PosGenerator, NOTNeuron4.PosGenerator, ORNeuron.PosGenerator (и еще 2)
- **NPSynapseBio**: NOTNeuron1.Dendrite1_1.ExcSynapse1, NOTNeuron1.Dendrite1_1.InhSynapse1, NOTNeuron1.Soma1.ExcSynapse1, NOTNeuron1.Soma1.InhSynapse1, NOTNeuron1.ExcSynapse1 (и еще 53)
- **NPulseGeneratorTransit**: NOTGenerator1, NOTGenerator2, NOTGenerator3, NOTGenerator4, Forward (и еще 5)
- **NPulseLTZoneThreshold**: NOTNeuron1.LTZone, NOTNeuron2.LTZone, NOTNeuron3.LTZone, NOTNeuron4.LTZone, ORNeuron.LTZone (и еще 2)
- **NSPNeuronGen**: NOTNeuron1, NOTNeuron2, NOTNeuron3, NOTNeuron4, ORNeuron (и еще 1)

**Входы системы:**
- `ANDNeuron.LTZone.Inputs`
- `ANDNeuron.NegGenerator`
- `ANDNeuron.PosGenerator`
- `ANDNeuron.Soma1.ExcChannel.ChannelInputs`
- `ANDNeuron.Soma1.ExcChannel.SynapticInputs`
- `ANDNeuron.Soma1.ExcSynapse1.Input`
- `ANDNeuron.Soma1.InhChannel.ChannelInputs`
- `ANDNeuron.Soma1.InhChannel.SynapticInputs`
- `ANDNeuron.Soma1.InputFeedbackSignal`
- `ANDNeuron.Soma2.ExcChannel.ChannelInputs`
- ... (всего 111 входов)

**Выходы системы:**
- `ANDNeuron.LTZone.Output`
- `ANDNeuron.NegGenerator.Output`
- `ANDNeuron.PosGenerator.Output`
- `ANDNeuron.Soma1.ExcChannel.Output`
- `ANDNeuron.Soma1.ExcSynapse1.Output`
- `ANDNeuron.Soma1.InhChannel.Output`
- `ANDNeuron.Soma1.InhSynapse1.Output`
- `ANDNeuron.Soma2.ExcChannel.Output`
- `ANDNeuron.Soma2.ExcSynapse1.Output`
- `ANDNeuron.Soma2.InhChannel.Output`
- ... (всего 85 выходов)

**Количество связей:** 102

---

### Ivan_VKR_3-4_21

**Путь:** `Bin\Configs\ivan\NeuroMouse\Ivan_VKR_3-4_21`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NPExcChannelBio**: NOTNeuron1.Dendrite1_1.ExcChannel, NOTNeuron1.Soma1.ExcChannel, NOTNeuron1.ExcChannel, NOTNeuron2.Dendrite1_1.ExcChannel, NOTNeuron2.Soma1.ExcChannel (и еще 19)
- **NPInhChannelBio**: NOTNeuron1.Dendrite1_1.InhChannel, NOTNeuron1.Soma1.InhChannel, NOTNeuron1.InhChannel, NOTNeuron2.Dendrite1_1.InhChannel, NOTNeuron2.Soma1.InhChannel (и еще 19)
- **NPMembraneBio**: NOTNeuron1.Dendrite1_1, NOTNeuron1.Soma1, NOTNeuron2.Dendrite1_1, NOTNeuron2.Soma1, NOTNeuron3.Dendrite1_1 (и еще 11)
- **NPNeuronNegCGenerator**: NOTNeuron1.NegGenerator, NOTNeuron2.NegGenerator, NOTNeuron3.NegGenerator, ANDNeuron1.NegGenerator, ANDNeuron2.NegGenerator (и еще 3)
- **NPNeuronPosCGenerator**: NOTNeuron1.PosGenerator, NOTNeuron2.PosGenerator, NOTNeuron3.PosGenerator, ANDNeuron1.PosGenerator, ANDNeuron2.PosGenerator (и еще 3)
- **NPSynapseBio**: NOTNeuron1.Dendrite1_1.ExcSynapse1, NOTNeuron1.Dendrite1_1.InhSynapse1, NOTNeuron1.Soma1.ExcSynapse1, NOTNeuron1.Soma1.InhSynapse1, NOTNeuron1.ExcSynapse1 (и еще 47)
- **NPulseGeneratorTransit**: ObstacleAhead, ObstacleLeft, ObstacleRight, NOTGenerator1, NOTGenerator2 (и еще 1)
- **NPulseLTZoneThreshold**: NOTNeuron1.LTZone, NOTNeuron2.LTZone, NOTNeuron3.LTZone, ANDNeuron1.LTZone, ANDNeuron2.LTZone (и еще 3)
- **NSPNeuronGen**: NOTNeuron1, NOTNeuron2, NOTNeuron3, ANDNeuron1, ANDNeuron2 (и еще 2)

**Входы системы:**
- `ANDNeuron.LTZone.Inputs`
- `ANDNeuron.NegGenerator`
- `ANDNeuron.PosGenerator`
- `ANDNeuron.Soma1.ExcChannel.ChannelInputs`
- `ANDNeuron.Soma1.ExcChannel.SynapticInputs`
- `ANDNeuron.Soma1.ExcSynapse1.Input`
- `ANDNeuron.Soma1.InhChannel.ChannelInputs`
- `ANDNeuron.Soma1.InhChannel.SynapticInputs`
- `ANDNeuron.Soma1.InputFeedbackSignal`
- `ANDNeuron.Soma2.ExcChannel.ChannelInputs`
- ... (всего 105 входов)

**Выходы системы:**
- `ANDNeuron.LTZone.Output`
- `ANDNeuron.NegGenerator.Output`
- `ANDNeuron.PosGenerator.Output`
- `ANDNeuron.Soma1.ExcChannel.Output`
- `ANDNeuron.Soma1.ExcSynapse1.Output`
- `ANDNeuron.Soma1.InhChannel.Output`
- `ANDNeuron.Soma1.InhSynapse1.Output`
- `ANDNeuron.Soma2.ExcChannel.Output`
- `ANDNeuron.Soma2.ExcSynapse1.Output`
- `ANDNeuron.Soma2.InhChannel.Output`
- ... (всего 80 выходов)

**Количество связей:** 97

---

### Ivan_VKR_3-4_22

**Путь:** `Bin\Configs\ivan\NeuroMouse\Ivan_VKR_3-4_22`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NPExcChannelBio**: ANDNeuron.Soma1.ExcChannel, ANDNeuron.Soma2.ExcChannel, ANDNeuron.ExcChannel, ANDNeuron2.Soma1.ExcChannel, ANDNeuron2.Soma2.ExcChannel (и еще 4)
- **NPInhChannelBio**: ANDNeuron.Soma1.InhChannel, ANDNeuron.Soma2.InhChannel, ANDNeuron.InhChannel, ANDNeuron2.Soma1.InhChannel, ANDNeuron2.Soma2.InhChannel (и еще 4)
- **NPMembraneBio**: ANDNeuron.Soma1, ANDNeuron.Soma2, ANDNeuron2.Soma1, ANDNeuron2.Soma2, Soma1 (и еще 1)
- **NPNeuronNegCGenerator**: ANDNeuron.NegGenerator, ANDNeuron2.NegGenerator, NegGenerator
- **NPNeuronPosCGenerator**: ANDNeuron.PosGenerator, ANDNeuron2.PosGenerator, PosGenerator
- **NPSynapseBio**: ANDNeuron.Soma1.ExcSynapse1, ANDNeuron.Soma1.ExcSynapse2, ANDNeuron.Soma1.InhSynapse1, ANDNeuron.Soma2.ExcSynapse1, ANDNeuron.Soma2.InhSynapse1 (и еще 19)
- **NPulseGeneratorTransit**: AheadObstacle, LeftObstacle, RightObstacle
- **NPulseLTZoneThreshold**: ANDNeuron.LTZone, ANDNeuron2.LTZone, LTZone
- **NSPNeuronGen**: ANDNeuron, ANDNeuron2

**Входы системы:**
- `ANDNeuron.LTZone.Inputs`
- `ANDNeuron.NegGenerator`
- `ANDNeuron.PosGenerator`
- `ANDNeuron.Soma1.ExcChannel.ChannelInputs`
- `ANDNeuron.Soma1.ExcChannel.SynapticInputs`
- `ANDNeuron.Soma1.ExcSynapse1.Input`
- `ANDNeuron.Soma1.ExcSynapse2.Input`
- `ANDNeuron.Soma1.InhChannel.ChannelInputs`
- `ANDNeuron.Soma1.InhChannel.SynapticInputs`
- `ANDNeuron.Soma1.InputFeedbackSignal`
- ... (всего 35 входов)

**Выходы системы:**
- `ANDNeuron.LTZone.Output`
- `ANDNeuron.NegGenerator.Output`
- `ANDNeuron.PosGenerator.Output`
- `ANDNeuron.Soma1.ExcChannel.Output`
- `ANDNeuron.Soma1.ExcSynapse1.Output`
- `ANDNeuron.Soma1.ExcSynapse2.Output`
- `ANDNeuron.Soma1.InhChannel.Output`
- `ANDNeuron.Soma1.InhSynapse1.Output`
- `ANDNeuron.Soma2.ExcChannel.Output`
- `ANDNeuron.Soma2.ExcSynapse1.Output`
- ... (всего 27 выходов)

**Количество связей:** 34

---

### Ivan_VKR_3-4_23ab

**Путь:** `Bin\Configs\ivan\NeuroMouse\Ivan_VKR_3-4_23ab`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NPExcChannelBio**: NOTNeuron.Dendrite1_2.ExcChannel, NOTNeuron.Dendrite1_1.ExcChannel, NOTNeuron.Soma1.ExcChannel, NOTNeuron.ExcChannel, NOTNeuron2.Dendrite1_2.ExcChannel (и еще 22)
- **NPInhChannelBio**: NOTNeuron.Dendrite1_2.InhChannel, NOTNeuron.Dendrite1_1.InhChannel, NOTNeuron.Soma1.InhChannel, NOTNeuron.InhChannel, NOTNeuron2.Dendrite1_2.InhChannel (и еще 22)
- **NPMembraneBio**: NOTNeuron.Dendrite1_2, NOTNeuron.Dendrite1_1, NOTNeuron.Soma1, NOTNeuron2.Dendrite1_2, NOTNeuron2.Dendrite1_1 (и еще 15)
- **NPNeuronNegCGenerator**: NOTNeuron.NegGenerator, NOTNeuron2.NegGenerator, NOTNeuron3.NegGenerator, NOTNeuron4.NegGenerator, ANDNeuron.NegGenerator (и еще 2)
- **NPNeuronPosCGenerator**: NOTNeuron.PosGenerator, NOTNeuron2.PosGenerator, NOTNeuron3.PosGenerator, NOTNeuron4.PosGenerator, ANDNeuron.PosGenerator (и еще 2)
- **NPSynapseBio**: NOTNeuron.Dendrite1_2.ExcSynapse1, NOTNeuron.Dendrite1_2.InhSynapse1, NOTNeuron.Dendrite1_1.ExcSynapse1, NOTNeuron.Dendrite1_1.InhSynapse1, NOTNeuron.Soma1.ExcSynapse1 (и еще 61)
- **NPulseGeneratorTransit**: AheadObstacle, LeftObstacle, RightObstacle, AheadObstacle2, LeftObstacle2 (и еще 5)
- **NPulseLTZoneThreshold**: NOTNeuron.LTZone, NOTNeuron2.LTZone, NOTNeuron3.LTZone, NOTNeuron4.LTZone, ANDNeuron.LTZone (и еще 2)
- **NSPNeuronGen**: NOTNeuron, NOTNeuron2, NOTNeuron3, NOTNeuron4, ANDNeuron (и еще 1)

**Входы системы:**
- `ANDNeuron.LTZone.Inputs`
- `ANDNeuron.NegGenerator`
- `ANDNeuron.PosGenerator`
- `ANDNeuron.Soma1.ExcChannel.ChannelInputs`
- `ANDNeuron.Soma1.ExcChannel.SynapticInputs`
- `ANDNeuron.Soma1.ExcSynapse1.Input`
- `ANDNeuron.Soma1.ExcSynapse2.Input`
- `ANDNeuron.Soma1.ExcSynapse3.Input`
- `ANDNeuron.Soma1.InhChannel.ChannelInputs`
- `ANDNeuron.Soma1.InhChannel.SynapticInputs`
- ... (всего 116 входов)

**Выходы системы:**
- `ANDNeuron.LTZone.Output`
- `ANDNeuron.NegGenerator.Output`
- `ANDNeuron.PosGenerator.Output`
- `ANDNeuron.Soma1.ExcChannel.Output`
- `ANDNeuron.Soma1.ExcSynapse1.Output`
- `ANDNeuron.Soma1.ExcSynapse2.Output`
- `ANDNeuron.Soma1.ExcSynapse3.Output`
- `ANDNeuron.Soma1.InhChannel.Output`
- `ANDNeuron.Soma1.InhSynapse1.Output`
- `ANDNeuron.Soma2.ExcChannel.Output`
- ... (всего 96 выходов)

**Количество связей:** 106

---

### Ivan_VKR_3-4_25

**Путь:** `Bin\Configs\ivan\NeuroMouse\Ivan_VKR_3-4_25`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NPExcChannelBio**: NOTNeuron.Dendrite1_2.ExcChannel, NOTNeuron.Dendrite1_1.ExcChannel, NOTNeuron.Soma1.ExcChannel, NOTNeuron.ExcChannel, NOTNeuron2.Dendrite1_2.ExcChannel (и еще 14)
- **NPInhChannelBio**: NOTNeuron.Dendrite1_2.InhChannel, NOTNeuron.Dendrite1_1.InhChannel, NOTNeuron.Soma1.InhChannel, NOTNeuron.InhChannel, NOTNeuron2.Dendrite1_2.InhChannel (и еще 14)
- **NPMembraneBio**: NOTNeuron.Dendrite1_2, NOTNeuron.Dendrite1_1, NOTNeuron.Soma1, NOTNeuron2.Dendrite1_2, NOTNeuron2.Dendrite1_1 (и еще 9)
- **NPNeuronNegCGenerator**: NOTNeuron.NegGenerator, NOTNeuron2.NegGenerator, ANDNeuron.NegGenerator, ANDNeuron2.NegGenerator, NegGenerator
- **NPNeuronPosCGenerator**: NOTNeuron.PosGenerator, NOTNeuron2.PosGenerator, ANDNeuron.PosGenerator, ANDNeuron2.PosGenerator, PosGenerator
- **NPSynapseBio**: NOTNeuron.Dendrite1_2.ExcSynapse1, NOTNeuron.Dendrite1_2.InhSynapse1, NOTNeuron.Dendrite1_1.ExcSynapse1, NOTNeuron.Dendrite1_1.InhSynapse1, NOTNeuron.Soma1.ExcSynapse1 (и еще 39)
- **NPulseGeneratorTransit**: TurnRight, WallAhead, TurnRight2, WallAhead2, NOTGen (и еще 1)
- **NPulseLTZoneThreshold**: NOTNeuron.LTZone, NOTNeuron2.LTZone, ANDNeuron.LTZone, ANDNeuron2.LTZone, LTZone
- **NSPNeuronGen**: NOTNeuron, NOTNeuron2, ANDNeuron, ANDNeuron2

**Входы системы:**
- `ANDNeuron.LTZone.Inputs`
- `ANDNeuron.NegGenerator`
- `ANDNeuron.PosGenerator`
- `ANDNeuron.Soma1.ExcChannel.ChannelInputs`
- `ANDNeuron.Soma1.ExcChannel.SynapticInputs`
- `ANDNeuron.Soma1.ExcSynapse1.Input`
- `ANDNeuron.Soma1.ExcSynapse2.Input`
- `ANDNeuron.Soma1.InhChannel.ChannelInputs`
- `ANDNeuron.Soma1.InhChannel.SynapticInputs`
- `ANDNeuron.Soma1.InputFeedbackSignal`
- ... (всего 74 входов)

**Выходы системы:**
- `ANDNeuron.LTZone.Output`
- `ANDNeuron.NegGenerator.Output`
- `ANDNeuron.PosGenerator.Output`
- `ANDNeuron.Soma1.ExcChannel.Output`
- `ANDNeuron.Soma1.ExcSynapse1.Output`
- `ANDNeuron.Soma1.ExcSynapse2.Output`
- `ANDNeuron.Soma1.InhChannel.Output`
- `ANDNeuron.Soma1.InhSynapse1.Output`
- `ANDNeuron.Soma2.ExcChannel.Output`
- `ANDNeuron.Soma2.ExcSynapse1.Output`
- ... (всего 60 выходов)

**Количество связей:** 68

---

### Ivan_VKR_3-4_4

**Путь:** `Bin\Configs\ivan\NeuroMouse\Ivan_VKR_3-4_4`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NPDelay**: Delay05To15
- **NPExcChannelBio**: IsForward.Soma1.ExcChannel, IsForward.Soma2.ExcChannel, IsForward.ExcChannel, IsBack.Soma1.ExcChannel, IsBack.Soma2.ExcChannel (и еще 66)
- **NPInhChannelBio**: IsForward.Soma1.InhChannel, IsForward.Soma2.InhChannel, IsForward.InhChannel, IsBack.Soma1.InhChannel, IsBack.Soma2.InhChannel (и еще 66)
- **NPMembraneBio**: IsForward.Soma1, IsForward.Soma2, IsBack.Soma1, IsBack.Soma2, IsLeft.Dendrite1_10 (и еще 54)
- **NPNeuronNegCGenerator**: IsForward.NegGenerator, IsBack.NegGenerator, IsLeft.NegGenerator, IsRight.NegGenerator, Forward.NegGenerator (и еще 7)
- **NPNeuronPosCGenerator**: IsForward.PosGenerator, IsBack.PosGenerator, IsLeft.PosGenerator, IsRight.PosGenerator, Forward.PosGenerator (и еще 7)
- **NPSynapseBio**: IsForward.Soma1.ExcSynapse1, IsForward.Soma1.InhSynapse1, IsForward.Soma2.ExcSynapse1, IsForward.Soma2.InhSynapse1, IsForward.ExcSynapse1 (и еще 149)
- **NPulseGeneratorTransit**: LeftEngine, RightEngine, Sinchro05, Sinchro15, NOTGenerator
- **NPulseLTZoneThreshold**: IsForward.LTZone, IsBack.LTZone, IsLeft.LTZone, IsRight.LTZone, Forward.LTZone (и еще 7)
- **NSPNeuronGen**: IsForward, IsBack, IsLeft, IsRight, Forward (и еще 6)

**Входы системы:**
- `Back.LTZone.Inputs`
- `Back.NegGenerator`
- `Back.PosGenerator`
- `Back.Soma1.ExcChannel.ChannelInputs`
- `Back.Soma1.ExcChannel.SynapticInputs`
- `Back.Soma1.ExcSynapse1.Input`
- `Back.Soma1.InhChannel.ChannelInputs`
- `Back.Soma1.InhChannel.SynapticInputs`
- `Back.Soma1.InputFeedbackSignal`
- `Delay05To15.Input`
- ... (всего 231 входов)

**Выходы системы:**
- `Back.LTZone.Output`
- `Back.NegGenerator.Output`
- `Back.PosGenerator.Output`
- `Back.Soma1.ExcChannel.Output`
- `Back.Soma1.ExcSynapse1.Output`
- `Back.Soma1.InhChannel.Output`
- `Back.Soma1.InhSynapse1.Output`
- `Delay05To15.Output`
- `Forward.LTZone.Output`
- `Forward.NegGenerator.Output`
- ... (всего 190 выходов)

**Количество связей:** 224

---

### Ivan_VKR_3-4_8

**Путь:** `Bin\Configs\ivan\NeuroMouse\Ivan_VKR_3-4_8`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NNeuronTrainer**: Fig8.NeuronTrainer1, Fig8.NeuronTrainer2, Fig8.NeuronTrainer3, Fig8.NeuronTrainer4, NeuronTrainer1 (и еще 3)
- **NPExcChannelBio**: Fig8.NeuronTrainer1.Neuron.Dendrite1_20.ExcChannel, Fig8.NeuronTrainer1.Neuron.Dendrite1_19.ExcChannel, Fig8.NeuronTrainer1.Neuron.Dendrite1_18.ExcChannel, Fig8.NeuronTrainer1.Neuron.Dendrite1_17.ExcChannel, Fig8.NeuronTrainer1.Neuron.Dendrite1_16.ExcChannel (и еще 343)
- **NPInhChannelBio**: Fig8.NeuronTrainer1.Neuron.Dendrite1_20.InhChannel, Fig8.NeuronTrainer1.Neuron.Dendrite1_19.InhChannel, Fig8.NeuronTrainer1.Neuron.Dendrite1_18.InhChannel, Fig8.NeuronTrainer1.Neuron.Dendrite1_17.InhChannel, Fig8.NeuronTrainer1.Neuron.Dendrite1_16.InhChannel (и еще 343)
- **NPMembraneBio**: Fig8.NeuronTrainer1.Neuron.Dendrite1_20, Fig8.NeuronTrainer1.Neuron.Dendrite1_19, Fig8.NeuronTrainer1.Neuron.Dendrite1_18, Fig8.NeuronTrainer1.Neuron.Dendrite1_17, Fig8.NeuronTrainer1.Neuron.Dendrite1_16 (и еще 323)
- **NPNeuronNegCGenerator**: Fig8.NeuronTrainer1.Neuron.NegGenerator, Fig8.NeuronTrainer1.NegGenerator, Fig8.NeuronTrainer2.Neuron.NegGenerator, Fig8.NeuronTrainer2.NegGenerator, Fig8.NeuronTrainer3.Neuron.NegGenerator (и еще 15)
- **NPNeuronPosCGenerator**: Fig8.NeuronTrainer1.Neuron.PosGenerator, Fig8.NeuronTrainer1.PosGenerator, Fig8.NeuronTrainer2.Neuron.PosGenerator, Fig8.NeuronTrainer2.PosGenerator, Fig8.NeuronTrainer3.Neuron.PosGenerator (и еще 15)
- **NPSynapseBio**: Fig8.NeuronTrainer1.Neuron.Dendrite1_20.ExcSynapse1, Fig8.NeuronTrainer1.Neuron.Dendrite1_20.ExcSynapse2, Fig8.NeuronTrainer1.Neuron.Dendrite1_20.ExcSynapse3, Fig8.NeuronTrainer1.Neuron.Dendrite1_20.ExcSynapse4, Fig8.NeuronTrainer1.Neuron.Dendrite1_20.ExcSynapse5 (и еще 1867)
- **NPulseGeneratorTransit**: Fig8.Source1, Fig8.Source2, Fig8.NeuronTrainer1.Source1, Fig8.NeuronTrainer1.Source2, Fig8.NeuronTrainer2.Source1 (и еще 15)
- **NPulseLTZoneThreshold**: Fig8.NeuronTrainer1.Neuron.LTZone, Fig8.NeuronTrainer1.LTZone, Fig8.NeuronTrainer2.Neuron.LTZone, Fig8.NeuronTrainer2.LTZone, Fig8.NeuronTrainer3.Neuron.LTZone (и еще 15)
- **NSPNeuronGen**: Fig8.NeuronTrainer1.Neuron, Fig8.NeuronTrainer2.Neuron, Fig8.NeuronTrainer3.Neuron, Fig8.NeuronTrainer4.Neuron, Fig8.Neuron (и еще 5)
- **NSpikeClassifier**: Fig8

**Входы системы:**
- `Fig8.NegGenerator`
- `Fig8.Neuron.NegGenerator`
- `Fig8.Neuron.PosGenerator`
- `Fig8.NeuronTrainer1.NegGenerator`
- `Fig8.NeuronTrainer1.Neuron.Dendrite1_1.ExcChannel.ChannelInputs`
- `Fig8.NeuronTrainer1.Neuron.Dendrite1_1.ExcChannel.SynapticInputs`
- `Fig8.NeuronTrainer1.Neuron.Dendrite1_1.InhChannel.ChannelInputs`
- `Fig8.NeuronTrainer1.Neuron.Dendrite1_1.InhChannel.SynapticInputs`
- `Fig8.NeuronTrainer1.Neuron.Dendrite1_10.ExcChannel.ChannelInputs`
- `Fig8.NeuronTrainer1.Neuron.Dendrite1_10.ExcChannel.SynapticInputs`
- ... (всего 426 входов)

**Выходы системы:**
- `Fig8.NeuronTrainer1.Neuron.Dendrite1_1.ExcChannel.Output`
- `Fig8.NeuronTrainer1.Neuron.Dendrite1_1.ExcSynapse1.Output`
- `Fig8.NeuronTrainer1.Neuron.Dendrite1_1.InhChannel.Output`
- `Fig8.NeuronTrainer1.Neuron.Dendrite1_1.InhSynapse1.Output`
- `Fig8.NeuronTrainer1.Neuron.Dendrite1_10.ExcChannel.Output`
- `Fig8.NeuronTrainer1.Neuron.Dendrite1_10.ExcSynapse1.Output`
- `Fig8.NeuronTrainer1.Neuron.Dendrite1_10.InhChannel.Output`
- `Fig8.NeuronTrainer1.Neuron.Dendrite1_10.InhSynapse1.Output`
- `Fig8.NeuronTrainer1.Neuron.Dendrite1_11.ExcChannel.Output`
- `Fig8.NeuronTrainer1.Neuron.Dendrite1_11.ExcSynapse1.Output`
- ... (всего 352 выходов)

**Количество связей:** 472

---

### Ivan_VKR_3-4_8_renamed

**Путь:** `Bin\Configs\ivan\NeuroMouse\Ivan_VKR_3-4_8_renamed`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NNeuronTrainer**: Fig8.EvalBl_0-005, Fig8.EvalBl_005-010, Fig8.EvalBl_010-015, Fig8.EvalBl_015-020, EvalBl_0-005 (и еще 3)
- **NPExcChannelBio**: Fig8.EvalBl_0-005.Neuron.Dendrite1_20.ExcChannel, Fig8.EvalBl_0-005.Neuron.Dendrite1_19.ExcChannel, Fig8.EvalBl_0-005.Neuron.Dendrite1_18.ExcChannel, Fig8.EvalBl_0-005.Neuron.Dendrite1_17.ExcChannel, Fig8.EvalBl_0-005.Neuron.Dendrite1_16.ExcChannel (и еще 343)
- **NPInhChannelBio**: Fig8.EvalBl_0-005.Neuron.Dendrite1_20.InhChannel, Fig8.EvalBl_0-005.Neuron.Dendrite1_19.InhChannel, Fig8.EvalBl_0-005.Neuron.Dendrite1_18.InhChannel, Fig8.EvalBl_0-005.Neuron.Dendrite1_17.InhChannel, Fig8.EvalBl_0-005.Neuron.Dendrite1_16.InhChannel (и еще 343)
- **NPMembraneBio**: Fig8.EvalBl_0-005.Neuron.Dendrite1_20, Fig8.EvalBl_0-005.Neuron.Dendrite1_19, Fig8.EvalBl_0-005.Neuron.Dendrite1_18, Fig8.EvalBl_0-005.Neuron.Dendrite1_17, Fig8.EvalBl_0-005.Neuron.Dendrite1_16 (и еще 323)
- **NPNeuronNegCGenerator**: Fig8.EvalBl_0-005.Neuron.NegGenerator, Fig8.EvalBl_0-005.NegGenerator, Fig8.EvalBl_005-010.Neuron.NegGenerator, Fig8.EvalBl_005-010.NegGenerator, Fig8.EvalBl_010-015.Neuron.NegGenerator (и еще 15)
- **NPNeuronPosCGenerator**: Fig8.EvalBl_0-005.Neuron.PosGenerator, Fig8.EvalBl_0-005.PosGenerator, Fig8.EvalBl_005-010.Neuron.PosGenerator, Fig8.EvalBl_005-010.PosGenerator, Fig8.EvalBl_010-015.Neuron.PosGenerator (и еще 15)
- **NPSynapseBio**: Fig8.EvalBl_0-005.Neuron.Dendrite1_20.ExcSynapse1, Fig8.EvalBl_0-005.Neuron.Dendrite1_20.ExcSynapse2, Fig8.EvalBl_0-005.Neuron.Dendrite1_20.ExcSynapse3, Fig8.EvalBl_0-005.Neuron.Dendrite1_20.ExcSynapse4, Fig8.EvalBl_0-005.Neuron.Dendrite1_20.ExcSynapse5 (и еще 1867)
- **NPulseGeneratorTransit**: Fig8.SensorInput, Fig8.SynchroPulse, Fig8.EvalBl_0-005.Source1, Fig8.EvalBl_0-005.Source2, Fig8.EvalBl_005-010.Source1 (и еще 19)
- **NPulseLTZoneThreshold**: Fig8.EvalBl_0-005.Neuron.LTZone, Fig8.EvalBl_0-005.LTZone, Fig8.EvalBl_005-010.Neuron.LTZone, Fig8.EvalBl_005-010.LTZone, Fig8.EvalBl_010-015.Neuron.LTZone (и еще 15)
- **NSPNeuronGen**: Fig8.EvalBl_0-005.Neuron, Fig8.EvalBl_005-010.Neuron, Fig8.EvalBl_010-015.Neuron, Fig8.EvalBl_015-020.Neuron, Fig8.Neuron (и еще 5)
- **NSpikeClassifier**: Fig8

**Входы системы:**
- `EvalBl_0-005.NegGenerator`
- `EvalBl_0-005.Neuron.NegGenerator`
- `EvalBl_0-005.Neuron.PosGenerator`
- `EvalBl_0-005.PosGenerator`
- `EvalBl_0-005.Source1`
- `EvalBl_0-005.Source2`
- `EvalBl_005-010.NegGenerator`
- `EvalBl_005-010.Neuron.NegGenerator`
- `EvalBl_005-010.Neuron.PosGenerator`
- `EvalBl_005-010.PosGenerator`
- ... (всего 430 входов)

**Выходы системы:**
- `Fig8.EvalBl_0-005.Neuron.Dendrite1_1.ExcChannel.Output`
- `Fig8.EvalBl_0-005.Neuron.Dendrite1_1.ExcSynapse1.Output`
- `Fig8.EvalBl_0-005.Neuron.Dendrite1_1.InhChannel.Output`
- `Fig8.EvalBl_0-005.Neuron.Dendrite1_1.InhSynapse1.Output`
- `Fig8.EvalBl_0-005.Neuron.Dendrite1_10.ExcChannel.Output`
- `Fig8.EvalBl_0-005.Neuron.Dendrite1_10.ExcSynapse1.Output`
- `Fig8.EvalBl_0-005.Neuron.Dendrite1_10.InhChannel.Output`
- `Fig8.EvalBl_0-005.Neuron.Dendrite1_10.InhSynapse1.Output`
- `Fig8.EvalBl_0-005.Neuron.Dendrite1_11.ExcChannel.Output`
- `Fig8.EvalBl_0-005.Neuron.Dendrite1_11.ExcSynapse1.Output`
- ... (всего 352 выходов)

**Количество связей:** 472

---

## OldExperiments

### AfferentNeurons

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\AfferentNeurons`

**Назначение:** Модель LIF нейрона

**Название проекта:** NoName

**Количество каналов:** 0

**Основные компоненты:**
- **NCGenerator**: CGenerator
- **NPLTZone**: AfferentNeuron.LTZone
- **NPNeuronChannel**: AfferentNeuron.PNeuronMembrane.PosChannel, AfferentNeuron.PNeuronMembrane.NegChannel, AfferentNeuron.PosChannel, AfferentNeuron.NegChannel, PNeuronMembrane.PosChannel (и еще 3)
- **NPNeuronMembrane**: AfferentNeuron.PNeuronMembrane, PNeuronMembrane
- **NPNeuronNegCGenerator**: AfferentNeuron.PNeuronNegCGenerator, PNeuronNegCGenerator
- **NPNeuronPosCGenerator**: AfferentNeuron.PNeuronPosCGenerator, PNeuronPosCGenerator
- **NPSimpleLTZone**: AfferentNeuron2.LTZone, LTZone
- **NPSynapse**: AfferentNeuron.PNeuronMembrane.PosChannel.Synapse, AfferentNeuron.PNeuronMembrane.PosChannel.Synapse2, AfferentNeuron.PNeuronMembrane.PosChannel.Synapse3, AfferentNeuron.PNeuronMembrane.NegChannel.Synapse, AfferentNeuron.PNeuronMembrane.NegChannel.Synapse2 (и еще 31)
- **NReceptor**: AfferentNeuron.Receptor, AfferentNeuron2.Receptor, Receptor
- **NSAfferentNeuron**: AfferentNeuron
- **NSimpleAfferentNeuron**: AfferentNeuron2

**Входы системы:**
- `AfferentNeuron.LTZone.DataInput0`
- `AfferentNeuron.LTZone.DataInput1`
- `AfferentNeuron.PNeuronMembrane.DataInput0`
- `AfferentNeuron.PNeuronMembrane.NegChannel.DataInput0`
- `AfferentNeuron.PNeuronMembrane.PosChannel.DataInput0`
- `AfferentNeuron.PNeuronNegCGenerator`
- `AfferentNeuron.PNeuronPosCGenerator`
- `AfferentNeuron.Receptor.DataInput0`
- `AfferentNeuron2.LTZone.DataInput0`
- `AfferentNeuron2.Receptor.DataInput0`
- ... (всего 13 входов)

**Выходы системы:**
- `AfferentNeuron.LTZone.DataOutput0`
- `AfferentNeuron.PNeuronMembrane.NegChannel.DataOutput0`
- `AfferentNeuron.PNeuronMembrane.PosChannel.DataOutput0`
- `AfferentNeuron.PNeuronNegCGenerator.DataOutput0`
- `AfferentNeuron.Receptor.DataOutput0`
- `AfferentNeuron2.Receptor.DataOutput0`
- `CGenerator.DataOutput0`

**Количество связей:** 8

---

### AsfMotionControl

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\AsfMotionControl`

**Назначение:** Система управления движением

**Количество каналов:** 0

**Основные компоненты:**
- **NAsfNewSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NAsfNewSimplestAfferentBranchedMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NCGenerator**: CGenerator, EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.Ib_NegIntervalSeparator1, EngineControlRangeAfferent.Ib_PosIntervalSeparator1, EngineControlRangeAfferent.II_NegIntervalSeparator1, EngineControlRangeAfferent.II_PosIntervalSeparator1, EngineControlRangeAfferent.Ia_NegIntervalSeparator1 (и еще 7)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NManipulatorSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.Motoneuron1, EngineControlRangeAfferent.MotionElement0.Motoneuron2, EngineControlRangeAfferent.MotionElement0.PostAfferent14, EngineControlRangeAfferent.MotionElement0.PostAfferent24, EngineControlRangeAfferent.Motoneuron1 (и еще 11)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, IIPosAfferentGenerator, IINegAfferentGenerator
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTZone, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTZone, EngineControlRangeAfferent.Motoneuron1.LTZone (и еще 11)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTMembrane, EngineControlRangeAfferent.MotionElement0.LTMembrane (и еще 15)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 15)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 15)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_II2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.LTZone (и еще 23)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2.PosChannel (и еще 163)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane3, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronMembrane2 (и еще 39)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_II2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.Receptor (и еще 23)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.Afferent_II1, EngineControlRangeAfferent.MotionElement0.Afferent_II2, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1 (и еще 19)
- **NWPhysicalManipulator**: WPhysicalManipulator

**Входы системы:**
- `AfferentSource1`
- `CGenerator`
- `DCEngine.DataInput0`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.II_NegIntervalSeparator1.DataInput0`
- `EngineControlRangeAfferent.II_PosIntervalSeparator1.DataInput0`
- `EngineControlRangeAfferent.Ia_NegIntervalSeparator1.DataInput0`
- `EngineControlRangeAfferent.Ia_PosIntervalSeparator1.DataInput0`
- ... (всего 132 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.II_NegIntervalSeparator1.DataOutput0`
- `EngineControlRangeAfferent.II_PosIntervalSeparator1.DataOutput0`
- `EngineControlRangeAfferent.Ia_NegIntervalSeparator1.DataOutput0`
- `EngineControlRangeAfferent.Ia_PosIntervalSeparator1.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.Afferent_II1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.Afferent_II1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.Afferent_II2.LTZone.DataOutput0`
- ... (всего 60 выходов)

**Количество связей:** 86

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### AsfMotionControl3

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\AsfMotionControl3`

**Назначение:** Система управления движением

**Количество каналов:** 0

**Основные компоненты:**
- **NAsfNewSimplestAfferentBranchedEngineControl3**: EngineControlRangeAfferent
- **NAsfNewSimplestAfferentBranchedMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent.MotionElement1, EngineControlRangeAfferent.MotionElement2, MotionElement0, MotionElement1 (и еще 1)
- **NCGenerator**: CGenerator, EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.Ib_NegIntervalSeparator1, EngineControlRangeAfferent.Ib_NegIntervalSeparator2, EngineControlRangeAfferent.Ib_NegIntervalSeparator3, EngineControlRangeAfferent.Ib_PosIntervalSeparator1, EngineControlRangeAfferent.Ib_PosIntervalSeparator2 (и еще 31)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NManipulatorSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.Motoneuron1, EngineControlRangeAfferent.MotionElement0.Motoneuron2, EngineControlRangeAfferent.MotionElement0.PostAfferent14, EngineControlRangeAfferent.MotionElement0.PostAfferent24, EngineControlRangeAfferent.MotionElement1.Motoneuron1 (и еще 27)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, IIPosAfferentGenerator, IINegAfferentGenerator
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTZone, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTZone, EngineControlRangeAfferent.MotionElement1.Motoneuron1.LTZone (и еще 27)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTMembrane, EngineControlRangeAfferent.MotionElement0.LTMembrane (и еще 35)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 35)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 35)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_II2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.LTZone (и еще 51)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2.PosChannel (и еще 427)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane3, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane4, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane5 (и еще 131)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_II2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.Receptor (и еще 51)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.Afferent_II1, EngineControlRangeAfferent.MotionElement0.Afferent_II2, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1 (и еще 43)
- **NWPhysicalManipulator**: WPhysicalManipulator

**Входы системы:**
- `AfferentSource1`
- `CGenerator`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator`
- ... (всего 87 входов)

**Количество связей:** 323

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### AsfMotionControl5

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\AsfMotionControl5`

**Назначение:** Система управления движением

**Количество каналов:** 0

**Основные компоненты:**
- **NAsfNewSimplestAfferentBranchedEngineControl5**: EngineControlRangeAfferent
- **NAsfNewSimplestAfferentBranchedMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent.MotionElement1, EngineControlRangeAfferent.MotionElement2, EngineControlRangeAfferent.MotionElement3, EngineControlRangeAfferent.MotionElement4 (и еще 5)
- **NCGenerator**: CGenerator, EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.Ib_NegIntervalSeparator1, EngineControlRangeAfferent.Ib_NegIntervalSeparator2, EngineControlRangeAfferent.Ib_NegIntervalSeparator3, EngineControlRangeAfferent.Ib_NegIntervalSeparator4, EngineControlRangeAfferent.Ib_NegIntervalSeparator5 (и еще 55)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NManipulatorSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.Motoneuron1, EngineControlRangeAfferent.MotionElement0.Motoneuron2, EngineControlRangeAfferent.MotionElement0.PostAfferent14, EngineControlRangeAfferent.MotionElement0.PostAfferent24, EngineControlRangeAfferent.MotionElement1.Motoneuron1 (и еще 43)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, IIPosAfferentGenerator, IINegAfferentGenerator
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTZone, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTZone, EngineControlRangeAfferent.MotionElement1.Motoneuron1.LTZone (и еще 43)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTMembrane, EngineControlRangeAfferent.MotionElement0.LTMembrane (и еще 55)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 55)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 55)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_II2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.LTZone (и еще 79)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2.PosChannel (и еще 643)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane3, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane4, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane5 (и еще 199)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_II2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.Receptor (и еще 79)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.Afferent_II1, EngineControlRangeAfferent.MotionElement0.Afferent_II2, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1 (и еще 67)
- **NWPhysicalManipulator**: WPhysicalManipulator

**Входы системы:**
- `AfferentSource1`
- `CGenerator`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator`
- ... (всего 127 входов)

**Количество связей:** 545

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### AsfPhysMotionControl

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\AsfPhysMotionControl`

**Назначение:** Система управления движением

**Количество каналов:** 0

**Основные компоненты:**
- **NAsfNewSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NAsfNewSimplestAfferentBranchedMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NCGenerator**: CGenerator, EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.Ib_NegIntervalSeparator1, EngineControlRangeAfferent.Ib_PosIntervalSeparator1, EngineControlRangeAfferent.II_NegIntervalSeparator1, EngineControlRangeAfferent.II_PosIntervalSeparator1, EngineControlRangeAfferent.Ia_NegIntervalSeparator1 (и еще 7)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NManipulatorSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.Motoneuron1, EngineControlRangeAfferent.MotionElement0.Motoneuron2, EngineControlRangeAfferent.MotionElement0.PostAfferent14, EngineControlRangeAfferent.MotionElement0.PostAfferent24, EngineControlRangeAfferent.Motoneuron1 (и еще 11)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, IIPosAfferentGenerator, IINegAfferentGenerator
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTZone, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTZone, EngineControlRangeAfferent.Motoneuron1.LTZone (и еще 11)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTMembrane, EngineControlRangeAfferent.MotionElement0.LTMembrane (и еще 15)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 15)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 15)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_II2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.LTZone (и еще 23)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2.PosChannel (и еще 211)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane3, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane4, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane5 (и еще 63)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_II2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.Receptor (и еще 23)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.Afferent_II1, EngineControlRangeAfferent.MotionElement0.Afferent_II2, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1 (и еще 19)
- **NWPhysicalManipulator**: WPhysicalManipulator

**Входы системы:**
- `AfferentSource1`
- `CGenerator`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator`
- ... (всего 47 входов)

**Количество связей:** 115

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### AsfPhysMotionControl3

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\AsfPhysMotionControl3`

**Назначение:** Система управления движением

**Количество каналов:** 0

**Основные компоненты:**
- **NAsfNewSimplestAfferentBranchedEngineControl3**: EngineControlRangeAfferent
- **NAsfNewSimplestAfferentBranchedMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent.MotionElement1, EngineControlRangeAfferent.MotionElement2, MotionElement0, MotionElement1 (и еще 1)
- **NCGenerator**: CGenerator, EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.Ib_NegIntervalSeparator1, EngineControlRangeAfferent.Ib_NegIntervalSeparator2, EngineControlRangeAfferent.Ib_NegIntervalSeparator3, EngineControlRangeAfferent.Ib_PosIntervalSeparator1, EngineControlRangeAfferent.Ib_PosIntervalSeparator2 (и еще 31)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NManipulatorSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.Motoneuron1, EngineControlRangeAfferent.MotionElement0.Motoneuron2, EngineControlRangeAfferent.MotionElement0.PostAfferent14, EngineControlRangeAfferent.MotionElement0.PostAfferent24, EngineControlRangeAfferent.MotionElement1.Motoneuron1 (и еще 27)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, IIPosAfferentGenerator, IINegAfferentGenerator
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTZone, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTZone, EngineControlRangeAfferent.MotionElement1.Motoneuron1.LTZone (и еще 27)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTMembrane, EngineControlRangeAfferent.MotionElement0.LTMembrane (и еще 35)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 35)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 35)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_II2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.LTZone (и еще 51)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2.PosChannel (и еще 427)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane3, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane4, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane5 (и еще 131)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_II2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.Receptor (и еще 51)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.Afferent_II1, EngineControlRangeAfferent.MotionElement0.Afferent_II2, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1 (и еще 43)
- **NWPhysicalManipulator**: WPhysicalManipulator

**Входы системы:**
- `AfferentSource1`
- `CGenerator`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator`
- ... (всего 87 входов)

**Количество связей:** 329

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### AsfPhysMotionControl5

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\AsfPhysMotionControl5`

**Назначение:** Система управления движением

**Количество каналов:** 0

**Основные компоненты:**
- **NAsfNewSimplestAfferentBranchedEngineControl5**: EngineControlRangeAfferent
- **NAsfNewSimplestAfferentBranchedMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent.MotionElement1, EngineControlRangeAfferent.MotionElement2, EngineControlRangeAfferent.MotionElement3, EngineControlRangeAfferent.MotionElement4 (и еще 5)
- **NCGenerator**: CGenerator, EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.Ib_NegIntervalSeparator1, EngineControlRangeAfferent.Ib_NegIntervalSeparator2, EngineControlRangeAfferent.Ib_NegIntervalSeparator3, EngineControlRangeAfferent.Ib_NegIntervalSeparator4, EngineControlRangeAfferent.Ib_NegIntervalSeparator5 (и еще 55)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NManipulatorSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.Motoneuron1, EngineControlRangeAfferent.MotionElement0.Motoneuron2, EngineControlRangeAfferent.MotionElement0.PostAfferent14, EngineControlRangeAfferent.MotionElement0.PostAfferent24, EngineControlRangeAfferent.MotionElement1.Motoneuron1 (и еще 43)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, IIPosAfferentGenerator, IINegAfferentGenerator
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTZone, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTZone, EngineControlRangeAfferent.MotionElement1.Motoneuron1.LTZone (и еще 43)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTMembrane, EngineControlRangeAfferent.MotionElement0.LTMembrane (и еще 55)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 55)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 55)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_II2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.LTZone (и еще 79)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2.PosChannel (и еще 643)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane3, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane4, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane5 (и еще 199)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_II2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.Receptor (и еще 79)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.Afferent_II1, EngineControlRangeAfferent.MotionElement0.Afferent_II2, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1 (и еще 67)
- **NWPhysicalManipulator**: WPhysicalManipulator

**Входы системы:**
- `AfferentSource1`
- `CGenerator`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator`
- ... (всего 127 входов)

**Количество связей:** 555

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### AslsMotionControl1

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\AslsMotionControl1`

**Назначение:** Система управления движением

**Количество каналов:** 0

**Основные компоненты:**
- **NAslsNewSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NAslsNewSimplestAfferentBranchedMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.Ib_NegIntervalSeparator1, EngineControlRangeAfferent.Ib_PosIntervalSeparator1, EngineControlRangeAfferent.II_NegIntervalSeparator1, EngineControlRangeAfferent.II_PosIntervalSeparator1, EngineControlRangeAfferent.Ia_NegIntervalSeparator1 (и еще 11)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NManipulatorSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.Motoneuron1, EngineControlRangeAfferent.MotionElement0.Motoneuron2, EngineControlRangeAfferent.MotionElement0.PostAfferent14, EngineControlRangeAfferent.MotionElement0.PostAfferent24, EngineControlRangeAfferent.Motoneuron1 (и еще 11)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, IIPosAfferentGenerator, IINegAfferentGenerator
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTZone, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTZone, EngineControlRangeAfferent.Motoneuron1.LTZone (и еще 11)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTMembrane, EngineControlRangeAfferent.MotionElement0.LTMembrane (и еще 15)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 15)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 15)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_II2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.LTZone (и еще 31)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2.PosChannel (и еще 211)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane3, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane4, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane5 (и еще 63)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_II2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.Receptor (и еще 31)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.Afferent_II1, EngineControlRangeAfferent.MotionElement0.Afferent_II2, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1 (и еще 27)
- **NWPhysicalManipulator**: WPhysicalManipulator

**Входы системы:**
- `AfferentSource1`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator`
- ... (всего 46 входов)

**Количество связей:** 116

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### Gyro

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\Gyro`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Количество каналов:** 0

**Основные компоненты:**
- **NAsfNewSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NAsfNewSimplestAfferentBranchedMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NAstaticGyro**: NAstaticGyro
- **NCGenerator**: CGenerator, EngineControlRangeAfferent.AfferentSource1, EngineControlRangeAfferent.CGenerator, EngineControlRangeAfferent.CGenerator2, EngineControlRangeAfferent.CGenerator3 (и еще 3)
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.Ib_NegIntervalSeparator1, EngineControlRangeAfferent.Ib_PosIntervalSeparator1, EngineControlRangeAfferent.II_NegIntervalSeparator1, EngineControlRangeAfferent.II_PosIntervalSeparator1, EngineControlRangeAfferent.Ia_NegIntervalSeparator1 (и еще 7)
- **NManipulatorAndGyro**: NManipulatorAndGyro
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NManipulatorSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.Motoneuron1, EngineControlRangeAfferent.MotionElement0.Motoneuron2, EngineControlRangeAfferent.MotionElement0.PostAfferent14, EngineControlRangeAfferent.MotionElement0.PostAfferent24, EngineControlRangeAfferent.Motoneuron1 (и еще 11)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, IIPosAfferentGenerator, IINegAfferentGenerator
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTZone, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTZone, EngineControlRangeAfferent.Motoneuron1.LTZone (и еще 11)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTMembrane, EngineControlRangeAfferent.MotionElement0.LTMembrane (и еще 15)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 15)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 15)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_II2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.LTZone (и еще 23)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2.PosChannel (и еще 211)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane3, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane4, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane5 (и еще 63)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_II2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.Receptor (и еще 23)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.Afferent_II1, EngineControlRangeAfferent.MotionElement0.Afferent_II2, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1 (и еще 19)
- **NWPhysicalManipulator**: WPhysicalManipulator

**Входы системы:**
- `AfferentSource1`
- `CGenerator`
- `CGenerator2`
- `CGenerator3`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.CGenerator`
- `EngineControlRangeAfferent.CGenerator2`
- `EngineControlRangeAfferent.CGenerator3`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- ... (всего 52 входов)

**Количество связей:** 109

---

### IzhikevichTest

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\IzhikevichTest`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Название проекта:** IzhikevichTest

**Количество каналов:** 0

**Основные компоненты:**
- **NCGenerator**: CGenerator
- **NPGenerator**: PGenerator
- **NPulseLTZoneIzhikevich**: PulseNeuron.LTZone, LTZone
- **NPulseMembraneIzhikevich**: PulseNeuron.PulseMembrane, PulseMembrane
- **NPulseNeuronIzhikevich**: PulseNeuron
- **NPulseSynChannelIzhikevich**: PulseNeuron.PulseMembrane.PosChannel, PulseNeuron.PosChannel, PulseMembrane.PosChannel, PosChannel

**Входы системы:**
- `CGenerator`
- `PGenerator`
- `PulseNeuron.LTZone.DataInput0`
- `PulseNeuron.LTZone.DataInput1`
- `PulseNeuron.PulseMembrane.DataInput0`
- `PulseNeuron.PulseMembrane.PosChannel.DataInput0`

**Выходы системы:**
- `CGenerator.DataOutput0`
- `PulseNeuron.LTZone.DataOutput0`
- `PulseNeuron.PulseMembrane.PosChannel.DataOutput0`
- `PulseNeuron.PulseMembrane.PosChannel.DataOutput1`

**Количество связей:** 5

---

### Muscle

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\Muscle`

**Назначение:** Модель управления мышцами

**Основные компоненты:**
- **NEyeMuscle**: EyeMuscle
- **NPGenerator**: PGenerator

**Входы системы:**
- `PGenerator`

**Количество связей:** 1

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### NeuronTimeConstnantsTest

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\NeuronTimeConstnantsTest`

**Назначение:** Модель LIF нейрона

**Название проекта:** Neuron time parameters test

**Количество каналов:** 0

**Основные компоненты:**
- **NNewSynMotoneuron**: Motoneuron2
- **NNewSynSPNeuron**: SPNeuron2
- **NPGenerator**: PGenerator, PGenerator2
- **NPLTZone**: SPNeuron.LTZone, Motoneuron.LTZone, SPNeuron2.LTZone, Motoneuron2.LTZone, SPNeuron3.LTZone (и еще 1)
- **NPLTZoneSynNeuronMembrane**: SPNeuron2.LTMembrane, Motoneuron2.LTMembrane, LTMembrane
- **NPNeuronNegCGenerator**: SPNeuron.PNeuronNegCGenerator, Motoneuron.PNeuronNegCGenerator, SPNeuron2.PNeuronNegCGenerator, Motoneuron2.PNeuronNegCGenerator, SPNeuron3.PNeuronNegCGenerator (и еще 1)
- **NPNeuronPosCGenerator**: SPNeuron.PNeuronPosCGenerator, Motoneuron.PNeuronPosCGenerator, SPNeuron2.PNeuronPosCGenerator, Motoneuron2.PNeuronPosCGenerator, SPNeuron3.PNeuronPosCGenerator (и еще 1)
- **NPSynNeuronChannel**: SPNeuron.LTMembrane.PosChannel, SPNeuron.LTMembrane.NegChannel, SPNeuron.PNeuronMembrane.PosChannel, SPNeuron.PNeuronMembrane.NegChannel, SPNeuron.PosChannel (и еще 41)
- **NPSynNeuronMembrane**: SPNeuron.LTMembrane, SPNeuron.PNeuronMembrane, Motoneuron.LTMembrane, Motoneuron.PNeuronMembrane, Motoneuron.PNeuronMembrane2 (и еще 9)
- **NSynMotoneuron**: Motoneuron
- **NSynSPNeuron**: SPNeuron, SPNeuron3

**Входы системы:**
- `Motoneuron.LTMembrane.DataInput0`
- `Motoneuron.LTMembrane.NegChannel.DataInput0`
- `Motoneuron.LTMembrane.NegChannel.DataInput1`
- `Motoneuron.LTMembrane.NegChannel.DataInput2`
- `Motoneuron.LTMembrane.PosChannel.DataInput0`
- `Motoneuron.LTMembrane.PosChannel.DataInput1`
- `Motoneuron.LTMembrane.PosChannel.DataInput2`
- `Motoneuron.LTZone.DataInput0`
- `Motoneuron.LTZone.DataInput1`
- `Motoneuron.PNeuronMembrane.NegChannel.DataInput0`
- ... (всего 72 входов)

**Выходы системы:**
- `Motoneuron.LTMembrane.NegChannel.DataOutput0`
- `Motoneuron.LTMembrane.PosChannel.DataOutput0`
- `Motoneuron.LTZone.DataOutput0`
- `Motoneuron.PNeuronMembrane.NegChannel.DataOutput0`
- `Motoneuron.PNeuronMembrane.PosChannel.DataOutput0`
- `Motoneuron.PNeuronMembrane2.NegChannel.DataOutput0`
- `Motoneuron.PNeuronMembrane2.PosChannel.DataOutput0`
- `Motoneuron.PNeuronMembrane3.NegChannel.DataOutput0`
- `Motoneuron.PNeuronMembrane3.PosChannel.DataOutput0`
- `Motoneuron.PNeuronNegCGenerator.DataOutput0`
- ... (всего 43 выходов)

**Количество связей:** 58

---

### PCN test

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\PCN test`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfNewSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator21, EngineControlRangeAfferent.PosIntervalSeparator21, EngineControlRangeAfferent.NegIntervalSeparator31 (и еще 27)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NManipulatorSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent.MotionElement1, EngineControlRangeAfferent.MotionElement2, EngineControlRangeAfferent.MotionElement3, EngineControlRangeAfferent.MotionElement4 (и еще 11)
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotionElement1.MotoneuronL (и еще 67)
- **NPCN**: NPCN
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, IIPosAfferentGenerator, IINegAfferentGenerator
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.LTZone (и еще 85)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTMembrane, EngineControlRangeAfferent.MotionElement0.LTMembrane (и еще 85)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 85)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 85)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement1.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement1.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement2.AfferentR1.LTZone (и еще 31)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel (и еще 535)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PNeuronMembrane (и еще 85)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.MotionElement1.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement1.AfferentL1.Receptor (и еще 49)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement1.AfferentR1, EngineControlRangeAfferent.MotionElement1.AfferentL1, EngineControlRangeAfferent.MotionElement2.AfferentR1 (и еще 31)
- **NWPhysicalManipulator**: WPhysicalManipulator

**Входы системы:**
- `AfferentSource1`
- `DCEngine.DataInput0`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.DataInput0`
- ... (всего 527 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel.DataOutput0`
- ... (всего 279 выходов)

**Количество связей:** 343

---

### Pendulum

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\Pendulum`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfNewSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: CGenerator, EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, EngineControlRangeAfferent.NegIntervalSeparator13 (и еще 11)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, IIPosAfferentGenerator, IINegAfferentGenerator (и еще 1)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTZone (и еще 39)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronNegCGenerator (и еще 39)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronPosCGenerator (и еще 39)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR3.LTZone (и еще 27)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane.PosChannel (и еще 171)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronMembrane (и еще 39)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR3.Receptor (и еще 31)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.MotionElement0.AfferentR3 (и еще 27)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotionElement0.PostAfferentL2 (и еще 35)

**Входы системы:**
- `AfferentSource1`
- `CGenerator`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.InternalGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataInput0`
- ... (всего 203 входов)

**Выходы системы:**
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL3.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL3.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL4.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL4.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- ... (всего 84 выходов)

**Количество связей:** 109

---

### Pendulum3

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\Pendulum3`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Количество каналов:** 0

**Основные компоненты:**
- **NAsfNewSimplestAfferentBranchedEngineControl3**: EngineControlRangeAfferent2
- **NAsfNewSimplestAfferentBranchedMotionElement**: EngineControlRangeAfferent2.MotionElement0, EngineControlRangeAfferent2.MotionElement1, EngineControlRangeAfferent2.MotionElement2, MotionElement0, MotionElement1 (и еще 1)
- **NCGenerator**: CGenerator, EngineControlRangeAfferent2.AfferentSource1, AfferentSource1
- **NIntervalSeparator**: EngineControlRangeAfferent2.Ib_NegIntervalSeparator1, EngineControlRangeAfferent2.Ib_NegIntervalSeparator2, EngineControlRangeAfferent2.Ib_NegIntervalSeparator3, EngineControlRangeAfferent2.Ib_PosIntervalSeparator1, EngineControlRangeAfferent2.Ib_PosIntervalSeparator2 (и еще 31)
- **NManipulatorInput**: EngineControlRangeAfferent2.NManipulatorInput1, NManipulatorInput1
- **NManipulatorSource**: EngineControlRangeAfferent2.NManipulatorSource1, NManipulatorSource1
- **NNewSynSPNeuron**: EngineControlRangeAfferent2.MotionElement0.Motoneuron1, EngineControlRangeAfferent2.MotionElement0.Motoneuron2, EngineControlRangeAfferent2.MotionElement0.PostAfferent14, EngineControlRangeAfferent2.MotionElement0.PostAfferent24, EngineControlRangeAfferent2.MotionElement1.Motoneuron1 (и еще 27)
- **NPGenerator**: EngineControlRangeAfferent2.IIPosAfferentGenerator, EngineControlRangeAfferent2.IINegAfferentGenerator, IIPosAfferentGenerator, IINegAfferentGenerator
- **NPLTZone**: EngineControlRangeAfferent2.MotionElement0.Motoneuron1.LTZone, EngineControlRangeAfferent2.MotionElement0.Motoneuron2.LTZone, EngineControlRangeAfferent2.MotionElement0.PostAfferent14.LTZone, EngineControlRangeAfferent2.MotionElement0.PostAfferent24.LTZone, EngineControlRangeAfferent2.MotionElement1.Motoneuron1.LTZone (и еще 27)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent2.MotionElement0.Motoneuron1.LTMembrane, EngineControlRangeAfferent2.MotionElement0.Motoneuron2.LTMembrane, EngineControlRangeAfferent2.MotionElement0.PostAfferent14.LTMembrane, EngineControlRangeAfferent2.MotionElement0.PostAfferent24.LTMembrane, EngineControlRangeAfferent2.MotionElement0.LTMembrane (и еще 35)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent2.MotionElement0.Motoneuron1.PNeuronNegCGenerator, EngineControlRangeAfferent2.MotionElement0.Motoneuron2.PNeuronNegCGenerator, EngineControlRangeAfferent2.MotionElement0.PostAfferent14.PNeuronNegCGenerator, EngineControlRangeAfferent2.MotionElement0.PostAfferent24.PNeuronNegCGenerator, EngineControlRangeAfferent2.MotionElement0.PNeuronNegCGenerator (и еще 35)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent2.MotionElement0.Motoneuron1.PNeuronPosCGenerator, EngineControlRangeAfferent2.MotionElement0.Motoneuron2.PNeuronPosCGenerator, EngineControlRangeAfferent2.MotionElement0.PostAfferent14.PNeuronPosCGenerator, EngineControlRangeAfferent2.MotionElement0.PostAfferent24.PNeuronPosCGenerator, EngineControlRangeAfferent2.MotionElement0.PNeuronPosCGenerator (и еще 35)
- **NPSimpleLTZone**: EngineControlRangeAfferent2.MotionElement0.Afferent_II1.LTZone, EngineControlRangeAfferent2.MotionElement0.Afferent_II2.LTZone, EngineControlRangeAfferent2.MotionElement0.Afferent_Ia1.LTZone, EngineControlRangeAfferent2.MotionElement0.Afferent_Ia2.LTZone, EngineControlRangeAfferent2.MotionElement0.Afferent_Ib1.LTZone (и еще 51)
- **NPSynNeuronChannel**: EngineControlRangeAfferent2.MotionElement0.Motoneuron1.LTMembrane.PosChannel, EngineControlRangeAfferent2.MotionElement0.Motoneuron1.LTMembrane.NegChannel, EngineControlRangeAfferent2.MotionElement0.Motoneuron1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent2.MotionElement0.Motoneuron1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent2.MotionElement0.Motoneuron1.PNeuronMembrane2.PosChannel (и еще 331)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent2.MotionElement0.Motoneuron1.PNeuronMembrane, EngineControlRangeAfferent2.MotionElement0.Motoneuron1.PNeuronMembrane2, EngineControlRangeAfferent2.MotionElement0.Motoneuron1.PNeuronMembrane3, EngineControlRangeAfferent2.MotionElement0.Motoneuron2.PNeuronMembrane, EngineControlRangeAfferent2.MotionElement0.Motoneuron2.PNeuronMembrane2 (и еще 83)
- **NPac**: EngineControlRangeAfferent2.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent2.MotionElement0.Afferent_II1.Receptor, EngineControlRangeAfferent2.MotionElement0.Afferent_II2.Receptor, EngineControlRangeAfferent2.MotionElement0.Afferent_Ia1.Receptor, EngineControlRangeAfferent2.MotionElement0.Afferent_Ia2.Receptor, EngineControlRangeAfferent2.MotionElement0.Afferent_Ib1.Receptor (и еще 51)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent2.MotionElement0.Afferent_II1, EngineControlRangeAfferent2.MotionElement0.Afferent_II2, EngineControlRangeAfferent2.MotionElement0.Afferent_Ia1, EngineControlRangeAfferent2.MotionElement0.Afferent_Ia2, EngineControlRangeAfferent2.MotionElement0.Afferent_Ib1 (и еще 43)

**Входы системы:**
- `AfferentSource1`
- `CGenerator`
- `EngineControlRangeAfferent2.AfferentSource1`
- `EngineControlRangeAfferent2.IINegAfferentGenerator`
- `EngineControlRangeAfferent2.IIPosAfferentGenerator`
- `EngineControlRangeAfferent2.II_NegIntervalSeparator1.DataInput0`
- `EngineControlRangeAfferent2.II_NegIntervalSeparator2.DataInput0`
- `EngineControlRangeAfferent2.II_NegIntervalSeparator3.DataInput0`
- `EngineControlRangeAfferent2.II_PosIntervalSeparator1.DataInput0`
- `EngineControlRangeAfferent2.II_PosIntervalSeparator2.DataInput0`
- ... (всего 333 входов)

**Выходы системы:**
- `EngineControlRangeAfferent2.II_NegIntervalSeparator1.DataOutput0`
- `EngineControlRangeAfferent2.II_NegIntervalSeparator2.DataOutput0`
- `EngineControlRangeAfferent2.II_NegIntervalSeparator3.DataOutput0`
- `EngineControlRangeAfferent2.II_PosIntervalSeparator1.DataOutput0`
- `EngineControlRangeAfferent2.II_PosIntervalSeparator2.DataOutput0`
- `EngineControlRangeAfferent2.II_PosIntervalSeparator3.DataOutput0`
- `EngineControlRangeAfferent2.Ia_NegIntervalSeparator1.DataOutput0`
- `EngineControlRangeAfferent2.Ia_NegIntervalSeparator2.DataOutput0`
- `EngineControlRangeAfferent2.Ia_NegIntervalSeparator3.DataOutput0`
- `EngineControlRangeAfferent2.Ia_PosIntervalSeparator1.DataOutput0`
- ... (всего 165 выходов)

**Количество связей:** 246

---

### Pendulum5

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\Pendulum5`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Количество каналов:** 0

**Основные компоненты:**
- **NAsfNewSimplestAfferentBranchedEngineControl5**: EngineControlRangeAfferent
- **NAsfNewSimplestAfferentBranchedMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent.MotionElement1, EngineControlRangeAfferent.MotionElement2, EngineControlRangeAfferent.MotionElement3, EngineControlRangeAfferent.MotionElement4 (и еще 5)
- **NCGenerator**: CGenerator, EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NIntervalSeparator**: EngineControlRangeAfferent.Ib_NegIntervalSeparator1, EngineControlRangeAfferent.Ib_NegIntervalSeparator2, EngineControlRangeAfferent.Ib_NegIntervalSeparator3, EngineControlRangeAfferent.Ib_NegIntervalSeparator4, EngineControlRangeAfferent.Ib_NegIntervalSeparator5 (и еще 55)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NManipulatorSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.Motoneuron1, EngineControlRangeAfferent.MotionElement0.Motoneuron2, EngineControlRangeAfferent.MotionElement0.PostAfferent14, EngineControlRangeAfferent.MotionElement0.PostAfferent24, EngineControlRangeAfferent.MotionElement1.Motoneuron1 (и еще 43)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, IIPosAfferentGenerator, IINegAfferentGenerator
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTZone, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTZone, EngineControlRangeAfferent.MotionElement1.Motoneuron1.LTZone (и еще 43)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTMembrane, EngineControlRangeAfferent.MotionElement0.LTMembrane (и еще 55)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 55)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 55)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_II2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.LTZone (и еще 79)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2.PosChannel (и еще 643)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane3, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane4, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane5 (и еще 199)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_II2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.Receptor (и еще 79)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.Afferent_II1, EngineControlRangeAfferent.MotionElement0.Afferent_II2, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1 (и еще 67)

**Входы системы:**
- `AfferentSource1`
- `CGenerator`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator`
- ... (всего 127 входов)

**Количество связей:** 507

---

### RCN test

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\RCN test`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfNewSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator21, EngineControlRangeAfferent.PosIntervalSeparator21, NegIntervalSeparator11 (и еще 3)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent.MotionElement1, MotionElement0, MotionElement1
- **NNewSynSPNeuron**: NPCN.InputNeuronL11, NPCN.InputNeuronR11, NPCN.ControlNeuronL11, NPCN.ControlNeuronR11, NPCN.InputNeuronL21 (и еще 11)
- **NPCN**: NPCN
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, NPCN.NPGeneratorL11, NPCN.NPGeneratorR11 (и еще 9)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.LTZone (и еще 42)
- **NPLTZoneSynNeuronMembrane**: NPCN.InputNeuronL11.LTMembrane, NPCN.InputNeuronR11.LTMembrane, NPCN.ControlNeuronL11.LTMembrane, NPCN.ControlNeuronR11.LTMembrane, NPCN.InputNeuronL21.LTMembrane (и еще 13)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 42)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 42)
- **NPNewSynNeuronMembrane**: NPCN.InputNeuronL11.PNeuronMembrane, NPCN.InputNeuronR11.PNeuronMembrane, NPCN.ControlNeuronL11.PNeuronMembrane, NPCN.ControlNeuronR11.PNeuronMembrane, NPCN.InputNeuronL21.PNeuronMembrane (и еще 13)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement1.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement1.AfferentL1.LTZone, EngineControlRangeAfferent.AfferentR1.LTZone (и еще 7)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane.PosChannel (и еще 219)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PNeuronMembrane (и еще 24)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.MotionElement1.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement1.AfferentL1.Receptor (и еще 13)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement1.AfferentR1, EngineControlRangeAfferent.MotionElement1.AfferentL1, EngineControlRangeAfferent.AfferentR1 (и еще 7)
- **NSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotionElement1.MotoneuronL (и еще 19)

**Входы системы:**
- `AfferentSource1`
- `ControlNeuronL11.PNeuronNegCGenerator`
- `ControlNeuronL11.PNeuronPosCGenerator`
- `ControlNeuronL21.PNeuronNegCGenerator`
- `ControlNeuronL21.PNeuronPosCGenerator`
- `ControlNeuronR11.PNeuronNegCGenerator`
- `ControlNeuronR11.PNeuronPosCGenerator`
- `ControlNeuronR21.PNeuronNegCGenerator`
- `ControlNeuronR21.PNeuronPosCGenerator`
- `DCEngine.DataInput0`
- ... (всего 251 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel.DataOutput0`
- ... (всего 119 выходов)

**Количество связей:** 177

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### RCN+PCN+PCN2

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\RCN+PCN+PCN2`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfNewSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent, EngineControlRangeAfferent2
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, EngineControlRangeAfferent2.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, EngineControlRangeAfferent2.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine, DCEngine2
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator21, EngineControlRangeAfferent.PosIntervalSeparator21, EngineControlRangeAfferent.NegIntervalSeparator31 (и еще 13)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, EngineControlRangeAfferent2.NManipulatorInput1, NManipulatorInput1
- **NMultiPositionControl**: NMultiPositionControl
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent.MotionElement1, EngineControlRangeAfferent.MotionElement2, EngineControlRangeAfferent2.MotionElement0, EngineControlRangeAfferent2.MotionElement1 (и еще 4)
- **NNewPositionControlElement**: NNewPositionControlElement, NNewPositionControlElement2
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotionElement1.MotoneuronL (и еще 163)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, NNewPositionControlElement.NPGeneratorL11, NNewPositionControlElement.NPGeneratorR11, NNewPositionControlElement.NPGeneratorL21 (и еще 19)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.LTZone (и еще 178)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTMembrane, EngineControlRangeAfferent.MotionElement0.LTMembrane (и еще 178)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 178)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 178)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement1.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement1.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement2.AfferentR1.LTZone (и еще 19)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel (и еще 1171)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PNeuronMembrane (и еще 217)
- **NPac**: EngineControlRangeAfferent.Pac, EngineControlRangeAfferent2.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.MotionElement1.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement1.AfferentL1.Receptor (и еще 31)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement1.AfferentR1, EngineControlRangeAfferent.MotionElement1.AfferentL1, EngineControlRangeAfferent.MotionElement2.AfferentR1 (и еще 19)
- **NWPhysicalManipulator**: WPhysicalManipulator

**Входы системы:**
- `AfferentSource1`
- `ControlNeuron1-1.PNeuronNegCGenerator`
- `ControlNeuron1-1.PNeuronPosCGenerator`
- `ControlNeuron1-2.PNeuronNegCGenerator`
- `ControlNeuron1-2.PNeuronPosCGenerator`
- `ControlNeuron1-3.PNeuronNegCGenerator`
- `ControlNeuron1-3.PNeuronPosCGenerator`
- `ControlNeuron1-4.PNeuronNegCGenerator`
- `ControlNeuron1-4.PNeuronPosCGenerator`
- `ControlNeuron1-5.PNeuronNegCGenerator`
- ... (всего 1436 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel.DataOutput0`
- ... (всего 779 выходов)

**Количество связей:** 1048

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### RCN+PCN+TCN

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\RCN+PCN+TCN`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfNewSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, NegIntervalSeparator11, PosIntervalSeparator11
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotoneuronL (и еще 11)
- **NPCN**: NPCN
- **NPGenerator**: PGenerator, PGenerator3, PGenerator2, EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator (и еще 2)
- **NPLTZone**: TCNNeuron3.LTZone, TCNNeuron4.LTZone, TCNNeuron.LTZone, TCNNeuron2.LTZone, TCNNeuron5.LTZone (и еще 21)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTMembrane, EngineControlRangeAfferent.MotionElement0.LTMembrane (и еще 15)
- **NPNeuronNegCGenerator**: TCNNeuron3.PNeuronNegCGenerator, TCNNeuron4.PNeuronNegCGenerator, TCNNeuron.PNeuronNegCGenerator, TCNNeuron2.PNeuronNegCGenerator, TCNNeuron5.PNeuronNegCGenerator (и еще 21)
- **NPNeuronPosCGenerator**: TCNNeuron3.PNeuronPosCGenerator, TCNNeuron4.PNeuronPosCGenerator, TCNNeuron.PNeuronPosCGenerator, TCNNeuron2.PNeuronPosCGenerator, TCNNeuron5.PNeuronPosCGenerator (и еще 21)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.AfferentR1.LTZone, EngineControlRangeAfferent.AfferentL1.LTZone, MotionElement0.AfferentR1.LTZone (и еще 3)
- **NPSynNeuronChannel**: TCNNeuron3.PNeuronMembrane.PosChannel, TCNNeuron3.PNeuronMembrane.NegChannel, TCNNeuron3.PNeuronMembrane2.PosChannel, TCNNeuron3.PNeuronMembrane2.NegChannel, TCNNeuron3.PNeuronMembrane3.PosChannel (и еще 223)
- **NPSynNeuronMembrane**: TCNNeuron3.PNeuronMembrane, TCNNeuron3.PNeuronMembrane2, TCNNeuron3.PNeuronMembrane3, TCNNeuron3.PNeuronMembrane4, TCNNeuron3.PNeuronMembrane5 (и еще 63)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.AfferentR1.Receptor, EngineControlRangeAfferent.AfferentL1.Receptor (и еще 7)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.AfferentR1, EngineControlRangeAfferent.AfferentL1, MotionElement0.AfferentR1 (и еще 3)
- **NSynTCNNeuron**: TCNNeuron3, TCNNeuron4, TCNNeuron, TCNNeuron2, TCNNeuron5 (и еще 1)
- **NWPhysicalManipulator**: WPhysicalManipulator

**Входы системы:**
- `AfferentSource1`
- `DCEngine.DataInput0`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataInput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.DataInput0`
- ... (всего 280 входов)

**Выходы системы:**
- `DCEngine.DataOutput0`
- `DCEngine.DataOutput1`
- `DCEngine.DataOutput2`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel.DataOutput0`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone.DataOutput0`
- ... (всего 145 выходов)

**Количество связей:** 220

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### SimpleRCNworkingExample

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\SimpleRCNworkingExample`

**Назначение:** Рефлекторная цепь нейронов (RCN - Reflex Chain of Neurons)

**Основные компоненты:**
- **N2AsfNewSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, NegIntervalSeparator11, PosIntervalSeparator11
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NNewSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotoneuronL, EngineControlRangeAfferent.MotoneuronR, MotionElement0.MotoneuronL (и еще 3)
- **NPExcChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.Soma1.ExcChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.ExcChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.Soma1.ExcChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.ExcChannel, EngineControlRangeAfferent.MotionElement0.Soma1.ExcChannel (и еще 19)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, EngineControlRangeAfferent.InternalGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.PGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PGenerator (и еще 25)
- **NPInhChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.Soma1.InhChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.InhChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.Soma1.InhChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.InhChannel, EngineControlRangeAfferent.MotionElement0.Soma1.InhChannel (и еще 19)
- **NPLTExcChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.ExcChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTMembrane.ExcChannel, EngineControlRangeAfferent.MotionElement0.LTMembrane.ExcChannel, EngineControlRangeAfferent.MotoneuronL.LTMembrane.ExcChannel, EngineControlRangeAfferent.MotoneuronR.LTMembrane.ExcChannel (и еще 7)
- **NPLTInhChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.InhChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTMembrane.InhChannel, EngineControlRangeAfferent.MotionElement0.LTMembrane.InhChannel, EngineControlRangeAfferent.MotoneuronL.LTMembrane.InhChannel, EngineControlRangeAfferent.MotoneuronR.LTMembrane.InhChannel (и еще 7)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotoneuronL.LTZone, EngineControlRangeAfferent.MotoneuronR.LTZone, MotionElement0.MotoneuronL.LTZone (и еще 3)
- **NPLTZoneNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTMembrane, EngineControlRangeAfferent.MotionElement0.LTMembrane, EngineControlRangeAfferent.MotoneuronL.LTMembrane, EngineControlRangeAfferent.MotoneuronR.LTMembrane (и еще 7)
- **NPMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.Soma1, EngineControlRangeAfferent.MotionElement0.MotoneuronR.Soma1, EngineControlRangeAfferent.MotionElement0.Soma1, EngineControlRangeAfferent.MotoneuronL.Soma1, EngineControlRangeAfferent.MotoneuronR.Soma1 (и еще 7)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.NegGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.NegGenerator, EngineControlRangeAfferent.MotionElement0.NegGenerator, EngineControlRangeAfferent.MotoneuronL.NegGenerator, EngineControlRangeAfferent.MotoneuronR.NegGenerator (и еще 7)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PosGenerator, EngineControlRangeAfferent.MotionElement0.PosGenerator, EngineControlRangeAfferent.MotoneuronL.PosGenerator, EngineControlRangeAfferent.MotoneuronR.PosGenerator (и еще 7)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.LTZone, EngineControlRangeAfferent.AfferentR1.LTZone, EngineControlRangeAfferent.AfferentL1.LTZone (и еще 7)
- **NPSynapse**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.ExcSynapse1, EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.InhSynapse1, EngineControlRangeAfferent.MotionElement0.MotoneuronL.Soma1.ExcSynapse1, EngineControlRangeAfferent.MotionElement0.MotoneuronL.Soma1.InhSynapse1, EngineControlRangeAfferent.MotionElement0.MotoneuronL.ExcSynapse1 (и еще 67)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.AfferentR1.Receptor, EngineControlRangeAfferent.AfferentL1.Receptor (и еще 7)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.AfferentR1, EngineControlRangeAfferent.AfferentL1, MotionElement0.AfferentR1 (и еще 3)
- **NWPhysicalManipulator**: WPhysicalManipulator
- **UStatisticDoubleMatrix**: EngineControlRangeAfferent.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentL1.LTZone.PGenerator`
- `AfferentL1.PGenerator`
- `AfferentR1.LTZone.PGenerator`
- `AfferentR1.PGenerator`
- `AfferentSource1`
- `DCEngine.InputVoltage`
- `EngineControlRangeAfferent.AfferentL1.LTZone.PGenerator`
- `EngineControlRangeAfferent.AfferentL1.PGenerator`
- `EngineControlRangeAfferent.AfferentR1.LTZone.PGenerator`
- `EngineControlRangeAfferent.AfferentR1.PGenerator`
- ... (всего 91 входов)

**Выходы системы:**
- `DCEngine.OutputAngle`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone.Output`
- `EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor.Output`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone.Output`
- `EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor.Output`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.ExcChannel.Output`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.ExcSynapse1.Output`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.InhChannel.Output`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.InhSynapse1.Output`
- `EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone.Output`
- ... (всего 32 выходов)

**Количество связей:** 38

**Связанные публикации:**
- [Моделирование процессов преобразования импульсных потоков в нейронных структурах управления мышечным сокращением](https://www.elibrary.ru/item.asp?id=13070251) - Публикация 3: А. В. Бахшиев, С.П. Романов

---

### SimplestMiotionControl2

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\SimplestMiotionControl2`

**Назначение:** Система управления движением

**Количество каналов:** 0

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### SimplestMotionControlSAfferent

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\SimplestMotionControlSAfferent`

**Назначение:** Система управления движением

**Название проекта:** NoName

**Количество каналов:** 0

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### SimplestMotionControlSAfferent10

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\SimplestMotionControlSAfferent10`

**Назначение:** Система управления движением

**Название проекта:** NoName

**Количество каналов:** 0

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### SimplestMotionControlSAfferent10_N

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\SimplestMotionControlSAfferent10_N`

**Назначение:** Система управления движением

**Название проекта:** NoName

**Количество каналов:** 0

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### SimplestMotionControlSAfferent3_N

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\SimplestMotionControlSAfferent3_N`

**Назначение:** Система управления движением

**Количество каналов:** 0

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### SimplestMotionControlSAfferent5

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\SimplestMotionControlSAfferent5`

**Назначение:** Система управления движением

**Название проекта:** NoName

**Количество каналов:** 0

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### SimplestMotionControlSAfferent5_N

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\SimplestMotionControlSAfferent5_N`

**Назначение:** Система управления движением

**Название проекта:** NoName

**Количество каналов:** 0

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### SimplestMotionControlSAfferent_N

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\SimplestMotionControlSAfferent_N`

**Назначение:** Система управления движением

**Название проекта:** NoName

**Количество каналов:** 0

**Основные компоненты:**
- **NAsfNewSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NAsfNewSimplestAfferentBranchedMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.Ib_NegIntervalSeparator1, EngineControlRangeAfferent.Ib_PosIntervalSeparator1, EngineControlRangeAfferent.II_NegIntervalSeparator1, EngineControlRangeAfferent.II_PosIntervalSeparator1, EngineControlRangeAfferent.Ia_NegIntervalSeparator1 (и еще 7)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NManipulatorSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.Motoneuron1, EngineControlRangeAfferent.MotionElement0.Motoneuron2, EngineControlRangeAfferent.MotionElement0.PostAfferent14, EngineControlRangeAfferent.MotionElement0.PostAfferent24, EngineControlRangeAfferent.Motoneuron1 (и еще 11)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, IIPosAfferentGenerator, IINegAfferentGenerator
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTZone, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTZone, EngineControlRangeAfferent.Motoneuron1.LTZone (и еще 11)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTMembrane, EngineControlRangeAfferent.MotionElement0.LTMembrane (и еще 15)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 15)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 15)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_II2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.LTZone (и еще 23)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2.PosChannel (и еще 211)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane3, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane4, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane5 (и еще 63)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_II2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.Receptor (и еще 23)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.Afferent_II1, EngineControlRangeAfferent.MotionElement0.Afferent_II2, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1 (и еще 19)
- **NWPhysicalManipulator**: WPhysicalManipulator

**Входы системы:**
- `AfferentSource1`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator`
- ... (всего 46 входов)

**Количество связей:** 113

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### TCN test

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\TCN test`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Количество каналов:** 0

**Основные компоненты:**
- **NPGenerator**: PGenerator3, PGenerator4
- **NPLTZone**: TCNNeuron3.LTZone, LTZone
- **NPNeuronNegCGenerator**: TCNNeuron3.PNeuronNegCGenerator, PNeuronNegCGenerator
- **NPNeuronPosCGenerator**: TCNNeuron3.PNeuronPosCGenerator, PNeuronPosCGenerator
- **NPSynNeuronChannel**: TCNNeuron3.PNeuronMembrane.PosChannel, TCNNeuron3.PNeuronMembrane.NegChannel, TCNNeuron3.PNeuronMembrane2.PosChannel, TCNNeuron3.PNeuronMembrane2.NegChannel, TCNNeuron3.PNeuronMembrane3.PosChannel (и еще 27)
- **NPSynNeuronMembrane**: TCNNeuron3.PNeuronMembrane, TCNNeuron3.PNeuronMembrane2, TCNNeuron3.PNeuronMembrane3, TCNNeuron3.PNeuronMembrane4, TCNNeuron3.PNeuronMembrane5 (и еще 9)
- **NSynTCNNeuron**: TCNNeuron3

**Входы системы:**
- `PGenerator3`
- `PGenerator4`
- `PNeuronNegCGenerator`
- `PNeuronPosCGenerator`
- `TCNNeuron3.LTZone.DataInput0`
- `TCNNeuron3.LTZone.DataInput1`
- `TCNNeuron3.LTZone.DataInput2`
- `TCNNeuron3.LTZone.DataInput3`
- `TCNNeuron3.LTZone.DataInput4`
- `TCNNeuron3.LTZone.DataInput5`
- ... (всего 32 входов)

**Выходы системы:**
- `PGenerator3.DataOutput0`
- `PGenerator4.DataOutput0`
- `TCNNeuron3.LTZone.DataOutput0`
- `TCNNeuron3.PNeuronMembrane.NegChannel.DataOutput0`
- `TCNNeuron3.PNeuronMembrane.PosChannel.DataOutput0`
- `TCNNeuron3.PNeuronMembrane2.NegChannel.DataOutput0`
- `TCNNeuron3.PNeuronMembrane2.PosChannel.DataOutput0`
- `TCNNeuron3.PNeuronMembrane3.NegChannel.DataOutput0`
- `TCNNeuron3.PNeuronMembrane3.PosChannel.DataOutput0`
- `TCNNeuron3.PNeuronMembrane4.NegChannel.DataOutput0`
- ... (всего 19 выходов)

**Количество связей:** 29

---

## OnlineTest

### CvTest

**Путь:** `Bin\Configs\!OldConfigs\OnlineTest\CvTest`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

---

## PositionControl

### AsfMotionControl

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\PositionControl\AsfMotionControl`

**Назначение:** Система управления движением

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfNewSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: CGenerator, EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, EngineControlRangeAfferent.NegIntervalSeparator13 (и еще 7)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NManipulatorSource**: EngineControlRangeAfferent.NManipulatorSource1, EngineControlRangeAfferent.NManipulatorSource12, NManipulatorSource1, NManipulatorSource12
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotionElement0.PostAfferentL2 (и еще 51)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, NPositionControlElement.NPGeneratorL11, NPositionControlElement.NPGeneratorR11, NPositionControlElement.NPGeneratorL12 (и еще 11)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTZone (и еще 56)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTMembrane (и еще 56)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronNegCGenerator (и еще 56)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronPosCGenerator (и еще 56)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR3.LTZone (и еще 19)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel (и еще 361)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronMembrane (и еще 56)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NPositionControlElement**: NPositionControlElement
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR3.Receptor (и еще 23)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.MotionElement0.AfferentR3 (и еще 19)
- **NWPhysicalManipulator**: WPhysicalManipulator

**Входы системы:**
- `AfferentSource1`
- `CGenerator`
- `ControlNeuronL11.PNeuronNegCGenerator`
- `ControlNeuronL11.PNeuronPosCGenerator`
- `ControlNeuronL12.PNeuronNegCGenerator`
- `ControlNeuronL12.PNeuronPosCGenerator`
- `ControlNeuronL13.PNeuronNegCGenerator`
- `ControlNeuronL13.PNeuronPosCGenerator`
- `ControlNeuronR11.PNeuronNegCGenerator`
- `ControlNeuronR11.PNeuronPosCGenerator`
- ... (всего 141 входов)

**Количество связей:** 214

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### AsfMotionControl-2Engines

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\PositionControl\AsfMotionControl-2Engines`

**Назначение:** Система управления движением

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfNewSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent, EngineControlRangeAfferent2
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, EngineControlRangeAfferent2.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, EngineControlRangeAfferent2.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine, DCEngine2
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent2.NegIntervalSeparator11, EngineControlRangeAfferent2.PosIntervalSeparator11, NegIntervalSeparator11 (и еще 1)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, EngineControlRangeAfferent2.NManipulatorInput1, NManipulatorInput1
- **NMultiPositionControl**: NMultiPositionControl
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent2.MotionElement0, MotionElement0
- **NNewPositionControlElement**: NNewPositionControlElement, NNewPositionControlElement2
- **NNewSynSPNeuron**: NMultiPositionControl.InputNeuron1-1, NMultiPositionControl.InputNeuron1-2, NMultiPositionControl.InputNeuron2-1, NMultiPositionControl.InputNeuron2-2, NMultiPositionControl.ControlNeuron1-1 (и еще 91)
- **NPGenerator**: NMultiPositionControl.PGenerator, NMultiPositionControl.PGenerator2, NMultiPositionControl.PGenerator3, NMultiPositionControl.PGenerator4, NMultiPositionControl.PGenerator5 (и еще 23)
- **NPLTZone**: NMultiPositionControl.InputNeuron1-1.LTZone, NMultiPositionControl.InputNeuron1-2.LTZone, NMultiPositionControl.InputNeuron2-1.LTZone, NMultiPositionControl.InputNeuron2-2.LTZone, NMultiPositionControl.ControlNeuron1-1.LTZone (и еще 100)
- **NPLTZoneSynNeuronMembrane**: NMultiPositionControl.InputNeuron1-1.LTMembrane, NMultiPositionControl.InputNeuron1-2.LTMembrane, NMultiPositionControl.InputNeuron2-1.LTMembrane, NMultiPositionControl.InputNeuron2-2.LTMembrane, NMultiPositionControl.ControlNeuron1-1.LTMembrane (и еще 100)
- **NPNeuronNegCGenerator**: NMultiPositionControl.InputNeuron1-1.PNeuronNegCGenerator, NMultiPositionControl.InputNeuron1-2.PNeuronNegCGenerator, NMultiPositionControl.InputNeuron2-1.PNeuronNegCGenerator, NMultiPositionControl.InputNeuron2-2.PNeuronNegCGenerator, NMultiPositionControl.ControlNeuron1-1.PNeuronNegCGenerator (и еще 100)
- **NPNeuronPosCGenerator**: NMultiPositionControl.InputNeuron1-1.PNeuronPosCGenerator, NMultiPositionControl.InputNeuron1-2.PNeuronPosCGenerator, NMultiPositionControl.InputNeuron2-1.PNeuronPosCGenerator, NMultiPositionControl.InputNeuron2-2.PNeuronPosCGenerator, NMultiPositionControl.ControlNeuron1-1.PNeuronPosCGenerator (и еще 100)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.AfferentR1.LTZone, EngineControlRangeAfferent.AfferentL1.LTZone, EngineControlRangeAfferent2.MotionElement0.AfferentR1.LTZone (и еще 7)
- **NPSynNeuronChannel**: NMultiPositionControl.InputNeuron1-1.LTMembrane.PosChannel, NMultiPositionControl.InputNeuron1-1.LTMembrane.NegChannel, NMultiPositionControl.InputNeuron1-1.PNeuronMembrane.PosChannel, NMultiPositionControl.InputNeuron1-1.PNeuronMembrane.NegChannel, NMultiPositionControl.InputNeuron1-1.PosChannel (и еще 681)
- **NPSynNeuronMembrane**: NMultiPositionControl.InputNeuron1-1.PNeuronMembrane, NMultiPositionControl.InputNeuron1-2.PNeuronMembrane, NMultiPositionControl.InputNeuron2-1.PNeuronMembrane, NMultiPositionControl.InputNeuron2-2.PNeuronMembrane, NMultiPositionControl.ControlNeuron1-1.PNeuronMembrane (и еще 128)
- **NPac**: EngineControlRangeAfferent.Pac, EngineControlRangeAfferent2.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.AfferentR1.Receptor, EngineControlRangeAfferent.AfferentL1.Receptor (и еще 13)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.AfferentR1, EngineControlRangeAfferent.AfferentL1, EngineControlRangeAfferent2.MotionElement0.AfferentR1 (и еще 7)
- **NWPhysicalManipulator**: WPhysicalManipulator

**Входы системы:**
- `AfferentSource1`
- `ControlNeuron1-1.PNeuronNegCGenerator`
- `ControlNeuron1-1.PNeuronPosCGenerator`
- `ControlNeuron1-2.PNeuronNegCGenerator`
- `ControlNeuron1-2.PNeuronPosCGenerator`
- `ControlNeuron2-1.PNeuronNegCGenerator`
- `ControlNeuron2-1.PNeuronPosCGenerator`
- `ControlNeuron2-2.PNeuronNegCGenerator`
- `ControlNeuron2-2.PNeuronPosCGenerator`
- `ControlNeuronL11.PNeuronNegCGenerator`
- ... (всего 241 входов)

**Количество связей:** 521

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### AsfMotionControl-2Engines - Continues

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\PositionControl\AsfMotionControl-2Engines - Continues`

**Назначение:** Система управления движением

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfNewSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent, EngineControlRangeAfferent2
- **NCGenerator**: EngineControlRangeAfferent.AfferentSource1, EngineControlRangeAfferent2.AfferentSource1, AfferentSource1
- **NCLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone (и еще 36)
- **NCNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator (и еще 36)
- **NCNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator (и еще 36)
- **NCSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane.PosChannel (и еще 159)
- **NCSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.AfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane (и еще 36)
- **NContinuesSAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.AfferentR1, EngineControlRangeAfferent.AfferentL1, EngineControlRangeAfferent2.MotionElement0.AfferentR1 (и еще 7)
- **NContinuesSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotoneuronL (и еще 19)
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1, EngineControlRangeAfferent2.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine, DCEngine2
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent2.NegIntervalSeparator11, EngineControlRangeAfferent2.PosIntervalSeparator11, NegIntervalSeparator11 (и еще 1)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, EngineControlRangeAfferent2.NManipulatorInput1, NManipulatorInput1
- **NMultiPositionControl**: NMultiPositionControl
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent2.MotionElement0, MotionElement0
- **NNewPositionControlElement**: NNewPositionControlElement, NNewPositionControlElement2
- **NNewSynSPNeuron**: NMultiPositionControl.InputNeuron1-1, NMultiPositionControl.InputNeuron1-2, NMultiPositionControl.InputNeuron2-1, NMultiPositionControl.InputNeuron2-2, NMultiPositionControl.ControlNeuron1-1 (и еще 83)
- **NPGenerator**: NMultiPositionControl.PGenerator, NMultiPositionControl.PGenerator2, NMultiPositionControl.PGenerator3, NMultiPositionControl.PGenerator4, NMultiPositionControl.PGenerator5 (и еще 23)
- **NPLTZone**: NMultiPositionControl.InputNeuron1-1.LTZone, NMultiPositionControl.InputNeuron1-2.LTZone, NMultiPositionControl.InputNeuron2-1.LTZone, NMultiPositionControl.InputNeuron2-2.LTZone, NMultiPositionControl.ControlNeuron1-1.LTZone (и еще 87)
- **NPLTZoneSynNeuronMembrane**: NMultiPositionControl.InputNeuron1-1.LTMembrane, NMultiPositionControl.InputNeuron1-2.LTMembrane, NMultiPositionControl.InputNeuron2-1.LTMembrane, NMultiPositionControl.InputNeuron2-2.LTMembrane, NMultiPositionControl.ControlNeuron1-1.LTMembrane (и еще 87)
- **NPNeuronNegCGenerator**: NMultiPositionControl.InputNeuron1-1.PNeuronNegCGenerator, NMultiPositionControl.InputNeuron1-2.PNeuronNegCGenerator, NMultiPositionControl.InputNeuron2-1.PNeuronNegCGenerator, NMultiPositionControl.InputNeuron2-2.PNeuronNegCGenerator, NMultiPositionControl.ControlNeuron1-1.PNeuronNegCGenerator (и еще 87)
- **NPNeuronPosCGenerator**: NMultiPositionControl.InputNeuron1-1.PNeuronPosCGenerator, NMultiPositionControl.InputNeuron1-2.PNeuronPosCGenerator, NMultiPositionControl.InputNeuron2-1.PNeuronPosCGenerator, NMultiPositionControl.InputNeuron2-2.PNeuronPosCGenerator, NMultiPositionControl.ControlNeuron1-1.PNeuronPosCGenerator (и еще 87)
- **NPSynNeuronChannel**: NMultiPositionControl.InputNeuron1-1.LTMembrane.PosChannel, NMultiPositionControl.InputNeuron1-1.LTMembrane.NegChannel, NMultiPositionControl.InputNeuron1-1.PNeuronMembrane.PosChannel, NMultiPositionControl.InputNeuron1-1.PNeuronMembrane.NegChannel, NMultiPositionControl.InputNeuron1-1.PosChannel (и еще 603)
- **NPSynNeuronMembrane**: NMultiPositionControl.InputNeuron1-1.PNeuronMembrane, NMultiPositionControl.InputNeuron1-2.PNeuronMembrane, NMultiPositionControl.InputNeuron2-1.PNeuronMembrane, NMultiPositionControl.InputNeuron2-2.PNeuronMembrane, NMultiPositionControl.ControlNeuron1-1.PNeuronMembrane (и еще 115)
- **NPac**: EngineControlRangeAfferent.Pac, EngineControlRangeAfferent2.Pac, Pac
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor, EngineControlRangeAfferent.AfferentR1.Receptor, EngineControlRangeAfferent.AfferentL1.Receptor (и еще 13)
- **NWPhysicalManipulator**: WPhysicalManipulator

**Входы системы:**
- `AfferentL1.PNeuronNegCGenerator`
- `AfferentL1.PNeuronPosCGenerator`
- `AfferentR1.PNeuronNegCGenerator`
- `AfferentR1.PNeuronPosCGenerator`
- `AfferentSource1`
- `ControlNeuron1-1.PNeuronNegCGenerator`
- `ControlNeuron1-1.PNeuronPosCGenerator`
- `ControlNeuron1-2.PNeuronNegCGenerator`
- `ControlNeuron1-2.PNeuronPosCGenerator`
- `ControlNeuron1-3.PNeuronNegCGenerator`
- ... (всего 297 входов)

**Количество связей:** 601

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### AsfMotionControl-LargeNeurons-NormalWeight

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\PositionControl\AsfMotionControl-LargeNeurons-NormalWeight`

**Назначение:** Модель LIF нейрона

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfNewSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent, EngineControlRangeAfferent2
- **NCGenerator**: CGenerator, EngineControlRangeAfferent.AfferentSource1, EngineControlRangeAfferent2.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineControlRangeAfferent.NManipulatorSource1
- **NDCEngine**: DCEngine, DCEngine2
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, EngineControlRangeAfferent.NegIntervalSeparator21 (и еще 21)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, EngineControlRangeAfferent2.NManipulatorInput1, NManipulatorInput1
- **NManipulatorSource**: EngineControlRangeAfferent2.NManipulatorSource1, NManipulatorSource1
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent.MotionElement1, EngineControlRangeAfferent.MotionElement2, EngineControlRangeAfferent2.MotionElement0, MotionElement0 (и еще 2)
- **NNewPositionControlElement**: NNewPositionControlElement
- **NNewSynLPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotionElement0.PostAfferentL2 (и еще 39)
- **NNewSynSPNeuron**: NNewPositionControlElement.InputNeuronL11, NNewPositionControlElement.InputNeuronR11, NNewPositionControlElement.ControlNeuronL11, NNewPositionControlElement.ControlNeuronR11, NNewPositionControlElement.PreControlNeuronL11 (и еще 99)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, NNewPositionControlElement.NPGeneratorL11, NNewPositionControlElement.NPGeneratorR11, NNewPositionControlElement.NPGeneratorL12 (и еще 25)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTZone (и еще 150)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTMembrane (и еще 154)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronNegCGenerator (и еще 154)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronPosCGenerator (и еще 154)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone, EngineControlRangeAfferent.MotionElement1.AfferentR1.LTZone (и еще 35)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2.PosChannel (и еще 1193)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane3, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane2 (и еще 276)
- **NPac**: EngineControlRangeAfferent.Pac, EngineControlRangeAfferent2.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.Receptor (и еще 41)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.MotionElement1.AfferentR1 (и еще 31)
- **NWPhysicalManipulator**: WPhysicalManipulator

**Входы системы:**
- `AfferentSource1`
- `CGenerator`
- `ControlNeuronL11.PNeuronNegCGenerator`
- `ControlNeuronL11.PNeuronPosCGenerator`
- `ControlNeuronL12.PNeuronNegCGenerator`
- `ControlNeuronL12.PNeuronPosCGenerator`
- `ControlNeuronL21.PNeuronNegCGenerator`
- `ControlNeuronL21.PNeuronPosCGenerator`
- `ControlNeuronL22.PNeuronNegCGenerator`
- `ControlNeuronL22.PNeuronPosCGenerator`
- ... (всего 352 входов)

**Количество связей:** 818

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### AsfMotionControl-LowWeight

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\PositionControl\AsfMotionControl-LowWeight`

**Назначение:** Система управления движением

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfNewSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: CGenerator, EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, EngineControlRangeAfferent.NegIntervalSeparator13 (и еще 7)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NManipulatorSource**: EngineControlRangeAfferent.NManipulatorSource1, EngineControlRangeAfferent.NManipulatorSource12, NManipulatorSource1, NManipulatorSource12
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotionElement0.PostAfferentL2 (и еще 51)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, NPositionControlElement.NPGeneratorL11, NPositionControlElement.NPGeneratorR11, NPositionControlElement.NPGeneratorL12 (и еще 11)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTZone (и еще 56)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTMembrane (и еще 56)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronNegCGenerator (и еще 56)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronPosCGenerator (и еще 56)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR3.LTZone (и еще 19)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel (и еще 361)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronMembrane (и еще 56)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NPositionControlElement**: NPositionControlElement
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR3.Receptor (и еще 23)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.MotionElement0.AfferentR3 (и еще 19)
- **NWPhysicalManipulator**: WPhysicalManipulator

**Входы системы:**
- `AfferentSource1`
- `CGenerator`
- `ControlNeuronL11.PNeuronNegCGenerator`
- `ControlNeuronL11.PNeuronPosCGenerator`
- `ControlNeuronL12.PNeuronNegCGenerator`
- `ControlNeuronL12.PNeuronPosCGenerator`
- `ControlNeuronL13.PNeuronNegCGenerator`
- `ControlNeuronL13.PNeuronPosCGenerator`
- `ControlNeuronR11.PNeuronNegCGenerator`
- `ControlNeuronR11.PNeuronPosCGenerator`
- ... (всего 141 входов)

**Количество связей:** 214

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### AsfMotionControl-NormalWeight

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\PositionControl\AsfMotionControl-NormalWeight`

**Назначение:** Система управления движением

**Количество каналов:** 0

**Основные компоненты:**
- **N2AsfNewSimplestAfferentBranchedEngineControl**: EngineControlRangeAfferent
- **NCGenerator**: CGenerator, EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.NegIntervalSeparator11, EngineControlRangeAfferent.PosIntervalSeparator11, EngineControlRangeAfferent.NegIntervalSeparator12, EngineControlRangeAfferent.PosIntervalSeparator12, EngineControlRangeAfferent.NegIntervalSeparator13 (и еще 7)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NManipulatorSource**: EngineControlRangeAfferent.NManipulatorSource1, EngineControlRangeAfferent.NManipulatorSource12, NManipulatorSource1, NManipulatorSource12
- **NNewMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.MotoneuronL, EngineControlRangeAfferent.MotionElement0.MotoneuronR, EngineControlRangeAfferent.MotionElement0.PostAfferentL1, EngineControlRangeAfferent.MotionElement0.PostAfferentR1, EngineControlRangeAfferent.MotionElement0.PostAfferentL2 (и еще 51)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, NPositionControlElement.NPGeneratorL11, NPositionControlElement.NPGeneratorR11, NPositionControlElement.NPGeneratorL12 (и еще 11)
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTZone, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTZone (и еще 56)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.LTMembrane (и еще 56)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronNegCGenerator (и еще 56)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronPosCGenerator (и еще 56)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.AfferentR1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL1.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentL2.LTZone, EngineControlRangeAfferent.MotionElement0.AfferentR3.LTZone (и еще 19)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.MotoneuronL.PosChannel (и еще 361)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.MotoneuronL.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.MotoneuronR.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentR1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferentL2.PNeuronMembrane (и еще 56)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NPositionControlElement**: NPositionControlElement
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.AfferentR1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL1.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentL2.Receptor, EngineControlRangeAfferent.MotionElement0.AfferentR3.Receptor (и еще 23)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.AfferentR1, EngineControlRangeAfferent.MotionElement0.AfferentL1, EngineControlRangeAfferent.MotionElement0.AfferentR2, EngineControlRangeAfferent.MotionElement0.AfferentL2, EngineControlRangeAfferent.MotionElement0.AfferentR3 (и еще 19)
- **NWPhysicalManipulator**: WPhysicalManipulator

**Входы системы:**
- `AfferentSource1`
- `CGenerator`
- `ControlNeuronL11.PNeuronNegCGenerator`
- `ControlNeuronL11.PNeuronPosCGenerator`
- `ControlNeuronL12.PNeuronNegCGenerator`
- `ControlNeuronL12.PNeuronPosCGenerator`
- `ControlNeuronL13.PNeuronNegCGenerator`
- `ControlNeuronL13.PNeuronPosCGenerator`
- `ControlNeuronR11.PNeuronNegCGenerator`
- `ControlNeuronR11.PNeuronPosCGenerator`
- ... (всего 141 входов)

**Количество связей:** 214

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

## Samples

### LIF-Neuron

**Путь:** `Bin\Configs\Samples\LIF-Neuron`

**Назначение:** Пример модели LIF (Leaky Integrate-and-Fire) нейрона для демонстрации базовой функциональности

**Основные компоненты:**
- **NPExcChannelBio**: PNeuron2.Soma1.ExcChannel, PNeuron2.ExcChannel, Soma1.ExcChannel, ExcChannel
- **NPGenerator**: PGenerator
- **NPInhChannelBio**: PNeuron2.Soma1.InhChannel, PNeuron2.InhChannel, Soma1.InhChannel, InhChannel
- **NPMembraneBio**: PNeuron2.Soma1, Soma1
- **NPNeuronNegCGeneratorBio**: PNeuron2.NegGenerator, NegGenerator
- **NPNeuronPosCGeneratorBio**: PNeuron2.PosGenerator, PosGenerator
- **NPNeuronPosCGeneratorCable**: CableNeuron2.NegGenerator
- **NPSynapseBio**: PNeuron2.Soma1.ExcSynapse1, PNeuron2.Soma1.InhSynapse1, PNeuron2.ExcSynapse1, PNeuron2.InhSynapse1, Soma1.ExcSynapse1 (и еще 3)
- **NPulseChannelCableMulti**: CableNeuron2.Soma1.ExcChannel, CableNeuron2.ExcChannel
- **NPulseChannelIaF**: IaFNeuron.Soma1.ExcChannel, IaFNeuron.ExcChannel
- **NPulseLTZoneCable**: CableNeuron2.LTZone
- **NPulseLTZoneIaF**: IaFNeuron.LTZone
- **NPulseLTZoneThresholdBio**: PNeuron2.LTZone, LTZone
- **NPulseMembraneCableMulti**: CableNeuron2.Soma1
- **NPulseMembraneIaF**: IaFNeuron.Soma1
- **NPulseNeuronCableMulti**: CableNeuron2
- **NPulseNeuronIaF**: IaFNeuron
- **NSPNeuronBio**: PNeuron2
- **NSynapseCableMulti**: CableNeuron2.Soma1.ExcSynapse1, CableNeuron2.ExcSynapse1
- **NSynapseIaF**: IaFNeuron.Soma1.ExcSynapse1, IaFNeuron.ExcSynapse1

**Входы системы:**
- `CableNeuron2.LTZone.Inputs`
- `CableNeuron2.NegGenerator`
- `CableNeuron2.Soma1.ExcChannel.ChannelInputs`
- `CableNeuron2.Soma1.ExcChannel.SynapticInputs`
- `CableNeuron2.Soma1.ExcSynapse1.Input`
- `CableNeuron2.Soma1.InputFeedbackSignal`
- `IaFNeuron.LTZone.Inputs`
- `IaFNeuron.Soma1.ExcChannel.SynapticInputs`
- `IaFNeuron.Soma1.ExcSynapse1.Input`
- `IaFNeuron.Soma1.InputFeedbackSignal`
- ... (всего 22 входов)

**Выходы системы:**
- `CableNeuron2.LTZone.Output`
- `CableNeuron2.NegGenerator.Output`
- `CableNeuron2.Soma1.ExcChannel.Output`
- `CableNeuron2.Soma1.ExcSynapse1.Output`
- `IaFNeuron.LTZone.Output`
- `IaFNeuron.Soma1.ExcChannel.Output`
- `IaFNeuron.Soma1.ExcSynapse1.Output`
- `PGenerator.Output`
- `PNeuron2.LTZone.Output`
- `PNeuron2.NegGenerator.Output`
- ... (всего 15 выходов)

**Количество связей:** 17

---

### SdeSolver

**Путь:** `Bin\Configs\Samples\SdeSolver`

**Назначение:** Пример решения стохастических дифференциальных уравнений (SDE)

**Основные компоненты:**
- **NCGenerator**: CGenerator
- **NPGenerator**: PGenerator
- **NSdeSolver**: SdeSolver, SdeSolver2, SynapseSdeSolver, IaFSegment, IaFSegment2 (и еще 2)
- **UMatrixSource**: MatrixSource

**Входы системы:**
- `CGenerator`
- `IaFSegment.Inputs`
- `IaFSegment2.Inputs`
- `IaFSegment3.Inputs`
- `PGenerator`
- `SdeSolver.Inputs`
- `SdeSolver2.Inputs`
- `SynapseSdeSolver.Inputs`
- `SynapseSdeSolver2.Inputs`

**Выходы системы:**
- `CGenerator.Output`
- `IaFSegment.Outputs`
- `IaFSegment2.Outputs`
- `PGenerator.Output`
- `SynapseSdeSolver.Outputs`

**Количество связей:** 7

---

## TimeConstant MotionControl

### AsfMotionControl

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\TimeConstant MotionControl\AsfMotionControl`

**Назначение:** Система управления движением

**Количество каналов:** 0

**Основные компоненты:**
- **NAsfNewSimplestAfferentBranchedEngineControlPM**: EngineControlRangeAfferent
- **NAsfNewSimplestAfferentBranchedMotionElement**: EngineControlRangeAfferent.MotionElement0, MotionElement0
- **NCGenerator**: CGenerator, EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.Ib_NegIntervalSeparator1, EngineControlRangeAfferent.Ib_PosIntervalSeparator1, EngineControlRangeAfferent.II_NegIntervalSeparator1, EngineControlRangeAfferent.II_PosIntervalSeparator1, EngineControlRangeAfferent.Ia_NegIntervalSeparator1 (и еще 7)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NManipulatorSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NNewMotionElement**: MotionElement
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.Motoneuron1, EngineControlRangeAfferent.MotionElement0.Motoneuron2, EngineControlRangeAfferent.MotionElement0.PostAfferent14, EngineControlRangeAfferent.MotionElement0.PostAfferent24, EngineControlRangeAfferent.Motoneuron1 (и еще 19)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, IIPosAfferentGenerator, IINegAfferentGenerator
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTZone, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTZone, EngineControlRangeAfferent.Motoneuron1.LTZone (и еще 21)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTMembrane, EngineControlRangeAfferent.MotionElement0.LTMembrane (и еще 24)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator (и еще 24)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PNeuronPosCGenerator (и еще 24)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_II2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.LTZone (и еще 26)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2.PosChannel (и еще 217)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane3, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronMembrane2 (и еще 48)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_II2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.Receptor (и еще 28)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.Afferent_II1, EngineControlRangeAfferent.MotionElement0.Afferent_II2, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1 (и еще 23)
- **NWPhysicalManipulator**: WPhysicalManipulator

**Входы системы:**
- `AfferentSource1`
- `CGenerator`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator`
- ... (всего 65 входов)

**Количество связей:** 119

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### AsfMotionControl3

**Путь:** `Bin\Configs\!OldConfigs\OldExperiments\TimeConstant MotionControl\AsfMotionControl3`

**Назначение:** Система управления движением

**Количество каналов:** 0

**Основные компоненты:**
- **NAsfNewSimplestAfferentBranchedEngineControlPM3**: EngineControlRangeAfferent
- **NAsfNewSimplestAfferentBranchedMotionElement**: EngineControlRangeAfferent.MotionElement0, EngineControlRangeAfferent.MotionElement1, EngineControlRangeAfferent.MotionElement2, MotionElement0, MotionElement1 (и еще 1)
- **NCGenerator**: CGenerator, EngineControlRangeAfferent.AfferentSource1, AfferentSource1
- **NDCEngine**: DCEngine
- **NIntervalSeparator**: EngineControlRangeAfferent.Ib_NegIntervalSeparator1, EngineControlRangeAfferent.Ib_NegIntervalSeparator2, EngineControlRangeAfferent.Ib_NegIntervalSeparator3, EngineControlRangeAfferent.Ib_PosIntervalSeparator1, EngineControlRangeAfferent.Ib_PosIntervalSeparator2 (и еще 31)
- **NManipulatorInput**: EngineControlRangeAfferent.NManipulatorInput1, NManipulatorInput1
- **NManipulatorSource**: EngineControlRangeAfferent.NManipulatorSource1, NManipulatorSource1
- **NNewSynSPNeuron**: EngineControlRangeAfferent.MotionElement0.Motoneuron1, EngineControlRangeAfferent.MotionElement0.Motoneuron2, EngineControlRangeAfferent.MotionElement0.PostAfferent14, EngineControlRangeAfferent.MotionElement0.PostAfferent24, EngineControlRangeAfferent.MotionElement0.SPNeuron (и еще 43)
- **NPGenerator**: EngineControlRangeAfferent.IIPosAfferentGenerator, EngineControlRangeAfferent.IINegAfferentGenerator, IIPosAfferentGenerator, IINegAfferentGenerator
- **NPLTZone**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTZone, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTZone, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTZone, EngineControlRangeAfferent.MotionElement0.SPNeuron.LTZone (и еще 51)
- **NPLTZoneSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron2.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent14.LTMembrane, EngineControlRangeAfferent.MotionElement0.PostAfferent24.LTMembrane, EngineControlRangeAfferent.MotionElement0.SPNeuron.LTMembrane (и еще 51)
- **NPNeuronNegCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronNegCGenerator, EngineControlRangeAfferent.MotionElement0.SPNeuron.PNeuronNegCGenerator (и еще 51)
- **NPNeuronPosCGenerator**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent14.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.PostAfferent24.PNeuronPosCGenerator, EngineControlRangeAfferent.MotionElement0.SPNeuron.PNeuronPosCGenerator (и еще 51)
- **NPSimpleLTZone**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_II2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.LTZone, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.LTZone (и еще 43)
- **NPSynNeuronChannel**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.LTMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.PosChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane.NegChannel, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2.PosChannel (и еще 427)
- **NPSynNeuronMembrane**: EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane2, EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronMembrane3, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronMembrane, EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronMembrane2 (и еще 99)
- **NPac**: EngineControlRangeAfferent.Pac, Pac
- **NPendulumAndCart**: PendulumAndCart
- **NReceptor**: EngineControlRangeAfferent.MotionElement0.Afferent_II1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_II2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2.Receptor, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1.Receptor (и еще 51)
- **NSimpleAfferentNeuron**: EngineControlRangeAfferent.MotionElement0.Afferent_II1, EngineControlRangeAfferent.MotionElement0.Afferent_II2, EngineControlRangeAfferent.MotionElement0.Afferent_Ia1, EngineControlRangeAfferent.MotionElement0.Afferent_Ia2, EngineControlRangeAfferent.MotionElement0.Afferent_Ib1 (и еще 43)
- **NWPhysicalManipulator**: WPhysicalManipulator

**Входы системы:**
- `AfferentSource1`
- `CGenerator`
- `EngineControlRangeAfferent.AfferentSource1`
- `EngineControlRangeAfferent.IINegAfferentGenerator`
- `EngineControlRangeAfferent.IIPosAfferentGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron1.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronNegCGenerator`
- `EngineControlRangeAfferent.MotionElement0.Motoneuron2.PNeuronPosCGenerator`
- `EngineControlRangeAfferent.MotionElement0.PNeuronNegCGenerator`
- ... (всего 119 входов)

**Количество связей:** 299

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

## a.demcheva

### 10_MazeMemory_HandmadeScheme

**Путь:** `Bin\Configs\a.demcheva\10_MazeMemory_HandmadeScheme`

**Назначение:** Модель памяти для навигации в лабиринте

**Основные компоненты:**
- **NMultiPositionControl**: NMultiPositionControl, NMultiPositionControl2, NMultiPositionControl3, NMultiPositionControl4, NMultiPositionControl5 (и еще 2)
- **NPExcChannelBio**: NMultiPositionControl.InputNeuron1-1.Soma1.ExcChannel, NMultiPositionControl.InputNeuron1-1.ExcChannel, NMultiPositionControl.ControlNeuron1-1.Soma1.ExcChannel, NMultiPositionControl.ControlNeuron1-1.ExcChannel, NMultiPositionControl.PreControlNeuron1.Soma1.ExcChannel (и еще 225)
- **NPGenerator**: NMultiPositionControl.PGenerator1, NMultiPositionControl2.PGenerator1, NMultiPositionControl3.PGenerator1, U_top_0, Point1 (и еще 12)
- **NPInhChannelBio**: NMultiPositionControl.InputNeuron1-1.Soma1.InhChannel, NMultiPositionControl.InputNeuron1-1.InhChannel, NMultiPositionControl.ControlNeuron1-1.Soma1.InhChannel, NMultiPositionControl.ControlNeuron1-1.InhChannel, NMultiPositionControl.PreControlNeuron1.Soma1.InhChannel (и еще 225)
- **NPMembraneBio**: NMultiPositionControl.InputNeuron1-1.Soma1, NMultiPositionControl.ControlNeuron1-1.Soma1, NMultiPositionControl.PreControlNeuron1.Soma1, NMultiPositionControl.PostInputNeuron1.Soma1, NMultiPositionControl.Soma1 (и еще 162)
- **NPNeuronNegCGenerator**: NMultiPositionControl.InputNeuron1-1.NegGenerator, NMultiPositionControl.ControlNeuron1-1.NegGenerator, NMultiPositionControl.PreControlNeuron1.NegGenerator, NMultiPositionControl.PostInputNeuron1.NegGenerator, NMultiPositionControl.NegGenerator (и еще 58)
- **NPNeuronPosCGenerator**: NMultiPositionControl.InputNeuron1-1.PosGenerator, NMultiPositionControl.ControlNeuron1-1.PosGenerator, NMultiPositionControl.PreControlNeuron1.PosGenerator, NMultiPositionControl.PostInputNeuron1.PosGenerator, NMultiPositionControl.PosGenerator (и еще 58)
- **NPSynapseBio**: NMultiPositionControl.InputNeuron1-1.Soma1.ExcSynapse1, NMultiPositionControl.InputNeuron1-1.Soma1.InhSynapse1, NMultiPositionControl.InputNeuron1-1.ExcSynapse1, NMultiPositionControl.InputNeuron1-1.InhSynapse1, NMultiPositionControl.ControlNeuron1-1.Soma1.ExcSynapse1 (и еще 493)
- **NPulseLTZoneThreshold**: NMultiPositionControl.InputNeuron1-1.LTZone, NMultiPositionControl.ControlNeuron1-1.LTZone, NMultiPositionControl.PreControlNeuron1.LTZone, NMultiPositionControl.PostInputNeuron1.LTZone, NMultiPositionControl.LTZone (и еще 58)
- **NSPNeuronGen**: NMultiPositionControl.InputNeuron1-1, NMultiPositionControl.ControlNeuron1-1, NMultiPositionControl.PreControlNeuron1, NMultiPositionControl.PostInputNeuron1, NMultiPositionControl2.InputNeuron1-1 (и еще 43)
- **NTrajectoryElement**: NTrajectoryElement2, NTrajectoryElement3, NTrajectoryElement4, NTrajectoryElement, NTrajectoryElement5 (и еще 2)

**Входы системы:**
- `ControlNeuron1-1.NegGenerator`
- `ControlNeuron1-1.PosGenerator`
- `InputNeuron1-1.NegGenerator`
- `InputNeuron1-1.PosGenerator`
- `NMultiPositionControl.ControlNeuron1-1.LTZone.Inputs`
- `NMultiPositionControl.ControlNeuron1-1.NegGenerator`
- `NMultiPositionControl.ControlNeuron1-1.PosGenerator`
- `NMultiPositionControl.ControlNeuron1-1.Soma1.ExcChannel.ChannelInputs`
- `NMultiPositionControl.ControlNeuron1-1.Soma1.ExcChannel.SynapticInputs`
- `NMultiPositionControl.ControlNeuron1-1.Soma1.ExcSynapse1.Input`
- ... (всего 728 входов)

**Выходы системы:**
- `NMultiPositionControl.ControlNeuron1-1.LTZone.Output`
- `NMultiPositionControl.ControlNeuron1-1.NegGenerator.Output`
- `NMultiPositionControl.ControlNeuron1-1.PosGenerator.Output`
- `NMultiPositionControl.ControlNeuron1-1.Soma1.ExcChannel.Output`
- `NMultiPositionControl.ControlNeuron1-1.Soma1.ExcSynapse1.Output`
- `NMultiPositionControl.ControlNeuron1-1.Soma1.InhChannel.Output`
- `NMultiPositionControl.ControlNeuron1-1.Soma1.InhSynapse1.Output`
- `NMultiPositionControl.InputNeuron1-1.LTZone.Output`
- `NMultiPositionControl.InputNeuron1-1.NegGenerator.Output`
- `NMultiPositionControl.InputNeuron1-1.PosGenerator.Output`
- ... (всего 550 выходов)

**Количество связей:** 634

**Связанные публикации:**
- [Исследование метода запоминания пространственных конфигураций робототехнической системы](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 7: Бахшиев А.В., Гунделах Ф.В.

---

### 11_MazeMemory_BlockDebugging

**Путь:** `Bin\Configs\a.demcheva\11_MazeMemory_BlockDebugging`

**Назначение:** Модель памяти для навигации в лабиринте

**Основные компоненты:**
- **NMazeMemory**: NMazeMemory
- **NMultiPositionControl**: NMultiPositionControl, NMultiPositionControl2, NMultiPositionControl3, NMultiPositionControl4, NMultiPositionControl5 (и еще 9)
- **NPExcChannelBio**: NMultiPositionControl.InputNeuron1-1.Soma1.ExcChannel, NMultiPositionControl.InputNeuron1-1.ExcChannel, NMultiPositionControl.ControlNeuron1-1.Soma1.ExcChannel, NMultiPositionControl.ControlNeuron1-1.ExcChannel, NMultiPositionControl.PreControlNeuron1.Soma1.ExcChannel (и еще 455)
- **NPGenerator**: NMultiPositionControl.PGenerator1, NMultiPositionControl2.PGenerator1, NMultiPositionControl3.PGenerator1, U_top_0, Point1 (и еще 14)
- **NPInhChannelBio**: NMultiPositionControl.InputNeuron1-1.Soma1.InhChannel, NMultiPositionControl.InputNeuron1-1.InhChannel, NMultiPositionControl.ControlNeuron1-1.Soma1.InhChannel, NMultiPositionControl.ControlNeuron1-1.InhChannel, NMultiPositionControl.PreControlNeuron1.Soma1.InhChannel (и еще 455)
- **NPMembraneBio**: NMultiPositionControl.InputNeuron1-1.Soma1, NMultiPositionControl.ControlNeuron1-1.Soma1, NMultiPositionControl.PreControlNeuron1.Soma1, NMultiPositionControl.PostInputNeuron1.Soma1, NMultiPositionControl.Soma1 (и еще 329)
- **NPNeuronNegCGenerator**: NMultiPositionControl.InputNeuron1-1.NegGenerator, NMultiPositionControl.ControlNeuron1-1.NegGenerator, NMultiPositionControl.PreControlNeuron1.NegGenerator, NMultiPositionControl.PostInputNeuron1.NegGenerator, NMultiPositionControl.NegGenerator (и еще 121)
- **NPNeuronPosCGenerator**: NMultiPositionControl.InputNeuron1-1.PosGenerator, NMultiPositionControl.ControlNeuron1-1.PosGenerator, NMultiPositionControl.PreControlNeuron1.PosGenerator, NMultiPositionControl.PostInputNeuron1.PosGenerator, NMultiPositionControl.PosGenerator (и еще 121)
- **NPSynapseBio**: NMultiPositionControl.InputNeuron1-1.Soma1.ExcSynapse1, NMultiPositionControl.InputNeuron1-1.Soma1.InhSynapse1, NMultiPositionControl.InputNeuron1-1.ExcSynapse1, NMultiPositionControl.InputNeuron1-1.InhSynapse1, NMultiPositionControl.ControlNeuron1-1.Soma1.ExcSynapse1 (и еще 1027)
- **NPulseLTZoneThreshold**: NMultiPositionControl.InputNeuron1-1.LTZone, NMultiPositionControl.ControlNeuron1-1.LTZone, NMultiPositionControl.PreControlNeuron1.LTZone, NMultiPositionControl.PostInputNeuron1.LTZone, NMultiPositionControl.LTZone (и еще 121)
- **NSPNeuronGen**: NMultiPositionControl.InputNeuron1-1, NMultiPositionControl.ControlNeuron1-1, NMultiPositionControl.PreControlNeuron1, NMultiPositionControl.PostInputNeuron1, NMultiPositionControl2.InputNeuron1-1 (и еще 91)
- **NTrajectoryElement**: NTrajectoryElement2, NTrajectoryElement3, NTrajectoryElement4, NTrajectoryElement, NTrajectoryElement5 (и еще 9)

**Входы системы:**
- `ControlNeuron1-1.NegGenerator`
- `ControlNeuron1-1.PosGenerator`
- `InputNeuron1-1.NegGenerator`
- `InputNeuron1-1.PosGenerator`
- `NMazeMemory.ControlNeuron1-1.NegGenerator`
- `NMazeMemory.ControlNeuron1-1.PosGenerator`
- `NMazeMemory.InputNeuron1-1.NegGenerator`
- `NMazeMemory.InputNeuron1-1.PosGenerator`
- `NMazeMemory.NMultiPositionControl0.ControlNeuron1-1.LTZone.Inputs`
- `NMazeMemory.NMultiPositionControl0.ControlNeuron1-1.NegGenerator`
- ... (всего 1268 входов)

**Выходы системы:**
- `NMazeMemory.NMultiPositionControl0.ControlNeuron1-1.LTZone.Output`
- `NMazeMemory.NMultiPositionControl0.ControlNeuron1-1.NegGenerator.Output`
- `NMazeMemory.NMultiPositionControl0.ControlNeuron1-1.PosGenerator.Output`
- `NMazeMemory.NMultiPositionControl0.ControlNeuron1-1.Soma1.ExcChannel.Output`
- `NMazeMemory.NMultiPositionControl0.ControlNeuron1-1.Soma1.ExcSynapse1.Output`
- `NMazeMemory.NMultiPositionControl0.ControlNeuron1-1.Soma1.InhChannel.Output`
- `NMazeMemory.NMultiPositionControl0.ControlNeuron1-1.Soma1.InhSynapse1.Output`
- `NMazeMemory.NMultiPositionControl0.InputNeuron1-1.LTZone.Output`
- `NMazeMemory.NMultiPositionControl0.InputNeuron1-1.NegGenerator.Output`
- `NMazeMemory.NMultiPositionControl0.InputNeuron1-1.PosGenerator.Output`
- ... (всего 935 выходов)

**Количество связей:** 1084

**Связанные публикации:**
- [Исследование метода запоминания пространственных конфигураций робототехнической системы](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 7: Бахшиев А.В., Гунделах Ф.В.

---

### 12_MazeMemory_HandmadeExperiment

**Путь:** `Bin\Configs\a.demcheva\12_MazeMemory_HandmadeExperiment`

**Назначение:** Модель памяти для навигации в лабиринте

**Основные компоненты:**
- **NNeuronTrainer**: NeuronTrainer_A, NeuronTrainer_B, NeuronTrainer_C
- **NPExcChannelBio**: NeuronTrainer_A.Neuron.Dendrite1_1.ExcChannel, NeuronTrainer_A.Neuron.Dendrite2_1.ExcChannel, NeuronTrainer_A.Neuron.Dendrite3_22.ExcChannel, NeuronTrainer_A.Neuron.Dendrite3_21.ExcChannel, NeuronTrainer_A.Neuron.Dendrite3_20.ExcChannel (и еще 360)
- **NPInhChannelBio**: NeuronTrainer_A.Neuron.Dendrite1_1.InhChannel, NeuronTrainer_A.Neuron.Dendrite2_1.InhChannel, NeuronTrainer_A.Neuron.Dendrite3_22.InhChannel, NeuronTrainer_A.Neuron.Dendrite3_21.InhChannel, NeuronTrainer_A.Neuron.Dendrite3_20.InhChannel (и еще 360)
- **NPMembraneBio**: NeuronTrainer_A.Neuron.Dendrite1_1, NeuronTrainer_A.Neuron.Dendrite2_1, NeuronTrainer_A.Neuron.Dendrite3_22, NeuronTrainer_A.Neuron.Dendrite3_21, NeuronTrainer_A.Neuron.Dendrite3_20 (и еще 340)
- **NPNeuronNegCGenerator**: NeuronTrainer_A.Neuron.NegGenerator, NeuronTrainer_A.NegGenerator, PNeuron_A.NegGenerator, A_L.NegGenerator, Left.NegGenerator (и еще 15)
- **NPNeuronPosCGenerator**: NeuronTrainer_A.Neuron.PosGenerator, NeuronTrainer_A.PosGenerator, PNeuron_A.PosGenerator, A_L.PosGenerator, Left.PosGenerator (и еще 15)
- **NPSynapseBio**: NeuronTrainer_A.Neuron.Dendrite1_1.ExcSynapse1, NeuronTrainer_A.Neuron.Dendrite1_1.InhSynapse1, NeuronTrainer_A.Neuron.Dendrite2_1.ExcSynapse1, NeuronTrainer_A.Neuron.Dendrite2_1.InhSynapse1, NeuronTrainer_A.Neuron.Dendrite3_22.ExcSynapse1 (и еще 1378)
- **NPulseGeneratorTransit**: NeuronTrainer_A.Source1, NeuronTrainer_A.Source2, NeuronTrainer_A.Source3, PGenTr_A, PGenTr_B (и еще 13)
- **NPulseLTZoneThreshold**: NeuronTrainer_A.Neuron.LTZone, NeuronTrainer_A.LTZone, PNeuron_A.LTZone, A_L.LTZone, Left.LTZone (и еще 15)
- **NSPNeuronGen**: NeuronTrainer_A.Neuron, PNeuron_A, A_L, Left, Right (и еще 11)

**Входы системы:**
- `A_L.Dendrite1_1.ExcChannel.ChannelInputs`
- `A_L.Dendrite1_1.ExcChannel.SynapticInputs`
- `A_L.Dendrite1_1.InhChannel.ChannelInputs`
- `A_L.Dendrite1_1.InhChannel.SynapticInputs`
- `A_L.Dendrite1_10.ExcChannel.ChannelInputs`
- `A_L.Dendrite1_10.ExcChannel.SynapticInputs`
- `A_L.Dendrite1_10.ExcSynapse1.Input`
- `A_L.Dendrite1_10.InhChannel.ChannelInputs`
- `A_L.Dendrite1_10.InhChannel.SynapticInputs`
- `A_L.Dendrite1_2.ExcChannel.ChannelInputs`
- ... (всего 722 входов)

**Выходы системы:**
- `A_L.Dendrite1_1.ExcChannel.Output`
- `A_L.Dendrite1_1.ExcSynapse1.Output`
- `A_L.Dendrite1_1.InhChannel.Output`
- `A_L.Dendrite1_1.InhSynapse1.Output`
- `A_L.Dendrite1_10.ExcChannel.Output`
- `A_L.Dendrite1_10.ExcSynapse1.Output`
- `A_L.Dendrite1_10.InhChannel.Output`
- `A_L.Dendrite1_10.InhSynapse1.Output`
- `A_L.Dendrite1_2.ExcChannel.Output`
- `A_L.Dendrite1_2.ExcSynapse1.Output`
- ... (всего 675 выходов)

**Количество связей:** 793

**Связанные публикации:**
- [Исследование метода запоминания пространственных конфигураций робототехнической системы](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 7: Бахшиев А.В., Гунделах Ф.В.

---

### 12_MazeMemory_HandmadeExperiment_sec_alg

**Путь:** `Bin\Configs\a.demcheva\12_MazeMemory_HandmadeExperiment_sec_alg`

**Назначение:** Модель памяти для навигации в лабиринте

**Основные компоненты:**
- **NNeuronTrainer**: NeuronTrainer_A, NeuronTrainer_B, NeuronTrainer_C
- **NPExcChannelBio**: NeuronTrainer_A.Neuron.Dendrite1_1.ExcChannel, NeuronTrainer_A.Neuron.Dendrite2_1.ExcChannel, NeuronTrainer_A.Neuron.Dendrite3_22.ExcChannel, NeuronTrainer_A.Neuron.Dendrite3_21.ExcChannel, NeuronTrainer_A.Neuron.Dendrite3_20.ExcChannel (и еще 360)
- **NPInhChannelBio**: NeuronTrainer_A.Neuron.Dendrite1_1.InhChannel, NeuronTrainer_A.Neuron.Dendrite2_1.InhChannel, NeuronTrainer_A.Neuron.Dendrite3_22.InhChannel, NeuronTrainer_A.Neuron.Dendrite3_21.InhChannel, NeuronTrainer_A.Neuron.Dendrite3_20.InhChannel (и еще 360)
- **NPMembraneBio**: NeuronTrainer_A.Neuron.Dendrite1_1, NeuronTrainer_A.Neuron.Dendrite2_1, NeuronTrainer_A.Neuron.Dendrite3_22, NeuronTrainer_A.Neuron.Dendrite3_21, NeuronTrainer_A.Neuron.Dendrite3_20 (и еще 340)
- **NPNeuronNegCGenerator**: NeuronTrainer_A.Neuron.NegGenerator, NeuronTrainer_A.NegGenerator, PNeuron_A.NegGenerator, A_L.NegGenerator, Left.NegGenerator (и еще 15)
- **NPNeuronPosCGenerator**: NeuronTrainer_A.Neuron.PosGenerator, NeuronTrainer_A.PosGenerator, PNeuron_A.PosGenerator, A_L.PosGenerator, Left.PosGenerator (и еще 15)
- **NPSynapseBio**: NeuronTrainer_A.Neuron.Dendrite1_1.ExcSynapse1, NeuronTrainer_A.Neuron.Dendrite1_1.InhSynapse1, NeuronTrainer_A.Neuron.Dendrite2_1.ExcSynapse1, NeuronTrainer_A.Neuron.Dendrite2_1.InhSynapse1, NeuronTrainer_A.Neuron.Dendrite3_22.ExcSynapse1 (и еще 1378)
- **NPulseGeneratorTransit**: NeuronTrainer_A.Source1, NeuronTrainer_A.Source2, NeuronTrainer_A.Source3, PGenTr_A, PGenTr_B (и еще 13)
- **NPulseLTZoneThreshold**: NeuronTrainer_A.Neuron.LTZone, NeuronTrainer_A.LTZone, PNeuron_A.LTZone, A_L.LTZone, Left.LTZone (и еще 15)
- **NSPNeuronGen**: NeuronTrainer_A.Neuron, PNeuron_A, A_L, Left, Right (и еще 11)

**Входы системы:**
- `A_L.Dendrite1_1.ExcChannel.ChannelInputs`
- `A_L.Dendrite1_1.ExcChannel.SynapticInputs`
- `A_L.Dendrite1_1.InhChannel.ChannelInputs`
- `A_L.Dendrite1_1.InhChannel.SynapticInputs`
- `A_L.Dendrite1_10.ExcChannel.ChannelInputs`
- `A_L.Dendrite1_10.ExcChannel.SynapticInputs`
- `A_L.Dendrite1_10.ExcSynapse1.Input`
- `A_L.Dendrite1_10.InhChannel.ChannelInputs`
- `A_L.Dendrite1_10.InhChannel.SynapticInputs`
- `A_L.Dendrite1_2.ExcChannel.ChannelInputs`
- ... (всего 722 входов)

**Выходы системы:**
- `A_L.Dendrite1_1.ExcChannel.Output`
- `A_L.Dendrite1_1.ExcSynapse1.Output`
- `A_L.Dendrite1_1.InhChannel.Output`
- `A_L.Dendrite1_1.InhSynapse1.Output`
- `A_L.Dendrite1_10.ExcChannel.Output`
- `A_L.Dendrite1_10.ExcSynapse1.Output`
- `A_L.Dendrite1_10.InhChannel.Output`
- `A_L.Dendrite1_10.InhSynapse1.Output`
- `A_L.Dendrite1_2.ExcChannel.Output`
- `A_L.Dendrite1_2.ExcSynapse1.Output`
- ... (всего 675 выходов)

**Количество связей:** 793

**Связанные публикации:**
- [Исследование метода запоминания пространственных конфигураций робототехнической системы](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 7: Бахшиев А.В., Гунделах Ф.В.

---

### 13_MazeMemory_HandmadeExperiment_first_alg

**Путь:** `Bin\Configs\a.demcheva\13_MazeMemory_HandmadeExperiment_first_alg`

**Назначение:** Модель памяти для навигации в лабиринте

**Основные компоненты:**
- **NMazeMemorySimplified**: A, C_Right, B_Left, A1_Forward, C1_Right (и еще 1)
- **NMultiPositionControl**: A.NMultiPositionControl0, C_Right.NMultiPositionControl0, B_Left.NMultiPositionControl0, A1_Forward.NMultiPositionControl0, C1_Right.NMultiPositionControl0 (и еще 2)
- **NNeuronTrainer**: A.NMultiPositionControl0.NeuronTrainer, A.NeuronTrainer, B_Left.NMultiPositionControl0.NeuronTrainer, B_Left.NeuronTrainer, C1_Right.NMultiPositionControl0.NeuronTrainer (и еще 3)
- **NPExcChannelBio**: A.NTrajectoryElement0.Neuron1.Dendrite1_5.ExcChannel, A.NTrajectoryElement0.Neuron1.Dendrite1_4.ExcChannel, A.NTrajectoryElement0.Neuron1.Dendrite1_3.ExcChannel, A.NTrajectoryElement0.Neuron1.Dendrite1_2.ExcChannel, A.NTrajectoryElement0.Neuron1.Dendrite1_1.ExcChannel (и еще 1569)
- **NPGenerator**: PGenerator
- **NPInhChannelBio**: A.NTrajectoryElement0.Neuron1.Dendrite1_5.InhChannel, A.NTrajectoryElement0.Neuron1.Dendrite1_4.InhChannel, A.NTrajectoryElement0.Neuron1.Dendrite1_3.InhChannel, A.NTrajectoryElement0.Neuron1.Dendrite1_2.InhChannel, A.NTrajectoryElement0.Neuron1.Dendrite1_1.InhChannel (и еще 1569)
- **NPMembraneBio**: A.NTrajectoryElement0.Neuron1.Dendrite1_5, A.NTrajectoryElement0.Neuron1.Dendrite1_4, A.NTrajectoryElement0.Neuron1.Dendrite1_3, A.NTrajectoryElement0.Neuron1.Dendrite1_2, A.NTrajectoryElement0.Neuron1.Dendrite1_1 (и еще 1451)
- **NPNeuronNegCGenerator**: A.NTrajectoryElement0.Neuron1.NegGenerator, A.NTrajectoryElement0.Neuron2.NegGenerator, A.NTrajectoryElement0.NegGenerator, A.NMultiPositionControl0.ControlNeuron1-1.NegGenerator, A.NMultiPositionControl0.PreControlNeuron1.NegGenerator (и еще 113)
- **NPNeuronPosCGenerator**: A.NTrajectoryElement0.Neuron1.PosGenerator, A.NTrajectoryElement0.Neuron2.PosGenerator, A.NTrajectoryElement0.PosGenerator, A.NMultiPositionControl0.ControlNeuron1-1.PosGenerator, A.NMultiPositionControl0.PreControlNeuron1.PosGenerator (и еще 113)
- **NPSynapseBio**: A.NTrajectoryElement0.Neuron1.Dendrite1_5.ExcSynapse1, A.NTrajectoryElement0.Neuron1.Dendrite1_5.InhSynapse1, A.NTrajectoryElement0.Neuron1.Dendrite1_4.ExcSynapse1, A.NTrajectoryElement0.Neuron1.Dendrite1_4.InhSynapse1, A.NTrajectoryElement0.Neuron1.Dendrite1_3.ExcSynapse1 (и еще 5820)
- **NPulseGeneratorTransit**: A.NMultiPositionControl0.NeuronTrainer.Source1, A.NMultiPositionControl0.NeuronTrainer.Source2, A.NMultiPositionControl0.NeuronTrainer.Source3, A.NMultiPositionControl0.Source1, A.NMultiPositionControl0.Source2 (и еще 43)
- **NPulseLTZoneThreshold**: A.NTrajectoryElement0.Neuron1.LTZone, A.NTrajectoryElement0.Neuron2.LTZone, A.NTrajectoryElement0.LTZone, A.NMultiPositionControl0.ControlNeuron1-1.LTZone, A.NMultiPositionControl0.PreControlNeuron1.LTZone (и еще 113)
- **NSPNeuronGen**: A.NTrajectoryElement0.Neuron1, A.NTrajectoryElement0.Neuron2, A.NMultiPositionControl0.ControlNeuron1-1, A.NMultiPositionControl0.PreControlNeuron1, A.NMultiPositionControl0.PostInputNeuron1 (и еще 84)
- **NTrajectoryElement**: A.NTrajectoryElement0, C_Right.NTrajectoryElement0, B_Left.NTrajectoryElement0, A1_Forward.NTrajectoryElement0, C1_Right.NTrajectoryElement0 (и еще 2)

**Входы системы:**
- `A.ControlNeuron1-1.NegGenerator`
- `A.ControlNeuron1-1.PosGenerator`
- `A.NMultiPositionControl0.ControlNeuron1-1.LTZone.Inputs`
- `A.NMultiPositionControl0.ControlNeuron1-1.NegGenerator`
- `A.NMultiPositionControl0.ControlNeuron1-1.PosGenerator`
- `A.NMultiPositionControl0.ControlNeuron1-1.Soma1.ExcChannel.ChannelInputs`
- `A.NMultiPositionControl0.ControlNeuron1-1.Soma1.ExcChannel.SynapticInputs`
- `A.NMultiPositionControl0.ControlNeuron1-1.Soma1.InhChannel.ChannelInputs`
- `A.NMultiPositionControl0.ControlNeuron1-1.Soma1.InhChannel.SynapticInputs`
- `A.NMultiPositionControl0.ControlNeuron1-1.Soma1.InputFeedbackSignal`
- ... (всего 1197 входов)

**Выходы системы:**
- `A.NMultiPositionControl0.ControlNeuron1-1.LTZone.Output`
- `A.NMultiPositionControl0.ControlNeuron1-1.NegGenerator.Output`
- `A.NMultiPositionControl0.ControlNeuron1-1.PosGenerator.Output`
- `A.NMultiPositionControl0.ControlNeuron1-1.Soma1.ExcChannel.Output`
- `A.NMultiPositionControl0.ControlNeuron1-1.Soma1.ExcSynapse1.Output`
- `A.NMultiPositionControl0.ControlNeuron1-1.Soma1.InhChannel.Output`
- `A.NMultiPositionControl0.ControlNeuron1-1.Soma1.InhSynapse1.Output`
- `A.NMultiPositionControl0.NeuronTrainer.Neuron.Dendrite1_1.ExcChannel.Output`
- `A.NMultiPositionControl0.NeuronTrainer.Neuron.Dendrite1_1.ExcSynapse1.Output`
- `A.NMultiPositionControl0.NeuronTrainer.Neuron.Dendrite1_1.InhChannel.Output`
- ... (всего 885 выходов)

**Количество связей:** 1072

**Связанные публикации:**
- [Исследование метода запоминания пространственных конфигураций робототехнической системы](https://neuromodeler.ru/index.php?option=com_content&view=article&id=44&Itemid=677&lang=ru) - Публикация 7: Бахшиев А.В., Гунделах Ф.В.

---

### 2_NewPositionControl_Test

**Путь:** `Bin\Configs\a.demcheva\2_NewPositionControl_Test`

**Назначение:** Система управления движением

**Основные компоненты:**
- **NCGenerator**: EngineMotionControl2.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineMotionControl2.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine2
- **NEngineMotionControl**: EngineMotionControl2
- **NIntervalSeparator**: EngineMotionControl2.NegIntervalSeparator11, EngineMotionControl2.PosIntervalSeparator11, EngineMotionControl2.NegIntervalSeparator21, EngineMotionControl2.PosIntervalSeparator21, EngineMotionControl2.NegIntervalSeparator31 (и еще 7)
- **NManipulatorInput**: EngineMotionControl2.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineMotionControl2.MotionElement0, EngineMotionControl2.MotionElement1, EngineMotionControl2.MotionElement2, MotionElement0, MotionElement1 (и еще 1)
- **NNewPositionControlElement**: NNewPositionControlElement2
- **NNewSPNeuron**: NNewPositionControlElement2.InputNeuronL11, NNewPositionControlElement2.InputNeuronR11, NNewPositionControlElement2.InputNeuronL21, NNewPositionControlElement2.InputNeuronR21, NNewPositionControlElement2.InputNeuronL31 (и еще 75)
- **NPExcChannel**: NNewPositionControlElement2.InputNeuronL11.Soma1.ExcChannel, NNewPositionControlElement2.InputNeuronR11.Soma1.ExcChannel, NNewPositionControlElement2.InputNeuronL21.Soma1.ExcChannel, NNewPositionControlElement2.InputNeuronR21.Soma1.ExcChannel, NNewPositionControlElement2.InputNeuronL31.Soma1.ExcChannel (и еще 84)
- **NPGenerator**: NNewPositionControlElement2.NPGeneratorL11, NNewPositionControlElement2.NPGeneratorR11, NNewPositionControlElement2.NPGeneratorL21, NNewPositionControlElement2.NPGeneratorR21, NNewPositionControlElement2.NPGeneratorL31 (и еще 61)
- **NPInhChannel**: NNewPositionControlElement2.InputNeuronL11.Soma1.InhChannel, NNewPositionControlElement2.InputNeuronR11.Soma1.InhChannel, NNewPositionControlElement2.InputNeuronL21.Soma1.InhChannel, NNewPositionControlElement2.InputNeuronR21.Soma1.InhChannel, NNewPositionControlElement2.InputNeuronL31.Soma1.InhChannel (и еще 84)
- **NPLTExcChannel**: NNewPositionControlElement2.InputNeuronL11.LTMembrane.ExcChannel, NNewPositionControlElement2.InputNeuronL11.ExcChannel, NNewPositionControlElement2.InputNeuronR11.LTMembrane.ExcChannel, NNewPositionControlElement2.InputNeuronR11.ExcChannel, NNewPositionControlElement2.InputNeuronL21.LTMembrane.ExcChannel (и еще 173)
- **NPLTInhChannel**: NNewPositionControlElement2.InputNeuronL11.LTMembrane.InhChannel, NNewPositionControlElement2.InputNeuronL11.InhChannel, NNewPositionControlElement2.InputNeuronR11.LTMembrane.InhChannel, NNewPositionControlElement2.InputNeuronR11.InhChannel, NNewPositionControlElement2.InputNeuronL21.LTMembrane.InhChannel (и еще 173)
- **NPLTZone**: NNewPositionControlElement2.InputNeuronL11.LTZone, NNewPositionControlElement2.InputNeuronR11.LTZone, NNewPositionControlElement2.InputNeuronL21.LTZone, NNewPositionControlElement2.InputNeuronR21.LTZone, NNewPositionControlElement2.InputNeuronL31.LTZone (и еще 84)
- **NPLTZoneNeuronMembrane**: NNewPositionControlElement2.InputNeuronL11.LTMembrane, NNewPositionControlElement2.InputNeuronR11.LTMembrane, NNewPositionControlElement2.InputNeuronL21.LTMembrane, NNewPositionControlElement2.InputNeuronR21.LTMembrane, NNewPositionControlElement2.InputNeuronL31.LTMembrane (и еще 84)
- **NPMembrane**: NNewPositionControlElement2.InputNeuronL11.Soma1, NNewPositionControlElement2.InputNeuronR11.Soma1, NNewPositionControlElement2.InputNeuronL21.Soma1, NNewPositionControlElement2.InputNeuronR21.Soma1, NNewPositionControlElement2.InputNeuronL31.Soma1 (и еще 84)
- **NPNeuronNegCGenerator**: NNewPositionControlElement2.InputNeuronL11.NegGenerator, NNewPositionControlElement2.InputNeuronR11.NegGenerator, NNewPositionControlElement2.InputNeuronL21.NegGenerator, NNewPositionControlElement2.InputNeuronR21.NegGenerator, NNewPositionControlElement2.InputNeuronL31.NegGenerator (и еще 84)
- **NPNeuronPosCGenerator**: NNewPositionControlElement2.InputNeuronL11.PosGenerator, NNewPositionControlElement2.InputNeuronR11.PosGenerator, NNewPositionControlElement2.InputNeuronL21.PosGenerator, NNewPositionControlElement2.InputNeuronR21.PosGenerator, NNewPositionControlElement2.InputNeuronL31.PosGenerator (и еще 84)
- **NPSimpleLTZone**: EngineMotionControl2.MotionElement0.AfferentR1.LTZone, EngineMotionControl2.MotionElement0.AfferentL1.LTZone, EngineMotionControl2.MotionElement1.AfferentR1.LTZone, EngineMotionControl2.MotionElement1.AfferentL1.LTZone, EngineMotionControl2.MotionElement2.AfferentR1.LTZone (и еще 11)
- **NPSynapse**: NNewPositionControlElement2.InputNeuronL11.Soma1.ExcSynapse1, NNewPositionControlElement2.InputNeuronL11.Soma1.InhSynapse1, NNewPositionControlElement2.InputNeuronL11.LTMembrane.ExcSynapse1, NNewPositionControlElement2.InputNeuronL11.LTMembrane.InhSynapse1, NNewPositionControlElement2.InputNeuronL11.ExcSynapse1 (и еще 639)
- **NPac**: EngineMotionControl2.Pac, Pac
- **NReceptor**: EngineMotionControl2.MotionElement0.AfferentR1.Receptor, EngineMotionControl2.MotionElement0.AfferentL1.Receptor, EngineMotionControl2.MotionElement0.Receptor, EngineMotionControl2.MotionElement1.AfferentR1.Receptor, EngineMotionControl2.MotionElement1.AfferentL1.Receptor (и еще 19)
- **NSimpleAfferentNeuron**: EngineMotionControl2.MotionElement0.AfferentR1, EngineMotionControl2.MotionElement0.AfferentL1, EngineMotionControl2.MotionElement1.AfferentR1, EngineMotionControl2.MotionElement1.AfferentL1, EngineMotionControl2.MotionElement2.AfferentR1 (и еще 11)
- **UStatisticDoubleMatrix**: EngineMotionControl2.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentL1.LTZone.PGenerator`
- `AfferentL1.PGenerator`
- `AfferentR1.LTZone.PGenerator`
- `AfferentR1.PGenerator`
- `AfferentSource1`
- `ControlNeuronL11.NegGenerator`
- `ControlNeuronL11.PosGenerator`
- `ControlNeuronL21.NegGenerator`
- `ControlNeuronL21.PosGenerator`
- `ControlNeuronL31.NegGenerator`
- ... (всего 703 входов)

**Выходы системы:**
- `DCEngine2.OutputAngle`
- `EngineMotionControl2.MotionElement0.AfferentL1.LTZone.Output`
- `EngineMotionControl2.MotionElement0.AfferentL1.Receptor.Output`
- `EngineMotionControl2.MotionElement0.AfferentR1.LTZone.Output`
- `EngineMotionControl2.MotionElement0.AfferentR1.Receptor.Output`
- `EngineMotionControl2.MotionElement0.MotoneuronL.LTMembrane.ExcChannel.Output`
- `EngineMotionControl2.MotionElement0.MotoneuronL.LTMembrane.ExcSynapse1.Output`
- `EngineMotionControl2.MotionElement0.MotoneuronL.LTMembrane.InhChannel.Output`
- `EngineMotionControl2.MotionElement0.MotoneuronL.LTMembrane.InhSynapse1.Output`
- `EngineMotionControl2.MotionElement0.MotoneuronL.LTZone.Output`
- ... (всего 442 выходов)

**Количество связей:** 517

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### 3_MultiPositionControl_SimpleTest

**Путь:** `Bin\Configs\a.demcheva\3_MultiPositionControl_SimpleTest`

**Назначение:** Система управления движением

**Основные компоненты:**
- **NCGenerator**: EngineMotionControl.AfferentSource1, EngineMotionControl2.AfferentSource1, EngineMotionControl3.AfferentSource1, EngineMotionControl4.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineMotionControl.NManipulatorSource1, EngineMotionControl2.NManipulatorSource1, EngineMotionControl3.NManipulatorSource1, EngineMotionControl4.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine, DCEngine2, DCEngine3, DCEngine4
- **NEngineMotionControl**: EngineMotionControl, EngineMotionControl2, EngineMotionControl3, EngineMotionControl4
- **NIntervalSeparator**: EngineMotionControl.NegIntervalSeparator11, EngineMotionControl.PosIntervalSeparator11, EngineMotionControl.NegIntervalSeparator21, EngineMotionControl.PosIntervalSeparator21, EngineMotionControl.NegIntervalSeparator31 (и еще 25)
- **NManipulatorInput**: EngineMotionControl.NManipulatorInput1, EngineMotionControl2.NManipulatorInput1, EngineMotionControl3.NManipulatorInput1, EngineMotionControl4.NManipulatorInput1, NManipulatorInput1
- **NMultiPositionControl**: NMultiPositionControl, NMultiPositionControl2
- **NNewMotionElement**: EngineMotionControl.MotionElement0, EngineMotionControl.MotionElement1, EngineMotionControl.MotionElement2, EngineMotionControl2.MotionElement0, EngineMotionControl2.MotionElement1 (и еще 10)
- **NNewPositionControlElement**: NNewPositionControlElement, NNewPositionControlElement2, NNewPositionControlElement3, NNewPositionControlElement4
- **NNewSPNeuron**: EngineMotionControl.MotionElement0.MotoneuronL, EngineMotionControl.MotionElement0.MotoneuronR, EngineMotionControl.MotionElement0.PostAfferentL1, EngineMotionControl.MotionElement0.PostAfferentR1, EngineMotionControl.MotionElement1.MotoneuronL (и еще 243)
- **NNewSynSPNeuron**: NMultiPositionControl.InputNeuron1-1, NMultiPositionControl.InputNeuron1-2, NMultiPositionControl.InputNeuron1-3, NMultiPositionControl.InputNeuron1-4, NMultiPositionControl.InputNeuron1-5 (и еще 23)
- **NPExcChannel**: EngineMotionControl.MotionElement0.MotoneuronL.Soma1.ExcChannel, EngineMotionControl.MotionElement0.MotoneuronR.Soma1.ExcChannel, EngineMotionControl.MotionElement0.PostAfferentL1.Soma1.ExcChannel, EngineMotionControl.MotionElement0.PostAfferentR1.Soma1.ExcChannel, EngineMotionControl.MotionElement0.Soma1.ExcChannel (и еще 268)
- **NPGenerator**: NMultiPositionControl.PGenerator1, EngineMotionControl.IIPosAfferentGenerator, EngineMotionControl.IINegAfferentGenerator, EngineMotionControl.InternalGenerator, EngineMotionControl.MotionElement0.AfferentR1.LTZone.PGenerator (и еще 162)
- **NPInhChannel**: EngineMotionControl.MotionElement0.MotoneuronL.Soma1.InhChannel, EngineMotionControl.MotionElement0.MotoneuronR.Soma1.InhChannel, EngineMotionControl.MotionElement0.PostAfferentL1.Soma1.InhChannel, EngineMotionControl.MotionElement0.PostAfferentR1.Soma1.InhChannel, EngineMotionControl.MotionElement0.Soma1.InhChannel (и еще 268)
- **NPLTExcChannel**: NMultiPositionControl.InputNeuron1-1.LTMembrane.ExcChannel, NMultiPositionControl.InputNeuron1-1.ExcChannel, NMultiPositionControl.InputNeuron1-2.LTMembrane.ExcChannel, NMultiPositionControl.InputNeuron1-2.ExcChannel, NMultiPositionControl.InputNeuron1-3.LTMembrane.ExcChannel (и еще 599)
- **NPLTInhChannel**: NMultiPositionControl.InputNeuron1-1.LTMembrane.InhChannel, NMultiPositionControl.InputNeuron1-1.InhChannel, NMultiPositionControl.InputNeuron1-2.LTMembrane.InhChannel, NMultiPositionControl.InputNeuron1-2.InhChannel, NMultiPositionControl.InputNeuron1-3.LTMembrane.InhChannel (и еще 599)
- **NPLTZone**: NMultiPositionControl.InputNeuron1-1.LTZone, NMultiPositionControl.InputNeuron1-2.LTZone, NMultiPositionControl.InputNeuron1-3.LTZone, NMultiPositionControl.InputNeuron1-4.LTZone, NMultiPositionControl.InputNeuron1-5.LTZone (и еще 297)
- **NPLTZoneNeuronMembrane**: NMultiPositionControl.InputNeuron1-1.LTMembrane, NMultiPositionControl.InputNeuron1-2.LTMembrane, NMultiPositionControl.InputNeuron1-3.LTMembrane, NMultiPositionControl.InputNeuron1-4.LTMembrane, NMultiPositionControl.InputNeuron1-5.LTMembrane (и еще 297)
- **NPMembrane**: EngineMotionControl.MotionElement0.MotoneuronL.Soma1, EngineMotionControl.MotionElement0.MotoneuronR.Soma1, EngineMotionControl.MotionElement0.PostAfferentL1.Soma1, EngineMotionControl.MotionElement0.PostAfferentR1.Soma1, EngineMotionControl.MotionElement0.Soma1 (и еще 268)
- **NPNeuronNegCGenerator**: NMultiPositionControl.InputNeuron1-1.NegGenerator, NMultiPositionControl.InputNeuron1-2.NegGenerator, NMultiPositionControl.InputNeuron1-3.NegGenerator, NMultiPositionControl.InputNeuron1-4.NegGenerator, NMultiPositionControl.InputNeuron1-5.NegGenerator (и еще 297)
- **NPNeuronPosCGenerator**: NMultiPositionControl.InputNeuron1-1.PosGenerator, NMultiPositionControl.InputNeuron1-2.PosGenerator, NMultiPositionControl.InputNeuron1-3.PosGenerator, NMultiPositionControl.InputNeuron1-4.PosGenerator, NMultiPositionControl.InputNeuron1-5.PosGenerator (и еще 297)
- **NPSimpleLTZone**: EngineMotionControl.MotionElement0.AfferentR1.LTZone, EngineMotionControl.MotionElement0.AfferentL1.LTZone, EngineMotionControl.MotionElement1.AfferentR1.LTZone, EngineMotionControl.MotionElement1.AfferentL1.LTZone, EngineMotionControl.MotionElement2.AfferentR1.LTZone (и еще 35)
- **NPSynExcChannel**: NMultiPositionControl.InputNeuron1-1.Soma1.ExcChannel, NMultiPositionControl.InputNeuron1-2.Soma1.ExcChannel, NMultiPositionControl.InputNeuron1-3.Soma1.ExcChannel, NMultiPositionControl.InputNeuron1-4.Soma1.ExcChannel, NMultiPositionControl.InputNeuron1-5.Soma1.ExcChannel (и еще 24)
- **NPSynInhChannel**: NMultiPositionControl.InputNeuron1-1.Soma1.InhChannel, NMultiPositionControl.InputNeuron1-2.Soma1.InhChannel, NMultiPositionControl.InputNeuron1-3.Soma1.InhChannel, NMultiPositionControl.InputNeuron1-4.Soma1.InhChannel, NMultiPositionControl.InputNeuron1-5.Soma1.InhChannel (и еще 24)
- **NPSynNeuronMembrane**: NMultiPositionControl.InputNeuron1-1.Soma1, NMultiPositionControl.InputNeuron1-2.Soma1, NMultiPositionControl.InputNeuron1-3.Soma1, NMultiPositionControl.InputNeuron1-4.Soma1, NMultiPositionControl.InputNeuron1-5.Soma1 (и еще 24)
- **NPSynapse**: NMultiPositionControl.InputNeuron1-1.Soma1.ExcSynapse1, NMultiPositionControl.InputNeuron1-1.Soma1.InhSynapse1, NMultiPositionControl.InputNeuron1-1.LTMembrane.ExcSynapse1, NMultiPositionControl.InputNeuron1-1.LTMembrane.InhSynapse1, NMultiPositionControl.InputNeuron1-1.ExcSynapse1 (и еще 2121)
- **NPac**: EngineMotionControl.Pac, EngineMotionControl2.Pac, EngineMotionControl3.Pac, EngineMotionControl4.Pac, Pac
- **NReceptor**: EngineMotionControl.MotionElement0.AfferentR1.Receptor, EngineMotionControl.MotionElement0.AfferentL1.Receptor, EngineMotionControl.MotionElement0.Receptor, EngineMotionControl.MotionElement1.AfferentR1.Receptor, EngineMotionControl.MotionElement1.AfferentL1.Receptor (и еще 55)
- **NSimpleAfferentNeuron**: EngineMotionControl.MotionElement0.AfferentR1, EngineMotionControl.MotionElement0.AfferentL1, EngineMotionControl.MotionElement1.AfferentR1, EngineMotionControl.MotionElement1.AfferentL1, EngineMotionControl.MotionElement2.AfferentR1 (и еще 35)
- **UStatisticDoubleMatrix**: EngineMotionControl.StatisticDoubleMatrix, EngineMotionControl2.StatisticDoubleMatrix, EngineMotionControl3.StatisticDoubleMatrix, EngineMotionControl4.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentL1.LTZone.PGenerator`
- `AfferentL1.PGenerator`
- `AfferentR1.LTZone.PGenerator`
- `AfferentR1.PGenerator`
- `AfferentSource1`
- `ControlNeuron1-1.NegGenerator`
- `ControlNeuron1-1.PosGenerator`
- `ControlNeuron1-2.NegGenerator`
- `ControlNeuron1-2.PosGenerator`
- `ControlNeuron1-3.NegGenerator`
- ... (всего 3128 входов)

**Выходы системы:**
- `DCEngine.OutputAngle`
- `DCEngine2.OutputAngle`
- `DCEngine3.OutputAngle`
- `DCEngine4.OutputAngle`
- `EngineMotionControl.MotionElement0.AfferentL1.LTZone.Output`
- `EngineMotionControl.MotionElement0.AfferentL1.Receptor.Output`
- `EngineMotionControl.MotionElement0.AfferentR1.LTZone.Output`
- `EngineMotionControl.MotionElement0.AfferentR1.Receptor.Output`
- `EngineMotionControl.MotionElement0.MotoneuronL.LTMembrane.ExcChannel.Output`
- `EngineMotionControl.MotionElement0.MotoneuronL.LTMembrane.ExcSynapse1.Output`
- ... (всего 2335 выходов)

**Количество связей:** 2683

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### 4_MultiPositionControl_SoloModeTest

**Путь:** `Bin\Configs\a.demcheva\4_MultiPositionControl_SoloModeTest`

**Назначение:** Система управления движением

**Основные компоненты:**
- **NMultiPositionControl**: NMultiPositionControl2
- **NNewSPNeuron**: NMultiPositionControl2.InputNeuron1-1, NMultiPositionControl2.InputNeuron1-2, NMultiPositionControl2.InputNeuron1-3, NMultiPositionControl2.InputNeuron2-1, NMultiPositionControl2.InputNeuron2-2 (и еще 31)
- **NPExcChannel**: NMultiPositionControl2.InputNeuron1-1.Soma1.ExcChannel, NMultiPositionControl2.InputNeuron1-2.Soma1.ExcChannel, NMultiPositionControl2.InputNeuron1-3.Soma1.ExcChannel, NMultiPositionControl2.InputNeuron2-1.Soma1.ExcChannel, NMultiPositionControl2.InputNeuron2-2.Soma1.ExcChannel (и еще 33)
- **NPGenerator**: PGenerator1-1, PGenerator1-2, PGenerator1-3, PGenerator2-1, PGenerator2-2 (и еще 7)
- **NPInhChannel**: NMultiPositionControl2.InputNeuron1-1.Soma1.InhChannel, NMultiPositionControl2.InputNeuron1-2.Soma1.InhChannel, NMultiPositionControl2.InputNeuron1-3.Soma1.InhChannel, NMultiPositionControl2.InputNeuron2-1.Soma1.InhChannel, NMultiPositionControl2.InputNeuron2-2.Soma1.InhChannel (и еще 33)
- **NPLTExcChannel**: NMultiPositionControl2.InputNeuron1-1.LTMembrane.ExcChannel, NMultiPositionControl2.InputNeuron1-1.ExcChannel, NMultiPositionControl2.InputNeuron1-2.LTMembrane.ExcChannel, NMultiPositionControl2.InputNeuron1-2.ExcChannel, NMultiPositionControl2.InputNeuron1-3.LTMembrane.ExcChannel (и еще 71)
- **NPLTInhChannel**: NMultiPositionControl2.InputNeuron1-1.LTMembrane.InhChannel, NMultiPositionControl2.InputNeuron1-1.InhChannel, NMultiPositionControl2.InputNeuron1-2.LTMembrane.InhChannel, NMultiPositionControl2.InputNeuron1-2.InhChannel, NMultiPositionControl2.InputNeuron1-3.LTMembrane.InhChannel (и еще 71)
- **NPLTZone**: NMultiPositionControl2.InputNeuron1-1.LTZone, NMultiPositionControl2.InputNeuron1-2.LTZone, NMultiPositionControl2.InputNeuron1-3.LTZone, NMultiPositionControl2.InputNeuron2-1.LTZone, NMultiPositionControl2.InputNeuron2-2.LTZone (и еще 33)
- **NPLTZoneNeuronMembrane**: NMultiPositionControl2.InputNeuron1-1.LTMembrane, NMultiPositionControl2.InputNeuron1-2.LTMembrane, NMultiPositionControl2.InputNeuron1-3.LTMembrane, NMultiPositionControl2.InputNeuron2-1.LTMembrane, NMultiPositionControl2.InputNeuron2-2.LTMembrane (и еще 33)
- **NPMembrane**: NMultiPositionControl2.InputNeuron1-1.Soma1, NMultiPositionControl2.InputNeuron1-2.Soma1, NMultiPositionControl2.InputNeuron1-3.Soma1, NMultiPositionControl2.InputNeuron2-1.Soma1, NMultiPositionControl2.InputNeuron2-2.Soma1 (и еще 33)
- **NPNeuronNegCGenerator**: NMultiPositionControl2.InputNeuron1-1.NegGenerator, NMultiPositionControl2.InputNeuron1-2.NegGenerator, NMultiPositionControl2.InputNeuron1-3.NegGenerator, NMultiPositionControl2.InputNeuron2-1.NegGenerator, NMultiPositionControl2.InputNeuron2-2.NegGenerator (и еще 33)
- **NPNeuronPosCGenerator**: NMultiPositionControl2.InputNeuron1-1.PosGenerator, NMultiPositionControl2.InputNeuron1-2.PosGenerator, NMultiPositionControl2.InputNeuron1-3.PosGenerator, NMultiPositionControl2.InputNeuron2-1.PosGenerator, NMultiPositionControl2.InputNeuron2-2.PosGenerator (и еще 33)
- **NPSynapse**: NMultiPositionControl2.InputNeuron1-1.Soma1.ExcSynapse1, NMultiPositionControl2.InputNeuron1-1.Soma1.InhSynapse1, NMultiPositionControl2.InputNeuron1-1.LTMembrane.ExcSynapse1, NMultiPositionControl2.InputNeuron1-1.LTMembrane.InhSynapse1, NMultiPositionControl2.InputNeuron1-1.ExcSynapse1 (и еще 251)

**Входы системы:**
- `ControlNeuron1-1.NegGenerator`
- `ControlNeuron1-1.PosGenerator`
- `ControlNeuron1-2.NegGenerator`
- `ControlNeuron1-2.PosGenerator`
- `ControlNeuron1-3.NegGenerator`
- `ControlNeuron1-3.PosGenerator`
- `ControlNeuron2-1.NegGenerator`
- `ControlNeuron2-1.PosGenerator`
- `ControlNeuron2-2.NegGenerator`
- `ControlNeuron2-2.PosGenerator`
- ... (всего 289 входов)

**Выходы системы:**
- `NMultiPositionControl2.ControlNeuron1-1.LTMembrane.ExcChannel.Output`
- `NMultiPositionControl2.ControlNeuron1-1.LTMembrane.ExcSynapse1.Output`
- `NMultiPositionControl2.ControlNeuron1-1.LTMembrane.InhChannel.Output`
- `NMultiPositionControl2.ControlNeuron1-1.LTMembrane.InhSynapse1.Output`
- `NMultiPositionControl2.ControlNeuron1-1.LTZone.Output`
- `NMultiPositionControl2.ControlNeuron1-1.NegGenerator.Output`
- `NMultiPositionControl2.ControlNeuron1-1.PosGenerator.Output`
- `NMultiPositionControl2.ControlNeuron1-1.Soma1.ExcChannel.Output`
- `NMultiPositionControl2.ControlNeuron1-1.Soma1.ExcSynapse1.Output`
- `NMultiPositionControl2.ControlNeuron1-1.Soma1.InhChannel.Output`
- ... (всего 211 выходов)

**Количество связей:** 223

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### 7_MultiPositionControl_Feedbacks_PostInp-PostInp

**Путь:** `Bin\Configs\a.demcheva\7_MultiPositionControl_Feedbacks_PostInp-PostInp`

**Назначение:** Система управления движением

**Основные компоненты:**
- **NMultiPositionControl**: NMultiPositionControl2
- **NNewSPNeuron**: NMultiPositionControl2.InputNeuron1-1, NMultiPositionControl2.InputNeuron1-2, NMultiPositionControl2.InputNeuron1-3, NMultiPositionControl2.InputNeuron2-1, NMultiPositionControl2.InputNeuron2-2 (и еще 35)
- **NPExcChannel**: NMultiPositionControl2.InputNeuron1-1.Soma1.ExcChannel, NMultiPositionControl2.InputNeuron1-2.Soma1.ExcChannel, NMultiPositionControl2.InputNeuron1-3.Soma1.ExcChannel, NMultiPositionControl2.InputNeuron2-1.Soma1.ExcChannel, NMultiPositionControl2.InputNeuron2-2.Soma1.ExcChannel (и еще 37)
- **NPGenerator**: PGenerator1-1, PGenerator1-2, PGenerator1-3, PGenerator2-1, PGenerator2-2 (и еще 9)
- **NPInhChannel**: NMultiPositionControl2.InputNeuron1-1.Soma1.InhChannel, NMultiPositionControl2.InputNeuron1-2.Soma1.InhChannel, NMultiPositionControl2.InputNeuron1-3.Soma1.InhChannel, NMultiPositionControl2.InputNeuron2-1.Soma1.InhChannel, NMultiPositionControl2.InputNeuron2-2.Soma1.InhChannel (и еще 37)
- **NPLTExcChannel**: NMultiPositionControl2.InputNeuron1-1.LTMembrane.ExcChannel, NMultiPositionControl2.InputNeuron1-1.ExcChannel, NMultiPositionControl2.InputNeuron1-2.LTMembrane.ExcChannel, NMultiPositionControl2.InputNeuron1-2.ExcChannel, NMultiPositionControl2.InputNeuron1-3.LTMembrane.ExcChannel (и еще 79)
- **NPLTInhChannel**: NMultiPositionControl2.InputNeuron1-1.LTMembrane.InhChannel, NMultiPositionControl2.InputNeuron1-1.InhChannel, NMultiPositionControl2.InputNeuron1-2.LTMembrane.InhChannel, NMultiPositionControl2.InputNeuron1-2.InhChannel, NMultiPositionControl2.InputNeuron1-3.LTMembrane.InhChannel (и еще 79)
- **NPLTZone**: NMultiPositionControl2.InputNeuron1-1.LTZone, NMultiPositionControl2.InputNeuron1-2.LTZone, NMultiPositionControl2.InputNeuron1-3.LTZone, NMultiPositionControl2.InputNeuron2-1.LTZone, NMultiPositionControl2.InputNeuron2-2.LTZone (и еще 37)
- **NPLTZoneNeuronMembrane**: NMultiPositionControl2.InputNeuron1-1.LTMembrane, NMultiPositionControl2.InputNeuron1-2.LTMembrane, NMultiPositionControl2.InputNeuron1-3.LTMembrane, NMultiPositionControl2.InputNeuron2-1.LTMembrane, NMultiPositionControl2.InputNeuron2-2.LTMembrane (и еще 37)
- **NPMembrane**: NMultiPositionControl2.InputNeuron1-1.Soma1, NMultiPositionControl2.InputNeuron1-2.Soma1, NMultiPositionControl2.InputNeuron1-3.Soma1, NMultiPositionControl2.InputNeuron2-1.Soma1, NMultiPositionControl2.InputNeuron2-2.Soma1 (и еще 37)
- **NPNeuronNegCGenerator**: NMultiPositionControl2.InputNeuron1-1.NegGenerator, NMultiPositionControl2.InputNeuron1-2.NegGenerator, NMultiPositionControl2.InputNeuron1-3.NegGenerator, NMultiPositionControl2.InputNeuron2-1.NegGenerator, NMultiPositionControl2.InputNeuron2-2.NegGenerator (и еще 37)
- **NPNeuronPosCGenerator**: NMultiPositionControl2.InputNeuron1-1.PosGenerator, NMultiPositionControl2.InputNeuron1-2.PosGenerator, NMultiPositionControl2.InputNeuron1-3.PosGenerator, NMultiPositionControl2.InputNeuron2-1.PosGenerator, NMultiPositionControl2.InputNeuron2-2.PosGenerator (и еще 37)
- **NPSynapse**: NMultiPositionControl2.InputNeuron1-1.Soma1.ExcSynapse1, NMultiPositionControl2.InputNeuron1-1.Soma1.InhSynapse1, NMultiPositionControl2.InputNeuron1-1.LTMembrane.ExcSynapse1, NMultiPositionControl2.InputNeuron1-1.LTMembrane.InhSynapse1, NMultiPositionControl2.InputNeuron1-1.ExcSynapse1 (и еще 447)

**Входы системы:**
- `ControlNeuron1-1.NegGenerator`
- `ControlNeuron1-1.PosGenerator`
- `ControlNeuron1-2.NegGenerator`
- `ControlNeuron1-2.PosGenerator`
- `ControlNeuron1-3.NegGenerator`
- `ControlNeuron1-3.PosGenerator`
- `ControlNeuron2-1.NegGenerator`
- `ControlNeuron2-1.PosGenerator`
- `ControlNeuron2-2.NegGenerator`
- `ControlNeuron2-2.PosGenerator`
- ... (всего 344 входов)

**Выходы системы:**
- `NMultiPositionControl2.ControlNeuron1-1.LTMembrane.ExcChannel.Output`
- `NMultiPositionControl2.ControlNeuron1-1.LTMembrane.ExcSynapse1.Output`
- `NMultiPositionControl2.ControlNeuron1-1.LTMembrane.InhChannel.Output`
- `NMultiPositionControl2.ControlNeuron1-1.LTMembrane.InhSynapse1.Output`
- `NMultiPositionControl2.ControlNeuron1-1.LTZone.Output`
- `NMultiPositionControl2.ControlNeuron1-1.NegGenerator.Output`
- `NMultiPositionControl2.ControlNeuron1-1.PosGenerator.Output`
- `NMultiPositionControl2.ControlNeuron1-1.Soma1.ExcChannel.Output`
- `NMultiPositionControl2.ControlNeuron1-1.Soma1.ExcSynapse1.Output`
- `NMultiPositionControl2.ControlNeuron1-1.Soma1.ExcSynapse2.Output`
- ... (всего 263 выходов)

**Количество связей:** 299

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### 8_MultiPositionControl_Tresholds+Normalization

**Путь:** `Bin\Configs\a.demcheva\8_MultiPositionControl_Tresholds+Normalization`

**Назначение:** Система управления движением

**Основные компоненты:**
- **NMultiPositionControl**: NMultiPositionControl_woNorm2, NMultiPositionControl_withNorm3
- **NPExcChannelBio**: NMultiPositionControl_woNorm2.InputNeuron1-1.Soma1.ExcChannel, NMultiPositionControl_woNorm2.InputNeuron1-1.ExcChannel, NMultiPositionControl_woNorm2.InputNeuron1-2.Soma1.ExcChannel, NMultiPositionControl_woNorm2.InputNeuron1-2.ExcChannel, NMultiPositionControl_woNorm2.InputNeuron1-3.Soma1.ExcChannel (и еще 147)
- **NPGenerator**: PGenerator1-1, PGenerator1-2, PGenerator1-3, PGenerator2-1, PGenerator2-2 (и еще 13)
- **NPInhChannelBio**: NMultiPositionControl_woNorm2.InputNeuron1-1.Soma1.InhChannel, NMultiPositionControl_woNorm2.InputNeuron1-1.InhChannel, NMultiPositionControl_woNorm2.InputNeuron1-2.Soma1.InhChannel, NMultiPositionControl_woNorm2.InputNeuron1-2.InhChannel, NMultiPositionControl_woNorm2.InputNeuron1-3.Soma1.InhChannel (и еще 147)
- **NPMembraneBio**: NMultiPositionControl_woNorm2.InputNeuron1-1.Soma1, NMultiPositionControl_woNorm2.InputNeuron1-2.Soma1, NMultiPositionControl_woNorm2.InputNeuron1-3.Soma1, NMultiPositionControl_woNorm2.InputNeuron2-1.Soma1, NMultiPositionControl_woNorm2.InputNeuron2-2.Soma1 (и еще 84)
- **NPNeuronNegCGenerator**: NMultiPositionControl_woNorm2.InputNeuron1-1.NegGenerator, NMultiPositionControl_woNorm2.InputNeuron1-2.NegGenerator, NMultiPositionControl_woNorm2.InputNeuron1-3.NegGenerator, NMultiPositionControl_woNorm2.InputNeuron2-1.NegGenerator, NMultiPositionControl_woNorm2.InputNeuron2-2.NegGenerator (и еще 58)
- **NPNeuronPosCGenerator**: NMultiPositionControl_woNorm2.InputNeuron1-1.PosGenerator, NMultiPositionControl_woNorm2.InputNeuron1-2.PosGenerator, NMultiPositionControl_woNorm2.InputNeuron1-3.PosGenerator, NMultiPositionControl_woNorm2.InputNeuron2-1.PosGenerator, NMultiPositionControl_woNorm2.InputNeuron2-2.PosGenerator (и еще 58)
- **NPSynapseBio**: NMultiPositionControl_woNorm2.InputNeuron1-1.Soma1.ExcSynapse1, NMultiPositionControl_woNorm2.InputNeuron1-1.Soma1.InhSynapse1, NMultiPositionControl_woNorm2.InputNeuron1-1.ExcSynapse1, NMultiPositionControl_woNorm2.InputNeuron1-1.InhSynapse1, NMultiPositionControl_woNorm2.InputNeuron1-2.Soma1.ExcSynapse1 (и еще 539)
- **NPulseLTZoneThreshold**: NMultiPositionControl_woNorm2.InputNeuron1-1.LTZone, NMultiPositionControl_woNorm2.InputNeuron1-2.LTZone, NMultiPositionControl_woNorm2.InputNeuron1-3.LTZone, NMultiPositionControl_woNorm2.InputNeuron2-1.LTZone, NMultiPositionControl_woNorm2.InputNeuron2-2.LTZone (и еще 58)
- **NSPNeuronGen**: NMultiPositionControl_woNorm2.InputNeuron1-1, NMultiPositionControl_woNorm2.InputNeuron1-2, NMultiPositionControl_woNorm2.InputNeuron1-3, NMultiPositionControl_woNorm2.InputNeuron2-1, NMultiPositionControl_woNorm2.InputNeuron2-2 (и еще 55)

**Входы системы:**
- `ControlNeuron1-1.NegGenerator`
- `ControlNeuron1-1.PosGenerator`
- `ControlNeuron1-2.NegGenerator`
- `ControlNeuron1-2.PosGenerator`
- `ControlNeuron1-3.NegGenerator`
- `ControlNeuron1-3.PosGenerator`
- `ControlNeuron2-1.NegGenerator`
- `ControlNeuron2-1.PosGenerator`
- `ControlNeuron2-2.NegGenerator`
- `ControlNeuron2-2.PosGenerator`
- ... (всего 492 входов)

**Выходы системы:**
- `NMultiPositionControl_withNorm3.ControlNeuron1-1.LTZone.Output`
- `NMultiPositionControl_withNorm3.ControlNeuron1-1.NegGenerator.Output`
- `NMultiPositionControl_withNorm3.ControlNeuron1-1.PosGenerator.Output`
- `NMultiPositionControl_withNorm3.ControlNeuron1-1.Soma1.ExcChannel.Output`
- `NMultiPositionControl_withNorm3.ControlNeuron1-1.Soma1.ExcSynapse1.Output`
- `NMultiPositionControl_withNorm3.ControlNeuron1-1.Soma1.ExcSynapse2.Output`
- `NMultiPositionControl_withNorm3.ControlNeuron1-1.Soma1.InhChannel.Output`
- `NMultiPositionControl_withNorm3.ControlNeuron1-1.Soma1.InhSynapse1.Output`
- `NMultiPositionControl_withNorm3.ControlNeuron1-2.LTZone.Output`
- `NMultiPositionControl_withNorm3.ControlNeuron1-2.NegGenerator.Output`
- ... (всего 376 выходов)

**Количество связей:** 454

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### 9_TrajectoryElement_SimpleTest

**Путь:** `Bin\Configs\a.demcheva\9_TrajectoryElement_SimpleTest`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NMultiPositionControl**: NMultiPositionControl, NMultiPositionControl2, NMultiPositionControl3
- **NPExcChannelBio**: NMultiPositionControl.InputNeuron1-1.Soma1.ExcChannel, NMultiPositionControl.InputNeuron1-1.ExcChannel, NMultiPositionControl.ControlNeuron1-1.Soma1.ExcChannel, NMultiPositionControl.ControlNeuron1-1.ExcChannel, NMultiPositionControl.PreControlNeuron1.Soma1.ExcChannel (и еще 109)
- **NPGenerator**: NMultiPositionControl.PGenerator1, NMultiPositionControl2.PGenerator1, NMultiPositionControl3.PGenerator1, U_top_0, Point1 (и еще 3)
- **NPInhChannelBio**: NMultiPositionControl.InputNeuron1-1.Soma1.InhChannel, NMultiPositionControl.InputNeuron1-1.InhChannel, NMultiPositionControl.ControlNeuron1-1.Soma1.InhChannel, NMultiPositionControl.ControlNeuron1-1.InhChannel, NMultiPositionControl.PreControlNeuron1.Soma1.InhChannel (и еще 109)
- **NPMembraneBio**: NMultiPositionControl.InputNeuron1-1.Soma1, NMultiPositionControl.ControlNeuron1-1.Soma1, NMultiPositionControl.PreControlNeuron1.Soma1, NMultiPositionControl.PostInputNeuron1.Soma1, NMultiPositionControl.Soma1 (и еще 78)
- **NPNeuronNegCGenerator**: NMultiPositionControl.InputNeuron1-1.NegGenerator, NMultiPositionControl.ControlNeuron1-1.NegGenerator, NMultiPositionControl.PreControlNeuron1.NegGenerator, NMultiPositionControl.PostInputNeuron1.NegGenerator, NMultiPositionControl.NegGenerator (и еще 26)
- **NPNeuronPosCGenerator**: NMultiPositionControl.InputNeuron1-1.PosGenerator, NMultiPositionControl.ControlNeuron1-1.PosGenerator, NMultiPositionControl.PreControlNeuron1.PosGenerator, NMultiPositionControl.PostInputNeuron1.PosGenerator, NMultiPositionControl.PosGenerator (и еще 26)
- **NPSynapseBio**: NMultiPositionControl.InputNeuron1-1.Soma1.ExcSynapse1, NMultiPositionControl.InputNeuron1-1.Soma1.InhSynapse1, NMultiPositionControl.InputNeuron1-1.ExcSynapse1, NMultiPositionControl.InputNeuron1-1.InhSynapse1, NMultiPositionControl.ControlNeuron1-1.Soma1.ExcSynapse1 (и еще 223)
- **NPulseLTZoneThreshold**: NMultiPositionControl.InputNeuron1-1.LTZone, NMultiPositionControl.ControlNeuron1-1.LTZone, NMultiPositionControl.PreControlNeuron1.LTZone, NMultiPositionControl.PostInputNeuron1.LTZone, NMultiPositionControl.LTZone (и еще 26)
- **NSPNeuronGen**: NMultiPositionControl.InputNeuron1-1, NMultiPositionControl.ControlNeuron1-1, NMultiPositionControl.PreControlNeuron1, NMultiPositionControl.PostInputNeuron1, NMultiPositionControl2.InputNeuron1-1 (и еще 19)
- **NTrajectoryElement**: NTrajectoryElement, NTrajectoryElement2, NTrajectoryElement3

**Входы системы:**
- `ControlNeuron1-1.NegGenerator`
- `ControlNeuron1-1.PosGenerator`
- `InputNeuron1-1.NegGenerator`
- `InputNeuron1-1.PosGenerator`
- `NMultiPositionControl.ControlNeuron1-1.LTZone.Inputs`
- `NMultiPositionControl.ControlNeuron1-1.NegGenerator`
- `NMultiPositionControl.ControlNeuron1-1.PosGenerator`
- `NMultiPositionControl.ControlNeuron1-1.Soma1.ExcChannel.ChannelInputs`
- `NMultiPositionControl.ControlNeuron1-1.Soma1.ExcChannel.SynapticInputs`
- `NMultiPositionControl.ControlNeuron1-1.Soma1.ExcSynapse1.Input`
- ... (всего 314 входов)

**Выходы системы:**
- `NMultiPositionControl.ControlNeuron1-1.LTZone.Output`
- `NMultiPositionControl.ControlNeuron1-1.NegGenerator.Output`
- `NMultiPositionControl.ControlNeuron1-1.PosGenerator.Output`
- `NMultiPositionControl.ControlNeuron1-1.Soma1.ExcChannel.Output`
- `NMultiPositionControl.ControlNeuron1-1.Soma1.ExcSynapse1.Output`
- `NMultiPositionControl.ControlNeuron1-1.Soma1.InhChannel.Output`
- `NMultiPositionControl.ControlNeuron1-1.Soma1.InhSynapse1.Output`
- `NMultiPositionControl.InputNeuron1-1.LTZone.Output`
- `NMultiPositionControl.InputNeuron1-1.NegGenerator.Output`
- `NMultiPositionControl.InputNeuron1-1.PosGenerator.Output`
- ... (всего 231 выходов)

**Количество связей:** 262

---

### MultiPC_TwoLevelsTask

**Путь:** `Bin\Configs\a.demcheva\MultiPC_TwoLevelsTask`

**Назначение:** Конфигурационный проект (назначение определяется по структуре компонентов)

**Основные компоненты:**
- **NMultiPositionControl**: NMultiPC_Objects3, NMultiPC_Rooms2
- **NPExcChannelBio**: NMultiPC_Objects3.InputNeuron1-1.Soma1.ExcChannel, NMultiPC_Objects3.InputNeuron1-1.ExcChannel, NMultiPC_Objects3.InputNeuron1-2.Soma1.ExcChannel, NMultiPC_Objects3.InputNeuron1-2.ExcChannel, NMultiPC_Objects3.InputNeuron1-3.Soma1.ExcChannel (и еще 299)
- **NPGenerator**: Wood, Plastic, Glass, Textile, Paper (и еще 34)
- **NPInhChannelBio**: NMultiPC_Objects3.InputNeuron1-1.Soma1.InhChannel, NMultiPC_Objects3.InputNeuron1-1.InhChannel, NMultiPC_Objects3.InputNeuron1-2.Soma1.InhChannel, NMultiPC_Objects3.InputNeuron1-2.InhChannel, NMultiPC_Objects3.InputNeuron1-3.Soma1.InhChannel (и еще 299)
- **NPMembraneBio**: NMultiPC_Objects3.InputNeuron1-1.Soma1, NMultiPC_Objects3.InputNeuron1-2.Soma1, NMultiPC_Objects3.InputNeuron1-3.Soma1, NMultiPC_Objects3.InputNeuron1-4.Soma1, NMultiPC_Objects3.InputNeuron1-5.Soma1 (и еще 190)
- **NPNeuronNegCGenerator**: NMultiPC_Objects3.InputNeuron1-1.NegGenerator, NMultiPC_Objects3.InputNeuron1-2.NegGenerator, NMultiPC_Objects3.InputNeuron1-3.NegGenerator, NMultiPC_Objects3.InputNeuron1-4.NegGenerator, NMultiPC_Objects3.InputNeuron1-5.NegGenerator (и еще 104)
- **NPNeuronPosCGenerator**: NMultiPC_Objects3.InputNeuron1-1.PosGenerator, NMultiPC_Objects3.InputNeuron1-2.PosGenerator, NMultiPC_Objects3.InputNeuron1-3.PosGenerator, NMultiPC_Objects3.InputNeuron1-4.PosGenerator, NMultiPC_Objects3.InputNeuron1-5.PosGenerator (и еще 104)
- **NPSynapseBio**: NMultiPC_Objects3.InputNeuron1-1.Soma1.ExcSynapse1, NMultiPC_Objects3.InputNeuron1-1.Soma1.InhSynapse1, NMultiPC_Objects3.InputNeuron1-1.ExcSynapse1, NMultiPC_Objects3.InputNeuron1-1.InhSynapse1, NMultiPC_Objects3.InputNeuron1-2.Soma1.ExcSynapse1 (и еще 949)
- **NPulseLTZoneThreshold**: NMultiPC_Objects3.InputNeuron1-1.LTZone, NMultiPC_Objects3.InputNeuron1-2.LTZone, NMultiPC_Objects3.InputNeuron1-3.LTZone, NMultiPC_Objects3.InputNeuron1-4.LTZone, NMultiPC_Objects3.InputNeuron1-5.LTZone (и еще 104)
- **NSPNeuronGen**: NMultiPC_Objects3.InputNeuron1-1, NMultiPC_Objects3.InputNeuron1-2, NMultiPC_Objects3.InputNeuron1-3, NMultiPC_Objects3.InputNeuron1-4, NMultiPC_Objects3.InputNeuron1-5 (и еще 101)

**Входы системы:**
- `Armchair`
- `Bench`
- `Black`
- `Blue`
- `Brown`
- `Chair`
- `ControlNeuron1-1.NegGenerator`
- `ControlNeuron1-1.PosGenerator`
- `ControlNeuron1-2.NegGenerator`
- `ControlNeuron1-2.PosGenerator`
- ... (всего 949 входов)

**Выходы системы:**
- `Black.Output`
- `Blue.Output`
- `Brown.Output`
- `Glass.Output`
- `Green.Output`
- `Grey.Output`
- `Metal.Output`
- `NMultiPC_Objects3.ControlNeuron1-1.LTZone.Output`
- `NMultiPC_Objects3.ControlNeuron1-1.NegGenerator.Output`
- `NMultiPC_Objects3.ControlNeuron1-1.PosGenerator.Output`
- ... (всего 674 выходов)

**Количество связей:** 902

---

### MultiPositionControl_RememberStateTest

**Путь:** `Bin\Configs\a.demcheva\MultiPositionControl_RememberStateTest`

**Назначение:** Система управления движением

**Основные компоненты:**
- **NCGenerator**: EngineMotionControl.AfferentSource1, EngineMotionControl2.AfferentSource1, EngineMotionControl3.AfferentSource1, EngineMotionControl4.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineMotionControl.NManipulatorSource1, EngineMotionControl2.NManipulatorSource1, EngineMotionControl3.NManipulatorSource1, EngineMotionControl4.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine, DCEngine2, DCEngine3, DCEngine4
- **NEngineMotionControl**: EngineMotionControl, EngineMotionControl2, EngineMotionControl3, EngineMotionControl4
- **NIntervalSeparator**: EngineMotionControl.NegIntervalSeparator11, EngineMotionControl.PosIntervalSeparator11, EngineMotionControl.NegIntervalSeparator21, EngineMotionControl.PosIntervalSeparator21, EngineMotionControl.NegIntervalSeparator31 (и еще 25)
- **NManipulatorInput**: EngineMotionControl.NManipulatorInput1, EngineMotionControl2.NManipulatorInput1, EngineMotionControl3.NManipulatorInput1, EngineMotionControl4.NManipulatorInput1, NManipulatorInput1
- **NMultiPositionControl**: NMultiPositionControl, NMultiPositionControl2, NMultiPositionControl3, NMultiPositionControl4
- **NNewMotionElement**: EngineMotionControl.MotionElement0, EngineMotionControl.MotionElement1, EngineMotionControl.MotionElement2, EngineMotionControl2.MotionElement0, EngineMotionControl2.MotionElement1 (и еще 10)
- **NNewPositionControlElement**: NNewPositionControlElement, NNewPositionControlElement2, NNewPositionControlElement3, NNewPositionControlElement4
- **NNewSPNeuron**: NMultiPositionControl.InputNeuron1-1, NMultiPositionControl.InputNeuron1-2, NMultiPositionControl.InputNeuron1-3, NMultiPositionControl.InputNeuron1-4, NMultiPositionControl.InputNeuron1-5 (и еще 333)
- **NPExcChannel**: NMultiPositionControl.InputNeuron1-1.Soma1.ExcChannel, NMultiPositionControl.InputNeuron1-2.Soma1.ExcChannel, NMultiPositionControl.InputNeuron1-3.Soma1.ExcChannel, NMultiPositionControl.InputNeuron1-4.Soma1.ExcChannel, NMultiPositionControl.InputNeuron1-5.Soma1.ExcChannel (и еще 361)
- **NPGenerator**: NMultiPositionControl.PGenerator1, NMultiPositionControl.PGenerator2, NMultiPositionControl.PGenerator3, EngineMotionControl.IIPosAfferentGenerator, EngineMotionControl.IINegAfferentGenerator (и еще 169)
- **NPInhChannel**: NMultiPositionControl.InputNeuron1-1.Soma1.InhChannel, NMultiPositionControl.InputNeuron1-2.Soma1.InhChannel, NMultiPositionControl.InputNeuron1-3.Soma1.InhChannel, NMultiPositionControl.InputNeuron1-4.Soma1.InhChannel, NMultiPositionControl.InputNeuron1-5.Soma1.InhChannel (и еще 361)
- **NPLTExcChannel**: NMultiPositionControl.InputNeuron1-1.LTMembrane.ExcChannel, NMultiPositionControl.InputNeuron1-1.ExcChannel, NMultiPositionControl.InputNeuron1-2.LTMembrane.ExcChannel, NMultiPositionControl.InputNeuron1-2.ExcChannel, NMultiPositionControl.InputNeuron1-3.LTMembrane.ExcChannel (и еще 727)
- **NPLTInhChannel**: NMultiPositionControl.InputNeuron1-1.LTMembrane.InhChannel, NMultiPositionControl.InputNeuron1-1.InhChannel, NMultiPositionControl.InputNeuron1-2.LTMembrane.InhChannel, NMultiPositionControl.InputNeuron1-2.InhChannel, NMultiPositionControl.InputNeuron1-3.LTMembrane.InhChannel (и еще 727)
- **NPLTZone**: NMultiPositionControl.InputNeuron1-1.LTZone, NMultiPositionControl.InputNeuron1-2.LTZone, NMultiPositionControl.InputNeuron1-3.LTZone, NMultiPositionControl.InputNeuron1-4.LTZone, NMultiPositionControl.InputNeuron1-5.LTZone (и еще 361)
- **NPLTZoneNeuronMembrane**: NMultiPositionControl.InputNeuron1-1.LTMembrane, NMultiPositionControl.InputNeuron1-2.LTMembrane, NMultiPositionControl.InputNeuron1-3.LTMembrane, NMultiPositionControl.InputNeuron1-4.LTMembrane, NMultiPositionControl.InputNeuron1-5.LTMembrane (и еще 361)
- **NPMembrane**: NMultiPositionControl.InputNeuron1-1.Soma1, NMultiPositionControl.InputNeuron1-2.Soma1, NMultiPositionControl.InputNeuron1-3.Soma1, NMultiPositionControl.InputNeuron1-4.Soma1, NMultiPositionControl.InputNeuron1-5.Soma1 (и еще 361)
- **NPNeuronNegCGenerator**: NMultiPositionControl.InputNeuron1-1.NegGenerator, NMultiPositionControl.InputNeuron1-2.NegGenerator, NMultiPositionControl.InputNeuron1-3.NegGenerator, NMultiPositionControl.InputNeuron1-4.NegGenerator, NMultiPositionControl.InputNeuron1-5.NegGenerator (и еще 361)
- **NPNeuronPosCGenerator**: NMultiPositionControl.InputNeuron1-1.PosGenerator, NMultiPositionControl.InputNeuron1-2.PosGenerator, NMultiPositionControl.InputNeuron1-3.PosGenerator, NMultiPositionControl.InputNeuron1-4.PosGenerator, NMultiPositionControl.InputNeuron1-5.PosGenerator (и еще 361)
- **NPSimpleLTZone**: EngineMotionControl.MotionElement0.AfferentR1.LTZone, EngineMotionControl.MotionElement0.AfferentL1.LTZone, EngineMotionControl.MotionElement1.AfferentR1.LTZone, EngineMotionControl.MotionElement1.AfferentL1.LTZone, EngineMotionControl.MotionElement2.AfferentR1.LTZone (и еще 35)
- **NPSynapse**: NMultiPositionControl.InputNeuron1-1.Soma1.ExcSynapse1, NMultiPositionControl.InputNeuron1-1.Soma1.InhSynapse1, NMultiPositionControl.InputNeuron1-1.LTMembrane.ExcSynapse1, NMultiPositionControl.InputNeuron1-1.LTMembrane.InhSynapse1, NMultiPositionControl.InputNeuron1-1.ExcSynapse1 (и еще 2581)
- **NPac**: EngineMotionControl.Pac, EngineMotionControl2.Pac, EngineMotionControl3.Pac, EngineMotionControl4.Pac, Pac
- **NReceptor**: EngineMotionControl.MotionElement0.AfferentR1.Receptor, EngineMotionControl.MotionElement0.AfferentL1.Receptor, EngineMotionControl.MotionElement0.Receptor, EngineMotionControl.MotionElement1.AfferentR1.Receptor, EngineMotionControl.MotionElement1.AfferentL1.Receptor (и еще 55)
- **NSimpleAfferentNeuron**: EngineMotionControl.MotionElement0.AfferentR1, EngineMotionControl.MotionElement0.AfferentL1, EngineMotionControl.MotionElement1.AfferentR1, EngineMotionControl.MotionElement1.AfferentL1, EngineMotionControl.MotionElement2.AfferentR1 (и еще 35)
- **UStatisticDoubleMatrix**: EngineMotionControl.StatisticDoubleMatrix, EngineMotionControl2.StatisticDoubleMatrix, EngineMotionControl3.StatisticDoubleMatrix, EngineMotionControl4.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentL1.LTZone.PGenerator`
- `AfferentL1.PGenerator`
- `AfferentR1.LTZone.PGenerator`
- `AfferentR1.PGenerator`
- `AfferentSource1`
- `ControlNeuron1-1.NegGenerator`
- `ControlNeuron1-1.PosGenerator`
- `ControlNeuron1-2.NegGenerator`
- `ControlNeuron1-2.PosGenerator`
- `ControlNeuron1-3.NegGenerator`
- ... (всего 3897 входов)

**Выходы системы:**
- `DCEngine.OutputAngle`
- `DCEngine2.OutputAngle`
- `DCEngine3.OutputAngle`
- `DCEngine4.OutputAngle`
- `EngineMotionControl.MotionElement0.AfferentL1.LTZone.Output`
- `EngineMotionControl.MotionElement0.AfferentL1.Receptor.Output`
- `EngineMotionControl.MotionElement0.AfferentR1.LTZone.Output`
- `EngineMotionControl.MotionElement0.AfferentR1.Receptor.Output`
- `EngineMotionControl.MotionElement0.MotoneuronL.LTMembrane.ExcChannel.Output`
- `EngineMotionControl.MotionElement0.MotoneuronL.LTMembrane.ExcSynapse1.Output`
- ... (всего 3003 выходов)

**Количество связей:** 3373

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### MultiPositionControl_SimpleTest

**Путь:** `Bin\Configs\a.demcheva\MultiPositionControl_SimpleTest`

**Назначение:** Система управления движением

**Основные компоненты:**
- **NCGenerator**: EngineMotionControl.AfferentSource1, EngineMotionControl2.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineMotionControl.NManipulatorSource1, EngineMotionControl2.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine, DCEngine2
- **NEngineMotionControl**: EngineMotionControl, EngineMotionControl2
- **NIntervalSeparator**: EngineMotionControl.NegIntervalSeparator11, EngineMotionControl.PosIntervalSeparator11, EngineMotionControl.NegIntervalSeparator21, EngineMotionControl.PosIntervalSeparator21, EngineMotionControl.NegIntervalSeparator31 (и еще 13)
- **NManipulatorInput**: EngineMotionControl.NManipulatorInput1, EngineMotionControl2.NManipulatorInput1, NManipulatorInput1
- **NMultiPositionControl**: NMultiPositionControl
- **NNewMotionElement**: EngineMotionControl.MotionElement0, EngineMotionControl.MotionElement1, EngineMotionControl.MotionElement2, EngineMotionControl2.MotionElement0, EngineMotionControl2.MotionElement1 (и еще 4)
- **NNewPositionControlElement**: NNewPositionControlElement, NNewPositionControlElement2
- **NNewSPNeuron**: EngineMotionControl.MotionElement0.MotoneuronL, EngineMotionControl.MotionElement0.MotoneuronR, EngineMotionControl.MotionElement0.PostAfferentL1, EngineMotionControl.MotionElement0.PostAfferentR1, EngineMotionControl.MotionElement1.MotoneuronL (и еще 115)
- **NNewSynSPNeuron**: NMultiPositionControl.InputNeuron1-1, NMultiPositionControl.InputNeuron1-2, NMultiPositionControl.InputNeuron1-3, NMultiPositionControl.InputNeuron1-4, NMultiPositionControl.InputNeuron1-5 (и еще 47)
- **NPExcChannel**: EngineMotionControl.MotionElement0.MotoneuronL.Soma1.ExcChannel, EngineMotionControl.MotionElement0.MotoneuronR.Soma1.ExcChannel, EngineMotionControl.MotionElement0.PostAfferentL1.Soma1.ExcChannel, EngineMotionControl.MotionElement0.PostAfferentR1.Soma1.ExcChannel, EngineMotionControl.MotionElement0.Soma1.ExcChannel (и еще 129)
- **NPGenerator**: NMultiPositionControl.PGenerator1, EngineMotionControl.IIPosAfferentGenerator, EngineMotionControl.IINegAfferentGenerator, EngineMotionControl.InternalGenerator, EngineMotionControl.MotionElement0.AfferentR1.LTZone.PGenerator (и еще 96)
- **NPInhChannel**: EngineMotionControl.MotionElement0.MotoneuronL.Soma1.InhChannel, EngineMotionControl.MotionElement0.MotoneuronR.Soma1.InhChannel, EngineMotionControl.MotionElement0.PostAfferentL1.Soma1.InhChannel, EngineMotionControl.MotionElement0.PostAfferentR1.Soma1.InhChannel, EngineMotionControl.MotionElement0.Soma1.InhChannel (и еще 129)
- **NPLTExcChannel**: NMultiPositionControl.InputNeuron1-1.LTMembrane.ExcChannel, NMultiPositionControl.InputNeuron1-1.ExcChannel, NMultiPositionControl.InputNeuron1-2.LTMembrane.ExcChannel, NMultiPositionControl.InputNeuron1-2.ExcChannel, NMultiPositionControl.InputNeuron1-3.LTMembrane.ExcChannel (и еще 369)
- **NPLTInhChannel**: NMultiPositionControl.InputNeuron1-1.LTMembrane.InhChannel, NMultiPositionControl.InputNeuron1-1.InhChannel, NMultiPositionControl.InputNeuron1-2.LTMembrane.InhChannel, NMultiPositionControl.InputNeuron1-2.InhChannel, NMultiPositionControl.InputNeuron1-3.LTMembrane.InhChannel (и еще 369)
- **NPLTZone**: NMultiPositionControl.InputNeuron1-1.LTZone, NMultiPositionControl.InputNeuron1-2.LTZone, NMultiPositionControl.InputNeuron1-3.LTZone, NMultiPositionControl.InputNeuron1-4.LTZone, NMultiPositionControl.InputNeuron1-5.LTZone (и еще 182)
- **NPLTZoneNeuronMembrane**: NMultiPositionControl.InputNeuron1-1.LTMembrane, NMultiPositionControl.InputNeuron1-2.LTMembrane, NMultiPositionControl.InputNeuron1-3.LTMembrane, NMultiPositionControl.InputNeuron1-4.LTMembrane, NMultiPositionControl.InputNeuron1-5.LTMembrane (и еще 182)
- **NPMembrane**: EngineMotionControl.MotionElement0.MotoneuronL.Soma1, EngineMotionControl.MotionElement0.MotoneuronR.Soma1, EngineMotionControl.MotionElement0.PostAfferentL1.Soma1, EngineMotionControl.MotionElement0.PostAfferentR1.Soma1, EngineMotionControl.MotionElement0.Soma1 (и еще 129)
- **NPNeuronNegCGenerator**: NMultiPositionControl.InputNeuron1-1.NegGenerator, NMultiPositionControl.InputNeuron1-2.NegGenerator, NMultiPositionControl.InputNeuron1-3.NegGenerator, NMultiPositionControl.InputNeuron1-4.NegGenerator, NMultiPositionControl.InputNeuron1-5.NegGenerator (и еще 182)
- **NPNeuronPosCGenerator**: NMultiPositionControl.InputNeuron1-1.PosGenerator, NMultiPositionControl.InputNeuron1-2.PosGenerator, NMultiPositionControl.InputNeuron1-3.PosGenerator, NMultiPositionControl.InputNeuron1-4.PosGenerator, NMultiPositionControl.InputNeuron1-5.PosGenerator (и еще 182)
- **NPSimpleLTZone**: EngineMotionControl.MotionElement0.AfferentR1.LTZone, EngineMotionControl.MotionElement0.AfferentL1.LTZone, EngineMotionControl.MotionElement1.AfferentR1.LTZone, EngineMotionControl.MotionElement1.AfferentL1.LTZone, EngineMotionControl.MotionElement2.AfferentR1.LTZone (и еще 19)
- **NPSynExcChannel**: NMultiPositionControl.InputNeuron1-1.Soma1.ExcChannel, NMultiPositionControl.InputNeuron1-2.Soma1.ExcChannel, NMultiPositionControl.InputNeuron1-3.Soma1.ExcChannel, NMultiPositionControl.InputNeuron1-4.Soma1.ExcChannel, NMultiPositionControl.InputNeuron1-5.Soma1.ExcChannel (и еще 48)
- **NPSynInhChannel**: NMultiPositionControl.InputNeuron1-1.Soma1.InhChannel, NMultiPositionControl.InputNeuron1-2.Soma1.InhChannel, NMultiPositionControl.InputNeuron1-3.Soma1.InhChannel, NMultiPositionControl.InputNeuron1-4.Soma1.InhChannel, NMultiPositionControl.InputNeuron1-5.Soma1.InhChannel (и еще 48)
- **NPSynNeuronMembrane**: NMultiPositionControl.InputNeuron1-1.Soma1, NMultiPositionControl.InputNeuron1-2.Soma1, NMultiPositionControl.InputNeuron1-3.Soma1, NMultiPositionControl.InputNeuron1-4.Soma1, NMultiPositionControl.InputNeuron1-5.Soma1 (и еще 48)
- **NPSynapse**: NMultiPositionControl.InputNeuron1-1.Soma1.ExcSynapse1, NMultiPositionControl.InputNeuron1-1.Soma1.InhSynapse1, NMultiPositionControl.InputNeuron1-1.LTMembrane.ExcSynapse1, NMultiPositionControl.InputNeuron1-1.LTMembrane.InhSynapse1, NMultiPositionControl.InputNeuron1-1.ExcSynapse1 (и еще 1283)
- **NPac**: EngineMotionControl.Pac, EngineMotionControl2.Pac, Pac
- **NReceptor**: EngineMotionControl.MotionElement0.AfferentR1.Receptor, EngineMotionControl.MotionElement0.AfferentL1.Receptor, EngineMotionControl.MotionElement0.Receptor, EngineMotionControl.MotionElement1.AfferentR1.Receptor, EngineMotionControl.MotionElement1.AfferentL1.Receptor (и еще 31)
- **NSimpleAfferentNeuron**: EngineMotionControl.MotionElement0.AfferentR1, EngineMotionControl.MotionElement0.AfferentL1, EngineMotionControl.MotionElement1.AfferentR1, EngineMotionControl.MotionElement1.AfferentL1, EngineMotionControl.MotionElement2.AfferentR1 (и еще 19)
- **UStatisticDoubleMatrix**: EngineMotionControl.StatisticDoubleMatrix, EngineMotionControl2.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentL1.LTZone.PGenerator`
- `AfferentL1.PGenerator`
- `AfferentR1.LTZone.PGenerator`
- `AfferentR1.PGenerator`
- `AfferentSource1`
- `ControlNeuron1-1.NegGenerator`
- `ControlNeuron1-1.PosGenerator`
- `ControlNeuron1-2.NegGenerator`
- `ControlNeuron1-2.PosGenerator`
- `ControlNeuron1-3.NegGenerator`
- ... (всего 1652 входов)

**Выходы системы:**
- `DCEngine.OutputAngle`
- `DCEngine2.OutputAngle`
- `EngineMotionControl.MotionElement0.AfferentL1.LTZone.Output`
- `EngineMotionControl.MotionElement0.AfferentL1.Receptor.Output`
- `EngineMotionControl.MotionElement0.AfferentR1.LTZone.Output`
- `EngineMotionControl.MotionElement0.AfferentR1.Receptor.Output`
- `EngineMotionControl.MotionElement0.MotoneuronL.LTMembrane.ExcChannel.Output`
- `EngineMotionControl.MotionElement0.MotoneuronL.LTMembrane.ExcSynapse1.Output`
- `EngineMotionControl.MotionElement0.MotoneuronL.LTMembrane.InhChannel.Output`
- `EngineMotionControl.MotionElement0.MotoneuronL.LTMembrane.InhSynapse1.Output`
- ... (всего 1173 выходов)

**Количество связей:** 1347

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### MultiPositionControl_SoloModeTest

**Путь:** `Bin\Configs\a.demcheva\MultiPositionControl_SoloModeTest`

**Назначение:** Система управления движением

**Основные компоненты:**
- **NMultiPositionControl**: NMultiPositionControl
- **NNewSPNeuron**: NMultiPositionControl.InputNeuron1-1, NMultiPositionControl.InputNeuron1-2, NMultiPositionControl.InputNeuron1-3, NMultiPositionControl.InputNeuron2-1, NMultiPositionControl.InputNeuron2-2 (и еще 27)
- **NPExcChannel**: NMultiPositionControl.InputNeuron1-1.Soma1.ExcChannel, NMultiPositionControl.InputNeuron1-2.Soma1.ExcChannel, NMultiPositionControl.InputNeuron1-3.Soma1.ExcChannel, NMultiPositionControl.InputNeuron2-1.Soma1.ExcChannel, NMultiPositionControl.InputNeuron2-2.Soma1.ExcChannel (и еще 29)
- **NPGenerator**: NMultiPositionControl.PGenerator1, NMultiPositionControl.PGenerator2, PGenerator1-1, PGenerator1-2, PGenerator1-3 (и еще 5)
- **NPInhChannel**: NMultiPositionControl.InputNeuron1-1.Soma1.InhChannel, NMultiPositionControl.InputNeuron1-2.Soma1.InhChannel, NMultiPositionControl.InputNeuron1-3.Soma1.InhChannel, NMultiPositionControl.InputNeuron2-1.Soma1.InhChannel, NMultiPositionControl.InputNeuron2-2.Soma1.InhChannel (и еще 29)
- **NPLTExcChannel**: NMultiPositionControl.InputNeuron1-1.LTMembrane.ExcChannel, NMultiPositionControl.InputNeuron1-1.ExcChannel, NMultiPositionControl.InputNeuron1-2.LTMembrane.ExcChannel, NMultiPositionControl.InputNeuron1-2.ExcChannel, NMultiPositionControl.InputNeuron1-3.LTMembrane.ExcChannel (и еще 63)
- **NPLTInhChannel**: NMultiPositionControl.InputNeuron1-1.LTMembrane.InhChannel, NMultiPositionControl.InputNeuron1-1.InhChannel, NMultiPositionControl.InputNeuron1-2.LTMembrane.InhChannel, NMultiPositionControl.InputNeuron1-2.InhChannel, NMultiPositionControl.InputNeuron1-3.LTMembrane.InhChannel (и еще 63)
- **NPLTZone**: NMultiPositionControl.InputNeuron1-1.LTZone, NMultiPositionControl.InputNeuron1-2.LTZone, NMultiPositionControl.InputNeuron1-3.LTZone, NMultiPositionControl.InputNeuron2-1.LTZone, NMultiPositionControl.InputNeuron2-2.LTZone (и еще 29)
- **NPLTZoneNeuronMembrane**: NMultiPositionControl.InputNeuron1-1.LTMembrane, NMultiPositionControl.InputNeuron1-2.LTMembrane, NMultiPositionControl.InputNeuron1-3.LTMembrane, NMultiPositionControl.InputNeuron2-1.LTMembrane, NMultiPositionControl.InputNeuron2-2.LTMembrane (и еще 29)
- **NPMembrane**: NMultiPositionControl.InputNeuron1-1.Soma1, NMultiPositionControl.InputNeuron1-2.Soma1, NMultiPositionControl.InputNeuron1-3.Soma1, NMultiPositionControl.InputNeuron2-1.Soma1, NMultiPositionControl.InputNeuron2-2.Soma1 (и еще 29)
- **NPNeuronNegCGenerator**: NMultiPositionControl.InputNeuron1-1.NegGenerator, NMultiPositionControl.InputNeuron1-2.NegGenerator, NMultiPositionControl.InputNeuron1-3.NegGenerator, NMultiPositionControl.InputNeuron2-1.NegGenerator, NMultiPositionControl.InputNeuron2-2.NegGenerator (и еще 29)
- **NPNeuronPosCGenerator**: NMultiPositionControl.InputNeuron1-1.PosGenerator, NMultiPositionControl.InputNeuron1-2.PosGenerator, NMultiPositionControl.InputNeuron1-3.PosGenerator, NMultiPositionControl.InputNeuron2-1.PosGenerator, NMultiPositionControl.InputNeuron2-2.PosGenerator (и еще 29)
- **NPSynapse**: NMultiPositionControl.InputNeuron1-1.Soma1.ExcSynapse1, NMultiPositionControl.InputNeuron1-1.Soma1.InhSynapse1, NMultiPositionControl.InputNeuron1-1.LTMembrane.ExcSynapse1, NMultiPositionControl.InputNeuron1-1.LTMembrane.InhSynapse1, NMultiPositionControl.InputNeuron1-1.ExcSynapse1 (и еще 211)

**Входы системы:**
- `ControlNeuron1-1.NegGenerator`
- `ControlNeuron1-1.PosGenerator`
- `ControlNeuron1-2.NegGenerator`
- `ControlNeuron1-2.PosGenerator`
- `ControlNeuron1-3.NegGenerator`
- `ControlNeuron1-3.PosGenerator`
- `ControlNeuron2-1.NegGenerator`
- `ControlNeuron2-1.PosGenerator`
- `ControlNeuron2-2.NegGenerator`
- `ControlNeuron2-2.PosGenerator`
- ... (всего 254 входов)

**Выходы системы:**
- `NMultiPositionControl.ControlNeuron1-1.LTMembrane.ExcChannel.Output`
- `NMultiPositionControl.ControlNeuron1-1.LTMembrane.ExcSynapse1.Output`
- `NMultiPositionControl.ControlNeuron1-1.LTMembrane.InhChannel.Output`
- `NMultiPositionControl.ControlNeuron1-1.LTMembrane.InhSynapse1.Output`
- `NMultiPositionControl.ControlNeuron1-1.LTZone.Output`
- `NMultiPositionControl.ControlNeuron1-1.NegGenerator.Output`
- `NMultiPositionControl.ControlNeuron1-1.PosGenerator.Output`
- `NMultiPositionControl.ControlNeuron1-1.Soma1.ExcChannel.Output`
- `NMultiPositionControl.ControlNeuron1-1.Soma1.ExcSynapse1.Output`
- `NMultiPositionControl.ControlNeuron1-1.Soma1.InhChannel.Output`
- ... (всего 186 выходов)

**Количество связей:** 194

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### MultiPositionControl_TaskTest

**Путь:** `Bin\Configs\a.demcheva\MultiPositionControl_TaskTest`

**Назначение:** Система управления движением

**Основные компоненты:**
- **NMultiPositionControl**: NMultiPositionControl
- **NNewSPNeuron**: NMultiPositionControl.Sun_IN1-1, NMultiPositionControl.Streetlight_IN1-2, NMultiPositionControl.Desklamp_IN1-3, NMultiPositionControl.Tree_IN2-1, NMultiPositionControl.Grass_IN2-2 (и еще 39)
- **NPExcChannel**: NMultiPositionControl.Sun_IN1-1.Soma1.ExcChannel, NMultiPositionControl.Streetlight_IN1-2.Soma1.ExcChannel, NMultiPositionControl.Desklamp_IN1-3.Soma1.ExcChannel, NMultiPositionControl.Tree_IN2-1.Soma1.ExcChannel, NMultiPositionControl.Grass_IN2-2.Soma1.ExcChannel (и еще 41)
- **NPGenerator**: Sun_1-1, Desklamp_1-3, Streetlight_1-2, Tree_2-1, Houseplant_2-3 (и еще 8)
- **NPInhChannel**: NMultiPositionControl.Sun_IN1-1.Soma1.InhChannel, NMultiPositionControl.Streetlight_IN1-2.Soma1.InhChannel, NMultiPositionControl.Desklamp_IN1-3.Soma1.InhChannel, NMultiPositionControl.Tree_IN2-1.Soma1.InhChannel, NMultiPositionControl.Grass_IN2-2.Soma1.InhChannel (и еще 41)
- **NPLTExcChannel**: NMultiPositionControl.Sun_IN1-1.LTMembrane.ExcChannel, NMultiPositionControl.Sun_IN1-1.ExcChannel, NMultiPositionControl.Streetlight_IN1-2.LTMembrane.ExcChannel, NMultiPositionControl.Streetlight_IN1-2.ExcChannel, NMultiPositionControl.Desklamp_IN1-3.LTMembrane.ExcChannel (и еще 87)
- **NPLTInhChannel**: NMultiPositionControl.Sun_IN1-1.LTMembrane.InhChannel, NMultiPositionControl.Sun_IN1-1.InhChannel, NMultiPositionControl.Streetlight_IN1-2.LTMembrane.InhChannel, NMultiPositionControl.Streetlight_IN1-2.InhChannel, NMultiPositionControl.Desklamp_IN1-3.LTMembrane.InhChannel (и еще 87)
- **NPLTZone**: NMultiPositionControl.Sun_IN1-1.LTZone, NMultiPositionControl.Streetlight_IN1-2.LTZone, NMultiPositionControl.Desklamp_IN1-3.LTZone, NMultiPositionControl.Tree_IN2-1.LTZone, NMultiPositionControl.Grass_IN2-2.LTZone (и еще 41)
- **NPLTZoneNeuronMembrane**: NMultiPositionControl.Sun_IN1-1.LTMembrane, NMultiPositionControl.Streetlight_IN1-2.LTMembrane, NMultiPositionControl.Desklamp_IN1-3.LTMembrane, NMultiPositionControl.Tree_IN2-1.LTMembrane, NMultiPositionControl.Grass_IN2-2.LTMembrane (и еще 41)
- **NPMembrane**: NMultiPositionControl.Sun_IN1-1.Soma1, NMultiPositionControl.Streetlight_IN1-2.Soma1, NMultiPositionControl.Desklamp_IN1-3.Soma1, NMultiPositionControl.Tree_IN2-1.Soma1, NMultiPositionControl.Grass_IN2-2.Soma1 (и еще 41)
- **NPNeuronNegCGenerator**: NMultiPositionControl.Sun_IN1-1.NegGenerator, NMultiPositionControl.Streetlight_IN1-2.NegGenerator, NMultiPositionControl.Desklamp_IN1-3.NegGenerator, NMultiPositionControl.Tree_IN2-1.NegGenerator, NMultiPositionControl.Grass_IN2-2.NegGenerator (и еще 41)
- **NPNeuronPosCGenerator**: NMultiPositionControl.Sun_IN1-1.PosGenerator, NMultiPositionControl.Streetlight_IN1-2.PosGenerator, NMultiPositionControl.Desklamp_IN1-3.PosGenerator, NMultiPositionControl.Tree_IN2-1.PosGenerator, NMultiPositionControl.Grass_IN2-2.PosGenerator (и еще 41)
- **NPSynapse**: NMultiPositionControl.Sun_IN1-1.Soma1.ExcSynapse1, NMultiPositionControl.Sun_IN1-1.Soma1.InhSynapse1, NMultiPositionControl.Sun_IN1-1.LTMembrane.ExcSynapse1, NMultiPositionControl.Sun_IN1-1.LTMembrane.InhSynapse1, NMultiPositionControl.Sun_IN1-1.ExcSynapse1 (и еще 343)

**Входы системы:**
- `Bench_3-1`
- `Bench_CN3-1.NegGenerator`
- `Bench_CN3-1.PosGenerator`
- `Bench_IN3-1.NegGenerator`
- `Bench_IN3-1.PosGenerator`
- `Chair_3-3`
- `Chair_CN3-3.NegGenerator`
- `Chair_CN3-3.PosGenerator`
- `Chair_IN3-3.NegGenerator`
- `Chair_IN3-3.PosGenerator`
- ... (всего 352 входов)

**Выходы системы:**
- `Bench_3-1.Output`
- `Chair_3-3.Output`
- `Desklamp_1-3.Output`
- `Grass_2-2.Output`
- `Houseplant_2-3.Output`
- `NMultiPositionControl.Bench_CN3-1.LTMembrane.ExcChannel.Output`
- `NMultiPositionControl.Bench_CN3-1.LTMembrane.ExcSynapse1.Output`
- `NMultiPositionControl.Bench_CN3-1.LTMembrane.InhChannel.Output`
- `NMultiPositionControl.Bench_CN3-1.LTMembrane.InhSynapse1.Output`
- `NMultiPositionControl.Bench_CN3-1.LTZone.Output`
- ... (всего 265 выходов)

**Количество связей:** 281

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### MultiPositionControl_Test

**Путь:** `Bin\Configs\a.demcheva\MultiPositionControl_Test`

**Назначение:** Система управления движением

**Основные компоненты:**
- **NMultiPositionControl**: NMultiPositionControl, NMultiPositionControl2
- **NNewSPNeuron**: NMultiPositionControl.InputNeuron1-1, NMultiPositionControl.InputNeuron1-2, NMultiPositionControl.InputNeuron1-3, NMultiPositionControl.InputNeuron1-4, NMultiPositionControl.InputNeuron1-5 (и еще 43)
- **NPExcChannel**: NMultiPositionControl.InputNeuron1-1.Soma1.ExcChannel, NMultiPositionControl.InputNeuron1-2.Soma1.ExcChannel, NMultiPositionControl.InputNeuron1-3.Soma1.ExcChannel, NMultiPositionControl.InputNeuron1-4.Soma1.ExcChannel, NMultiPositionControl.InputNeuron1-5.Soma1.ExcChannel (и еще 45)
- **NPGenerator**: PGenerator
- **NPInhChannel**: NMultiPositionControl.InputNeuron1-1.Soma1.InhChannel, NMultiPositionControl.InputNeuron1-2.Soma1.InhChannel, NMultiPositionControl.InputNeuron1-3.Soma1.InhChannel, NMultiPositionControl.InputNeuron1-4.Soma1.InhChannel, NMultiPositionControl.InputNeuron1-5.Soma1.InhChannel (и еще 45)
- **NPLTExcChannel**: NMultiPositionControl.InputNeuron1-1.LTMembrane.ExcChannel, NMultiPositionControl.InputNeuron1-1.ExcChannel, NMultiPositionControl.InputNeuron1-2.LTMembrane.ExcChannel, NMultiPositionControl.InputNeuron1-2.ExcChannel, NMultiPositionControl.InputNeuron1-3.LTMembrane.ExcChannel (и еще 95)
- **NPLTInhChannel**: NMultiPositionControl.InputNeuron1-1.LTMembrane.InhChannel, NMultiPositionControl.InputNeuron1-1.InhChannel, NMultiPositionControl.InputNeuron1-2.LTMembrane.InhChannel, NMultiPositionControl.InputNeuron1-2.InhChannel, NMultiPositionControl.InputNeuron1-3.LTMembrane.InhChannel (и еще 95)
- **NPLTZone**: NMultiPositionControl.InputNeuron1-1.LTZone, NMultiPositionControl.InputNeuron1-2.LTZone, NMultiPositionControl.InputNeuron1-3.LTZone, NMultiPositionControl.InputNeuron1-4.LTZone, NMultiPositionControl.InputNeuron1-5.LTZone (и еще 45)
- **NPLTZoneNeuronMembrane**: NMultiPositionControl.InputNeuron1-1.LTMembrane, NMultiPositionControl.InputNeuron1-2.LTMembrane, NMultiPositionControl.InputNeuron1-3.LTMembrane, NMultiPositionControl.InputNeuron1-4.LTMembrane, NMultiPositionControl.InputNeuron1-5.LTMembrane (и еще 45)
- **NPMembrane**: NMultiPositionControl.InputNeuron1-1.Soma1, NMultiPositionControl.InputNeuron1-2.Soma1, NMultiPositionControl.InputNeuron1-3.Soma1, NMultiPositionControl.InputNeuron1-4.Soma1, NMultiPositionControl.InputNeuron1-5.Soma1 (и еще 45)
- **NPNeuronNegCGenerator**: NMultiPositionControl.InputNeuron1-1.NegGenerator, NMultiPositionControl.InputNeuron1-2.NegGenerator, NMultiPositionControl.InputNeuron1-3.NegGenerator, NMultiPositionControl.InputNeuron1-4.NegGenerator, NMultiPositionControl.InputNeuron1-5.NegGenerator (и еще 45)
- **NPNeuronPosCGenerator**: NMultiPositionControl.InputNeuron1-1.PosGenerator, NMultiPositionControl.InputNeuron1-2.PosGenerator, NMultiPositionControl.InputNeuron1-3.PosGenerator, NMultiPositionControl.InputNeuron1-4.PosGenerator, NMultiPositionControl.InputNeuron1-5.PosGenerator (и еще 45)
- **NPSynapse**: NMultiPositionControl.InputNeuron1-1.Soma1.ExcSynapse1, NMultiPositionControl.InputNeuron1-1.Soma1.InhSynapse1, NMultiPositionControl.InputNeuron1-1.LTMembrane.ExcSynapse1, NMultiPositionControl.InputNeuron1-1.LTMembrane.InhSynapse1, NMultiPositionControl.InputNeuron1-1.ExcSynapse1 (и еще 295)

**Входы системы:**
- `ControlNeuron1-1.NegGenerator`
- `ControlNeuron1-1.PosGenerator`
- `ControlNeuron1-2.NegGenerator`
- `ControlNeuron1-2.PosGenerator`
- `ControlNeuron1-3.NegGenerator`
- `ControlNeuron1-3.PosGenerator`
- `ControlNeuron1-4.NegGenerator`
- `ControlNeuron1-4.PosGenerator`
- `ControlNeuron1-5.NegGenerator`
- `ControlNeuron1-5.PosGenerator`
- ... (всего 342 входов)

**Выходы системы:**
- `NMultiPositionControl.ControlNeuron1-1.LTMembrane.ExcChannel.Output`
- `NMultiPositionControl.ControlNeuron1-1.LTMembrane.ExcSynapse1.Output`
- `NMultiPositionControl.ControlNeuron1-1.LTMembrane.InhChannel.Output`
- `NMultiPositionControl.ControlNeuron1-1.LTMembrane.InhSynapse1.Output`
- `NMultiPositionControl.ControlNeuron1-1.LTZone.Output`
- `NMultiPositionControl.ControlNeuron1-1.NegGenerator.Output`
- `NMultiPositionControl.ControlNeuron1-1.PosGenerator.Output`
- `NMultiPositionControl.ControlNeuron1-1.Soma1.ExcChannel.Output`
- `NMultiPositionControl.ControlNeuron1-1.Soma1.ExcSynapse1.Output`
- `NMultiPositionControl.ControlNeuron1-1.Soma1.InhChannel.Output`
- ... (всего 265 выходов)

**Количество связей:** 265

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

### NewPositionControl_Test

**Путь:** `Bin\Configs\a.demcheva\NewPositionControl_Test`

**Назначение:** Система управления движением

**Основные компоненты:**
- **NCGenerator**: EngineMotionControl2.AfferentSource1, AfferentSource1
- **NControlObjectSource**: EngineMotionControl2.NManipulatorSource1, NManipulatorSource1
- **NDCEngine**: DCEngine2
- **NEngineMotionControl**: EngineMotionControl2
- **NIntervalSeparator**: EngineMotionControl2.NegIntervalSeparator11, EngineMotionControl2.PosIntervalSeparator11, EngineMotionControl2.NegIntervalSeparator21, EngineMotionControl2.PosIntervalSeparator21, EngineMotionControl2.NegIntervalSeparator31 (и еще 7)
- **NManipulatorInput**: EngineMotionControl2.NManipulatorInput1, NManipulatorInput1
- **NNewMotionElement**: EngineMotionControl2.MotionElement0, EngineMotionControl2.MotionElement1, EngineMotionControl2.MotionElement2, MotionElement0, MotionElement1 (и еще 1)
- **NNewPositionControlElement**: NNewPositionControlElement2
- **NNewSPNeuron**: NNewPositionControlElement2.InputNeuronL11, NNewPositionControlElement2.InputNeuronR11, NNewPositionControlElement2.InputNeuronL21, NNewPositionControlElement2.InputNeuronR21, NNewPositionControlElement2.InputNeuronL31 (и еще 75)
- **NPExcChannel**: NNewPositionControlElement2.InputNeuronL11.Soma1.ExcChannel, NNewPositionControlElement2.InputNeuronR11.Soma1.ExcChannel, NNewPositionControlElement2.InputNeuronL21.Soma1.ExcChannel, NNewPositionControlElement2.InputNeuronR21.Soma1.ExcChannel, NNewPositionControlElement2.InputNeuronL31.Soma1.ExcChannel (и еще 84)
- **NPGenerator**: NNewPositionControlElement2.NPGeneratorL11, NNewPositionControlElement2.NPGeneratorR11, NNewPositionControlElement2.NPGeneratorL21, NNewPositionControlElement2.NPGeneratorR21, NNewPositionControlElement2.NPGeneratorL31 (и еще 61)
- **NPInhChannel**: NNewPositionControlElement2.InputNeuronL11.Soma1.InhChannel, NNewPositionControlElement2.InputNeuronR11.Soma1.InhChannel, NNewPositionControlElement2.InputNeuronL21.Soma1.InhChannel, NNewPositionControlElement2.InputNeuronR21.Soma1.InhChannel, NNewPositionControlElement2.InputNeuronL31.Soma1.InhChannel (и еще 84)
- **NPLTExcChannel**: NNewPositionControlElement2.InputNeuronL11.LTMembrane.ExcChannel, NNewPositionControlElement2.InputNeuronL11.ExcChannel, NNewPositionControlElement2.InputNeuronR11.LTMembrane.ExcChannel, NNewPositionControlElement2.InputNeuronR11.ExcChannel, NNewPositionControlElement2.InputNeuronL21.LTMembrane.ExcChannel (и еще 173)
- **NPLTInhChannel**: NNewPositionControlElement2.InputNeuronL11.LTMembrane.InhChannel, NNewPositionControlElement2.InputNeuronL11.InhChannel, NNewPositionControlElement2.InputNeuronR11.LTMembrane.InhChannel, NNewPositionControlElement2.InputNeuronR11.InhChannel, NNewPositionControlElement2.InputNeuronL21.LTMembrane.InhChannel (и еще 173)
- **NPLTZone**: NNewPositionControlElement2.InputNeuronL11.LTZone, NNewPositionControlElement2.InputNeuronR11.LTZone, NNewPositionControlElement2.InputNeuronL21.LTZone, NNewPositionControlElement2.InputNeuronR21.LTZone, NNewPositionControlElement2.InputNeuronL31.LTZone (и еще 84)
- **NPLTZoneNeuronMembrane**: NNewPositionControlElement2.InputNeuronL11.LTMembrane, NNewPositionControlElement2.InputNeuronR11.LTMembrane, NNewPositionControlElement2.InputNeuronL21.LTMembrane, NNewPositionControlElement2.InputNeuronR21.LTMembrane, NNewPositionControlElement2.InputNeuronL31.LTMembrane (и еще 84)
- **NPMembrane**: NNewPositionControlElement2.InputNeuronL11.Soma1, NNewPositionControlElement2.InputNeuronR11.Soma1, NNewPositionControlElement2.InputNeuronL21.Soma1, NNewPositionControlElement2.InputNeuronR21.Soma1, NNewPositionControlElement2.InputNeuronL31.Soma1 (и еще 84)
- **NPNeuronNegCGenerator**: NNewPositionControlElement2.InputNeuronL11.NegGenerator, NNewPositionControlElement2.InputNeuronR11.NegGenerator, NNewPositionControlElement2.InputNeuronL21.NegGenerator, NNewPositionControlElement2.InputNeuronR21.NegGenerator, NNewPositionControlElement2.InputNeuronL31.NegGenerator (и еще 84)
- **NPNeuronPosCGenerator**: NNewPositionControlElement2.InputNeuronL11.PosGenerator, NNewPositionControlElement2.InputNeuronR11.PosGenerator, NNewPositionControlElement2.InputNeuronL21.PosGenerator, NNewPositionControlElement2.InputNeuronR21.PosGenerator, NNewPositionControlElement2.InputNeuronL31.PosGenerator (и еще 84)
- **NPSimpleLTZone**: EngineMotionControl2.MotionElement0.AfferentR1.LTZone, EngineMotionControl2.MotionElement0.AfferentL1.LTZone, EngineMotionControl2.MotionElement1.AfferentR1.LTZone, EngineMotionControl2.MotionElement1.AfferentL1.LTZone, EngineMotionControl2.MotionElement2.AfferentR1.LTZone (и еще 11)
- **NPSynapse**: NNewPositionControlElement2.InputNeuronL11.Soma1.ExcSynapse1, NNewPositionControlElement2.InputNeuronL11.Soma1.InhSynapse1, NNewPositionControlElement2.InputNeuronL11.LTMembrane.ExcSynapse1, NNewPositionControlElement2.InputNeuronL11.LTMembrane.InhSynapse1, NNewPositionControlElement2.InputNeuronL11.ExcSynapse1 (и еще 639)
- **NPac**: EngineMotionControl2.Pac, Pac
- **NReceptor**: EngineMotionControl2.MotionElement0.AfferentR1.Receptor, EngineMotionControl2.MotionElement0.AfferentL1.Receptor, EngineMotionControl2.MotionElement0.Receptor, EngineMotionControl2.MotionElement1.AfferentR1.Receptor, EngineMotionControl2.MotionElement1.AfferentL1.Receptor (и еще 19)
- **NSimpleAfferentNeuron**: EngineMotionControl2.MotionElement0.AfferentR1, EngineMotionControl2.MotionElement0.AfferentL1, EngineMotionControl2.MotionElement1.AfferentR1, EngineMotionControl2.MotionElement1.AfferentL1, EngineMotionControl2.MotionElement2.AfferentR1 (и еще 11)
- **UStatisticDoubleMatrix**: EngineMotionControl2.StatisticDoubleMatrix, StatisticDoubleMatrix

**Входы системы:**
- `AfferentL1.LTZone.PGenerator`
- `AfferentL1.PGenerator`
- `AfferentR1.LTZone.PGenerator`
- `AfferentR1.PGenerator`
- `AfferentSource1`
- `ControlNeuronL11.NegGenerator`
- `ControlNeuronL11.PosGenerator`
- `ControlNeuronL21.NegGenerator`
- `ControlNeuronL21.PosGenerator`
- `ControlNeuronL31.NegGenerator`
- ... (всего 703 входов)

**Выходы системы:**
- `DCEngine2.OutputAngle`
- `EngineMotionControl2.MotionElement0.AfferentL1.LTZone.Output`
- `EngineMotionControl2.MotionElement0.AfferentL1.Receptor.Output`
- `EngineMotionControl2.MotionElement0.AfferentR1.LTZone.Output`
- `EngineMotionControl2.MotionElement0.AfferentR1.Receptor.Output`
- `EngineMotionControl2.MotionElement0.MotoneuronL.LTMembrane.ExcChannel.Output`
- `EngineMotionControl2.MotionElement0.MotoneuronL.LTMembrane.ExcSynapse1.Output`
- `EngineMotionControl2.MotionElement0.MotoneuronL.LTMembrane.InhChannel.Output`
- `EngineMotionControl2.MotionElement0.MotoneuronL.LTMembrane.InhSynapse1.Output`
- `EngineMotionControl2.MotionElement0.MotoneuronL.LTZone.Output`
- ... (всего 442 выходов)

**Количество связей:** 517

**Связанные публикации:**
- [Перспективы применения моделей биологических нейронных структур в системах управления движением](https://www.elibrary.ru/item.asp?id=17257136) - Публикация 4: А. В. Бахшиев

---

