#!/bin/bash

# Скрипт для исправления проблемы Qt Creator с CMake конфигурацией
echo "🔧 Исправление проблемы Qt Creator с CMake конфигурацией..."

# Очищаем все старые конфигурации
echo "🧹 Очистка старых конфигураций..."
rm -rf .qtc
rm -rf build
rm -rf build-*

# Создаем новую конфигурацию с явным указанием типа сборки
echo "📦 Создание новой конфигурации..."
cmake -B build -S . -DCMAKE_BUILD_TYPE=Debug -DCMAKE_CXX_STANDARD=20

# Проверяем, что конфигурация создалась
if [ -f "build/CMakeCache.txt" ]; then
    echo "✅ Конфигурация создана успешно!"
    
    # Создаем файл настроек Qt Creator
    mkdir -p .qtc
    cat > .qtc/qtcreator.ini << EOF
[General]
# Qt Creator settings for NMSDK project

[CMake]
# CMake configuration
CMAKE_BUILD_TYPE=Debug
CMAKE_CXX_STANDARD=20
CMAKE_CXX_STANDARD_REQUIRED=ON
CMAKE_CXX_EXTENSIONS=OFF

# Build configurations
Debug=Debug
Release=Release
MinSizeRel=MinSizeRel
RelWithDebInfo=RelWithDebInfo

[Qt]
# Qt version
QtVersion=5.15.2

[Build]
# Build configuration
BuildConfiguration=Debug
EOF

    echo "✅ Файл настроек Qt Creator создан!"
    
else
    echo "❌ Ошибка создания конфигурации!"
    exit 1
fi

echo ""
echo "📋 Инструкции для Qt Creator:"
echo "1. Закройте Qt Creator (если открыт)"
echo "2. Откройте Qt Creator"
echo "3. File → Open File or Project"
echo "4. Выберите /home/user/Nmsdk/CMakeLists.txt"
echo "5. В окне 'Configure Project':"
echo "   - Build type: Debug"
echo "   - CMake executable: оставьте по умолчанию"
echo "   - CMake arguments: -DCMAKE_BUILD_TYPE=Debug"
echo "6. Нажмите 'Configure Project'"
echo ""
echo "🔧 Если проблема сохраняется:"
echo "- Убедитесь, что Qt Creator использует правильную версию CMake"
echo "- Проверьте, что Qt Creator может найти компилятор C++"
echo "- Попробуйте перезапустить Qt Creator"




