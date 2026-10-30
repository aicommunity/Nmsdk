#!/usr/bin/env python3
"""Set curated ClDesc Favorites (direct + optional aliases). Does not mass-regenerate Descriptions."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLDESC = ROOT / "Bin" / "ClDesc"

NOISE_LEAF = {
    "Coord", "Activity", "Type", "Name", "TimeStep", "StepDuration",
    "DebugSysEventsMask", "CalculationDurationThreshold", "MaxCalculationDuration",
    "Id", "IsVisible",
}


def favorites_xml(direct: list[str], aliases: list[tuple[str, str]] | None = None) -> str:
    aliases = aliases or []
    lines = ["\t<Favorites>"]
    for prop in direct:
        lines.append(f"\t\t<{prop}>")
        lines.append(f"\t\t\t<Path>{{CompName}}:{prop}</Path>")
        lines.append(f"\t\t</{prop}>")
    for name, path in aliases:
        lines.append(f"\t\t<{name}>")
        lines.append(f"\t\t\t<Path>{path}</Path>")
        lines.append(f"\t\t</{name}>")
    lines.append("\t</Favorites>")
    return "\n".join(lines)


def property_names(text: str) -> set[str]:
    m = re.search(r"<Properties>(.*?)</Properties>", text, re.S)
    if not m:
        return set()
    return set(re.findall(r"^\t\t<([A-Za-z0-9_]+)>", m.group(1), re.M))


def filter_existing(direct: list[str], names: set[str]) -> list[str]:
    return [p for p in direct if p in names]


def set_favorites(path: Path, direct: list[str], aliases: list[tuple[str, str]] | None = None, class_desc: str | None = None) -> bool:
    text = path.read_text(encoding="utf-8")
    names = property_names(text)
    direct_f = filter_existing(direct, names)
    aliases_f = []
    for name, apath in aliases or []:
        # keep alias if we can't validate nested; always keep curated list
        aliases_f.append((name, apath))
    if not direct_f and not aliases_f:
        print(f"SKIP (no matching props): {path.relative_to(ROOT)}")
        return False
    block = favorites_xml(direct_f, aliases_f)
    if re.search(r"<Favorites/>", text):
        new = re.sub(r"<Favorites/>", block, text, count=1)
    elif re.search(r"<Favorites>.*?</Favorites>", text, re.S):
        new = re.sub(r"<Favorites>.*?</Favorites>", block, text, count=1, flags=re.S)
    else:
        print(f"SKIP (no Favorites node): {path}")
        return False
    if class_desc:
        new = re.sub(
            r"(<ClassName>.*?</ClassName>\s*<Header>.*?</Header>\s*)<Description>.*?</Description>",
            r"\1<Description>" + class_desc + "</Description>",
            new,
            count=1,
            flags=re.S,
        )
    path.write_text(new, encoding="utf-8")
    print(f"OK {path.relative_to(ROOT)} directs={len(direct_f)} aliases={len(aliases_f)}")
    return True


def find_class(class_name: str) -> Path | None:
    hits = list(CLDESC.rglob(f"{class_name}.xml"))
    return hits[0] if hits else None


# --- Pulse ---
SYNAPSE = [
    "Weight", "Resistance", "SecretionTC", "DissociationTC", "PulseAmplitude",
    "UsePulseSignal", "InhibitionCoeff", "UsePresynapticInhibition", "TrainerClassName",
    "Input", "Output", "WeightInput",
]
CHANNEL = [
    "Capacity", "Resistance", "FBResistance", "RestingResistance",
    "UseAveragePotential", "UseAverageSynapsis", "SynapticInputs", "Output", "ChannelInputs",
]
MEMBRANE = [
    "NumExcitatorySynapses", "NumInhibitorySynapses", "SynapseClassName",
    "ExcChannelClassName", "InhChannelClassName", "FeedbackGain",
    "UseAveragePotential", "ResetAvailable",
]
LTZONE = [
    "Threshold", "ThresholdOff", "PulseAmplitude", "PulseLength", "TimeConstant",
    "UseAveragePotential", "UseLTZIntegtation", "UseSpikeStabilizer", "NumChannelsInGroup",
    "Inputs", "Output", "OutputFrequency",
]
GENERATOR = [
    "Frequency", "Amplitude", "PulseLength", "Delay", "FrequencyDeviation",
    "RandomFrequency", "AvgInterval", "ActionPeriod", "Output",
]
TRANSIT = GENERATOR + [
    "UseTransitSignal", "UsePatternOutput", "PatternFrequency", "PatternDuration", "Input",
]
RECEPTOR = [
    "Gain", "MinInputRange", "MaxInputRange", "MinOutputRange", "MaxOutputRange",
    "ExpCoeff", "SumCoeff", "InputAdaptationMode", "OutputAdaptationMode",
    "InputAdaptationArrestingTC", "ActionPeriod", "Input", "Output",
]
NEURON = [
    "StructureBuildMode", "NumSomaMembraneParts", "NumDendriteMembranePartsVec",
    "NumDendriteMembraneParts", "MembraneClassName", "LTMembraneClassName", "LTZoneClassName",
    "ExcGeneratorClassName", "InhGeneratorClassName", "UseAverageDendritesPotential",
    "UseAverageLTZonePotential", "UseAveragePotential", "TrainingPattern",
    "TrainingDendIndexes", "TrainingSynapsisNum", "Output", "SomaSumPotential",
    "DendriticSumPotential", "LayerWidth", "LayerHeight", "NetStructure",
]
NEURON_ALIASES = [
    ("ExcSynapseInput", "Soma1.ExcSynapse1.Input"),
    ("InhSynapseInput", "Soma1.InhSynapse1.Input"),
    ("LTZoneOutput", "LTZone.Output"),
    ("LTZoneThreshold", "LTZone.Threshold"),
]
CLASSIFIER = [
    "NumNeurons", "NumInputDendrite", "IsNeedToTrain", "LTZThreshold",
    "UseFixedLTZThreshold", "FixedLTZThreshold", "SpikesFrequency", "Delay",
    "StructureBuildMode", "NeuronClassName", "NeuronTrainerClassName",
    "PulseGeneratorClassName", "SynapseClassName", "UseTransitSignal",
    "InputPattern", "TrainingPatterns", "Output",
]
TRAINER = [
    "IsNeedToTrain", "LTZThreshold", "UseFixedLTZThreshold", "FixedLTZThreshold",
    "SpikesFrequency", "NeuronClassName", "StructureBuildMode", "InputPattern",
    "TrainingPatterns", "Output",
]


def apply_pulse() -> None:
    specs: list[tuple[str, list[str], list[tuple[str, str]] | None, str | None]] = []
    for c in ["NPSynapse", "NPSynapseBio", "NPSynapseBio2", "NPSynapseStdp",
              "NSynapseCable", "NSynapseCableMulti"]:
        specs.append((c, SYNAPSE, None, None))
    for c in ["NPExcChannel", "NPInhChannel", "NPExcChannelBio", "NPInhChannelBio",
              "NPExcChannelBio2", "NPInhChannelBio2"]:
        specs.append((c, CHANNEL, None, None))
    for c in ["NPMembrane", "NPMembraneBio", "NPMembraneBio2"]:
        specs.append((c, MEMBRANE, None, None))
    for c in ["NPLTZone", "NPulseLTZone", "NPulseLTZoneThreshold", "NPSimpleLTZone",
              "NPulseLTZoneCable"]:
        specs.append((c, LTZONE, None, None))
    specs.append(("NPGenerator", GENERATOR, None,
                  "Генератор импульсов (алиас NPulseGenerator): частота, длительность и амплитуда спайков для входов SNN."))
    specs.append(("NPulseGeneratorTransit", TRANSIT, None, None))
    specs.append(("NReceptor", RECEPTOR, None, None))
    for c in ["NNewSPNeuron", "NPNeuron", "NSPNeuronBio", "NSPNeuronBio2", "NSPNeuron",
              "NSPNeuronGen", "NPulseNeuronIaF", "NPulseNeuronCable", "NPulseNeuronCableMulti",
              "NPulseNeuronIaFStdp", "NSimpleAfferentNeuron", "NSAfferentNeuron",
              "NNewSynSPNeuron", "NSPHebbNeuron"]:
        specs.append((c, NEURON, NEURON_ALIASES, None))
    specs.append(("NSpikeClassifier", CLASSIFIER, None, None))
    specs.append(("NNeuronTrainer", TRAINER, None, None))
    for c, d, a, desc in specs:
        p = find_class(c)
        if not p:
            print(f"MISSING {c}")
            continue
        set_favorites(p, d, a, desc)


# --- Motion ---
MOTION: dict[str, list[str]] = {
    "NNewMotionElement": [
        "NumControlLoops", "EnableControlLoopFlags", "LinkModes", "ExternalControlMode",
        "MotoneuronBranchMode", "RenshowMode", "InterneuronPresentMode", "PacemakerMode",
        "NeuroObjectName", "AfferentObjectName",
    ],
    "NIntervalSeparator": ["Mode", "MinRange", "MaxRange", "Gain", "Input", "Output"],
    "NManipulatorInput": ["Voltage", "ActionPeriod", "Input", "Output"],
    "NControlObjectSource": ["DataIndexes", "DataMul", "DataShift", "ActionPeriod", "Input", "Output"],
    "NDCEngine": [
        "EMFactor", "Resistance", "Inductance", "Tm", "ReductionRate",
        "InputVoltage", "InputMomentum", "OutputAngle", "OutputAngleSpeed", "OutputMomentum", "Angle", "OutMoment",
    ],
    "NPendulumAndCart": [
        "Mode", "CartMass", "RodMass", "RodLength", "Kp", "Ki", "Kd",
        "MovementKp", "MovementKi", "MovementKd", "AngleWeight", "MovementWeight",
    ],
    "NMultiPositionControl": [
        "NumOfPositions", "PCsNum", "BuildSolo", "ExternalControl", "TargetPosition",
        "CurrentPosition", "RememberState", "ControlNeuronType", "InputNeuronType", "Delta",
    ],
    "NEngineMotionControl": [
        "NumMotionElements", "NumControlLoops", "MotionElementClassName", "CreationMode",
        "AfferentRangeMode", "RenshowMode", "MCAfferentObjectName", "MCNeuroObjectName", "PacGain",
    ],
    "NNewPositionControlElement": [
        "TargetPosition", "CurrentPosition", "ExternalControl", "Delta",
        "MotionControl", "ControlNeuronType",
    ],
    "NFrequencyReceiver": ["LeftRange", "RightRange", "FrequencyStep", "OutputFreq", "PulseCounter"],
    "NEyeRetina": [
        "InputImage", "CaptureImage", "OnGanglionicOuts", "OffGanglionicOuts",
        "LeftMuscle", "RightMuscle", "TopMuscle", "BottomMuscle",
    ],
}

# Keep these directs when cleaning aliases
MOTION_KEEP_DIRECT_EXTRA = {
    "NSignalEstimation": [
        "DelaysSignal", "DelaysSinchro", "Frequency", "NumZones",
        "UpperLimitsOfZones", "UseTransitSignal", "UseTransitSinchro",
    ],
    "NActuatorSignals": [
        "DelayLeft", "DelayRight", "DelaySinchro1", "DelaySinchro2",
        "Frequency", "UseTransitEngineSignal", "UseTransitSinchroSignal",
        "Amplitude", "PulseLength",
    ],
    "NSuppressionUnit": None,  # keep existing directs from file
    "NSeqComparison": None,
    "NObjInArea": None,
    "NCounterNeuron": ["CurCount", "MaxCount", "Amplitude", "PulseLength", "LTZThreshold"],
}


def extract_direct_favorites(text: str) -> list[str]:
    m = re.search(r"<Favorites>(.*?)</Favorites>", text, re.S)
    if not m:
        return []
    items = re.findall(r"<([A-Za-z0-9_]+)>\s*<Path>(.*?)</Path>\s*</\1>", m.group(1), re.S)
    out = []
    for name, path in items:
        if "." not in path:
            # use property name from path after :
            prop = path.split(":")[-1] if ":" in path else path
            out.append(prop if prop else name)
    return out


def useful_aliases(text: str) -> list[tuple[str, str]]:
    m = re.search(r"<Favorites>(.*?)</Favorites>", text, re.S)
    if not m:
        return []
    items = re.findall(r"<([A-Za-z0-9_]+)>\s*<Path>(.*?)</Path>\s*</\1>", m.group(1), re.S)
    out = []
    for name, path in items:
        if "." not in path:
            continue
        leaf = path.split(".")[-1]
        if leaf in NOISE_LEAF:
            continue
        if leaf in ("Input", "Output", "Weight", "Threshold", "Frequency"):
            out.append((name, path))
    return out[:6]


def apply_motion() -> None:
    for c, directs in MOTION.items():
        p = find_class(c)
        if not p:
            print(f"MISSING {c}")
            continue
        set_favorites(p, directs, None, None)
    # hygiene existing
    for c in ["NSignalEstimation", "NActuatorSignals", "NSuppressionUnit", "NSeqComparison",
              "NObjInArea", "NCounterNeuron", "NMazeMemory", "NMazeMemorySimplified",
              "NTrajectoryElement", "NNewMotionElement", "NEngineMotionControl",
              "N2AsfNewSimplestAfferentBranchedEngineControl"]:
        p = find_class(c)
        if not p:
            continue
        text = p.read_text(encoding="utf-8")
        existing = extract_direct_favorites(text)
        extra = MOTION_KEEP_DIRECT_EXTRA.get(c)
        if extra is None and c in MOTION_KEEP_DIRECT_EXTRA:
            directs = existing
        elif extra:
            directs = list(dict.fromkeys(existing + extra))
        elif c in MOTION:
            directs = list(dict.fromkeys(MOTION[c] + existing))
        else:
            directs = existing
        aliases = useful_aliases(text)
        set_favorites(p, directs, aliases, None)


# --- Hardware / Basic / CV ---
HARDWARE: dict[str, list[str]] = {
    "ArduinoBoard": [
        "PortName", "BundledFirmwareId", "Connect", "Disconnect", "Reconnect",
        "UploadFirmware", "IsConnected", "HasError", "ConnectOnBuild", "BaudRate",
        "BoardProfile", "LastError",
    ],
    "ArduinoFirmata": [
        "SelectedPin", "SelectedPinMode", "AutoRefreshPins", "RestartFirmata",
        "ApplyPinConfig", "SetPinMode", "WriteDigital", "ReadAnalog", "RefreshPins",
        "IsFirmataReady", "IsLinkReady", "HandshakeStage", "AnalogSamples", "DigitalSamples",
        "PinConfigPreset", "LoadPreset", "AnalogPinValue", "DigitalPinValue",
        "WritePwm", "PwmPinValue", "PinStatusJson",
    ],
    "ArduinoSensorSketch": [
        "PortName", "Command", "ProtocolVersion", "SendCommand", "StartReading",
        "StopReading", "GetDataFromBuffers", "IsProtocolReady",
    ],
    "ArduinoAdc": [
        "LinkedFirmataName", "AnalogPin", "UseLinkedAnalogSamples", "ReadAdcFlag",
        "AdcValue", "BoardProfile",
    ],
    "ArduinoDcDemo": [
        "PortName", "BundledFirmwareId", "SendCommand", "GetSpeed", "Speed",
    ],
    "Arduino": ["PortToConnect", "Command", "SendCommandFlag"],
    "ADC": [],
    "DC": ["Command", "SendCommandFlag", "Speed", "GetSpeed"],
}

BASIC_CV: dict[str, list[str]] = {
    "UStatisticDoubleMatrix": [
        "SavePath", "SaveMode", "AverageMode", "AverageNumber", "AverageInput",
        "PrefixName", "NumSkipSteps", "TimeInterval", "ManualModeEnabled",
        "InputMatrixData", "ForceCreateSavePath",
    ],
    "UStatisticIntMatrix": [
        "SavePath", "SaveMode", "AverageMode", "AverageNumber", "AverageInput",
        "PrefixName", "NumSkipSteps", "TimeInterval", "ManualModeEnabled", "InputMatrixData",
    ],
    "TCaptureImageSequence": [
        "Path", "IsPathRelativeFromConfig", "RepeatFlag", "CaptureDelay", "EnableCapture",
        "DesiredFps", "DesiredWidth", "DesiredHeight", "NumImages", "CurrentImageIndex",
    ],
    "Reduce": ["NumRows", "NumCols", "Input", "Output"],
    "VideoSimulatorSimple": ["NumObjects", "WorkArea", "BgMode", "ShowGrid", "Input", "Output"],
    "UMatrixSourceDataFile": [
        "FileName", "ReloadFile", "SkipCalcIfNoNewData", "IsCheckDateTime",
        "UseRelativePathFromConfig", "FullMatrix", "RowCount", "ColCount",
    ],
    "UNoiseGen": ["NoiseLevel", "OneErrorForAll", "InputParams", "OutputParams"],
    "UNoiseGenDouble": ["NoiseLevel", "OneErrorForAll", "InputParams", "OutputParams"],
    "UNoiseGenInt": ["NoiseLevel", "OneErrorForAll", "InputParams", "OutputParams"],
    "UMatrixSourceTimeSeries": [
        "FileName", "CurrentLineIndex", "IsStandartizeData", "SkipCalcIfNoNewData", "FullMatrix",
    ],
    "UMatrixSource": [
        "DoubleMatrix", "DoubleMatrixInput", "IntMatrix", "IntMatrixInput",
        "DoubleVector", "IntVector",
    ],
    "Crop": ["CropRect", "Input", "Output"],
    "ColorConvert": ["NewColorModel", "Input", "Output"],
    "TBinarizationSimple": ["Threshold", "Input", "Output"],
}


def apply_hw_basic_cv() -> None:
    for mapping in (HARDWARE, BASIC_CV):
        for c, directs in mapping.items():
            p = find_class(c)
            if not p:
                print(f"MISSING {c}")
                continue
            if not directs:
                # leave empty or minimal
                continue
            set_favorites(p, directs, None, None)


def main(argv: list[str]) -> int:
    waves = argv[1:] or ["pulse", "motion", "hw"]
    if "pulse" in waves:
        apply_pulse()
    if "motion" in waves:
        apply_motion()
    if "hw" in waves:
        apply_hw_basic_cv()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
