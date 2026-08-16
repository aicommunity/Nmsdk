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
\t\t\t\t\t<BoardProfile Type="int" PType="257" IoType="17">{board_profile}</BoardProfile>
\t\t\t\t\t<AutoReconnect Type="bool" PType="257" IoType="17">0</AutoReconnect>
\t\t\t\t\t<ConnectOnBuild Type="bool" PType="257" IoType="17">0</ConnectOnBuild>
\t\t\t\t\t<Connect Type="bool" PType="257" IoType="17">0</Connect>
\t\t\t\t\t<Disconnect Type="bool" PType="257" IoType="17">0</Disconnect>
\t\t\t\t\t<Reconnect Type="bool" PType="257" IoType="17">0</Reconnect>
\t\t\t\t\t<UploadFirmware Type="bool" PType="257" IoType="17">0</UploadFirmware>
\t\t\t\t\t<ClearLastError Type="bool" PType="257" IoType="17">0</ClearLastError>
\t\t\t\t\t<HeartbeatEnabled Type="bool" PType="257" IoType="17">1</HeartbeatEnabled>
\t\t\t\t\t<HeartbeatIntervalMs Type="int" PType="257" IoType="17">3000</HeartbeatIntervalMs>
\t\t\t\t\t<HeartbeatTimeoutMs Type="int" PType="257" IoType="17">10000</HeartbeatTimeoutMs>
\t\t\t\t\t<FirmwarePath Type="std::string" PType="257" IoType="17"></FirmwarePath>
\t\t\t\t\t<BundledFirmwareId Type="std::string" PType="257" IoType="17">{bundled}</BundledFirmwareId>
\t\t\t\t\t<ShowDebug Type="bool" PType="257" IoType="17">0</ShowDebug>
\t\t\t\t\t<ConnectionState Type="int" PType="258" IoType="17">0</ConnectionState>
\t\t\t\t\t<LastError Type="std::string" PType="258" IoType="17"></LastError>
\t\t\t\t\t<LastActivityMs Type="double" PType="258" IoType="17">0</LastActivityMs>
\t\t\t\t\t<IsConnected Type="bool" PType="258" IoType="17">0</IsConnected>
\t\t\t\t\t<IsOpening Type="bool" PType="258" IoType="17">0</IsOpening>
\t\t\t\t\t<HasError Type="bool" PType="258" IoType="17">0</HasError>
\t\t\t\t\t<IsDisconnected Type="bool" PType="258" IoType="17">1</IsDisconnected>
\t\t\t\t\t<IsUploading Type="bool" PType="258" IoType="17">0</IsUploading>
\t\t\t\t\t<UploadComplete Type="bool" PType="258" IoType="17">0</UploadComplete>
\t\t\t\t\t<MissedHeartbeats Type="int" PType="258" IoType="17">0</MissedHeartbeats>
\t\t\t\t\t<RequestHealthCheck Type="bool" PType="258" IoType="17">0</RequestHealthCheck>
\t\t\t\t\t<UploadFirmwareFlag Type="bool" PType="258" IoType="17">0</UploadFirmwareFlag>
\t\t\t\t\t<UploadProgress Type="int" PType="258" IoType="17">0</UploadProgress>
\t\t\t\t\t<UploadLastResult Type="std::string" PType="258" IoType="17"></UploadLastResult>
\t\t\t\t\t<HardwareSetupPath Type="std::string" PType="257" IoType="17">{setup_path}</HardwareSetupPath>
\t\t\t\t\t<HardwareSetupJson Type="std::string" PType="257" IoType="17"></HardwareSetupJson>
\t\t\t\t\t<HardwareSetupValid Type="bool" PType="258" IoType="17">1</HardwareSetupValid>
\t\t\t\t\t<HardwareSetupIssues Type="std::string" PType="258" IoType="17"></HardwareSetupIssues>
"""

CUSTOM_LINK_EXTRA = """\
\t\t\t\t\t<Command Type="std::string" PType="257" IoType="17"></Command>
\t\t\t\t\t<SendCommand Type="bool" PType="257" IoType="17">0</SendCommand>
\t\t\t\t\t<RequestGetStatus Type="bool" PType="257" IoType="17">0</RequestGetStatus>
\t\t\t\t\t<RequestProtocolNegotiate Type="bool" PType="257" IoType="17">0</RequestProtocolNegotiate>
\t\t\t\t\t<ProtocolVersion Type="int" PType="257" IoType="17">{proto}</ProtocolVersion>
\t\t\t\t\t<SendCommandFlag Type="bool" PType="258" IoType="17">0</SendCommandFlag>
\t\t\t\t\t<SentCommand Type="std::string" PType="258" IoType="17"></SentCommand>
\t\t\t\t\t<InputCommand Type="std::string" PType="258" IoType="17"></InputCommand>
\t\t\t\t\t<RxFrameCount Type="int" PType="258" IoType="17">0</RxFrameCount>
\t\t\t\t\t<TxCommandCount Type="int" PType="258" IoType="17">0</TxCommandCount>
\t\t\t\t\t<IsProtocolReady Type="bool" PType="258" IoType="17">0</IsProtocolReady>
\t\t\t\t\t<HasPendingCommands Type="bool" PType="258" IoType="17">0</HasPendingCommands>
\t\t\t\t\t<LastSentCommand Type="std::string" PType="258" IoType="17"></LastSentCommand>
"""

SKETCH_EXTRA = CUSTOM_LINK_EXTRA + """\
\t\t\t\t\t<LowerSensorLimit Type="double" PType="257" IoType="17">-100</LowerSensorLimit>
\t\t\t\t\t<UpperSensorLimit Type="double" PType="257" IoType="17">100</UpperSensorLimit>
\t\t\t\t\t<MatrixCols Type="int" PType="257" IoType="17">100</MatrixCols>
\t\t\t\t\t<GetDataFromBuffers Type="bool" PType="258" IoType="17">0</GetDataFromBuffers>
\t\t\t\t\t<GetPinsInfo Type="bool" PType="258" IoType="17">0</GetPinsInfo>
\t\t\t\t\t<DoubleMatrixReadings Type="MDMatrix&lt;double&gt;" Rows="4" Cols="100" PType="258" IoType="17">
</DoubleMatrixReadings>
\t\t\t\t\t<PinStatusJson Type="std::string" PType="258" IoType="17"></PinStatusJson>
"""

FIRMATA_EXTRA = """\
\t\t\t\t\t<SelectedPin Type="int" PType="257" IoType="17">13</SelectedPin>
\t\t\t\t\t<SelectedPinMode Type="int" PType="257" IoType="17">1</SelectedPinMode>
\t\t\t\t\t<DigitalPinValue Type="int" PType="257" IoType="17">0</DigitalPinValue>
\t\t\t\t\t<AutoRefreshPins Type="bool" PType="257" IoType="17">0</AutoRefreshPins>
\t\t\t\t\t<StreamLogEnable Type="bool" PType="257" IoType="17">0</StreamLogEnable>
\t\t\t\t\t<SetPinMode Type="bool" PType="265" IoType="17">0</SetPinMode>
\t\t\t\t\t<WriteDigital Type="bool" PType="265" IoType="17">0</WriteDigital>
\t\t\t\t\t<ReadAnalog Type="bool" PType="265" IoType="17">0</ReadAnalog>
\t\t\t\t\t<FirmataReady Type="bool" PType="258" IoType="17">0</FirmataReady>
\t\t\t\t\t<FirmataFirmwareVersion Type="std::string" PType="258" IoType="17"></FirmataFirmwareVersion>
\t\t\t\t\t<AnalogPinValue Type="int" PType="258" IoType="17">0</AnalogPinValue>
\t\t\t\t\t<PinStatusJson Type="std::string" PType="258" IoType="17"></PinStatusJson>
\t\t\t\t\t<AnalogSamples Type="MDMatrix&lt;double&gt;" Rows="0" Cols="4" PType="274" IoType="17"></AnalogSamples>
\t\t\t\t\t<DigitalSamples Type="MDMatrix&lt;double&gt;" Rows="0" Cols="3" PType="274" IoType="17"></DigitalSamples>
\t\t\t\t\t<SetPinModeFlag Type="bool" PType="258" IoType="17">0</SetPinModeFlag>
\t\t\t\t\t<ReadAnalogFlag Type="bool" PType="258" IoType="17">0</ReadAnalogFlag>
\t\t\t\t\t<WriteDigitalFlag Type="bool" PType="258" IoType="17">0</WriteDigitalFlag>
"""

# Override AutoRefreshPins=1 without duplicating the property element.
FIRMATA_ANALOG_LINK_EXTRA = FIRMATA_EXTRA.replace(
    '">0</AutoRefreshPins>',
    '">1</AutoRefreshPins>',
    1,
)

ADC_LINK_PROPS = """\
\t\t\t\t\t<LinkedFirmataName Type="std::string" PType="257" IoType="17">Firmata</LinkedFirmataName>
\t\t\t\t\t<AnalogPin Type="int" PType="257" IoType="17">14</AnalogPin>
\t\t\t\t\t<BoardProfile Type="int" PType="257" IoType="17">{board_profile}</BoardProfile>
\t\t\t\t\t<UseLinkedAnalogSamples Type="bool" PType="257" IoType="17">1</UseLinkedAnalogSamples>
\t\t\t\t\t<AdcValue Type="int" PType="258" IoType="17">0</AdcValue>
\t\t\t\t\t<ReadAdcFlag Type="bool" PType="265" IoType="17">0</ReadAdcFlag>
"""

ADC_PROPS = """\
\t\t\t\t\t<LinkedFirmataName Type="std::string" PType="257" IoType="17">Firmata</LinkedFirmataName>
\t\t\t\t\t<AnalogPin Type="int" PType="257" IoType="17">14</AnalogPin>
\t\t\t\t\t<AdcValue Type="int" PType="258" IoType="17">0</AdcValue>
\t\t\t\t\t<ReadAdcFlag Type="bool" PType="258" IoType="17">0</ReadAdcFlag>
"""

DEVICE_IO_PROPS = """\
\t\t\t\t\t<LinkedFirmataName Type="std::string" PType="257" IoType="17">Firmata</LinkedFirmataName>
\t\t\t\t\t<ModuleId Type="std::string" PType="257" IoType="17">{module}</ModuleId>
\t\t\t\t\t<DeviceId Type="std::string" PType="257" IoType="17">{device_id}</DeviceId>
\t\t\t\t\t<Port Type="std::string" PType="257" IoType="17">{port}</Port>
\t\t\t\t\t<Channel Type="std::string" PType="257" IoType="17">{channel}</Channel>
\t\t\t\t\t<Role Type="int" PType="257" IoType="17">{role}</Role>
\t\t\t\t\t<BoardProfile Type="int" PType="257" IoType="17">{board_profile}</BoardProfile>
\t\t\t\t\t<HardwareSetupPath Type="std::string" PType="257" IoType="17">{setup_path}</HardwareSetupPath>
\t\t\t\t\t<Value Type="double" PType="274" IoType="17">0</Value>
\t\t\t\t\t<ValueRaw Type="int" PType="258" IoType="17">0</ValueRaw>
\t\t\t\t\t<ValueIn Type="double" PType="265" IoType="17">0</ValueIn>
\t\t\t\t\t<InputMode Type="int" PType="257" IoType="17">0</InputMode>
\t\t\t\t\t<IsOnline Type="bool" PType="258" IoType="17">0</IsOnline>
\t\t\t\t\t<LastError Type="std::string" PType="258" IoType="17"></LastError>
\t\t\t\t\t<ApplyConfig Type="bool" PType="265" IoType="17">0</ApplyConfig>
\t\t\t\t\t<WriteOutput Type="bool" PType="265" IoType="17">0</WriteOutput>
\t\t\t\t\t<ReadInput Type="bool" PType="265" IoType="17">0</ReadInput>
\t\t\t\t\t<Continuous Type="bool" PType="257" IoType="17">1</Continuous>
"""

DC_PROPS = CUSTOM_LINK_EXTRA.format(proto=1) + """\
\t\t\t\t\t<Speed Type="float" PType="258" IoType="17">0</Speed>
\t\t\t\t\t<Acceleration Type="float" PType="258" IoType="17">0</Acceleration>
\t\t\t\t\t<GetSpeed Type="bool" PType="257" IoType="17">0</GetSpeed>
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

## Плата Uno vs Mega 2560

- Свойство `BoardProfile`: **0** = Arduino Uno, **1** = Arduino Mega 2560.
- Bundled HEX (`BundledFirmwareId`) выбирается по профилю (см. `Bin/ArduinoFirmware/manifest.json`).
- Перед **Upload** на Mega установите профиль **1** в GUI (Board) или включите авто-детект при выборе COM.
- Конфиги в этом каталоге по умолчанию используют **Uno (0)**.

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
    board_profile: int = 0,
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
    board_profile = 0

    board = BOARD_PROPS.format(
        port=port, bundled="sensor_lab_v1", board_profile=board_profile, setup_path=""
    )
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

    firmata_board = BOARD_PROPS.format(
        port=port, bundled="standard_firmata", board_profile=board_profile, setup_path=""
    ) + FIRMATA_EXTRA
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

    dc_demo = BOARD_PROPS.format(
        port=port, bundled="sensor_lab_v1", board_profile=board_profile, setup_path=""
    ) + DC_PROPS
    write_project(
        "05-ArduinoDcDemo",
        "Hardware test: ArduinoDcDemo",
        "Проверка `ArduinoDcDemo`: один узел CustomLink + DC (sensor_lab_v1), edge Connect/SendCommand/GetSpeed.",
        "- `DcDemo` (`ArduinoDcDemo`) — порт, прошивка, команды DC без LinkedSketchName.",
        component_block("DcDemo", "ArduinoDcDemo", "8 12 0", dc_demo),
        port,
    )

    firmata_link = BOARD_PROPS.format(
        port=port, bundled="standard_firmata", board_profile=board_profile, setup_path=""
    ) + FIRMATA_ANALOG_LINK_EXTRA
    adc_link_props = ADC_LINK_PROPS.format(board_profile=board_profile)
    adc_link_body = (
        component_block("Firmata", "ArduinoFirmata", "12 4 0", firmata_link)
        + component_block(
            "Adc", "ArduinoAdc", "12 8 0", UNET_BASE.format(coord="12 8 0") + adc_link_props
        )
    )
    dest08 = OUT / "08-ArduinoFirmata-AnalogLink"
    dest08.mkdir(parents=True, exist_ok=True)
    (dest08 / "Model_00.xml").write_text(MODEL_HEADER + adc_link_body + MODEL_FOOTER, encoding="utf-8")
    (dest08 / "Parameters_00.xml").write_text(PARAM_HEADER + adc_link_body + PARAM_FOOTER, encoding="utf-8")
    (dest08 / "Project.ini").write_text(
        PROJECT_INI.format(name="Hardware test: Firmata AnalogSamples link"), encoding="utf-8"
    )
    (dest08 / "Interface.xml").write_text(INTERFACE_XML, encoding="utf-8")
    (dest08 / "README.md").write_text(
        README_TEMPLATE.format(
            title="Hardware test: Firmata AnalogSamples link",
            folder="08-ArduinoFirmata-AnalogLink",
            purpose="Firmata с `AutoRefreshPins` + `ArduinoAdc.UseLinkedAnalogSamples` для проверки link на `AnalogSamples`.",
            components="- `Firmata` + `Adc` (linked samples, A0 = pin 14).",
        ),
        encoding="utf-8",
    )

    write_project(
        "07-ArduinoPropertyEdges",
        "Hardware test: Arduino property edges",
        "Ручная проверка edge-свойств Board: в XML edges = 0; импульс Connect/UploadFirmware из GUI или Property editor.",
        "- `Board` (`ArduinoBoard`) — edges по умолчанию 0; пульсируйте `Connect` / `UploadFirmware` вручную.",
        component_block("Board", "ArduinoBoard", "8 4 0", board),
        port,
    )

    setup_rel = "../_shared/HardwareSetup.json"
    firmata_setup = BOARD_PROPS.format(
        port=port,
        bundled="standard_firmata",
        board_profile=board_profile,
        setup_path=setup_rel,
    ) + FIRMATA_EXTRA
    write_project(
        "09-HardwareSetup-SensorShield",
        "Hardware test: Hardware Setup + Assembly",
        "Board/Firmata с `HardwareSetupPath` на Sensor Shield + pot/servo; откройте вкладку Assembly.",
        "- `Firmata` — `HardwareSetupPath=../_shared/HardwareSetup.json`, firmware `standard_firmata`.",
        component_block("Firmata", "ArduinoFirmata", "16 4 0", firmata_setup),
        port,
    )

    setup_rel = "../_shared/HardwareSetup.json"
    dio_common = dict(board_profile=board_profile, setup_path=setup_rel, channel="")
    pot_body = (
        component_block("Firmata", "ArduinoFirmata", "12 4 0", firmata_setup)
        + component_block(
            "Pot",
            "ArduinoDeviceIO",
            "12 8 0",
            UNET_BASE.format(coord="12 8 0")
            + DEVICE_IO_PROPS.format(
                module="potentiometer", device_id="pot1", port="A0", role=0, **dio_common
            ),
        )
    )
    dest10 = OUT / "10-DeviceIO-Potentiometer"
    dest10.mkdir(parents=True, exist_ok=True)
    (dest10 / "Model_00.xml").write_text(MODEL_HEADER + pot_body + MODEL_FOOTER, encoding="utf-8")
    (dest10 / "Parameters_00.xml").write_text(PARAM_HEADER + pot_body + PARAM_FOOTER, encoding="utf-8")
    (dest10 / "Project.ini").write_text(
        PROJECT_INI.format(name="Hardware test: DeviceIO Potentiometer"), encoding="utf-8"
    )
    (dest10 / "Interface.xml").write_text(INTERFACE_XML, encoding="utf-8")
    (dest10 / "README.md").write_text(
        README_TEMPLATE.format(
            title="Hardware test: DeviceIO Potentiometer",
            folder="10-DeviceIO-Potentiometer",
            purpose="Firmata + DeviceIO potentiometer A0; Upload standard_firmata, ApplyHardwareSetup, Continuous Value.",
            components="- `Firmata` + `Pot` (`ArduinoDeviceIO`, ModuleId=potentiometer).",
        ),
        encoding="utf-8",
    )

    servo_body = (
        component_block("Firmata", "ArduinoFirmata", "12 4 0", firmata_setup)
        + component_block(
            "Servo",
            "ArduinoDeviceIO",
            "12 8 0",
            UNET_BASE.format(coord="12 8 0")
            + DEVICE_IO_PROPS.format(
                module="servo", device_id="servo1", port="D9", role=1, **dio_common
            ),
        )
    )
    write_project(
        "11-DeviceIO-Servo",
        "Hardware test: DeviceIO Servo",
        "Firmata + DeviceIO servo D9; ValueIn 0..1 → угол.",
        "- `Firmata` + `Servo` (`ArduinoDeviceIO`).",
        servo_body,
        port,
    )

    motor_setup_path = "../_shared/MotorShieldR3Setup.json"
    motor_firmata = BOARD_PROPS.format(
        port=port,
        bundled="standard_firmata",
        board_profile=board_profile,
        setup_path=motor_setup_path,
    ) + FIRMATA_EXTRA
    motor_body = (
        component_block("Firmata", "ArduinoFirmata", "8 4 0", motor_firmata)
        + component_block(
            "MotorA",
            "ArduinoDeviceIO",
            "8 8 0",
            UNET_BASE.format(coord="8 8 0")
            + DEVICE_IO_PROPS.format(
                module="dc_motor_channel",
                device_id="mA",
                port="",
                channel="A",
                role=1,
                board_profile=board_profile,
                setup_path=motor_setup_path,
            ),
        )
        + component_block(
            "MotorB",
            "ArduinoDeviceIO",
            "8 12 0",
            UNET_BASE.format(coord="8 12 0")
            + DEVICE_IO_PROPS.format(
                module="dc_motor_channel",
                device_id="mB",
                port="",
                channel="B",
                role=1,
                board_profile=board_profile,
                setup_path=motor_setup_path,
            ),
        )
    )
    dest12 = OUT / "12-MotorShield-R3"
    dest12.mkdir(parents=True, exist_ok=True)
    (dest12 / "Model_00.xml").write_text(MODEL_HEADER + motor_body + MODEL_FOOTER, encoding="utf-8")
    (dest12 / "Parameters_00.xml").write_text(PARAM_HEADER + motor_body + PARAM_FOOTER, encoding="utf-8")
    (dest12 / "Project.ini").write_text(
        PROJECT_INI.format(name="Hardware test: Motor Shield R3"), encoding="utf-8"
    )
    (dest12 / "Interface.xml").write_text(INTERFACE_XML, encoding="utf-8")
    (dest12 / "README.md").write_text(
        README_TEMPLATE.format(
            title="Hardware test: Motor Shield R3",
            folder="12-MotorShield-R3",
            purpose="Firmata + 2× DeviceIO dc_motor_channel A/B. Для Seeed смените setup на MotorShieldSeeedSetup.json.",
            components="- `Firmata` + `MotorA`/`MotorB`.",
        ),
        encoding="utf-8",
    )

    pulse_body = (
        component_block("Firmata", "ArduinoFirmata", "8 4 0", firmata_setup)
        + component_block(
            "Pot",
            "ArduinoDeviceIO",
            "8 8 0",
            UNET_BASE.format(coord="8 8 0")
            + DEVICE_IO_PROPS.format(
                module="potentiometer", device_id="pot1", port="A0", role=0, **dio_common
            ),
        )
        + component_block(
            "Btn",
            "ArduinoDeviceIO",
            "8 12 0",
            UNET_BASE.format(coord="8 12 0")
            + DEVICE_IO_PROPS.format(
                module="button", device_id="btn1", port="D2", role=0, **dio_common
            ),
        )
    )
    dest13 = OUT / "13-Sensors-To-Pulse"
    dest13.mkdir(parents=True, exist_ok=True)
    (dest13 / "Model_00.xml").write_text(MODEL_HEADER + pulse_body + MODEL_FOOTER, encoding="utf-8")
    (dest13 / "Parameters_00.xml").write_text(PARAM_HEADER + pulse_body + PARAM_FOOTER, encoding="utf-8")
    (dest13 / "Project.ini").write_text(
        PROJECT_INI.format(name="Hardware test: Sensors to network"), encoding="utf-8"
    )
    (dest13 / "Interface.xml").write_text(INTERFACE_XML, encoding="utf-8")
    (dest13 / "README.md").write_text(
        README_TEMPLATE.format(
            title="Hardware test: Sensors to network",
            folder="13-Sensors-To-Pulse",
            purpose="DeviceIO pot/button → Value; добавьте Watch/PulseLib downstream вручную.",
            components="- `Firmata` + `Pot` + `Btn`.",
        ),
        encoding="utf-8",
    )

    index = OUT / "README.md"
    index.write_text(
        textwrap.dedent(
            """\
            # Hardware — тестовые конфигурации Rdk-HardwareLib

            Набор минимальных проектов для ручной проверки компонентов Arduino на плате.

            | Каталог | ClassName | Прошивка | Default BP |
            |---------|-----------|----------|------------|
            | [01-ArduinoBoard](01-ArduinoBoard/) | `ArduinoBoard` | sensor_lab_v1 | Uno (0) |
            | [02-ArduinoSensorSketch](02-ArduinoSensorSketch/) | `ArduinoSensorSketch` | sensor_lab_v1 | Uno (0) |
            | [03-ArduinoFirmata](03-ArduinoFirmata/) | `ArduinoFirmata` | standard_firmata | Uno (0) |
            | [04-ArduinoAdc](04-ArduinoAdc/) | `ArduinoAdc` + `ArduinoFirmata` | standard_firmata | Uno (0) |
            | [05-ArduinoDcDemo](05-ArduinoDcDemo/) | `ArduinoDcDemo` (single node) | sensor_lab_v1 | Uno (0) |
            | [06-ArduinoSensorSketch-Proto2](06-ArduinoSensorSketch-Proto2/) | `ArduinoSensorSketch` (v2) | sensor_lab_v1 | Uno (0) |
            | [07-ArduinoPropertyEdges](07-ArduinoPropertyEdges/) | `ArduinoBoard` (edge API) | sensor_lab_v1 | Uno (0) |
            | [08-ArduinoFirmata-AnalogLink](08-ArduinoFirmata-AnalogLink/) | `ArduinoFirmata` + `ArduinoAdc` | standard_firmata | Uno (0) |
            | [09-HardwareSetup-SensorShield](09-HardwareSetup-SensorShield/) | `ArduinoFirmata` + HardwareSetup | standard_firmata | Uno (0) |
            | [10-DeviceIO-Potentiometer](10-DeviceIO-Potentiometer/) | `ArduinoDeviceIO` | standard_firmata | Uno (0) |
            | [11-DeviceIO-Servo](11-DeviceIO-Servo/) | `ArduinoDeviceIO` | standard_firmata | Uno (0) |
            | [12-MotorShield-R3](12-MotorShield-R3/) | `ArduinoDeviceIO` motor | standard_firmata | Uno (0) |
            | [13-Sensors-To-Pulse](13-Sensors-To-Pulse/) | DeviceIO sensors | standard_firmata | Uno (0) |

            **BoardProfile:** 0 = Uno, 1 = Mega 2560. Перед Upload на Mega выберите профиль 1 или авто-детект в GUI.

            Перед тестом задайте `PortName` и следуйте [чеклисту](../../../../Libraries/Rdk-HardwareLib/Firmware/README.md).

            Генерация: `Scripts/generate_arduino_hardware_configs.py`  
            Миграция legacy DC: `Scripts/migrate_arduino_board_hierarchy.py`
            """
        ),
        encoding="utf-8",
    )
    print(f"Generated configs under {OUT}")


if __name__ == "__main__":
    main()
