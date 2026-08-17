#!/usr/bin/env python3
"""Generate Bin/Configs/SpikeSamples/Hardware/* test projects for Rdk-HardwareLib."""

from __future__ import annotations

import argparse
import json
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

CUSTOM_FW_EXTRA = CUSTOM_LINK_EXTRA + """\
\t\t\t\t\t<HostPluginId Type="std::string" PType="257" IoType="17">{plugin}</HostPluginId>
\t\t\t\t\t<ClearFrameLog Type="bool" PType="257" IoType="17">0</ClearFrameLog>
\t\t\t\t\t<FrameLog Type="std::string" PType="258" IoType="17"></FrameLog>
\t\t\t\t\t<NamedValuesJson Type="std::string" PType="258" IoType="17">{{}}</NamedValuesJson>
\t\t\t\t\t<PluginBound Type="bool" PType="258" IoType="17">0</PluginBound>
\t\t\t\t\t<DoubleMatrixReadings Type="MDMatrix&lt;double&gt;" Rows="0" Cols="8" PType="258" IoType="17"></DoubleMatrixReadings>
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
\t\t\t\t\t<AnalogPin Type="int" PType="257" IoType="17">{analog_pin}</AnalogPin>
\t\t\t\t\t<BoardProfile Type="int" PType="257" IoType="17">{board_profile}</BoardProfile>
\t\t\t\t\t<UseLinkedAnalogSamples Type="bool" PType="257" IoType="17">1</UseLinkedAnalogSamples>
\t\t\t\t\t<AdcValue Type="int" PType="258" IoType="17">0</AdcValue>
\t\t\t\t\t<ReadAdcFlag Type="bool" PType="265" IoType="17">0</ReadAdcFlag>
"""

ADC_PROPS = """\
\t\t\t\t\t<LinkedFirmataName Type="std::string" PType="257" IoType="17">Firmata</LinkedFirmataName>
\t\t\t\t\t<AnalogPin Type="int" PType="257" IoType="17">{analog_pin}</AnalogPin>
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

INTERFACE_XML = """\
<Interfaces>
\t<UGEngineControlForm>
\t\t<UComponentsListFrame1>
\t\t\t<UpdateInterval>-1</UpdateInterval>
\t\t\t<ComponentControlName></ComponentControlName>
\t\t\t<AlwaysUpdateFlag>0</AlwaysUpdateFlag>
\t\t</UComponentsListFrame1>
\t\t<UComponentsPerformanceFrame1>
\t\t\t<ShowModeRadioGroup>0</ShowModeRadioGroup>
\t\t\t<UpdateInterval>1000</UpdateInterval>
\t\t\t<ComponentControlName></ComponentControlName>
\t\t\t<AlwaysUpdateFlag>0</AlwaysUpdateFlag>
\t\t</UComponentsPerformanceFrame1>
\t\t<UDrawEngineFrame1>
\t\t\t<FontFileName></FontFileName>
\t\t\t<CanvasWidth>1280</CanvasWidth>
\t\t\t<CanvasHeight>720</CanvasHeight>
\t\t\t<FontType>Tahoma</FontType>
\t\t\t<FontSize>16</FontSize>
\t\t\t<RectWidth>100</RectWidth>
\t\t\t<RectHeight>25</RectHeight>
\t\t\t<ShowLinksDetail>0</ShowLinksDetail>
\t\t\t<UpdateInterval>-1</UpdateInterval>
\t\t\t<ComponentControlName></ComponentControlName>
\t\t\t<AlwaysUpdateFlag>0</AlwaysUpdateFlag>
\t\t</UDrawEngineFrame1>
\t\t<AutoupdateProperties>0</AutoupdateProperties>
\t\t<Pages/>
\t\t<PageCount>0</PageCount>
\t\t<FormPosition>
\t\t\t<Left>0</Left>
\t\t\t<Top>0</Top>
\t\t\t<Width>1280</Width>
\t\t\t<Height>800</Height>
\t\t\t<Visible>1</Visible>
\t\t\t<WindowState>0</WindowState>
\t\t</FormPosition>
\t\t<ComponentControlName></ComponentControlName>
\t\t<UpdateInterval>1000</UpdateInterval>
\t\t<AlwaysUpdateFlag>0</AlwaysUpdateFlag>
\t</UGEngineControlForm>
</Interfaces>
"""

README_TEMPLATE = """\
# {title}

**Путь:** `Bin/Configs/SpikeSamples/Hardware/{folder}`

Общий HOWTO Firmata: [LAB-Firmata.md](../LAB-Firmata.md).

## Назначение

{purpose}

## BOM

{bom}

## Проводка

{wiring}

{media}

## Перед запуском

1. Подключите плату по USB. По умолчанию генератор пишет `PortName={port}`, `BoardProfile={board_profile}` ({board_title}).
2. Откройте `Project.ini` в NeuroModeler.
3. Клик по узлу **Firmata** (или Board) → вкладки **Assembly** / **Pinout** / **Pins** / **Monitor** / **Board**.
4. **Upload** bundled `standard_firmata` (если ещё не прошито) → **Connect** → дождитесь `FirmataReady`.
5. Для DeviceIO: **ApplyConfig**, затем Continuous / Calculate.

## Компоненты

{components}

## Схема Assembly

{assembly}

## Критерий успеха

{success}

Тексты BOM/проводки — пересказ открытых Arduino docs ([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)), не копипаст гайдов. Firmata: [firmata/arduino](https://github.com/firmata/arduino) (LGPL-2.1, в документ не вставляем `.ino`).
"""

README_SIMPLE = """\
# {title}

**Путь:** `Bin/Configs/SpikeSamples/Hardware/{folder}`

## Назначение

{purpose}

## Перед запуском

1. Подключите Arduino по USB.
2. Свойства по умолчанию: `PortName={port}`, `BoardProfile={board_profile}` ({board_title}).
3. Connect / Upload из GUI при необходимости.
4. Чеклист: `Libraries/Rdk-HardwareLib/Firmware/README.md`.

## Компоненты

{components}

## Проверка

Открыть проект в NeuroModeler → Build / Reset / Calculate.
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


def media_caption(prefix: str) -> str:
    return (
        f"![Arduino Mega 2560 Rev3]({prefix}Arduino_MEGA2560.png)\n\n"
        f"*Arduino, [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), "
        f"[Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Arduino_MEGA2560.png). "
        f"Pinout PDF: [Mega A000067]({prefix}A000067-full-pinout.pdf) / "
        f"[Uno A000066]({prefix}A000066-full-pinout.pdf) (Arduino, CC BY-SA 4.0).*\n"
    )


MEDIA_CAPTION = media_caption("../_shared/media/")

WIRING_POT = (
    "Потенциометр: крайние выводы на 5V и GND, средний (wiper) на **A0**. "
    "См. [Analog Input](https://docs.arduino.cc/built-in-examples/analog/AnalogInput/) "
    "(Arduino docs, CC BY-SA 4.0)."
)
WIRING_SERVO = (
    "Сервопривод: сигнал на **D9** (PWM), питание 5V, земля GND. "
    "Внешнее питание серво — если ток больше, чем даёт USB. "
    "См. [Servo](https://docs.arduino.cc/learn/electronics/servo-motors/) (Arduino docs, CC BY-SA 4.0)."
)
WIRING_LED_D13 = (
    "Встроенный светодиод платы на **D13** (Uno/Mega). Дополнительная проводка не нужна. "
    "См. [Digital Pins](https://docs.arduino.cc/learn/microcontrollers/digital-pins/) (Arduino docs, CC BY-SA 4.0)."
)
WIRING_PWM_LED = (
    "Потенциометр на **A0** (как в лабе 10). Светодиод: анод через резистор **~220 Ω** на **D9** (PWM), катод на GND. "
    "Сценарий как в [Analog In, Out Serial](https://docs.arduino.cc/built-in-examples/analog/AnalogInOutSerial/) "
    "(Arduino docs, CC BY-SA 4.0)."
)
WIRING_BUTTON = (
    "Кнопка на **D2**: один контакт на D2, второй на GND; либо D2–кнопка–5V с подтяжкой. "
    "См. [Button](https://docs.arduino.cc/built-in-examples/digital/Button/) (Arduino docs, CC BY-SA 4.0)."
)
WIRING_MOTOR = (
    "Наденьте Arduino Motor Shield R3 на плату, моторы в клеммы A/B. USB не тянет большие токи — "
    "внешнее питание шилда. Не оставляйте `ValueIn` > 0 надолго без нагрузки. "
    "См. [Motor Shield Rev3](https://docs.arduino.cc/hardware/motor-shield-rev3/) (Arduino docs, CC BY-SA 4.0)."
)


def analog_firmata_pin(board_profile: int) -> int:
    return 54 if board_profile == 1 else 14


def board_id_for_profile(board_profile: int) -> str:
    return "mega2560" if board_profile == 1 else "uno"


def board_title_for_profile(board_profile: int) -> str:
    return "Arduino Mega 2560" if board_profile == 1 else "Arduino Uno"


def setup_json(board: str, firmware: str, stack: list[str], devices: list[dict]) -> str:
    payload = {
        "schemaVersion": 1,
        "board": board,
        "firmwareId": firmware,
        "stack": stack,
        "devices": devices,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def write_setup_pair(shared: Path, stem: str, firmware: str, stack: list[str], devices: list[dict]) -> None:
    for board in ("uno", "mega2560"):
        (shared / f"{stem}-{board}.json").write_text(
            setup_json(board, firmware, stack, devices), encoding="utf-8"
        )


def media_block(out_root: Path) -> str:
    mega = out_root / "_shared/media/Arduino_MEGA2560.png"
    if mega.is_file():
        return MEDIA_CAPTION
    return (
        "Превью платы: положите CC-фото в `_shared/media/` "
        "(скрипт `Scripts/download_hardware_lab_assets.py`).\n"
    )


def dio_block(
    name: str,
    coord: str,
    *,
    module: str,
    device_id: str,
    port: str,
    role: int,
    board_profile: int,
    setup_path: str,
    channel: str = "",
) -> str:
    return component_block(
        name,
        "ArduinoDeviceIO",
        coord,
        DEVICE_IO_PROPS.format(
            module=module,
            device_id=device_id,
            port=port,
            channel=channel,
            role=role,
            board_profile=board_profile,
            setup_path=setup_path,
        ),
    )


def write_project(
    folder: str,
    title: str,
    purpose: str,
    components_desc: str,
    components_xml: str,
    *,
    port: str,
    board_profile: int,
    firmata_lab: bool = False,
    bom: str = "Плата Arduino + USB-кабель.",
    wiring: str = "Только USB.",
    assembly: str = "Вкладка **Assembly** у узла Firmata (если задан HardwareSetupPath).",
    success: str = "Нет ошибок связи, свойства обновляются.",
    out_root: Path | None = None,
) -> None:
    dest_root = out_root or OUT
    dest = dest_root / folder
    dest.mkdir(parents=True, exist_ok=True)
    body = components_xml
    (dest / "Model_00.xml").write_text(MODEL_HEADER + body + MODEL_FOOTER, encoding="utf-8")
    (dest / "Parameters_00.xml").write_text(PARAM_HEADER + body + PARAM_FOOTER, encoding="utf-8")
    (dest / "Project.ini").write_text(PROJECT_INI.format(name=title), encoding="utf-8")
    (dest / "Interface.xml").write_text(INTERFACE_XML, encoding="utf-8")
    ctx = dict(
        title=title,
        folder=folder,
        purpose=purpose,
        components=components_desc,
        port=port,
        board_profile=board_profile,
        board_title=board_title_for_profile(board_profile),
    )
    if firmata_lab:
        ctx.update(
            bom=bom,
            wiring=wiring,
            media=media_block(dest_root),
            assembly=assembly,
            success=success,
        )
        (dest / "README.md").write_text(README_TEMPLATE.format(**ctx), encoding="utf-8")
    else:
        (dest / "README.md").write_text(README_SIMPLE.format(**ctx), encoding="utf-8")


def write_lab_firmata_md(port: str, board_profile: int, out_root: Path) -> None:
    board = board_title_for_profile(board_profile)
    analog_pin = analog_firmata_pin(board_profile)
    body = textwrap.dedent(
        f"""\
        # Лабораторные конфиги StandardFirmata

        Сценарий: открыли `Project.ini` → увидели схему **Assembly** → собрали по BOM →
        Upload / Connect / ApplyConfig → увидели результат в **Monitor**, инспекторе `Value` / `ValueIn`
        или на светодиоде платы.

        Hub-сэмплы 14–16 **не** входят в этот документ (не StandardFirmata).

        ## Общие шаги (один раз)

        1. NeuroModeler → открыть `Bin/Configs/SpikeSamples/Hardware/<каталог>/Project.ini`.
        2. На канвасе клик по узлу **Firmata**. Виджет: **Assembly** | **Pinout** | **Pins** | **Monitor** | **Board**.
        3. Вкладка **Board**: `PortName` = `{port}`, `BoardProfile` = **{board_profile}** ({board}).
        4. **Upload** bundled firmware `standard_firmata` (если плата ещё без StandardFirmata).
        5. **Connect**. Дождаться `FirmataReady` / handshake.
        6. Собрать схему по вкладке **Assembly** и BOM карточки (если нужны внешние детали).
        7. DeviceIO: **ApplyConfig**, затем Continuous / Calculate. Результат — не Watch: вкладка
           **Monitor**, свойство `Value` / `ValueIn`, светодиод D13 / серво / мотор.

        Без датчиков на столе проверяются только **03** и **17**.

        Генерация: `python Scripts/generate_arduino_hardware_configs.py --port {port} --board-profile {board_profile}`

        __MEDIA__

        ## Карточки конфигов

        ### 03-ArduinoFirmata — пульт пинов

        - **BOM:** плата + USB.
        - **Assembly:** setup не задан; смотрите **Pinout** / **Pins**.
        - **Шаги:** Upload → Connect → Pins: D13 OUTPUT, WriteDigital 1.
        - **Успех:** handshake, встроенный светодиод D13 реагирует с пульта Pins; Monitor показывает сэмплы.

        ### 17-DeviceIO-LED — встроенный светодиод

        - **BOM:** плата + USB (датчики не нужны).
        - **Assembly:** модуль `led` на D13.
        - **Шаги:** Connect → ApplyConfig на `Led` → `Led.ValueIn` = 1.
        - **Успех:** светодиод D13 горит при `ValueIn` ≥ 0.5, гаснет при 0.

        ### 18-DeviceIO-PotToPwmLed — потенциометр → PWM LED

        - **BOM:** потенциометр, светодиод, резистор ~220 Ω, провода.
        - **Assembly:** `potentiometer` A0 + `pwm_led` D9.
        - **Шаги:** собрать как Analog In/Out → Connect → ApplyConfig → Continuous; крутить A0.
        - **Успех:** `Pot.Value` 0..1, яркость LED на D9 следует за потенциометром.

        ### 08-ArduinoFirmata-AnalogLink — AnalogSamples → Adc

        - **BOM:** потенциометр на A0.
        - **Assembly:** нет DeviceIO; Firmata + Adc.
        - **Успех:** `Adc.AdcValue` / `Firmata.AnalogSamples` меняются при вращении (A0 = Firmata pin {analog_pin}).

        ### 09-HardwareSetup-SensorShield — только схема

        - **BOM:** как 10+11 (pot A0, servo D9), но IO-узлов нет.
        - **Assembly:** Sensor Shield + pot + servo.
        - **Успех:** схема на вкладке Assembly; IO читайте в лабах 10/11.

        ### 10-DeviceIO-Potentiometer

        - **BOM:** потенциометр A0.
        - **Успех:** `Pot.Value` меняется 0..1 в инспекторе / Continuous.

        ### 11-DeviceIO-Servo

        - **BOM:** сервопривод D9.
        - **Успех:** `Servo.ValueIn` 0..1 поворачивает вал (0 → ~0°, 1 → ~180°).

        ### 12-MotorShield-R3

        - **BOM:** Arduino Motor Shield R3 + 1–2 DC-мотора, внешнее питание шилда.
        - **Успех:** короткий импульс `MotorA.ValueIn` крутит канал A. Не держите PWM > 0 долго без мотора/радиатора.
        - Seeed: смените `HardwareSetupPath` на `../_shared/MotorShieldSeeedSetup.json`.

        ### 13-Sensors-To-Pulse — pot + кнопка

        - **BOM:** потенциометр A0 + кнопка D2.
        - **Успех:** `Pot.Value` и `Btn.Value` в инспекторе; Monitor Firmata. Watch добавлять не нужно.

        ## Источники

        - Arduino docs: [docs.arduino.cc](https://docs.arduino.cc/) — **CC BY-SA 4.0**
          ([LICENSE](https://github.com/arduino/docs-content/blob/main/LICENSE.md)).
          Pinout: [UNO A000066](https://docs.arduino.cc/resources/pinouts/A000066-full-pinout.pdf),
          [Mega A000067](https://docs.arduino.cc/resources/pinouts/A000067-full-pinout.pdf).
        - Analog In/Out: [AnalogInOutSerial](https://docs.arduino.cc/built-in-examples/analog/AnalogInOutSerial/).
        - Firmata: [github.com/firmata/arduino](https://github.com/firmata/arduino),
          [API](https://firmata.github.io/arduino/html/index.html) — исходники LGPL-2.1, здесь только ссылки.
        - Фото Mega: [Arduino MEGA2560.png](https://commons.wikimedia.org/wiki/File:Arduino_MEGA2560.png) — Arduino, CC BY-SA 4.0.
        - Фото Uno: [Arduino Uno - R3.jpg](https://commons.wikimedia.org/wiki/File:Arduino_Uno_-_R3.jpg) — SparkFun Electronics, CC BY 2.0.
        - Габаритные SVG Uno/Mega: [Wayne and Layne](https://www.wayneandlayne.com/blog/2010/12/19/nice-drawings-of-the-arduino-uno-and-mega-2560/) — public domain.
        - Полная таблица файлов: `Libraries/Rdk-HardwareLib/Catalog/assets/ATTRIBUTION.md`.

        Arduino — товарный знак Arduino SA; логотип как марка продукта не используется.
        CC BY-SA share-alike относится к vendored-файлам в `assets/` / `_shared/media/`, не ко всему SDK.
        """
    ).replace("__MEDIA__", media_caption("_shared/media/"))
    (out_root / "LAB-Firmata.md").write_text(body, encoding="utf-8")



def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", default="COM3", help="Serial PortName (default: COM3)")
    parser.add_argument(
        "--board-profile",
        type=int,
        default=1,
        choices=(0, 1),
        help="0 = Uno, 1 = Mega 2560 (default: 1)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=OUT,
        help="Output root (default: Bin/Configs/SpikeSamples/Hardware)",
    )
    args = parser.parse_args()
    out_root: Path = args.out
    port: str = args.port
    board_profile: int = args.board_profile
    board = board_id_for_profile(board_profile)
    analog_pin = analog_firmata_pin(board_profile)
    bp_label = f"{board_title_for_profile(board_profile)} ({board_profile})"

    shared = out_root / "_shared"
    shared.mkdir(parents=True, exist_ok=True)

    pot_servo_devices = [
        {"id": "pot1", "module": "potentiometer", "port": "A0", "role": "sensor"},
        {"id": "servo1", "module": "servo", "port": "D9", "role": "actuator"},
    ]
    write_setup_pair(shared, "HardwareSetup", "standard_firmata", ["sensor_shield_v5"], pot_servo_devices)
    (shared / "HardwareSetup.json").write_text(
        setup_json(board, "standard_firmata", ["sensor_shield_v5"], pot_servo_devices),
        encoding="utf-8",
    )

    motor_devices = [
        {"id": "mA", "module": "dc_motor_channel", "channel": "A", "role": "actuator"},
        {"id": "mB", "module": "dc_motor_channel", "channel": "B", "role": "actuator"},
    ]
    write_setup_pair(shared, "MotorShieldR3Setup", "standard_firmata", ["motor_shield_r3"], motor_devices)
    (shared / "MotorShieldR3Setup.json").write_text(
        setup_json(board, "standard_firmata", ["motor_shield_r3"], motor_devices),
        encoding="utf-8",
    )
    write_setup_pair(
        shared,
        "MotorShieldSeeedSetup",
        "standard_firmata",
        ["motor_shield_seeed_v1"],
        motor_devices,
    )
    (shared / "MotorShieldSeeedSetup.json").write_text(
        setup_json(board, "standard_firmata", ["motor_shield_seeed_v1"], motor_devices),
        encoding="utf-8",
    )

    led_devices = [{"id": "led1", "module": "led", "port": "D13", "role": "actuator"}]
    write_setup_pair(shared, "LedSetup", "standard_firmata", [], led_devices)

    pwm_devices = [
        {"id": "pot1", "module": "potentiometer", "port": "A0", "role": "sensor"},
        {"id": "pwmled1", "module": "pwm_led", "port": "D9", "role": "actuator"},
    ]
    write_setup_pair(shared, "PotPwmLedSetup", "standard_firmata", [], pwm_devices)

    setup_rel = f"../_shared/HardwareSetup-{board}.json"
    led_rel = f"../_shared/LedSetup-{board}.json"
    pwm_rel = f"../_shared/PotPwmLedSetup-{board}.json"
    motor_setup_path = f"../_shared/MotorShieldR3Setup-{board}.json"

    kw = dict(port=port, board_profile=board_profile, out_root=out_root)

    board_xml = BOARD_PROPS.format(
        port=port, bundled="sensor_lab_v1", board_profile=board_profile, setup_path=""
    )
    write_project(
        "01-ArduinoBoard",
        "Hardware test: ArduinoBoard",
        "Проверка `ArduinoBoard`: прошивка sensor_lab, upload, heartbeat, подключение.",
        "- `Board` (`ArduinoBoard`) — upload `sensor_lab_v1`, порт, heartbeat.",
        component_block("Board", "ArduinoBoard", "8 4 0", board_xml),
        **kw,
    )

    sketch = board_xml + SKETCH_EXTRA.format(proto=1)
    write_project(
        "02-ArduinoSensorSketch",
        "Hardware test: ArduinoSensorSketch",
        "Проверка `ArduinoSensorSketch`: кастомный протокол sensor_lab, команды, матрица.",
        "- `SensorSketch` (`ArduinoSensorSketch`) — bundled `sensor_lab_v1`, ProtocolVersion 1.",
        component_block("SensorSketch", "ArduinoSensorSketch", "8 8 0", sketch),
        **kw,
    )

    sketch_v2 = board_xml + SKETCH_EXTRA.format(proto=2)
    write_project(
        "06-ArduinoSensorSketch-Proto2",
        "Hardware test: ArduinoSensorSketch PROTO v2",
        "Проверка framed protocol v2: `ProtocolVersion` = 2, команда `PROTO 2` при подключении.",
        "- `SensorSketch` (`ArduinoSensorSketch`) — ProtocolVersion 2.",
        component_block("SensorSketch", "ArduinoSensorSketch", "8 12 0", sketch_v2),
        **kw,
    )

    firmata_board = BOARD_PROPS.format(
        port=port, bundled="standard_firmata", board_profile=board_profile, setup_path=""
    ) + FIRMATA_EXTRA
    write_project(
        "03-ArduinoFirmata",
        "Hardware test: ArduinoFirmata",
        "Пульт пинов StandardFirmata: handshake, D13 с вкладки Pins, Monitor.",
        "- `Firmata` (`ArduinoFirmata`) — bundled `standard_firmata`.",
        component_block("Firmata", "ArduinoFirmata", "16 4 0", firmata_board),
        firmata_lab=True,
        bom="Плата Arduino + USB. Датчики не нужны.",
        wiring=WIRING_LED_D13,
        assembly="Setup JSON не задан. Смотрите вкладки **Pinout** и **Pins**.",
        success="`FirmataReady`; D13 OUTPUT + WriteDigital 1 зажигает встроенный светодиод.",
        **kw,
    )

    adc_body = component_block("Firmata", "ArduinoFirmata", "16 4 0", firmata_board) + component_block(
        "Adc",
        "ArduinoAdc",
        "16 8 0",
        ADC_PROPS.format(analog_pin=analog_pin),
    )
    write_project(
        "04-ArduinoAdc",
        "Hardware test: ArduinoAdc",
        f"Проверка `ArduinoAdc` через связанный `Firmata` (A0 = Firmata pin {analog_pin}).",
        "- `Firmata` + `Adc` (`ArduinoAdc`, `LinkedFirmataName=Firmata`).",
        adc_body,
        **kw,
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
        **kw,
    )

    firmata_link = BOARD_PROPS.format(
        port=port, bundled="standard_firmata", board_profile=board_profile, setup_path=""
    ) + FIRMATA_ANALOG_LINK_EXTRA
    adc_link_body = component_block("Firmata", "ArduinoFirmata", "12 4 0", firmata_link) + component_block(
        "Adc",
        "ArduinoAdc",
        "12 8 0",
        ADC_LINK_PROPS.format(board_profile=board_profile, analog_pin=analog_pin),
    )
    write_project(
        "08-ArduinoFirmata-AnalogLink",
        "Hardware test: Firmata AnalogSamples link",
        "Firmata с `AutoRefreshPins` + `ArduinoAdc.UseLinkedAnalogSamples` (потенциометр A0).",
        f"- `Firmata` + `Adc` (linked samples, A0 = Firmata pin {analog_pin}).",
        adc_link_body,
        firmata_lab=True,
        bom="Плата + USB + потенциометр.",
        wiring=WIRING_POT,
        assembly="Нет HardwareSetup. Результат — `AnalogSamples` / `AdcValue`, не Watch.",
        success="При вращении потенциометра меняются `Adc.AdcValue` и строки `Firmata.AnalogSamples`.",
        **kw,
    )

    write_project(
        "07-ArduinoPropertyEdges",
        "Hardware test: Arduino property edges",
        "Ручная проверка edge-свойств Board: в XML edges = 0; импульс Connect/UploadFirmware из GUI или Property editor.",
        "- `Board` (`ArduinoBoard`) — edges по умолчанию 0; пульсируйте `Connect` / `UploadFirmware` вручную.",
        component_block("Board", "ArduinoBoard", "8 4 0", board_xml),
        **kw,
    )

    firmata_setup = BOARD_PROPS.format(
        port=port,
        bundled="standard_firmata",
        board_profile=board_profile,
        setup_path=setup_rel,
    ) + FIRMATA_EXTRA
    write_project(
        "09-HardwareSetup-SensorShield",
        "Hardware test: Hardware Setup + Assembly",
        "Только Firmata + JSON Sensor Shield (pot A0, servo D9). IO-узлов нет — схема на вкладке Assembly.",
        f"- `Firmata` — `HardwareSetupPath={setup_rel}`, firmware `standard_firmata`.",
        component_block("Firmata", "ArduinoFirmata", "16 4 0", firmata_setup),
        firmata_lab=True,
        bom="Как лабы 10+11: потенциометр и/или серво (для сверки схемы). Запуск без деталей допустим.",
        wiring=f"{WIRING_POT} {WIRING_SERVO}",
        assembly="Вкладка **Assembly**: плата, Sensor Shield, pot A0, servo D9. IO читайте в 10/11.",
        success="Схема отображается; `HardwareSetupValid` = 1.",
        **kw,
    )

    pot_body = component_block("Firmata", "ArduinoFirmata", "12 4 0", firmata_setup) + dio_block(
        "Pot",
        "12 8 0",
        module="potentiometer",
        device_id="pot1",
        port="A0",
        role=0,
        board_profile=board_profile,
        setup_path=setup_rel,
    )
    write_project(
        "10-DeviceIO-Potentiometer",
        "Hardware test: DeviceIO Potentiometer",
        "Firmata + DeviceIO potentiometer A0. Результат — `Pot.Value` в инспекторе.",
        "- `Firmata` + `Pot` (`ArduinoDeviceIO`, ModuleId=potentiometer).",
        pot_body,
        firmata_lab=True,
        bom="Плата + USB + потенциометр.",
        wiring=WIRING_POT,
        assembly="Sensor Shield + potentiometer A0 (и servo D9 в JSON — на схеме есть, узел IO только Pot).",
        success="Continuous: `Pot.Value` в диапазоне 0..1 следует за ручкой.",
        **kw,
    )

    servo_body = component_block("Firmata", "ArduinoFirmata", "12 4 0", firmata_setup) + dio_block(
        "Servo",
        "12 8 0",
        module="servo",
        device_id="servo1",
        port="D9",
        role=1,
        board_profile=board_profile,
        setup_path=setup_rel,
    )
    write_project(
        "11-DeviceIO-Servo",
        "Hardware test: DeviceIO Servo",
        "Firmata + DeviceIO servo D9; `ValueIn` 0..1 → угол ~0..180°.",
        "- `Firmata` + `Servo` (`ArduinoDeviceIO`).",
        servo_body,
        firmata_lab=True,
        bom="Плата + USB + сервопривод (3 провода).",
        wiring=WIRING_SERVO,
        assembly="Sensor Shield + servo D9 на вкладке Assembly.",
        success="`Servo.ValueIn` 0..1 поворачивает вал. ApplyConfig перед записью.",
        **kw,
    )

    motor_firmata = BOARD_PROPS.format(
        port=port,
        bundled="standard_firmata",
        board_profile=board_profile,
        setup_path=motor_setup_path,
    ) + FIRMATA_EXTRA
    motor_body = (
        component_block("Firmata", "ArduinoFirmata", "8 4 0", motor_firmata)
        + dio_block(
            "MotorA",
            "8 8 0",
            module="dc_motor_channel",
            device_id="mA",
            port="",
            channel="A",
            role=1,
            board_profile=board_profile,
            setup_path=motor_setup_path,
        )
        + dio_block(
            "MotorB",
            "8 12 0",
            module="dc_motor_channel",
            device_id="mB",
            port="",
            channel="B",
            role=1,
            board_profile=board_profile,
            setup_path=motor_setup_path,
        )
    )
    write_project(
        "12-MotorShield-R3",
        "Hardware test: Motor Shield R3",
        "Firmata + 2× DeviceIO dc_motor_channel A/B.",
        "- `Firmata` + `MotorA`/`MotorB`.",
        motor_body,
        firmata_lab=True,
        bom="Плата + USB + Arduino Motor Shield R3 + 1–2 DC-мотора + внешнее питание шилда.",
        wiring=WIRING_MOTOR,
        assembly="Шилд R3 на плате, каналы A/B.",
        success="Короткий `MotorA.ValueIn` (например 0.3) крутит канал A. Не оставляйте PWM>0 без мотора.",
        **kw,
    )

    pulse_body = (
        component_block("Firmata", "ArduinoFirmata", "8 4 0", firmata_setup)
        + dio_block(
            "Pot",
            "8 8 0",
            module="potentiometer",
            device_id="pot1",
            port="A0",
            role=0,
            board_profile=board_profile,
            setup_path=setup_rel,
        )
        + dio_block(
            "Btn",
            "8 12 0",
            module="button",
            device_id="btn1",
            port="D2",
            role=0,
            board_profile=board_profile,
            setup_path=setup_rel,
        )
    )
    write_project(
        "13-Sensors-To-Pulse",
        "Hardware test: Sensors to network",
        "DeviceIO потенциометр A0 и кнопка D2. Результат — `Pot.Value` / `Btn.Value` в инспекторе и Monitor.",
        "- `Firmata` + `Pot` + `Btn`.",
        pulse_body,
        firmata_lab=True,
        bom="Плата + USB + потенциометр + тактовая кнопка.",
        wiring=f"{WIRING_POT} {WIRING_BUTTON}",
        assembly="Pot A0 и button D2 на Assembly (JSON 09 также содержит servo — на схеме щита).",
        success="`Pot.Value` меняется при вращении; `Btn.Value` 0/1 при нажатии. Watch не требуется.",
        **kw,
    )

    firmata_led = BOARD_PROPS.format(
        port=port,
        bundled="standard_firmata",
        board_profile=board_profile,
        setup_path=led_rel,
    ) + FIRMATA_EXTRA
    led_body = component_block("Firmata", "ArduinoFirmata", "12 4 0", firmata_led) + dio_block(
        "Led",
        "12 8 0",
        module="led",
        device_id="led1",
        port="D13",
        role=1,
        board_profile=board_profile,
        setup_path=led_rel,
    )
    write_project(
        "17-DeviceIO-LED",
        "Hardware lab: DeviceIO onboard LED",
        "Firmata + DeviceIO `led` на D13. Работает без внешних датчиков (встроенный светодиод Uno/Mega).",
        "- `Firmata` + `Led` (`ArduinoDeviceIO`, ModuleId=led, port=D13, role=actuator).",
        led_body,
        firmata_lab=True,
        bom="Плата + USB. Датчики не нужны.",
        wiring=WIRING_LED_D13,
        assembly="Модуль LED на D13.",
        success="`Led.ValueIn` = 1 зажигает D13; 0 гасит. ApplyConfig перед записью.",
        **kw,
    )

    firmata_pwm = BOARD_PROPS.format(
        port=port,
        bundled="standard_firmata",
        board_profile=board_profile,
        setup_path=pwm_rel,
    ) + FIRMATA_EXTRA
    pwm_body = (
        component_block("Firmata", "ArduinoFirmata", "10 4 0", firmata_pwm)
        + dio_block(
            "Pot",
            "10 8 0",
            module="potentiometer",
            device_id="pot1",
            port="A0",
            role=0,
            board_profile=board_profile,
            setup_path=pwm_rel,
        )
        + dio_block(
            "PwmLed",
            "10 12 0",
            module="pwm_led",
            device_id="pwmled1",
            port="D9",
            role=1,
            board_profile=board_profile,
            setup_path=pwm_rel,
        )
    )
    write_project(
        "18-DeviceIO-PotToPwmLed",
        "Hardware lab: pot A0 → PWM LED D9",
        "Analog In/Out: потенциометр A0 управляет яркостью PWM LED на D9 (модуль `pwm_led`).",
        "- `Firmata` + `Pot` + `PwmLed` (`ArduinoDeviceIO`).",
        pwm_body,
        firmata_lab=True,
        bom="Плата + USB + потенциометр + светодиод + резистор ~220 Ω.",
        wiring=WIRING_PWM_LED,
        assembly="Pot A0 и PWM LED D9.",
        success="Крутите A0 → `Pot.Value` и яркость LED на D9 меняются. Нужны внешние детали.",
        **kw,
    )

    (shared / "SensorHubSetup.json").write_text(
        setup_json(
            board,
            "nmsdk_sensor_hub_v1",
            ["sensor_shield_v5"],
            [
                {"id": "dht", "module": "dht11", "port": "D2", "role": "sensor"},
                {"id": "sonar", "module": "hc_sr04", "port": "D7", "role": "sensor"},
            ],
        ),
        encoding="utf-8",
    )
    (shared / "MotorHubSetup.json").write_text(
        setup_json(
            board,
            "nmsdk_motor_hub_v1",
            ["motor_shield_r3"],
            [{"id": "m1", "module": "dc_motor_channel", "channel": "A", "role": "actuator"}],
        ),
        encoding="utf-8",
    )

    sensor_hub = BOARD_PROPS.format(
        port=port,
        bundled="nmsdk_sensor_hub_v1",
        board_profile=board_profile,
        setup_path="../_shared/SensorHubSetup.json",
    ) + CUSTOM_FW_EXTRA.format(proto=2, plugin="nmsdk_sensor_hub_v1")
    write_project(
        "14-SensorHub",
        "Hardware test: Nmsdk Sensor Hub",
        "CustomFirmware + plugin `nmsdk_sensor_hub_v1`: DHT/HC-SR04 framed hub, Assembly setup.",
        "- `Hub` (`ArduinoCustomFirmware`) — HostPluginId/BundledFirmwareId = nmsdk_sensor_hub_v1.",
        component_block("Hub", "ArduinoCustomFirmware", "8 4 0", sensor_hub),
        **kw,
    )

    motor_hub = BOARD_PROPS.format(
        port=port,
        bundled="nmsdk_motor_hub_v1",
        board_profile=board_profile,
        setup_path="../_shared/MotorHubSetup.json",
    ) + CUSTOM_FW_EXTRA.format(proto=2, plugin="nmsdk_motor_hub_v1")
    write_project(
        "15-MotorHub",
        "Hardware test: Nmsdk Motor Hub",
        "CustomFirmware + plugin `nmsdk_motor_hub_v1`: MOTOR A pwm/dir, framed status 0x20.",
        "- `Hub` (`ArduinoCustomFirmware`) — HostPluginId = nmsdk_motor_hub_v1.",
        component_block("Hub", "ArduinoCustomFirmware", "8 4 0", motor_hub),
        **kw,
    )

    custom_lab = BOARD_PROPS.format(
        port=port,
        bundled="sensor_lab_v1",
        board_profile=board_profile,
        setup_path="",
    ) + CUSTOM_FW_EXTRA.format(proto=2, plugin="sensor_lab_v1")
    write_project(
        "16-CustomFirmware-SensorLab",
        "Hardware test: CustomFirmware + sensor_lab plugin",
        "ArduinoCustomFirmware bound to sensor_lab_v1 plugin (generic custom path).",
        "- `Fw` (`ArduinoCustomFirmware`) — HostPluginId=sensor_lab_v1.",
        component_block("Fw", "ArduinoCustomFirmware", "8 4 0", custom_lab),
        **kw,
    )

    write_lab_firmata_md(port, board_profile, out_root)

    index = out_root / "README.md"
    index.write_text(
        textwrap.dedent(
            f"""\
            # Hardware — тестовые конфигурации Rdk-HardwareLib

            Набор проектов для проверки компонентов Arduino. **Firmata-лабы (схема → сборка → результат):**
            см. [LAB-Firmata.md](LAB-Firmata.md).

            По умолчанию генератор пишет **{bp_label}**, порт `{port}`.
            Перегенерация: `python Scripts/generate_arduino_hardware_configs.py --port {port} --board-profile {board_profile}`

            | Каталог | ClassName | Прошивка | Примечание |
            |---------|-----------|----------|------------|
            | [01-ArduinoBoard](01-ArduinoBoard/) | `ArduinoBoard` | sensor_lab_v1 | |
            | [02-ArduinoSensorSketch](02-ArduinoSensorSketch/) | `ArduinoSensorSketch` | sensor_lab_v1 | |
            | [03-ArduinoFirmata](03-ArduinoFirmata/) | `ArduinoFirmata` | standard_firmata | лаба, без датчиков |
            | [04-ArduinoAdc](04-ArduinoAdc/) | `ArduinoAdc` + `ArduinoFirmata` | standard_firmata | |
            | [05-ArduinoDcDemo](05-ArduinoDcDemo/) | `ArduinoDcDemo` | sensor_lab_v1 | |
            | [06-ArduinoSensorSketch-Proto2](06-ArduinoSensorSketch-Proto2/) | `ArduinoSensorSketch` | sensor_lab_v1 | |
            | [07-ArduinoPropertyEdges](07-ArduinoPropertyEdges/) | `ArduinoBoard` | sensor_lab_v1 | |
            | [08-ArduinoFirmata-AnalogLink](08-ArduinoFirmata-AnalogLink/) | `ArduinoFirmata` + `ArduinoAdc` | standard_firmata | лаба, нужен pot |
            | [09-HardwareSetup-SensorShield](09-HardwareSetup-SensorShield/) | `ArduinoFirmata` + HardwareSetup | standard_firmata | лаба, схема Assembly |
            | [10-DeviceIO-Potentiometer](10-DeviceIO-Potentiometer/) | `ArduinoDeviceIO` | standard_firmata | лаба, pot A0 |
            | [11-DeviceIO-Servo](11-DeviceIO-Servo/) | `ArduinoDeviceIO` | standard_firmata | лаба, servo D9 |
            | [12-MotorShield-R3](12-MotorShield-R3/) | `ArduinoDeviceIO` motor | standard_firmata | лаба, шилд |
            | [13-Sensors-To-Pulse](13-Sensors-To-Pulse/) | DeviceIO sensors | standard_firmata | лаба, pot+кнопка |
            | [14-SensorHub](14-SensorHub/) | `ArduinoCustomFirmware` | nmsdk_sensor_hub_v1 | не Firmata |
            | [15-MotorHub](15-MotorHub/) | `ArduinoCustomFirmware` | nmsdk_motor_hub_v1 | не Firmata |
            | [16-CustomFirmware-SensorLab](16-CustomFirmware-SensorLab/) | `ArduinoCustomFirmware` | sensor_lab_v1 | не Firmata |
            | [17-DeviceIO-LED](17-DeviceIO-LED/) | `ArduinoDeviceIO` led | standard_firmata | лаба, без датчиков |
            | [18-DeviceIO-PotToPwmLed](18-DeviceIO-PotToPwmLed/) | DeviceIO pot+PWM LED | standard_firmata | лаба Analog In/Out |

            **BoardProfile:** 0 = Uno, 1 = Mega 2560. JSON setup: `_shared/HardwareSetup-uno.json` и `HardwareSetup-mega2560.json`.

            Чеклист прошивок: `Libraries/Rdk-HardwareLib/Firmware/README.md`.

            Генерация: `Scripts/generate_arduino_hardware_configs.py`  
            Ассеты: `Scripts/download_hardware_lab_assets.py`  
            Валидация: `Scripts/validate_hardware_spike_configs.py`  
            Миграция legacy DC: `Scripts/migrate_arduino_board_hierarchy.py`
            """
        ),
        encoding="utf-8",
    )
    print(f"Generated configs under {out_root} (port={port}, board={board}, profile={board_profile})")


if __name__ == "__main__":
    main()
