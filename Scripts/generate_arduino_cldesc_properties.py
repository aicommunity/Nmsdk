#!/usr/bin/env python3
"""Fill Bin/ClDesc HardwareLibrary Arduino*.xml with property-driven API entries."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLDESC_DIR = ROOT / "Bin/ClDesc/HardwareLibrary/ru-RU"
LEXICON_PATH = ROOT / "Docs/ClDescLexicon.json"

# (name, header_en, desc_ru, type_flags, property_type)
# property_type: 257=param, 258=state, 265=param|input (edge bool)
EDGE = ("| ptPubParameter | | ptInput | ", "265")
PARAM = ("| ptPubParameter | ", "257")
STATE = ("| ptPubState | ", "258")

PROPS: dict[str, list[tuple[str, str, str, tuple[str, str]]]] = {
    "ArduinoBoard": [
        ("Connect", "Connect", "Edge: открыть serial-порт (`EnsureConnected`).", EDGE),
        ("Disconnect", "Disconnect", "Edge: закрыть порт; `PortName` не очищается.", EDGE),
        ("Reconnect", "Reconnect", "Edge: close + open.", EDGE),
        ("UploadFirmware", "Upload firmware", "Edge: прошивка HEX (avrdude).", EDGE),
        ("ClearLastError", "Clear last error", "Edge: очистить `LastError`.", EDGE),
        ("IsConnected", "Is connected", "State: `ConnectionState==Connected`.", STATE),
        ("IsOpening", "Is opening", "State: открытие порта.", STATE),
        ("HasError", "Has error", "State: ошибка подключения/upload.", STATE),
        ("IsDisconnected", "Is disconnected", "State: порт закрыт.", STATE),
        ("IsUploading", "Is uploading", "State: прошивка в процессе.", STATE),
        ("UploadComplete", "Upload complete", "State: `UploadLastResult==ok`.", STATE),
        ("PortName", "Port name", "Путь к serial (`/dev/ttyACM0`, `COM3`).", PARAM),
        ("BundledFirmwareId", "Bundled firmware", "ID из manifest (`sensor_lab_v1`, `standard_firmata`).", PARAM),
    ],
    "ArduinoSensorSketch": [
        ("SendCommand", "Send command", "Edge: отправить `Command` на устройство.", EDGE),
        ("RequestGetStatus", "Request GET STATUS", "Edge: запрос статуса.", EDGE),
        ("RequestProtocolNegotiate", "Negotiate protocol", "Edge: сброс и `PROTO n`.", EDGE),
        ("StartReading", "Start reading", "Edge: команда `START READING`.", EDGE),
        ("StopReading", "Stop reading", "Edge: команда `STOP READING`.", EDGE),
        ("Rotate", "Rotate", "Edge: команда `ROTATE`.", EDGE),
        ("StopRotate", "Stop rotate", "Edge: команда `STOP ROTATE`.", EDGE),
        ("GetDataFromBuffers", "Get data from buffers", "Edge: записать RX в `DoubleMatrixReadings`.", EDGE),
        ("GetPinsInfo", "Get pins info", "Edge: `GET STATUS` → `PinStatusJson`.", EDGE),
        ("IsProtocolReady", "Protocol ready", "State: протокол согласован.", STATE),
        ("HasPendingCommands", "Pending commands", "State: очередь/TX не пусты.", STATE),
        ("LastSentCommand", "Last sent command", "State: последняя отправленная строка.", STATE),
        ("Command", "Command", "Текстовая команда для прошивки.", PARAM),
        ("ProtocolVersion", "Protocol version", "1=legacy, 2=framed CRC.", PARAM),
    ],
    "ArduinoFirmata": [
        ("RestartFirmata", "Restart Firmata", "Edge: сброс handshake.", EDGE),
        ("ApplyPinConfig", "Apply pin config", "Edge: применить pin mode / IO.", EDGE),
        ("IsFirmataReady", "Firmata ready", "State: handshake завершён.", STATE),
        ("IsLinkReady", "Link ready", "State: connected ∧ Firmata ready.", STATE),
        ("ReportAnalogEnable", "Report analog", "Включить analog report для `SelectedPin`.", PARAM),
        ("SelectedPin", "Selected pin", "Номер пина Firmata.", PARAM),
    ],
    "ArduinoDcDemo": [
        ("SendCommand", "Send command", "Edge: DC-команда (`SET SPEED …`).", EDGE),
        ("GetSpeed", "Get speed", "Edge: обновить `Speed`/`Acceleration` из RX.", EDGE),
        ("Speed", "Speed", "State: скорость DC.", STATE),
        ("Acceleration", "Acceleration", "State: ускорение (если есть в кадре).", STATE),
        (
            "LinkedSketchName",
            "Linked sketch (deprecated)",
            "**Устарело.** Используйте один узел `ArduinoDcDemo` с `PortName`.",
            PARAM,
        ),
        ("PortName", "Port name", "Serial-порт (наследуется от Board).", PARAM),
        ("BundledFirmwareId", "Bundled firmware", "По умолчанию `sensor_lab_v1`.", PARAM),
    ],
    "ArduinoAdc": [
        ("ReadAdcFlag", "Read ADC", "Edge: чтение через связанный Firmata.", EDGE),
        ("AdcReadOk", "ADC read OK", "State: Firmata готов и значение прочитано.", STATE),
        ("LinkedFirmataName", "Linked Firmata", "Имя узла `ArduinoFirmata` на canvas.", PARAM),
        ("AnalogPin", "Analog pin", "Номер аналогового пина Firmata.", PARAM),
        ("AdcValue", "ADC value", "State: 0–1023.", STATE),
    ],
}


def prop_xml(name: str, header: str, desc: str, type_flags: str, ptype: str) -> str:
    return f"""\t\t<{name}>
\t\t\t<Header>{header}</Header>
\t\t\t<Description>{desc}</Description>
\t\t\t<Type>{type_flags}</Type>
\t\t\t<DataSelectionType>0</DataSelectionType>
\t\t\t<ValueList Type="std::vector" Size="2" elemType="std::string">
\t\t\t\t<elem Type="std::string"></elem>
\t\t\t\t<elem Type="std::string"></elem>
\t\t\t</ValueList>
\t\t\t<PropertyType>{ptype}</PropertyType>
\t\t</{name}>
"""


def update_class_xml(class_name: str, props: list) -> None:
    path = CLDESC_DIR / f"{class_name}.xml"
    text = path.read_text(encoding="utf-8")
    block = "\n".join(prop_xml(n, h, d, tf, pt) for n, h, d, (tf, pt) in props)
    if "<Properties/>" in text:
        text = text.replace("<Properties/>", f"<Properties>\n{block}\t</Properties>")
    else:
        text = re.sub(
            r"<Properties>.*?</Properties>",
            f"<Properties>\n{block}\t</Properties>",
            text,
            count=1,
            flags=re.DOTALL,
        )
    path.write_text(text, encoding="utf-8")
    print(f"updated {path}")


def update_lexicon() -> None:
    data = json.loads(LEXICON_PATH.read_text(encoding="utf-8"))
    overrides: dict[str, dict[str, dict[str, str]]] = data.setdefault("propertyOverrides", {})
    for class_name, props in PROPS.items():
        cls = overrides.setdefault(class_name, {})
        for name, header, desc, _ in props:
            cls[name] = {"header": header, "description": desc}
    LEXICON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"updated {LEXICON_PATH}")


def main() -> None:
    for class_name, props in PROPS.items():
        update_class_xml(class_name, props)
    update_lexicon()


if __name__ == "__main__":
    main()
