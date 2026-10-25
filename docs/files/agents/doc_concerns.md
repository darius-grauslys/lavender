config.md: should be renamed to engine_config.md
*.md: in all files, some explicit quantities for configurable fields are given. This should not be given explicit size and be detailed as resizable and that the reader should grep [INSERT MACRO NAME] to see the configured size.
client.md: MAX_QUANTITY_OF__CLIENTS is designated as resizable in engine_config.h - see *.md note.
client.md: 8x8x1 local space size is resizable in engine_config.h - see *.md note.
client.md: `set_client_as__active()` is marked as resetting to fresh connected state - this is strictly speaking incorrect. It only sets the flags to indicate that, but not the concrete state - we might have pending game_actions in the client, or other UUID linked components in the engine still attached to the client.
client.md:
