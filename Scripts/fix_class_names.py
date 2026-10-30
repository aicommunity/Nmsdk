#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления неправильных имен классов в Model_*.xml.

Исправляет классы без префикса "N" или с неправильными именами на правильные.
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import re
from collections import defaultdict

# Маппинг неправильных имен на правильные
CLASS_NAME_MAPPING = {
    'DCEngine': 'NDCEngine',
    'DCEngine2': 'NDCEngine',
    'EyeRetina': 'NEyeRetina',
    'NeuronTrainer': 'NNeuronTrainer',
    'SpikeClassifier': 'NSpikeClassifier',
    'ConditionedReflex': 'NConditionedReflex',
    'EngineMotionControl': 'NEngineMotionControl',
    'EngineMotionControl2': 'NEngineMotionControl',
    'NMultiPositionControl2': 'NMultiPositionControl',
    'NMultiPositionControl3': 'NMultiPositionControl',
    'NMultiPositionControl4': 'NMultiPositionControl',
    'NMultiPositionControl5': 'NMultiPositionControl',
    'NMultiPositionControl6': 'NMultiPositionControl',
    'NMultiPositionControl7': 'NMultiPositionControl',
    'NTrajectoryElement2': 'NTrajectoryElement',
    'NTrajectoryElement3': 'NTrajectoryElement',
    'NNewPositionControlElement2': 'NNewPositionControlElement',
}

class ClassNameFixer:
    """Исправляет неправильные имена классов в Model_*.xml"""
    
    def __init__(self, configs_dir: str = "Bin/Configs", reports_dir: str = "Reports"):
        self.configs_dir = Path(configs_dir)
        self.reports_dir = Path(reports_dir)
        self.validation_report = self.reports_dir / "ConfigValidation-Detailed-Report.md"
        self.fixes_applied = []
        self.class_fixes = defaultdict(int)
        
    def find_configs_with_wrong_classes(self) -> list:
        """Находит конфигурации с неправильными именами классов"""
        if not self.validation_report.exists():
            print(f"Отчет валидации не найден: {self.validation_report}")
            return []
        
        content = self.validation_report.read_text(encoding='utf-8')
        problematic_configs = defaultdict(set)
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
            
            if current_section == 'Несуществующие классы компонентов' and current_config:
                # Ищем строки вида: **Класс:** `ClassName` (не существует)
                match = re.search(r'\*\*Класс:\*\*\s+`([^`]+)`', line)
                if match:
                    class_name = match.group(1)
                    if class_name in CLASS_NAME_MAPPING:
                        problematic_configs[current_config].add(class_name)
        
        return list(problematic_configs.keys())
    
    def fix_class_names_in_model(self, model_file: Path) -> bool:
        """Исправляет имена классов в Model_*.xml"""
        modified = False
        
        try:
            if not model_file.exists():
                return False
            
            tree = ET.parse(model_file)
            root = tree.getroot()
            model = root.find("Model")
            if model is None:
                return False
            
            components = model.find("Components")
            if components is None:
                return False
            
            # Рекурсивно исправляем классы во всех компонентах
            def fix_component_class(elem):
                nonlocal modified
                class_attr = elem.get("Class", "")
                if class_attr and class_attr in CLASS_NAME_MAPPING:
                    correct_class = CLASS_NAME_MAPPING[class_attr]
                    elem.set("Class", correct_class)
                    self.class_fixes[class_attr] += 1
                    modified = True
                    print(f"    ✅ Исправлен класс: {class_attr} → {correct_class}")
                
                # Рекурсивно обрабатываем дочерние компоненты
                for child in elem:
                    fix_component_class(child)
            
            for component in components:
                fix_component_class(component)
            
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
            
            # Исправляем классы в Model
            return self.fix_class_names_in_model(model_file)
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            return False
    
    def run(self):
        """Запускает исправление всех проблемных конфигураций"""
        print("Поиск конфигураций с неправильными именами классов...")
        problematic_configs = self.find_configs_with_wrong_classes()
        
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
        
        if self.class_fixes:
            print(f"\nИсправленные классы:")
            for wrong_class, count in sorted(self.class_fixes.items(), key=lambda x: x[1], reverse=True):
                correct_class = CLASS_NAME_MAPPING[wrong_class]
                print(f"  {wrong_class} → {correct_class}: {count} раз(а)")
        
        if self.fixes_applied:
            print(f"\nИсправленные конфигурации:")
            for config in self.fixes_applied[:10]:
                print(f"  - {config}")
            if len(self.fixes_applied) > 10:
                print(f"  ... и еще {len(self.fixes_applied) - 10} конфигураций")

if __name__ == "__main__":
    fixer = ClassNameFixer()
    fixer.run()
