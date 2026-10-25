# Log — Ring-buffer message queue with three named instances

**Sources:** `core/source/log/message.c` + `core/source/log/log.c` + `core/include/log/message.h` + `core/include/log/log.h`

## Surface Concerns

The log module provides a fixed-capacity circular queue of `Message` slots stored in a fixed array and tracked with two pointers (no dynamic links). Three independent logs live in the `Game` struct: `log__global`, `log__local`, and `log__system`. Messages are flushed from game.c via `print_log__global`, `print_log__local`, and `print_log__system`, which write into the next message slot and advance the write pointer. The core module has zero platform coupling -- no `platform.h` include in any log source or header.

- **Circular queue with eviction** — Two pointers track the queue: `p_next_message` (write head) and `p_oldest_message` (read head). When the queue fills, flushing advances both pointers, silently dropping the oldest message. Capacity: 32 messages.
- **Three log instances** — `log__global` (system-wide), `log__local` (per-client or per-scene), and `log__system` (engine-internal). Each has its own independent queue and pointers.
- **Message body construction** — `Message` supports character-by-character and C-string append, plus title assignment. Title is truncated at 15 characters; body at 96 bytes. Append functions return `true` on overflow.
- **Platform contract** — `PLATFORM_update_log__global/local/system` and `PLATFORM_clear_log__global/local/system` are declared in `platform.h` and called from game.c. The backend decides output destinations (console, file, HUD). Calls are currently commented out in game.c, making the log a write-only ring buffer with no display.

## Public API Surface

### Key Types

**`Message`** — defined in `defines.h`. Key members:
- `unsigned char message__title[MESSAGE_NAME_MAX_LENGTH_OF]` — 16-byte title buffer.
- `unsigned char message__body[MESSAGE_MAX_LENGTH_OF]` — 96-byte body buffer.
- `Serialization_Header _serialization_header` — pool tracking branding (`IDENTIFIER__UNKNOWN__u32` at init).

**`Log`** — defined in `defines.h`. Key members:
- `Message messages[MESSAGE_MAX_QUANTITY_OF]` — fixed array of 32 message slots.
- `Message *p_next_message` — pointer to the next write slot (write head).
- `Message *p_oldest_message` — pointer to the first valid message (read head / eviction sentinel).

### Key Functions

- `void initialize_log(Log *p_log);` — resets all 32 slots and sets pointers to initial empty state.
- `void flush_message_into__log(Log *p_log);` — advances the write pointer (evicting oldest if queue is full), then re-initializes the new slot.
- `Message *get_p_message_from__log(Log *p_log, Index__u8 index_of__message);` — returns the message at the given logical index from the read head; returns NULL if beyond valid range.
- `void initialize_message(Message *p_message);`
- `bool put_char_into__message(Message *p_message, char character);` — returns `true` if body is full.
- `bool put_cstr_into__message(Message *p_message, char *cstr);` — returns `true` on first overflow.
- `bool set_title_of__message(Message *p_message, char *cstr);` — returns `true` if title was truncated (max 15 chars).
- `static inline Message *get_next_p_message_in__log(Log *p_log);` / `static inline void clear_log(Log *p_log);`

## Key Files Table

| File | Role |
|------|------|
| `core/source/log/message.c` | Message init, char/cstr append, title setting |
| `core/source/log/log.c` | Log init, circular buffer management, message retrieval |
| `core/include/log/message.h` | Message API declarations, `clear_message` inline |
| `core/include/log/log.h` | Log API declarations, `get_next_p_message_in__log`, `clear_log` |
