# Outstanding Item 4 — Optimize build time (linker & build-system evaluation)

**Scope:** evaluation only, no code changes (per request).
**Verdict: switching `ld` for a modern linker is the *lowest-impact* lever available — the
measured link step is ~0.5 s of a 92 s cold build. The build time is dominated by **serial
compilation of 281 objects** (~205 s of CPU), with a small number of generated/OpenGL modules
accounting for ~41%. Parallelism (`-j`), the `glad.o` outlier, and per-build fixed overhead
(bear + full assets copy) are where the wins are.**

Date: 2026-09-17. All numbers measured on this machine: 4-core x86-64, GCC 14.2.1,
GNU ld 2.44 (the only linker installed — no mold/lld/gold present), target
`PLATFORM=sdl`, `GAME_DIR=…/AncientsGame` (281 objects, 26.7 MB of .o, 7.7 MB binary with the
user's usual debug flags; my instrumented cold build produced a 1.9 MB non-`-ggdb` binary).

---

## 1. Build-system shape (what we're optimizing)

- Three make layers: top-level `Makefile` → `make -f Makefile.build $(BUILD)` (outer) →
  `make -f Makefile.build -C $(BUILD)` (inner). **No `-j` anywhere in the chain** — a default
  build compiles all 281 objects serially.
- Single unified pattern rule `%.o: %.c` (core/platform/game/grit via `vpath`),
  `-MMD -MP -MF` dependency tracking for incremental builds (`Makefile.build:59-62`).
- Link: `$(LD) $(LDFLAGS) $(FLAGS_LINKER) $(OFILES) $(LIBPATHS) $(LIBS)` with
  **`LD := $(CC)`** (`sdl/Makefile.include:27`) — i.e. the GCC driver, which invokes GNU ld
  2.44 under the hood.
- The default target wraps everything in **`bear --force-preload`** (compile-command capture)
  (`Makefile:51-52`). A separate `compile_commands` target already exists and uses `-B`
  (`Makefile:62-69`) — the bear wrap in the *default* build is redundant with it.
- `GAME_SETUP` does **`cp -r $(GAME_DIR)/assets $(BUILD)` on every build** (it's `.PHONY`)
  (`Makefile.build` include chain, `GAME_SETUP` rule) — full assets tree copy, every time.
- `PERF_METRICS=1` already exists: times every module + link into `performance-metrics/modules.csv`
  and runs `tools/perf_summary.sh` (`Makefile.build:46-77`) — the measurement harness for this
  evaluation (and for future regression tracking).

## 2. Measured baseline (PERF_METRICS=1, instrumented runs)

| Scenario | Wall | Notes |
|---|---|---|
| No-op build (everything current) | **3.2 s** | 3 make layers + bear post-process + full assets `cp -r` — i.e. ~3 s of *fixed* overhead per invocation |
| 3-file incremental (2 core + 1 game file touched) | **4.1 s** | ≈0.9 s of real work (3 compiles + relink) on top of the 3.2 s fixed |
| Link-only (1 .o touched, 281 objects) | **3.8 s** | ≈0.6 s fixed overhead + **~0.5 s GNU-ld link** of the whole binary |
| **Cold build, `-j4`** | **92.2 s** | 281 compiles + 1 link + assets copy; only failure was `perf_summary.sh` path-check in my sandboxed BUILD (see §6) |
| Cold build, serial (extrapolated) | **≈206 s + overhead ≈ 3.5 min** | from the 205 s compile-CPU total |

Per-module compile distribution under `-j4` (281 modules, 205.0 s total CPU — inflated by
4-way contention + bear preload):

| Stat | Value |
|---|---|
| min / median / p90 / max | 202 ms / **513 ms** / 1069 ms / **26132 ms** |
| modules > 1 s / > 2 s | 31 / 4 |

Top offenders:

| Module | ms | Share of total |
|---|---|---|
| `sdl/source/rendering/opengl/glad/glad.c` | 26132 | **12.7%** |
| `sdl/source/rendering/opengl/gl_texture.c` | 10421 | 5.1% |
| `sdl/source/debug/opengl/gl_debug_screen.c` | 3132 | 1.5% |
| `sdl/source/sdl_game.c` | 2849 | 1.4% |
| rest of the `gl_*`/`sdl_*` band (top-10 remainder) | ≈42 s combined | — |
| **entire opengl/sdl band** | **≈84.7 s** | **41%** |

The remaining ~120 s is 270 modules at a ~513 ms median — i.e. the *long tail of ordinary
code*, only reachable by parallelism (or -O1, at a runtime cost).

## 3. The linker question specifically

- **Current**: GNU ld 2.44 via the GCC driver. Measured link of the full 281-object binary:
  **~0.5 s**. That's already fast — the object count and binary size are small, and GNU ld
  2.44's single-threaded pass over 26 MB of objects just isn't the bottleneck.
- **mold** (the usual answer): parallelizes section processing; at this scale expect
  ~0.2–0.3 s savings per link. Not installed; installable via distro package or `cargo install
  mold`. **mold would save <0.5% of a cold build.**
- **lld** (`-fuse-ld=lld`): similar magnitude.
- **Recommendation: do not switch linkers as a build-time measure.** Keep `LD := $(CC)`, but
  make it *overridable* (`export LD ?= $(CC)` style, or honor an `LD` env var) so it can be
  revisited for free when the object count grows 10×, or if link *correctness* ever favors a
  different flavor. The parallelism win people expect from mold is real at 1000+ objects; at
  281 it's noise next to the 205 s of compilation.

## 4. Where the build time actually is (impact-ordered levers)

1. **Parallelize compilation** — biggest single win. Serial cold ≈ 206 s; measured `-j4` =
   92 s wall (~2.3× realized; contention + bear + the 26 s `glad.o` long tail cap the
   speedup). Make `-j$(nproc)` the default (e.g. `MAKEFLAGS += -j$(shell nproc)` guarded so a
   user-supplied `-j` still wins, or a `build-parallel` alias). Bear works fine under `-j`.
2. **`glad.o` diet** — 26.1 s, 12.7% of the whole build, one generated file. Options, in order
   of cleanliness: (a) regenerate GLAD with a minimal profile (core-only, the GL version
   actually used) — file size drops by orders of magnitude; (b) special make rule compiling
   just `glad.c` with `-O1` (generated boilerplate; runtime cost negligible); (c) vendor a
   prebuilt `glad.o` out of the graph (least incremental-friendly).
3. **The OpenGL/sdl band** (≈41% of compile CPU; `gl_texture` alone 10.4 s) — candidate for a
   band-scoped `-O1` (build time) vs `-O2` (runtime) trade, or file splitting. Only worth it
   if the runtime cost is measured acceptable; these are hot rendering paths.
4. **Decouple bear from the default build** — the default wraps every compile in
   `bear --force-preload` purely for LSP convenience, while a dedicated `compile_commands`
   target already exists (with `-B`). Default = bare make; `make compile_commands` = bear.
   Removes preload overhead from every compile and the post-process from every build.
5. **Stop the full assets copy per build** — `cp -r assets` is `.PHONY`; switch to
   `cp -n`/`rsync -a --update` (or an mtime check) so unchanged assets are skipped.
6. **Warning noise** — `core/include/defines.h:2367-2371` carries intentional `#warning`
   markers that print into *every* TU that includes `defines.h` (~1400 warning lines per full
   build; CPU-negligible, but it buries real diagnostics — gate behind a debug macro).

   (Also noted: `-march` is set to the generic baseline (`x86-64` via the `uname -m` sed in
   `Makefile.include:16`); `-march=native` is a *runtime* win, not a build-time one.)

### Projected cold-build trajectory (this machine, this target)

| Step | Cold build (4 cores) |
|---|---|
| Today (serial) | ≈3.5 min |
| + `-j4` default | **92 s** (measured) |
| + glad.o diet | ≈70 s |
| + bear decoupling + conditional assets | ≈65 s |
| + opengl band at -O1 | ≈45–50 s (runtime tradeoff — measure first) |

And the no-op rebuild goes 3.2 s → <1 s with levers 4–5 (matters most for the daily
edit-compile-test loop, more than any cold-build number).

## 5. Incremental-build health (why the daily loop feels slow)

Dependency tracking is sound (`-MMD -MP`, `-include $(OFILES:.o=.d)`), so a 1-file edit is a
1-object rebuild — measured ~0.3–0.8 s of actual work. The perceived slowness is the **3.2 s
fixed overhead** (3 make layers + bear + assets copy) paid on *every* invocation, dwarfing
the actual work in small edits. Levers 4 and 5 are therefore the highest-value *daily*
improvement even though they're small on paper.

## 6. Measurement notes / caveats

- The instrumented cold build ran in a scratch `BUILD=/tmp/opencode/coldbuild` to avoid
  disturbing the live `AncientsGame/build/sdl` tree. It succeeded end-to-end (binary produced);
  the only "Error 2" was `perf_summary.sh` refusing a CSV outside its expected
  `build/*/performance-metrics/` location — a script path-assumption, harmless here, worth a
  one-line fix if `PERF_METRICS` builds in custom BUILD dirs are kept.
- The live `AncientsGame/build/sdl/AncientsGame` binary was relinked once during incremental
  tests (identical source, new mtime) — no content change.
- My cold build omitted the user's `-ggdb` FLAGS (binary 1.9 MB vs 7.7 MB live); with `-ggdb`
  expect compiles ~10–20% slower. The *ratios* (glad share, band share, parallel speedup)
  hold.
- `PERF_METRICS=1` + `make -j` CSV is per-module wall time under contention; treat absolute
  per-module numbers as upper bounds, and the `LINK` row (496 ms, uncontended) as the honest
  linker figure.
