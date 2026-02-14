#!/bin/bash
# Automatic script for testing debug messages
# Runs validation and checks logs until the messages are found or attempts are exhausted

set -e

PROJECT_INI="Bin/Configs/a.demcheva/12_MazeMemory_HandmadeExperiment/project.ini"
CONSOLE_EXE="Bin/Platform/Linux/NeuroModelerConsole"
LOG_DIR="Bin/Platform/Linux/EventsLog"
MAX_ATTEMPTS=5

echo "================================================================================"
echo "AUTOMATED TESTING OF DEBUG MESSAGES"
echo "================================================================================"
echo ""

ATTEMPT=1
while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "Attempt $ATTEMPT of $MAX_ATTEMPTS..."
    echo ""

    # Run validation
    echo "Starting validation..."
    "$CONSOLE_EXE" --check-config "$PROJECT_INI" > /dev/null 2>&1

    sleep 2

    # Find the latest log file
    LATEST_LOG=$(ls -t "$LOG_DIR"/*.INFO* 2>/dev/null | head -1)

    if [ -z "$LATEST_LOG" ]; then
        echo "❌ Log files not found"
        ATTEMPT=$((ATTEMPT + 1))
        continue
    fi

    echo "Checking log: $(basename "$LATEST_LOG")"

    # Look for key messages
    KEY_MESSAGES=(
        "UEngine::CreateEnvironment() called"
        "MotionControlLibrary::CreateClassSamples() called"
        "Loading library: MotionControlLibrary"
        "Adding library to Storage: MotionControlLibrary"
    )

    FOUND_COUNT=0
    for msg in "${KEY_MESSAGES[@]}"; do
        if grep -q "$msg" "$LATEST_LOG" 2>/dev/null; then
            echo "  ✅ Found: $msg"
            FOUND_COUNT=$((FOUND_COUNT + 1))
        fi
    done

    if [ $FOUND_COUNT -ge 2 ]; then
        echo ""
        echo "================================================================================"
        echo "✅ SUCCESS! Found $FOUND_COUNT key messages"
        echo "================================================================================"
        echo ""
        echo "All found debug messages:"
        grep -E "(CreateEnvironment|MotionControlLibrary|Loading library|Adding library|Build storage|Registered classes)" "$LATEST_LOG" | head -20
        exit 0
    else
        echo "  ⚠️  Found only $FOUND_COUNT of ${#KEY_MESSAGES[@]} key messages"
        ATTEMPT=$((ATTEMPT + 1))
        if [ $ATTEMPT -le $MAX_ATTEMPTS ]; then
            echo "  Waiting before the next attempt..."
            sleep 3
        fi
    fi
done

echo ""
echo "================================================================================"
echo "⚠️  PROBLEM NOT RESOLVED AFTER $MAX_ATTEMPTS ATTEMPTS"
echo "================================================================================"
echo ""
echo "Last lines from the log:"
tail -20 "$LATEST_LOG"
exit 1
