#!/bin/bash
# Скрипт для автоматической проверки отладочных сообщений в логах

set -e

PROJECT_INI="Bin/Configs/a.demcheva/12_MazeMemory_HandmadeExperiment/project.ini"
CONSOLE_EXE="Bin/Platform/Linux/NeuroModelerConsole"
LOG_DIR="Bin/Platform/Linux/EventsLog"

echo "================================================================================"
echo "АВТОМАТИЧЕСКАЯ ПРОВЕРКА ОТЛАДОЧНЫХ СООБЩЕНИЙ"
echo "================================================================================"

# Запускаем валидацию
echo ""
echo "Запускаю валидацию..."
"$CONSOLE_EXE" --check-config "$PROJECT_INI" > /dev/null 2>&1

sleep 2

# Находим последний лог
LATEST_LOG=$(ls -t "$LOG_DIR"/*.INFO* 2>/dev/null | head -1)

if [ -z "$LATEST_LOG" ]; then
    echo "❌ Файлы логов не найдены"
    exit 1
fi

echo ""
echo "Проверяю лог: $(basename "$LATEST_LOG")"
echo ""

# Ищем отладочные сообщения
KEYWORDS=(
    "UEngine::CreateEnvironment() called"
    "MotionControlLibrary::CreateClassSamples() called"
    "MotionControlLibrary::CreateClassSamples() completed"
    "Loading library: MotionControlLibrary"
    "Loading library: PulseLibrary"
    "Adding library to Storage: MotionControlLibrary"
    "Adding library to Storage: PulseLibrary"
    "Registered classes"
    "Build storage has been started"
    "Adding components from MotionControlLibrary"
    "Adding components from PulseLibrary"
)

FOUND_COUNT=0
for keyword in "${KEYWORDS[@]}"; do
    if grep -q "$keyword" "$LATEST_LOG" 2>/dev/null; then
        echo "✅ Найдено: $keyword"
        grep "$keyword" "$LATEST_LOG" | head -3 | sed 's/^/   /'
        FOUND_COUNT=$((FOUND_COUNT + 1))
    fi
done

echo ""
if [ $FOUND_COUNT -gt 0 ]; then
    echo "================================================================================"
    echo "✅ НАЙДЕНО $FOUND_COUNT ТИПОВ ОТЛАДОЧНЫХ СООБЩЕНИЙ"
    echo "================================================================================"
    exit 0
else
    echo "================================================================================"
    echo "⚠️  ОТЛАДОЧНЫЕ СООБЩЕНИЯ НЕ НАЙДЕНЫ"
    echo "================================================================================"
    exit 1
fi
