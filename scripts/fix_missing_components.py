#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для автоматического анализа и исправления проблем с отсутствующими компонентами
в конфигурациях проекта Nmsdk.

Анализирует отчет валидации и предлагает исправления для конфигураций с ошибками.
"""

import os
import sys
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

# Добавляем путь к скриптам
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class ConfigFixer:
    """Класс для исправления конфигураций с отсутствующими компонентами"""
    
    def __init__(self, configs_dir: str = "Bin/Configs", reports_dir: str = "Reports"):
        self.configs_dir = Path(configs_dir)
        self.reports_dir = Path(reports_dir)
        self.validation_report = self.reports_dir / "ConfigValidation-Detailed-Report.md"
        
        # Маппинг проблемных компонентов на их типы и параметры
        self.component_fixes = {
            'LTZone': {
                'type': 'LTZone',
                'param': 'LTZoneClassName',
                'default_class': 'NPLTZone',
                'build_mode': [1, 2]
            },
            'Receptor': {
                'type': 'Receptor',
                'param': 'ReceptorClassName',
                'default_class': 'NReceptor',
                'build_mode': [1, 2]
            },
            'Soma1': {
                'type': 'Soma',
                'param': 'NumSomaMembraneParts',
                'default_value': 1,
                'build_mode': [1, 2]
            },
            'Soma2': {
                'type': 'Soma',
                'param': 'NumSomaMembraneParts',
                'default_value': 2,
                'build_mode': [1, 2]
            },
            'Dendrite1_1': {
                'type': 'Dendrite',
                'param': 'NumDendriteMembraneParts',
                'default_value': 1,
                'build_mode': [1, 2]
            },
            'Dendrite1_2': {
                'type': 'Dendrite',
                'param': 'NumDendriteMembraneParts',
                'default_value': 2,
                'build_mode': [1, 2]
            },
            'NegGenerator': {
                'type': 'Generator',
                'param': 'InhGeneratorClassName',
                'default_class': 'NPNeuronNegCGenerator',
                'build_mode': [1, 2]
            },
            'PosGenerator': {
                'type': 'Generator',
                'param': 'ExcGeneratorClassName',
                'default_class': 'NPNeuronPosCGenerator',
                'build_mode': [1, 2]
            },
            'LTMembrane': {
                'type': 'LTMembrane',
                'param': 'LTMembraneClassName',
                'default_class': 'NPMembrane',
                'build_mode': [1, 2]
            }
        }
        
    def parse_validation_report(self) -> Dict[str, Dict]:
        """Парсит отчет валидации и извлекает информацию об ошибках"""
        if not self.validation_report.exists():
            print(f"Отчет валидации не найден: {self.validation_report}")
            return {}
        
        configs_errors = {}
        current_config = None
        
        with open(self.validation_report, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Ищем начало описания конфигурации
            if line.startswith('### '):
                config_path = line[4:].strip()
                if config_path.endswith('/project.ini'):
                    current_config = config_path
                    configs_errors[current_config] = {
                        'missing_components': [],
                        'missing_classes': [],
                        'invalid_links': []
                    }
            
            # Ищем несуществующие компоненты
            if current_config and 'Несуществующие компоненты' in line:
                i += 1
                while i < len(lines) and not lines[i].startswith('####'):
                    comp_line = lines[i]
                    match = re.search(r'Компонент.*`(\w+)`.*не существует', comp_line)
                    if match:
                        component_name = match.group(1)
                        configs_errors[current_config]['missing_components'].append(component_name)
                    i += 1
                continue
            
            # Ищем несуществующие классы
            if current_config and 'Несуществующие классы компонентов' in line:
                i += 1
                while i < len(lines) and not lines[i].startswith('####'):
                    comp_line = lines[i]
                    match = re.search(r'Компонент.*`(\w+)`.*Класс.*`(\w+)`', comp_line)
                    if match:
                        component_name = match.group(1)
                        class_name = match.group(2)
                        configs_errors[current_config]['missing_classes'].append({
                            'component': component_name,
                            'class': class_name
                        })
                    i += 1
                continue
            
            i += 1
        
        return configs_errors
    
    def find_xml_files(self, config_path: str) -> Tuple[Optional[Path], Optional[Path]]:
        """Находит файлы Parameters и Model для конфигурации"""
        # Извлекаем путь к директории конфигурации
        if config_path.endswith('/project.ini'):
            config_dir = Path(config_path[:-11])  # Убираем '/project.ini'
        else:
            config_dir = Path(config_path)
        
        full_config_dir = self.configs_dir / config_dir
        
        parameters_file = None
        model_file = None
        
        # Ищем Parameters_00.xml или Parameters.xml
        for pattern in ['Parameters_00.xml', 'Parameters.xml', 'parameters.xml']:
            candidate = full_config_dir / pattern
            if candidate.exists():
                parameters_file = candidate
                break
        
        # Ищем Model_00.xml или model.xml
        for pattern in ['Model_00.xml', 'Model.xml', 'model.xml']:
            candidate = full_config_dir / pattern
            if candidate.exists():
                model_file = candidate
                break
        
        return parameters_file, model_file
    
    def fix_component_issues(self, config_path: str, errors: Dict) -> List[str]:
        """Исправляет проблемы с компонентами в конфигурации"""
        fixes_applied = []
        
        parameters_file, model_file = self.find_xml_files(config_path)
        
        if not parameters_file:
            return fixes_applied
        
        # Создаем резервную копию перед изменением
        backup_file = None
        try:
            backup_file = self._create_backup(parameters_file)
        except Exception as e:
            print(f"Предупреждение: не удалось создать резервную копию {parameters_file}: {e}")
            return fixes_applied  # Не продолжаем без резервной копии
        
        try:
            tree = ET.parse(parameters_file)
            root = tree.getroot()
            
            # В XML Nmsdk тег = имя экземпляра, а тип хранится в атрибуте Class.
            # Поэтому фильтруем именно по component.get("Class"), а не по component.tag.
            allowed_component_classes = {
                'NPulseNeuron',
                'NAfferentNeuron',
                'NSimpleAfferentNeuron',
                'NSAfferentNeuron',
                'NSPNeuronGen',
                'PHebbNeuron',
                'PNeuron',
            }

            for component in root.iter():
                component_class = component.get('Class', '')
                if component_class in allowed_component_classes:
                    component_instance = component.tag
                    
                    # Проверяем StructureBuildMode
                    structure_build_mode = None
                    params_elem = component.find('Parameters')
                    if params_elem is not None:
                        mode_param = params_elem.find('StructureBuildMode')
                        if mode_param is not None and mode_param.text is not None:
                            try:
                                structure_build_mode = int(mode_param.text)
                            except Exception:
                                structure_build_mode = None
                    
                    # Если StructureBuildMode == 0, но есть отсутствующие компоненты, нужно установить правильный режим
                    if structure_build_mode == 0:
                        # Проверяем, какие компоненты отсутствуют для этого типа
                        missing_for_this = self._get_missing_for_component_type(
                            component_class, errors.get('missing_components', [])
                        )
                        
                        if missing_for_this:
                            # Устанавливаем StructureBuildMode = 2 (простая структура) или 1 (классическая)
                            # Создаем элемент Parameters, если его нет
                            if params_elem is None:
                                params_elem = ET.SubElement(component, 'Parameters')
                                
                            if params_elem.find('StructureBuildMode') is None:
                                # Добавляем StructureBuildMode
                                mode_elem = ET.SubElement(params_elem, 'StructureBuildMode')
                                mode_elem.set('Type', 'i')
                                mode_elem.set('PType', '257')
                                mode_elem.set('IoType', '17')
                                mode_elem.text = '2'  # Простая структура
                                
                                fixes_applied.append(
                                    f"Установлен StructureBuildMode=2 для {component_instance} "
                                    f"(Class={component_class}, было 0, отсутствуют компоненты: {', '.join(missing_for_this)})"
                                )
                    
                    # Исправляем параметры для отсутствующих компонентов
                    # Используем component_class, который определен выше
                    for missing_comp in errors.get('missing_components', []):
                        if missing_comp in self.component_fixes:
                            fix_info = self.component_fixes[missing_comp]
                            
                            # Проверяем, нужен ли этот компонент для данного типа нейрона
                            if self._component_needed_for_type(component_class, missing_comp):
                                # Устанавливаем параметры
                                if params_elem is None:
                                    params_elem = ET.SubElement(component, 'Parameters')
                                
                                # Устанавливаем параметр, если его нет
                                param_elem = params_elem.find(fix_info['param'])
                                if param_elem is None:
                                    param_elem = ET.SubElement(params_elem, fix_info['param'])
                                    param_elem.set('Type', 'std::string' if 'ClassName' in fix_info['param'] else 'i')
                                    param_elem.set('PType', '257')
                                    if 'ClassName' in fix_info['param']:
                                        param_elem.text = fix_info.get('default_class', '')
                                    else:
                                        param_elem.text = str(fix_info.get('default_value', 1))
                                    
                                    fixes_applied.append(
                                        f"Установлен {fix_info['param']}={param_elem.text} "
                                        f"для {component_instance} (Class={component_class}, отсутствует компонент {missing_comp})"
                                    )
            
            # Сохраняем изменения только если есть исправления
            if fixes_applied:
                # Проверяем целостность перед сохранением
                elements_before = len(list(root.iter()))
                
                # Сохраняем без форматирования, чтобы сохранить комментарии
                tree.write(parameters_file, encoding='utf-8', xml_declaration=True)
                
                # Проверяем целостность после сохранения
                tree_check = ET.parse(parameters_file)
                elements_after = len(list(tree_check.getroot().iter()))
                
                if elements_after < elements_before * 0.95:  # Если потеряно более 5%
                    print(f"  ⚠️ ПРЕДУПРЕЖДЕНИЕ: Потеряно элементов при сохранении!")
                    print(f"     Было: {elements_before}, Стало: {elements_after}")
                    print(f"     Восстанавливаю из резервной копии...")
                    if backup_file and backup_file.exists():
                        import shutil
                        shutil.copy2(backup_file, parameters_file)
                        print(f"     ✅ Файл восстановлен из резервной копии")
                        fixes_applied = []  # Отменяем исправления
                else:
                    print(f"  Изменения сохранены в {parameters_file} (элементов: {elements_after})")
        
        except Exception as e:
            print(f"Ошибка при обработке {parameters_file}: {e}")
            # Восстанавливаем из резервной копии при ошибке
            if backup_file and backup_file.exists():
                try:
                    import shutil
                    shutil.copy2(backup_file, parameters_file)
                    print(f"  Файл восстановлен из резервной копии")
                except Exception as restore_error:
                    print(f"  КРИТИЧЕСКАЯ ОШИБКА: не удалось восстановить файл: {restore_error}")
            fixes_applied = []  # Очищаем список исправлений при ошибке
        
        finally:
            # Резервные копии НЕ удаляем автоматически:
            # они нужны для ручного отката и расследований.
            pass
        
        # Обрабатываем Model_*.xml, если он существует
        if model_file and model_file.exists():
            model_fixes = self.fix_model_issues(model_file, parameters_file, errors)
            fixes_applied.extend(model_fixes)
        
        return fixes_applied
    
    def _get_missing_for_component_type(self, component_class: str, missing_components: List[str]) -> List[str]:
        """Определяет, какие отсутствующие компоненты относятся к данному типу"""
        # Простая эвристика: компоненты Soma, Dendrite, LTZone, Generators относятся к NPulseNeuron
        # Receptor, LTZone относятся к NAfferentNeuron
        neuron_types = {
            'NPulseNeuron': ['Soma', 'Dendrite', 'LTZone', 'NegGenerator', 'PosGenerator', 'LTMembrane'],
            'NAfferentNeuron': ['Receptor', 'LTZone'],
            'NSimpleAfferentNeuron': ['Receptor', 'LTZone'],
            'NSAfferentNeuron': ['Receptor', 'LTZone'],
            'NSPNeuronGen': ['Soma', 'Dendrite', 'LTZone', 'NegGenerator', 'PosGenerator'],
            'PHebbNeuron': ['Soma', 'Dendrite', 'LTZone', 'NegGenerator', 'PosGenerator', 'LTMembrane'],
            'PNeuron': ['Soma', 'Dendrite', 'LTZone', 'NegGenerator', 'PosGenerator', 'LTMembrane']
        }
        
        relevant = []
        for missing in missing_components:
            for comp_type in neuron_types.get(component_class, []):
                if comp_type in missing or missing.startswith(comp_type):
                    relevant.append(missing)
                    break
        
        return relevant
    
    def _component_needed_for_type(self, component_class: str, component_name: str) -> bool:
        """Проверяет, нужен ли компонент для данного типа нейрона"""
        neuron_components = {
            'NPulseNeuron': ['Soma', 'Dendrite', 'LTZone', 'NegGenerator', 'PosGenerator', 'LTMembrane'],
            'NAfferentNeuron': ['Receptor', 'LTZone'],
            'NSimpleAfferentNeuron': ['Receptor', 'LTZone'],
            'NSAfferentNeuron': ['Receptor', 'LTZone'],
            'NSPNeuronGen': ['Soma', 'Dendrite', 'LTZone', 'NegGenerator', 'PosGenerator'],
            'PHebbNeuron': ['Soma', 'Dendrite', 'LTZone', 'NegGenerator', 'PosGenerator', 'LTMembrane'],
            'PNeuron': ['Soma', 'Dendrite', 'LTZone', 'NegGenerator', 'PosGenerator', 'LTMembrane']
        }
        
        for comp_type in neuron_components.get(component_class, []):
            if comp_type in component_name or component_name.startswith(comp_type):
                return True
        
        return False
    
    def _extract_components_from_parameters(self, parameters_file: Path) -> Dict[str, Dict]:
        """Извлекает список всех компонентов из Parameters_*.xml с их классами и путями"""
        components_map = {}  # component_name -> {'class': ..., 'parent_paths': [...]}
        
        try:
            tree = ET.parse(parameters_file)
            root = tree.getroot()
            
            def extract_recursive(elem, parent_path: List[str]):
                """Рекурсивно извлекает компоненты с их путями к родительским контейнерам"""
                # Пропускаем служебные элементы на верхнем уровне
                if elem.tag in ['SaveProperties', 'Model']:
                    for child in elem:
                        extract_recursive(child, parent_path)
                    return
                
                # Если это Components, обрабатываем дочерние компоненты
                if elem.tag == 'Components':
                    for child in elem:
                        extract_recursive(child, parent_path)
                    return
                
                # Если это Parameters, пропускаем (не компонент)
                if elem.tag == 'Parameters':
                    return
                
                # Если это компонент (имеет атрибут Class)
                component_class = elem.get('Class', '')
                if component_class:
                    component_name = elem.tag
                    
                    # Сохраняем компонент с путем к родительскому контейнеру
                    if component_name not in components_map:
                        components_map[component_name] = {
                            'class': component_class,
                            'parent_paths': []
                        }
                    # Сохраняем путь к родительскому Components (без самого компонента)
                    components_map[component_name]['parent_paths'].append(parent_path.copy())
                
                # Рекурсивно обрабатываем дочерние элементы (включая вложенные Components)
                for child in elem:
                    if child.tag == 'Components':
                        # Если дочерний элемент - Components, обновляем путь, добавляя текущий компонент
                        extract_recursive(child, parent_path + [elem.tag])
                    else:
                        # Для других элементов передаем текущий путь
                        extract_recursive(child, parent_path)
            
            # Начинаем с корневого Model
            model_elem = root.find('Model')
            if model_elem is not None:
                model_components = model_elem.find('Components')
                if model_components is not None:
                    extract_recursive(model_components, [])
            
        except Exception as e:
            print(f"  Предупреждение: не удалось извлечь компоненты из {parameters_file}: {e}")
            import traceback
            traceback.print_exc()
        
        return components_map
    
    def _find_component_in_model(self, model_root, component_name: str, parent_path: List[str] = None) -> Optional[ET.Element]:
        """Находит компонент в Model по имени и пути"""
        if parent_path is None:
            parent_path = []
        
        # Ищем в корневом Components
        model_components = model_root.find('Components')
        if model_components is None:
            return None
        
        # Если путь пустой, ищем напрямую в корневом Components
        if not parent_path:
            for comp in model_components:
                if comp.tag == component_name:
                    return comp
            return None
        
        # Ищем по пути (например, Model.Components.Neuron1.Components.Dendrite1_1)
        current = model_components
        for path_elem in parent_path:
            found = None
            for child in current:
                if child.tag == path_elem:
                    found = child
                    break
            if found is None:
                return None
            # Переходим к Components следующего уровня
            current = found.find('Components')
            if current is None:
                return None
        
        # Ищем компонент в текущем уровне
        for comp in current:
            if comp.tag == component_name:
                return comp
        
        return None
    
    def fix_model_issues(self, model_file: Path, parameters_file: Path, errors: Dict) -> List[str]:
        """Исправляет проблемы с компонентами в Model_*.xml, добавляя недостающие компоненты из Parameters_*.xml"""
        fixes_applied = []
        
        if not parameters_file.exists():
            return fixes_applied
        
        # Создаем резервную копию Model перед изменением
        backup_file = None
        try:
            backup_file = self._create_backup(model_file)
        except Exception as e:
            print(f"  Предупреждение: не удалось создать резервную копию {model_file}: {e}")
            return fixes_applied
        
        try:
            # Парсим Model
            model_tree = ET.parse(model_file)
            model_root = model_tree.getroot()
            
            # Извлекаем компоненты из Parameters
            params_components = self._extract_components_from_parameters(parameters_file)
            
            # Подсчитываем элементы до изменений
            elements_before = len(list(model_root.iter()))
            
            # Находим корневой Components в Model
            model_components_elem = model_root.find('Components')
            if model_components_elem is None:
                # Если Components нет, создаем его
                model_components_elem = ET.SubElement(model_root, 'Components')
            
            # Создаем карту существующих компонентов в Model для быстрого поиска
            # Ключ: (component_name, parent_path_str) -> element
            existing_components = {}
            
            def map_existing_recursive(elem, parent_path: List[str]):
                """Рекурсивно создает карту существующих компонентов"""
                if elem.tag == 'Components':
                    for child in elem:
                        component_name = child.tag
                        component_class = child.get('Class', '')
                        if component_class:  # Только компоненты с Class
                            parent_path_str = '.'.join(parent_path) if parent_path else 'root'
                            key = (component_name, parent_path_str)
                            existing_components[key] = child
                            # Рекурсивно обрабатываем вложенные Components
                            child_components = child.find('Components')
                            if child_components is not None:
                                map_existing_recursive(child_components, parent_path + [component_name])
            
            map_existing_recursive(model_components_elem, [])
            
            # Добавляем недостающие компоненты из Parameters в Model
            for comp_name, comp_info in params_components.items():
                comp_class = comp_info['class']
                
                # Пропускаем служебные элементы
                if comp_name in ['SaveProperties', 'Model', 'Parameters', 'Components', 'Links']:
                    continue
                
                if not comp_class:
                    continue  # Пропускаем элементы без класса
                
                # Проверяем, есть ли компонент в Model
                found_in_model = False
                for parent_path in comp_info['parent_paths']:
                    parent_path_str = '.'.join(parent_path) if parent_path else 'root'
                    key = (comp_name, parent_path_str)
                    if key in existing_components:
                        found_in_model = True
                        break
                
                # Если компонент не найден в Model, добавляем его
                if not found_in_model:
                    # Определяем родительский контейнер для добавления
                    parent_elem = model_components_elem
                    
                    # Если есть информация о родительском пути, пытаемся найти родителя
                    if comp_info['parent_paths']:
                        parent_path = comp_info['parent_paths'][0]  # Используем первый путь
                        
                        # Ищем родительский компонент по пути
                        current = model_components_elem
                        for parent_name in parent_path:
                            found_parent = None
                            for child in current:
                                if child.tag == parent_name:
                                    found_parent = child
                                    break
                            if found_parent is None:
                                # Родитель не найден, добавляем в корневой Components
                                break
                            # Переходим к Components родителя
                            parent_components = found_parent.find('Components')
                            if parent_components is None:
                                # Создаем Components для родителя, если его нет
                                parent_components = ET.SubElement(found_parent, 'Components')
                            current = parent_components
                            parent_elem = current
                    
                    # Проверяем, что компонент еще не существует в этом контейнере
                    already_exists = False
                    for child in parent_elem:
                        if child.tag == comp_name and child.get('Class', '') == comp_class:
                            already_exists = True
                            break
                    
                    if not already_exists:
                        # Создаем компонент
                        new_comp = ET.SubElement(parent_elem, comp_name)
                        new_comp.set('Class', comp_class)
                        
                        # Добавляем минимальную структуру
                        ET.SubElement(new_comp, 'Parameters')
                        ET.SubElement(new_comp, 'Components')
                        
                        parent_desc = '.'.join(comp_info['parent_paths'][0]) if comp_info['parent_paths'] else 'root'
                        fixes_applied.append(
                            f"Создан компонент {comp_name} в {model_file.name} "
                            f"(Class={comp_class}, parent={parent_desc}, отсутствовал в Model)"
                        )
            
            # Сохраняем изменения только если есть исправления
            if fixes_applied:
                # Проверяем целостность перед сохранением
                elements_before_save = len(list(model_root.iter()))
                
                # Сохраняем без форматирования
                model_tree.write(model_file, encoding='utf-8', xml_declaration=True)
                
                # Проверяем целостность после сохранения
                model_check_tree = ET.parse(model_file)
                elements_after = len(list(model_check_tree.getroot().iter()))
                
                if elements_after < elements_before_save * 0.95:  # Если потеряно более 5%
                    print(f"  ⚠️ ПРЕДУПРЕЖДЕНИЕ: Потеряно элементов при сохранении Model!")
                    print(f"     Было: {elements_before_save}, Стало: {elements_after}")
                    print(f"     Восстанавливаю из резервной копии...")
                    if backup_file and backup_file.exists():
                        import shutil
                        shutil.copy2(backup_file, model_file)
                        print(f"     ✅ Файл Model восстановлен из резервной копии")
                        fixes_applied = []  # Отменяем исправления
                else:
                    print(f"  Изменения сохранены в {model_file} (элементов: {elements_after})")
        
        except Exception as e:
            print(f"  Ошибка при обработке {model_file}: {e}")
            import traceback
            traceback.print_exc()
            # Восстанавливаем из резервной копии при ошибке
            if backup_file and backup_file.exists():
                try:
                    import shutil
                    shutil.copy2(backup_file, model_file)
                    print(f"  Файл Model восстановлен из резервной копии")
                except Exception as restore_error:
                    print(f"  КРИТИЧЕСКАЯ ОШИБКА: не удалось восстановить Model: {restore_error}")
            fixes_applied = []  # Очищаем список исправлений при ошибке
        
        finally:
            # Резервные копии НЕ удаляем автоматически
            pass
        
        return fixes_applied
    
    def _create_backup(self, file_path: Path) -> Path:
        """Создает резервную копию файла перед изменением"""
        from datetime import datetime
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = file_path.with_suffix(file_path.suffix + f'.backup.{stamp}')
        import shutil
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def generate_fix_report(self, fixes: Dict[str, List[str]]) -> str:
        """Генерирует отчет об исправлениях"""
        report = "# Отчет об исправлениях конфигураций\n\n"
        report += f"**Дата создания:** {self._get_current_date()}\n\n"
        
        total_fixed = sum(len(f) for f in fixes.values())
        report += f"**Всего исправлено конфигураций:** {len(fixes)}\n"
        report += f"**Всего применено исправлений:** {total_fixed}\n\n"
        
        report += "## Детали исправлений\n\n"
        
        for config_path, config_fixes in sorted(fixes.items()):
            if config_fixes:
                report += f"### {config_path}\n\n"
                for fix in config_fixes:
                    report += f"- {fix}\n"
                report += "\n"
        
        return report
    
    def _get_current_date(self) -> str:
        """Возвращает текущую дату в формате DD.MM.YYYY HH:MM"""
        from datetime import datetime
        return datetime.now().strftime("%d.%m.%Y %H:%M")
    
    def run(self, dry_run: bool = False) -> Dict[str, List[str]]:
        """Запускает процесс исправления конфигураций"""
        print("Анализ отчета валидации...")
        configs_errors = self.parse_validation_report()
        
        if not configs_errors:
            print("Не найдено конфигураций с ошибками в отчете валидации.")
            return {}
        
        print(f"Найдено {len(configs_errors)} конфигураций с ошибками.")
        
        fixes_applied = {}
        
        for config_path, errors in configs_errors.items():
            if errors.get('missing_components') or errors.get('missing_classes'):
                print(f"\nОбработка: {config_path}")
                
                if not dry_run:
                    fixes = self.fix_component_issues(config_path, errors)
                    if fixes:
                        fixes_applied[config_path] = fixes
                        print(f"  Применено исправлений: {len(fixes)}")
                else:
                    # В режиме dry-run просто показываем, что будет исправлено
                    print(f"  Будет исправлено: {len(errors.get('missing_components', []))} отсутствующих компонентов")
        
        if not dry_run and fixes_applied:
            # Сохраняем отчет об исправлениях
            report = self.generate_fix_report(fixes_applied)
            report_file = self.reports_dir / "ConfigFixes-Report.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\nОтчет об исправлениях сохранен: {report_file}")
        
        return fixes_applied


def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Исправление проблем с отсутствующими компонентами в конфигурациях'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Режим проверки без применения изменений'
    )
    parser.add_argument(
        '--configs-dir',
        default='Bin/Configs',
        help='Директория с конфигурациями (по умолчанию: Bin/Configs)'
    )
    parser.add_argument(
        '--reports-dir',
        default='Reports',
        help='Директория с отчетами (по умолчанию: Reports)'
    )
    
    args = parser.parse_args()
    
    fixer = ConfigFixer(
        configs_dir=args.configs_dir,
        reports_dir=args.reports_dir
    )
    
    fixes = fixer.run(dry_run=args.dry_run)
    
    if args.dry_run:
        print("\nРежим проверки завершен. Используйте без --dry-run для применения исправлений.")
    else:
        print(f"\nИсправления применены для {len(fixes)} конфигураций.")


if __name__ == '__main__':
    main()
