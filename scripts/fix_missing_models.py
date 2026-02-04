#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления проблем с отсутствующими файлами моделей.

Проверяет конфигурации с ошибкой "Model does not exist" и:
1. Проверяет наличие файлов Model_*.xml или model.xml
2. Обновляет пути в project.ini если нужно
3. Создает пустые Model_00.xml файлы если они отсутствуют
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple
import re

# Добавляем путь к скриптам
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class ModelFixer:
    """Класс для исправления проблем с отсутствующими моделями"""
    
    def __init__(self, configs_dir: str = "Bin/Configs", reports_dir: str = "Reports"):
        self.configs_dir = Path(configs_dir)
        self.reports_dir = Path(reports_dir)
        self.validation_report = self.reports_dir / "ConfigValidation-Detailed-Report.md"
        self.fixes_applied = []
        
    def find_configs_with_missing_models(self) -> List[Tuple[str, str]]:
        """Находит конфигурации с проблемой 'Model does not exist'"""
        if not self.validation_report.exists():
            print(f"Отчет валидации не найден: {self.validation_report}")
            return []
        
        content = self.validation_report.read_text(encoding='utf-8')
        problematic_configs = []
        current_config = None
        
        for line in content.split('\n'):
            if line.startswith('### '):
                current_config = line[4:].strip()
            if 'Model does not exist' in line or "Can't open model file" in line:
                if current_config and current_config not in [c[0] for c in problematic_configs]:
                    problematic_configs.append((current_config, line.strip()))
        
        return problematic_configs
    
    def check_model_file(self, project_path: Path, model_file_name: str) -> Tuple[bool, Path, bool]:
        """Проверяет наличие файла модели и его содержимое
        
        Returns:
            (exists, path, is_empty): существует ли файл, путь к файлу, пустой ли файл
        """
        if not model_file_name:
            return False, None, False
        
        # Проверяем относительный путь
        model_path = project_path / model_file_name
        if model_path.exists():
            # Проверяем, пустой ли файл
            is_empty = False
            try:
                tree = ET.parse(model_path)
                root = tree.getroot()
                model = root.find("Model")
                if model is not None:
                    components = model.find("Components")
                    links = model.find("Links")
                    comp_count = len(list(components)) if components is not None else 0
                    links_count = len(list(links)) if links is not None else 0
                    is_empty = (comp_count == 0 and links_count == 0)
            except:
                # Если не удалось распарсить, считаем что файл не пустой
                pass
            return True, model_path, is_empty
        
        # Проверяем абсолютный путь
        if Path(model_file_name).is_absolute() and Path(model_file_name).exists():
            return True, Path(model_file_name), False
        
        return False, model_path, False
    
    def create_empty_model_file(self, model_path: Path) -> bool:
        """Создает пустой файл модели"""
        try:
            # Создаем минимальную структуру Model_*.xml
            root = ET.Element("Save")
            model_elem = ET.SubElement(root, "Model")
            components_elem = ET.SubElement(model_elem, "Components")
            links_elem = ET.SubElement(model_elem, "Links")
            
            # Форматируем XML
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ")
            
            # Создаем директорию если нужно
            model_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Сохраняем файл
            tree.write(model_path, encoding='utf-8', xml_declaration=True)
            print(f"  ✅ Создан пустой файл модели: {model_path}")
            return True
        except Exception as e:
            print(f"  ❌ Ошибка при создании файла модели {model_path}: {e}")
            return False
    
    def fix_model_paths(self, project_ini_path: Path) -> bool:
        """Исправляет пути к моделям в project.ini"""
        project_path = project_ini_path.parent
        modified = False
        
        try:
            # Пробуем парсить XML
            try:
                tree = ET.parse(project_ini_path)
                root = tree.getroot()
            except ET.ParseError as e:
                # Если XML невалидный, пробуем найти ModelFileName другим способом
                print(f"  ⚠️  Ошибка парсинга XML, используем альтернативный метод")
                content = project_ini_path.read_text(encoding='utf-8', errors='ignore')
                
                # Ищем ModelFileName через регулярные выражения
                model_match = re.search(r'<ModelFileName>([^<]+)</ModelFileName>', content)
                if model_match:
                    model_file_name = model_match.group(1).strip()
                    exists, model_path, is_empty = self.check_model_file(project_path, model_file_name)
                    
                    if not exists and model_path:
                        if self.create_empty_model_file(model_path):
                            modified = True
                    elif exists and is_empty:
                        # Файл существует, но пустой - это нормально для некоторых конфигураций
                        # Не создаем новый файл, так как он уже существует
                        print(f"  ℹ️  Файл модели существует, но пустой: {model_path}")
                
                return modified
            
            # Проверяем каналы (новый формат)
            channels = root.find("Channels")
            if channels is not None:
                for channel in channels:
                    model_file_elem = channel.find("ModelFileName")
                    if model_file_elem is not None:
                        model_file_name = model_file_elem.text
                        if model_file_name:
                            exists, model_path, is_empty = self.check_model_file(project_path, model_file_name)
                            
                            if not exists:
                                # Пробуем альтернативные имена
                                alternatives = []
                                if model_file_name == "model.xml":
                                    alternatives = ["Model_00.xml", "Model.xml"]
                                elif model_file_name.startswith("Model_"):
                                    # Пробуем без префикса
                                    alternatives = ["model.xml", "Model.xml"]
                                
                                for alt in alternatives:
                                    alt_exists, alt_path, _ = self.check_model_file(project_path, alt)
                                    if alt_exists:
                                        print(f"  📝 Обновляем путь: {model_file_name} -> {alt}")
                                        model_file_elem.text = alt
                                        modified = True
                                        break
                                
                                # Если ничего не найдено, создаем пустой файл
                                if not modified and model_path:
                                    if self.create_empty_model_file(model_path):
                                        modified = True
                            elif exists and is_empty:
                                # Файл существует, но пустой - это нормально для некоторых конфигураций
                                print(f"  ℹ️  Файл модели существует, но пустой: {model_path}")
            else:
                # Старый формат - ModelFileName в секции General
                general = root.find("General")
                if general is not None:
                    model_file_elem = general.find("ModelFileName")
                    if model_file_elem is not None:
                        model_file_name = model_file_elem.text
                        if model_file_name:
                            exists, model_path, is_empty = self.check_model_file(project_path, model_file_name)
                            
                            if not exists:
                                # Пробуем альтернативные имена
                                alternatives = []
                                if model_file_name == "model.xml":
                                    alternatives = ["Model_00.xml", "Model.xml"]
                                elif model_file_name.startswith("Model_"):
                                    alternatives = ["model.xml", "Model.xml"]
                                
                                for alt in alternatives:
                                    alt_exists, alt_path, _ = self.check_model_file(project_path, alt)
                                    if alt_exists:
                                        print(f"  📝 Обновляем путь: {model_file_name} -> {alt}")
                                        model_file_elem.text = alt
                                        modified = True
                                        break
                                
                                # Если ничего не найдено, создаем пустой файл
                                if not modified and model_path:
                                    if self.create_empty_model_file(model_path):
                                        modified = True
                            elif exists and is_empty:
                                # Файл существует, но пустой - это нормально для некоторых конфигураций
                                print(f"  ℹ️  Файл модели существует, но пустой: {model_path}")
            
            if modified:
                try:
                    tree.write(project_ini_path, encoding='utf-8', xml_declaration=True)
                    print(f"  ✅ Обновлен project.ini: {project_ini_path}")
                except Exception as e:
                    print(f"  ⚠️  Не удалось сохранить project.ini: {e}")
                    # Но файл модели создан, так что считаем успешным
                    return True
            
            return modified
        except Exception as e:
            print(f"  ❌ Ошибка при обработке {project_ini_path}: {e}")
            return False
    
    def fix_config(self, config_rel_path: str) -> bool:
        """Исправляет одну конфигурацию"""
        # config_rel_path уже содержит "project.ini" в конце, нужно его убрать
        if config_rel_path.endswith("/project.ini") or config_rel_path.endswith("\\project.ini"):
            config_dir = config_rel_path.rsplit("/", 1)[0].rsplit("\\", 1)[0]
        else:
            config_dir = config_rel_path
        
        project_ini_path = self.configs_dir / config_dir / "project.ini"
        
        if not project_ini_path.exists():
            print(f"  ⚠️  project.ini не найден: {project_ini_path}")
            return False
        
        print(f"\nОбработка: {config_rel_path}")
        fixed = self.fix_model_paths(project_ini_path)
        
        if fixed:
            self.fixes_applied.append(config_rel_path)
        
        return fixed
    
    def run(self):
        """Запускает исправление всех проблемных конфигураций"""
        print("Поиск конфигураций с проблемой 'Model does not exist'...")
        problematic_configs = self.find_configs_with_missing_models()
        
        if not problematic_configs:
            print("Проблемных конфигураций не найдено.")
            return
        
        print(f"Найдено проблемных конфигураций: {len(problematic_configs)}")
        
        for config_path, error_msg in problematic_configs:
            self.fix_config(config_path)
        
        print(f"\n{'='*60}")
        print(f"Исправлено конфигураций: {len(self.fixes_applied)}")
        
        if self.fixes_applied:
            print("\nИсправленные конфигурации:")
            for config in self.fixes_applied:
                print(f"  - {config}")
        
        # Сохраняем отчет
        self.save_report()
    
    def save_report(self):
        """Сохраняет отчет об исправлениях"""
        report_path = self.reports_dir / "ModelFixes-Report.md"
        
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# Отчет об исправлении проблем с моделями

**Дата создания:** {now}

**Всего исправлено конфигураций:** {len(self.fixes_applied)}

## Детали исправлений

"""
        
        for config in self.fixes_applied:
            report += f"### {config}\n\n"
            report += f"- Исправлены пути к файлам моделей в project.ini\n"
            report += f"- Созданы отсутствующие файлы Model_*.xml (если требовалось)\n\n"
        
        report_path.write_text(report, encoding='utf-8')
        print(f"\nОтчет сохранен: {report_path}")

if __name__ == "__main__":
    fixer = ModelFixer()
    fixer.run()
