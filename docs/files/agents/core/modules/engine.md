# Engine — Bootstrap, Frame Loop, and Game Lifecycle

**Sources:** `core/source/main.c` + `core/source/game.c` + `core/include/game.h`

## Surface Concerns

The engine module orchestrates the Lavender game lifecycle: bootstrap, the per-frame loop, scene management, fixed-point tick pacing, and multiplayer client handling. Layer: L2 (engine services). Called by `main.c` at bootstrap and by the game layer every frame.

- **Bootstrap** — `initialize_game()` zero-inits the `Game` struct, initializes the embedded managers (gfx context, scene manager + scene registration, process manager, sort-list manager, hitbox context, aliased texture manager, three loggers), registers the offline game-action logic table, sets singleplayer-default dispatch/receive/resolve handlers and default client load/save process handlers, calls `PLATFORM_initialize_game()`, and sets up platform graphics windows. The singleplayer defaults are overwritten by `begin_multiplayer_for__game()`.
- **Frame loop** — `run_game()` iterates the scene state machine (load → enter → unload each scene); the enter handler is required and a missing one aborts. It then waits out pending serialization requests by polling the process manager until all save/load processes complete. Returns 0 on a clean stop, -1 if no valid active scene is set or the active scene has no enter handler.
- **Per-frame management** — `manage_game__pre_render()` only calls `PLATFORM_pre_render()`. `manage_game__post_render()` runs poll_input → `reset__game_tick_timer()` → poll process manager → `PLATFORM_poll_audio_effects()` → `PLATFORM_post_render()` → loop tick timer. Scene/world updates are driven by the active scene, not by game.c.
- **Tick timing** — fixed-point accumulator (`u32F20`) drives deterministic frame pacing. `poll_elapsed_time__u32F20_of__game()` accumulates platform-reported time; `poll__game_tick_timer()` returns `(tick_accumilator + time_elapsed) >> 15` (32 ticks/sec); `reset__game_tick_timer()` subtracts the whole-tick portion from the accumulator (preserving the sub-tick remainder) and zeroes `time_elapsed`.
- **Multiplayer setup** — `begin_multiplayer_for__game()` aborts if `sizeof(Game_Action) > sizeof(TCP_Packet)`, then mallocs + initializes the TCP socket manager, calls `PLATFORM_tcp_begin()`, and installs the multiplayer dispatch/receive/resolve handlers. `max_quantity_of__clients == 1` flags the game as client and registers client game actions; otherwise it flags it as server and registers server actions. `poll_multiplayer()` delegates to the TCP socket manager each frame.
- **Client pool lifecycle** — pool is allocated with `allocate_client_pool_for__game()` (clamped to `MAX_QUANTITY_OF__TCP_SOCKETS`), client 0 is initialized with the session-token UUID, and the pool supports per-client `allocate`, `release` (swap-to-fill), `get_p_client_by__uuid_from__game`, and save/load via process dispatch (`dispatch_handler_process_to__save/load/create_client`). `release_client_pool_from__game()` refuses while any client is still active.
- **Process wrapping** — client save/load/create are all driven through the process manager: dispatch functions create processes whose run handlers perform the actual I/O. The process manager handles 512 processes across 4 priority levels. The create-client dispatch has no default handler installed (warning if called without one).
- **Fixed-capacity / no-growth design** — `Game` embeds almost everything. Four `pM_`-prefixed heap pointers: `pM_world`, `pM_clients`, `pM_ptr_array_of__clients`, `pM_tcp_socket_manager`.

## Public API Surface

### Key Types

**`Game`** (`defines.h`) — the root struct containing every manager, callback, and state. Key members: `Input input`, `Scene_Manager scene_manager`, `Hitbox_Context hitbox_context`, `World *pM_world`, `Process_Manager process_manager`, `Sort_List_Manager sort_list_manager`, `Path_List_Manager path_list_manager`, `Log log__global`/`log__local`/`log__system`, `Gfx_Context gfx_context`, platform contexts, `Game_Action_Logic_Table game_action_logic_table`, `Session_Token session_token`, timing fields (`tick__timer_u32`, `time__seconds__u32`, `time__nanoseconds__u32`, `u32F20 time_elapsed__u32F20`, `u32F20 tick_accumilator__u32F20`), client pool fields (`max_quantity_of__clients`, `pM_clients`, `pM_ptr_array_of__clients`), `TCP_Socket_Manager *pM_tcp_socket_manager`, game action callbacks (`m_game_action_handler__dispatch`/`__receive`/`__resolve`), client serialization callbacks (`m_process__serialize_client`/`__deserialize_client`/`__create_client`), and `Game_Flags__u32 game_flags__u32`.

### Key Functions

- `void initialize_game(Game *p_game);` — bootstrap: zero-init and initialize all managers.
- `int run_game(Game *p_game);` — scene iteration + wait out serialization; 0 on clean stop, -1 on invalid/missing active scene.
- `void manage_game__pre_render(Game *p_game);` / `void manage_game__post_render(Game *p_game);` — per-frame pre and post render phases.
- `u32F20 poll_elapsed_time__u32F20_of__game(Game *p_game);` — accumulates platform-reported elapsed time.
- `Quantity__u32 poll__game_tick_timer(Game *p_game);` — returns elapsed tick count (`(accumulator + elapsed) >> 15`, 32 ticks/sec).
- `void reset__game_tick_timer(Game *p_game);` — subtracts whole ticks, preserving the sub-tick remainder; zeroes `time_elapsed`.
- `void begin_multiplayer_for__game(Game *p_game, m_Poll_TCP_Socket_Manager m_poll_tcp_socket_manager);` — install multiplayer handlers, flag server/client by client count, register matching game actions.
- `void stop_multiplayer_for__game(Game *p_game);` — stop multiplayer mode and free the TCP socket manager.
- `void poll_multiplayer(Game *p_game);` — poll TCP socket manager.
- `bool allocate_client_pool_for__game(Game *p_game, Quantity__u32 quantity_of__clients);` — clamped to `MAX_QUANTITY_OF__TCP_SOCKETS`; false if a pool already exists.
- `bool release_client_pool_from__game(Game *p_game);` — frees the client pool; false while any client is active.
- `Client *allocate_client_from__game(Game *p_game, Identifier__u32 uuid__u32);` — allocates client from pool.
- `void release_client_from__game(Game *p_game, Client *p_client);` — releases client (swap-to-fill).
- `Client *get_p_client_by__uuid_from__game(Game *p_game, Identifier__u32 uuid__u32);` — returns client pointer.
- `Local_Space_Manager *get_p_local_space_manager_thats__closest_to__this_position(Game *p_game, Vector__3i32 vector__3i32);` — nearest local-space manager for a world position.
- `Process *dispatch_handler_process_to__create_client(Game *p_game, Identifier__u32 uuid_of__client__u32);` — creates client via process; no default handler installed.
- `Process *dispatch_handler_process_to__load_client(Game *p_game, IO_path path_to__client_file, Identifier__u32 uuid_of__client__u32);` — returns process.
- `Process *dispatch_handler_process_to__save_client(Game *p_game, IO_path path_to__client_file, Client *p_client);` — returns process.
- `Process *load_client(Game *p_game, Identifier__u32 uuid_of__client__u32);` — returns process.
- `void save_all__clients(Game *p_game);` — saves all clients.
- `Process *save_client(Game *p_game, Client *p_client);` — returns process.
- `void allocate_world_for__game(Game *p_game);` — allocates the world (no-op if already allocated).
- `u32F20 get_elapsed_ticks__u32F20_of__game(Game *p_game);` — elapsed time as fixed-point ticks.
- `bool print_log__global(Game *p_game, char *cstr);` / `print_log__local` / `print_log__system` — appends a C string to the named logger's next message; false if it doesn't fit.
- `static inline void set_dispatch_handler_process_for__create_client(Game *p_game, m_Process m_process);` / `set_dispatch_handler_process_for__load_client(Game *p_game, m_Process m_process);` / `set_dispatch_handler_process_for__save_client(Game *p_game, m_Process m_process);` — set client serialization handlers.
- `static inline Client *get_p_local_client_by__from__game(Game *p_game);` — returns local client.
- `static inline bool dispatch_game_action(Game *p_game, Identifier__u32 uuid_of__client__u32, Game_Action *p_game_action);` — returns success.
- `static inline bool dispatch_game_action_to__server(Game *p_game, Game_Action *p_game_action);` — returns success.
- `static inline bool receive_game_action(Game *p_game, Identifier__u32 uuid_of__client__u32, Game_Action *p_game_action);` — returns success.
- `static inline bool resolve_game_action(Game *p_game, Identifier__u32 uuid_of__client__u32, Game_Action *p_game_action);` — returns success.

## Key Files Table

| File | Role |
|------|------|
| `core/source/main.c` | `main()` — bootstrap: initialize → run → close |
| `core/source/game.c` | `initialize_game`, `run_game`, frame management, tick timing, multiplayer, client pool, log helpers |
| `core/include/game.h` | public API declarations + inline getters/handlers (`Game` struct itself lives in `defines.h`) |
| `core/include/defines.h` | `Game` struct definition |
