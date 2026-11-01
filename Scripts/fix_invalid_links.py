#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления неправильных связей в Model_*.xml.

Удаляет связи на несуществующие компоненты или создает недостающие компоненты,
если они должны существовать согласно Parameters_*.xml.
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Set
import re
from collections import defaultdict

# Добавляем путь к скриптам
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class InvalidLinksFixer:
    """Исправляет неправильные связи в Model_*.xml"""
    
    def __init__(self, configs_dir: str = "Bin/Configs", reports_dir: str = "Reports"):
        self.configs_dir = Path(configs_dir)
        self.reports_dir = Path(reports_dir)
        self.validation_report = self.reports_dir / "ConfigValidation-Detailed-Report.md"
        self.fixes_applied = []
        
    def find_configs_with_invalid_links(self) -> List[str]:
        """Находит конфигурации с неправильными связями"""
        if not self.validation_report.exists():
            print(f"Отчет валидации не найден: {self.validation_report}")
            return []
        
        content = self.validation_report.read_text(encoding='utf-8')
        problematic_configs = set()
        current_config = None
        current_section = None
        
        for line in content.split('\n'):
            if line.startswith('### '):
                current_config = line[4:].strip()
                current_section = None
                continue
            if line.startswith('#### '):
                current_section = line[5:].strip()
                continue
            
            if current_section == 'Неправильные связи' and current_config:
                problematic_configs.add(current_config)
        
        return list(problematic_configs)
    
    def get_existing_components(self, model_file: Path) -> Set[str]:
        """Получает список существующих компонентов из Model_*.xml"""
        components = set()
        
        if not model_file.exists():
            return components
        
        try:
            tree = ET.parse(model_file)
            root = tree.getroot()
            model = root.find("Model")
            if model is not None:
                comps_elem = model.find("Components")
                if comps_elem is not None:
                    # Рекурсивно собираем все компоненты (включая вложенные)
                    def collect_components(elem, prefix=""):
                        for child in elem:
                            comp_name = child.tag
                            full_name = f"{prefix}.{comp_name}" if prefix else comp_name
                            components.add(full_name)
                            components.add(comp_name)  # Также добавляем короткое имя
                            # Рекурсивно обрабатываем вложенные компоненты
                            collect_components(child, full_name)
                    
                    collect_components(comps_elem)
        except Exception as e:
            print(f"  ⚠️  Ошибка парсинга Model: {e}")
        
        return components
    
    def fix_links(self, model_file: Path, existing_components: Set[str]) -> bool:
        """Исправляет неправильные связи в Model_*.xml"""
        modified = False
        
        try:
            if not model_file.exists():
                return False
            
            tree = ET.parse(model_file)
            root = tree.getroot()
            model = root.find("Model")
            if model is None:
                return False
            
            links = model.find("Links")
            if links is None:
                return False
            
            # Проверяем каждую связь
            links_to_remove = []
            
            for link in list(links):
                # Проверяем источник связи
                source_id = link.get("Source", "")
                if source_id:
                    # Извлекаем имя компонента (до первой точки)
                    source_comp = source_id.split('.')[0] if '.' in source_id else source_id
                    if source_comp and source_comp not in existing_components:
                        print(f"    ⚠️  Связь с несуществующим источником: {source_id}")
                        links_to_remove.append(link)
                        modified = True
                        continue
                
                # Проверяем приемники связи
                connectors = link.findall("Connector")
                invalid_connectors = []
                
                for connector in connectors:
                    dest_id = connector.get("Destination", "")
                    if dest_id:
                        # Извлекаем имя компонента (до первой точки)
                        dest_comp = dest_id.split('.')[0] if '.' in dest_id else dest_id
                        if dest_comp and dest_comp not in existing_components:
                            print(f"    ⚠️  Связь с несуществующим приемником: {dest_id}")
                            invalid_connectors.append(connector)
                            modified = True
                
                # Удаляем невалидные коннекторы
                for connector in invalid_connectors:
                    link.remove(connector)
                
                # Если все коннекторы удалены, удаляем всю связь
                if len(link.findall("Connector")) == 0:
                    links_to_remove.append(link)
            
            # Удаляем невалидные связи
            for link in links_to_remove:
                links.remove(link)
            
            if modified:
                ET.indent(tree, space="  ")
                tree.write(model_file, encoding='utf-8', xml_declaration=True)
                print(f"  ✅ Обновлен: {model_file}")
            
            return modified
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            return False
    
    def fix_config(self, config_path: str) -> bool:
        """Исправляет одну конфигурацию"""
        # Убираем "/project.ini" из конца пути если есть
        if config_path.endswith("/project.ini") or config_path.endswith("\\project.ini"):
            config_path = config_path.rsplit("/", 1)[0].rsplit("\\", 1)[0]
        
        config_dir = self.configs_dir / config_path
        project_ini = config_dir / "project.ini"
        
        if not project_ini.exists():
            return False
        
        try:
            project_content = project_ini.read_text(encoding='utf-8', errors='ignore')
            
            # Находим Model файл
            model_match = re.search(r'<ModelFileName>([^<]+)</ModelFileName>', project_content)
            if not model_match:
                return False
            
            model_file = config_dir / model_match.group(1).strip()
            
            print(f"\nОбработка: {config_path}")
            
            # Получаем существующие компоненты
            existing_components = self.get_existing_components(model_file)
            
            # Исправляем связи
            return self.fix_links(model_file, existing_components)
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            return False
    
    def run(self):
        """Запускает исправление всех проблемных конфигураций"""
        print("Поиск конфигураций с неправильными связями...")
        problematic_configs = self.find_configs_with_invalid_links()
        
        if not problematic_configs:
            print("Проблемных конфигураций не найдено.")
            return
        
        print(f"Найдено проблемных конфигураций: {len(problematic_configs)}")
        print(f"Обрабатываем все конфигурации...")
        
        for config_path in problematic_configs:
            if self.fix_config(config_path):
                self.fixes_applied.append(config_path)
        
        print(f"\n{'='*60}")
        print(f"Исправлено конфигураций: {len(self.fixes_applied)}")
        
        if self.fixes_applied:
            print("\nИсправленные конфигурации:")
            for config in self.fixes_applied[:10]:
                print(f"  - {config}")
            if len(self.fixes_applied) > 10:
                print(f"  ... и еще {len(self.fixes_applied) - 10} конфигураций")

if __name__ == "__main__":
    fixer = InvalidLinksFixer()
    fixer.run()
