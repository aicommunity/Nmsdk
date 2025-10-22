#!/bin/bash

# Скрипт для настройки проекта NMSDK для Qt Creator
# Этот скрипт решает проблемы с конфигурацией CMake

echo "🔧 Настройка проекта NMSDK для Qt Creator..."

# Создаем директории сборки
mkdir -p build-debug
mkdir -p build-release

# Очищаем старые конфигурации
rm -rf build
rm -rf build-debug
rm -rf build-release

# Создаем новые конфигурации
echo "📦 Создание Debug конфигурации..."
cmake -B build-debug -S . -DCMAKE_BUILD_TYPE=Debug

echo "📦 Создание Release конфигурации..."
cmake -B build-release -S . -DCMAKE_BUILD_TYPE=Release

# Создаем симлинк для совместимости
ln -sf build-debug build

echo "✅ Проект настроен для Qt Creator!"
echo ""
echo "📋 Инструкции для Qt Creator:"
echo "1. Откройте /home/user/Nmsdk/CMakeLists.txt в Qt Creator"
echo "2. Выберите конфигурацию 'Debug' или 'Release'"
echo "3. Убедитесь, что Build type соответствует выбранной конфигурации"
echo ""
echo "🔧 Если проблема сохраняется:"
echo "- Удалите папку .qtc в корне проекта"
echo "- Перезапустите Qt Creator"
echo "- Откройте проект заново"




