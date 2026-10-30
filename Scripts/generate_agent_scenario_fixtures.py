#!/usr/bin/env python3
"""Regenerate Rdk/Tests/Fixtures/LLM/agent-scenarios from the v1 matrix."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "Rdk/Tests/Fixtures/LLM/agent-scenarios"
CONNECT = {
    "from_long_name": "Model.Source1",
    "from_property": "Output",
    "to_long_name": "Model.Net1",
    "to_property": "Input",
    "channel_index": 0,
}

mock_empty = {"tool_calls": []}
mock_snapshot = {
    "tool_calls": [
        {
            "id": "c1",
            "name": "get_net_snapshot",
            "arguments": {"channel_index": 0, "max_components": 200},
        }
    ]
}
mock_snapshot_extra = {
    "tool_calls": [
        {
            "id": "c1",
            "name": "get_net_snapshot",
            "arguments": {
                "channel_index": 0,
                "max_components": 200,
                "reason": "inspect",
            },
        }
    ]
}
mock_text = {"text": "Краткий ответ по результатам tool."}

fixtures: list[dict] = []


def w(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def det(
    suite: str,
    id_: str,
    text: str,
    script: list,
    expect: dict,
    session=None,
    tags=None,
    variants=None,
    profile="core",
    confirm_pending=False,
    env=None,
    auto_apply_writes=None,
):
    default_session = {"project_loaded": True, "llm_write_enabled": True}
    if auto_apply_writes is not None:
        default_session["auto_apply_writes"] = auto_apply_writes
    o = {
        "schema_version": 1,
        "id": id_,
        "tier": "deterministic",
        "suite": suite,
        "registry_profile": profile,
        "user_text": text,
        "session": session or default_session,
        "env": env or {"NMSDK_LLM_INTENT_LLM": ""},
        "mock_script": script,
        "expect": expect,
    }
    if tags:
        o["tags"] = tags
    if variants:
        o["variants"] = variants
    if confirm_pending:
        o["confirm_pending"] = True
    return o


# --- Graph ---
fixtures.append(
    det(
        "graph",
        "graph_snapshot",
        "какие компоненты на схеме",
        [mock_snapshot],
        {
            "orchestrator_ok": True,
            "tools_invoked_any": ["get_net_snapshot"],
            "final_text_not_contains": ["Done.", "need additional information"],
            "needs_argument_clarification": False,
        },
        variants=[
            {"id_suffix": "ru_modules", "user_text": "какие модули есть в проекте"},
            {"id_suffix": "en", "user_text": "what components are on the diagram"},
        ],
    )
)
fixtures.append(
    det(
        "graph",
        "graph_snapshot_normalize",
        "покажи схему",
        [mock_snapshot_extra],
        {
            "orchestrator_ok": True,
            "tools_invoked_any": ["get_net_snapshot"],
            "final_text_not_contains": ["Done."],
        },
    )
)
fixtures.append(
    det(
        "graph",
        "graph_snapshot_subtree",
        "что внутри Net1",
        [
            {
                "tool_calls": [
                    {
                        "name": "get_net_snapshot",
                        "arguments": {
                            "channel_index": 0,
                            "root_long_name": "Model.Net1",
                        },
                    }
                ]
            },
            mock_text,
        ],
        {"tools_invoked_any": ["get_net_snapshot"]},
    )
)
fixtures.append(
    det(
        "graph",
        "graph_snapshot_max_components",
        "покажи схему, не больше 50 узлов",
        [
            {
                "tool_calls": [
                    {
                        "name": "get_net_snapshot",
                        "arguments": {"channel_index": 0, "max_components": 50},
                    }
                ]
            },
            mock_text,
        ],
        {"tools_invoked_any": ["get_net_snapshot"]},
    )
)
fixtures.append(
    det(
        "graph",
        "graph_find_component",
        "найди компонент Source1",
        [
            {
                "tool_calls": [
                    {
                        "name": "find_component",
                        "arguments": {"query": "Source1", "channel_index": 0},
                    }
                ]
            },
            mock_text,
        ],
        {"tools_invoked_any": ["find_component"]},
    )
)
fixtures.append(
    det(
        "graph",
        "graph_properties",
        "свойства Source1",
        [
            {
                "tool_calls": [
                    {
                        "name": "get_component_properties",
                        "arguments": {
                            "long_name": "Model.Source1",
                            "channel_index": 0,
                        },
                    }
                ]
            },
            mock_text,
        ],
        {"tools_invoked_any": ["get_component_properties"]},
    )
)
fixtures.append(
    det(
        "graph",
        "graph_list_classes",
        "какие классы зарегистрированы",
        [{"tool_calls": [{"name": "list_registered_classes", "arguments": {}}]}],
        {
            "tools_invoked_any": ["list_registered_classes"],
            "tools_forbidden": ["add_component"],
        },
        session={"project_loaded": False, "llm_write_enabled": True},
    )
)
fixtures.append(
    det(
        "graph",
        "graph_list_classes_filter",
        "классы из PulseLib",
        [
            {
                "tool_calls": [
                    {
                        "name": "list_registered_classes",
                        "arguments": {"library_filter": "PulseLib"},
                    }
                ]
            },
            mock_text,
        ],
        {"tools_invoked_any": ["list_registered_classes"]},
        session={"project_loaded": False, "llm_write_enabled": True},
        profile="full",
    )
)
fixtures.append(
    det(
        "graph",
        "graph_describe_class",
        "что такое UNet",
        [{"tool_calls": [{"name": "describe_class", "arguments": {"class_name": "UNet"}}]}],
        {"tools_invoked_any": ["describe_class"]},
        session={"project_loaded": False, "llm_write_enabled": True},
    )
)
fixtures.append(
    det(
        "graph",
        "graph_search_docs",
        "как устроен orchestrator",
        [
            {
                "tool_calls": [
                    {
                        "name": "search_project_docs",
                        "arguments": {"query": "orchestrator", "scope": "docs"},
                    }
                ]
            },
            mock_text,
        ],
        {"tools_invoked_any": ["search_project_docs"]},
        session={"project_loaded": False, "llm_write_enabled": True},
    )
)
fixtures.append(
    det(
        "graph",
        "graph_validate_project",
        "проверь текущий проект",
        [{"tool_calls": [{"name": "validate_project", "arguments": {}}]}],
        {"tools_invoked_any": ["validate_project"]},
    )
)

# --- Links ---
fixtures.append(
    det(
        "links",
        "link_connect",
        "соедини Source1.Output с Net1.Input",
        [{"tool_calls": [{"name": "connect_components", "arguments": CONNECT}]}],
        {
            "tools_invoked_any": ["connect_components"],
            "tools_forbidden": ["add_component"],
        },
    )
)
fixtures.append(
    det(
        "links",
        "link_connect_en",
        "connect Source1 output to Net1 input",
        [{"tool_calls": [{"name": "connect_components", "arguments": CONNECT}]}],
        {"tools_invoked_any": ["connect_components"]},
        variants=[{"id_suffix": "ru", "user_text": "соедини выход Source1 со входом Net1"}],
    )
)
fixtures.append(
    det(
        "links",
        "link_disconnect",
        "разорви связь Source1 и Net1",
        [{"tool_calls": [{"name": "disconnect_components", "arguments": CONNECT}]}],
        {"tools_invoked_any": ["disconnect_components"]},
    )
)
fixtures.append(
    det(
        "links",
        "link_connect_then_disconnect",
        "соедини и разорви Source1 и Net1",
        [
            {"tool_calls": [{"name": "connect_components", "arguments": CONNECT}]},
            {"tool_calls": [{"name": "disconnect_components", "arguments": CONNECT}]},
            mock_text,
        ],
        {
            "tools_invoked_all": ["connect_components", "disconnect_components"],
            "tools_invoked_count_min": 2,
        },
    )
)

# --- Write ---
fixtures.append(
    det(
        "write",
        "write_add_root",
        "добавь NPulseNeuron в корень",
        [
            {
                "tool_calls": [
                    {
                        "name": "add_component",
                        "arguments": {
                            "class_name": "NPulseNeuron",
                            "parent_long_name": "",
                            "short_name": "Neuron1",
                        },
                    }
                ]
            },
            mock_text,
        ],
        {"tools_invoked_any": ["add_component"]},
    )
)
fixtures.append(
    det(
        "write",
        "write_add_nested",
        "добавь Neuron внутрь Net1",
        [
            {
                "tool_calls": [
                    {
                        "name": "add_component",
                        "arguments": {
                            "class_name": "NPulseNeuron",
                            "parent_long_name": "Model.Net1",
                            "short_name": "Neuron1",
                        },
                    }
                ]
            },
            mock_text,
        ],
        {"tools_invoked_any": ["add_component"]},
    )
)
fixtures.append(
    det(
        "write",
        "write_set_property",
        "установи Comment=hello для Source1",
        [
            {
                "tool_calls": [
                    {
                        "name": "set_property",
                        "arguments": {
                            "long_name": "Model.Source1",
                            "property_name": "Comment",
                            "value": "hello",
                        },
                    }
                ]
            },
            mock_text,
        ],
        {"tools_invoked_any": ["set_property"]},
    )
)
fixtures.append(
    det(
        "write",
        "write_remove",
        "удали Source1",
        [
            {
                "tool_calls": [
                    {"name": "remove_component", "arguments": {"long_name": "Model.Source1"}}
                ]
            },
            mock_text,
        ],
        {"tools_invoked_any": ["remove_component"]},
    )
)
# --- Lifecycle ---
fixtures.append(
    det(
        "lifecycle",
        "life_create",
        "создай новый проект",
        [
            {
                "tool_calls": [
                    {
                        "name": "create_configuration",
                        "arguments": {"autocreate_subdirectory": True},
                    }
                ]
            },
            mock_text,
        ],
        {
            "tools_invoked_any": ["create_configuration"],
            "tools_forbidden": ["add_component"],
        },
        session={"project_loaded": False, "llm_write_enabled": True},
    )
)
fixtures.append(
    det(
        "lifecycle",
        "life_create_path",
        "create config in /tmp/nmsdk_agent_test",
        [
            {
                "tool_calls": [
                    {
                        "name": "create_configuration",
                        "arguments": {
                            "parent_directory": "/tmp/nmsdk_agent_test",
                            "project_ini_path": "/tmp/nmsdk_agent_test/project.ini",
                        },
                    }
                ]
            },
            mock_text,
        ],
        {"tools_invoked_any": ["create_configuration"]},
        session={"project_loaded": False, "llm_write_enabled": True},
    )
)
fixtures.append(
    det(
        "lifecycle",
        "life_load_missing",
        "load config",
        [mock_empty, mock_empty],
        {
            "orchestrator_ok": True,
            "provider_rounds_max": 2,
            "tools_invoked_count_max": 0,
        },
        session={"project_loaded": False, "llm_write_enabled": True},
    )
)
fixtures.append(
    det(
        "lifecycle",
        "life_load_recent",
        "открой последний конфиг",
        [
            {
                "tool_calls": [
                    {
                        "name": "open_recent_configuration",
                        "arguments": {"index": 1},
                    }
                ]
            },
            mock_text,
        ],
        {
            "orchestrator_ok": True,
            "tools_invoked_any": ["open_recent_configuration", "load_configuration"],
            "final_text_not_contains": ["Done."],
            "provider_rounds_max": 2,
        },
        session={"project_loaded": False, "llm_write_enabled": True},
    )
)
fixtures.append(
    det(
        "lifecycle",
        "life_load_path",
        "открой /tmp/nmsdk_sample/project.ini",
        [
            {
                "tool_calls": [
                    {
                        "name": "load_configuration",
                        "arguments": {
                            "configuration_path": "/tmp/nmsdk_sample/project.ini"
                        },
                    }
                ]
            },
            mock_text,
        ],
        {"tools_invoked_any": ["load_configuration", "load_project"]},
        session={"project_loaded": False, "llm_write_enabled": True},
    )
)
fixtures.append(
    det(
        "lifecycle",
        "life_list_recent",
        "покажи недавние конфигурации",
        [{"tool_calls": [{"name": "list_recent_configurations", "arguments": {}}]}],
        {"tools_invoked_any": ["list_recent_configurations"]},
        session={"project_loaded": False, "llm_write_enabled": True},
    )
)
fixtures.append(
    det(
        "lifecycle",
        "life_validate_disk",
        "проверь конфиг на диске /tmp/x/project.ini",
        [
            {
                "tool_calls": [
                    {
                        "name": "validate_configuration",
                        "arguments": {"configuration_path": "/tmp/x/project.ini"},
                    }
                ]
            },
            mock_text,
        ],
        {"tools_invoked_any": ["validate_configuration"]},
        session={"project_loaded": False, "llm_write_enabled": True},
    )
)
fixtures.append(
    det(
        "lifecycle",
        "life_save",
        "сохрани конфигурацию",
        [{"tool_calls": [{"name": "save_configuration", "arguments": {}}]}],
        {"tools_invoked_any": ["save_configuration", "save_project"]},
    )
)
fixtures.append(
    det(
        "lifecycle",
        "life_close",
        "закрой проект",
        [{"tool_calls": [{"name": "close_configuration", "arguments": {}}]}],
        {"tools_invoked_any": ["close_configuration"]},
    )
)
fixtures.append(
    det(
        "lifecycle",
        "life_update",
        "обнови конфигурацию",
        [{"tool_calls": [{"name": "update_configuration", "arguments": {}}]}],
        {"tools_invoked_any": ["update_configuration"]},
    )
)
fixtures.append(
    det(
        "lifecycle",
        "life_copy",
        "скопируй проект в /tmp/copy",
        [
            {
                "tool_calls": [
                    {
                        "name": "copy_configuration",
                        "arguments": {"destination_directory": "/tmp/copy"},
                    }
                ]
            },
            mock_text,
        ],
        {"tools_invoked_any": ["copy_configuration"]},
        session={"project_loaded": False, "llm_write_enabled": True},
    )
)
fixtures.append(
    det(
        "lifecycle",
        "life_rename",
        "переименуй проект в Demo2",
        [
            {
                "tool_calls": [
                    {"name": "rename_configuration", "arguments": {"new_name": "Demo2"}}
                ]
            },
            mock_text,
        ],
        {"tools_invoked_any": ["rename_configuration"]},
        session={"project_loaded": False, "llm_write_enabled": True},
    )
)

# --- Channels / UI / meta ---
for cid, text, tool, args in [
    ("chan_list", "какие каналы расчёта", "list_channels", {}),
    ("chan_set", "переключись на канал 1", "set_active_channel", {"channel_index": 1}),
    ("calc_start", "запусти расчёт", "start_channel_calculation", {"channel_index": 0}),
    ("calc_pause", "останови расчёт", "pause_channel_calculation", {"channel_index": 0}),
    ("calc_reset", "сбрось расчёт", "reset_channel_calculation", {"channel_index": 0}),
    ("calc_step", "один шаг расчёта", "step_channel_calculation", {"channel_index": 0}),
    ("ui_list", "какие панели доступны", "list_ui_panels", {}),
    ("ui_logger", "покажи окно лога", "show_ui_panel", {"panel": "logger"}),
    ("meta_reload", "перечитай parameters.xml", "reload_configuration_parameters", {}),
    ("meta_save_metadata", "сохрани метаданные проекта", "save_project_metadata", {}),
]:
    fixtures.append(
        det(
            "channels",
            cid,
            text,
            [{"tool_calls": [{"name": tool, "arguments": args}]}],
            {"tools_invoked_any": [tool]},
        )
    )

fixtures.append(
    det(
        "channels",
        "ui_open_tab",
        "открой вкладку Source1",
        [
            {
                "tool_calls": [
                    {
                        "name": "open_component_gui_tab",
                        "arguments": {"long_name": "Model.Source1"},
                    }
                ]
            },
            mock_text,
        ],
        {"tools_invoked_any": ["open_component_gui_tab"]},
    )
)

# --- Observability ---
fixtures.append(
    det(
        "observability",
        "obs_policy",
        "какой уровень логов в проекте",
        [{"tool_calls": [{"name": "get_system_log_policy", "arguments": {}}]}],
        {"tools_invoked_any": ["get_system_log_policy"]},
    )
)
fixtures.append(
    det(
        "observability",
        "obs_read_tail",
        "покажи последние строки лога",
        [
            {
                "tool_calls": [
                    {
                        "name": "read_system_log",
                        "arguments": {"mode": "tail", "max_lines": 80},
                    }
                ]
            },
            mock_text,
        ],
        {"tools_invoked_any": ["read_system_log"]},
    )
)
fixtures.append(
    det(
        "observability",
        "obs_read_debug_reminder",
        "покажи DEBUG лог",
        [
            {
                "tool_calls": [
                    {
                        "name": "read_system_log",
                        "arguments": {"mode": "tail", "severity": "debug"},
                    }
                ]
            },
            mock_text,
        ],
        {"tools_invoked_any": ["read_system_log"]},
    )
)
fixtures.append(
    det(
        "observability",
        "obs_disabled",
        "привет",
        [mock_empty],
        {
            "tools_forbidden": ["read_system_log", "get_system_log_policy"],
            "provider_rounds_max": 2,
        },
        env={"NMSDK_LLM_INTENT_LLM": "", "NMSDK_LLM_DISABLE_SYSTEM_LOG": "1"},
    )
)

# --- No suitable tool ---
for nid, text in [
    ("no_tool_email_ru", "добавь отправку отчёта на email boss@corp.ru"),
    ("no_tool_compile_en", "compile this project to .exe"),
]:
    fixtures.append(
        det(
            "no-suitable-tool",
            nid,
            text,
            [mock_empty, mock_empty],
            {
                "no_suitable_tool": True,
                "orchestrator_ok": True,
                "provider_rounds_max": 2,
                "tools_invoked_count_max": 0,
                "final_text_contains_any": ["Не найдено", "Cannot find", "подходящ"],
                "final_text_not_contains": ["Done.", "too many steps", "maximum tool"],
            },
            tags=["no_tool"],
        )
    )

fixtures.append(
    det(
        "no-suitable-tool",
        "no_tool_explicit",
        "удали все файлы с диска C:",
        [mock_empty, {"text": "NO_SUITABLE_TOOL", "tool_calls": []}],
        {
            "no_suitable_tool": True,
            "provider_rounds_max": 2,
            "tools_invoked_count_max": 0,
        },
        tags=["no_tool"],
    )
)

fixtures.append(
    det(
        "no-suitable-tool",
        "no_tool_query_weather",
        "покажи погоду в Москве",
        [{"text": "В NeuroModeler нет инструмента для погоды."}],
        {
            "orchestrator_ok": True,
            "provider_rounds_max": 1,
            "tools_invoked_count_max": 0,
            "expect_intent": "query",
        },
        tags=["no_tool"],
    )
)

# --- Negative ---
fixtures.append(
    det(
        "negative",
        "neg_empty_done",
        "привет",
        [mock_empty],
        {"orchestrator_ok": True, "final_text_not_contains": ["Done."]},
    )
)
fixtures.append(
    det(
        "negative",
        "neg_write_disabled",
        "добавь нейрон в корень",
        [
            {
                "tool_calls": [
                    {
                        "name": "add_component",
                        "arguments": {
                            "class_name": "NPulseNeuron",
                            "parent_long_name": "",
                            "short_name": "N1",
                        },
                    }
                ]
            },
            mock_text,
        ],
        {"tools_forbidden": ["add_component", "set_property"]},
        session={"project_loaded": True, "llm_write_enabled": False},
    )
)

# --- Library full ---
for lid, text, tool in [
    ("lib_pulse_search", "документация PulseLib neuron", "search_pulse_docs"),
    ("lib_pulse_classes", "классы PulseLib", "list_pulse_component_classes"),
    ("lib_hw_search", "документация HardwareLib", "search_hardware_docs"),
    ("lib_hw_classes", "классы HardwareLib", "list_hardware_component_classes"),
    ("lib_mc_search", "документация MotionControl", "search_motion_control_docs"),
    (
        "lib_mc_classes",
        "классы MotionControlLib",
        "list_motion_control_component_classes",
    ),
]:
    args = {"query": "overview"} if "search" in tool else {}
    fixtures.append(
        det(
            "library",
            lid,
            text,
            [{"tool_calls": [{"name": tool, "arguments": args}]}],
            {"tools_invoked_any": [tool]},
            session={"project_loaded": False, "llm_write_enabled": True},
            profile="full",
        )
    )

# Write deterministic files
for sub in (
    "graph",
    "lifecycle",
    "links",
    "write",
    "channels",
    "observability",
    "no-suitable-tool",
    "negative",
    "library",
):
    d = ROOT / "deterministic" / sub
    if d.exists():
        for p in d.glob("*.json"):
            p.unlink()

det_count = 0
for fx in fixtures:
    path = ROOT / "deterministic" / fx["suite"] / f"{fx['id']}.json"
    w(path, fx)
    det_count += 1
    det_count += len(fx.get("variants", []))

# mock-patterns
patterns = {
    "tool_call_get_net_snapshot_extra_field.json": mock_snapshot_extra,
    "tool_call_connect_minimal.json": {
        "tool_calls": [{"name": "connect_components", "arguments": CONNECT}]
    },
    "provider_empty.json": mock_empty,
    "provider_no_suitable_tool_text.json": {
        "text": "NO_SUITABLE_TOOL",
        "tool_calls": [],
    },
}
for name, body in patterns.items():
    w(ROOT / "mock-patterns" / name, body)

# E2E
e2e_dir = ROOT / "e2e"
if e2e_dir.exists():
    for p in e2e_dir.glob("*.json"):
        p.unlink()

e2e_cases = [
    (
        "e2e_graph_snapshot",
        "list components on channel 0",
        "ToolInvoked",
        ["get_net_snapshot"],
        ["add_component"],
    ),
    (
        "e2e_list_classes_ru",
        "какие классы компонентов зарегистрированы",
        "ClassesListed",
        ["list_registered_classes"],
        ["add_component"],
    ),
    (
        "e2e_list_classes_en",
        "What component classes are registered in RDK?",
        "ClassesListed",
        ["list_registered_classes"],
        ["add_component"],
    ),
    (
        "e2e_no_tool_email",
        "Send this diagram by email to the team",
        "NoSuitableToolOrRefusal",
        [],
        [],
    ),
    (
        "e2e_link_connect",
        "connect the signal source to the network input",
        "ToolInvoked",
        ["connect_components"],
        ["add_component"],
    ),
    (
        "e2e_write_add",
        "add a neuron to the root net",
        "ToolInvoked",
        ["add_component"],
        [],
    ),
    (
        "e2e_validate_fuzzy",
        "Could you check whether the configuration at /tmp/nmsdk_sample/project.ini is valid?",
        "ValidateRan",
        ["validate_configuration"],
        ["add_component"],
    ),
    (
        "e2e_load_fuzzy",
        "Open the existing sample configuration located at /tmp/nmsdk_sample",
        "LoadRequested",
        ["load_configuration", "load_project"],
        ["add_component"],
    ),
    (
        "e2e_create_fuzzy",
        "I want a brand new configuration under /tmp/nmsdk_e2e_agent",
        "CreateRequested",
        ["create_configuration"],
        ["add_component"],
    ),
    (
        "e2e_save_howto",
        "How do I save my open NeuroModeler configuration to disk?",
        "InformativeAnswer",
        ["save_configuration", "save_project"],
        ["create_configuration"],
    ),
    (
        "e2e_describe_class",
        "Tell me about the Model component class using describe_class",
        "ToolInvoked",
        ["describe_class", "list_registered_classes"],
        ["add_component"],
    ),
    (
        "e2e_lifecycle_close",
        "close the open project configuration",
        "LifecycleToolUsed",
        ["close_configuration"],
        [],
    ),
    (
        "e2e_obs_policy",
        "what log level is configured for this project",
        "ToolInvoked",
        ["get_system_log_policy"],
        [],
    ),
    (
        "e2e_channels_list",
        "which calculation channels exist",
        "ToolInvoked",
        ["list_channels"],
        [],
    ),
    (
        "e2e_orchestrator_ok_smoke",
        "hello assistant",
        "OrchestratorOk",
        [],
        [],
    ),
]

for eid, text, goal, tools_any, forbidden in e2e_cases:
    w(
        e2e_dir / f"{eid}.json",
        {
            "schema_version": 1,
            "id": eid,
            "tier": "e2e",
            "suite": "e2e",
            "user_text": text,
            "session": {"project_loaded": False, "llm_write_enabled": True},
            "e2e": {
                "goal": goal,
                "expected_tools_any": tools_any,
                "forbidden_tools": forbidden,
                "require_orchestrator_ok": True,
                "allow_app_unavailable_result": True,
            },
            "expect": {
                "provider_rounds_max": 4,
                "final_text_not_contains": ["too many steps", "maximum tool"],
            },
        },
    )

w(
    ROOT / "manifest.json",
    {
        "version": 1,
        "suites": [
            {
                "id": "deterministic-all",
                "tier": "deterministic",
                "gtest": "Test_LLM_AgentScenarios",
                "filter": "AgentDeterministic",
            },
            {
                "id": "e2e-nl",
                "tier": "e2e",
                "gtest": "Test_LLM_AgentScenarios",
                "filter": "AgentE2e",
            },
        ],
    },
)

print(f"deterministic files: {det_count} expanded cases target")
print(f"e2e files: {len(e2e_cases)}")
