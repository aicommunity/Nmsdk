#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки и исправления несоответствий классов компонентов
между Parameters_*.xml (ожидаемые) и Model_*.xml (фактические).
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
import re

class ComponentClassFixer:
    """Исправляет несоответствия классов компонентов"""
    
    def __init__(self, configs_dir: str = "Bin/Configs", reports_dir: str = "Reports"):
        self.configs_dir = Path(configs_dir)
        self.reports_dir = Path(reports_dir)
        self.validation_report = self.reports_dir / "ConfigValidation-Detailed-Report.md"
        self.fixes_applied = []
        
    def get_expected_classes(self, params_file: Path) -> dict:
        """Извлекает ожидаемые классы компонентов из Parameters"""
        expected = {}
        
        try:
            content = params_file.read_text(encoding='utf-8', errors='ignore')
            
            # Маппинг компонентов на параметры
            component_params = {
                'LTZone': 'LTZoneClassName',
                'PosGenerator': 'ExcGeneratorClassName',
                'NegGenerator': 'InhGeneratorClassName',
                'Soma': 'MembraneClassName',  # Для всех Soma*
                'Dendrite': 'MembraneClassName',  # Для всех Dendrite*
                'LTMembrane': 'LTMembraneClassName',  # LTMembrane компонент
                'Receptor': 'ReceptorClassName',  # Receptor компонент
            }
            
            for comp_type, param_name in component_params.items():
                pattern = rf'<{re.escape(param_name)}[^>]*>([^<]+)</{re.escape(param_name)}>'
                match = re.search(pattern, content)
                if match:
                    expected[comp_type] = match.group(1).strip()
        except Exception as e:
            print(f"  ⚠️  Ошибка чтения Parameters: {e}")
        
        return expected
    
    def fix_model_classes(self, model_file: Path, expected_classes: dict, missing_components: list) -> bool:
        """Исправляет классы компонентов в Model и добавляет отсутствующие"""
        modified = False
        
        try:
            # Загружаем Model
            if model_file.exists():
                tree = ET.parse(model_file)
                root = tree.getroot()
            else:
                root = ET.Element("Save")
                tree = ET.ElementTree(root)
            
            model = root.find("Model")
            if model is None:
                model = ET.SubElement(root, "Model")
            
            components = model.find("Components")
            if components is None:
                components = ET.SubElement(model, "Components")
            
            # Проверяем и исправляем существующие компоненты
            for comp in list(components):
                comp_name = comp.tag
                comp_class = comp.get("Class", "")
                
                # Определяем ожидаемый класс
                expected_class = None
                if comp_name == "LTZone" and "LTZone" in expected_classes:
                    expected_class = expected_classes["LTZone"]
                elif comp_name == "PosGenerator" and "PosGenerator" in expected_classes:
                    expected_class = expected_classes["PosGenerator"]
                elif comp_name == "NegGenerator" and "NegGenerator" in expected_classes:
                    expected_class = expected_classes["NegGenerator"]
                elif comp_name.startswith("Soma") and "Soma" in expected_classes:
                    expected_class = expected_classes["Soma"]
                elif comp_name.startswith("Dendrite") and "Dendrite" in expected_classes:
                    expected_class = expected_classes["Dendrite"]
                elif comp_name == "LTMembrane" and "LTMembrane" in expected_classes:
                    expected_class = expected_classes["LTMembrane"]
                elif comp_name == "Receptor" and "Receptor" in expected_classes:
                    expected_class = expected_classes["Receptor"]
                
                if expected_class and comp_class != expected_class:
                    comp.set("Class", expected_class)
                    modified = True
                    print(f"    ✅ Исправлен класс {comp_name}: {comp_class} -> {expected_class}")
            
            # Добавляем отсутствующие компоненты
            for comp_name in missing_components:
                if components.find(comp_name) is None:
                    expected_class = None
                    if comp_name == "LTZone" and "LTZone" in expected_classes:
                        expected_class = expected_classes["LTZone"]
                    elif comp_name == "PosGenerator" and "PosGenerator" in expected_classes:
                        expected_class = expected_classes["PosGenerator"]
                    elif comp_name == "NegGenerator" and "NegGenerator" in expected_classes:
                        expected_class = expected_classes["NegGenerator"]
                    elif comp_name.startswith("Soma") and "Soma" in expected_classes:
                        expected_class = expected_classes["Soma"]
                    elif comp_name.startswith("Dendrite") and "Dendrite" in expected_classes:
                        expected_class = expected_classes["Dendrite"]
                    elif comp_name == "LTMembrane" and "LTMembrane" in expected_classes:
                        expected_class = expected_classes["LTMembrane"]
                    elif comp_name == "Receptor" and "Receptor" in expected_classes:
                        expected_class = expected_classes["Receptor"]
                    
                    if expected_class:
                        comp_elem = ET.Element(comp_name)
                        comp_elem.set("Class", expected_class)
                        components.append(comp_elem)
                        modified = True
                        print(f"    ✅ Добавлен компонент {comp_name} с классом {expected_class}")
            
            if modified:
                ET.indent(tree, space="  ")
                model_file.parent.mkdir(parents=True, exist_ok=True)
                tree.write(model_file, encoding='utf-8', xml_declaration=True)
                print(f"  ✅ Обновлен: {model_file}")
            
            return modified
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            return False
    
    def fix_config(self, config_path: str, missing_components: list) -> bool:
        """Исправляет одну конфигурацию"""
        # Убираем "/project.ini" из конца пути если есть
        if config_path.endswith("/project.ini") or config_path.endswith("\\project.ini"):
            config_path = config_path.rsplit("/", 1)[0].rsplit("\\", 1)[0]
        
        config_dir = self.configs_dir / config_path
        
        # Находим файлы
        project_ini = config_dir / "project.ini"
        if not project_ini.exists():
            return False
        
        try:
            project_content = project_ini.read_text(encoding='utf-8', errors='ignore')
            
            # Находим Parameters
            params_match = re.search(r'<ParametersFileName>([^<]+)</ParametersFileName>', project_content)
            model_match = re.search(r'<ModelFileName>([^<]+)</ModelFileName>', project_content)
            
            if not params_match or not model_match:
                return False
            
            params_file = config_dir / params_match.group(1).strip()
            model_file = config_dir / model_match.group(1).strip()
            
            if not params_file.exists():
                return False
            
            print(f"\nОбработка: {config_path}")
            
            # Получаем ожидаемые классы
            expected_classes = self.get_expected_classes(params_file)
            if not expected_classes:
                print(f"  ⚠️  Не найдены параметры классов в Parameters")
                return False
            
            # Исправляем Model
            return self.fix_model_classes(model_file, expected_classes, missing_components)
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            return False
    
    def run(self):
        """Запускает исправление"""
        # Находим конфигурации с проблемами из отчета
        if not self.validation_report.exists():
            print("Отчет валидации не найден")
            return
        
        content = self.validation_report.read_text(encoding='utf-8')
        
        # Парсим отчет для поиска конфигураций с отсутствующими компонентами
        configs_with_missing = defaultdict(list)
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
            
            if current_section == 'Несуществующие компоненты':
                match = re.search(r'\*\*Компонент:\*\*\s+`([^`]+)`', line)
                if match:
                    component = match.group(1)
                    configs_with_missing[current_config].append(component)
        
        print(f"Найдено конфигураций с проблемами: {len(configs_with_missing)}")
        
        # Обрабатываем все конфигурации (не только первые 5)
        for config_path, missing_comps in configs_with_missing.items():
            if self.fix_config(config_path, missing_comps):
                self.fixes_applied.append(config_path)
        
        print(f"\nИсправлено конфигураций: {len(self.fixes_applied)}")

if __name__ == "__main__":
    fixer = ComponentClassFixer()
    fixer.run()
