### Overview

./mcp will be a finalization of our efforts in ./harness.
We will be developing an MCP tool which has pygdbmi on the
backend, and exposes lavender domain specific operations
through the MCP protocol.

### MCP Tooling

#### Session Management
Tool name: "session"
Sub commands: ["start", "status", "stop"]

##### Start
This command will cause the configured game to run if it is
not already running.

Details to the agent of any failures.

##### Status
Details to the AI the following:
1) If the game has started
2) If the game is halted (pygdbmi breakpoint)
3) If the game has crashed
4) The current backtrace.

##### Stop
Stops the configured game if it is running.

Details to the agent of any failures.

#### Game State Navigation
Tool name: "navigate"
Sub commands: ["step",  "source"]

##### Step
Uses pygdbmi to perform the following:
1) Cause the game to break if it is currently running, stop the current `step` operation
if one is happening.
2) Make a breakpoint at `manage_game__post_render`.
3) Continue repeatedly until `manage_game__post_render` is reached. Timeouts.
4) Remove the breakpoint at `manage_game__post_render`.
5) Execute `finish` through pygdbmi to get the game state after `manage_game__post_render`.

Step semantically encapsulates a singular game frame progression in Lavender.

Details to the agent of any failures.

##### Source
Prints the whole backtrace.
Print the entire function body of the current frame in pygdbmi.

Details to the agent of any failures.

#### Core Management
Tool name: "core"
Sub commands: ["dump", "load", "reset"]

##### Dump
Extracts a coredump of the current state of the game to resume.
The file output is saved to a configured location, and resorts
to /tmp/lav-core-dump/ if unspecified.

Informs the agent of the core dump UUID.

Details to the agent of any failures.

##### Load
Stops the game if it is currently running.
Loads the game with the provided core dump UUID.
Looks up in the configured directory, /tmp/lav-core-dump if
unspecified.

Details to the agent of any failures.

##### Reset
Stops the game if it is currently running.
Reloads the last dump specified by Load.

Details to the agent of any failures.

#### Process Management
Tool name: "process"
Sub commands: ["list", "watch"]

##### List
Uses DebugProcessScanner to acquire all processes running in Lavender
and presents them to the agent.

##### Watch
Uses pygdbmi to break at the process's function handler.
Continues repeatedly with timeout until:
1) the process is hit
2) the process hit is the same pointer as the process being watched.
If reached, remove the beakpoint, and inform the agent the process is in frame.

Details to the agent any failures.

#### Input Management
Tool name: "input"
Sub commands: ["read", "write"]

##### Read
Dumps the current readings of DebugInputScanner.

Details to the agent any failures.

##### Write
Outputs to the Lavender input object via the DebugInputScanner.

Details to the agent any failures.

#### UI Manipulation
Tool name: "ui"
Sub commands: ["manager", "manager-select", "list", "invoke"]

##### Manager
Uses DebugUIScanner to list all UI managers to the agent.
Also informs the agent of the currently selected manager.

##### Manager-Select
Uses DebugUIScanner to select the specified manager in the scanner.

##### List
Uses DebugUIScanner to list all UI elements under the selected manager to the agent.

##### Invoke
Invokes the specified m_ function of the UI_Element. All functions supported
except m_UI_Transformed

Details to the agent any failures.

#### Graphics Processing
Tool name: "graphics"
Sub commands: ["screenshot", "record"]

##### Screenshot
Uses gl_debug.h to produce a screenshot, then directs the screenshot
to the agent.

##### Record
Unsupported at this time, future expansion.

#### Audio Processing
Tool name: "audio"
Sub commands: ["list", "listen"]

##### List
Unsupported at this time, future expansion.

##### Listen
Unsupported at this time, future expansion.

### Config
config.json

"config": {
  "session": {
    "executable": "path to executable"
  },
  "core": {
    "dump-location": "path to dump location"
  }
}

### MCP Server
The MCP tool described is to be a comprehensive system module.

lav_mcp.py (singular comprehensive system module, replicated per session)
lav_mcp_server.py (server middleware router to sessions.)

The MCP Server is a middleware router that listens on a port
and operates on the specified protocol:
1) Look at the MCP-protocol equivalent for a session ID
2) Look for existing session ID to active MCP session
3) If missing, make a new session and route.

This is to support multiple agents communicating to a singular server.
