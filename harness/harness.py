"""
harness.py — Skeleton for the langchain agent loop.

This module will eventually house the autonomous debugging logic:

  1. Build langchain tools wrapping gdb MI operations
     (step, continue, read memory, read registers, set breakpoints, etc.).
  2. Instantiate an LLM agent with those tools.
  3. Feed the agent the program / binary info and let it drive the debug
     session toward a goal (e.g. "find the crash").

For now this is a placeholder — the interactive read-loop in ``main.py``
keeps the gdbmi session alive while the agent framework is wired in.
"""

from __future__ import annotations

# TODO: langchain agent integration
#   from langchain.agents import AgentExecutor, initialize_agent
#   from langchain.tools import Tool
#   from langchain.chat_models import ChatOpenAI
#
#   from .gdb_frame_controller import GDBFrameController
#   from .lavender_debug import Input_Flags__u32, parse_hex
#   from .debug_input_driver import DebugInputDriver
#   from .debug_scanner import DebugUIScannerExplorer
#
# def run_agent(gdbmi, goal: str):
#     """Drive an autonomous debug session toward *goal*."""
#     ...
