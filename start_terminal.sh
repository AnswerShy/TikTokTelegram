#!/bin/bash

SCRIPT_DIR="$(dirname "$0")"

start_bot() {
    "$SCRIPT_DIR/my_env/bin/python3" "$SCRIPT_DIR/start.py" &
    PYTHON_TG_TT_BOT_PID=$!
    echo "Telegram server started with PID $PYTHON_TG_TT_BOT_PID. Press 'q' to quit, or type 'rs' to restart."
}

stop_bot() {
    if [ -n "$PYTHON_TG_TT_BOT_PID" ]; then
        kill "$PYTHON_TG_TT_BOT_PID"
        wait "$PYTHON_TG_TT_BOT_PID" 2>/dev/null
        echo "Telegram bot stopped."
    fi
}

restart_bot() {
    echo "Restarting bot..."
    stop_bot
    start_bot
}

start_bot

while : ; do
    read -r k
    case $k in
        q)
            stop_bot
            echo "Application closed."
            break
            ;;
        rs)
            restart_bot
            ;;
        *)
            echo "Invalid command. Press 'q' to quit, or type 'rs' to restart."
            ;;
    esac
done

