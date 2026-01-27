#!/bin/bash
# Автоматический скрипт для тестирования отладочных сообщений
# Запускает валидацию и проверяет логи до тех пор, пока сообщения не будут найдены

set -e

PROJECT_INI="Bin/Configs/a.demcheva/12_MazeMemory_HandmadeExperiment/project.ini"
CONSOLE_EXE="Bin/Platform/Linux/NeuroModelerConsole"
LOG_DIR="Bin/Platform/Linux/EventsLog"
MAX_ATTEMPTS=5

echo "================================================================================"
echo "АВТОМАТИЧЕСКОЕ ТЕСТИРОВАНИЕ ОТЛАДОЧНЫХ СООБЩЕНИЙ"
echo "================================================================================"
echo ""

ATTEMPT=1
while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "Попытка $ATTEMPT из $MAX_ATTEMPTS..."
    echo ""
    
    # Запускаем валидацию
    echo "Запускаю валидацию..."
    "$CONSOLE_EXE" --check-config "$PROJECT_INI" > /dev/null 2>&1
    
    sleep 2
    
    # Находим последний лог
    LATEST_LOG=$(ls -t "$LOG_DIR"/*.INFO* 2>/dev/null | head -1)
    
    if [ -z "$LATEST_LOG" ]; then
        echo "❌ Файлы логов не найдены"
        ATTEMPT=$((ATTEMPT + 1))
        continue
    fi
    
    echo "Проверяю лог: $(basename "$LATEST_LOG")"
    
    # Ищем ключевые сообщения
    KEY_MESSAGES=(
        "UEngine::CreateEnvironment() called"
        "MotionControlLibrary::CreateClassSamples() called"
        "Loading library: MotionControlLibrary"
        "Adding library to Storage: MotionControlLibrary"
    )
    
    FOUND_COUNT=0
    for msg in "${KEY_MESSAGES[@]}"; do
        if grep -q "$msg" "$LATEST_LOG" 2>/dev/null; then
            echo "  ✅ Найдено: $msg"
            FOUND_COUNT=$((FOUND_COUNT + 1))
        fi
    done
    
    if [ $FOUND_COUNT -ge 2 ]; then
        echo ""
        echo "================================================================================"
        echo "✅ УСПЕХ! Найдено $FOUND_COUNT ключевых сообщений"
        echo "================================================================================"
        echo ""
        echo "Все найденные отладочные сообщения:"
        grep -E "(CreateEnvironment|MotionControlLibrary|Loading library|Adding library|Build storage|Registered classes)" "$LATEST_LOG" | head -20
        exit 0
    else
        echo "  ⚠️  Найдено только $FOUND_COUNT из ${#KEY_MESSAGES[@]} ключевых сообщений"
        ATTEMPT=$((ATTEMPT + 1))
        if [ $ATTEMPT -le $MAX_ATTEMPTS ]; then
            echo "  Ожидание перед следующей попыткой..."
            sleep 3
        fi
    fi
done

echo ""
echo "================================================================================"
echo "⚠️  ПРОБЛЕМА НЕ РЕШЕНА ПОСЛЕ $MAX_ATTEMPTS ПОПЫТОК"
echo "================================================================================"
echo ""
echo "Последние строки из лога:"
tail -20 "$LATEST_LOG"
exit 1
