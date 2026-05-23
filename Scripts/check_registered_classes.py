#!/usr/bin/env python3
"""
Диагностический скрипт для проверки зарегистрированных классов в Storage.

Скрипт запускает NeuroModelerConsole с тестовым проектом и проверяет,
какие классы зарегистрированы в Storage после инициализации.
"""

import subprocess
import sys
import tempfile
import os
from pathlib import Path
import xml.etree.ElementTree as ET

# Список проблемных классов из анализа
PROBLEMATIC_CLASSES = [
    # Из NPulseLibrary
    "NConditionedReflex",
    "NNeuronTrainer",
    "NSpikeClassifier",
    "NStatePredictor",
    # Из NMotionControlLibrary
    "NDCEngine",
    "NEyeRetina",
    "NManipulatorInput",
    "NIntervalSeparator",
    "NManipulatorSource",
    "NEngineMotionControl",
    "NNewMotionElement",
    "NNewPositionControlElement",
    "NMultiPositionControl",
    "NTrajectoryElement",
    "NMazeMemory",
    "NMazeMemorySimplified",
]

def create_test_project():
    """Создает минимальный тестовый project.ini для проверки классов."""
    project_content = """<?xml version="1.0" encoding="UTF-8"?>
<Save>
  <General>
    <ProjectDescriptionFileName>Description.rtf</ProjectDescriptionFileName>
    <InterfaceFileName>Interface.xml</InterfaceFileName>
  </General>
  <Channels>
    <Channel>
      <ModelFileName>Model_00.xml</ModelFileName>
      <ParametersFileName>Parameters_00.xml</ParametersFileName>
      <StatesFileName>States_00.xml</StatesFileName>
    </Channel>
  </Channels>
</Save>
"""
    
    model_content = """<?xml version="1.0" encoding="UTF-8"?>
<Save>
  <Model>
    <Components/>
    <Links/>
  </Model>
</Save>
"""
    
    params_content = """<?xml version="1.0" encoding="UTF-8"?>
<Save>
  <Parameters>
  </Parameters>
</Save>
"""
    
    states_content = """<?xml version="1.0" encoding="UTF-8"?>
<Save>
  <States>
  </States>
</Save>
"""
    
    # Создаем временную директорию
    temp_dir = tempfile.mkdtemp(prefix="nmsdk_class_check_")
    project_dir = Path(temp_dir)
    
    # Создаем файлы
    (project_dir / "project.ini").write_text(project_content, encoding='utf-8')
    (project_dir / "Model_00.xml").write_text(model_content, encoding='utf-8')
    (project_dir / "Parameters_00.xml").write_text(params_content, encoding='utf-8')
    (project_dir / "States_00.xml").write_text(states_content, encoding='utf-8')
    
    return project_dir / "project.ini", temp_dir

def check_classes_via_validation(project_ini_path):
    """Проверяет классы через валидацию проекта."""
    nmsdk_root = Path(__file__).parent.parent
    console_exe = nmsdk_root / "Bin" / "Platform" / "Linux" / "NeuroModelerConsole"
    
    if not console_exe.exists():
        # Пробуем другие возможные пути
        possible_paths = [
            nmsdk_root / "Bin" / "Win" / "NeuroModelerConsole.exe",
            nmsdk_root / "Bin" / "NeuroModelerConsole",
            nmsdk_root / "build" / "NeuroModelerConsole",
        ]
        for path in possible_paths:
            if path.exists():
                console_exe = path
                break
        else:
            print(f"❌ NeuroModelerConsole не найден. Ожидался в: {console_exe}")
            return None
    
    try:
        # Запускаем валидацию
        result = subprocess.run(
            [str(console_exe), "--check-config", str(project_ini_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        print("❌ Валидация превысила время ожидания")
        return None
    except Exception as e:
        print(f"❌ Ошибка при запуске валидации: {e}")
        return None

def parse_validation_output(output):
    """Парсит вывод валидации и извлекает информацию о классах."""
    if not output:
        return {}
    
    class_info = {}
    
    # Ищем ошибки о несуществующих классах
    import re
    pattern = r"Class\s+['\"]([^'\"]+)['\"]\s+does not exist"
    matches = re.findall(pattern, output, re.IGNORECASE)
    
    for class_name in matches:
        if class_name not in class_info:
            class_info[class_name] = {"status": "not_found", "errors": []}
        class_info[class_name]["errors"].append("Class does not exist")
    
    return class_info

def main():
    """Основная функция."""
    print("=" * 80)
    print("Проверка зарегистрированных классов в Storage")
    print("=" * 80)
    
    # Создаем тестовый проект
    print("\n1. Создание тестового проекта...")
    project_ini, temp_dir = create_test_project()
    print(f"   ✅ Создан: {project_ini}")
    
    try:
        # Запускаем валидацию
        print("\n2. Запуск валидации...")
        output = check_classes_via_validation(project_ini)
        
        if not output:
            print("   ❌ Не удалось получить вывод валидации")
            return 1
        
        # Парсим результаты
        print("\n3. Анализ результатов...")
        class_info = parse_validation_output(output)
        
        # Проверяем проблемные классы
        print("\n" + "=" * 80)
        print("Результаты проверки проблемных классов:")
        print("=" * 80)
        
        found_count = 0
        not_found_count = 0
        
        for class_name in PROBLEMATIC_CLASSES:
            if class_name in class_info:
                status = "❌ НЕ НАЙДЕН"
                not_found_count += 1
            else:
                status = "✅ НАЙДЕН (нет ошибок)"
                found_count += 1
            
            print(f"{status:30s} {class_name}")
        
        print("\n" + "=" * 80)
        print(f"Итого:")
        print(f"  Найдено: {found_count}/{len(PROBLEMATIC_CLASSES)}")
        print(f"  Не найдено: {not_found_count}/{len(PROBLEMATIC_CLASSES)}")
        print("=" * 80)
        
        # Сохраняем полный вывод для анализа
        output_file = Path("Reports/ClassCheck-Output.txt")
        output_file.parent.mkdir(exist_ok=True)
        output_file.write_text(output, encoding='utf-8')
        print(f"\nПолный вывод валидации сохранен в: {output_file}")
        
        return 0 if not_found_count == 0 else 1
        
    finally:
        # Удаляем временную директорию
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

if __name__ == "__main__":
    sys.exit(main())
