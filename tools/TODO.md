restore in a lav only opencode:

    "lavender-tools": {
      "type": "local",
      "command": ["sh", "-c", "PYTHONPATH=\"$LAVENDER_DIR/tools\" python3 \"$LAVENDER_DIR/tools/lavender_tools/lav_ai/lav_ai_app.py\""],
      "enabled": true
    }
