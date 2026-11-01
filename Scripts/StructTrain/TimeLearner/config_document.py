"""Lossless, fail-closed editing of existing text leaves in Rdk XML-like files.

Rdk accepts numeric element names such as <00>. No standard XML serializer is
used. This adapter preserves all bytes outside explicitly selected leaf content;
it does not validate component capabilities or effective numerical parameters.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import re


class ConfigDocumentError(ValueError):
    pass


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ConfigDocumentError(reason)


def xml_char(code: int) -> bool:
    return code in (9, 10, 13) or 32 <= code <= 0xD7FF or 0xE000 <= code <= 0xFFFD or 0x10000 <= code <= 0x10FFFF


def decode_text(raw: bytes) -> str:
    try:
        text = raw.decode("utf-8")
    except UnicodeError as error:
        raise ConfigDocumentError("config_requires_utf8") from error
    require(all(xml_char(ord(c)) for c in text), "invalid_config_character")
    require("<" not in text and "]]>" not in text, "unsupported_mixed_leaf_content")
    named = {"amp": "&", "lt": "<", "gt": ">", "quot": '"', "apos": "'"}
    def entity(match: re.Match) -> str:
        name = match.group(1)
        if name in named:
            return named[name]
        try:
            require(name.startswith("#"), "unknown_config_entity")
            require(re.fullmatch(r"#(?:[0-9]+|x[0-9a-fA-F]+)", name) is not None, "invalid_config_entity")
            code = int(name[2:], 16) if name.startswith("#x") else int(name[1:], 10)
            require(xml_char(code), "invalid_config_character_reference")
            return chr(code)
        except ValueError as error:
            raise ConfigDocumentError("invalid_config_entity") from error
    require(re.fullmatch(r"(?:[^&]|&[^&;]+;)*", text) is not None, "unterminated_config_entity")
    return re.sub(r"&([^&;]+);", entity, text)


def valid_name(name: str) -> bool:
    return bool(name) and all(c.isalnum() or c in "_:-." for c in name) and name[0] not in "-."


@dataclass
class Node:
    name: str
    content_start: int
    content_end: int = -1
    children: list[Node] = field(default_factory=list)
    self_closing: bool = False


@dataclass(frozen=True)
class TextEdit:
    path: tuple[str, ...]
    expected_old: str
    value: str


class ConfigDocument:
    def __init__(self, raw: bytes):
        require(type(raw) is bytes and len(raw) <= 64 * 1024 * 1024, "invalid_config_document_size_or_type")
        try:
            decoded = raw.decode("utf-8")
        except UnicodeError as error:
            raise ConfigDocumentError("config_requires_utf8") from error
        self.raw = raw
        require(all(xml_char(ord(c)) for c in decoded), "invalid_config_character")
        roots: list[Node] = []
        stack: list[Node] = []
        cursor, nodes = (3 if raw.startswith(b"\xef\xbb\xbf") else 0), 0
        declaration_seen = False
        while cursor < len(raw):
            if raw[cursor] != 60:
                end = raw.find(b"<", cursor)
                if end < 0:
                    end = len(raw)
                if stack:
                    decode_text(raw[cursor:end])
                else:
                    require(not raw[cursor:end].strip(), "config_text_outside_root")
                cursor = end
                continue
            if raw.startswith(b"<!--", cursor):
                end = raw.find(b"-->", cursor + 4)
                require(end >= 0 and b"--" not in raw[cursor + 4:end], "invalid_config_comment")
                cursor = end + 3
                continue
            if raw.startswith(b"<![CDATA[", cursor):
                end = raw.find(b"]]>", cursor + 9)
                require(bool(stack) and end >= 0, "invalid_config_cdata")
                require(all(xml_char(ord(c)) for c in raw[cursor + 9:end].decode("utf-8")), "invalid_config_character")
                cursor = end + 3
                continue
            if raw.startswith(b"<?xml", cursor):
                end = raw.find(b"?>", cursor + 5)
                require(not roots and not stack and not declaration_seen and end >= 0 and raw[cursor + 5:cursor + 6] in (b" ", b"\t", b"\r", b"\n"), "misplaced_config_declaration")
                declaration_seen = True
                declaration = raw[cursor:end].decode("utf-8")
                encoding = re.search(r"encoding\s*=\s*(['\"])(.*?)\1", declaration)
                require(encoding is None or encoding[2].lower() in {"utf-8", "utf8"}, "config_requires_utf8")
                cursor = end + 2
                continue
            require(not raw.startswith((b"<!", b"<?"), cursor), "unsupported_config_declaration")
            end, quote = cursor + 1, None
            while end < len(raw):
                char = raw[end]
                if quote is not None:
                    if char == quote:
                        quote = None
                elif char in (34, 39):
                    quote = char
                elif char == 62:
                    break
                end += 1
            require(end < len(raw) and quote is None, "unterminated_config_tag")
            tag = raw[cursor + 1:end].decode("utf-8")
            if tag.startswith("/"):
                name = tag[1:].strip()
                require(valid_name(name) and bool(stack) and stack[-1].name == name, "mismatched_config_end_tag")
                stack.pop().content_end = cursor
            else:
                self_closing = tag.endswith("/")
                header = tag[:-1] if self_closing else tag
                match = re.match(r"([^\s]+)(.*)\Z", header, re.S)
                require(match is not None and valid_name(match[1]), "invalid_config_tag_name")
                attributes, seen = match[2], set()
                while attributes.strip():
                    attr = re.match(r"\s+([^\s=]+)\s*=\s*(['\"])(.*?)\2", attributes, re.S)
                    require(attr is not None and valid_name(attr[1]) and attr[1] not in seen, "invalid_or_duplicate_config_attribute")
                    decode_text(attr[3].encode("utf-8"))
                    seen.add(attr[1]);attributes = attributes[attr.end():]
                node = Node(match[1], end + 1, end + 1 if self_closing else -1, self_closing=self_closing)
                (stack[-1].children if stack else roots).append(node)
                nodes += 1
                require(nodes <= 1000000 and len(stack) < 256, "config_structure_limit")
                if not self_closing:
                    stack.append(node)
            cursor = end + 1
        require(not stack and len(roots) == 1, "missing_or_unclosed_config_root")
        self.root = roots[0]

    def select(self, path: tuple[str, ...]) -> Node:
        require(type(path) is tuple and bool(path) and all(type(name) is str for name in path), "config_path_tuple_required")
        candidates = [self.root]
        node = None
        for name in path:
            matches = [item for item in candidates if item.name == name]
            require(len(matches) == 1, "config_path_match_count:" + "/".join(path))
            node = matches[0]
            candidates = node.children
        return node

    def text(self, path: tuple[str, ...]) -> str:
        node = self.select(path)
        require(not node.children, "config_leaf_required")
        return decode_text(self.raw[node.content_start:node.content_end])

    def edited(self, edits: list[TextEdit]) -> bytes:
        spans = []
        paths = set()
        for edit in edits:
            require(isinstance(edit, TextEdit), "invalid_config_edit")
            node = self.select(edit.path)
            require(edit.path not in paths, "duplicate_config_edit")
            paths.add(edit.path)
            require(not node.self_closing, "cannot_edit_self_closing_config_leaf")
            require(type(edit.expected_old) is str and self.text(edit.path) == edit.expected_old, "config_stale_expected_value")
            require(type(edit.value) is str and all(xml_char(ord(c)) for c in edit.value), "invalid_config_replacement")
            value = edit.value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").encode("utf-8")
            spans.append((node.content_start, node.content_end, value))
        result = self.raw
        for begin, end, value in sorted(spans, reverse=True):
            result = result[:begin] + value + result[end:]
        readback = ConfigDocument(result)
        for edit in edits:
            require(readback.text(edit.path) == edit.value, "config_edit_readback_mismatch")
        return result
