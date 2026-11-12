#!/usr/bin/env python3
"""Apply CamelCase class members and snake_case locals/params in Rdk-HardwareLib sources."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "Libraries/Rdk-HardwareLib"

# Whole-word member renames (order: longer keys first to avoid partial matches)
MEMBER_RENAMES = [
    ("m_showDebugCheck", "ShowDebugCheck"),
    ("m_heartbeatIntervalSpin", "HeartbeatIntervalSpin"),
    ("m_heartbeatTimeoutSpin", "HeartbeatTimeoutSpin"),
    ("m_heartbeatEnabledCheck", "HeartbeatEnabledCheck"),
    ("m_connectOnBuildCheck", "ConnectOnBuildCheck"),
    ("m_boardProfileCombo", "BoardProfileCombo"),
    ("m_bundledFirmwareCombo", "BundledFirmwareCombo"),
    ("m_digitalValueSpin", "DigitalValueSpin"),
    ("m_autoReconnectCheck", "AutoReconnectCheck"),
    ("m_firmwarePathEdit", "FirmwarePathEdit"),
    ("m_svgPlaceholder", "SvgPlaceholder"),
    ("m_uploadProgress", "UploadProgress"),
    ("m_highlightedPins", "HighlightedPins"),
    ("m_connectionState", "ConnectionStateValue"),
    ("m_selectedPinId", "SelectedPinId"),
    ("m_analogChannelByPin", "AnalogChannelByPin"),
    ("m_protocolVersion", "ProtocolVersionValue"),
    ("m_gotAnalogMapping", "GotAnalogMapping"),
    ("m_lastReconnectAttemptMs", "LastReconnectAttemptMs"),
    ("m_boardPanel", "BoardPanel"),
    ("m_commandEdit", "CommandEdit"),
    ("m_presetsList", "PresetsList"),
    ("m_matrixTable", "MatrixTable"),
    ("m_linkedEdit", "LinkedEdit"),
    ("m_speedLabel", "SpeedLabel"),
    ("m_valueLabel", "ValueLabel"),
    ("m_statusLog", "StatusLog"),
    ("m_boardProfile", "BoardProfileValue"),
    ("m_diagramHost", "DiagramHost"),
    ("m_gotCapability", "GotCapability"),
    ("m_gotFirmware", "GotFirmware"),
    ("m_analogValues", "AnalogValues"),
    ("m_sysexBuffer", "SysexBuffer"),
    ("m_highlighted", "HighlightedIds"),
    ("m_selectedId", "SelectedId"),
    ("m_modeCombo", "ModeCombo"),
    ("m_portCombo", "PortCombo"),
    ("m_pinSpin", "PinSpin"),
    ("m_baudSpin", "BaudSpin"),
    ("m_v2Buffer", "V2Buffer"),
    ("m_rxBuffer", "RxBuffer"),
    ("m_lastError", "LastErrorText"),
    ("m_pinRoles", "PinRoles"),
    ("m_interactive", "Interactive"),
    ("m_context", "Context"),
    ("m_diagram", "Diagram"),
    ("m_overlay", "Overlay"),
    ("m_onReady", "OnReadyCallback"),
    ("m_inSysex", "InSysex"),
    ("m_mutex", "RxMutex"),
    ("m_debug", "DebugEnabled"),
    ("m_port", "SerialPort"),
    ("m_pins", "Pins"),
    ("m_roles", "Roles"),
    ("m_tabs", "Tabs"),
    ("m_svg", "SvgWidget"),
    ("firmwareVersion", "FirmwareVersion"),
    ("showDebug", "ShowDebug"),
    ("delegateToLinkedSketch", "DelegateToLinkedSketch"),
    ("resolveHexPath", "ResolveHexPath"),
    ("runPresetCommand", "RunPresetCommand"),
]

# Struct field renames in PinRegion
STRUCT_FIELD_RENAMES = [
    (".id", ".Id"),
    (".label", ".Label"),
    (".role", ".Role"),
    (".normalizedRect", ".NormalizedRect"),
    ("region.id", "region.Id"),
    ("pin.id", "pin.Id"),
]

METHOD_PARAM_MAP = {
    "portName": "port_name",
    "baudRate": "baud_rate",
    "boardProfile": "board_profile",
    "pinId": "pin_id",
    "devicePath": "device_path",
    "port_name": "port_name",
    "baud_rate": "baud_rate",
    "board_profile": "board_profile",
    "pin_id": "pin_id",
    "device_path": "device_path",
    "paramCount": "param_count",
    "errorFlags": "error_flags",
    "pinCount": "pin_count",
    "analogPinCount": "analog_pin_count",
    "dataSize": "data_size",
    "requiredBytes": "required_bytes",
    "frameLen": "frame_len",
    "expectedCrc": "expected_crc",
    "actualCrc": "actual_crc",
    "sendRequested": "send_requested",
    "progressConn": "progress_conn",
    "portPath": "port_path",
    "selectDevicePath": "select_device_path",
    "component_context": "component_context",
    "maxRows": "max_rows",
    "maxCols": "max_cols",
    "propertyName": "property_name",
    "defaultValue": "default_value",
    "edgeName": "edge_name",
    "linkReady": "link_ready",
    "colCount": "col_count",
    "sdkRoot": "sdk_root",
    "testFile": "test_file",
    "rel": "rel_path",
    "candidates": "candidates",
    "candidate": "candidate",
    "preferred": "preferred",
    "normalizedName": "normalized_name",
    "accumulated": "accumulated",
    "best": "best",
}


def apply_member_renames(text: str) -> str:
    for old, new in MEMBER_RENAMES:
        text = re.sub(r"\b" + re.escape(old) + r"\b", new, text)
    return text


def apply_struct_fields(text: str) -> str:
    # PinRegion initializers: id → Id in struct definition only
    text = text.replace("QString id;", "QString Id;")
    text = text.replace("QString label;", "QString Label;")
    text = text.replace("QString role;", "QString Role;")
    text = text.replace("QRectF normalizedRect;", "QRectF NormalizedRect;")
    # JSON keys stay as "id" in pins json - only C++ struct
    text = re.sub(r"\bpin\.id\b", "pin.Id", text)
    text = re.sub(r"\bregion\.id\b", "region.Id", text)
    text = re.sub(r"\.value\(\"id\"\)", ".value(\"id\")", text)  # unchanged
    text = re.sub(r"obj\.value\(QStringLiteral\(\"id\"\)\)", "obj.value(QStringLiteral(\"id\"))", text)
    # setters using .id = in cpp when building PinRegion
    text = re.sub(r"(\w+)\.id\s*=", r"\1.Id =", text)
    text = re.sub(r"(\w+)\.label\s*=", r"\1.Label =", text)
    text = re.sub(r"(\w+)\.role\s*=", r"\1.Role =", text)
    text = re.sub(r"(\w+)\.normalizedRect\s*=", r"\1.NormalizedRect =", text)
    text = re.sub(r"(\w+)\.id\)", r"\1.Id)", text)
    text = re.sub(r"pr\.id", "pr.Id", text)
    text = re.sub(r"p\.id", "p.Id", text)
    return text


def apply_param_renames_in_signatures(text: str) -> str:
    for old, new in METHOD_PARAM_MAP.items():
        if old == new:
            continue
        text = re.sub(
            r"\b(const\s+)?(QString|QByteArray|int|bool|float|double|uint8_t|UComponentGuiContext)(\s*&|\s+\*|\s+)"
            + re.escape(old)
            + r"\b",
            lambda m, o=old, n=new: f"{m.group(1) or ''}{m.group(2)}{m.group(3)}{n}",
            text,
        )
    return text


def process_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    text = original
    text = apply_member_renames(text)
    if "PinOverlay" in path.name or "BoardDiagram" in path.name or "PinRegion" in text:
        text = apply_struct_fields(text)
    if path.suffix in {".h", ".cpp"}:
        text = apply_param_renames_in_signatures(text)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    for path in sorted(ROOT.rglob("*")):
        if path.suffix not in {".h", ".cpp"}:
            continue
        if process_file(path):
            print("updated", path.relative_to(ROOT))
            changed += 1
    print(f"done, {changed} files")


if __name__ == "__main__":
    main()
