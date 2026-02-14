#!/bin/bash
# Script for automatic verification of debug messages in logs

set -e

PROJECT_INI="Bin/Configs/a.demcheva/12_MazeMemory_HandmadeExperiment/project.ini"
CONSOLE_EXE="Bin/Platform/Linux/NeuroModelerConsole"
LOG_DIR="Bin/Platform/Linux/EventsLog"

echo "================================================================================"
echo "AUTOMATED DEBUG MESSAGE CHECK"
echo "================================================================================"

# Run validation
echo ""
echo "Starting validation..."
"$CONSOLE_EXE" --check-config "$PROJECT_INI" > /dev/null 2>&1

sleep 2

# Find the latest log file
LATEST_LOG=$(ls -t "$LOG_DIR"/*.INFO* 2>/dev/null | head -1)

if [ -z "$LATEST_LOG" ]; then
    echo "❌ Log files not found"
    exit 1
fi

echo ""
echo "Checking log: $(basename "$LATEST_LOG")"
echo ""

# Look for debug messages
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
        echo "✅ Found: $keyword"
        grep "$keyword" "$LATEST_LOG" | head -3 | sed 's/^/   /'
        FOUND_COUNT=$((FOUND_COUNT + 1))
    fi
done

echo ""
if [ $FOUND_COUNT -gt 0 ]; then
    echo "================================================================================"
    echo "✅ FOUND $FOUND_COUNT TYPES OF DEBUG MESSAGES"
    echo "================================================================================"
    exit 0
else
    echo "================================================================================"
    echo "⚠️  NO DEBUG MESSAGES FOUND"
    echo "================================================================================"
    exit 1
fi
