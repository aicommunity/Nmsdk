#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для генерации детального отчета валидации конфигураций.
Группирует ошибки по типам и предоставляет детальный анализ проблем.
"""

import subprocess
import re
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# Пути
CONSOLE_EXE = "./Bin/Platform/Linux/NeuroModelerConsole"
REPORT_FILE = "Reports/ConfigValidation-Detailed-Report.md"
RESULTS_FILE = "Reports/ConfigValidation-Results.jsonl"
CONFIGS_DIR = Path("Bin/Configs")

# Типы ошибок
class ErrorType:
    NONEXISTENT_CLASS = "Несуществующие классы компонентов"
    NONEXISTENT_COMPONENT = "Несуществующие компоненты"
    INVALID_LINK = "Неправильные связи"
    MISSING_FILE = "Отсутствующие файлы"
    MODEL_LOAD_ERROR = "Ошибки загрузки моделей"
    MODEL_NOT_EXISTS = "Модель не существует"
    OTHER = "Другие ошибки"

# Структуры для хранения данных
class ErrorInfo:
    def __init__(self, error_type: str, message: str, channel: int = None, 
                 component: str = None, link: int = None, connector: int = None,
                 class_name: str = None, missing_component: str = None):
        self.error_type = error_type
        self.message = message
        self.channel = channel
        self.component = component
        self.link = link
        self.connector = connector
        self.class_name = class_name
        self.missing_component = missing_component

def parse_error_message(error: str) -> ErrorInfo:
    """Парсит сообщение об ошибке и извлекает структурированную информацию."""
    
    # Несуществующий класс (Model level)
    match = re.search(r"Model:\s+Component\s+'([^']+)':\s+Class\s+'([^']+)'\s+does not exist", error)
    if match:
        return ErrorInfo(
            ErrorType.NONEXISTENT_CLASS,
            error,
            component=match.group(1),
            class_name=match.group(2)
        )
    
    # Несуществующий класс (Channel level)
    match = re.search(r"Channel\s+(\d+),\s+Component\s+'([^']+)':\s+Class\s+'([^']+)'\s+does not exist", error)
    if match:
        return ErrorInfo(
            ErrorType.NONEXISTENT_CLASS,
            error,
            channel=int(match.group(1)),
            component=match.group(2),
            class_name=match.group(3)
        )
    
    # Несуществующий компонент-источник в связи
    match = re.search(r"Channel\s+(\d+),\s+Component\s+([^,]+),\s+Link\s+(\d+):\s+Source component\s+'([^']+)'\s+does not exist", error)
    if match:
        return ErrorInfo(
            ErrorType.INVALID_LINK,
            error,
            channel=int(match.group(1)),
            component=match.group(2).strip(),
            link=int(match.group(3)),
            missing_component=match.group(4)
        )
    
    # Несуществующий компонент-приемник в связи
    match = re.search(r"Channel\s+(\d+),\s+Component\s+([^,]+),\s+Link\s+(\d+)(?:,\s+Connector\s+(\d+))?:\s+Destination component\s+'([^']+)'\s+does not exist", error)
    if match:
        return ErrorInfo(
            ErrorType.INVALID_LINK,
            error,
            channel=int(match.group(1)),
            component=match.group(2).strip(),
            link=int(match.group(3)),
            connector=int(match.group(4)) if match.group(4) else None,
            missing_component=match.group(5)
        )
    
    # Модель не существует
    match = re.search(r"Channel\s+(\d+):\s+Model does not exist", error)
    if match:
        return ErrorInfo(
            ErrorType.MODEL_NOT_EXISTS,
            error,
            channel=int(match.group(1))
        )
    
    # Ошибка загрузки файла
    match = re.search(r"Failed to load model file:\s+(.+)", error)
    if match:
        return ErrorInfo(
            ErrorType.MODEL_LOAD_ERROR,
            error,
            missing_component=match.group(1)
        )
    
    # Отсутствующий файл
    if "missing file" in error.lower() or "file not found" in error.lower():
        return ErrorInfo(ErrorType.MISSING_FILE, error)
    
    # Другие ошибки
    return ErrorInfo(ErrorType.OTHER, error)

def validate_config(config_path: Path) -> Dict:
    """Валидирует одну конфигурацию и возвращает структурированные результаты."""
    rel_path = str(config_path.relative_to(CONFIGS_DIR))
    
    try:
        result = subprocess.run(
            [CONSOLE_EXE, "--check-config", str(config_path)],
            capture_output=True,
            text=True,
            timeout=15
        )
        output = result.stdout + result.stderr
        
        # Парсим базовую информацию
        status_match = re.search(r'Configuration is (\w+)', output)
        errors_match = re.search(r'Errors: (\d+)', output)
        warnings_match = re.search(r'Warnings: (\d+)', output)
        channels_match = re.search(r'Channels loaded: (\d+)/(\d+)', output)
        components_match = re.search(r'Components count per channel: (.+)', output)
        
        status = status_match.group(1) if status_match else "UNKNOWN"
        errors_count = int(errors_match.group(1)) if errors_match else 0
        warnings_count = int(warnings_match.group(1)) if warnings_match else 0
        channels = channels_match.groups() if channels_match else (None, None)
        components = components_match.group(1) if components_match else None
        
        # Извлекаем ошибки
        error_lines = []
        lines = output.split('\n')
        for i, line in enumerate(lines):
            # Ищем заголовок "Errors:" (без числа после двоеточия) - это заголовок списка ошибок
            stripped = line.strip()
            if stripped == 'Errors:' and errors_count > 0:
                # Следующие строки до "Warnings:" или "Configuration is" содержат ошибки
                for j in range(i + 1, len(lines)):
                    next_line = lines[j].strip()
                    if next_line.startswith('- '):
                        error_lines.append(next_line[2:])  # Убираем "- "
                    elif next_line and ('Warnings:' in next_line or 'Configuration is' in next_line):
                        break
                break
        
        # Парсим ошибки
        parsed_errors = []
        error_groups = defaultdict(list)
        nonexistent_classes = set()
        nonexistent_components = set()
        invalid_links = []
        
        for error in error_lines:
            error_info = parse_error_message(error)
            parsed_errors.append(error_info)
            error_groups[error_info.error_type].append(error_info)
            
            if error_info.error_type == ErrorType.NONEXISTENT_CLASS and error_info.class_name:
                nonexistent_classes.add((error_info.component, error_info.class_name))
            
            if error_info.missing_component:
                nonexistent_components.add(error_info.missing_component)
            
            if error_info.error_type == ErrorType.INVALID_LINK:
                invalid_links.append(error_info)
        
        # Извлекаем предупреждения
        warning_lines = []
        in_warnings = False
        for line in output.split('\n'):
            if 'Warnings:' in line and warnings_count > 0:
                in_warnings = True
                continue
            if in_warnings and line.strip().startswith('- '):
                warning_lines.append(line.strip()[2:])
            elif in_warnings and line.strip() and not line.strip().startswith('- '):
                if 'Configuration is' in line:
                    break
        
        return {
            'path': rel_path,
            'status': status,
            'errors_count': errors_count,
            'warnings_count': warnings_count,
            'channels': channels,
            'components': components,
            'parsed_errors': parsed_errors,
            'error_groups': dict(error_groups),
            'nonexistent_classes': nonexistent_classes,
            'nonexistent_components': nonexistent_components,
            'invalid_links': invalid_links,
            'warnings': warning_lines,
            'output': output
        }
        
    except subprocess.TimeoutExpired:
        return {
            'path': rel_path,
            'status': 'TIMEOUT',
            'errors_count': 0,
            'warnings_count': 0,
            'channels': (None, None),
            'components': None,
            'parsed_errors': [],
            'error_groups': {},
            'nonexistent_classes': set(),
            'nonexistent_components': set(),
            'invalid_links': [],
            'warnings': [],
            'output': 'Timeout after 15 seconds'
        }
    except Exception as e:
        return {
            'path': rel_path,
            'status': 'ERROR',
            'errors_count': 0,
            'warnings_count': 0,
            'channels': (None, None),
            'components': None,
            'parsed_errors': [],
            'error_groups': {},
            'nonexistent_classes': set(),
            'nonexistent_components': set(),
            'invalid_links': [],
            'warnings': [],
            'output': f'Exception: {str(e)}'
        }

def generate_detailed_report(results: List[Dict]) -> str:
    """Генерирует детальный отчет в формате Markdown."""
    
    # Общая статистика по типам ошибок
    total_errors_by_type = defaultdict(int)
    total_nonexistent_classes = set()
    total_nonexistent_components = set()
    total_invalid_links = 0
    
    for result in results:
        for error_type, errors in result['error_groups'].items():
            total_errors_by_type[error_type] += len(errors)
        total_nonexistent_classes.update(result['nonexistent_classes'])
        total_nonexistent_components.update(result['nonexistent_components'])
        total_invalid_links += len(result['invalid_links'])
    
    # Генерируем отчет
    report = []
    report.append("# Детальный отчет валидации конфигураций\n")
    report.append(f"**Дата создания:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"**Инструмент:** NeuroModelerConsole --check-config\n")
    report.append(f"**Всего конфигураций:** {len(results)}\n")
    
    # Сводка
    valid_count = sum(1 for r in results if r['status'] == 'VALID')
    invalid_count = len(results) - valid_count
    
    report.append("\n## Общая сводка\n\n")
    report.append("| Показатель | Значение |\n")
    report.append("|------------|----------|\n")
    report.append(f"| Всего конфигураций | {len(results)} |\n")
    report.append(f"| Валидных | {valid_count} |\n")
    report.append(f"| Невалидных | {invalid_count} |\n")
    
    # Сводка по типам ошибок
    report.append("\n## Сводка по типам ошибок\n\n")
    report.append("| Тип ошибки | Количество |\n")
    report.append("|------------|-----------|\n")
    for error_type in [ErrorType.NONEXISTENT_CLASS, ErrorType.NONEXISTENT_COMPONENT, 
                       ErrorType.INVALID_LINK, ErrorType.MISSING_FILE, 
                       ErrorType.MODEL_LOAD_ERROR, ErrorType.MODEL_NOT_EXISTS, ErrorType.OTHER]:
        count = total_errors_by_type.get(error_type, 0)
        if count > 0:
            report.append(f"| {error_type} | {count} |\n")
    
    report.append(f"\n| Уникальных несуществующих классов | {len(total_nonexistent_classes)} |\n")
    report.append(f"| Уникальных несуществующих компонентов | {len(total_nonexistent_components)} |\n")
    report.append(f"| Всего неправильных связей | {total_invalid_links} |\n")
    
    # Детали по конфигурациям
    report.append("\n## Детали по конфигурациям\n\n")
    
    for result in results:
        if result['status'] == 'VALID' and result['errors_count'] == 0:
            # Пропускаем валидные конфигурации без ошибок
            continue
        
        report.append(f"### {result['path']}\n\n")
        report.append(f"**Статус:** {result['status']}\n")
        report.append(f"**Ошибок:** {result['errors_count']}\n")
        report.append(f"**Предупреждений:** {result['warnings_count']}\n")
        
        if result['channels'][0] is not None:
            report.append(f"**Каналов загружено:** {result['channels'][0]}/{result['channels'][1]}\n")
        if result['components']:
            report.append(f"**Компонентов:** {result['components']}\n")
        report.append("\n")
        
        # Несуществующие классы
        if result['nonexistent_classes']:
            report.append(f"#### {ErrorType.NONEXISTENT_CLASS}\n\n")
            for component, class_name in sorted(result['nonexistent_classes']):
                report.append(f"- **Компонент:** `{component}` → **Класс:** `{class_name}` (не существует)\n")
            report.append("\n")
        
        # Несуществующие компоненты
        if result['nonexistent_components']:
            report.append(f"#### {ErrorType.NONEXISTENT_COMPONENT}\n\n")
            # Группируем по компонентам, где они используются
            component_usage = defaultdict(list)
            for error in result['parsed_errors']:
                if error.missing_component:
                    usage_info = f"Канал {error.channel}"
                    if error.component:
                        usage_info += f", компонент {error.component}"
                    if error.link is not None:
                        usage_info += f", связь {error.link}"
                    component_usage[error.missing_component].append(usage_info)
            
            for component in sorted(result['nonexistent_components']):
                usages = component_usage.get(component, [])
                report.append(f"- **Компонент:** `{component}` (не существует)\n")
                if usages:
                    report.append(f"  Используется в: {', '.join(usages[:3])}")
                    if len(usages) > 3:
                        report.append(f" и еще {len(usages) - 3} местах")
                    report.append("\n")
            report.append("\n")
        
        # Неправильные связи
        if result['invalid_links']:
            report.append(f"#### {ErrorType.INVALID_LINK}\n\n")
            # Группируем связи
            links_by_component = defaultdict(list)
            for link in result['invalid_links']:
                key = f"{link.component} (канал {link.channel})"
                links_by_component[key].append(link)
            
            for component_key, links in links_by_component.items():
                report.append(f"**Компонент:** {component_key}\n\n")
                for link in links:
                    link_desc = f"Связь {link.link}"
                    if link.connector is not None:
                        link_desc += f", коннектор {link.connector}"
                    if link.missing_component:
                        link_desc += f": отсутствует компонент `{link.missing_component}`"
                    report.append(f"- {link_desc}\n")
                report.append("\n")
        
        # Другие типы ошибок
        other_errors = []
        for error_type in [ErrorType.MISSING_FILE, ErrorType.MODEL_LOAD_ERROR, 
                          ErrorType.MODEL_NOT_EXISTS, ErrorType.OTHER]:
            if error_type in result['error_groups']:
                other_errors.extend(result['error_groups'][error_type])
        
        if other_errors:
            report.append(f"#### Другие ошибки\n\n")
            for error in other_errors[:10]:
                report.append(f"- {error.message}\n")
            if len(other_errors) > 10:
                report.append(f"- ... и еще {len(other_errors) - 10} ошибок\n")
            report.append("\n")
        
        # Предупреждения
        if result['warnings']:
            report.append("#### Предупреждения\n\n")
            for warning in result['warnings'][:10]:
                report.append(f"- {warning}\n")
            if len(result['warnings']) > 10:
                report.append(f"- ... и еще {len(result['warnings']) - 10} предупреждений\n")
            report.append("\n")
    
    return ''.join(report)

def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(description="Generate config validation report (incremental).")
    parser.add_argument(
        "--time-budget-seconds",
        type=int,
        default=540,
        help="Stop after this many seconds (default: 540) and save partial results.",
    )
    parser.add_argument(
        "--finalize",
        action="store_true",
        help="Force (re)generate markdown report from accumulated JSONL results.",
    )
    args = parser.parse_args()

    print("Начинаю генерацию детального отчета валидации...")
    print(f"Time budget: {args.time_budget_seconds}s")
    print(f"Console: {CONSOLE_EXE}")
    print(f"Results cache: {RESULTS_FILE}")
    print("")

    # Проверяем наличие консоли
    if not Path(CONSOLE_EXE).exists():
        print(f"ОШИБКА: NeuroModelerConsole не найден: {CONSOLE_EXE}", file=sys.stderr)
        sys.exit(2)
    
    # Находим все конфигурации
    configs = sorted(CONFIGS_DIR.rglob("project.ini"))
    total = len(configs)
    
    print(f"Найдено конфигураций: {total}")
    print("Начинаю валидацию (инкрементально)...")
    print("")

    # Загружаем уже обработанные результаты из JSONL (если есть)
    results_by_path: Dict[str, Dict] = {}
    results_path = Path(RESULTS_FILE)
    results_path.parent.mkdir(parents=True, exist_ok=True)
    if results_path.exists():
        try:
            with open(results_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        if isinstance(obj, dict) and "path" in obj:
                            results_by_path[obj["path"]] = obj
                    except json.JSONDecodeError:
                        # Пропускаем битые строки
                        continue
        except Exception:
            # Если файл недоступен/битый - продолжим без кеша
            results_by_path = {}

    start_time = time.monotonic()
    processed_now = 0
    remaining_before = total - len(results_by_path)

    if remaining_before <= 0:
        print("Все конфигурации уже провалидированы (по кешу).")
    else:
        print(f"Уже есть результатов: {len(results_by_path)}. Осталось: {remaining_before}.")

        with open(results_path, "a", encoding="utf-8") as out:
            for i, config_path in enumerate(configs, 1):
                rel_path = str(config_path.relative_to(CONFIGS_DIR))
                if rel_path in results_by_path:
                    continue

                elapsed = time.monotonic() - start_time
                if elapsed >= args.time_budget_seconds:
                    print("")
                    print(f"Остановка по time-budget. Обработано за этот запуск: {processed_now}.")
                    break

                print(f"[{i}/{total}] {rel_path}")
                result = validate_config(config_path)

                # Превращаем в JSON-совместимый вид
                json_obj = {
                    "path": result.get("path"),
                    "status": result.get("status"),
                    "errors_count": result.get("errors_count"),
                    "warnings_count": result.get("warnings_count"),
                    "channels": list(result.get("channels")) if result.get("channels") else [None, None],
                    "components": result.get("components"),
                    "warnings": result.get("warnings", []),
                    "nonexistent_classes": sorted(
                        [{"component": c, "class": cls} for (c, cls) in result.get("nonexistent_classes", set())],
                        key=lambda x: (x["class"], x["component"]),
                    ),
                    "nonexistent_components": sorted(list(result.get("nonexistent_components", set()))),
                    # Для отладки оставляем сырой вывод (может быть большой, но конфигов всего ~123)
                    "output": result.get("output", ""),
                }

                out.write(json.dumps(json_obj, ensure_ascii=False) + "\n")
                out.flush()
                results_by_path[rel_path] = json_obj
                processed_now += 1

    remaining_after = total - len(results_by_path)

    # Если всё провалидировано или пользователь запросил finalize — генерируем md-отчет
    if args.finalize or remaining_after == 0:
        print("")
        print("Генерирую отчет...")

        # Восстанавливаем структуру results, близкую к исходной generate_detailed_report()
        results: List[Dict] = []
        for config_path in configs:
            rel_path = str(config_path.relative_to(CONFIGS_DIR))
            cached = results_by_path.get(rel_path)
            if not cached:
                continue

            # Минимальная реконструкция: для generate_detailed_report важны группы/множества.
            error_groups = defaultdict(list)
            parsed_errors: List[ErrorInfo] = []

            # Парсим ошибки из output так же, как в validate_config (чтобы не хранить промежуточные структуры)
            output = cached.get("output", "")
            errors_match = re.search(r"Errors: (\d+)", output)
            errors_count = int(errors_match.group(1)) if errors_match else int(cached.get("errors_count") or 0)
            error_lines = []
            lines = output.split("\n")
            for idx, line in enumerate(lines):
                stripped = line.strip()
                if stripped == "Errors:" and errors_count > 0:
                    for j in range(idx + 1, len(lines)):
                        next_line = lines[j].strip()
                        if next_line.startswith("- "):
                            error_lines.append(next_line[2:])
                        elif next_line and ("Warnings:" in next_line or "Configuration is" in next_line):
                            break
                    break

            nonexistent_classes = set()
            nonexistent_components = set()
            invalid_links = []
            for err in error_lines:
                info = parse_error_message(err)
                parsed_errors.append(info)
                error_groups[info.error_type].append(info)
                if info.error_type == ErrorType.NONEXISTENT_CLASS and info.class_name:
                    nonexistent_classes.add((info.component, info.class_name))
                if info.missing_component:
                    nonexistent_components.add(info.missing_component)
                if info.error_type == ErrorType.INVALID_LINK:
                    invalid_links.append(info)

            results.append(
                {
                    "path": cached.get("path"),
                    "status": cached.get("status"),
                    "errors_count": cached.get("errors_count", 0),
                    "warnings_count": cached.get("warnings_count", 0),
                    "channels": tuple(cached.get("channels", [None, None])),
                    "components": cached.get("components"),
                    "parsed_errors": parsed_errors,
                    "error_groups": dict(error_groups),
                    "nonexistent_classes": nonexistent_classes,
                    "nonexistent_components": nonexistent_components,
                    "invalid_links": invalid_links,
                    "warnings": cached.get("warnings", []),
                    "output": output,
                }
            )

        report_content = generate_detailed_report(results)

        report_path = Path(REPORT_FILE)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        # Статистика
        valid = sum(1 for r in results if r["status"] == "VALID")
        invalid = len(results) - valid

        print("")
        print("Детальный отчет создан!")
        print(f"Отчет сохранен в: {REPORT_FILE}")
        print("")
        print("Статистика:")
        print(f"  Всего: {len(results)}")
        print(f"  Валидных: {valid}")
        print(f"  Невалидных: {invalid}")

        total_errors_by_type = defaultdict(int)
        for result in results:
            for error_type, errors in result["error_groups"].items():
                total_errors_by_type[error_type] += len(errors)
        if total_errors_by_type:
            print("")
            print("Ошибки по типам:")
            for error_type, count in sorted(total_errors_by_type.items(), key=lambda x: x[1], reverse=True):
                print(f"  {error_type}: {count}")
    else:
        print("")
        print(f"Частичный прогон завершен. Осталось конфигураций: {remaining_after}.")
    
    # Возвращаем 0 всегда: кеш/отчет могут генерироваться по частям.

if __name__ == "__main__":
    main()
