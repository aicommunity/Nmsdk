#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление кракозябр в rdk_init.h и rdk_init.cpp.
1) Строки вида "Р'РѕР·Р²СЂР°С‰Р°РµС‚" — UTF-8, ошибочно прочитанный как CP1251: исправляем через encode('cp1251').decode('utf-8').
2) Строки с "пїЅ" — заменяем на правильный русский текст по контексту (следующая строка — объявление функции).
"""
import re
import sys
import os

# Маппинг: следующая строка (ключ) -> правильный комментарий для строк с пїЅ
COMMENT_MAP = [
    (r"Ver_CoreMinor", "/// Возвращает номер минорной версии ядра"),
    (r"Ver_CoreRevision", "/// Возвращает номер ревизии ядра"),
    (r"Ver_Core\(void\)", "/// Возвращает строку версии ядра в формате строки"),
    (r"Ver_CoreCompare", "/// Сравнивает версию ядра с переданной"),
    (r"Ver_CompilerName", "/// Возвращает имя компилятора ядра"),
    (r"Ver_CompilerVersion", "/// Возвращает версию компилятора ядра"),
    (r"Log_GetDebugMode", "/// Возвращает текущий режим отладки логгера ядра"),
    (r"Log_SetDebugMode", "/// Устанавливает текущий режим отладки логгера ядра"),
    (r"Log_GetDebugSysEventsMask", "/// Возвращает маску системных событий для отладки"),
    (r"Log_SetDebugSysEventsMask", "/// Устанавливает маску системных событий для отладки"),
    (r"Log_GetDebuggerMessageFlag", "/// Возвращает флаг вывода сообщений в отладчик"),
    (r"Log_SetDebuggerMessageFlag", "/// Устанавливает флаг вывода сообщений в отладчик"),
    (r"Log_LogMessage", "/// Записывает строку в лог ядра"),
    (r"Log_LogMessageEx", "/// Записывает в лог сообщение с номером события"),
    (r"Core_GetSystemDir", "/// Возвращает путь к системной директории ядра"),
    (r"Core_SetSystemDir", "/// Устанавливает путь к системной директории ядра"),
    (r"Core_GetLogDir", "/// Возвращает путь к директории логов ядра"),
    (r"Core_SetLogDir", "/// Устанавливает путь к директории логов ядра"),
    (r"Core_GetDebugMode", "/// Возвращает текущий режим отладки системных сообщений логгера ядра"),
    (r"Core_SetDebugMode", "/// Устанавливает текущий режим отладки системных сообщений логгера ядра"),
    (r"Core_GetDebuggerMessageFlag", "/// Возвращает флаг вывода сообщений в отладчик"),
    (r"Core_SetDebuggerMessageFlag", "/// Устанавливает флаг вывода сообщений в отладчик"),
    (r"Core_ClearFonts", "/// Очищает загруженные шрифты"),
    (r"Core_LoadFonts", "/// Загружает загруженные шрифты"),
    (r"Core_GetNumChannels", "/// Возвращает число каналов"),
    (r"Core_SetNumChannels", "/// Устанавливает число каналов ядра"),
]


def fix_cp1251_mojibake(line: str) -> str:
    """Если строка — комментарий с кракозябрами (UTF-8 прочитан как CP1251), исправить."""
    s = line.strip()
    if not (s.startswith("//") or s.startswith("///")):
        return line
    rest = s.lstrip("/").strip()
    if not rest or "пїЅ" in rest:
        return line
    # Проверяем, есть ли кириллица в виде кракозябр (Р, С, Рѕ и т.д. — типичный паттерн)
    try:
        # Кодируем строку как cp1251 (каждый символ -> байт), декодируем как utf-8
        decoded = rest.encode("cp1251").decode("utf-8")
        if decoded != rest and any("\u0400" <= c <= "\u04FF" for c in decoded):
            return line[: line.index(rest)] + decoded + "\n"
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass
    return line


def get_func_name_from_decl(line: str) -> str:
    """Из строки объявления извлечь имя функции (например Core_GetSystemDir)."""
    m = re.search(r"RDK_CALL\s+(\w+)\s*\(", line)
    return m.group(1) if m else ""


def fix_pyiny_line(line: str, following_lines: list) -> str:
    """Если в строке пїЅ-кракозябры, заменить на комментарий по следующему объявлению или общий."""
    # Проверка на кракозябры: пїЅ (U+043F U+0457 U+0405) или символ замены
    has_mojibake = (
        "пїЅ" in line
        or ("\u043f" in line and "\u0457" in line)
        or "\ufffd" in line
    )
    if not has_mojibake:
        return line
    s = line.strip()
    if not (s.startswith("//") or s.startswith("///")):
        return line
    indent = line[: len(line) - len(line.lstrip())]
    prefix = "//" if s.startswith("//") and not s.startswith("///") else "///"
    # Ищем по COMMENT_MAP в следующих строках
    for follow in following_lines:
        for pattern, comment in COMMENT_MAP:
            if re.search(pattern, follow):
                return indent + comment + "\n"
    # Иначе подставляем общий комментарий (всегда для строк с кракозябрами)
    return indent + prefix + " См. описание в rdk_init.cpp\n"


def process_file(path: str) -> bool:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    out = []
    for i, line in enumerate(lines):
        # Следующие 8 строк для поиска объявления функции
        following = lines[i + 1 : i + 9] if i + 1 < len(lines) else []
        fixed = fix_pyiny_line(line, following)
        if fixed != line:
            out.append(fixed)
            continue
        fixed = fix_cp1251_mojibake(line)
        out.append(fixed)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(out)
    return True


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rdk = os.path.join(root, "Rdk")
    for name in ["Deploy/Include/rdk_init.h", "Deploy/Include/rdk_init.cpp"]:
        path = os.path.join(rdk, name)
        if os.path.isfile(path):
            process_file(path)
            print(f"Processed: {path}")


if __name__ == "__main__":
    main()
