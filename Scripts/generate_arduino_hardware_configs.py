#!/usr/bin/env python3
"""Generate Bin/Configs/SpikeSamples/Hardware/* test projects for Rdk-HardwareLib."""

from __future__ import annotations

import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Bin/Configs/SpikeSamples/Hardware"

MODEL_HEADER = """\
<Save ModelName="Model">
\t<Model Class="Model">
\t\t<Parameters>
\t\t\t<Output Type="UBitmap" Size="0" PType="257" IoType="17">
\t\t\t\t<Width Type="int">0</Width>
\t\t\t\t<Height Type="int">0</Height>
\t\t\t\t<ColorModel Type="UBMColorModel">3</ColorModel>
\t\t\t\t<Data/>
\t\t\t</Output>
\t\t\t<DebugSysEventsMask Type="unsigned int" PType="769" IoType="17">2147483647</DebugSysEventsMask>
\t\t\t<CalculationDurationThreshold Type="__int64" PType="257" IoType="17">-1</CalculationDurationThreshold>
\t\t\t<MaxCalculationDuration Type="__int64" PType="257" IoType="17">-1</MaxCalculationDuration>
\t\t\t<Activity Type="bool" PType="257" IoType="17">1</Activity>
\t\t\t<Coord Type="MVector&lt;double&gt;" Size="3" PType="257" IoType="17">0 0 0</Coord>
\t\t\t</Parameters>
\t\t<Links Type="ULinksList" Size="0"/>
\t\t<Components>
"""

MODEL_FOOTER = """\
\t\t</Components>
\t</Model>
</Save>
"""

PARAM_HEADER = """\
<SaveProperties ModelName="Model">
\t<Model Class="Model">
\t\t<Parameters>
\t\t\t<Output Type="UBitmap" Size="0" PType="257" IoType="17">
\t\t\t\t<Width Type="int">0</Width>
\t\t\t\t<Height Type="int">0</Height>
\t\t\t\t<ColorModel Type="UBMColorModel">3</ColorModel>
\t\t\t\t<Data/>
\t\t\t</Output>
\t\t\t<DebugSysEventsMask Type="unsigned int" PType="769" IoType="17">2147483647</DebugSysEventsMask>
\t\t\t<CalculationDurationThreshold Type="__int64" PType="257" IoType="17">-1</CalculationDurationThreshold>
\t\t\t<MaxCalculationDuration Type="__int64" PType="257" IoType="17">-1</MaxCalculationDuration>
\t\t\t<Activity Type="bool" PType="257" IoType="17">1</Activity>
\t\t\t<Coord Type="MVector&lt;double&gt;" Size="3" PType="257" IoType="17">0 0 0</Coord>
\t\t\t</Parameters>
\t\t<Components>
"""

PARAM_FOOTER = """\
\t\t</Components>
\t</Model>
</SaveProperties>
"""

UNET_BASE = """\
\t\t\t\t\t<Activity Type="bool" PType="257" IoType="17">1</Activity>
\t\t\t\t\t<Coord Type="MVector&lt;double&gt;" Size="3" PType="257" IoType="17">{coord}</Coord>
\t\t\t\t\t<MaxCalculationDuration Type="__int64" PType="257" IoType="17">-1</MaxCalculationDuration>
\t\t\t\t\t<CalculationDurationThreshold Type="__int64" PType="257" IoType="17">-1</CalculationDurationThreshold>
\t\t\t\t\t<DebugSysEventsMask Type="unsigned int" PType="769" IoType="17">2147483647</DebugSysEventsMask>
"""

BOARD_PROPS = """\
\t\t\t\t\t<PortName Type="std::string" PType="257" IoType="17">{port}</PortName>
\t\t\t\t\t<BaudRate Type="int" PType="257" IoType="17">57600</BaudRate>
\t\t\t\t\t<BoardProfile Type="int" PType="257" IoType="17">0</BoardProfile>
\t\t\t\t\t<AutoReconnect Type="bool" PType="257" IoType="17">0</AutoReconnect>
\t\t\t\t\t<ConnectOnBuild Type="bool" PType="257" IoType="17">0</ConnectOnBuild>
\t\t\t\t\t<HeartbeatEnabled Type="bool" PType="257" IoType="17">1</HeartbeatEnabled>
\t\t\t\t\t<HeartbeatIntervalMs Type="int" PType="257" IoType="17">3000</HeartbeatIntervalMs>
\t\t\t\t\t<HeartbeatTimeoutMs Type="int" PType="257" IoType="17">10000</HeartbeatTimeoutMs>
\t\t\t\t\t<FirmwarePath Type="std::string" PType="257" IoType="17"></FirmwarePath>
\t\t\t\t\t<BundledFirmwareId Type="std::string" PType="257" IoType="17">{bundled}</BundledFirmwareId>
\t\t\t\t\t<ShowDebug Type="bool" PType="257" IoType="17">0</ShowDebug>
\t\t\t\t\t<ConnectionState Type="int" PType="258" IoType="17">0</ConnectionState>
\t\t\t\t\t<LastError Type="std::string" PType="258" IoType="17"></LastError>
\t\t\t\t\t<LastActivityMs Type="double" PType="258" IoType="17">0</LastActivityMs>
\t\t\t\t\t<MissedHeartbeats Type="int" PType="258" IoType="17">0</MissedHeartbeats>
\t\t\t\t\t<RequestHealthCheck Type="bool" PType="258" IoType="17">0</RequestHealthCheck>
\t\t\t\t\t<UploadFirmwareFlag Type="bool" PType="258" IoType="17">0</UploadFirmwareFlag>
\t\t\t\t\t<UploadProgress Type="int" PType="258" IoType="17">0</UploadProgress>
\t\t\t\t\t<UploadLastResult Type="std::string" PType="258" IoType="17"></UploadLastResult>
"""

SKETCH_EXTRA = """\
\t\t\t\t\t<Command Type="std::string" PType="257" IoType="17"></Command>
\t\t\t\t\t<ProtocolVersion Type="int" PType="257" IoType="17">{proto}</ProtocolVersion>
\t\t\t\t\t<LowerSensorLimit Type="double" PType="257" IoType="17">-100</LowerSensorLimit>
\t\t\t\t\t<UpperSensorLimit Type="double" PType="257" IoType="17">100</UpperSensorLimit>
\t\t\t\t\t<MatrixCols Type="int" PType="257" IoType="17">100</MatrixCols>
\t\t\t\t\t<GetDataFromBuffers Type="bool" PType="258" IoType="17">0</GetDataFromBuffers>
\t\t\t\t\t<GetPinsInfo Type="bool" PType="258" IoType="17">0</GetPinsInfo>
\t\t\t\t\t<SendCommandFlag Type="bool" PType="258" IoType="17">0</SendCommandFlag>
\t\t\t\t\t<SentCommand Type="std::string" PType="258" IoType="17"></SentCommand>
\t\t\t\t\t<InputCommand Type="std::string" PType="258" IoType="17"></InputCommand>
\t\t\t\t\t<RxFrameCount Type="int" PType="258" IoType="17">0</RxFrameCount>
\t\t\t\t\t<TxCommandCount Type="int" PType="258" IoType="17">0</TxCommandCount>
\t\t\t\t\t<DoubleMatrixReadings Type="MDMatrix&lt;double&gt;" Rows="4" Cols="100" PType="258" IoType="17">
</DoubleMatrixReadings>
\t\t\t\t\t<PinStatusJson Type="std::string" PType="258" IoType="17"></PinStatusJson>
"""

FIRMATA_EXTRA = """\
\t\t\t\t\t<SelectedPin Type="int" PType="257" IoType="17">13</SelectedPin>
\t\t\t\t\t<SelectedPinMode Type="int" PType="257" IoType="17">1</SelectedPinMode>
\t\t\t\t\t<DigitalPinValue Type="int" PType="257" IoType="17">0</DigitalPinValue>
\t\t\t\t\t<FirmataReady Type="bool" PType="258" IoType="17">0</FirmataReady>
\t\t\t\t\t<FirmataFirmwareVersion Type="std::string" PType="258" IoType="17"></FirmataFirmwareVersion>
\t\t\t\t\t<AnalogPinValue Type="int" PType="258" IoType="17">0</AnalogPinValue>
\t\t\t\t\t<SetPinModeFlag Type="bool" PType="258" IoType="17">0</SetPinModeFlag>
\t\t\t\t\t<ReadAnalogFlag Type="bool" PType="258" IoType="17">0</ReadAnalogFlag>
\t\t\t\t\t<WriteDigitalFlag Type="bool" PType="258" IoType="17">0</WriteDigitalFlag>
"""

ADC_PROPS = """\
\t\t\t\t\t<LinkedFirmataName Type="std::string" PType="257" IoType="17">Firmata</LinkedFirmataName>
\t\t\t\t\t<AnalogPin Type="int" PType="257" IoType="17">14</AnalogPin>
\t\t\t\t\t<AdcValue Type="int" PType="258" IoType="17">0</AdcValue>
\t\t\t\t\t<ReadAdcFlag Type="bool" PType="258" IoType="17">0</ReadAdcFlag>
"""

DC_PROPS = """\
\t\t\t\t\t<LinkedSketchName Type="std::string" PType="257" IoType="17">SensorSketch</LinkedSketchName>
\t\t\t\t\t<Command Type="std::string" PType="257" IoType="17"></Command>
\t\t\t\t\t<SendCommandFlag Type="bool" PType="258" IoType="17">0</SendCommandFlag>
\t\t\t\t\t<SentCommand Type="std::string" PType="258" IoType="17"></SentCommand>
\t\t\t\t\t<Speed Type="float" PType="258" IoType="17">0</Speed>
\t\t\t\t\t<Acceleration Type="float" PType="258" IoType="17">0</Acceleration>
\t\t\t\t\t<GetSpeed Type="bool" PType="258" IoType="17">0</GetSpeed>
"""

PROJECT_INI = """\
<Project Version="2.1">
\t<MultiGeneral>
\t\t<DebugModeFlag>1</DebugModeFlag>
\t\t<DebugSysEventsMask>0</DebugSysEventsMask>
\t\t<DebuggerMessageFlag>0</DebuggerMessageFlag>
\t\t<EventsLogMode>0</EventsLogMode>
\t\t<OverrideLogParameters>1</OverrideLogParameters>
\t\t<EnginesMode>1</EnginesMode>
\t\t<CalculationTimeSourceMode>0</CalculationTimeSourceMode>
\t\t<NumEngines>1</NumEngines>
\t\t<ProjectShowChannelsStates>0</ProjectShowChannelsStates>
\t\t<DisableStopVideoSources>0</DisableStopVideoSources>
\t</MultiGeneral>
\t<General>
\t\t<InterfaceFileName>Interface.xml</InterfaceFileName>
\t\t<ProjectDescriptionFileName>README.md</ProjectDescriptionFileName>
\t\t<ProjectAutoSaveFlag>1</ProjectAutoSaveFlag>
\t\t<ProjectAutoSaveStateFlag>0</ProjectAutoSaveStateFlag>
\t\t<MTUpdateInterfaceInterval>30</MTUpdateInterfaceInterval>
\t\t<GuiUpdateMode>0</GuiUpdateMode>
\t\t<ProjectMode>1</ProjectMode>
\t\t<ProjectName>{name}</ProjectName>
\t\t<UserName>guest</UserName>
\t\t<UserId>-1</UserId>
\t\t<CreationTime>2026.05.16 00_00_00</CreationTime>
\t</General>
\t<Channels>
\t\t<00>
\t\t\t<ModelFileName>Model_00.xml</ModelFileName>
\t\t\t<ParametersFileName>Parameters_00.xml</ParametersFileName>
\t\t\t<PredefinedStructure>0</PredefinedStructure>
\t\t\t<DefaultTimeStep>1000</DefaultTimeStep>
\t\t\t<GlobalTimeStep>1000</GlobalTimeStep>
\t\t\t<CalculationMode>1</CalculationMode>
\t\t\t<MinInterstepsInterval>1</MinInterstepsInterval>
\t\t\t<InitAfterLoadFlag>1</InitAfterLoadFlag>
\t\t\t<ResetAfterLoadFlag>1</ResetAfterLoadFlag>
\t\t\t<DebugModeFlag>1</DebugModeFlag>
\t\t\t<EventsLogMode>0</EventsLogMode>
\t\t\t<DebugSysEventsMask>0</DebugSysEventsMask>
\t\t\t<DebuggerMessageFlag>0</DebuggerMessageFlag>
\t\t\t<MaxCalculationModelTime>0</MaxCalculationModelTime>
\t\t\t<UseIndTimeStepFlag>0</UseIndTimeStepFlag>
\t\t</00>
\t</Channels>
</Project>
"""

INTERFACE_XML = "<Interfaces/>\n"

README_TEMPLATE = """\
# {title}

**Путь:** `Bin/Configs/SpikeSamples/Hardware/{folder}`

## Назначение

{purpose}

## Перед запуском

1. Подключите Arduino Uno/Mega по USB.
2. В свойстве `PortName` укажите порт (`/dev/ttyACM0`, `COM3`, …).
3. При необходимости установите `ConnectOnBuild` = 1 или нажмите Connect в GUI.
4. См. чеклист: `Libraries/Rdk-HardwareLib/Firmware/README.md`.

## Компоненты

{components}

## Проверка

- Открыть проект в NeuroModeler.
- Build / Reset / Calculate.
- Сверить с пунктами чеклиста для данного компонента.
"""


def component_block(name: str, class_name: str, coord: str, inner: str) -> str:
    return (
        f"\t\t\t<{name} Class=\"{class_name}\">\n"
        f"\t\t\t\t<Parameters>\n"
        + UNET_BASE.format(coord=coord)
        + inner
        + "\t\t\t\t</Parameters>\n"
        f"\t\t\t\t<Components/>\n"
        f"\t\t\t</{name}>\n"
    )


def write_project(
    folder: str,
    title: str,
    purpose: str,
    components_desc: str,
    components_xml: str,
    port: str = "/dev/ttyACM0",
) -> None:
    dest = OUT / folder
    dest.mkdir(parents=True, exist_ok=True)
    body = components_xml
    model = MODEL_HEADER + body + MODEL_FOOTER
    params = PARAM_HEADER + body + PARAM_FOOTER
    (dest / "Model_00.xml").write_text(model, encoding="utf-8")
    (dest / "Parameters_00.xml").write_text(params, encoding="utf-8")
    (dest / "Project.ini").write_text(PROJECT_INI.format(name=title), encoding="utf-8")
    (dest / "Interface.xml").write_text(INTERFACE_XML, encoding="utf-8")
    (dest / "README.md").write_text(
        README_TEMPLATE.format(
            title=title,
            folder=folder,
            purpose=purpose,
            components=components_desc,
        ),
        encoding="utf-8",
    )


def main() -> None:
    port = "/dev/ttyACM0"

    board = BOARD_PROPS.format(port=port, bundled="sensor_lab_v1")
    write_project(
        "01-ArduinoBoard",
        "Hardware test: ArduinoBoard",
        "Проверка `ArduinoBoard`: прошивка sensor_lab, upload, heartbeat, подключение.",
        "- `Board` (`ArduinoBoard`) — upload `sensor_lab_v1`, порт, heartbeat.",
        component_block("Board", "ArduinoBoard", "8 4 0", board),
        port,
    )

    sketch = board.replace("sensor_lab_v1", "sensor_lab_v1") + SKETCH_EXTRA.format(proto=1)
    write_project(
        "02-ArduinoSensorSketch",
        "Hardware test: ArduinoSensorSketch",
        "Проверка `ArduinoSensorSketch`: кастомный протокол sensor_lab, команды, матрица.",
        "- `SensorSketch` (`ArduinoSensorSketch`) — bundled `sensor_lab_v1`, ProtocolVersion 1.",
        component_block("SensorSketch", "ArduinoSensorSketch", "8 8 0", sketch),
        port,
    )

    sketch_v2 = board + SKETCH_EXTRA.format(proto=2)
    write_project(
        "06-ArduinoSensorSketch-Proto2",
        "Hardware test: ArduinoSensorSketch PROTO v2",
        "Проверка framed protocol v2: `ProtocolVersion` = 2, команда `PROTO 2` при подключении.",
        "- `SensorSketch` (`ArduinoSensorSketch`) — ProtocolVersion 2.",
        component_block("SensorSketch", "ArduinoSensorSketch", "8 12 0", sketch_v2),
        port,
    )

    firmata_board = BOARD_PROPS.format(port=port, bundled="standard_firmata") + FIRMATA_EXTRA
    write_project(
        "03-ArduinoFirmata",
        "Hardware test: ArduinoFirmata",
        "Проверка `ArduinoFirmata`: StandardFirmata, pin mode, digital/analog.",
        "- `Firmata` (`ArduinoFirmata`) — bundled `standard_firmata`.",
        component_block("Firmata", "ArduinoFirmata", "16 4 0", firmata_board),
        port,
    )

    adc_body = (
        component_block("Firmata", "ArduinoFirmata", "16 4 0", firmata_board)
        + component_block("Adc", "ArduinoAdc", "16 8 0", UNET_BASE.format(coord="16 8 0") + ADC_PROPS)
    )
    dest = OUT / "04-ArduinoAdc"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "Model_00.xml").write_text(MODEL_HEADER + adc_body + MODEL_FOOTER, encoding="utf-8")
    (dest / "Parameters_00.xml").write_text(PARAM_HEADER + adc_body + PARAM_FOOTER, encoding="utf-8")
    (dest / "Project.ini").write_text(
        PROJECT_INI.format(name="Hardware test: ArduinoAdc"), encoding="utf-8"
    )
    (dest / "Interface.xml").write_text(INTERFACE_XML, encoding="utf-8")
    (dest / "README.md").write_text(
        README_TEMPLATE.format(
            title="Hardware test: ArduinoAdc",
            folder="04-ArduinoAdc",
            purpose="Проверка `ArduinoAdc` через связанный `Firmata` (analog pin A0 = Firmata 14).",
            components="- `Firmata` + `Adc` (`ArduinoAdc`, `LinkedFirmataName=Firmata`).",
        ),
        encoding="utf-8",
    )

    dc_body = (
        component_block("SensorSketch", "ArduinoSensorSketch", "8 8 0", sketch)
        + component_block("DcDemo", "ArduinoDcDemo", "8 12 0", UNET_BASE.format(coord="8 12 0") + DC_PROPS)
    )
    dest = OUT / "05-ArduinoDcDemo"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "Model_00.xml").write_text(MODEL_HEADER + dc_body + MODEL_FOOTER, encoding="utf-8")
    (dest / "Parameters_00.xml").write_text(PARAM_HEADER + dc_body + PARAM_FOOTER, encoding="utf-8")
    (dest / "Project.ini").write_text(
        PROJECT_INI.format(name="Hardware test: ArduinoDcDemo"), encoding="utf-8"
    )
    (dest / "Interface.xml").write_text(INTERFACE_XML, encoding="utf-8")
    (dest / "README.md").write_text(
        README_TEMPLATE.format(
            title="Hardware test: ArduinoDcDemo",
            folder="05-ArduinoDcDemo",
            purpose="Проверка `ArduinoDcDemo`: команды и скорость через `SensorSketch`.",
            components="- `SensorSketch` + `DcDemo` (`LinkedSketchName=SensorSketch`).",
        ),
        encoding="utf-8",
    )

    index = OUT / "README.md"
    index.write_text(
        textwrap.dedent(
            """\
            # Hardware — тестовые конфигурации Rdk-HardwareLib

            Набор минимальных проектов для ручной проверки компонентов Arduino на плате.

            | Каталог | ClassName | Прошивка |
            |---------|-----------|----------|
            | [01-ArduinoBoard](01-ArduinoBoard/) | `ArduinoBoard` | sensor_lab_v1 |
            | [02-ArduinoSensorSketch](02-ArduinoSensorSketch/) | `ArduinoSensorSketch` | sensor_lab_v1 |
            | [03-ArduinoFirmata](03-ArduinoFirmata/) | `ArduinoFirmata` | standard_firmata |
            | [04-ArduinoAdc](04-ArduinoAdc/) | `ArduinoAdc` + `ArduinoFirmata` | standard_firmata |
            | [05-ArduinoDcDemo](05-ArduinoDcDemo/) | `ArduinoDcDemo` + `ArduinoSensorSketch` | sensor_lab_v1 |
            | [06-ArduinoSensorSketch-Proto2](06-ArduinoSensorSketch-Proto2/) | `ArduinoSensorSketch` (v2) | sensor_lab_v1 |

            Перед тестом задайте `PortName` и следуйте [чеклисту](../../../../Libraries/Rdk-HardwareLib/Firmware/README.md).

            Генерация: `Scripts/generate_arduino_hardware_configs.py`
            """
        ),
        encoding="utf-8",
    )
    print(f"Generated configs under {OUT}")


if __name__ == "__main__":
    main()
