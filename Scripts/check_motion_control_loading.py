#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для диагностики загрузки NMotionControlLibrary.

Проверяет:
1. Определены ли макросы NMSDK_DEBUG и NO_MOTION_CONTROL
2. Загружается ли библиотека при запуске
3. Доступны ли классы из библиотеки
"""

import subprocess
import sys
import tempfile
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import re

def check_binary_macros():
    """Проверяет макросы в скомпилированном бинарнике"""
    console_exe = Path("Bin/Platform/Linux/NeuroModelerConsole")
    
    if not console_exe.exists():
        print(f"❌ NeuroModelerConsole не найден: {console_exe}")
        return False
    
    try:
        result = subprocess.run(
            ["strings", str(console_exe)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = result.stdout
        
        has_nmsdk_debug = "NMSDK_DEBUG" in output
        has_no_motion_control = "NO_MOTION_CONTROL" in output
        has_motion_control = "MotionControl" in output or "MotionControlLibrary" in output
        
        print("=" * 80)
        print("Проверка макросов в бинарнике:")
        print("=" * 80)
        print(f"NMSDK_DEBUG найден в бинарнике: {has_nmsdk_debug}")
        print(f"NO_MOTION_CONTROL найден в бинарнике: {has_no_motion_control}")
        print(f"MotionControlLibrary упоминается: {has_motion_control}")
        
        return {
            'nmsdk_debug': has_nmsdk_debug,
            'no_motion_control': has_no_motion_control,
            'motion_control_present': has_motion_control
        }
    except Exception as e:
        print(f"❌ Ошибка при проверке бинарника: {e}")
        return None

def check_cmake_config():
    """Проверяет конфигурацию CMake"""
    print("\n" + "=" * 80)
    print("Проверка конфигурации CMake:")
    print("=" * 80)
    
    # Проверяем главный CMakeLists.txt
    cmake_main = Path("CMakeLists.txt")
    if cmake_main.exists():
        content = cmake_main.read_text(encoding='utf-8', errors='ignore')
        has_nmsdk_debug = 'NMSDK_DEBUG' in content
        has_no_motion_control = 'NO_MOTION_CONTROL' in content
        
        print(f"CMakeLists.txt содержит NMSDK_DEBUG: {has_nmsdk_debug}")
        print(f"CMakeLists.txt содержит NO_MOTION_CONTROL: {has_no_motion_control}")
    
    # Проверяем CMake кэш
    cmake_cache = Path("build/CMakeCache.txt")
    if cmake_cache.exists():
        content = cmake_cache.read_text(encoding='utf-8', errors='ignore')
        
        compile_defs = []
        for line in content.split('\n'):
            if 'CMAKE_CXX_FLAGS' in line or 'COMPILE_DEFINITIONS' in line:
                if 'NMSDK_DEBUG' in line or 'NO_MOTION_CONTROL' in line:
                    compile_defs.append(line.strip())
        
        if compile_defs:
            print("\nНайдены определения в CMake кэше:")
            for d in compile_defs[:5]:
                print(f"  {d}")
        else:
            print("\nОпределения NMSDK_DEBUG и NO_MOTION_CONTROL не найдены в CMake кэше")
    else:
        print("CMake кэш не найден (build/CMakeCache.txt)")

def test_class_loading():
    """Тестирует загрузку классов через валидацию"""
    print("\n" + "=" * 80)
    print("Тест загрузки классов MotionControlLibrary:")
    print("=" * 80)
    
    # Создаем тестовый проект с компонентом из MotionControlLibrary
    temp_dir = tempfile.mkdtemp(prefix="nmsdk_motion_test_")
    project_dir = Path(temp_dir)
    
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
    <Components>
      <DCEngine Class="NDCEngine" X="10" Y="10"/>
    </Components>
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
    
    (project_dir / "project.ini").write_text(project_content, encoding='utf-8')
    (project_dir / "Model_00.xml").write_text(model_content, encoding='utf-8')
    (project_dir / "Parameters_00.xml").write_text(params_content, encoding='utf-8')
    (project_dir / "States_00.xml").write_text(states_content, encoding='utf-8')
    
    console_exe = Path("Bin/Platform/Linux/NeuroModelerConsole")
    
    if not console_exe.exists():
        print("❌ NeuroModelerConsole не найден")
        return
    
    try:
        result = subprocess.run(
            [str(console_exe), "--check-config", str(project_dir / "project.ini")],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout + result.stderr
        
        # Проверяем, есть ли ошибка о несуществующем классе
        if "NDCEngine" in output and ("does not exist" in output or "не существует" in output):
            print("❌ Класс NDCEngine не найден - библиотека НЕ загружается")
        elif "NDCEngine" in output:
            print("✅ Класс NDCEngine найден - библиотека загружается")
        else:
            print("⚠️  Не удалось определить статус класса NDCEngine")
        
        # Сохраняем вывод для анализа
        output_file = Path("Reports/MotionControl-Loading-Test.txt")
        output_file.parent.mkdir(exist_ok=True)
        output_file.write_text(output, encoding='utf-8')
        print(f"\nПолный вывод сохранен в: {output_file}")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
    finally:
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

def check_libraries_cpp():
    """Проверяет код загрузки библиотек"""
    print("\n" + "=" * 80)
    print("Проверка кода загрузки библиотек:")
    print("=" * 80)
    
    libs_cpp = Path("Libraries/Libraries.cpp")
    if libs_cpp.exists():
        content = libs_cpp.read_text(encoding='utf-8', errors='ignore')
        
        # Ищем условие загрузки
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'MotionControlLibrary' in line:
                print(f"Строка {i+1}: {line.strip()}")
                # Показываем контекст
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    marker = ">>>" if j == i else "   "
                    print(f"{marker} {j+1:4d}: {lines[j].rstrip()}")

def main():
    """Основная функция"""
    print("=" * 80)
    print("Диагностика загрузки NMotionControlLibrary")
    print("=" * 80)
    
    # 1. Проверка макросов в бинарнике
    binary_info = check_binary_macros()
    
    # 2. Проверка конфигурации CMake
    check_cmake_config()
    
    # 3. Проверка кода загрузки
    check_libraries_cpp()
    
    # 4. Тест загрузки классов
    test_class_loading()
    
    # Выводы
    print("\n" + "=" * 80)
    print("ВЫВОДЫ:")
    print("=" * 80)
    
    if binary_info:
        if binary_info['nmsdk_debug']:
            print("⚠️  NMSDK_DEBUG определен - библиотека НЕ загружается")
        elif binary_info['no_motion_control']:
            print("⚠️  NO_MOTION_CONTROL определен - библиотека НЕ загружается")
        elif not binary_info['motion_control_present']:
            print("⚠️  MotionControlLibrary не найден в бинарнике - библиотека НЕ загружается")
        else:
            print("✅ Макросы не определены, библиотека должна загружаться")
    
    print("\nРекомендации:")
    print("1. Проверить CMakeLists.txt на наличие определений NMSDK_DEBUG или NO_MOTION_CONTROL")
    print("2. Убедиться, что библиотека компилируется и линкуется")
    print("3. Проверить порядок загрузки библиотек в RdkLoadPredefinedLibraries()")

if __name__ == "__main__":
    main()
