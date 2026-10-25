# Lavender

Lavender is a **cross-platform multiplayer retro game engine**.

Its goal is to let you target whichever retro console you want — and to let
players on *different* consoles play together in the same multiplayer instance.
It achieves this with **fixed-size memory pools** that are configured at build
time for the target platform. These build configurations are advertised as
*performance profiles*, and the least performant profile is used for all
players (with a few client-side exceptions, such as rendering
performance/effects), so that every client stays in lockstep.

The engine is developed as a strict hierarchical tree: `core/` is the portable
engine and is completely console-agnostic, while each console lives in its own
backend directory (`nds/`, `sdl/`, `no_gui/`, …).

## Quick start

> **Note:** Only the SDL backend builds at the moment. You need to define
> `LAVENDER_DIR` to point to the Lavender directory.

If you add `./tools` to your `PATH` you can use the engine's tooling.
Run the following in an empty directory:

```bash
lav_new_project
lav_build -e PLATFORM=sdl
```

If all goes well you should have an SDL executable in
`./build/sdl/<NAME-OF-DIR>`.

## Project layout

The navigation index on the left mirrors the source tree. Top-level sections:

| Directory  | What it is |
|------------|------------|
| [core/](core/index.md) | The portable engine core. Console-agnostic. |
| [nds/](nds/index.md) | Nintendo DS backend (devkitpro). |
| [sdl/](sdl/index.md) | SDL backend — the only buildable backend at the moment. |
| [no_gui/](no_gui/index.md) | Headless backend. |
| [tools/](tools/index.md) | Engine tooling (`lav_new_project`, `lav_build`, …). |
| [examples/](examples/index.md) | Example projects, one per subsystem. |
| [tests/](tests/index.md) | Test suite. |
| [harness/](harness/index.md) | Python test harness. |
| [graph/](graph/index.md) | Architecture graph: modules, layers, and dependencies. |
| [reference/](reference/index.md) | Reserved for auto-generated API reference (coming soon). |

## Building the engine

**Note:** currently you have to run `make clean` every time you build.

The project is built with `make` and the [devkitpro toolkit](https://devkitpro.org/).

### Podman Docker image (recommended)

```bash
podman pull docker.io/devkitpro
./run_build_podman.sh
```

### Docker image

```bash
docker pull devkitpro/devkitarm
sudo docker run -v ./:/home/$WHOAMI/GitRepos/AncientsGame docker.io/devkitpro/devkitarm \
  sh -c "export PATH=\$PATH:/opt/devkitpro/devkitARM/bin/ && \
         cd /home/\$WHOAMI/GitRepos/AncientsGame && make clean nds"
```

### Local devkitpro install

Follow the [devkitpro getting started guide](https://devkitpro.org/wiki/Getting_Started),
make sure `$DEVKITPRO` and `$DEVKITARM` are defined, and add
`/opt/devkitpro/devkitARM/bin/` to your `PATH`. Then, from the project's base
directory:

```bash
make clean nds
```

## Contributing

Older git commits contain code style instructions. The code style section is
being rewritten — for now, if you make a pull request the maintainer will
refactor as needed.

## Community

- **Discord:** [join here](https://discord.gg/VkzbCGyGRF)
- **Donate:** [please consider donating to help the project](https://www.paypal.com/donate/?hosted_button_id=HDFNAB5DC9F2L)
